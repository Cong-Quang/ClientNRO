from targeted_commands.base_targeted_command import TargetedCommand
from typing import Any
from account import Account
from logs.logger_config import TerminalColors

class AiagentCommand(TargetedCommand):
    def __init__(self):
        self.C = TerminalColors

    async def execute(self, account: Account, *args, **kwargs) -> Any:
        parts = kwargs.get('parts', [])
        if len(parts) > 1:
            sub = parts[1]
            
            if sub in ["on", "off"]:
                status = sub == "on"
                account.controller.toggle_ai_agent(status)
                print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Đã {'BẬT' if status else 'TẮT'} AI Agent.")
            
            elif sub == "status":
                # Show AI status for this account
                if account.controller.ai_agent:
                    ai_status = account.controller.ai_agent.get_status()
                    print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] AI Status:")
                    for key, val in ai_status.items():
                        print(f"  {key}: {val}")
                    
                    # DEBUG: Print SharedMemory consistency check
                    debug = account.controller.ai_agent.get_debug_status()
                    print(f"  [DEBUG] SM_ID: {debug['sm_id']}")
                    print(f"  [DEBUG] Groups: {debug['sm_groups']}")
                    print(f"  [DEBUG] Active: {debug['sm_active_groups']}")
                else:
                    print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] AI Agent chưa được khởi tạo.")
            
            elif sub == "train":
                # Enable/disable training
                if len(parts) > 2 and parts[2] in ["on", "off"]:
                    train_status = parts[2] == "on"
                    if account.controller.ai_agent:
                        account.controller.ai_agent.enable_training(train_status)
                        print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Online training {'BẬT' if train_status else 'TẮT'}.")
                    else:
                        print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Cần bật AI Agent trước.")
                else:
                    print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Sử dụng: aiagent train <on|off>")
            
            elif sub == "save":
                # Save current model
                if account.controller.ai_agent:
                    path = account.controller.ai_agent.save_model()
                    print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Model saved: {self.C.GREEN}{path}{self.C.RESET}")
                else:
                    print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] AI Agent chưa được khởi tạo.")
            
            else:
                print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Sử dụng: aiagent <on|off|status|train|save>")
        else:
            print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Sử dụng: aiagent <on|off|status|train|save>")
        return True, "OK"
