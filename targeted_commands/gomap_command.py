from targeted_commands.base_targeted_command import TargetedCommand
from typing import Any
from account import Account
from logs.logger_config import TerminalColors

class GomapCommand(TargetedCommand):
    def __init__(self):
        self.C = TerminalColors

    async def execute(self, account: Account, *args, **kwargs) -> Any:
        parts = kwargs.get('parts', [])
        if len(parts) > 1:
            if parts[1] == "stop":
                account.controller.xmap.finish()
                print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Đã dừng XMap.")
            elif parts[1] == "home":
                print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Đang về nhà...")
                await account.controller.xmap.go_home()
            else:
                try:
                    map_id = int(parts[1])
                    print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Bắt đầu XMap tới {map_id}...")
                    await account.controller.xmap.start(map_id)
                except ValueError:
                    print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Map ID không hợp lệ: {parts[1]}")
        else:
            print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Sử dụng: gomap <map_id> | gomap home | gomap stop")
        return True, "OK"
