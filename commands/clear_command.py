import os
from commands.base_command import Command

class ClearCommand(Command):
    async def execute(self, *args, **kwargs):
        os.system('cls' if os.name == 'nt' else 'clear')
        return False
