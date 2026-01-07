"""Module chứa các utilities cho việc render table."""

from logs.logger_config import TerminalColors as C, Box as B


def pad_colored(text: str, raw_text: str, width: int, align: str = 'left') -> str:
    """Pad a colored string based on its raw (uncolored) length."""
    raw_len = len(raw_text)
    if align == 'right':
        padding = ' ' * max(0, width - raw_len)
        return padding + text
    else:
        padding = ' ' * max(0, width - raw_len)
        return text + padding


def print_table_header(columns: list, widths: list, sep: str = " │ ") -> None:
    """Print a formatted table header with box drawing."""
    parts = []
    for col, w in zip(columns, widths):
        parts.append(f"{C.BOLD}{C.BRIGHT_CYAN}{col:<{w}}{C.RESET}")
    header = sep.join(parts)
    print(f"{C.CYAN}{B.LT}{B.H * (sum(widths) + len(sep) * (len(columns) - 1))}{C.RESET}")
    print(f"{C.CYAN}{B.V}{C.RESET} {header} {C.CYAN}{B.V}{C.RESET}")
    print(f"{C.CYAN}{B.LT}{B.H * (sum(widths) + len(sep) * (len(columns) - 1))}{C.RESET}")


def print_compact_divider(width: int = 80) -> None:
    """Print a subtle divider line."""
    print(f"{C.DIM}{B.H * width}{C.RESET}")
