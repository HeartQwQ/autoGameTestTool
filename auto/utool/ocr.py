# -*- coding: utf-8 -*-
import time
import warnings
from pathlib import Path
from utool.getWindow import capture_window, snap_center_rect, text_center, mouse_click, slide_from

warnings.filterwarnings("ignore", message="No ccache found")


def ocr_task(self, task: dict) -> bool:
    # 配置参数
    target = task["识别内容"]
    max_tr = task.get("识别次数", self.cfg["任务识别次数"])
    interval = task.get("识别间隔", self.cfg["任务识别间隔"])
    strategy = task.get("识别策略", 0)
    min_score = task.get("识别精度", 0.9)

    # 执行任务
    for i in range(1, max_tr + 1):
        base = self.log_dir / f"{task['任务名称']}" / f"{target}_第{i}次"
        Path(base).parent.mkdir(parents=True, exist_ok=True)
        paths = {
            "识别前": base.with_name(f"{target}_第{i}次_识别前.png"),
            "识别预览": base.with_name(f"{target}_第{i}次_识别预览.png"),
            "识别后": base.with_name(f"{target}_第{i}次_识别后.png"),
            "识别坐标": base.with_name(f"{target}_第{i}次_识别坐标.png")
        }

        print(f"[{i:03d}] 正在识别‘{target}’ …")
        img, info = capture_window(self.hwnd, paths["识别前"])
        print(f"      ✅ 窗口：{self.cfg['识别窗口']}  分辨率：{info["client_size"]}  坐标：{info["window_rect"]}")
        print(f"      ✅ 已对窗口进行截图，OCR识别中...")
        result = self.ocr.predict(img)
        print(f"      ✅ 已获得OCR结果，保存预览中...")

        for res in result:
            res.save_to_img(paths["识别预览"])

        print(f"      ✅ 保存成功，查找所有‘{target}’中...")
        hits = [
            (box, text, score)
            for res in result
            for box, text, score in zip(res['rec_boxes'], res['rec_texts'], res['rec_scores'])
            if target in text and score > min_score
        ]

        if hits:
            hit_info = [f"{text}({score:.3f})" for _, text, score in hits]
            print(f"      ✅ 已识别全部‘{target}’: " + ", ".join(hit_info))
            # 按索引识别
            if isinstance(strategy, int):
                idx = strategy
                box, text, score = hits[idx - 1]
                print(f"      ✅ 执行目标‘{text}’  置信度：{score}  坐标：{box}")
                # 矩阵图
                cx_img, cy_img = text_center(box, img, paths["识别后"])
                ops = task.get("执行操作")
                if isinstance(ops, str):
                    ops = [ops]
                for op in ops:
                    time.sleep(interval)
                    if op == "点击":
                        # 屏幕绝对坐标 & 点击
                        cx_screen = int(cx_img + info["client_screen_pos"][0])
                        cy_screen = int(cy_img + info["client_screen_pos"][1])
                        # 坐标图
                        snap_center_rect(cx_screen, cy_screen, save_path=paths["识别坐标"])
                        # 模拟点击
                        mouse_click(cx_screen, cy_screen)
                        print(f"      ✅ 已点击‘{target}’ 坐标={cx_screen, cy_screen}")

                    elif op == "截图":
                        name = task.get("截图名称", f"未指定名称-{task['任务名称']}-{task['识别内容']}.png")
                        path = Path("result") / name
                        path.parent.mkdir(parents=True, exist_ok=True)
                        capture_window(self.hwnd, path)

                    elif op == "滑动":
                        # 屏幕绝对坐标 & 点击
                        cx_screen = int(cx_img + info["client_screen_pos"][0])
                        cy_screen = int(cy_img + info["client_screen_pos"][1])
                        # 坐标图
                        snap_center_rect(cx_screen, cy_screen, save_path=paths["识别坐标"])
                        print(f"      ✅ 滑动起点坐标：{cx_screen}, {cy_screen}")

                print(f"")
                return True
            # 后续可以继续加 elif strategy == "max_score": ...
            else:
                raise ValueError(f"未知识别策略：{strategy}")

        else:
            print(f"      ❌ 本次识别未查找到‘{target}’")
            if i < max_tr:
                time.sleep(interval)

    print(f"      ❌ 未找到‘{target}’（重试{max_tr}次\n")
    return False

