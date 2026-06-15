from targeted_commands.base_targeted_command import TargetedCommand
from logs.logger_config import TerminalColors
from core.account import Account
import asyncio
from typing import Any

class CongcsCommand(TargetedCommand):
    def __init__(self):
        self.C = TerminalColors
        self.running_tasks = {}

    async def execute(self, account: Account, *args, **kwargs) -> Any:
        parts = kwargs.get('parts', [])
        if len(parts) >= 2 and parts[1].lower() == "stop":
            if account.username in self.running_tasks:
                self.running_tasks[account.username] = False
                print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Đã dừng tự động cộng chỉ số.")
            return True, "OK"

        if len(parts) < 4:
            print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] {self.C.RED}Sử dụng: congcs <hp> <mp> <sd> (hoặc congcs stop){self.C.RESET}")
            return True, "OK"

        try:
            hp_clicks = int(parts[1])
            mp_clicks = int(parts[2])
            sd_clicks = int(parts[3])
        except ValueError:
            print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] {self.C.RED}Các tham số <hp>, <mp>, <sd> phải là số!{self.C.RESET}")
            return True, "OK"

        if account.username in self.running_tasks and self.running_tasks[account.username]:
            print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Đang tự động cộng chỉ số rồi. Gõ 'congcs stop' để dừng.")
            return True, "OK"

        self.running_tasks[account.username] = True
        print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Bắt đầu cộng: {hp_clicks} HP, {mp_clicks} MP, {sd_clicks} SD")
        
        asyncio.create_task(self._auto_congcs(account, hp_clicks, mp_clicks, sd_clicks))
        return True, "OK"

    async def _auto_congcs(self, account: Account, hp: int, mp: int, sd: int):
        username = account.username
        
        async def up(type_pt, count):
            while count > 0 and self.running_tasks.get(username, False):
                num = 100 if count >= 100 else (10 if count >= 10 else 1)
                await account.service.up_potential(type_pt, num)
                count -= num
                await asyncio.sleep(0.2)

        if hp > 0: await up(0, hp)
        if mp > 0: await up(1, mp)
        if sd > 0: await up(2, sd)

        if self.running_tasks.get(username, False):
            print(f"[{self.C.YELLOW}{username}{self.C.RESET}] {self.C.GREEN}Đã cộng xong chỉ số!{self.C.RESET}")
        self.running_tasks[username] = False
