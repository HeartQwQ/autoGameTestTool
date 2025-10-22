import cv2


def exchange_shop_exchange_middle(self, name, frame_res, img, logger, stage_dir):
    logger.debug("=" * 20 + f"第{self.frame_idx}帧" + "=" * 20)

    # Step 1: 提取所有 OCR 文本
    ocr_texts = [cleaned_text for (cleaned_text, score, box_poi, box) in frame_res]
    logger.debug(f"OCR 识别结果: {ocr_texts}")

    # Step 2: 判断是否为兑换弹窗界面
    if "总计" not in ocr_texts:
        logger.info(f"⚠️ 不是兑换弹窗界面，跳过物品识别")
        return

    # Step 3: 在确认是兑换弹窗的前提下，识别 self.data_name(数值表.物品名称) 中的物品
    target = False  # 判断是否有找到目标物品
    for (cleaned_text, score, box_poi, box) in frame_res:
        # 判断当前物品是否在左下角
        if box_poi == "中间":
            # 不在物品表，或者已经命中过的物品，跳过
            if cleaned_text not in self.data_name or cleaned_text in self.hit[name]:
                continue

            target = True
            self.hit[name].add(cleaned_text)     # 识别到的加入集合，避免重复识别
            logger.info(f"🎯 识别到目标物品：{cleaned_text}")

            # 保存原图
            output_path = str(stage_dir / f"{name}_{cleaned_text}.jpg")
            cv2.imencode(".jpg", img)[1].tofile(output_path)

    if not target:
        logger.info("🔍 兑换弹窗界面已加载，但未发现新目标物品")

    logger.debug(f"当前已识别到的集合: {self.hit[name]}")
