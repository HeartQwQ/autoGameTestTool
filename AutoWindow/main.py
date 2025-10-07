import json
import time
from pathlib import Path
from paddleocr import PaddleOCR
from utool.log import setup_logger
from utool.ocr import ocr_task
from utool.getWindow import find_window, tap


# ---------------- 配置 ----------------
LOG_DIR = Path("logs") / time.strftime("%m%d_%H%M%S")
# 开启日志模块
setup_logger(log_dir=LOG_DIR, log_name="日志.log")
# 获取任务配置
task_cfg = json.loads(Path("json/task1.json").read_text(encoding='utf-8'))
# data = json.loads(Path("json/data.json").read_text(encoding='utf-8'))


# ---------------- 任务流程控制 ----------------
class TaskRunner:
    def __init__(self):
        self.cfg = task_cfg
        # self.data = data
        self.log_dir = LOG_DIR
        self.hwnd = find_window(self.cfg["识别窗口"])
        if self.hwnd:
            print(f"成功获取{self.cfg['识别窗口']}窗口，开始执行任务")
        print("初始化OCR中...")
        self.ocr = PaddleOCR(
            use_doc_orientation_classify=False,  # 不使用文档方向分类模型
            use_doc_unwarping=False,  # 不使用文本图像矫正模型
            use_textline_orientation=False,  # 不使用文本行方向分类模型
            device="gpu",  # 使用GPU推理
            text_rec_score_thresh=self.cfg.get("OCR置信度", 0.8),  # 只保留置信度0.8以上的结果
            text_detection_model_name="PP-OCRv5_mobile_det",  # 文本检测模块，使用轻量化模型
            # text_recognition_model_name="PP-OCRv5_mobile_rec",  # 文本识别模块，使用轻量化模型
        )
        print("初始化OCR完成")

    def run(self):
        queue = self.cfg["任务列表"]
        while queue:
            print(f"任务列表: {queue}")
            task = queue.pop(0)
            print(f"当前任务: {task}")
            print(f">>> 开始执行任务：{task['任务名称']}")
            if "OCR" in task.get("识别类型", ""):
                ok = ocr_task(self, task)
                if ok or task.get("超时跳过", False):  # 成功 || 超时即跳下一步
                    time.sleep(self.cfg["任务执行间隔"])
            elif "键盘" in task.get("识别类型", "") or "键盘" in task.get("操作类型", ""):
                ok = tap(task["执行操作"])
                if ok or task.get("超时跳过", False):  # 成功 || 超时即跳下一步
                    time.sleep(self.cfg["任务执行间隔"])
            else:
                print(f"❌ 任务链中断：{task['任务名称']}")
                break


if __name__ == "__main__":
    TaskRunner().run()