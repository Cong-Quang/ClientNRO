"""Module chứa hàm hiển thị items."""

from logs.logger_config import TerminalColors as C, Box as B, print_header, print_separator


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
