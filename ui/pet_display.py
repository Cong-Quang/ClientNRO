"""Module chứa các hàm hiển thị thông tin pet."""

from logs.logger_config import logger, TerminalColors as C, print_header, print_separator
from ui.formatters import short_number
from ui.pet_status import get_pet_status_vietnamese, get_pet_status_short, get_pet_status_short_raw
from ui.table_utils import pad_colored


def display_pet_info(pet, username="Unknown", compact=False, idx: int = None):
    """Hiển thị thông tin chi tiết của đệ tử."""
    if not pet or not pet.have_pet:
        if compact:
            idx_str = f"[{idx}]" if idx is not None else ""
            print(f" {C.PURPLE}{idx_str:<4}{C.RESET}{C.YELLOW}{username:<12}{C.RESET} {C.DIM}│{C.RESET} {C.GREY}Không có đệ tử{C.RESET}")
        else:
            logger.info(f"[{username}] Không có thông tin đệ tử hoặc chưa nhận được dữ liệu từ server.")
        return

    if compact:
        # Compact mode: Single line display
        idx_str = f"[{idx}]" if idx is not None else ""
        status_raw = get_pet_status_short_raw(pet.pet_status)
        status_colored = get_pet_status_short(pet.pet_status)
        
        hp_s = short_number(pet.c_hp)
        mp_s = short_number(pet.c_mp)
        sm_s = short_number(pet.c_power)
        dam_s = short_number(getattr(pet, 'c_dam_full', getattr(pet, 'damage_full', 0)))
        
        # Build row with consistent padding
        row = (
            f" {C.PURPLE}{idx_str:<4}{C.RESET}"
            f"{C.YELLOW}{username:<12}{C.RESET} {C.DIM}│{C.RESET} "
            f"{C.GREEN}{pet.name:<10}{C.RESET} {C.DIM}│{C.RESET} "
            f"{pad_colored(status_colored, status_raw, 8)} {C.DIM}│{C.RESET} "
            f"{C.RED}{hp_s:>7}{C.RESET} {C.DIM}│{C.RESET} "
            f"{C.BLUE}{mp_s:>6}{C.RESET} {C.DIM}│{C.RESET} "
            f"{C.YELLOW}{sm_s:>7}{C.RESET} {C.DIM}│{C.RESET} "
            f"{C.PURPLE}{dam_s:>7}{C.RESET}"
        )
        
        # Alternate row colors
        if idx is not None and idx % 2 == 0:
            print(f"{C.DIM}{row}{C.RESET}")
        else:
            print(row)
    else:
        # Detailed mode
        print_header(f"[PET] De Tu - {username}", width=50, color=C.CYAN)
        print(f"  {C.GREEN}Tên      :{C.RESET} {C.BRIGHT_WHITE}{pet.name}{C.RESET}")
        print(f"  {C.GREEN}Trạng thái:{C.RESET} {get_pet_status_vietnamese(pet.pet_status)}")
        print(f"  {C.GREEN}HP       :{C.RESET} {C.RED}{pet.c_hp:,}{C.RESET} / {pet.c_hp_full:,}")
        print(f"  {C.GREEN}MP       :{C.RESET} {C.BLUE}{pet.c_mp:,}{C.RESET} / {pet.c_mp_full:,}")
        print(f"  {C.GREEN}Sức đánh :{C.RESET} {C.PURPLE}{pet.c_dam_full:,}{C.RESET}")
        print(f"  {C.GREEN}Sức mạnh :{C.RESET} {C.YELLOW}{pet.c_power:,}{C.RESET}")
        print(f"  {C.GREEN}Tiềm năng:{C.RESET} {C.CYAN}{pet.c_tiem_nang:,}{C.RESET}")
        print(f"  {C.GREEN}Phòng thủ:{C.RESET} {pet.c_def_full:,}")
        print(f"  {C.GREEN}Chí mạng :{C.RESET} {pet.c_critical_full}%")
        print(f"  {C.GREEN}Thể lực  :{C.RESET} {pet.c_stamina:,} / {pet.c_max_stamina:,}")
        print_separator(50, color=C.CYAN)


def display_pet_help():
    """Hiển thị các lệnh có sẵn cho đệ tử."""
    print_header("[PET] Lenh De Tu", width=50, color=C.CYAN)
    commands = [
        ("pet info", "Hiển thị thông tin chi tiết đệ tử"),
        ("pet follow", "Ra lệnh đệ tử đi theo"),
        ("pet protect", "Ra lệnh đệ tử bảo vệ"),
        ("pet attack", "Ra lệnh đệ tử tấn công"),
        ("pet home", "Ra lệnh đệ tử về nhà"),
    ]
    for cmd, desc in commands:
        print(f"  {C.GREEN}{cmd:<14}{C.RESET} {C.DIM}-{C.RESET} {desc}")
    print_separator(50, color=C.CYAN)
