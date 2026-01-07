"""Module chứa các hàm in headers và footers cho compact tables."""

from logs.logger_config import TerminalColors as C, Box as B


def print_compact_header_show():
    """Print header for compact 'show' command."""
    print(f"{C.CYAN}{B.TL}{B.H * 110}{B.TR}{C.RESET}")
    header = (
        f" {C.BOLD}{'#':<4}{C.RESET}"
        f"{C.BOLD}{'User':<12}{C.RESET} {C.DIM}│{C.RESET} "
        f"{C.BOLD}{'Map':<15}{C.RESET} {C.DIM}│{C.RESET} "
        f"{C.BOLD}{'ID/Khu':<6}{C.RESET} {C.DIM}│{C.RESET} "
        f"{C.BOLD}{'Tọa độ':<9}{C.RESET} {C.DIM}│{C.RESET} "
        f"{C.BOLD}{'HP':>7}{C.RESET} {C.DIM}│{C.RESET} "
        f"{C.BOLD}{'MP':>6}{C.RESET} {C.DIM}│{C.RESET} "
        f"{C.BOLD}{'SM':>7}{C.RESET} {C.DIM}│{C.RESET} "
        f"{C.BOLD}{'SĐ':>7}{C.RESET} {C.DIM}│{C.RESET} "
        f"{C.BOLD}{'F'}{C.RESET}"
    )
    print(header)
    print(f"{C.CYAN}{B.LT}{B.H * 110}{B.RT}{C.RESET}")


def print_compact_header_pet():
    """Print header for compact 'pet info' command."""
    print(f"{C.CYAN}{B.TL}{B.H * 90}{B.TR}{C.RESET}")
    header = (
        f" {C.BOLD}{'#':<4}{C.RESET}"
        f"{C.BOLD}{'User':<12}{C.RESET} {C.DIM}│{C.RESET} "
        f"{C.BOLD}{'Đệ tử':<10}{C.RESET} {C.DIM}│{C.RESET} "
        f"{C.BOLD}{'Trạng thái':<8}{C.RESET} {C.DIM}│{C.RESET} "
        f"{C.BOLD}{'HP':>7}{C.RESET} {C.DIM}│{C.RESET} "
        f"{C.BOLD}{'MP':>6}{C.RESET} {C.DIM}│{C.RESET} "
        f"{C.BOLD}{'SM':>7}{C.RESET} {C.DIM}│{C.RESET} "
        f"{C.BOLD}{'SĐ':>7}{C.RESET}"
    )
    print(header)
    print(f"{C.CYAN}{B.LT}{B.H * 90}{B.RT}{C.RESET}")


def print_compact_header_csgoc():
    """Print header for compact 'show csgoc' command."""
    print(f"{C.PURPLE}{B.TL}{B.H * 85}{B.TR}{C.RESET}")
    header = (
        f" {C.BOLD}{'#':<4}{C.RESET}"
        f"{C.BOLD}{'User':<12}{C.RESET} {C.DIM}│{C.RESET} "
        f"{C.BOLD}{'HP Gốc':>8}{C.RESET} {C.DIM}│{C.RESET} "
        f"{C.BOLD}{'MP Gốc':>7}{C.RESET} {C.DIM}│{C.RESET} "
        f"{C.BOLD}{'SĐ Gốc':>7}{C.RESET} {C.DIM}│{C.RESET} "
        f"{C.BOLD}{'Giáp':>7}{C.RESET} {C.DIM}│{C.RESET} "
        f"{C.BOLD}{'CM':>5}{C.RESET} {C.DIM}│{C.RESET} "
        f"{C.BOLD}{'Tiềm năng':>8}{C.RESET}"
    )
    print(header)
    print(f"{C.PURPLE}{B.LT}{B.H * 85}{B.RT}{C.RESET}")


def print_compact_header_task():
    """Print header for compact 'show nhiemvu' command."""
    print(f"{C.YELLOW}{B.TL}{B.H * 105}{B.TR}{C.RESET}")
    header = (
        f" {C.BOLD}{'#':<3}{C.RESET} {C.DIM}│{C.RESET} "
        f"{C.BOLD}{'User':<12}{C.RESET} {C.DIM}│{C.RESET} "
        f"{C.BOLD}{'ID':<3}{C.RESET} {C.DIM}│{C.RESET} "
        f"{C.BOLD}{'Tên Nhiệm Vụ':<28}{C.RESET} {C.DIM}│{C.RESET} "
        f"{C.BOLD}{'Bước hiện tại':<23}{C.RESET} {C.DIM}│{C.RESET} "
        f"{C.BOLD}{'Tiến độ'}{C.RESET}"
    )
    print(header)
    print(f"{C.YELLOW}{B.LT}{B.H * 105}{B.RT}{C.RESET}")


def print_compact_header_autoquest():
    """Print header for compact 'autoquest status' command."""
    print(f"{C.BRIGHT_GREEN}{B.TL}{B.H * 98}{B.TR}{C.RESET}")
    header = (
        f" {C.BOLD}{'User':<14}{C.RESET} {C.DIM}|{C.RESET} "
        f"{C.BOLD}{'On':<4}{C.RESET} {C.DIM}|{C.RESET} "
        f"{C.BOLD}{'Trạng thái':<20}{C.RESET} {C.DIM}|{C.RESET} "
        f"{C.BOLD}{'NV':<5}{C.RESET} {C.DIM}|{C.RESET} "
        f"{C.BOLD}{'Quái':<6}{C.RESET} {C.DIM}|{C.RESET} "
        f"{C.BOLD}{'Nhiệm vụ':<16}{C.RESET} {C.DIM}|{C.RESET} "
        f"{C.BOLD}{'Tiến độ'}{C.RESET}"
    )
    print(header)
    print(f"{C.BRIGHT_GREEN}{B.LT}{B.H * 98}{B.RT}{C.RESET}")


def print_compact_footer(width: int = 90, color: str = None):
    """Print footer line for compact tables."""
    col = color or C.CYAN
    print(f"{col}{B.BL}{B.H * width}{B.BR}{C.RESET}")
