# ui.py - Giao diện Terminal với Box Drawing và Color Formatting
from logs.logger_config import logger, TerminalColors, Box, print_header, print_separator, print_section_header

# Alias for cleaner code
C = TerminalColors
B = Box


def short_number(num: int) -> str:
    """Định dạng số ngắn gọn (VD: 1.2tr, 5.5tỷ)."""
    if num >= 1_000_000_000:
        return f"{num/1_000_000_000:.1f}tỷ".replace('.0tỷ', 'tỷ')
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}tr".replace('.0tr', 'tr')
    if num >= 1_000:
        return f"{num/1_000:.1f}k".replace('.0k', 'k')
    return str(num)


# ═══════════════════════════════════════════════════════════════════════════════
# PET STATUS HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

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


# ═══════════════════════════════════════════════════════════════════════════════
# TABLE RENDERING UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

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


# ═══════════════════════════════════════════════════════════════════════════════
# PET DISPLAY
# ═══════════════════════════════════════════════════════════════════════════════

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


# ═══════════════════════════════════════════════════════════════════════════════
# CHARACTER STATUS DISPLAY
# ═══════════════════════════════════════════════════════════════════════════════

def display_character_base_info(account):
    """Hiển thị thông tin cơ bản của tài khoản."""
    char = account.char
    
    print_header(f"[CHAR] {account.username}", width=55, color=C.CYAN)
    
    # Status with color
    status_text = account.status
    if account.status == "Logged In":
        status_color = C.BRIGHT_GREEN
        if not char.name:
            status_text = "Loading..."
    elif account.status == "Reconnecting":
        status_color = C.BRIGHT_YELLOW
    else:
        status_color = C.RED
    
    print(f"  {C.DIM}Trạng thái:{C.RESET} {status_color}{status_text}{C.RESET}")
    
    # Proxy info
    proxy_info = "Local IP"
    if account.proxy:
        try:
            ip_part = account.proxy.split('@')[-1]
            proxy_info = f"Proxy @ {ip_part}"
        except:
            proxy_info = "Proxy"
    print(f"  {C.DIM}Kết nối   :{C.RESET} {C.PURPLE}{proxy_info}{C.RESET}")
    
    if char.name:
        print(f"  {C.DIM}Nhân vật  :{C.RESET} {C.BRIGHT_WHITE}{char.name}{C.RESET} {C.DIM}(ID: {char.char_id}){C.RESET}")


def display_character_status(account, compact=False, idx: int = None):
    """Hiển thị thông tin trạng thái của một tài khoản."""
    char = account.char
    map_info = account.controller.map_info

    if not char.name:
        if compact:
            idx_str = f"[{idx}]" if idx is not None else ""
            status = account.status
            if status == "Logged In":
                status = "Loading..."
                status_col = C.YELLOW
            elif status == "Reconnecting":
                status_col = C.YELLOW
            else:
                status_col = C.RED
            print(f" {C.PURPLE}{idx_str:<4}{C.RESET}{C.YELLOW}{account.username:<12}{C.RESET} {C.DIM}│{C.RESET} {status_col}{status:<15}{C.RESET}")
        else:
            display_character_base_info(account)
        return

    if compact:
        # Compact single-line mode
        idx_str = f"[{idx}]" if idx is not None else ""
        
        hp_s = short_number(char.c_hp)
        mp_s = short_number(char.c_mp)
        pow_s = short_number(char.c_power)
        dam_s = short_number(getattr(char, 'c_dam_full', 0))
        
        map_name = map_info.get('name', 'N/A')
        if len(map_name) > 15:
            map_name = map_name[:13] + ".."
        map_id = str(map_info.get('id', '?'))
        zone_id = str(map_info.get('zone', '?'))
        coords = f"{char.cx},{char.cy}"
        
        # Function status indicators
        ap_on = account.controller.auto_play.interval
        apet_on = account.controller.auto_pet.is_running
        aquest_on = getattr(account.controller.auto_quest, 'is_running', False)
        
        funcs = ""
        if ap_on:
            funcs += f"{C.BRIGHT_GREEN}[A]{C.RESET}"
        if apet_on:
            funcs += f"{C.BRIGHT_CYAN}[P]{C.RESET}"
        if aquest_on:
            funcs += f"{C.YELLOW}[Q]{C.RESET}"
            
        funcs = funcs if funcs else f"{C.DIM}-{C.RESET}"
        
        row = (
            f" {C.PURPLE}{idx_str:<4}{C.RESET}"
            f"{C.YELLOW}{account.username:<12}{C.RESET} {C.DIM}|{C.RESET} "
            f"{C.CYAN}{map_name:<15}{C.RESET} {C.DIM}|{C.RESET} "
            f"{C.PURPLE}{map_id:>3}{C.RESET}{C.DIM}/{C.RESET}{C.BLUE}{zone_id:<2}{C.RESET} {C.DIM}|{C.RESET} "
            f"{C.GREY}{coords:<9}{C.RESET} {C.DIM}|{C.RESET} "
            f"{C.RED}{hp_s:>7}{C.RESET} {C.DIM}|{C.RESET} "
            f"{C.BLUE}{mp_s:>6}{C.RESET} {C.DIM}|{C.RESET} "
            f"{C.YELLOW}{pow_s:>7}{C.RESET} {C.DIM}|{C.RESET} "
            f"{C.PURPLE}{dam_s:>7}{C.RESET} {C.DIM}|{C.RESET} {funcs}"
        )
        print(row)
    else:
        # Detailed mode
        display_character_base_info(account)
        
        print_section_header("Vị trí & Chỉ số", width=55, color=C.CYAN)
        print(f"  {C.GREEN}Vị trí  :{C.RESET} {C.BRIGHT_WHITE}{map_info.get('name', 'N/A')}{C.RESET} "
              f"{C.DIM}[ID:{C.RESET}{C.YELLOW}{map_info.get('id', '?')}{C.RESET}{C.DIM}]{C.RESET} "
              f"{C.DIM}Khu{C.RESET} {C.CYAN}{map_info.get('zone', '?')}{C.RESET} "
              f"{C.DIM}({C.RESET}{C.GREY}{char.cx},{char.cy}{C.RESET}{C.DIM}){C.RESET}")
        print(f"  {C.GREEN}HP      :{C.RESET} {C.RED}{char.c_hp:,}{C.RESET} / {char.c_hp_full:,}")
        print(f"  {C.GREEN}MP      :{C.RESET} {C.BLUE}{char.c_mp:,}{C.RESET} / {char.c_mp_full:,}")
        print(f"  {C.GREEN}Sức mạnh:{C.RESET} {C.YELLOW}{char.c_power:,}{C.RESET}")
        print(f"  {C.GREEN}Sức đánh:{C.RESET} {C.PURPLE}{getattr(char, 'c_dam_full', 0):,}{C.RESET}")
        print(f"  {C.GREEN}Tiềm năng:{C.RESET} {C.CYAN}{getattr(char, 'c_tiem_nang', 0):,}{C.RESET}")

        print_section_header("Tài sản", width=55, color=C.CYAN)
        print(f"  {C.GREEN}Vàng    :{C.RESET} {C.YELLOW}{getattr(char, 'xu', 0):,}{C.RESET}")
        print(f"  {C.GREEN}Ngọc    :{C.RESET} {C.BRIGHT_GREEN}{getattr(char, 'luong', 0):,}{C.RESET}")
        print(f"  {C.GREEN}Ngọc khóa:{C.RESET} {C.PURPLE}{getattr(char, 'luong_khoa', 0):,}{C.RESET}")
        
        print_section_header("Chức năng", width=55, color=C.CYAN)
        ap_status = f"{C.BRIGHT_GREEN}[ON]{C.RESET}" if account.controller.auto_play.interval else f"{C.RED}[OFF]{C.RESET}"
        apet_status = f"{C.BRIGHT_GREEN}[ON]{C.RESET}" if account.controller.auto_pet.is_running else f"{C.RED}[OFF]{C.RESET}"
        aquest_status = f"{C.BRIGHT_GREEN}[ON]{C.RESET}" if getattr(account.controller.auto_quest, 'is_running', False) else f"{C.RED}[OFF]{C.RESET}"
        
        print(f"  {C.DIM}AutoPlay :{C.RESET} {ap_status}    {C.DIM}AutoPet:{C.RESET} {apet_status}    {C.DIM}AutoQuest:{C.RESET} {aquest_status}")

        # Pet info if available
        pet = account.pet
        if pet and pet.have_pet:
            print_section_header(f"Đệ tử: {pet.name}", width=55, color=C.CYAN)
            print(f"  {C.GREEN}HP:{C.RESET} {C.RED}{pet.c_hp:,}{C.RESET}/{pet.c_hp_full:,} "
                  f"{C.DIM}│{C.RESET} {C.GREEN}MP:{C.RESET} {C.BLUE}{pet.c_mp:,}{C.RESET}/{pet.c_mp_full:,} "
                  f"{C.DIM}│{C.RESET} {C.GREEN}SM:{C.RESET} {C.YELLOW}{pet.c_power:,}{C.RESET}")
        
        print_separator(55, color=C.CYAN)


def display_character_base_stats(account, compact=False, idx: int = None):
    """Hiển thị thông tin chỉ số GỐC của nhân vật."""
    char = account.char
    
    if compact:
        idx_str = f"[{idx}]" if idx is not None else ""
        hp_s = short_number(char.c_hp_goc)
        mp_s = short_number(char.c_mp_goc)
        dam_s = short_number(char.c_dam_goc)
        def_s = short_number(getattr(char, 'c_def_goc', 0))
        crit_s = f"{getattr(char, 'c_critical_goc', 0)}%"
        tn_s = short_number(getattr(char, 'c_tiem_nang', 0))
        
        row = (
            f" {C.PURPLE}{idx_str:<4}{C.RESET}"
            f"{C.YELLOW}{account.username:<12}{C.RESET} {C.DIM}│{C.RESET} "
            f"{C.RED}{hp_s:>8}{C.RESET} {C.DIM}│{C.RESET} "
            f"{C.BLUE}{mp_s:>7}{C.RESET} {C.DIM}│{C.RESET} "
            f"{C.PURPLE}{dam_s:>7}{C.RESET} {C.DIM}│{C.RESET} "
            f"{C.GREY}{def_s:>7}{C.RESET} {C.DIM}│{C.RESET} "
            f"{C.CYAN}{crit_s:>5}{C.RESET} {C.DIM}│{C.RESET} "
            f"{C.YELLOW}{tn_s:>8}{C.RESET}"
        )
        
        if idx is not None and idx % 2 == 0:
            print(f"{C.DIM}{row}{C.RESET}")
        else:
            print(row)
    else:
        print_header(f"[STATS] Chi So Goc - {account.username}", width=50, color=C.PURPLE)
        print(f"  {C.GREEN}HP Gốc      :{C.RESET} {C.RED}{char.c_hp_goc:,}{C.RESET}")
        print(f"  {C.GREEN}MP Gốc      :{C.RESET} {C.BLUE}{char.c_mp_goc:,}{C.RESET}")
        print(f"  {C.GREEN}Sức đánh Gốc:{C.RESET} {C.PURPLE}{char.c_dam_goc:,}{C.RESET}")
        print(f"  {C.GREEN}Giáp Gốc    :{C.RESET} {getattr(char, 'c_def_goc', 0):,}")
        print(f"  {C.GREEN}Chí mạng Gốc:{C.RESET} {getattr(char, 'c_critical_goc', 0)}%")
        print(f"  {C.GREEN}Tiềm năng   :{C.RESET} {C.CYAN}{getattr(char, 'c_tiem_nang', 0):,}{C.RESET}")
        print_separator(50, color=C.PURPLE)


# ═══════════════════════════════════════════════════════════════════════════════
# TASK INFO DISPLAY
# ═══════════════════════════════════════════════════════════════════════════════

def display_task_info(account, compact=False, idx: int = None, print_output=True):
    """Hiển thị thông tin nhiệm vụ."""
    task = account.char.task
    
    if not task or not task.name:
        if compact:
            idx_str = f"[{idx}]" if idx is not None else ""
            line = f" {C.PURPLE}{idx_str:<3}{C.RESET} {C.DIM}│{C.RESET} {C.YELLOW}{account.username:<12}{C.RESET} {C.DIM}│{C.RESET} {C.GREY}Chưa có dữ liệu{C.RESET}"
            if print_output: print(line)
            return line
        else:
            msg = f"{C.YELLOW}[{account.username}] Chưa có thông tin nhiệm vụ.{C.RESET}"
            if print_output: print(msg)
            return msg

    task_id = task.task_id
    raw_task_id = getattr(account.char, 'ctask_id', -1)
    task_name = task.name.strip()
    
    sub_name = ""
    if task.sub_names and 0 <= task.index < len(task.sub_names):
        sub_name = task.sub_names[task.index].strip()
    else:
        sub_name = "..."

    current = task.count
    required = 0
    if task.counts and 0 <= task.index < len(task.counts):
        required = task.counts[task.index]
    
    prog_str = f"{current}/{required}"
    
    if compact:
        idx_str = f"[{idx}]" if idx is not None else ""
        name_short = task_name if len(task_name) < 28 else task_name[:26] + ".."
        step_short = sub_name if len(sub_name) < 23 else sub_name[:21] + ".."
        
        # Highlight desync
        if raw_task_id != -1 and raw_task_id != task_id:
            prog_full = f"{C.RED}(!){C.RESET} {prog_str}"
        else:
            prog_full = prog_str

        line = (
            f" {C.PURPLE}{idx_str:<3}{C.RESET} {C.DIM}│{C.RESET} "
            f"{C.YELLOW}{account.username:<12}{C.RESET} {C.DIM}│{C.RESET} "
            f"{C.CYAN}{str(task_id):<3}{C.RESET} {C.DIM}│{C.RESET} "
            f"{C.GREEN}{name_short:<28}{C.RESET} {C.DIM}│{C.RESET} "
            f"{C.BRIGHT_YELLOW}{step_short:<23}{C.RESET} {C.DIM}│{C.RESET} "
            f"{C.PURPLE}{prog_full}{C.RESET}"
        )
        if print_output: print(line)
        return line
    else:
        id_display = f"{task_id}"
        if raw_task_id != -1 and raw_task_id != task_id:
            id_display = f"{task_id} {C.RED}(Server: {raw_task_id} - Mismatch!){C.RESET}"
        
        lines = []
        lines.append("")
        print_header(f"[QUEST] Nhiem Vu - {account.username}", width=50, color=C.YELLOW)
        lines.append(f"  {C.GREEN}Tên NV  :{C.RESET} {task_name} {C.DIM}[ID:{id_display}]{C.RESET}")
        lines.append(f"  {C.GREEN}Bước    :{C.RESET} {sub_name} {C.DIM}(Index: {task.index}){C.RESET}")
        lines.append(f"  {C.GREEN}Tiến độ :{C.RESET} {C.PURPLE}{prog_str}{C.RESET}")
        
        output = "\n".join(lines)
        if print_output:
            for l in lines[1:]:
                print(l)
            print_separator(50, color=C.YELLOW)
        return output


# ═══════════════════════════════════════════════════════════════════════════════
# HELP DISPLAY
# ═══════════════════════════════════════════════════════════════════════════════

def display_help():
    """Hiển thị menu trợ giúp với định dạng đẹp."""
    print()
    print_header("[HELP] HUONG DAN SU DUNG", width=70, color=C.BRIGHT_CYAN)
    print()
    
    # Section: Account & Group Management
    print_section_header("Quản Lý Tài Khoản & Nhóm", width=70, color=C.PURPLE)
    cmds = [
        ("list", "Liệt kê tất cả tài khoản và trạng thái"),
        ("login <idx|all|default>", "Đăng nhập tài khoản"),
        ("logout <idx|all>", "Đăng xuất tài khoản"),
        ("target <idx|group>", "Chọn mục tiêu gửi lệnh"),
        ("group list", "Liệt kê các nhóm đã tạo"),
        ("group create <name> <ids>", "Tạo nhóm mới (VD: group create nhom1 0,1,2)"),
        ("group delete <name>", "Xóa một nhóm"),
    ]
    for cmd, desc in cmds:
        print(f"  {C.GREEN}{cmd:<26}{C.RESET} {C.DIM}-{C.RESET} {desc}")
    print()
    
    # Section: Character Commands
    print_section_header("Lệnh Nhân Vật", width=70, color=C.PURPLE)
    cmds = [
        ("show", "Hiển thị thông tin nhân vật"),
        ("show csgoc", "Hiển thị chỉ số GỐC (chưa cộng đồ)"),
        ("show nhiemvu", "Hiển thị thông tin nhiệm vụ"),
        ("pet", "Xem các lệnh đệ tử"),
        ("andau", "Sử dụng đậu thần hồi HP/MP"),
        ("hit", "Tấn công quái vật gần nhất"),
    ]
    for cmd, desc in cmds:
        print(f"  {C.GREEN}{cmd:<26}{C.RESET} {C.DIM}-{C.RESET} {desc}")
    print()
    
    # Section: Navigation
    print_section_header("Di Chuyển", width=70, color=C.PURPLE)
    cmds = [
        ("gomap <id|home>", "Di chuyển đến bản đồ ID hoặc về nhà"),
        ("khu <id>", "Chuyển nhanh đến khu vực"),
        ("teleport <x> <y>", "Dịch chuyển đến tọa độ"),
        ("teleportnpc <id>", "Dịch chuyển đến NPC"),
        ("findnpc", "Liệt kê NPC trong map hiện tại"),
    ]
    for cmd, desc in cmds:
        print(f"  {C.GREEN}{cmd:<26}{C.RESET} {C.DIM}-{C.RESET} {desc}")
    print()
    
    # Section: Automation
    print_section_header("Tự Động", width=70, color=C.PURPLE)
    cmds = [
        ("autoplay <on|off>", "Bật/tắt tự động đánh quái"),
        ("autoplay add <id>", "Thêm ID quái vào danh sách"),
        ("autoplay remove <id>", "Xóa ID quái khỏi danh sách"),
        ("autoplay list", "Xem danh sách quái đang đánh"),
        ("autopet <on|off>", "Bật/tắt tự động đệ tử"),
        ("autobomong <on|off|status>", "Quản lý tự động nhiệm vụ"),
    ]
    for cmd, desc in cmds:
        print(f"  {C.GREEN}{cmd:<26}{C.RESET} {C.DIM}-{C.RESET} {desc}")
    print()
    
    # Section: Other
    print_section_header("Khác", width=70, color=C.PURPLE)
    cmds = [
        ("congcs <hp> <mp> <sd>", "Tự động cộng tiềm năng"),
        ("opennpc <id> [menu...]", "Mở NPC và chọn menu"),
        ("combo <name>", "Chạy combo/macro"),
        ("cls / clear", "Xóa màn hình"),
        ("exit", "Thoát chương trình"),
    ]
    for cmd, desc in cmds:
        print(f"  {C.GREEN}{cmd:<26}{C.RESET} {C.DIM}-{C.RESET} {desc}")
    
    print()
    print_separator(70, color=C.BRIGHT_CYAN)
    print()


# ═══════════════════════════════════════════════════════════════════════════════
# ITEM DISPLAY
# ═══════════════════════════════════════════════════════════════════════════════

def display_found_items(items, username, template_id):
    """Hiển thị kết quả tìm kiếm item."""
    print()
    print_header(f"[SEARCH] Tim Item ID {template_id} - {username}", width=60, color=C.CYAN)
    
    if not items:
        print(f"  {C.RED}Không tìm thấy item nào với ID {template_id} trong hành trang.{C.RESET}")
        print_separator(60, color=C.CYAN)
        return
    
    # Header
    print(f"  {C.BOLD}{C.BRIGHT_CYAN}{'#':<3} {'Tên':<28} {'SL':<6} {'Idx':<4} {'Option'}{C.RESET}")
    print(f"  {C.DIM}{B.H * 56}{C.RESET}")
    
    total_quantity = 0
    for i, item in enumerate(items):
        info_str = item.info if item.info else f"Item {item.item_id}"
        if len(info_str) > 26:
            info_str = info_str[:24] + ".."
        
        opt_str = ""
        if item.item_option:
            opt_str = ", ".join([f"[{o.option_template_id}:{o.param}]" for o in item.item_option[:2]])
        
        print(f"  {C.GREY}{i+1:<3}{C.RESET} {C.GREEN}{info_str:<28}{C.RESET} {C.YELLOW}{item.quantity:<6}{C.RESET} {C.PURPLE}{item.index_ui:<4}{C.RESET} {C.DIM}{opt_str}{C.RESET}")
        total_quantity += item.quantity
    
    print(f"  {C.DIM}{B.H * 56}{C.RESET}")
    print(f"  {C.BRIGHT_WHITE}Tổng số lượng:{C.RESET} {C.BRIGHT_YELLOW}{total_quantity}{C.RESET}")
    print_separator(60, color=C.CYAN)


# ═══════════════════════════════════════════════════════════════════════════════
# COMPACT TABLE HEADERS
# ═══════════════════════════════════════════════════════════════════════════════

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


# ═══════════════════════════════════════════════════════════════════════════════
# ZONE DISPLAY
# ═══════════════════════════════════════════════════════════════════════════════

def display_zone_list(zones_data: list, map_name: str, account_name: str, current_zone_id: int = -1):
    """Hiển thị danh sách khu vực và số lượng người chơi."""
    print()
    print_header(f"[ZONE] Danh Sach Khu Vuc - {map_name} ({account_name})", width=60, color=C.CYAN)
    
    # Header
    print(f"  {C.BOLD}{C.BRIGHT_CYAN}{'Zone':<6} {'Người Chơi':<12} {'Tối Đa':<8} {'Thông Tin Thêm'}{C.RESET}")
    print(f"  {C.DIM}{B.H * 56}{C.RESET}")
    
    # Sort zones by Zone ID (ascending) for cleaner list
    sorted_zones = sorted(zones_data, key=lambda x: x['zone_id'])
    
    for z in sorted_zones:
        z_id = z['zone_id']
        curr = z['num_players']
        max_p = z['max_players']
        
        # Color coding for occupancy
        if curr >= max_p:
            p_color = C.RED      # Full
        elif curr >= max_p * 0.8:
            p_color = C.YELLOW   # Crowded
        else:
            p_color = C.GREEN    # Good
            
        extra_info = ""
        if z.get('rank_flag'):
            r1 = z.get('rank1', 0)
            r2 = z.get('rank2', 0)
            extra_info = f"{C.DIM}({r1} vs {r2}){C.RESET}"
            
        # Highlight current zone
        if z_id == current_zone_id:
            z_display = f"{z_id} (*)"
        else:
            z_display = f"{z_id}"
            
        print(f"  {C.CYAN}{z_display:<6}{C.RESET} {p_color}{curr:<12}{C.RESET} {C.GREY}{max_p:<8}{C.RESET} {extra_info}")

    print(f"  {C.DIM}{B.H * 56}{C.RESET}")
    print(f"  {C.BRIGHT_WHITE}Tổng số khu:{C.RESET} {C.BRIGHT_YELLOW}{len(zones_data)}{C.RESET}")
    print_separator(60, color=C.CYAN)
