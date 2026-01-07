"""Module chứa các hàm hiển thị thông tin nhân vật."""

from logs.logger_config import TerminalColors as C, print_header, print_section_header, print_separator
from ui.formatters import short_number


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
