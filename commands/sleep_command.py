import asyncio
from commands.base_command import Command

class SleepCommand(Command):
    async def execute(self, *args, **kwargs) -> bool:
        parts = kwargs.get('parts', [])
        if len(parts) > 1:
            try:
                duration = float(parts[1])
                await asyncio.sleep(duration)
            except (ValueError, IndexError):
                print("Sử dụng: sleep <giây>")
        else:
            print("Sử dụng: sleep <giây>")
        return False
