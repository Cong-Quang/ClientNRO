"""
Setup Accounts Command — tự động setup tài khoản mới hoàn chỉnh.

State Machine Flow:
  STEP 1  → Create Character (nếu chưa có)
  STEP 2  → Select Character (vào game)
  STEP 3  → Go Home
  STEP 4  → Open NPC Ông Muri
  STEP 5  → Claim Rewards (vàng + ngọc + giftcode + đệ tử)
  STEP 6  → Farm Beans (1000 đậu thần)
  STEP 7  → Buy BUA (Vách Núi Moori)
  STEP 8  → Santa Shop (Đảo Kame)
  STEP 9  → Use Support Items (1182 → 441, 1680)
  STEP 10 → Activate Reward Items (2000, 290, 1269, 1357, 1649, 1983, 1499, 1323)
  STEP 11 → Upgrade Item 16 (Bà Hạt Mít - Ép Sao Trang Bị x11)
  STEP 12 → Upgrade Items 1, 22, 28, 12 (Bà Hạt Mít - Ép Sao Trang Bị)

Các bước chi tiết được tách riêng trong package commands/setup/.
"""

import asyncio
from typing import Any

from commands.base_command import Command
from logs.logger_config import TerminalColors

from commands.setup.constants import (
    ALL_STEPS, STEP_LABELS, RETRY_CONFIGS,
    STEP_CREATE_CHAR, STEP_SELECT_CHAR, STEP_GO_HOME, STEP_OPEN_MURI,
    STEP_CLAIM_REWARDS, STEP_FARM_BEANS, STEP_BUY_BUA, STEP_SANTA_SHOP,
    STEP_USE_SUPPORT, STEP_ACTIVATE_ITEMS, STEP_UPGRADE_16, STEP_UPGRADE_OTHER,
    TARGET_BEAN_QTY, ITEM_441, ITEM_UPGRADE_16, ITEM_12, BUA_ITEM_IDS,
)
from commands.setup.state_manager import SetupStateManager
from commands.setup.retry_utils import RetryConfig, retry_operation
from commands.setup.inventory_helpers import count_beans, count_item, count_bua_items

# Import các step handlers
from commands.setup.step_character import create_character, select_character
from commands.setup.step_rewards import open_muri, claim_rewards
from commands.setup.step_farm_beans import farm_magic_tree
from commands.setup.step_buy_bua import buy_bua
from commands.setup.step_santa_shop import santa_shop
from commands.setup.step_support_items import use_support_items
from commands.setup.step_activate_items import activate_items
from commands.setup.step_upgrade import upgrade_item_16, upgrade_other_items


# ── Cấu hình timeout cho mỗi step (giây) ─────
STEP_TIMEOUTS = {
    STEP_FARM_BEANS: 90.0,
    STEP_GO_HOME: 90.0,
    STEP_BUY_BUA: 60.0,
    STEP_SANTA_SHOP: 60.0,
    STEP_UPGRADE_16: 90.0,
    STEP_UPGRADE_OTHER: 120.0,
}
DEFAULT_STEP_TIMEOUT = 30.0


class SetupAccountsCommand(Command):
    """Lệnh tự động setup tài khoản mới — dựa trên state machine."""

    def __init__(self, manager=None):
        self.C = TerminalColors
        self.manager = manager
        self.state_mgr = SetupStateManager()
        self.state_mgr.load()

    # ── Logging ────────────────────────────────

    def _log(self, acc, msg: str):
        C = self.C
        prefix = f"[{C.YELLOW}{acc.username}{C.RESET}]"
        display = msg[2:] if msg.startswith("  ") else msg
        print(f"{prefix} {display}")

    def _step_log(self, acc, step: int, msg: str):
        label = STEP_LABELS.get(step, f"Step {step}")
        self._log(acc, f"[{label}] {msg}")

    # ── Entry Point ────────────────────────────

    async def execute(self, *args, **kwargs) -> Any:
        parts = kwargs.get('parts', [])
        C = self.C

        if not self.manager:
            print(f"{C.RED}Lỗi: Không tìm thấy AccountManager.{C.RESET}")
            return False

        if len(parts) < 3:
            print(f"{C.YELLOW}Cú pháp: setup_accounts <start> <end> [force|reset|start_step=N]{C.RESET}")
            print(f"  Ví dụ: {C.CYAN}setup_accounts 0 9{C.RESET}")
            print(f"        {C.CYAN}setup_accounts 0 9 force{C.RESET}")
            print(f"        {C.CYAN}setup_accounts 0 9 reset{C.RESET}")
            print(f"        {C.CYAN}setup_accounts 0 9 start_step=7{C.RESET}  (chạy từ step 7)")
            print()
            print(f"  {C.BOLD}Danh sách Steps:{C.RESET}")
            for step in ALL_STEPS:
                label = STEP_LABELS.get(step, f"Step {step}")
                print(f"    {C.CYAN}{step:>2}{C.RESET} → {label}")
            return False

        try:
            start_idx = int(parts[1])
            end_idx = int(parts[2])
        except ValueError:
            print(f"{C.RED}Chỉ số không hợp lệ.{C.RESET}")
            return False

        if start_idx < 0 or end_idx >= len(self.manager.accounts) or start_idx > end_idx:
            print(f"{C.RED}Khoảng không hợp lệ (0-{len(self.manager.accounts) - 1}).{C.RESET}")
            return False

        force = False
        reset_state = False
        start_step = 1
        if len(parts) >= 4:
            for p in parts[3:]:
                pl = p.lower()
                if pl in ('force', 'again', 'true', '1'):
                    force = True
                elif pl == 'reset':
                    reset_state = True
                elif pl.startswith('start_step='):
                    try:
                        start_step = int(pl.split('=')[1])
                    except ValueError:
                        pass

        accounts = self.manager.accounts[start_idx:end_idx + 1]

        if reset_state:
            for acc in accounts:
                self.state_mgr.reset(acc.username)
            print(f"{C.GREEN}→ Đã reset trạng thái setup cho {len(accounts)} tài khoản.{C.RESET}")
            return False

        print(f"{C.CYAN}=== SETUP {len(accounts)} TÀI KHOẢN ({start_idx}-{end_idx}) ĐỒNG THỜI (TỐI ĐA 5 ACC) ==={C.RESET}")
        if force:
            print(f"{C.RED}!!! CHẾ ĐỘ FORCE (Chạy lại các bước đã hoàn thành) !!!{C.RESET}")
        if start_step > 1:
            print(f"{C.YELLOW}!!! BẮT ĐẦU TỪ STEP {start_step} !!!{C.RESET}")
        print(f"{C.DIM}Tạo NV → Chọn NV → Về nhà → NPC → Nhận thưởng → Đậu → Bùa → Santa → Item hỗ trợ → Kích hoạt → Ép 16 → Ép 1/22/28/12{C.RESET}")
        print()

        sem = asyncio.Semaphore(5)

        async def setup_with_sem(acc, idx):
            async with sem:
                return await self._setup_one(acc, idx, end_idx, force=force, start_step=start_step)

        tasks = [setup_with_sem(acc, start_idx + i) for i, acc in enumerate(accounts)]
        results = await asyncio.gather(*tasks)

        success = sum(1 for r in results if r)
        fail = len(results) - success

        print()
        print(f"{C.CYAN}=== HOÀN TẤT ==={C.RESET}")
        print(f"  {C.GREEN}OK: {success}{C.RESET}  |  {C.RED}Fail: {fail}{C.RESET}")
        if accounts:
            self.manager.command_target = start_idx
            print(f"  Target: {C.YELLOW}{start_idx} ({accounts[0].username}){C.RESET}")
        self.state_mgr.save()
        return False

    # ── Main Orchestrator ──────────────────────

    async def _setup_one(self, acc, idx, end_idx, force=False, start_step=1) -> bool:
        C = self.C
        username = acc.username
        self._log(acc, f"{C.CYAN}=== Bắt đầu Setup (Acc {idx}/{end_idx}) từ step {start_step} ==={C.RESET}")

        if force:
            self.state_mgr.reset(username)

        # Đánh dấu các step trước start_step là done (nếu chưa done)
        for step in ALL_STEPS:
            if step < start_step and not self.state_mgr.is_step_done(username, step):
                self.state_mgr.mark_step(username, step, completed=True)

        for step in ALL_STEPS:
            if not await self._ensure_logged_in(acc, C):
                self._log(acc, f"{C.RED}→ Mất kết nối, dừng setup.{C.RESET}")
                return False

            if not force and self.state_mgr.is_step_done(username, step):
                self._step_log(acc, step, f"{C.GREEN}✓ Đã hoàn thành trước đó.{C.RESET}")
                continue

            # Skip step 1 nếu state nói đã có NV
            if step == STEP_CREATE_CHAR and self.state_mgr.get(username).has_character:
                if not force:
                    self._step_log(acc, step, f"{C.GREEN}→ Đã có nhân vật (state).{C.RESET}")
                    self.state_mgr.mark_step(username, step, completed=True)
                    continue

            label = STEP_LABELS.get(step, f"Step {step}")
            retry_cfg = RETRY_CONFIGS.get(step, RetryConfig())
            sig = f"[{step}/12] {label}"

            self._log(acc, f"{C.CYAN}{sig}...{C.RESET}")

            timeout = STEP_TIMEOUTS.get(step, DEFAULT_STEP_TIMEOUT)

            ok = await retry_operation(
                acc, self._log, label,
                lambda s=step: self._run_step(acc, s, force),
                retry_cfg,
                timeout=timeout
            )

            if ok:
                self.state_mgr.mark_step(username, step, completed=True)
                self._step_log(acc, step, f"{C.GREEN}✓ Thành công.{C.RESET}")
            else:
                self.state_mgr.mark_step(username, step, completed=False, error="Failed after retries")
                self._step_log(acc, step, f"{C.YELLOW}✗ Thất bại, chuyển step tiếp.{C.RESET}")
                # Không return False — tiếp tục step tiếp theo

        # Tóm tắt cuối
        if await self._ensure_logged_in(acc, C):
            bean_final = count_beans(acc)
            bua_count = count_bua_items(acc)
            gold = getattr(acc.char, 'xu', 0)
            item441 = count_item(acc, ITEM_441)
            item16 = count_item(acc, ITEM_UPGRADE_16)
            item12 = count_item(acc, ITEM_12)
            self._log(acc, f"{C.GREEN}✓ Setup xong tài khoản này.{C.RESET}")
            self._log(acc, f"{C.DIM}  Vàng: {gold} | Đậu: {bean_final} | Bùa: {bua_count}/{len(BUA_ITEM_IDS)} | Item 441: {item441} | Item 16: {item16} | Item 12: {item12}{C.RESET}")
        return True

    async def _run_step(self, acc, step: int, force: bool) -> bool:
        """Dispatch tới step handler tương ứng."""
        C = self.C
        log = lambda msg: self._log(acc, msg)

        if step == STEP_CREATE_CHAR:
            return await create_character(acc, log)
        elif step == STEP_SELECT_CHAR:
            return await select_character(acc, log)
        elif step == STEP_GO_HOME:
            from commands.setup.navigation_helpers import go_home
            return await go_home(acc, log)
        elif step == STEP_OPEN_MURI:
            return await open_muri(acc, log)
        elif step == STEP_CLAIM_REWARDS:
            return await claim_rewards(acc, self.state_mgr, log, force)
        elif step == STEP_FARM_BEANS:
            return await farm_magic_tree(acc, log, target_count=TARGET_BEAN_QTY)
        elif step == STEP_BUY_BUA:
            return await buy_bua(acc, log)
        elif step == STEP_SANTA_SHOP:
            return await santa_shop(acc, log)
        elif step == STEP_USE_SUPPORT:
            return await use_support_items(acc, log)
        elif step == STEP_ACTIVATE_ITEMS:
            return await activate_items(acc, log)
        elif step == STEP_UPGRADE_16:
            return await upgrade_item_16(acc, log, C)
        elif step == STEP_UPGRADE_OTHER:
            return await upgrade_other_items(acc, log, C)
        return False

    # ── Ensure Logged In ──────────────────────

    async def _ensure_logged_in(self, acc, C) -> bool:
        if acc.is_logged_in:
            return True
        self._log(acc, f"{C.YELLOW}→ Mất kết nối, đang đăng nhập lại...{C.RESET}")
        for attempt in range(3):
            try:
                if await acc.login():
                    if await self._wait_game_ready(acc, C):
                        self._log(acc, f"{C.GREEN}→ Đăng nhập lại thành công.{C.RESET}")
                        return True
            except Exception as e:
                self._log(acc, f"{C.RED}  Thử lại {attempt+1} lỗi: {e}{C.RESET}")
            await asyncio.sleep(3)
        return False

    async def _wait_game_ready(self, acc, C, timeout=30) -> bool:
        for sec in range(timeout):
            if not acc.is_logged_in:
                return False
            await asyncio.sleep(1)
            if acc.controller.tile_map.map_id > 0 and acc.char.c_power > 0:
                return True
            if sec == 8:
                try:
                    await acc.service.request_me_info()
                except Exception:
                    pass
            if sec == 15:
                try:
                    await acc.service.request_change_map()
                except Exception:
                    pass
        self._log(acc, f"{C.YELLOW}→ Timeout map={acc.controller.tile_map.map_id} power={acc.char.c_power}{C.RESET}")
        return acc.controller.tile_map.map_id > 0
