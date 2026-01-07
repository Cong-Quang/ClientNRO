from targeted_commands.base_targeted_command import TargetedCommand
from typing import Any
from core.account import Account
from logs.logger_config import set_logger_status

class LoggerCommand(TargetedCommand):
    async def execute(self, account: Account, *args, **kwargs) -> Any:
        parts = kwargs.get('parts', [])
        if len(parts) > 1 and parts[1] in ["on", "off"]:
            status = parts[1] == "on"
            set_logger_status(status)
            print(f"Đã {'BẬT' if status else 'TẮT'} logger.")
        else:
            print("Sử dụng: logger <on|off>")
        return True, "OK"
