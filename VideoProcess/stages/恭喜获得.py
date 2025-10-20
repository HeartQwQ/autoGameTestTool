def exchange_shop_congratulation(self, name, frame_res, img, logger, out_dir):
    logger.debug("=" * 20 + f"第{self.frame_idx}帧" + "=" * 20)
    logger.debug(f"OCR结果: {frame_res}")
    logger.debug(f"已命中集合: {self.hit[name]}")
    logger.debug(f"识别命中后的存储路径: {out_dir}")