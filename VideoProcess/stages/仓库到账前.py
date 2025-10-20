import cv2


def exchange_shop_before(self, name, frame_res, img, logger, stage_dir):
    logger.debug("=" * 20 + f"第{self.frame_idx}帧" + "=" * 20)
    logger.debug(f"OCR结果: {frame_res}")
    logger.debug(f"已命中集合: {self.hit[name]}")
