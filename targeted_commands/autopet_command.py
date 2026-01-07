from targeted_commands.base_targeted_command import TargetedCommand
from typing import Any
from account import Account
from logs.logger_config import TerminalColors

class AutopetCommand(TargetedCommand):
    def __init__(self):
        self.C = TerminalColors

    async def execute(self, account: Account, *args, **kwargs) -> Any:
        parts = kwargs.get('parts', [])
        if len(parts) > 1 and parts[1] in ["on", "off"]:
            status = parts[1] == "on"
            account.controller.toggle_auto_pet(status)
            print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Đã {'BẬT' if status else 'TẮT'} autopet.")
        else:
            print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Sử dụng: autopet <on|off>")
        return True, "OK"
