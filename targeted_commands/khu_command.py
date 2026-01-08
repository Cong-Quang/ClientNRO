from targeted_commands.base_targeted_command import TargetedCommand
from typing import Any
from core.account import Account
from logs.logger_config import TerminalColors

class KhuCommand(TargetedCommand):
    """Lệnh quản lý khu vực (zone)
    - khu: Hiển thị danh sách khu vực
    - khu <id>: Chuyển đến khu vực
    """
    def __init__(self):
        self.C = TerminalColors

    async def execute(self, account: Account, *args, **kwargs) -> Any:
        parts = kwargs.get('parts', [])
        
        # Nếu không có tham số, hiển thị danh sách khu vực
        if len(parts) == 1:
            try:
                print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Đang yêu cầu danh sách khu vực...")
                await account.service.open_zone_ui()
                return True, "OK"
            except Exception as e:
                print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] {self.C.RED}Lỗi khi lấy danh sách khu vực: {e}{self.C.RESET}")
                return False, str(e)
        
        # Nếu có tham số, chuyển đến khu vực
        if not parts[1].isdigit():
            print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] {self.C.RED}Zone ID phải là số!{self.C.RESET}")
            print(f"  {self.C.DIM}Sử dụng:{self.C.RESET}")
            print(f"    {self.C.GREEN}khu{self.C.RESET}        - Hiển thị danh sách khu vực")
            print(f"    {self.C.GREEN}khu <id>{self.C.RESET}   - Chuyển đến khu vực")
            return False, "Invalid zone_id"
        
        zone_id = int(parts[1])
        
        if zone_id < 0:
            print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] {self.C.RED}Zone ID phải >= 0{self.C.RESET}")
            return False, "Invalid zone_id"
        
        try:
            print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Đang chuyển đến khu vực {self.C.CYAN}{zone_id}{self.C.RESET}...")
            await account.service.request_change_zone(zone_id)
            return True, "OK"
        except Exception as e:
            print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] {self.C.RED}Lỗi khi chuyển khu vực: {e}{self.C.RESET}")
            return False, str(e)
