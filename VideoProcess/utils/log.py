import logging
import sys
import threading
from pathlib import Path
from typing import Optional, Union


# 线程锁，确保logger创建的原子性
_logger_lock = threading.Lock()
# 缓存已创建的logger实例
_logger_cache: dict[str, logging.Logger] = {}


def setup_logger(
        name: str,
        log_file: Optional[Union[str, Path]] = None,
        console_level: int = logging.INFO,
        file_level: int = logging.DEBUG,
        max_bytes: int = 50 * 1024 * 1024,  # 10MB
        backup_count: int = 5
) -> logging.Logger:
    """
    设置并返回一个配置好的logger实例

    Args:
        name: logger名称
        log_file: 日志文件路径，如果为None则不写入文件
        console_level: 控制台日志级别
        file_level: 文件日志级别
        max_bytes: 日志文件最大字节数（用于轮转）
        backup_count: 保留的备份文件数量

    Returns:
        配置好的logger实例

    Raises:
        ValueError: 当参数无效时
        OSError: 当无法创建日志文件时
    """

    # 参数验证
    if not name or not isinstance(name, str):
        raise ValueError("Logger name must be a non-empty string")

    # 检查缓存，避免重复创建
    with _logger_lock:
        if name in _logger_cache:
            return _logger_cache[name]

    # 创建logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # 设置为最低级别，由handler控制实际输出级别
    logger.propagate = False

    # 清空已存在的handlers，避免重复
    logger.handlers.clear()

    # 日志格式
    fmt = "{asctime}.{msecs:03.0f} | {levelname:<8} | {name} | {message}"
    datefmt = "%Y-%m-%d %H:%M:%S"

    try:
        # 文件handler（如果指定了日志文件）
        if log_file:
            log_path = Path(log_file)

            # 确保日志目录存在
            log_path.parent.mkdir(parents=True, exist_ok=True)

            # 使用RotatingFileHandler支持日志轮转
            from logging.handlers import RotatingFileHandler
            fh = RotatingFileHandler(
                log_path,
                encoding="utf-8",
                maxBytes=max_bytes,
                backupCount=backup_count
            )
            fh.setLevel(file_level)
            fh.setFormatter(logging.Formatter(fmt, style="{", datefmt=datefmt))
            logger.addHandler(fh)

        # 控制台handler
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(console_level)

        # 根据配置决定是否使用颜色格式化器
        ch.setFormatter(logging.Formatter(fmt, style="{", datefmt=datefmt))

        logger.addHandler(ch)

        # 缓存logger实例
        with _logger_lock:
            _logger_cache[name] = logger

        return logger

    except (OSError, IOError) as e:
        raise OSError(f"Failed to create log file or directory: {e}")


def get_logger(name: str) -> Optional[logging.Logger]:
    """
    获取已创建的logger实例

    Args:
        name: logger名称

    Returns:
        logger实例，如果不存在则返回None
    """
    return _logger_cache.get(name)


def clear_logger(name: str) -> bool:
    """
    清除指定名称的logger缓存

    Args:
        name: logger名称

    Returns:
        如果成功清除返回True，如果不存在返回False
    """
    with _logger_lock:
        if name in _logger_cache:
            logger = _logger_cache[name]
            # 清理handler
            for handler in logger.handlers[:]:
                handler.close()
                logger.removeHandler(handler)
            del _logger_cache[name]
            return True
    return False


# 便捷函数，创建默认logger
def create_default_logger(name: str, log_dir: Path) -> logging.Logger:
    """创建带有默认配置的logger"""
    return setup_logger(
        name=name,
        log_file=log_dir / f"{name}.log",
        console_level=logging.INFO,
        file_level=logging.DEBUG
    )
