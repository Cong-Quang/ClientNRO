from targeted_commands.base_targeted_command import TargetedCommand

class TapChatCommand(TargetedCommand):
    def __init__(self):
        super().__init__()

    async def execute(self, account, parts, compact_mode=False, idx=None):
        if len(parts) < 2:
            return False, "Cú pháp: tapchat <message>"

        message = " ".join(parts[1:])
        
        if hasattr(account, 'service') and account.service:
             # Delay a bit to ensure natural behavior? No, macro handles delays.
             await account.service.send_chat(message)
             return True, f"[{account.username}] Chat: {message}"
        else:
             return False, f"[{account.username}] Không có service"
