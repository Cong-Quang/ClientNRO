from targeted_commands.base_targeted_command import TargetedCommand
from typing import Any
from account import Account
from logs.logger_config import TerminalColors
from ui import Box

class AutobomongCommand(TargetedCommand):
    def __init__(self):
        self.C = TerminalColors
        self.B = Box

    async def execute(self, account: Account, *args, **kwargs) -> Any:
        parts = kwargs.get('parts', [])
        compact_mode = kwargs.get('compact_mode', False)
        if len(parts) > 1:
            sub = parts[1]
            if sub == "on":
                account.controller.toggle_auto_quest(True)
                print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] {self.C.GREEN}Đã BẬT Auto Bo Mong{self.C.RESET}")
            elif sub == "off":
                account.controller.toggle_auto_quest(False)
                # Hiển thị thống kê khi tắt
                stats = account.controller.auto_quest.get_stats()
                print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] {self.C.RED}Đã TẮT Auto Bo Mong{self.C.RESET}")
                if stats["quests_completed"] > 0 or stats["total_kills"] > 0:
                    print(f"Thống kê: {self.C.GREEN}{stats['quests_completed']}{self.C.RESET} NV | {self.C.CYAN}{stats['total_kills']}{self.C.RESET} quái | ⏱️ {stats['time_str']}")
            elif sub == "status":
                aq = account.controller.auto_quest
                status = aq.current_state.value
                is_running = aq.is_running
                stats = aq.get_stats()
                
                if compact_mode:
                    # Mode gọn cho nhiều account - Align với header trong ui.py
                    quest_short = aq.quest_info.mob_name[:16] if aq.quest_info.is_valid else "-"
                    progress = f"{aq.quest_info.current_progress}/{aq.quest_info.target_count}" if aq.quest_info.is_valid else "-"
                    rem = stats.get('quests_remaining', 0)
                    tot = stats.get('quests_total', 0)
                    nv_str = f"{rem}/{tot}" if tot > 0 else f"{stats['quests_completed']}"
                    
                    # On/Off
                    on_txt = "[ON]" if is_running else "[--]"
                    on_col = f"{self.C.BRIGHT_GREEN}{on_txt}{self.C.RESET}" if is_running else f"{self.C.RED}{on_txt}{self.C.RESET}"
                    
                    # Row Format: User(14) | On(4) | Status(20) | NV(4) | Quái(6) | NV Hiện tại(16) | Tiến độ
                    user_padded = f"[{account.username}]"
                    user_padded = f"{user_padded:<14}"
                    
                    row = (
                        f" {self.C.YELLOW}{user_padded}{self.C.RESET} {self.C.DIM}|{self.C.RESET} "
                        f"{on_col} {self.C.DIM}|{self.C.RESET} "
                        f"{status:<20} {self.C.DIM}|{self.C.RESET} "
                        f"{self.C.CYAN}{nv_str:<5}{self.C.RESET} {self.C.DIM}|{self.C.RESET} "
                        f"{self.C.GREEN}{stats['total_kills']:<6}{self.C.RESET} {self.C.DIM}|{self.C.RESET} "
                        f"{quest_short:<16} {self.C.DIM}|{self.C.RESET} "
                        f"{progress}"
                    )
                    print(row)
                else:
                    # Mode chi tiết cho 1 account
                    running_str = f"{self.C.GREEN}Đang chạy{self.C.RESET}" if is_running else f"{self.C.RED}Đã dừng{self.C.RESET}"
                    print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Auto Bo Mong")
                    print(f"Trạng thái: {running_str} | {self.C.CYAN}{status}{self.C.RESET}")
                    print(f"Thống kê: {self.C.GREEN}{stats['quests_completed']}{self.C.RESET} NV hoàn thành | {self.C.CYAN}{stats['total_kills']}{self.C.RESET} quái đã giết | {stats['time_str']}")
                    if aq.quest_info.is_valid:
                        print(f"NV hiện tại: {self.C.PURPLE}{aq.quest_info.mob_name}{self.C.RESET} ({aq.quest_info.current_progress}/{aq.quest_info.target_count})")
                    else:
                        print(f"NV hiện tại: {self.C.GREY}Chưa có{self.C.RESET}")
            else:
                print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Sử dụng: autobomong <on|off|status>")
        else:
            print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Sử dụng: autobomong <on|off|status>")
        return True, "OK"
