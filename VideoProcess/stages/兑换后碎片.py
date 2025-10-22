import cv2


def exchange_shop_exchange_after(self, name, frame_res, img, logger, stage_dir):
    logger.debug("=" * 20 + f"第{self.frame_idx}帧" + "=" * 20)

    # Step 1: 提取所有 OCR 文本和对应 box
    ocr_texts = [cleaned_text for (cleaned_text, score, box_poi, box) in frame_res]
    logger.debug(f"OCR 识别结果: {ocr_texts}")

    # Step 2: 判断是否为兑换界面
    if "碎片兑换" not in ocr_texts:
        logger.info(f"⚠️ 不是兑换界面，跳过物品识别")
        return

    # Step 3: 在确认是兑换的前提下
    target = False  # 判断是否有找到目标物品
    for (cleaned_text, score, box_poi, box) in frame_res:
        # 尝试将文本转为整数
        try:
            shard_num = int(cleaned_text)
        except ValueError:
            continue  # 不是数字，跳过

        # 检查该碎片数是否在“兑换前”映射中
        if shard_num not in self.redeem_shards_after_map:
            continue

        # 根据兑换数量获取物品名称
        item_name = self.redeem_shards_after_map[shard_num]

        # 避免重复识别同一物品
        if item_name in self.hit[name]:
            continue

        target = True
        self.hit[name].add(item_name)
        logger.info(f"🎯 通过碎片数 {shard_num} 识别到物品：{item_name}")

        # 用物品名称保存图片
        output_path = str(stage_dir / f"{name}_{item_name}_{shard_num}.jpg")
        cv2.imencode(".jpg", img)[1].tofile(output_path)

    if not target:
        logger.info("🔍 仓库界面已加载，但未发现新目标物品")

    logger.debug(f"当前已识别到的集合: {self.hit[name]}")
