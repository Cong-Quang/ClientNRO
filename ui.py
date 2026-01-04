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
    """Trả về trạng thái ngắn gọn (có màu)."""
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


def get_pet_status_short_raw(status: int) -> str:
    """Trả về trạng thái ngắn gọn không màu (dùng để căn chỉnh)."""
    status_map = {
        0: "Theo",
        1: "B.Vệ",
        2: "T.Công",
        3: "Về",
        4: "H.Thể",
        5: "H.Thể VV"
    }
    return status_map.get(status, f"Unk({status})")


def display_pet_info(pet, username="Unknown", compact=False, idx: int = None):
    """
    Hiển thị thông tin chi tiết của đệ tử.
    :param compact: Nếu True, hiển thị dạng 1 dòng (dành cho multi-account).
    :param idx: Nếu được cung cấp, in số thứ tự (ví dụ: [0]) bên cạnh tên tài khoản.
    """
    C = TerminalColors
    if not pet or not pet.have_pet:
        if compact:
             # Hiển thị gọn nếu không có đệ tử
             user_str = f"[{username}] {f'[{idx}]' if idx is not None else ''}"
             print(f"{C.YELLOW}{user_str:<15}{C.RESET} {C.GREY}Không có đệ tử{C.RESET}")
        else:
             logger.info(f"[{username}] Không có thông tin đệ tử hoặc chưa nhận được dữ liệu từ server.")
        return

    if compact:
        # Chế độ hiển thị 1 dòng ngắn gọn (gọn hơn, căn chỉnh chặt)
        idx_str = f"[{idx}]" if idx is not None else ""

        # Raw/short values
        hp_short = short_number(pet.c_hp)
        mp_short = short_number(pet.c_mp)
        sm_short = short_number(pet.c_power)
        dam_short = short_number(getattr(pet, 'c_dam_full', getattr(pet, 'damage_full', 0)))

        # Status raw + color mapping for consistent padding
        status_raw = get_pet_status_short_raw(pet.pet_status)
        status_colors = {
            0: C.GREEN, 1: C.PURPLE, 2: C.RED, 3: C.YELLOW, 4: C.CYAN, 5: C.BOLD_RED
        }
        status_plain = f"{status_raw:<6}"
        status_col = f"{status_colors.get(pet.pet_status, C.GREY)}{status_plain}{C.RESET}"

        # Build padded plain columns first, then colorize to avoid ANSI misalignment
        user_plain = f"[{username}]"
        # Widen username area to align ID under header
        user_padded = f"{user_plain:<15}"
        user_col = f"{C.YELLOW}{user_padded}{C.RESET}"

        id_plain = f"{idx_str:<4}"
        id_col = f"{C.PURPLE}{id_plain}{C.RESET}"

        name_plain = f"{pet.name:<12}"
        name_col = f"{C.GREEN}{name_plain}{C.RESET}"

        hp_plain = f"{hp_short:>7}"
        hp_col = f"{C.RED}{hp_plain}{C.RESET}"

        mp_plain = f"{mp_short:>7}"
        mp_col = f"{C.BLUE}{mp_plain}{C.RESET}"

        sm_plain = f"{sm_short:>7}"
        sm_col = f"{C.YELLOW}{sm_plain}{C.RESET}"

        dam_plain = f"{dam_short:>7}"
        dam_col = f"{C.PURPLE}{dam_plain}{C.RESET}"

        line = f"{user_col} {id_col} {name_col} | {status_col} | {hp_col} | {mp_col} | {sm_col} | {dam_col}"

        # Alternate row color: even -> GREEN, odd -> GREY
        if idx is not None:
            if (idx % 2) == 0:
                print(f"{C.GREEN}{line}{C.RESET}")
            else:
                print(f"{C.GREY}{line}{C.RESET}")
        else:
            print(line)
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
    print(f"  {C.GREEN}show csgoc{C.RESET}        - Hiển thị chỉ số GỐC (chưa cộng đồ) của nhân vật.")
    print(f"  {C.GREEN}pet{C.RESET}               - Hiển thị các lệnh liên quan đến đệ tử.")
    print(f"  {C.GREEN}khu{C.RESET} {C.YELLOW}[id khu]{C.RESET}      - Chuyển nhanh đến khu vực có ID [id khu].")
    print(f"  {C.GREEN}gomap{C.RESET} {C.YELLOW}<id|home>{C.RESET}     - Di chuyển đến bản đồ ID hoặc về nhà.")
    print(f"  {C.GREEN}opennpc{C.RESET} {C.YELLOW}<id> [idx..]{C.RESET}- Mở NPC theo ID và chọn các menu nếu có.")
    print(f"  {C.GREEN}autoplay{C.RESET} {C.YELLOW}[on|off|add|remove|list]{C.RESET} - Quản lý tự động đánh quái.")
    print(f"      {C.YELLOW}- autoplay add <id1> [id2]...{C.RESET} : Thêm ID quái vào danh sách đánh (Mặc định đánh tất cả).")
    print(f"      {C.YELLOW}- autoplay remove <id1> [id2]...{C.RESET} : Xóa ID quái khỏi danh sách.")
    print(f"      {C.YELLOW}- autoplay list{C.RESET} : Xem danh sách quái đang chọn.")
    print(f"  {C.GREEN}autopet{C.RESET} {C.YELLOW}[on|off]{C.RESET}  - Bật hoặc tắt tự động nâng cấp đệ tử.")
    print(f"  {C.GREEN}findnpc{C.RESET}            - Liệt kê các NPC có trong bản đồ hiện tại.")
    print(f"  {C.GREEN}teleport{C.RESET} {C.YELLOW}<x> <y>{C.RESET}   - Dịch chuyển đến tọa độ (x, y).")
    print(f"  {C.GREEN}teleportnpc{C.RESET} {C.YELLOW}<id>{C.RESET} - Dịch chuyển đến NPC có ID là [id].")
    print(f"  {C.GREEN}congcs{C.RESET} {C.YELLOW}<hp> <mp> <sd>{C.RESET} - Tự động cộng tiềm năng đến chỉ số gốc mong muốn.")
    print(f"  {C.GREEN}andau{C.RESET}               - Sử dụng đậu thần trong hành trang (hồi HP/MP/Thể lực).")
    print(f"  {C.GREEN}hit{C.RESET}                 - Tấn công quái vật gần nhất một lần.")
    print(f"  {C.GREEN}show nhiemvu{C.RESET}        - Hiển thị thông tin nhiệm vụ chi tiết/danh sách.")
    print(f"\n{C.PURPLE}--- Lệnh chung ---{C.RESET}")

def display_task_info(account, compact=False, idx: int = None):
    """
    Hiển thị thông tin nhiệm vụ.
    - Compact: Dạng bảng.
    - Detailed: Dạng khối chuẩn theo yêu cầu.
    """
    C = TerminalColors
    task = account.char.task
    
    # Chuẩn bị dữ liệu
    task_id = task.task_id
    # Check for desync with raw ctask_id from ME_LOAD_ALL
    raw_task_id = getattr(account.char, 'ctask_id', -1)    # Xử lý khi chưa có dữ liệu
    if not task or not task.name:
        if compact:
            idx_str = f"[{idx}]" if idx is not None else ""
            user_str = f"[{account.username}]"
            print(f"{C.PURPLE}{idx_str:<3}{C.RESET} | {C.YELLOW}{user_str:<13}{C.RESET} | {C.GREY}No Data{C.RESET}")
        else:
            print(f"{C.YELLOW}[{account.username}] Chưa có thông tin nhiệm vụ.{C.RESET}")
        return

    # Chuẩn bị dữ liệu
    task_id = task.task_id
    # Check for desync with raw ctask_id from ME_LOAD_ALL
    raw_task_id = getattr(account.char, 'ctask_id', -1)
    
    task_name = task.name.strip()
    # Lấy tên bước hiện tại
    sub_name = ""
    if task.sub_names and 0 <= task.index < len(task.sub_names):
        sub_name = task.sub_names[task.index].strip()
    else:
        sub_name = "..."

    # Lấy tiến độ
    current = task.count
    required = 0
    if task.counts and 0 <= task.index < len(task.counts):
        required = task.counts[task.index]
    
    prog_str = f"{current}/{required}"
    
    if compact:
        # --- COMPACT MODE ---
        idx_str = f"[{idx}]" if idx is not None else ""
        user_str = f"[{account.username}]"
        name_short = task_name if len(task_name) < 30 else task_name[:28] + ".."
        step_short = sub_name if len(sub_name) < 25 else sub_name[:23] + ".."
        
        # Highlight progress if desync
        if raw_task_id != -1 and raw_task_id != task_id:
             prog_full = f"{C.RED}[Desync: {raw_task_id}]{C.RESET} {prog_str} [{task.index}]"
        else:
             prog_full = f"{prog_str} [{task.index}]"

        line = f"{C.PURPLE}{idx_str:<3}{C.RESET} | {C.YELLOW}{user_str:<13}{C.RESET} | {C.CYAN}{str(task_id):<3}{C.RESET} | {C.GREEN}{name_short:<30}{C.RESET} | {C.YELLOW}{step_short:<25}{C.RESET} | {C.PURPLE}{prog_full}{C.RESET}"
        print(line)

    else:
        # --- DETAILED MODE (Formatted exactly as requested) ---
        print(f"{C.BOLD_RED}--- Nhiệm Vụ: {C.YELLOW}{account.username}{C.BOLD_RED} ---{C.RESET}")
        
        id_display = f"{task_id}"
        if raw_task_id != -1 and raw_task_id != task_id:
             id_display = f"{task_id} {C.RED}(Server ID: {raw_task_id} - Mismatch!){C.RESET}"
             
        print(f"  {C.GREEN}Tên NV  :{C.RESET} {task_name}{C.RESET} {C.GREY} [id:{id_display}] ")
        print(f"  {C.GREEN}Bước    :{C.RESET} {sub_name} {C.GREY}(Index: {task.index}){C.RESET}")
        print(f"  {C.GREEN}Tiến độ :{C.RESET} {C.PURPLE}{prog_str}{C.RESET}")
        print(f"{C.BOLD_RED}--------------------------{C.RESET}\n")

def short_number(num: int) -> str:
    """Định dạng số ngắn gọn (VD: 1.2tr, 5.5tỷ)."""
    if num >= 1_000_000_000:
        return f"{num/1_000_000_000:.1f}tỷ".replace('.0tỷ', 'tỷ')
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}tr".replace('.0tr', 'tr')
    if num >= 1_000:
        return f"{num/1_000:.1f}k".replace('.0k', 'k')
    return str(num)

def display_character_base_stats(account, compact=False, idx: int = None):
    """
    Hiển thị thông tin chỉ số GỐC của nhân vật.
    :param compact: Nếu True, hiển thị dạng 1 dòng (dành cho multi-account).
    :param idx: Nếu được cung cấp, in số thứ tự (ví dụ: [0]) bên cạnh tên tài khoản.
    """
    C = TerminalColors
    char = account.char
    
    if compact:
        # Chế độ hiển thị 1 dòng ngắn gọn
        user_plain = f"[{account.username}] {f'[{idx}]' if idx is not None else ''}"
        user_padded = f"{user_plain:<19}"
        user_col = f"{C.YELLOW}{user_padded}{C.RESET}"

        hp_str = short_number(char.c_hp_goc)
        mp_str = short_number(char.c_mp_goc)
        dam_str = short_number(char.c_dam_goc)
        def_str = short_number(getattr(char, 'c_def_goc', 0))
        crit_str = f"{getattr(char, 'c_critical_goc', 0)}%"
        tn_str = short_number(getattr(char, 'c_tiem_nang', 0))

        hp_col = f"{C.RED}{hp_str:>8}{C.RESET}"
        mp_col = f"{C.BLUE}{mp_str:>7}{C.RESET}"
        dam_col = f"{C.PURPLE}{dam_str:>7}{C.RESET}"
        def_col = f"{C.GREY}{def_str:>7}{C.RESET}"
        crit_col = f"{C.CYAN}{crit_str:>5}{C.RESET}"
        tn_col = f"{C.YELLOW}{tn_str:>7}{C.RESET}"

        line = f"{user_col} | {hp_col} | {mp_col} | {dam_col} | {def_col} | {crit_col} | {tn_col}"
        
        # Xen kẽ màu cho dễ đọc
        if idx is not None:
            if (idx % 2) == 0:
                print(f"{C.GREEN}{line}{C.RESET}")
            else:
                print(f"{C.GREY}{line}{C.RESET}")
        else:
            print(line)
    else:
        # Chế độ chi tiết
        print(f"{C.BOLD_RED}--- Chỉ Số Gốc: {C.YELLOW}{account.username}{C.BOLD_RED} ---{C.RESET}")
        print(f"  {C.GREEN}HP Gốc:{C.RESET} {C.RED}{char.c_hp_goc:,}{C.RESET}")
        print(f"  {C.GREEN}MP Gốc:{C.RESET} {C.BLUE}{char.c_mp_goc:,}{C.RESET}")
        print(f"  {C.GREEN}Sức đánh Gốc:{C.RESET} {C.PURPLE}{char.c_dam_goc:,}{C.RESET}")
        print(f"  {C.GREEN}Giáp Gốc:{C.RESET} {getattr(char, 'c_def_goc', 0):,}")
        print(f"  {C.GREEN}Chí mạng Gốc:{C.RESET} {getattr(char, 'c_critical_goc', 0)}%")
        print(f"  {C.GREEN}Tiềm năng:{C.RESET} {C.CYAN}{getattr(char, 'c_tiem_nang', 0):,}{C.RESET}")
        print(f"{C.BOLD_RED}--------------------------{C.RESET}\n")

def display_character_status(account, compact=False, idx: int = None):
    """
    Hiển thị thông tin trạng thái của một tài khoản.
    :param compact: Nếu True, hiển thị dạng 1 dòng (dành cho multi-account).
    :param idx: Nếu được cung cấp, in số thứ tự (ví dụ: [0]) bên cạnh tên tài khoản.
    """
    C = TerminalColors
    char = account.char
    map_info = account.controller.map_info

    # Nếu nhân vật chưa được load, hiển thị trạng thái cơ bản và thoát
    if not char.name:
        if compact:
            user_plain = f"[{account.username}] {f'[{idx}]' if idx is not None else ''}"
            user_padded = f"{user_plain:<19}"
            user_col = f"{C.YELLOW}{user_padded}{C.RESET}"
            
            status_text = account.status
            if account.status == "Logged In":
                status_color = C.GREEN
                status_text = "Loading..." # Trạng thái khi đã login nhưng chưa có data char
            elif account.status == "Reconnecting":
                status_color = C.YELLOW
            else:
                status_color = C.RED

            status_padded = f"{status_text:<18}" # Căn lề cho trạng thái loading
            status_col = f"{status_color}{status_padded}{C.RESET}"

            line = f"{user_col} | {status_col}"
            print(line)
        else:
            display_character_base_info(account)
        return

    if compact:
        # --- 1. Build PLAIN strings for all columns ---
        hp_str = short_number(char.c_hp)
        mp_str = short_number(char.c_mp)
        pow_str = short_number(char.c_power)
        dam_str = short_number(getattr(char, 'c_dam_full', 0))
        
        map_name = map_info.get('name', 'N/A')
        if len(map_name) > 18:
            map_name = map_name[:16] + ".."
            
        map_id_str = str(map_info.get('id', 'N/A'))
        zone_id_str = str(map_info.get('zone', 'N/A'))
        coords_str = f"{char.cx},{char.cy}"
        
        ap_plain = "A.Play" if account.controller.auto_play.interval else ""
        apet_plain = "A.Pet" if account.controller.auto_pet.is_running else ""
        funcs_plain = f"{ap_plain} {apet_plain}".strip()

        # --- 2. Colorize content strings (before padding) ---
        user_colored = f"[{C.YELLOW}{account.username}{C.RESET}] {f'[{C.PURPLE}{idx}{C.RESET}]' if idx is not None else ''}"
        map_colored = f"{C.CYAN}{map_name}{C.RESET}"
        id_colored = f"{C.PURPLE}{map_id_str}{C.RESET}"
        zone_colored = f"{C.BLUE}{zone_id_str}{C.RESET}"
        coords_colored = f"{C.GREY}{coords_str}{C.RESET}"
        hp_colored = f"{C.RED}{hp_str}{C.RESET}"
        mp_colored = f"{C.BLUE}{mp_str}{C.RESET}"
        pow_colored = f"{C.YELLOW}{pow_str}{C.RESET}"
        dam_colored = f"{C.PURPLE}{dam_str}{C.RESET}"

        ap_status_colored = f"{C.GREEN}A.Play{C.RESET}" if account.controller.auto_play.interval else ""
        apet_status_colored = f"{C.GREEN}A.Pet{C.RESET}" if account.controller.auto_pet.is_running else ""
        funcs_colored = f"{ap_status_colored} {apet_status_colored}".strip()
        
        # --- 3. Pad the colored strings manually ---
        # This is the tricky part. We calculate padding based on plain string length.
        user_padding = 19 - len(f"[{account.username}] {f'[{idx}]' if idx is not None else ''}")
        map_padding = 18 - len(map_name)
        id_padding = 3 - len(map_id_str)
        zone_padding = 3 - len(zone_id_str)
        coords_padding = 10 - len(coords_str) # Increased width
        hp_padding = 8 - len(hp_str)
        mp_padding = 7 - len(mp_str)
        pow_padding = 7 - len(pow_str)
        dam_padding = 7 - len(dam_str)
        funcs_padding = 14 - len(funcs_plain) # Re-added width

        user_final = user_colored + " " * user_padding
        map_final = map_colored + " " * map_padding
        id_final = id_colored + " " * id_padding
        zone_final = zone_colored + " " * zone_padding
        coords_final = coords_colored + " " * coords_padding
        hp_final = " " * hp_padding + hp_colored
        mp_final = " " * mp_padding + mp_colored
        pow_final = " " * pow_padding + pow_colored
        dam_final = " " * dam_padding + dam_colored
        funcs_final = funcs_colored + " " * funcs_padding # Re-added final column

        line = f"{user_final} | {map_final} | {id_final} | {zone_final} | {coords_final} | {hp_final} | {mp_final} | {pow_final} | {dam_final} | {funcs_final}"
        
        print(line)

    else:
        # Chế độ chi tiết (cải tiến)
        display_character_base_info(account)
        
        print(f"  {C.CYAN}--- Vị trí & Chỉ số ---{C.RESET}")
        print(f"    - {C.GREEN}Vị trí:{C.RESET} {map_info.get('name', 'N/A')} [{C.YELLOW}{map_info.get('id', 'N/A')}{C.RESET}] / Khu {C.CYAN}{map_info.get('zone', 'N/A')}{C.RESET} / Tọa độ ({C.GREY}{char.cx}{C.RESET}, {C.GREY}{char.cy}{C.RESET})")
        print(f"    - {C.GREEN}HP:{C.RESET} {C.RED}{char.c_hp:,}{C.RESET} / {char.c_hp_full:,}")
        print(f"    - {C.GREEN}MP:{C.RESET} {C.BLUE}{char.c_mp:,}{C.RESET} / {char.c_mp_full:,}")
        print(f"    - {C.GREEN}Sức mạnh:{C.RESET} {C.YELLOW}{char.c_power:,}{C.RESET}")
        print(f"    - {C.GREEN}Sức đánh:{C.RESET} {C.PURPLE}{getattr(char, 'c_dam_full', 0):,}{C.RESET}")
        print(f"    - {C.GREEN}Tiềm năng:{C.RESET} {C.CYAN}{getattr(char, 'c_tiem_nang', 0):,}{C.RESET}")

        print(f"  {C.CYAN}--- Tài sản ---{C.RESET}")
        print(f"    - {C.GREEN}Vàng:{C.RESET} {C.YELLOW}{getattr(char, 'xu', 0):,}{C.RESET}")
        print(f"    - {C.GREEN}Ngọc:{C.RESET} {C.GREEN}{getattr(char, 'luong', 0):,}{C.RESET}")
        print(f"    - {C.GREEN}Ngọc khóa:{C.RESET} {C.PURPLE}{getattr(char, 'luong_khoa', 0):,}{C.RESET}")
        
        print(f"  {C.CYAN}--- Chức năng ---{C.RESET}")
        autoplay_status = f"{C.GREEN}Bật{C.RESET}" if account.controller.auto_play.interval else f"{C.RED}Tắt{C.RESET}"
        autopet_status = f"{C.GREEN}Bật{C.RESET}" if account.controller.auto_pet.is_running else f"{C.RED}Tắt{C.RESET}"
        print(f"    - Tự động đánh: {autoplay_status}")
        print(f"    - Tự động đệ tử: {autopet_status}")

        pet = account.pet
        if pet and pet.have_pet:
            print(f"  {C.CYAN}--- Đệ tử: {pet.name} ---{C.RESET}")
            print(f"    - {C.GREEN}HP:{C.RESET} {C.RED}{pet.c_hp:,}{C.RESET} / {pet.c_hp_full:,} | {C.GREEN}MP:{C.RESET} {C.BLUE}{pet.c_mp:,}{C.RESET} / {pet.c_mp_full:,}")
            print(f"    - {C.GREEN}Sức mạnh:{C.RESET} {C.YELLOW}{pet.c_power:,}{C.RESET}")
        
        print(f"{C.BOLD_RED}" + "-" * (len(account.username) + 20) + f"{C.RESET}\n")

def display_character_base_info(account):
    """Hiển thị thông tin cơ bản, dùng cho cả 'show' và khi acc chưa load xong."""
    C = TerminalColors
    char = account.char
    
    print(f"{C.BOLD_RED}--- Trạng thái: {C.YELLOW}{account.username}{C.BOLD_RED} ---{C.RESET}")
    
    # Status
    status_text = account.status
    if account.status == "Logged In":
        status_color = C.GREEN
        if not char.name: # Phân biệt giữa Login và Loading
             status_text = "Loading..."
    elif account.status == "Reconnecting":
        status_color = C.YELLOW
    else:
        status_color = C.RED
    print(f"  {C.CYAN}Trạng thái:{C.RESET} {status_color}{status_text}{C.RESET}")
    
    # Proxy
    proxy_info = "Local IP"
    if account.proxy:
        try:
            ip_part = account.proxy.split('@')[-1]
            proxy_info = f"Proxy @ {ip_part}"
        except:
            proxy_info = "Proxy"
    print(f"  {C.CYAN}Kết nối:{C.RESET} {C.PURPLE}{proxy_info}{C.RESET}")
    
    if char.name:
        print(f"  {C.CYAN}Nhân vật:{C.RESET} {char.name} ({C.YELLOW}ID: {char.char_id}{C.RESET})")

