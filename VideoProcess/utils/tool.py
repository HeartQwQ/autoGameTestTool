import re
import time

import cv2
import imagehash
from PIL import Image


def format_duration_with_ms(total_ms: float) -> str:
    """
    将总毫秒数格式化为：
      - <1000 ms → "xxx ms"
      - ≥1000 ms → "x秒"
      - ≥60000 ms → "x分y秒"
    :param total_ms: 总毫秒数
    :return: 格式化后的字符串
    """
    total_ms = int(round(total_ms))  # 转为整数毫秒，避免浮点误差

    if total_ms < 1000:
        return f"{total_ms} ms"

    seconds_total = total_ms // 1000

    if seconds_total < 60:
        return f"{seconds_total} 秒"

    minutes = seconds_total // 60
    seconds = seconds_total % 60
    return f"{minutes}分{seconds}秒"


def clean_text(text: str) -> str:
    """
    保留中文、英文字母（a-z, A-Z）、数字（0-9），移除所有其他字符
    :param text: 原始文本
    :return: 清理后的文本
    """
    cleaned = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff]', '', text)
    return cleaned


def clean_json_strings(obj):
    """
    递归遍历 JSON 对象（dict/list），清洗所有字符串值
    """
    if isinstance(obj, dict):
        return {key: clean_json_strings(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [clean_json_strings(item) for item in obj]
    elif isinstance(obj, str):
        return clean_text(obj)
    else:
        return obj


def get_video_info(cap, target_fps):
    """
    获取视频基本信息
    :param cap: 视频捕获对象
    :param target_fps: 目标帧率
    :return: fps（帧率）, frame_count（总帧数）, width（宽）, height（高）, duration（时长）, interval（间隔）
    """
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration = frame_count / fps if fps > 0 else 0
    # 根据帧率计算间隔，一秒3张
    interval = round(fps / target_fps)

    return {
        "fps": fps,
        "frame_count": frame_count,
        "width": width,
        "height": height,
        "duration": duration,
        "interval": interval
    }


def frame_to_phash(frame, hash_size=16, last_hash=None, hamming_threshold=12):
    """
    将 OpenCV 帧转换为 pHash，并计算汉明距离判断是否是重复帧
    :param frame: 帧
    :param hash_size: pHash 精度（8/16，越大越准但慢），默认16
    :param last_hash: 上一个哈希，默认None
    :param hamming_threshold: 汉明距离，越小越敏感（推荐 8~20），默认12
    :return: current_hash（当前哈希）, is_duplicate（是否重复）, hamming_dist（汉明距离）, phash_process_time（处理时间）
    """
    phash_start = time.perf_counter()
    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    current_hash = imagehash.phash(img, hash_size=hash_size)
    is_duplicate = False
    hamming_dist = 0
    if last_hash is not None:
        hamming_dist = current_hash - last_hash
        if hamming_dist <= hamming_threshold:
            is_duplicate = True
    phash_process_time = time.perf_counter() - phash_start

    return {
        "current_hash": current_hash,
        "is_duplicate": is_duplicate,
        "hamming_dist": hamming_dist,
        "phash_process_time": phash_process_time
    }


def get_box_position(box, img):
    """
    判断 box 在图像九宫格中的方位
    :param box: [x1, y1, x2, y2] —— 两点式矩形框
    :param img: 图像
    :return:
            "左上"、"上中"、"右上"、
            "左中"、"中间"、"右中"、
            "左下"、"下中"、"右下"
    """
    h, w = img.shape[:2]

    x1, y1, x2, y2 = box
    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2

    # 计算每个区域的边界
    left_bound = int(w / 4)
    right_bound = int(w * 3 / 4)
    top_bound = int(h / 4)
    bottom_bound = int(h * 3 / 4)

    # 画垂直线（左右两根）
    cv2.line(img, (left_bound, 0), (left_bound, h), (0, 255, 0), 2)
    cv2.line(img, (right_bound, 0), (right_bound, h), (0, 255, 0), 2)
    # 画水平线（上下两根）
    cv2.line(img, (0, top_bound), (w, top_bound), (0, 255, 0), 2)
    cv2.line(img, (0, bottom_bound), (w, bottom_bound), (0, 255, 0), 2)

    # 确定水平位置
    if center_x < left_bound:
        horizontal = "左"
    elif center_x > right_bound:
        horizontal = "右"
    else:
        horizontal = "中"

    # 确定垂直位置
    if center_y < top_bound:
        vertical = "上"
    elif center_y > bottom_bound:
        vertical = "下"
    else:
        vertical = "中"

    if horizontal == "中" and vertical == "中":
        return "中间"
    elif horizontal == "中":
        return vertical + horizontal
    else:
        return horizontal + vertical