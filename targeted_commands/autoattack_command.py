from targeted_commands.base_targeted_command import TargetedCommand
from typing import Any
from account import Account
from logs.logger_config import TerminalColors

class AutoattackCommand(TargetedCommand):
    def __init__(self):
        self.C = TerminalColors

    async def execute(self, account: Account, *args, **kwargs) -> Any:
        parts = kwargs.get('parts', [])
        if len(parts) > 1:
            sub = parts[1]
            
            if sub in ["on", "off"]:
                status = sub == "on"
                account.controller.toggle_auto_attack(status)
                print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Đã {'BẬT' if status else 'TẮT'} autoattack.")
            
            elif sub == "target":
                # Lazy init auto_attack
                if account.controller.auto_attack is None:
                    from logic.auto_attack import AutoAttack
                    account.controller.auto_attack = AutoAttack(account.controller)
                
                if len(parts) > 2:
                    target_arg = parts[2]
                    
                    # autoattack target nearest [mob|char|both]
                    if target_arg == "nearest":
                        target_type = parts[3] if len(parts) > 3 else "both"
                        if account.controller.auto_attack.set_target_nearest(target_type):
                            print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] {self.C.GREEN}Đã target {target_type} gần nhất{self.C.RESET}")
                        else:
                            print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] {self.C.RED}Không tìm thấy target{self.C.RESET}")
                    
                    # autoattack target mob <id>
                    elif target_arg == "mob":
                        if len(parts) > 3 and parts[3].isdigit():
                            mob_id = int(parts[3])
                            if account.controller.auto_attack.set_target_mob(mob_id):
                                print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] {self.C.GREEN}Đã target Mob {mob_id}{self.C.RESET}")
                            else:
                                print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] {self.C.RED}Mob {mob_id} không tồn tại{self.C.RESET}")
                        else:
                            print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Sử dụng: autoattack target mob <id>")
                    
                    # autoattack target char <id>
                    elif target_arg == "char":
                        if len(parts) > 3 and parts[3].isdigit():
                            char_id = int(parts[3])
                            if account.controller.auto_attack.set_target_char(char_id):
                                print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] {self.C.GREEN}Đã target Char {char_id}{self.C.RESET}")
                            else:
                                print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] {self.C.RED}Char {char_id} không tồn tại{self.C.RESET}")
                        else:
                            print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Sử dụng: autoattack target char <id>")
                    
                    # autoattack target name <tên> [mob|char|both]
                    elif target_arg == "name":
                        if len(parts) > 3:
                            target_name = parts[3]
                            target_type = parts[4] if len(parts) > 4 else "both"
                            if account.controller.auto_attack.set_target_by_name(target_name, target_type):
                                print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] {self.C.GREEN}Đã target '{target_name}'{self.C.RESET}")
                            else:
                                print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] {C.RED}Không tìm thấy '{target_name}'{self.C.RESET}")
                        else:
                            print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Sử dụng: autoattack target name <tên> [mob|char|both]")
                    
                    else:
                        print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Sử dụng: autoattack target <nearest|mob|char|name>")
                else:
                    print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Sử dụng: autoattack target <nearest|mob|char|name> [args]")

            
            elif sub == "clear":
                # Lazy init auto_attack
                if account.controller.auto_attack is None:
                    from logic.auto_attack import AutoAttack
                    account.controller.auto_attack = AutoAttack(account.controller)
                
                account.controller.auto_attack.clear_target()
                print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Đã xóa target")
            
            else:
                print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Sử dụng: autoattack <on|off|target|clear>")
        else:
            print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Sử dụng: autoattack <on|off|target|clear>")
        return True, "OK"
