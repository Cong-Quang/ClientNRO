from targeted_commands.base_targeted_command import TargetedCommand
from typing import Any
from account import Account
from logs.logger_config import TerminalColors

class AutoplayCommand(TargetedCommand):
    def __init__(self):
        self.C = TerminalColors

    async def execute(self, account: Account, *args, **kwargs) -> Any:
        parts = kwargs.get('parts', [])
        if len(parts) > 1:
            sub = parts[1]
            if sub in ["on", "off"]:
                status = sub == "on"
                account.controller.toggle_autoplay(status)
                print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Đã {'BẬT' if status else 'TẮT'} autoplay.")
            elif sub == "add":
                # autoplay add id1 id2 ...
                ids = []
                for x in parts[2:]:
                    if x.isdigit():
                        ids.append(int(x))
                if ids:
                    account.controller.auto_play.target_mobs.update(ids)
                    print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Đã thêm ID quái: {ids}")
                else:
                    print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Vui lòng cung cấp ID quái (số).")
            elif sub == "remove":
                    # autoplay remove id1 id2 ...
                ids = []
                for x in parts[2:]:
                    if x.isdigit():
                        ids.append(int(x))
                if ids:
                    account.controller.auto_play.target_mobs.difference_update(ids)
                    print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Đã xóa ID quái: {ids}")
                else:
                    print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Vui lòng cung cấp ID quái (số).")
            elif sub == "list":
                current = account.controller.auto_play.target_mobs
                if current:
                    print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Danh sách quái mục tiêu: {current}")
                else:
                    print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Danh sách trống (Đánh tất cả).")
            else:
                    print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Lệnh con không hợp lệ: {sub}")
        else:
            print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Sử dụng: autoplay <on|off|add|remove|list>")
        return True, "OK"
