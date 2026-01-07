from targeted_commands.base_targeted_command import TargetedCommand
from typing import Any
from account import Account
from logs.logger_config import TerminalColors

class TeleportnpcCommand(TargetedCommand):
    def __init__(self):
        self.C = TerminalColors

    async def execute(self, account: Account, *args, **kwargs) -> Any:
        parts = kwargs.get('parts', [])
        if len(parts) == 2 and parts[1].isdigit():
            npc_id = int(parts[1])
            print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Dịch chuyển tới NPC ID {npc_id}...")
            await account.controller.movement.teleport_to_npc(npc_id)
        else:
            print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Sử dụng: teleportnpc <id>")
        return True, "OK"
