"""Module chứa các hàm liên quan đến trạng thái pet."""

from logs.logger_config import TerminalColors as C


def get_pet_status_vietnamese(status: int) -> str:
    """Trả về trạng thái của đệ tử bằng tiếng Việt có màu."""
    status_map = {
        0: f"{C.GREEN}Đi theo{C.RESET}",
        1: f"{C.PURPLE}Bảo vệ{C.RESET}",
        2: f"{C.RED}Tấn công{C.RESET}",
        3: f"{C.YELLOW}Về nhà{C.RESET}",
        4: f"{C.CYAN}Hợp thể{C.RESET}",
        5: f"{C.BOLD_RED}Hợp thể VV{C.RESET}"
    }
    return status_map.get(status, f"Không xác định ({status})")


def get_pet_status_short(status: int) -> str:
    """Trả về trạng thái ngắn gọn có màu."""
    status_map = {
        0: f"{C.GREEN}Theo{C.RESET}",
        1: f"{C.PURPLE}B.Vệ{C.RESET}",
        2: f"{C.RED}T.Công{C.RESET}",
        3: f"{C.YELLOW}Về{C.RESET}",
        4: f"{C.CYAN}H.Thể{C.RESET}",
        5: f"{C.BOLD_RED}H.Thể VV{C.RESET}"
    }
    return status_map.get(status, f"Unk({status})")


def get_pet_status_short_raw(status: int) -> str:
    """Trả về trạng thái ngắn gọn không màu (dùng để căn chỉnh)."""
    status_map = {0: "Theo", 1: "B.Vệ", 2: "T.Công", 3: "Về", 4: "H.Thể", 5: "H.Thể VV"}
    return status_map.get(status, f"Unk({status})")
