"""Module chứa các hàm hiển thị help/hướng dẫn."""

from logs.logger_config import TerminalColors as C, print_header, print_section_header, print_separator


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
        ("show boss", "Hiển thị danh sách Boss xuất hiện"),
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
        ("khu", "Hiển thị danh sách khu vực"),
        ("khu <id>", "Chuyển đến khu vực"),
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
    
    # Section: Plugin & Macro
    print_section_header("Plugin & Macro", width=70, color=C.PURPLE)
    cmds = [
        ("plugin list", "Xem danh sách plugin"),
        ("plugin enable/disable <name>", "Bật/Tắt plugin"),
        ("combo <name>", "Chạy combo/macro từ file"),
        ("tapchat <msg>", "Chat nội dung (hỗ trợ target)"),
        ("plugin info <name>", "Xem thông tin chi tiết plugin"),
    ]
    for cmd, desc in cmds:
        print(f"  {C.GREEN}{cmd:<26}{C.RESET} {C.DIM}-{C.RESET} {desc}")
    print()

    # Section: Other
    print_section_header("Khác", width=70, color=C.PURPLE)
    cmds = [
        ("congcs <hp> <mp> <sd>", "Tự động cộng tiềm năng"),
        ("opennpc <id> [menu...]", "Mở NPC và chọn menu"),
        ("cls / clear", "Xóa màn hình"),
        ("exit", "Thoát chương trình"),
    ]
    for cmd, desc in cmds:
        print(f"  {C.GREEN}{cmd:<26}{C.RESET} {C.DIM}-{C.RESET} {desc}")
    
    print()
    print_separator(70, color=C.BRIGHT_CYAN)
    print()


def display_macro_help():
    """Hiển thị hướng dẫn sử dụng hệ thống Macro mới."""
    print()
    print_header("[MACRO] HUONG DAN LAP TRINH MACRO", width=70, color=C.BRIGHT_GREEN)
    print()
    print(f"  {C.CYAN}Hệ thống Macro mới hỗ trợ biến, vòng lặp và logic cơ bản.{C.RESET}")
    print(f"  {C.GREY}Sử dụng dấu # để viết ghi chú (VD: var a 1 # bien a){C.RESET}")
    print()
    
    # Section: Core Commands
    print_section_header("Cấu trúc lệnh cơ bản", width=70, color=C.PURPLE)
    cmds = [
        ("var <name> <val>", "Khai báo biến. VD: var a 10"),
        ("set <name> <expr>", "Gán giá trị mới. VD: set a int(a) + 1"),
        ("print <msg>", "In ra màn hình console (hỗ trợ ${var})"),
        ("sleep <sec>", "Chờ X giây (VD: sleep 1.5)"),
    ]
    for cmd, desc in cmds:
        print(f"  {C.GREEN}{cmd:<26}{C.RESET} {C.DIM}-{C.RESET} {desc}")
    print()

    # Section: Control Flow
    print_section_header("Vòng lặp & Điều kiện", width=70, color=C.PURPLE)
    print(f"  {C.YELLOW}while <condition>{C.RESET}")
    print(f"      ... commands ...")
    print(f"  {C.YELLOW}endwhile{C.RESET}")
    print()
    print(f"  Ví dụ:")
    print(f"    var i 0")
    print(f"    while int(i) < 5")
    print(f"      print Lặp lần ${{i}}")
    print(f"      set i int(i) + 1")
    print(f"      sleep 1")
    print(f"    endwhile")
    print()
    
    # Section: Expressions
    print_section_header("Biểu thức & Toán học", width=70, color=C.PURPLE)
    print(f"  Hỗ trợ các hàm Python cơ bản: {C.CYAN}int(), float(), str(), abs(), round(), math.*{C.RESET}")
    print(f"  Truy cập biến trong lệnh game bằng cú pháp: {C.ORANGE}${{ten_bien}}{C.RESET}")
    print(f"  Trong biểu thức (while/set) có thể dùng tên biến trực tiếp.")
    print()
    print_separator(70, color=C.BRIGHT_GREEN)
    print()
