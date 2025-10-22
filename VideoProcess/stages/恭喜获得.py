import re

import cv2


def exchange_shop_congratulation(self, name, frame_res, img, logger, stage_dir):
    logger.debug("=" * 20 + f"第{self.frame_idx}帧" + "=" * 20)

    # Step 1: 提取所有 OCR 文本
    ocr_texts = [cleaned_text for (cleaned_text, score, box_poi, box) in frame_res]
    logger.debug(f"OCR 识别结果: {ocr_texts}")

    # Step 2: 判断是否为仓库界面
    if "恭喜获得" in ocr_texts:
        if "炫耀" in ocr_texts:
            for (cleaned_text, score, box_poi, box) in frame_res:
                if cleaned_text not in self.data_name or cleaned_text in self.hit[name]["illustration"]:
                    continue
                self.hit[name]["illustration"].add(cleaned_text)
                logger.info(f"🎯 识别到立绘物品：{cleaned_text}")

                # 保存原图
                output_path = str(stage_dir / f"{name}_立绘_{cleaned_text}.jpg")
                cv2.imencode(".jpg", img)[1].tofile(output_path)
                
        else:
            for (cleaned_text, score, box_poi, box) in frame_res:
                if cleaned_text not in self.data_name or cleaned_text in self.hit[name]["icon"]:
                    continue
                self.hit[name]["icon"].add(cleaned_text)
                logger.info(f"🎯 识别到图标物品：{cleaned_text}")

                # 保存原图
                output_path = str(stage_dir / f"{name}_图标_{cleaned_text}.jpg")
                cv2.imencode(".jpg", img)[1].tofile(output_path)

    elif "游戏空间" in ocr_texts:
        for (cleaned_text, score, box_poi, box) in frame_res:
            if cleaned_text not in self.data_name or cleaned_text in self.hit[name]["share"]:
                continue
            self.hit[name]["share"].add(cleaned_text)
            logger.info(f"🎯 识别到分享物品：{cleaned_text}")

            # 保存原图
            output_path = str(stage_dir / f"{name}_分享_{cleaned_text}.jpg")
            cv2.imencode(".jpg", img)[1].tofile(output_path)
    else:
        logger.info(f"⚠️ 不是恭喜获得界面，跳过物品识别")


    logger.debug(f"当前已识别到的集合: {self.hit[name]}")