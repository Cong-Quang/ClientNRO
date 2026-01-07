from targeted_commands.base_targeted_command import TargetedCommand
from typing import Any
from account import Account
from logs.logger_config import TerminalColors

class FindnpcCommand(TargetedCommand):
    def __init__(self):
        self.C = TerminalColors

    async def execute(self, account: Account, *args, **kwargs) -> Any:
        npcs = account.controller.npcs
        if not npcs:
            print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Không tìm thấy NPC nào trên bản đồ hiện tại.")
        else:
            print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Các NPC trên bản đồ:")
            for npc_id, npc_data in npcs.items():
                # thêm màu sắc cho npc id map
                template_id = npc_data.get('template_id', 'N/A')
                raw_name = npc_data.get('name')
                if raw_name:
                    name = f"{raw_name} ({template_id})"
                else:
                    name = f"NPC {template_id}"
                x = npc_data.get('x', 'N/A')
                y = npc_data.get('y', 'N/A')
                print(f" - ID: {self.C.CYAN}{npc_id + 1}{self.C.RESET}, Tên: {self.C.GREEN}{name}{self.C.RESET}, Vị trí: ({x}, {y})")
        return True, "OK"
