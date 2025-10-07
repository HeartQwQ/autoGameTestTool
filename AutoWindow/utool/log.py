"""
log.py  终极版：进程结束前统一捕获 & 刷盘所有异常与日志
用法不变：
    from log import setup_logger
    logger = setup_logger()
"""
import builtins
import sys
import logging
import atexit
import queue
import threading
from pathlib import Path
from logging.handlers import QueueHandler, QueueListener
import functools
import time

_real_print = builtins.print


# -------------- 核心：setup_logger --------------
def setup_logger(
    name: str = "print_mirror",
    level: int = logging.INFO,
    fmt: str = "[%(asctime)s] %(levelname)s | %(message)s",
    datefmt: str = "%H:%M:%S",
    log_dir: Path | str | None = None,
    log_name: str = "日志.log",
) -> logging.Logger:
    if log_dir is None:
        log_dir = Path.cwd() / "logs" / time.strftime("%m%d_%H%M%S")
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / log_name

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 异步队列：保证崩溃也不丢日志
    log_queue: queue.SimpleQueue = queue.SimpleQueue()
    queue_handler = QueueHandler(log_queue)

    # 真正落盘的 handler
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(level)
    formatter = logging.Formatter(fmt=fmt, datefmt=datefmt)
    file_handler.setFormatter(formatter)

    console = logging.StreamHandler(sys.stdout)
    console.setLevel(level)
    console.setFormatter(formatter)

    # QueueListener 负责异步刷盘
    listener = QueueListener(log_queue, file_handler, console)
    listener.start()

    logger.addHandler(queue_handler)

    # 劫持 print
    def print(*args, **kwargs):
        safe_kwargs = {k: v for k, v in kwargs.items()
                       if k in {"exc_info", "stack_info", "extra"}}
        logger.info(" ".join(map(str, args)), **safe_kwargs)

    builtins.print = print

    # 未捕获异常 → 日志
    def log_except(exc_type, exc_value, exc_tb):
        logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_tb))

    sys.excepthook = log_except
    if hasattr(threading, "excepthook"):  # py3.8+
        threading.excepthook = lambda args: logger.error(
            "Uncaught exception in thread", exc_info=(args.exc_type, args.exc_value, args.exc_traceback)
        )

    # 进程退出前必刷盘
    @atexit.register
    def _finalize():
        listener.stop()
        file_handler.close()
        print("===== 日志已完整写入 =====")

    return logger