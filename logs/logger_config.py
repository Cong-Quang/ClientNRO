import logging
import sys

class TerminalColors:
    """Mã màu ANSI cho Terminal"""
    GREY = "\x1b[38;20m"
    BLUE = "\x1b[34;20m"
    YELLOW = "\x1b[33;20m"
    RED = "\x1b[31;20m"
    BOLD_RED = "\x1b[31;1m"
    GREEN = "\x1b[32;20m"
    CYAN = "\x1b[36;20m"
    PURPLE = "\x1b[35;20m"
    RESET = "\x1b[0m"

class ColoredFormatter(logging.Formatter):
    """Formatter tùy chỉnh để gán màu cho từng Level log"""
    
    # Định dạng: Giờ | Level (8 ký tự) | Message
    fmt_str = "%(asctime)s | %(levelname)-8s | %(message)s"

    FORMATS = {
        logging.DEBUG: f"{TerminalColors.GREY}%(asctime)s{TerminalColors.RESET} | {TerminalColors.CYAN}%(levelname)-8s{TerminalColors.RESET} | %(message)s",
        logging.INFO: f"{TerminalColors.GREY}%(asctime)s{TerminalColors.RESET} | {TerminalColors.GREEN}%(levelname)-8s{TerminalColors.RESET} | %(message)s",
        logging.WARNING: f"{TerminalColors.GREY}%(asctime)s{TerminalColors.RESET} | {TerminalColors.YELLOW}%(levelname)-8s{TerminalColors.RESET} | %(message)s",
        logging.ERROR: f"{TerminalColors.GREY}%(asctime)s{TerminalColors.RESET} | {TerminalColors.RED}%(levelname)-8s{TerminalColors.RESET} | %(message)s",
        logging.CRITICAL: f"{TerminalColors.GREY}%(asctime)s{TerminalColors.RESET} | {TerminalColors.BOLD_RED}%(levelname)-8s{TerminalColors.RESET} | %(message)s",
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt="%H:%M:%S")
        return formatter.format(record)

def setup_logger(name="Bot", level=logging.INFO):
    """Hàm khởi tạo logger để sử dụng ở các file khác"""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Tránh việc add handler nhiều lần nếu hàm này bị gọi lại
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(ColoredFormatter())
        logger.addHandler(handler)
    
    return logger

# Tạo sẵn một instance mặc định
logger = setup_logger("Main", level=logging.DEBUG)

def set_logger_status(is_enabled: bool):
    """Bật hoặc tắt logger."""
    logger.disabled = not is_enabled

set_logger_status(False)