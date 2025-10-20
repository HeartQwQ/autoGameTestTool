import json
import warnings
import time
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
from paddleocr import PaddleOCR
from utils.log import create_default_logger
from utils.tool import get_video_info, format_duration_with_ms, clean_json_strings, frame_to_phash, clean_text, \
    get_box_position

warnings.filterwarnings("ignore", message="No ccache found")


class VideoProcess:
    def __init__(self, config: dict):
        self.config = config
        self.project_root = Path(__file__).parent.parent    # 项目根目录
        # 初始化主日志器
        self._init_logger("VideoProcess")
        # 初始化视频
        self._init_video()
        # 初始化表格
        self._init_table()
        # 初始化OCR
        self._init_ocr()

    def _init_logger(self, name: str):
        # 创建运行结果目录
        self.out_dir = Path(datetime.now().strftime(f"%Y-%m-%d_%H·%M·%S"))
        self.out_dir.mkdir(parents=True, exist_ok=True)
        # 预览结果目录
        self.preview_dir = Path(self.out_dir / "识别预览")
        self.preview_dir.mkdir(parents=True, exist_ok=True)
        self.logger = create_default_logger(name, self.out_dir)
        self.logger.info("=" * 30 + "VideoProcess" + "=" * 30)
        self.logger.info(f"运行结果目录: {self.out_dir}")
        self.logger.info(f"主日志器初始化完成: {self.logger}")

    def _init_video(self):
        self.logger.info("=" * 30 + "初始化视频" + "=" * 30)
        self.video_path = self.project_root / self.config.get("video_path")
        self.logger.info(f"视频路径: {self.video_path}")
        self.cap = cv2.VideoCapture(self.video_path)
        self.video_info = get_video_info(self.cap, self.config.get("target_fps"))
        self.frame_idx = 0  # 帧索引
        self.logger.info(f"分辨率: {self.video_info.get('width')} x {self.video_info.get('height')}")
        self.logger.info(f"时长: {format_duration_with_ms(self.video_info.get('duration') * 1000)}")
        self.logger.info(f"帧率: {self.video_info.get('fps'):.2f} FPS")
        self.logger.info(f"总帧数: {self.video_info.get('frame_count')}")
        self.logger.info(f"帧间隔: {self.video_info.get('interval')}")

    def _init_table(self):
        self.logger.info("=" * 30 + "初始化表格" + "=" * 30)
        # 表格路径
        self.data_path = self.project_root / self.config.get("data_path")
        self.logger.info(f"表格路径: {self.data_path}")
        # 加载表格
        with open(self.data_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
            self.data_json = clean_json_strings(raw_data)
        self.logger.info(f"表格数据: {self.data_json}")
        # 提取表格数据
        self.data_name = {d["物品名称"] for d in self.data_json}
        self.logger.info(f"物品名称: {self.data_name}")

        # 初始化兑换碎片列表
        self.current = self.config.get("redeem_shards")
        self.redeem_shards_before_map = {}
        self.redeem_shards_after_map = {}
        # 按 data_json 顺序遍历，逐个处理
        for item in self.data_json:
            # 记录兑换前的状态
            self.redeem_shards_before_map[self.current] = item["物品名称"]
            # 执行兑换
            self.current -= item["兑换数量"]
            # 记录兑换后的状态
            self.redeem_shards_after_map[self.current] = item["物品名称"]
        self.logger.info(f"兑换前映射: {self.redeem_shards_before_map}")
        self.logger.info(f"兑换后映射: {self.redeem_shards_after_map}")

        # 初始化命中集合
        self.hit = {}
        for stage in self.config.get("stages"):
            self.hit[stage.get("name")] = set()
        self.logger.info(f"命中前集合: {self.hit}")

    def _init_ocr(self):
        """初始化OCR引擎"""
        self.logger.info("=" * 30 + "初始化OCR" + "=" * 30)
        ocr_config = self.config.get("ocr", {})
        self.ocr = PaddleOCR(**ocr_config)
        self.logger.info(f"OCR初始化完成: {self.ocr}")
        self.logger.info(f"OCR配置: {ocr_config}")

    def video_ocr(self):
        self.logger.info("=" * 30 + "开始视频OCR" + "=" * 30)
        process_start = time.perf_counter()     # 记录处理开始时间

        skip_count = 0          # 跳帧计数
        phash_count = 0         # 哈希去重计数
        process_count = 0       # 处理计数
        last_hash = None        # 上一帧的哈希值
        phash_time_list = []    # 哈希处理时间列表
        ocr_time_list = []      # OCR处理时间列表

        while True:
            ret, frame = self.cap.read()    # 读取帧
            if not ret:                     # 如果读取失败，退出循环
                self.logger.info("已读到视频结尾，OCR 循环结束")
                break
            self.frame_idx += 1

            # 根据帧间隔跳帧
            if self.frame_idx % self.video_info.get('interval') == 0:
                self.logger.info("=" * 30 + f"📸 第 {self.frame_idx} 帧" + "=" * 30)
                # 计算帧的哈希值
                phash = frame_to_phash(frame, self.config.get('hash_size'), last_hash, self.config.get('hamming_threshold'))
                phash_time_list.append(phash.get('phash_process_time'))
                self.logger.info(f"哈希耗时: {format_duration_with_ms(phash.get('phash_process_time') * 1000)}")
                # 如果帧重复，跳过
                if phash.get("is_duplicate"):
                    phash_count += 1
                    self.logger.info(f"🔁 重复帧（汉明距离={phash.get('hamming_dist')}）")
                    continue

                last_hash = phash.get('current_hash')
                process_count += 1
                self.logger.info(f"✅ 新帧")
                # OCR处理
                ocr_start = time.perf_counter()     # 记录开始时间
                ocr_res = self.ocr.predict(frame)   # 进行OCR识别
                preview = frame.copy()              # 复制一份帧图片
                result = []                         # 存储OCR结果
                for res in ocr_res:
                    for text, score, box in zip(res['rec_texts'], res['rec_scores'], res['rec_boxes']):
                        cleaned_text = clean_text(text)                         # 清理文本，只留下中文、英文字母、数字
                        box_poi = get_box_position(box, preview)                # 获取识别到的文案的坐标
                        frame_res = (cleaned_text, score, box_poi, box)         # 组合OCR结果，清理后的文本，置信度，两点矩形框坐标
                        x, y, w, h = box
                        cv2.rectangle(preview, (x, y), (w, h), (0, 0, 255), 2)  # 画出识别到的文案-红色框
                        result.append(frame_res)                                # 存储OCR结果
                        self.logger.info(f"OCR结果: {text}, 清洗文本: {cleaned_text}, 置信度: {score:.2f}, 位于: {box_poi}")
                preview_path = str(self.preview_dir / f"{self.frame_idx}帧.jpg")
                cv2.imencode(".jpg", preview)[1].tofile(preview_path)
                ocr_time = time.perf_counter() - ocr_start  # 计算耗时
                ocr_time_list.append(ocr_time)
                self.logger.info(f"OCR识别耗时: {format_duration_with_ms(ocr_time * 1000)}")

                self.run(result, frame)   # 运行所有处理模块，对当前帧进行处理
            else:
                skip_count += 1

        self.cap.release()
        self.logger.info("=" * 30 + f"🎉 视频OCR处理完成！" + "=" * 30)
        self.logger.info(f"共读取 {self.frame_idx} 帧, 跳过 {skip_count} 帧, 哈希去重{phash_count}帧, 实际OCR {process_count} 帧")
        duration_ms = time.perf_counter() - process_start
        self.logger.info(f"视频处理耗时: {format_duration_with_ms(duration_ms * 1000)}")
        self.logger.info(f"平均每帧处理耗时: {format_duration_with_ms(duration_ms / process_count * 1000)}")
        self.logger.info(f"总哈希耗时: {format_duration_with_ms(sum(phash_time_list) * 1000)}")
        self.logger.info(f"平均每帧哈希耗时: {format_duration_with_ms(np.mean(phash_time_list) * 1000)}")
        self.logger.info(f"总OCR耗时: {format_duration_with_ms(sum(ocr_time_list) * 1000)}")
        self.logger.info(f"平均每帧OCR耗时: {format_duration_with_ms(np.mean(ocr_time_list) * 1000)}")

        # 输出识别结果
        self.logger.info("=" * 30 + f"识别结果" + "=" * 30)
        for name, hit in self.hit.items():
            hit_count = len(hit)
            self.logger.info(f"{name} : 共识别到{hit_count}个 缺少{len(self.data_name) - hit_count}个")
            missing = sorted(set(self.data_name) - hit)
            if missing:
                self.logger.info(f"❌ 缺少: {missing}")
            else:
                self.logger.info(" ✅ 全部目标物品已识别！")
            self.logger.info(f"已识别: {sorted(hit)}" + "\n")

    def process_run(self, name, frame_res, frame, function):
        """运行处理模块"""
        # 准备处理模块的目录和日志器
        stage_dir = Path(self.out_dir / name)
        stage_dir.mkdir(parents=True, exist_ok=True)
        logger = create_default_logger(name, stage_dir)
        # 记录单模块的处理开始时间
        process_after_start = time.perf_counter()
        # 运行处理模块，传递self, 模块名称，OCR结果，图片，日志器，目录
        function(self, name, frame_res, frame, logger, stage_dir)
        # 计算单模块的处理耗时
        process_after_time = time.perf_counter() - process_after_start
        self.logger.info(f"{name}处理耗时: {format_duration_with_ms(process_after_time * 1000)}")

    def run(self, frame_res, frame):
        """运行所有处理模块"""
        for stage in self.config.get("stages"):
            self.process_run(stage.get("name"), frame_res, frame, stage.get("fun"))