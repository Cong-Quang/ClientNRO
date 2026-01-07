from targeted_commands.base_targeted_command import TargetedCommand
from typing import Any
from core.account import Account

class HitCommand(TargetedCommand):
    async def execute(self, account: Account, *args, **kwargs) -> Any:
        await account.controller.attack_nearest_mob()
        return True, "OK"
