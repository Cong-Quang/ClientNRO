from targeted_commands.base_targeted_command import TargetedCommand
from typing import Any
from core.account import Account
from logs.logger_config import TerminalColors

class AutobossCommand(TargetedCommand):
    def __init__(self):
        self.C = TerminalColors

    async def execute(self, account: Account, *args, **kwargs) -> Any:
        parts = kwargs.get('parts', [])
        if len(parts) > 1:
            sub = parts[1]
            
            # Queue management (support both 'add' and 'queue')
            if sub in ["add", "queue"]:
                # autoboss add <boss_name> hoặc autoboss add Boss1,Boss2,Boss3
                if len(parts) > 2:
                    boss_input = " ".join(parts[2:])
                    
                    # Check if comma-separated (nhiều boss)
                    if "," in boss_input:
                        boss_names = [name.strip() for name in boss_input.split(",")]
                        for boss_name in boss_names:
                            if boss_name:
                                account.controller.auto_boss.add_to_queue(boss_name)
                        print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Đã thêm {self.C.PURPLE}{len(boss_names)} bosses{self.C.RESET} vào queue")
                    else:
                        # Single boss
                        account.controller.auto_boss.add_to_queue(boss_input)
                        print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Đã thêm '{self.C.PURPLE}{boss_input}{self.C.RESET}' vào queue")
                else:
                    print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Sử dụng: autoboss add <tên boss> hoặc autoboss add Boss1,Boss2,Boss3")
            
            elif sub == "start":
                # autoboss start (start queue mode)
                account.controller.auto_boss.start_queue()
                queue_size = len(account.controller.auto_boss.boss_queue)
                if queue_size > 0:
                    print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] {self.C.GREEN}Bắt đầu săn {queue_size} bosses theo queue{self.C.RESET}")
            
            elif sub == "clear":
                # autoboss clear (clear queue)
                account.controller.auto_boss.clear_queue()
                print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Đã xóa queue")
            
            elif sub == "list":
                # autoboss list (show queue)
                queue_info = account.controller.auto_boss.show_queue()
                print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}]")
                print(queue_info)
            
            elif sub == "stop":
                account.controller.toggle_auto_boss(False)
                print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] {self.C.RED}Đã dừng Auto Boss{self.C.RESET}")
                
            elif sub == "status":
                ab = account.controller.auto_boss
                if ab.is_running:
                    mode = "QUEUE" if ab.use_queue_mode else "SINGLE"
                    print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Auto Boss: {self.C.GREEN}RUNNING{self.C.RESET} ({mode} mode)")
                    print(f"  Target: {self.C.PURPLE}{ab.target_boss_name}{self.C.RESET}")
                    print(f"  State: {self.C.CYAN}{ab.state.value}{self.C.RESET}")
                    if ab.use_queue_mode:
                        print(f"  Queue Progress: [{ab.current_boss_index}/{len(ab.boss_queue)-1}]")
                    if ab.target_map_id != -1:
                        print(f"  Map: {ab.target_map_id}, Zone: {ab.target_zone_id}")
                else:
                    print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Auto Boss: {self.C.RED}STOPPED{self.C.RESET}")
                    queue_size = len(account.controller.auto_boss.boss_queue)
                    if queue_size > 0:
                        print(f"  Queue: {queue_size} bosses waiting")
                        
            else:
                # Tên boss là phần còn lại của command (single boss mode)
                boss_name = " ".join(parts[1:])
                account.controller.toggle_auto_boss(True, boss_name)
                print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] {self.C.GREEN}Bắt đầu Auto Boss (Single): {self.C.PURPLE}{boss_name}{self.C.RESET}")
        else:
            print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Sử dụng:")
            print(f"  autoboss <tên boss>                    - Săn 1 boss")
            print(f"  autoboss add <boss>                    - Thêm boss vào queue")
            print(f"  autoboss add Boss1,Boss2,Boss3         - Thêm nhiều boss")
            print(f"  autoboss start                         - Bắt đầu queue")
            print(f"  autoboss list                          - Xem queue")
            print(f"  autoboss clear                         - Xóa queue")
            print(f"  autoboss stop                          - Dừng")
            print(f"  autoboss status                        - Trạng thái")
        return True, "OK"
