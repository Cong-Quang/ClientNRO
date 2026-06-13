from targeted_commands.base_targeted_command import TargetedCommand
from typing import Any
from core.account import Account
from logs.logger_config import TerminalColors

class TeleportCommand(TargetedCommand):
    def __init__(self):
        self.C = TerminalColors

    async def execute(self, account: Account, *args, **kwargs) -> Any:
        parts = kwargs.get('parts', [])
        
        if len(parts) == 3 and parts[1].lower() == 'npc' and parts[2].isdigit():
            npc_id = int(parts[2])
            print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Dịch chuyển tới NPC {npc_id}...")
            success = await account.controller.movement.teleport_to_npc(npc_id)
            if not success:
                print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Không tìm thấy NPC {npc_id} trong map hiện tại.")
            return True, "OK"
            
        elif len(parts) == 3 and parts[1].isdigit() and parts[2].isdigit():
            x, y = int(parts[1]), int(parts[2])
            print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Dịch chuyển tới ({x}, {y})...")
            await account.controller.movement.teleport_to(x, y)
        else:
            print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Sử dụng: teleport <x> <y> HOẶC teleport npc <id>")
        return True, "OK"
