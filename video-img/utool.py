import os
import sys
import json
import time
import warnings
from datetime import datetime
from pathlib import Path
import re
import logging

import cv2
import numpy as np
from paddleocr import PaddleOCR

from log import setup_logger

os.system("chcp 65001 > nul")  # 控制台切到 UTF-8
sys.stdout.reconfigure(encoding='utf-8')  # Python 输出也 UTF-8
warnings.filterwarnings("ignore", message="No ccache found")


def process(
        video_path: str | Path = Path("data") / "1.mp4",
        data_json=Path("data") / "data.json",
        start_sec: int = 0,
        end_sec: int = None,
        interval: int = 1,
        scope: bool = False,
        roi: tuple = None,
        min_score: float = 0.8,
        ifs: list | None = None,
        out_dir: str | Path = "result",
        log_dir: str | Path = Path("logs"),
        log_name: str = "process",
        log_dir_name: str = datetime.now().strftime(f"%Y-%m-%d_%H·%M·%S") + ".log"
) -> set[str]:
    """
        对单个视频文件进行「起始秒开始 → 每N帧进行范围OCR识别 → 条件命中 → 截图保存」。
        :param video_path: 视频路径, 默认data/1.mp4
        :param data_json: 表格数据路径, 默认data/data.json
        :param start_sec: 采样起始秒, 默认0秒开始采样
        :param end_sec: 采样结束秒，默认None
        :param interval: 每N帧采样一次，默认1帧采样一次
        :param scope: 是否开启范围识别框选的辅助工具，默认False
        :param roi: 识别范围，默认全屏识别
        :param min_score: 最小置信度，默认0.8
        :param ifs: 附加条件列表，默认None
        :param out_dir: 输出目录；默认result文件夹
        :param log_dir: 日志路径，默认logs文件夹
        :param log_name: 日志名称，默认process
        :param log_dir_name: 日志文件名，默认当前时间
    """
    # --------------- 路径配置 ---------------
    video_path, data_json, out_dir = Path(video_path), Path(data_json), Path(out_dir)

    if not video_path.exists():
        raise RuntimeError(f"视频不存在：{video_path}")
    out_dir.mkdir(exist_ok=True)
    log_dir.mkdir(exist_ok=True)
    logger = setup_logger(log_name, log_dir / log_dir_name)

    # --------------- 视频处理 ---------------
    cap = cv2.VideoCapture(str(video_path))  # 打开视频文件
    if not cap.isOpened():
        raise RuntimeError(f"无法打开视频：{video_path}")
    # 获取视频信息
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps
    start_frame = int(start_sec * fps)

    logger.info(f"视频信息：")
    logger.info(f"  总帧数: {total_frames}")
    logger.info(f"  帧率: {fps:.2f} FPS")
    logger.info(f"  时长: {duration:.2f} 秒")
    logger.info(f"  输出目录: {out_dir}")
    logger.info(f"  帧间隔: {interval}")

    if start_frame >= total_frames:
        raise RuntimeError(f"起始秒={start_sec} s 超出视频总长 {total_frames / fps:.1f} s")

    # 定位到起始帧
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    ret, frame = cap.read()
    if not ret:
        raise RuntimeError(f"无法读取视频第 {start_sec} 秒（frame #{start_frame}）")

    # 保存图片
    start_sec_path = Path(out_dir) / f"frame{start_sec}s.jpg"
    cv2.imwrite(str(start_sec_path), frame)
    logger.info(f"已定位到视频第 {start_sec} 秒，已保存为图片 → {start_sec_path}")

    # 3. 判断是否需要手动选 ROI
    if roi is not None:
        pass
    elif scope:
        roi = manual_roi(frame, logger)
    else:
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        roi = (0, 0, w, h)

    # 初始化OCR
    logger.info("OCR初始化中...")
    ocr = PaddleOCR(
        use_doc_orientation_classify=False,  # 不使用文档方向分类模型
        use_doc_unwarping=False,  # 不使用文本图像矫正模型
        use_textline_orientation=False,  # 不使用文本行方向分类模型
        device="gpu",  # 使用GPU推理
        text_rec_score_thresh=0.9,  # 置信度阈值
    )
    if ocr:
        logger.info("OCR初始化成功！")

    # --------------- 按 interval 逐帧 OCR，保存带框图片 ---------------
    frame_id = start_frame
    frame_cnt = 0   # 单次识别耗时
    total_time = 0.0  # 平均耗时
    total_sec = total_time / 1000  # 毫秒 → 秒
    minutes, seconds = divmod(total_sec, 60)
    logger.info("开始OCR识别，帧间隔=%d，ROI=%s", interval, roi)
    with open(data_json, "r", encoding="utf-8") as f:
        data = json.load(f)
    items = [d["物品名称"] for d in data]
    hit_items = set()
    logger.info(f"识别列表：{items}")

    ifs = ifs or []  # 生成器/元组/集合都转成列表
    must_texts = {d["文案"]: d.get("识别范围") for d in ifs if d.get("识别范围")}

    while frame_id < total_frames:
        logger.debug("=" * 50)
        logger.debug(f"第{frame_id}帧")
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_id)
        ret, frame = cap.read()
        if not ret:  # 保险：万一读失败也跳出
            logger.info("已读到视频结尾，OCR 循环结束")
            break

        # ① 记录开始时间（毫秒级）
        t_start = time.perf_counter()

        # 按 ROI 裁剪子图
        x, y, w, h = roi
        roi_frame = frame[y:y + h, x:x + w]

        # 3. OCR 识别
        ocr_res = ocr.predict(roi_frame)
        ocr_records = []
        texts = set()

        # 识别当前帧的所有文字，存进ocr_records中
        for res in ocr_res:
            for text, score, box in zip(res['rec_texts'], res['rec_scores'], res['rec_boxes']):
                clean_text = re.sub(r'[()\[\]（）【】\s]', '', text)
                logger.debug(f"识别到文字：{text} 置信度：{score:.5f}")
                ocr_records.append((clean_text, box, score))
                texts.add(clean_text)

        # 判断识别到的文字里有没有符合策划表的
        for item in items:
            # 文字判断
            hit_rec = next((rec for rec in ocr_records if item in rec[0]), None)
            if hit_rec is None or item in hit_items:
                continue

            # 必须 / 或者 条件
            if must_texts and not must_texts.issubset(texts):
                continue
            if or_texts and or_texts.isdisjoint(texts):
                continue

            hit_items.add(item)
            preview = frame.copy()


            # ① 画「必须项」框（红色）
            for rec in ocr_records:
                for must in must_texts:
                    if must in rec[0]:
                        x, y, w, h = rec[1]
                        cv2.rectangle(preview, (x, y), (w, h),(0, 0, 255), 2)
                        break

            # ② 画「或者项」框（蓝色）
            for rec in ocr_records:
                for or_txt in or_texts:
                    if or_txt in rec[0]:
                        x, y, w, h = rec[1]
                        cv2.rectangle(preview, (x, y), (w, h),(255, 0, 0), 2)
                        break

            box, score = hit_rec[1], hit_rec[2]
            cv2.imencode(".png", frame)[1].tofile(out_dir / f"仓库到账后_{item}.png")
            x, y, w, h = box
            cv2.rectangle(preview, (x, y), (w, h), (0, 255, 0), 2)
            truncated = f"{int(score * 1000) / 1000:.3f}"
            cv2.putText(preview, truncated, (x, y-6), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

            # ⑤ 无乱码保存
            cv2.imencode(".png", preview)[1].tofile(out_dir / f"仓库到账后_{item}_预览.png")
            cv2.imencode(".png", frame)[1].tofile(out_dir / f"仓库到账后_{item}.png")

            logger.info(f"✅ 命中：{item} {x, y, w, h}")
            break

        # ③ 记录结束时间
        t_end = time.perf_counter()
        elapsed = (t_end - t_start) * 1000  # 毫秒
        total_time += elapsed
        frame_cnt += 1

        logger.debug(f"帧 {frame_id} 处理耗时 {elapsed:.2f} ms")

        # 5. 步进到下一采样帧
        frame_id += interval

    # --------------- 循环结束，打印汇总 ---------------
    logger.info("=" * 50)
    logger.info(f"OCR识别完成, 共命中 {len(hit_items)} 个物品: {hit_items}, 总耗时: {int(minutes):02d}分{seconds:05.2f}秒, 单次识别平均耗时: {total_time / frame_cnt:.2f} ms")
    cap.release()  # 释放视频句柄
    cv2.destroyAllWindows()  # 保险：关闭所有 OpenCV 窗口

    return hit_items


def manual_roi(frame, logger: logging.Logger) -> None:
    """
    用鼠标在当前帧上画矩形选 ROI，按回车/空格确认，返回 (x, y, w, h)。
    """
    roi_xywh = None
    drawing, ix, iy = False, -1, -1

    def mouse_cb(event, x, y, flags, param):
        nonlocal roi_xywh, drawing, ix, iy
        if event == cv2.EVENT_LBUTTONDOWN:
            drawing, ix, iy = True, x, y
        elif event == cv2.EVENT_MOUSEMOVE and drawing:
            img2 = frame.copy()
            cv2.rectangle(img2, (ix, iy), (x, y), (0, 255, 0), 2)
            cv2.imshow("select_roi", img2)
        elif event == cv2.EVENT_LBUTTONUP:
            drawing = False
            x1, y1, x2, y2 = min(ix, x), min(iy, y), max(ix, x), max(iy, y)
            roi_xywh = (x1, y1, x2 - x1, y2 - y1)
            logger.info("选择 → ROI(x,y,w,h)：(%d, %d, %d, %d)", *roi_xywh)

    cv2.namedWindow("select_roi")
    cv2.setMouseCallback("select_roi", mouse_cb)
    cv2.imshow("select_roi", frame)
    logger.info("请在图片上拖动鼠标框选 ROI，按【回车】或【空格】确认")

    while True:
        key = cv2.waitKey(0) & 0xFF
        if key in (13, 32):  # 13=Enter  32=Space
            break
        elif key == 27:  # Esc 取消
            roi_xywh = None
            break

    cv2.destroyAllWindows()
    if roi_xywh is None:
        raise RuntimeError("未选择 ROI，程序退出")

    logger.info("确定 ROI(x,y,w,h)：(%d, %d, %d, %d)", *roi_xywh)
    return roi_xywh


def clean(text: str) -> str:
    """
    去掉所有中英文括号、空格、横线等符号，只保留汉字、字母、数字
    """
    # \u4e00-\u9fa5 → 汉字；\w → 字母数字下划线；其余全部剔除
    return re.sub(r"[^\u4e00-\u9fa5\w]", "", text)


def given_in_ocr(given: str, ocr_texts: set[str]) -> bool:
    """
    给定文字经过清洗后，必须完整出现在任意一条OCR文字（清洗后）里
    """
    given_clean = clean(given)
    for t in ocr_texts:
        if given_clean in clean(t):
            return True
    return False
