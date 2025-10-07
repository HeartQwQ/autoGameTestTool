import logging
import sys
from pathlib import Path


class ColoredFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG: "\033[36m",
        logging.INFO: "\033[32m",
        logging.WARNING: "\033[33m",
        logging.ERROR: "\033[31m",
        logging.CRITICAL: "\033[35m",
    }
    RESET = "\033[0m"

    def format(self, record):
        color = self.COLORS.get(record.levelno, "")
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logger(name: str, log_file: Path):
    logging.root.handlers.clear()
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False  # 关键：不向根 logger 传递消息

    # 日志格式
    fmt = "{asctime}.{msecs:03.0f} | {levelname} | {name} | {message}"
    datefmt = "%Y-%m-%d %H:%M:%S"

    # 文件 handler
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.DEBUG)

    # 控制台 handler（带颜色）
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)

    fh.setFormatter(logging.Formatter(fmt, style="{", datefmt=datefmt))
    ch.setFormatter(ColoredFormatter(fmt, style="{", datefmt=datefmt))

    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger
