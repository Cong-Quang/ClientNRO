from commands.base_command import Command

class ExitCommand(Command):
    def __init__(self, manager):
        self.manager = manager

    async def execute(self, *args, **kwargs) -> bool:
        print("Đang dừng tất cả các tài khoản...")
        self.manager.stop_all()
        return True
