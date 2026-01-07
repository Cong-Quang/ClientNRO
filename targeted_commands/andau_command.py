from targeted_commands.base_targeted_command import TargetedCommand
from typing import Any
from account import Account

class AndauCommand(TargetedCommand):
    async def execute(self, account: Account, *args, **kwargs) -> Any:
        await account.controller.eat_pea()
        return True, "OK"
