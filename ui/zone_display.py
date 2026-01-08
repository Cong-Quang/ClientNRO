"""Module chứa các hàm hiển thị zone và boss."""

from datetime import datetime
from logs.logger_config import TerminalColors as C, Box as B, print_header, print_separator


def display_zone_list(zones_data: list, map_name: str, account_name: str, current_zone_id: int = -1, map_id: int = -1):
    """Hiển thị danh sách khu vực và số lượng người chơi."""
    print()
    # Hiển thị map_id trong header nếu có
    if map_id != -1:
        width = 50
        print_header(f"[ZONE] {map_name} [ID:{map_id}] ({account_name})", width=width, color=C.CYAN)
    else:
        width = 40
        print_header(f"[ZONE] {map_name} ({account_name})", width=width, color=C.CYAN)
    
    # Header
    print(f"  {C.BOLD}{C.BRIGHT_CYAN}{'Zone':<8} {'Người Chơi':<12}{C.RESET}")
    print(f"  {C.DIM}{B.H * (width - 4)}{C.RESET}")
    
    # Sort zones by Zone ID (ascending) for cleaner list
    sorted_zones = sorted(zones_data, key=lambda x: x['zone_id'])
    
    for z in sorted_zones:
        z_id = z['zone_id']
        curr = z['num_players']
        max_p = z['max_players']
        
        # Format: curr/max
        player_info = f"{curr}/{max_p}"
        
        # Color coding for occupancy
        if curr >= max_p:
            p_color = C.RED      # Full
        elif curr >= max_p * 0.8:
            p_color = C.YELLOW   # Crowded
        else:
            p_color = C.GREEN    # Good
            
        # Highlight current zone
        if z_id == current_zone_id:
            z_display = f"{z_id} (*)"
            z_color = C.BRIGHT_CYAN
        else:
            z_display = f"{z_id}"
            z_color = C.CYAN
            
        print(f"  {z_color}{z_display:<8}{C.RESET} {p_color}{player_info:<12}{C.RESET}")

    print(f"  {C.DIM}{B.H * (width - 4)}{C.RESET}")
    print(f"  {C.BRIGHT_WHITE}Tổng:{C.RESET} {C.BRIGHT_YELLOW}{len(zones_data)}{C.RESET} khu")
    print_separator(width, color=C.CYAN)


def display_boss_list(bosses: list):
    """Hiển thị danh sách Boss đã xuất hiện."""
    try:
        print()
        print_header("[BOSS] DANH SACH BOSS XUAT HIEN", width=80, color=C.RED)
        
        if not bosses:
            print(f"  {C.GREY}Chưa có thông tin boss nào xuất hiện gần đây.{C.RESET}")
            print_separator(80, color=C.RED)
            return

        # Format columns: Name(28) Map(22) Zone(6) Status(12) MapID(8) Time(15)
        # Using a fixed format string helps alignment
        row_fmt = "  {color}{name:<28} {map_name:<22} {zone:^6} {status_display:<12} {map_id_str:<8} {time_str:<15}{C.RESET}"
        header_fmt = f"  {C.BOLD}{C.BOLD_RED}{'Boss':<28} {'Bản Đồ':<22} {'Khu':^6} {'Trạng Thái':<12} {'Map ID':<8} {'Thời Gian':<15}{C.RESET}"

        # Header
        print(header_fmt)
        print(f"  {C.DIM}{B.H * 95}{C.RESET}")

        now = datetime.now()
        for b in bosses:
            name = b['name'][:27] # Truncate to fit
            map_name = b['map'][:21] # Truncate to fit
            zone = str(b['zone']) if b['zone'] != -1 else "?"
            spawn_time = b['time']
            status = b.get('status', 'Sống')
            map_id_val = b.get('map_id', -1)
            map_id_str = f"[{map_id_val}]" if map_id_val != -1 else "[?]"
            
            # Calculate elapsed time
            elapsed = now - spawn_time
            total_seconds = int(elapsed.total_seconds())
            
            if total_seconds < 60:
                time_str = f"{total_seconds}s trước"
            else:
                time_str = f"{total_seconds // 60}p trước"
                
            # Color logic:
            if status == 'Chết':
                color = C.RED
                status_display = "Đã chết"
                curr_color = C.RED
            elif total_seconds >= 15 * 60:
                color = C.RED
                status_display = "Sống (?)"
                curr_color = C.RED
            else:
                color = C.BRIGHT_GREEN # or C.GREEN
                status_display = "Sống"
                curr_color = C.BRIGHT_GREEN
            
            print(f"  {curr_color}{name:<28} {map_name:<22} {zone:^6} {status_display:<12} {map_id_str:<8} {time_str:<15}{C.RESET}")

        print(f"  {C.DIM}{B.H * 95}{C.RESET}")
        print_separator(90, color=C.RED)
    except Exception as e:
        print(f"{C.RED}Error displaying boss list: {e}{C.RESET}")
