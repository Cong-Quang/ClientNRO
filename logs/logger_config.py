import logging
import sys

class TerminalColors:
    """Mã màu ANSI cho Terminal"""
    # Basic colors
    GREY = "\x1b[38;20m"
    BLUE = "\x1b[34;20m"
    YELLOW = "\x1b[33;20m"
    RED = "\x1b[31;20m"
    BOLD_RED = "\x1b[31;1m"
    GREEN = "\x1b[32;20m"
    CYAN = "\x1b[36;20m"
    PURPLE = "\x1b[35;20m"
    RESET = "\x1b[0m"
    
    # Text styles
    BOLD = "\x1b[1m"
    DIM = "\x1b[2m"
    UNDERLINE = "\x1b[4m"
    
    # Bright colors
    BRIGHT_GREEN = "\x1b[92m"
    BRIGHT_CYAN = "\x1b[96m"
    BRIGHT_YELLOW = "\x1b[93m"
    BRIGHT_WHITE = "\x1b[97m"


class Box:
    """ASCII box drawing characters - Compatible with all terminals"""
    # Simple ASCII characters for maximum compatibility
    H = "-"      # Horizontal
    V = "|"      # Vertical
    TL = "+"     # Top-left
    TR = "+"     # Top-right
    BL = "+"     # Bottom-left
    BR = "+"     # Bottom-right
    LT = "+"     # Left-T
    RT = "+"     # Right-T
    TT = "+"     # Top-T
    BT = "+"     # Bottom-T
    X = "+"      # Cross
    
    # Double line (same as single for ASCII)
    DH = "="     # Double horizontal
    DV = "|"     # Double vertical
    DTL = "+"    # Double top-left
    DTR = "+"    # Double top-right
    DBL = "+"    # Double bottom-left
    DBR = "+"    # Double bottom-right


def print_header(title: str, width: int = 60, color: str = None) -> None:
    """In header với box style."""
    C = TerminalColors
    B = Box
    col = color or C.CYAN
    
    # Calculate padding for centered title
    title_len = len(title)
    left_pad = (width - title_len - 2) // 2
    right_pad = width - title_len - 2 - left_pad
    
    print(f"{col}{B.TL}{B.H * width}{B.TR}{C.RESET}")
    print(f"{col}{B.V}{C.RESET}{' ' * left_pad}{C.BOLD}{C.BRIGHT_WHITE}{title}{C.RESET}{' ' * right_pad}{col}{B.V}{C.RESET}")
    print(f"{col}{B.BL}{B.H * width}{B.BR}{C.RESET}")


def print_separator(width: int = 60, char: str = None, color: str = None) -> None:
    """In đường phân cách."""
    C = TerminalColors
    col = color or C.DIM
    ch = char or Box.H
    print(f"{col}{ch * width}{C.RESET}")


def print_section_header(title: str, width: int = 50, color: str = None) -> None:
    """In section header nhỏ gọn."""
    C = TerminalColors
    B = Box
    col = color or C.PURPLE
    
    line = f"{B.LT}{B.H * 2} {title} "
    remaining = width - len(title) - 5
    if remaining > 0:
        line += B.H * remaining
    
    print(f"{col}{line}{C.RESET}")

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