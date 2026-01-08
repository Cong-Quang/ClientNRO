from commands.base_command import Command
import asyncio

class WaitCommand(Command):
    """
    Pause execution for a specified duration (in seconds).
    Usage: wait <seconds>
    """
    async def execute(self, parts):
        if len(parts) < 2:
            print("Usage: wait <seconds>")
            return
        
        try:
            duration = float(parts[1])
            await asyncio.sleep(duration)
        except ValueError:
            print("Invalid duration format.")
