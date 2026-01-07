from commands.base_command import Command
from ui import display_help

class HelpCommand(Command):
    async def execute(self, *args, **kwargs):
        display_help()
        return False
