from targeted_commands.base_targeted_command import TargetedCommand
from typing import Any
from account import Account
import asyncio
from ui import display_pet_info, display_pet_help
from logs.logger_config import TerminalColors

class PetCommand(TargetedCommand):
    def __init__(self):
        self.C = TerminalColors

    async def execute(self, account: Account, *args, **kwargs) -> Any:
        parts = kwargs.get('parts', [])
        compact_mode = kwargs.get('compact_mode', False)
        idx = kwargs.get('idx')

        if len(parts) == 1:
            display_pet_help()
        else:
            sub_cmd = parts[1]
            if sub_cmd == "info":
                await account.service.pet_info()
                await asyncio.sleep(0.5)
                # This now needs the specific pet object and username (and optional idx for compact view)
                display_pet_info(account.pet, account.username, compact=compact_mode, idx=idx)
            elif sub_cmd in {"follow", "protect", "attack", "home"}:
                status_map = {"follow": 0, "protect": 1, "attack": 2, "home": 3}
                await account.service.pet_status(status_map[sub_cmd])
            else:
                print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Lệnh đệ tử không xác định: '{sub_cmd}'.")
        return True, "OK"
