# toolsDev/ui.py
from logs.logger_config import logger, TerminalColors

def get_pet_status_vietnamese(status: int) -> str:
    """
    Trả về trạng thái của đệ tử bằng tiếng Việt.
    """
    C = TerminalColors
    status_map = {
        0: f"{C.GREEN}Đi theo{C.RESET}",
        1: f"{C.PURPLE}Bảo vệ{C.RESET}",
        2: f"{C.RED}Tấn công{C.RESET}",
        3: f"{C.YELLOW}Về nhà{C.RESET}",
        4: f"{C.CYAN}Hợp thể{C.RESET}",
        5: f"{C.BOLD_RED}Hợp thể vĩnh viễn{C.RESET}"
    }
    return status_map.get(status, f"Không xác định ({status})")

def get_pet_status_short(status: int) -> str:
    """Trả về trạng thái ngắn gọn."""
    C = TerminalColors
    status_map = {
        0: f"{C.GREEN}Theo{C.RESET}",
        1: f"{C.PURPLE}B.Vệ{C.RESET}",
        2: f"{C.RED}T.Công{C.RESET}",
        3: f"{C.YELLOW}Về{C.RESET}",
        4: f"{C.CYAN}H.Thể{C.RESET}",
        5: f"{C.BOLD_RED}H.Thể VV{C.RESET}"
    }
    return status_map.get(status, f"Unk({status})")

def display_pet_info(pet, username="Unknown", compact=False):
    """
    Hiển thị thông tin chi tiết của đệ tử.
    :param compact: Nếu True, hiển thị dạng 1 dòng (dành cho multi-account).
    """
    C = TerminalColors
    if not pet or not pet.have_pet:
        if compact:
             print(f"[{C.YELLOW}{username:<15}{C.RESET}] {C.GREY}Không có đệ tử{C.RESET}")
        else:
             logger.info(f"[{username}] Không có thông tin đệ tử hoặc chưa nhận được dữ liệu từ server.")
        return

    if compact:
        # Chế độ hiển thị 1 dòng ngắn gọn
        # Căn chỉnh cột:
        # User: 18 chars (bao gồm [])
        # Name: 12 chars
        # Status: ~20 chars (do chứa mã màu ẩn ~9 chars, hiển thị thực tế khoảng 11 chars)
        # HP: 15 chars (HP: + 12 số)
        # MP: 15 chars (MP: + 12 số)
        # SM: 19 chars (SM: + 16 số)
        
        user_str = f"[{username}]"
        status = get_pet_status_short(pet.pet_status)
        
        # Format số liệu raw
        hp_raw = f"{pet.c_hp:,}"
        mp_raw = f"{pet.c_mp:,}"
        pow_raw = f"{pet.c_power:,}"
        
        print(f"{C.YELLOW}{user_str:<18}{C.RESET} "
              f"{C.GREEN}{pet.name:<12}{C.RESET} | "
              f"{status:<20} | " 
              f"{C.RED}HP:{hp_raw:<12}{C.RESET} | "
              f"{C.BLUE}MP:{mp_raw:<12}{C.RESET} | "
              f"{C.YELLOW}SM:{pow_raw:<16}{C.RESET}")
    else:
        # Chế độ hiển thị chi tiết (cũ)
        print(f"{C.CYAN}--- Thông Tin Đệ Tử [{C.YELLOW}{username}{C.CYAN}] ---{C.RESET}")
        
        info_lines = [
            f"{C.GREEN}Tên:{C.RESET} {pet.name}",
            f"{C.GREEN}Trạng thái:{C.RESET} {get_pet_status_vietnamese(pet.pet_status)} (Status ID: {pet.pet_status})",
            f"{C.GREEN}HP:{C.RESET} {C.RED}{pet.c_hp:,} / {pet.c_hp_full:,}{C.RESET}",
            f"{C.GREEN}MP:{C.RESET} {C.BLUE}{pet.c_mp:,} / {pet.c_mp_full:,}{C.RESET}",
            f"{C.GREEN}Sát thương:{C.RESET} {pet.c_dam_full:,}",
            f"{C.GREEN}Sức mạnh:{C.RESET} {C.YELLOW}{pet.c_power:,}{C.RESET}",
            f"{C.GREEN}Tiềm năng:{C.RESET} {C.CYAN}{pet.c_tiem_nang:,}{C.RESET}",
            f"{C.GREEN}Phòng thủ:{C.RESET} {pet.c_def_full:,}",
            f"{C.GREEN}Chí mạng:{C.RESET} {pet.c_critical_full}%",
            f"{C.GREEN}Thể lực:{C.RESET} {pet.c_stamina:,} / {pet.c_max_stamina:,}",
        ]
        for line in info_lines:
            print(line)
        print(f"{C.CYAN}--- Kết thúc ---{C.RESET}")

def display_pet_help():
    """Hiển thị các lệnh có sẵn cho đệ tử."""
    C = TerminalColors
    print(f"{C.CYAN}--- Trợ giúp Đệ Tử ---{C.RESET}")
    print("Các lệnh có sẵn cho đệ tử:")
    print(f"  {C.GREEN}pet info{C.RESET}            - Hiển thị thông tin chi tiết của đệ tử.")
    print(f"  {C.GREEN}pet follow{C.RESET}          - Ra lệnh đệ tử đi theo.")
    print(f"  {C.GREEN}pet protect{C.RESET}         - Ra lệnh đệ tử bảo vệ.")
    print(f"  {C.GREEN}pet attack{C.RESET}          - Ra lệnh đệ tử tấn công.")
    print(f"  {C.GREEN}pet home{C.RESET}            - Ra lệnh đệ tử về nhà.")
    print(f"{C.CYAN}--- Kết thúc ---{C.RESET}")

def display_help():
    """Hiển thị các lệnh có sẵn."""
    C = TerminalColors
    print(f"{C.CYAN}--- Trợ giúp ---{C.RESET}")
    print(f"{C.PURPLE}--- Quản lý mục tiêu & Nhóm ---{C.RESET}")
    print(f"  {C.GREEN}list{C.RESET}              - Liệt kê tất cả các tài khoản và trạng thái.")
    print(f"  {C.GREEN}login{C.RESET} {C.YELLOW}<index|list|all|default>{C.RESET} - Đăng nhập tài khoản (VD: 'login 0', 'login default').")
    print(f"  {C.GREEN}logout{C.RESET} {C.YELLOW}<index|list|all>{C.RESET}- Đăng xuất tài khoản (VD: 'logout 0', 'logout 1,3', 'logout all').")
    print(f"  {C.GREEN}target{C.RESET} {C.YELLOW}<id|name>{C.RESET}  - Chọn mục tiêu để gửi lệnh (VD: 'target 0', 'target all', 'target nhom1').")
    print(f"  {C.GREEN}group list{C.RESET}        - Liệt kê các nhóm đã tạo.")
    print(f"  {C.GREEN}group create{C.RESET} {C.YELLOW}<name> <ids>{C.RESET} - Tạo nhóm mới (VD: 'group nhom1 0,1,2').")
    print(f"  {C.GREEN}group delete{C.RESET} {C.YELLOW}<name>{C.RESET}     - Xóa một nhóm.")
    print(f"  {C.GREEN}group add{C.RESET} {C.YELLOW}<name> <ids>{C.RESET}    - Thêm tài khoản vào nhóm.")
    print(f"  {C.GREEN}group remove{C.RESET} {C.YELLOW}<name> <ids>{C.RESET} - Xóa tài khoản khỏi nhóm.")
    print(f"\n{C.PURPLE}--- Lệnh cho Mục tiêu đã chọn ---{C.RESET}")
    print(f"  {C.GREEN}show{C.RESET}              - Hiển thị thông tin nhân vật, đệ tử và vị trí của mục tiêu.")
    print(f"  {C.GREEN}pet{C.RESET}               - Hiển thị các lệnh liên quan đến đệ tử.")
    print(f"  {C.GREEN}khu{C.RESET} {C.YELLOW}[id khu]{C.RESET}      - Chuyển nhanh đến khu vực có ID [id khu].")
    print(f"  {C.GREEN}autoplay{C.RESET} {C.YELLOW}[on|off]{C.RESET} - Bật hoặc tắt tự động tấn công.")
    print(f"  {C.GREEN}autopet{C.RESET} {C.YELLOW}[on|off]{C.RESET}  - Bật hoặc tắt tự động nâng cấp đệ tử.")
    print(f"  {C.GREEN}findnpc{C.RESET}            - Liệt kê các NPC có trong bản đồ hiện tại.")
    print(f"  {C.GREEN}teleport{C.RESET} {C.YELLOW}<x> <y>{C.RESET}   - Dịch chuyển đến tọa độ (x, y).")
    print(f"  {C.GREEN}teleportnpc{C.RESET} {C.YELLOW}<id>{C.RESET} - Dịch chuyển đến NPC có ID là [id].")
    print(f"  {C.GREEN}andau{C.RESET}               - Sử dụng đậu thần trong hành trang (hồi HP/MP/Thể lực).")
    print(f"  {C.GREEN}hit{C.RESET}                 - Tấn công quái vật gần nhất một lần.")
    print(f"\n{C.PURPLE}--- Lệnh chung ---{C.RESET}")
    print(f"  {C.GREEN}logger{C.RESET} {C.YELLOW}[on|off]{C.RESET}   - Bật hoặc tắt logger chi tiết.")
    print(f"  {C.GREEN}clear{C.RESET}             - Xóa nội dung hiện tại trong console.")
    print(f"  {C.GREEN}show{C.RESET}              - Hiển thị thông tin nhân vật.")
    print(f"  {C.GREEN}help{C.RESET}              - Hiển thị bảng trợ giúp này.")
    print(f"  {C.GREEN}exit{C.RESET}              - Thoát khỏi công cụ.")
    print(f"{C.CYAN}--- Kết thúc ---{C.RESET}")

def short_number(num: int) -> str:
    """Định dạng số ngắn gọn (VD: 1.2tr, 5.5tỷ)."""
    if num >= 1_000_000_000:
        return f"{num/1_000_000_000:.1f}tỷ".replace('.0tỷ', 'tỷ')
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}tr".replace('.0tr', 'tr')
    if num >= 1_000:
        return f"{num/1_000:.1f}k".replace('.0k', 'k')
    return str(num)

def display_character_status(account, compact=False):
    """
    Hiển thị thông tin trạng thái của một tài khoản.
    :param compact: Nếu True, hiển thị dạng 1 dòng (dành cho multi-account).
    """
    C = TerminalColors
    char = account.char
    pet = account.pet
    map_info = account.controller.map_info

    if compact:
        # Format 1 dòng: [User] | Map | ID | Zone | X,Y | HP | MP | SM | Status
        user_str = f"[{account.username}]"
        
        hp_str = short_number(char.c_hp)
        mp_str = short_number(char.c_mp)
        pow_str = short_number(char.c_power)
        
        map_name = map_info.get('name', 'N/A')
        # Cắt tên map nếu quá dài
        if len(map_name) > 20:
            map_name = map_name[:18] + ".."
            
        map_id = str(map_info.get('id', 'N/A'))
        zone_id = str(map_info.get('zone', 'N/A'))
        coords = f"{char.cx},{char.cy}"
        
        # Thêm trạng thái chức năng
        ap_status = f"{C.GREEN}A.Play{C.RESET}" if account.controller.auto_play.interval else f"{C.GREY}A.Play{C.RESET}"
        apet_status = f"{C.GREEN}A.Pet{C.RESET}" if account.controller.auto_pet.is_running else f"{C.GREY}A.Pet{C.RESET}"
        funcs_str = f"{ap_status} {apet_status}"
        
        print(f"{C.YELLOW}{user_str:<13}{C.RESET} | "
              f"{C.CYAN}{map_name:<20}{C.RESET} | "
              f"{C.PURPLE}{map_id:<3}{C.RESET} | "
              f"{C.BLUE}{zone_id:<3}{C.RESET} | "
              f"{C.GREY}{coords:<9}{C.RESET} | "
              f"{C.RED}{hp_str:<7}{C.RESET} | "
              f"{C.BLUE}{mp_str:<7}{C.RESET} | "
              f"{C.YELLOW}{pow_str:<7}{C.RESET} | "
              f"{funcs_str:<31}")
    else:
        # Chế độ chi tiết cũ
        print(f"{C.BOLD_RED}--- Trạng thái: {C.YELLOW}{account.username}{C.BOLD_RED} ---{C.RESET}")
        
        # Hiển thị thông tin Proxy
        proxy_info = account.proxy if account.proxy else "Local IP"
        print(f"  {C.CYAN}Kết nối:{C.RESET} {C.PURPLE}{proxy_info}{C.RESET}")

        # Thông tin nhân vật
        print(f"  {C.CYAN}Nhân vật:{C.RESET}")
        print(f"    - {C.GREEN}Tên:{C.RESET} {char.name} ({C.YELLOW}ID: {char.char_id}{C.RESET})")
        print(f"    - {C.GREEN}Vị trí:{C.RESET} {map_info.get('name', 'N/A')} [{C.YELLOW}{map_info.get('id', 'N/A')}{C.RESET}] / Khu {C.YELLOW}{map_info.get('zone', 'N/A')}{C.RESET} / Tọa độ ({C.YELLOW}{char.cx}{C.RESET}, {C.YELLOW}{char.cy}{C.RESET})")
        print(f"    - {C.GREEN}HP:{C.RESET} {C.RED}{char.c_hp:,} / {char.c_hp_full:,}{C.RESET}")
        print(f"    - {C.GREEN}MP:{C.RESET} {C.BLUE}{char.c_mp:,} / {char.c_mp_full:,}{C.RESET}")
        print(f"    - {C.GREEN}Sức mạnh:{C.RESET} {C.YELLOW}{char.c_power:,}{C.RESET}")

        # Hiển thị trạng thái chức năng
        print(f"  {C.CYAN}Chức năng:{C.RESET}")
        autoplay_status = f"{C.GREEN}Bật{C.RESET}" if account.controller.auto_play.interval else f"{C.RED}Tắt{C.RESET}"
        autopet_status = f"{C.GREEN}Bật{C.RESET}" if account.controller.auto_pet.is_running else f"{C.RED}Tắt{C.RESET}"
        print(f"    - Tự động đánh: {autoplay_status}")
        print(f"    - Tự động đệ tử: {autopet_status}")

        # Thông tin đệ tử
        print(f"  {C.CYAN}Đệ tử:{C.RESET}")
        if pet and pet.have_pet:
            print(f"    - {C.GREEN}Tên:{C.RESET} {pet.name}")
            print(f"    - {C.GREEN}HP:{C.RESET} {C.RED}{pet.c_hp:,} / {pet.c_hp_full:,}{C.RESET}")
            print(f"    - {C.GREEN}MP:{C.RESET} {C.BLUE}{pet.c_mp:,} / {pet.c_mp_full:,}{C.RESET}")
            print(f"    - {C.GREEN}Sức mạnh:{C.RESET} {C.YELLOW}{pet.c_power:,}{C.RESET}")
        else:
            print(f"    - {C.GREY}Không có đệ tử.{C.RESET}")
        print(f"{C.BOLD_RED}---" + "-" * (len(account.username) + 12) + f"---{C.RESET}\n")


