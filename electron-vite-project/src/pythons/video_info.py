import sys
import json
import cv2


def log(msg: str):
    """将日志写入 stderr，不会干扰 stdout 的 JSON"""
    sys.stderr.write(f"[INFO] {msg}\n")
    sys.stderr.flush()  # 确保立即输出


def get_video_info(video_path):
    log("正在解析视频...")
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        sys.stderr.write("[ERROR] 无法打开视频文件\n")
        print(json.dumps({"success": False, "error": "无法打开视频"}))
        return {"error": "无法打开视频文件"}

    # 获取基本信息
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps if fps > 0 else 0

    cap.release()

    return {
        "时长": round(duration, 2),  # 秒
        "总帧数": frame_count,
        "帧率": round(fps, 2),
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "未提供视频路径"}))
        sys.exit(1)

    video_path = sys.argv[1]
    info = get_video_info(video_path)
    print(json.dumps(info, ensure_ascii=False))
    sys.stdout.flush()
