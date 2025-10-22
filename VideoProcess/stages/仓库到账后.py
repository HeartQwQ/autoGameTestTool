import re

import cv2


def normalize_for_upgrade(text: str) -> str:
    """仅对「可升级道具」尝试剥离等级后缀"""
    # 只剥离末尾的「数字+级」，且保留原始文本以防误伤
    return re.sub(r'\d+[级]?$', '', text).rstrip()


def exchange_shop_after(self, name, frame_res, img, logger, stage_dir):
    logger.debug("=" * 20 + f"第{self.frame_idx}帧" + "=" * 20)

    # Step 1: 提取所有 OCR 文本
    ocr_texts = [cleaned_text for (cleaned_text, score, box_poi, box) in frame_res]
    logger.debug(f"OCR 识别结果: {ocr_texts}")

    # Step 2: 判断是否为仓库界面
    if "更换形象" not in ocr_texts:
        logger.info(f"⚠️ 不是仓库界面，跳过物品识别")
        return

    # Step 3: 在确认是仓库的前提下，识别 self.data_name(数值表.物品名称) 中的物品
    target = False  # 判断是否有找到目标物品
    for (cleaned_text, score, box_poi, box) in frame_res:
        # 判断当前物品是否在左下角
        if box_poi == "左下" or box_poi == "左中":
            # 不在物品表，或者已经命中过的物品，跳过
            if cleaned_text not in self.data_name or cleaned_text in self.hit[name]:
                continue

            item_name = normalize_for_upgrade(cleaned_text)

            if item_name not in self.data_name or item_name in self.hit[name]:
                continue

            target = True
            self.hit[name].add(item_name)     # 识别到的加入集合，避免重复识别
            logger.info(f"🎯 识别到目标物品：{item_name}")

            # 保存原图
            output_path = str(stage_dir / f"{name}_{item_name}.jpg")
            cv2.imencode(".jpg", img)[1].tofile(output_path)

    if not target:
        logger.info("🔍 仓库界面已加载，但未发现新目标物品")

    logger.debug(f"当前已识别到的集合: {self.hit[name]}")

