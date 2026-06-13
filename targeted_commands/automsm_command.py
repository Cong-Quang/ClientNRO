from targeted_commands.base_targeted_command import TargetedCommand
from typing import Any
from core.account import Account
from logs.logger_config import TerminalColors as C

class AutomsmCommand(TargetedCommand):
    async def execute(self, account: Account, *args, **kwargs) -> Any:
        parts = kwargs.get('parts', [])
        
        if len(parts) >= 2:
            action = parts[1].lower()
            if action in ["banthan", "detu"]:
                account.controller.auto_msm.start(target=action)
                print(f"[{C.YELLOW}{account.username}{C.RESET}] Bật Auto Mở Sức Mạnh (Mục tiêu: {action})")
            elif action == "stop":
                account.controller.auto_msm.stop()
                print(f"[{C.YELLOW}{account.username}{C.RESET}] Đã tắt Auto Mở Sức Mạnh")
            else:
                print(f"[{C.YELLOW}{account.username}{C.RESET}] Sử dụng: automsm <banthan|detu|stop>")
        else:
            print(f"[{C.YELLOW}{account.username}{C.RESET}] Sử dụng: automsm <banthan|detu|stop>")
        return True, "OK"
