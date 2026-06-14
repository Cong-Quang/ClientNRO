"""
Setup Accounts Command - Tự động setup tài khoản mới hoàn chỉnh
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
"""
import asyncio
import json
import os
import re
from dataclasses import dataclass, field, asdict
from typing import Any, Callable, Awaitable
from commands.base_command import Command
from logs.logger_config import TerminalColors
from config import Config

# ──────────────────────────────────────────────
# CONSTANTS
# ──────────────────────────────────────────────

# Step IDs
STEP_CREATE_CHAR    = 1
STEP_SELECT_CHAR    = 2
STEP_GO_HOME        = 3
STEP_OPEN_MURI      = 4
STEP_CLAIM_REWARDS  = 5
STEP_FARM_BEANS     = 6
STEP_BUY_BUA        = 7
STEP_SANTA_SHOP     = 8
STEP_USE_SUPPORT    = 9
STEP_ACTIVATE_ITEMS = 10
STEP_UPGRADE_16    = 11
STEP_UPGRADE_OTHER = 12

# Each equipment piece in STEP 12 needs 10 upgrades (like an "áo")
UPGRADE_TIMES_PER_PIECE = 10
ALL_STEPS = [STEP_CREATE_CHAR, STEP_SELECT_CHAR, STEP_GO_HOME, STEP_OPEN_MURI,
             STEP_CLAIM_REWARDS, STEP_FARM_BEANS, STEP_BUY_BUA, STEP_SANTA_SHOP,
             STEP_USE_SUPPORT, STEP_ACTIVATE_ITEMS,
             STEP_UPGRADE_16, STEP_UPGRADE_OTHER]
STEP_LABELS = {
    STEP_CREATE_CHAR: "Tạo nhân vật",
    STEP_SELECT_CHAR: "Chọn nhân vật",
    STEP_GO_HOME: "Về nhà",
    STEP_OPEN_MURI: "Mở NPC Muri",
    STEP_CLAIM_REWARDS: "Nhận thưởng (vàng/ngọc/giftcode/đệ tử)",
    STEP_FARM_BEANS: "Farm đậu thần",
    STEP_BUY_BUA: "Mua bùa",
    STEP_SANTA_SHOP: "Santa shop",
    STEP_USE_SUPPORT: "Dùng item hỗ trợ",
    STEP_ACTIVATE_ITEMS: "Kích hoạt vật phẩm thưởng",
    STEP_UPGRADE_16: "Ép sao Item 16 (x11)",
    STEP_UPGRADE_OTHER: "Ép sao Item 1/22/28/12",
}

# Gender constants
GENDER_TRAI_DAT = 0
GENDER_NAMEK    = 1
GENDER_XAYDA    = 2

# Home maps per gender
HOME_MAPS       = {GENDER_TRAI_DAT: 21, GENDER_NAMEK: 22, GENDER_XAYDA: 23}
# Home NPCs per gender
HOME_NPC        = {GENDER_TRAI_DAT: 0, GENDER_NAMEK: 2, GENDER_XAYDA: 1}
# Santa maps per gender
SANTA_MAPS      = {GENDER_TRAI_DAT: 5, GENDER_NAMEK: 13, GENDER_XAYDA: 20}
# Default hair per gender
HAIR_BY_GENDER  = {GENDER_TRAI_DAT: 64, GENDER_NAMEK: 9, GENDER_XAYDA: 6}

NPC_SANTA       = 39
NPC_DAU_THAN    = 4
NPC_BA_HAT_MIT  = 21
MAP_VACH_NUI    = 43

# Bean item IDs (đậu thần)
BEAN_ITEM_IDS   = [13, 60, 61, 62, 63, 64, 65, 352, 523, 595]
TARGET_BEAN_QTY = 1000

# Giftcodes
GIFTCODES = ["tdstudio"]

# BUA items (bùa 1 tháng)
BUA_ITEM_IDS = [213, 214, 215, 216, 217, 218, 219, 522, 671, 672]

# Santa shop items
SANTA_ITEM_HO_TRO   = [(517, 100), (518, 50)]
SANTA_ITEM_DAC_BIET = [(402, 6), (403, 6)]
# Items that don't go into bag (bay, pet, sách...)
SANTA_NO_BAG_ITEMS  = {517, 518, 402, 403}

# Support items
ITEM_1182 = 1182  # Dùng để nhận item 441
ITEM_441  = 441   # Mục tiêu: >= 20
ITEM_1680 = 1680  # Dùng 1 lần

# Reward activation items (dùng 1 lần mỗi item)
ACTIVATE_ITEMS_ONCE = [290, 1269, 1357, 1649, 1983, 1499, 1323]
# Item 2000 dùng 2 lần, chọn Set Liên Hoàn
ITEM_2000 = 2000
ITEM_2000_USE_TIMES = 2

# ── Upgrade / Ép sao constants ────────────────

# Map Đảo Kame (nơi Bà Hạt Mít có chức năng ép sao)
MAP_DAO_KAME = 5

# Upgrade: Item 16 → ép 11 lần
ITEM_UPGRADE_16    = 16
ITEM_UPGRADE_16_CRYSTAL = 1   # Item ID 1 là nguyên liệu (DaPhaLe)
ITEM_UPGRADE_16_TIMES = 11

# STEP 12 items (mỗi item ép 2 lần, trừ ID 12 có cách đặc biệt)
# Mỗi món ép cần: chính nó x1 + chính nó x1 (tổng 2)
UPGRADE_OTHER_ITEMS = [1, 22, 28, 12]  # Item IDs cần ép 10 lần mỗi item (1, 22, 28, và rada 12)
# ID 12 đặc biệt:
#   First:  ID 12 + ID 16 (đã ép sao từ STEP 11)
#   Second: ID 12 + 2x ID 442 + 8x ID 441
ITEM_12 = 12
ITEM_442 = 442

# Combine tab constants (server-side)
EP_SAO_TRANG_BI = 500

# ──────────────────────────────────────────────
# STATE MANAGEMENT
# ──────────────────────────────────────────────

STATE_FILE = "setup_state.json"


@dataclass
class StepState:
    completed: bool = False
    skipped: bool = False
    retry_count: int = 0
    error: str = ""


@dataclass
class AccountSetupState:
    username: str = ""
    steps: dict = field(default_factory=dict)
    has_character: bool = False
    has_pet: bool = False
    gold_claimed: bool = False
    gem_claimed: bool = False
    giftcode_done: bool = False
    disciple_claimed: bool = False


class SetupStateManager:
    """Quản lý trạng thái setup cho từng account, lưu vào file JSON để resume."""

    def __init__(self):
        self._states: dict[str, AccountSetupState] = {}

    def load(self):
        if not os.path.exists(STATE_FILE):
            return
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                raw = json.load(f)
            for username, data in raw.items():
                state = AccountSetupState(**data)
                # Ensure all step keys exist
                for s in ALL_STEPS:
                    if str(s) not in state.steps:
                        state.steps[str(s)] = StepState().__dict__
                self._states[username] = state
        except (json.JSONDecodeError, IOError, TypeError):
            pass

    def save(self):
        try:
            raw = {u: asdict(s) for u, s in self._states.items()}
            with open(STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(raw, f, indent=2, ensure_ascii=False)
        except IOError:
            pass

    def get(self, username: str) -> AccountSetupState:
        if username not in self._states:
            state = AccountSetupState(username=username)
            state.steps = {str(s): StepState().__dict__ for s in ALL_STEPS}
            self._states[username] = state
        return self._states[username]

    def mark_step(self, username: str, step: int, completed: bool = True,
                  skipped: bool = False, error: str = ""):
        state = self.get(username)
        s = state.steps.get(str(step), StepState().__dict__)
        s["completed"] = completed
        s["skipped"] = skipped
        s["error"] = error
        state.steps[str(step)] = s
        self.save()

    def is_step_completed(self, username: str, step: int) -> bool:
        state = self.get(username)
        s = state.steps.get(str(step), {})
        return s.get("completed", False)

    def is_step_skipped(self, username: str, step: int) -> bool:
        state = self.get(username)
        s = state.steps.get(str(step), {})
        return s.get("skipped", False)

    def is_step_done(self, username: str, step: int) -> bool:
        """Step đã hoàn thành hoặc đã skip."""
        return self.is_step_completed(username, step) or self.is_step_skipped(username, step)

    def reset(self, username: str):
        if username in self._states:
            del self._states[username]
            self.save()

    def reset_all(self):
        self._states.clear()
        self.save()

    def set_attribute(self, username: str, **kwargs):
        state = self.get(username)
        for k, v in kwargs.items():
            if hasattr(state, k):
                setattr(state, k, v)
        self.save()


# ──────────────────────────────────────────────
# RETRY / TIMEOUT MANAGER
# ──────────────────────────────────────────────

class RetryConfig:
    """Cấu hình retry cho mỗi bước."""
    def __init__(self, max_attempts: int = 3, base_delay: float = 1.0,
                 max_delay: float = 5.0, backoff: float = 2.0):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff = backoff


RETRY_CONFIGS = {
    STEP_CREATE_CHAR:    RetryConfig(2, 1.0, 3.0, 1.0),
    STEP_SELECT_CHAR:    RetryConfig(3, 1.0, 5.0, 1.5),
    STEP_GO_HOME:        RetryConfig(3, 1.0, 5.0, 1.5),
    STEP_OPEN_MURI:      RetryConfig(3, 0.5, 3.0, 1.5),
    STEP_CLAIM_REWARDS:  RetryConfig(3, 0.5, 3.0, 1.5),
    STEP_FARM_BEANS:     RetryConfig(5, 1.0, 5.0, 1.5),
    STEP_BUY_BUA:        RetryConfig(3, 1.0, 5.0, 1.5),
    STEP_SANTA_SHOP:     RetryConfig(3, 1.0, 5.0, 1.5),
    STEP_USE_SUPPORT:    RetryConfig(2, 0.5, 3.0, 1.0),
    STEP_ACTIVATE_ITEMS:  RetryConfig(2, 0.5, 3.0, 1.0),
    STEP_UPGRADE_16:     RetryConfig(5, 1.0, 5.0, 1.5),
    STEP_UPGRADE_OTHER:  RetryConfig(5, 1.0, 5.0, 1.5),
}


async def run_with_timeout(coro: Awaitable, timeout: float = 10.0,
                           default_return=None):
    """Chạy coroutine với timeout, trả về default nếu timeout."""
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        return default_return


async def retry_operation(acc, log_func, label: str, coro_factory: Callable,
                          config: RetryConfig, timeout: float = 15.0) -> bool:
    """Retry wrapper: thực thi coroutine với retry + timeout + backoff."""
    for attempt in range(1, config.max_attempts + 1):
        if not acc.is_logged_in:
            log_func(f"{TerminalColors.RED}→ Mất kết nối khi {label}.{TerminalColors.RESET}")
            return False
        try:
            result = await asyncio.wait_for(coro_factory(), timeout=timeout)
            if result:
                return True
        except asyncio.TimeoutError:
            log_func(f"{TerminalColors.YELLOW}→ {label}: timeout lần {attempt}/{config.max_attempts}.{TerminalColors.RESET}")
        except Exception as e:
            log_func(f"{TerminalColors.YELLOW}→ {label}: lỗi lần {attempt}/{config.max_attempts}: {e}.{TerminalColors.RESET}")
        if attempt < config.max_attempts:
            delay = min(config.base_delay * (config.backoff ** (attempt - 1)), config.max_delay)
            await asyncio.sleep(delay)
    return False


# ──────────────────────────────────────────────
# MAIN COMMAND
# ──────────────────────────────────────────────

class SetupAccountsCommand(Command):
    """State-machine based setup command."""

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
            print(f"{C.YELLOW}Cú pháp: setup_accounts <start_index> <end_index> [force|reset]{C.RESET}")
            print(f"  Ví dụ: {C.CYAN}setup_accounts 0 9{C.RESET}")
            print(f"        {C.CYAN}setup_accounts 0 9 force{C.RESET}")
            print(f"        {C.CYAN}setup_accounts 0 9 reset{C.RESET}  (reset trạng thái)")
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
        if len(parts) >= 4:
            cmd = parts[3].lower()
            force = cmd in ('force', 'again', 'true', '1')
            reset_state = cmd in ('reset',)

        accounts = self.manager.accounts[start_idx:end_idx + 1]

        if reset_state:
            for acc in accounts:
                self.state_mgr.reset(acc.username)
            print(f"{C.GREEN}→ Đã reset trạng thái setup cho {len(accounts)} tài khoản.{C.RESET}")
            return False

        print(f"{C.CYAN}=== SETUP {len(accounts)} TÀI KHOẢN ({start_idx}-{end_idx}) ĐỒNG THỜI (TỐI ĐA 5 ACC) ==={C.RESET}")
        if force:
            print(f"{C.RED}!!! CHẾ ĐỘ FORCE (Chạy lại các bước đã hoàn thành) !!!{C.RESET}")
        print(f"{C.DIM}Tạo NV → Chọn NV → Về nhà → NPC → Nhận thưởng → Đậu → Bùa → Santa → Item hỗ trợ → Kích hoạt → Ép 16 → Ép 1/22/28/12{C.RESET}")
        print()

        sem = asyncio.Semaphore(5)

        async def setup_with_sem(acc, idx):
            async with sem:
                return await self._setup_one(acc, idx, end_idx, force=force)

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

    async def _setup_one(self, acc, idx, end_idx, force=False) -> bool:
        C = self.C
        username = acc.username
        self._log(acc, f"{C.CYAN}=== Bắt đầu Setup (Acc {idx}/{end_idx}) ==={C.RESET}")

        if force:
            self.state_mgr.reset(username)

        for step in ALL_STEPS:
            if not await self._ensure_logged_in(acc, C):
                self._log(acc, f"{C.RED}→ Mất kết nối, dừng setup.{C.RESET}")
                return False

            if not force and self.state_mgr.is_step_done(username, step):
                self._step_log(acc, step, f"{C.GREEN}✓ Đã hoàn thành trước đó.{C.RESET}")
                continue

            label = STEP_LABELS.get(step, f"Step {step}")
            retry_cfg = RETRY_CONFIGS.get(step, RetryConfig())
            sig = f"[{step}/12] {label}"

            self._log(acc, f"{C.CYAN}{sig}...{C.RESET}")

            ok = await retry_operation(
                acc, self._log, label,
                lambda s=step: self._run_step(acc, s, force),
                retry_cfg,
                timeout=90.0 if step in (STEP_FARM_BEANS, STEP_GO_HOME, STEP_UPGRADE_16, STEP_UPGRADE_OTHER) else 30.0
            )

            if ok:
                self.state_mgr.mark_step(username, step, completed=True)
                self._step_log(acc, step, f"{C.GREEN}✓ Thành công.{C.RESET}")
            else:
                self.state_mgr.mark_step(username, step, completed=False, error="Failed after retries")
                self._step_log(acc, step, f"{C.RED}✗ Thất bại sau retry.{C.RESET}")
                return False

        # Final summary
        if await self._ensure_logged_in(acc, C):
            bean_final = self._count_beans(acc)
            bua_count = self._count_bua_items(acc)
            gold = getattr(acc.char, 'xu', 0)
            item441 = self._count_item(acc, ITEM_441)
            item16 = self._count_item(acc, ITEM_UPGRADE_16)
            item12 = self._count_item(acc, ITEM_12)
            self._log(acc, f"{C.GREEN}✓ Setup xong tài khoản này.{C.RESET}")
            self._log(acc, f"{C.DIM}  Vàng: {gold} | Đậu: {bean_final} | Bùa: {bua_count}/{len(BUA_ITEM_IDS)} | Item 441: {item441} | Item 16: {item16} | Item 12: {item12}{C.RESET}")
        return True

    async def _run_step(self, acc, step: int, force: bool) -> bool:
        """Dispatch to step handler."""
        C = self.C
        if step == STEP_CREATE_CHAR:
            return await self._step_create_character(acc, C)
        elif step == STEP_SELECT_CHAR:
            return await self._step_select_character(acc, C)
        elif step == STEP_GO_HOME:
            return await self._go_home(acc, C)
        elif step == STEP_OPEN_MURI:
            return await self._step_open_muri(acc, C)
        elif step == STEP_CLAIM_REWARDS:
            return await self._step_claim_rewards(acc, C, force)
        elif step == STEP_FARM_BEANS:
            return await self._farm_magic_tree(acc, C, target_count=TARGET_BEAN_QTY)
        elif step == STEP_BUY_BUA:
            return await self._buy_bua(acc, C)
        elif step == STEP_SANTA_SHOP:
            return await self._santa_shop(acc, C)
        elif step == STEP_USE_SUPPORT:
            return await self._step_use_support_items(acc, C)
        elif step == STEP_ACTIVATE_ITEMS:
            return await self._step_activate_items(acc, C)
        elif step == STEP_UPGRADE_16:
            return await self._step_upgrade_item_16(acc, C)
        elif step == STEP_UPGRADE_OTHER:
            return await self._step_upgrade_other_items(acc, C)
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

    # ── Wait Game Ready ────────────────────────

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

    # ══════════════════════════════════════════
    # STEP 1: CREATE CHARACTER
    # ══════════════════════════════════════════

    async def _step_create_character(self, acc, C) -> bool:
        """Tạo nhân vật mới nếu chưa có.
        Suppress auto-creation trong misc_handler để tránh race condition.
        """
        if acc.char.c_power > 0:
            self._log(acc, f"{C.GREEN}→ Đã có nhân vật (SM={acc.char.c_power}).{C.RESET}")
            return True

        # Suppress auto character creation trong misc_handler
        acc._suppress_auto_create = True

        try:
            # Generate character name: hentz + last 2-3 digits of username
            match = re.search(r'(\d+)$', acc.username)
            if match:
                raw_suffix = match.group(1)  # keep original digits, no padding
            else:
                raw_suffix = "001"
            char_name = f"hentz{raw_suffix}"

            gender = getattr(Config, 'DEFAULT_CHAR_GENDER', GENDER_NAMEK)
            hair = HAIR_BY_GENDER.get(gender, 9)

            self._log(acc, f"{C.DIM}→ Tạo nhân vật: name='{char_name}', gender={gender}, hair={hair}{C.RESET}")

            await acc.service.create_character(char_name, gender, hair)
            await asyncio.sleep(2.0)

            # Đợi server xác nhận (login_event được set khi ME_LOAD_ALL nhận được)
            try:
                await asyncio.wait_for(acc.login_event.wait(), timeout=10.0)
            except asyncio.TimeoutError:
                self._log(acc, f"{C.YELLOW}→ Timeout chờ tạo nhân vật.{C.RESET}")
            await asyncio.sleep(1.0)

            if acc.char.c_power > 0:
                self._log(acc, f"{C.GREEN}→ Tạo nhân vật '{char_name}' thành công.{C.RESET}")
                return True

            self._log(acc, f"{C.YELLOW}→ Chưa có nhân vật sau khi tạo. Có thể đã tồn tại hoặc tên không hợp lệ.{C.RESET}")
            # Thử gửi lại request create
            await acc.service.create_character(char_name, gender, hair)
            await asyncio.sleep(2.0)

            try:
                await asyncio.wait_for(acc.login_event.wait(), timeout=10.0)
            except asyncio.TimeoutError:
                pass
            await asyncio.sleep(1.0)

            if acc.char.c_power > 0:
                self._log(acc, f"{C.GREEN}→ Tạo nhân vật thành công (lần 2).{C.RESET}")
                return True

            self._log(acc, f"{C.RED}→ Không thể tạo nhân vật sau 2 lần thử.{C.RESET}")
            return False
        finally:
            # Luôn bỏ suppress sau khi hoàn tất (thành công hay thất bại)
            acc._suppress_auto_create = False

    # ══════════════════════════════════════════
    # STEP 2: SELECT CHARACTER (vào game)
    # ══════════════════════════════════════════

    async def _step_select_character(self, acc, C) -> bool:
        """Chọn nhân vật mặc định và vào game."""
        if acc.is_logged_in and acc.char.c_power > 0 and acc.controller.tile_map.map_id > 0:
            self._log(acc, f"{C.GREEN}→ Đã ở trong game (map {acc.controller.tile_map.map_id}).{C.RESET}")
            return True

        self._log(acc, f"{C.DIM}→ Đợi vào game...{C.RESET}")

        # Đợi game ready (login_event + map loaded)
        for attempt in range(30):
            if not acc.is_logged_in:
                await asyncio.sleep(1)
                continue
            if acc.controller.tile_map.map_id > 0 and acc.char.c_power > 0:
                self._log(acc, f"{C.GREEN}→ Vào game OK (map={acc.controller.tile_map.map_id}, SM={acc.char.c_power}).{C.RESET}")
                return True
            if attempt == 5:
                try:
                    await acc.service.request_me_info()
                except Exception:
                    pass
            if attempt == 10:
                try:
                    await acc.service.request_change_map()
                except Exception:
                    pass
            await asyncio.sleep(1)

        self._log(acc, f"{C.RED}→ Không vào được game sau 30s.{C.RESET}")
        return False

    # ══════════════════════════════════════════
    # STEP 3: GO HOME (handled by dispatch)
    # ══════════════════════════════════════════

    # (Uses _go_home below)

    # ══════════════════════════════════════════
    # STEP 4: OPEN NPC MURI
    # ══════════════════════════════════════════

    async def _step_open_muri(self, acc, C) -> bool:
        """Teleport tới NPC Ông Muri và mở menu."""
        npc_id = HOME_NPC.get(acc.char.gender, 2)

        if not await self._teleport_to_npc(acc, npc_id):
            self._log(acc, f"{C.YELLOW}→ Không tìm thấy NPC (template={npc_id}).{C.RESET}")
            # Thử về nhà trước
            await self._go_home(acc, C)
            await asyncio.sleep(1)
            if not await self._teleport_to_npc(acc, npc_id):
                self._log(acc, f"{C.RED}→ Vẫn không tìm thấy NPC.{C.RESET}")
                return False

        # Mở menu
        ctrl = acc.controller
        ctrl.ui_menu_event.clear()
        await acc.service.open_menu_npc(npc_id)
        try:
            await asyncio.wait_for(ctrl.ui_menu_event.wait(), timeout=3.0)
        except asyncio.TimeoutError:
            pass
        await asyncio.sleep(0.2)

        opts = ctrl.last_ui_options or []
        self._log(acc, f"{C.DIM}→ Menu NPC: {opts}{C.RESET}")
        if not opts:
            self._log(acc, f"{C.YELLOW}→ Menu rỗng, thử mở lại...{C.RESET}")
            return False

        return True

    # ══════════════════════════════════════════
    # STEP 5: CLAIM REWARDS
    # ══════════════════════════════════════════

    async def _step_claim_rewards(self, acc, C, force: bool) -> bool:
        """Nhận vàng miễn phí → ngọc miễn phí → giftcode → đệ tử miễn phí."""
        npc_id = HOME_NPC.get(acc.char.gender, 2)

        # Đảm bảo đang đứng gần NPC
        if not await self._teleport_to_npc(acc, npc_id):
            self._log(acc, f"{C.YELLOW}→ Không tìm thấy NPC để nhận thưởng.{C.RESET}")
            return False

        # ── 5a. Nhận vàng miễn phí ──
        if force or not self.state_mgr.get(acc.username).gold_claimed:
            self._log(acc, f"{C.DIM}→ Nhận vàng miễn phí...{C.RESET}")
            await self._claim_gold(acc, C)
            self.state_mgr.set_attribute(acc.username, gold_claimed=True)
        else:
            self._log(acc, f"{C.GREEN}→ Đã nhận vàng trước đó.{C.RESET}")

        if not await self._ensure_logged_in(acc, C):
            return False

        # ── 5b. Nhận ngọc miễn phí ──
        if force or not self.state_mgr.get(acc.username).gem_claimed:
            self._log(acc, f"{C.DIM}→ Nhận ngọc miễn phí...{C.RESET}")
            await self._claim_gem(acc, npc_id, C)
            self.state_mgr.set_attribute(acc.username, gem_claimed=True)
        else:
            self._log(acc, f"{C.GREEN}→ Đã nhận ngọc trước đó.{C.RESET}")

        if not await self._ensure_logged_in(acc, C):
            return False

        # ── 5c. Giftcode ──
        if force or not self.state_mgr.get(acc.username).giftcode_done:
            has_gift = self._has_giftcode_items(acc)
            if has_gift and not force:
                self._log(acc, f"{C.GREEN}→ Đã có item giftcode, bỏ qua.{C.RESET}")
            else:
                for code in GIFTCODES:
                    if not await self._ensure_logged_in(acc, C):
                        return False
                    await self._npc_giftcode(acc, npc_id, code, C)
            self.state_mgr.set_attribute(acc.username, giftcode_done=True)
        else:
            self._log(acc, f"{C.GREEN}→ Đã nhập giftcode trước đó.{C.RESET}")

        if not await self._ensure_logged_in(acc, C):
            return False

        # ── 5d. Nhận đệ tử miễn phí ──
        if force or not self.state_mgr.get(acc.username).disciple_claimed:
            self._log(acc, f"{C.DIM}→ Nhận đệ tử miễn phí...{C.RESET}")
            await self._claim_disciple(acc, npc_id, C)
            self.state_mgr.set_attribute(acc.username, disciple_claimed=True)
        else:
            self._log(acc, f"{C.GREEN}→ Đã nhận đệ tử trước đó.{C.RESET}")

        return True

    async def _claim_gold(self, acc, C):
        """Nhận vàng từ NPC nhà."""
        ctrl = acc.controller
        home_npc = HOME_NPC.get(acc.char.gender, 2)

        # Retry tối đa 3 lần
        for attempt in range(1, 4):
            if not acc.is_logged_in:
                return

            if attempt > 1:
                self._log(acc, f"{C.YELLOW}→ Retry nhận vàng lần {attempt}/3...{C.RESET}")
                await asyncio.sleep(1)

            gold_before = getattr(acc.char, 'xu', 0)

            if not await self._teleport_to_npc(acc, home_npc, y_offset=-1):
                self._log(acc, f"{C.YELLOW}→ Không tìm thấy NPC nhà.{C.RESET}")
                continue

            await asyncio.sleep(0.3)

            ctrl.ui_menu_event.clear()
            await acc.service.open_menu_npc(home_npc)
            try:
                await asyncio.wait_for(ctrl.ui_menu_event.wait(), timeout=3.0)
            except asyncio.TimeoutError:
                pass
            await asyncio.sleep(0.3)

            opts = ctrl.last_ui_options or []
            gold_opt_idx = -1

            for i, opt in enumerate(opts):
                opt_clean = opt.lower().replace("\n", " ").strip()
                if "vàng" in opt_clean:
                    gold_opt_idx = i
                    break

            if gold_opt_idx != -1:
                self._log(acc, f"{C.DIM}→ Chọn nhận vàng ở vị trí {gold_opt_idx}.{C.RESET}")
                await acc.service.confirm_menu_npc(home_npc, gold_opt_idx)
                await asyncio.sleep(1.0)

                try:
                    await acc.service.request_me_info()
                    await asyncio.sleep(0.5)
                except Exception:
                    pass

                gold_after = getattr(acc.char, 'xu', 0)
                if gold_after > gold_before:
                    self._log(acc, f"{C.GREEN}→ Nhận vàng: +{gold_after - gold_before} (tổng: {gold_after}).{C.RESET}")
                    return
                elif gold_after > 0:
                    self._log(acc, f"{C.GREEN}→ Vàng hiện tại: {gold_after}.{C.RESET}")
                    return
            else:
                self._log(acc, f"{C.YELLOW}→ Không tìm thấy tùy chọn vàng (options: {opts}).{C.RESET}")
                break

        self._log(acc, f"{C.YELLOW}→ Không nhận được vàng (có thể đã nhận trước).{C.RESET}")

    async def _claim_gem(self, acc, npc_id, C):
        """Nhận ngọc xanh miễn phí từ NPC nhà."""
        ctrl = acc.controller

        if not await self._teleport_to_npc(acc, npc_id):
            self._log(acc, f"{C.YELLOW}→ Không tìm thấy NPC.{C.RESET}")
            return

        ctrl.ui_menu_event.clear()
        await acc.service.open_menu_npc(npc_id)
        try:
            await asyncio.wait_for(ctrl.ui_menu_event.wait(), timeout=3.0)
        except asyncio.TimeoutError:
            pass
        await asyncio.sleep(0.3)

        opts = ctrl.last_ui_options or []
        gem_opt_idx = -1
        for i, opt in enumerate(opts):
            opt_lower = opt.lower()
            if "ngọc" in opt_lower or "xanh" in opt_lower:
                gem_opt_idx = i
                break

        if gem_opt_idx != -1:
            self._log(acc, f"{C.DIM}→ Chọn nhận ngọc xanh ở vị trí {gem_opt_idx}.{C.RESET}")
            await acc.service.confirm_menu_npc(npc_id, gem_opt_idx)
            await asyncio.sleep(0.5)
            self._log(acc, f"{C.GREEN}→ Đã nhận ngọc xanh.{C.RESET}")
        else:
            self._log(acc, f"{C.YELLOW}→ Không tìm thấy tùy chọn ngọc, dùng option 2.{C.RESET}")
            await acc.service.confirm_menu_npc(npc_id, 2)
            await asyncio.sleep(0.5)

    async def _claim_disciple(self, acc, npc_id, C):
        """Nhận đệ tử miễn phí từ NPC nhà."""
        ctrl = acc.controller

        # Kiểm tra đã có đệ tử chưa
        if acc.char.have_pet or acc.pet.have_pet:
            self._log(acc, f"{C.GREEN}→ Đã có đệ tử.{C.RESET}")
            return

        if not await self._teleport_to_npc(acc, npc_id):
            self._log(acc, f"{C.YELLOW}→ Không tìm thấy NPC.{C.RESET}")
            return

        # Mở menu → tìm "Nhận Đệ Tử Miễn Phí"
        ctrl.ui_menu_event.clear()
        await acc.service.open_menu_npc(npc_id)
        try:
            await asyncio.wait_for(ctrl.ui_menu_event.wait(), timeout=3.0)
        except asyncio.TimeoutError:
            pass
        await asyncio.sleep(0.3)

        opts = ctrl.last_ui_options or []
        disciple_opt = -1
        for i, opt in enumerate(opts):
            if "đệ tử" in opt.lower() or "pet" in opt.lower() or "de tu" in opt.lower():
                disciple_opt = i
                break

        if disciple_opt == -1:
            self._log(acc, f"{C.YELLOW}→ Không tìm thấy tùy chọn đệ tử (options: {opts}).{C.RESET}")
            return

        # Chọn lần 1 → có thể server gửi menu xác nhận
        ctrl.ui_menu_event.clear()
        await acc.service.confirm_menu_npc(npc_id, disciple_opt)
        try:
            await asyncio.wait_for(ctrl.ui_menu_event.wait(), timeout=3.0)
        except asyncio.TimeoutError:
            pass
        await asyncio.sleep(0.5)

        # Nếu có menu con "Nhận Đệ Tử Miễn Phí" thì chọn tiếp
        opts2 = ctrl.last_ui_options or []
        if opts2 and opts2 != opts:
            confirm_opt = -1
            for i, opt in enumerate(opts2):
                if "đệ tử" in opt.lower() or "nhận" in opt.lower():
                    confirm_opt = i
                    break
            if confirm_opt != -1:
                await acc.service.confirm_menu_npc(npc_id, confirm_opt)
                await asyncio.sleep(0.5)

        # Refresh trạng thái đệ tử
        try:
            await acc.service.pet_info()
            await asyncio.sleep(0.5)
        except Exception:
            pass

        if acc.char.have_pet or acc.pet.have_pet:
            self._log(acc, f"{C.GREEN}→ Nhận đệ tử thành công.{C.RESET}")
        else:
            self._log(acc, f"{C.YELLOW}→ Có thể chưa nhận được đệ tử (server chưa cập nhật).{C.RESET}")

    # ══════════════════════════════════════════
    # GENERIC UTILITY METHODS
    # ══════════════════════════════════════════

    async def _go_home(self, acc, C) -> bool:
        home_map = HOME_MAPS.get(acc.char.gender, 22)
        if acc.controller.tile_map.map_id == home_map:
            self._log(acc, f"{C.GREEN}→ Đã ở nhà (map {home_map}).{C.RESET}")
            return True
        try:
            await acc.controller.xmap.start(home_map)
            for _ in range(45):
                if not acc.is_logged_in:
                    return False
                await asyncio.sleep(1)
                if not acc.controller.xmap.is_xmapping:
                    break
                if acc.controller.tile_map.map_id == home_map:
                    acc.controller.xmap.stop()
                    break
            if acc.controller.tile_map.map_id == home_map:
                self._log(acc, f"{C.GREEN}→ Về nhà OK.{C.RESET}")
                return True
            self._log(acc, f"{C.YELLOW}→ Đang ở map {acc.controller.tile_map.map_id}.{C.RESET}")
            return False
        except Exception as e:
            self._log(acc, f"{C.RED}→ Lỗi xmap: {e}{C.RESET}")
            return False

    async def _teleport_to_npc(self, acc, npc_id, y_offset=-3):
        """Teleport đến gần NPC. Retry nếu thất bại."""
        npc_data = self._find_npc(acc, npc_id)
        if npc_data:
            x, y = npc_data.get('x', 100), npc_data.get('y', 100)
            await acc.controller.movement.teleport_to(x, y + y_offset)
            await asyncio.sleep(0.2)
            return True
        try:
            result = await acc.controller.movement.teleport_to_npc(npc_id, search_by_template=True)
            if result:
                await asyncio.sleep(0.2)
                return True
        except Exception:
            pass
        return False

    def _find_npc(self, acc, npc_id):
        npcs = acc.controller.npcs or {}
        for _, npc_data in npcs.items():
            if npc_data.get('template_id') == npc_id:
                return npc_data
        if npc_id in npcs:
            return npcs[npc_id]
        return None

    # ── Giftcode response helper ──────────────

    async def _wait_giftcode_response(self, acc, ctrl, C, timeout=5.0):
        """Đợi phản hồi server sau khi gửi giftcode, trả về (status, detail).
        Xử lý race condition: nếu nhận được message không liên quan, sẽ chờ message tiếp theo.
        status: 'success' | 'used' | 'expired' | 'invalid' | 'unknown'
        """
        GIFTCODE_KEYWORDS = ["thành công", "chúc mừng", "nhận được", "tặng", "giftcode",
                             "đã sử dụng", "da su dung", "hết hạn", "het han",
                             "không tồn tại", "khong ton tai", "sai mã", "mã quà"]

        deadline = asyncio.get_event_loop().time() + timeout
        while True:
            remaining = deadline - asyncio.get_event_loop().time()
            if remaining <= 0:
                self._log(acc, f"{C.YELLOW}→ Timeout chờ phản hồi giftcode từ server.{C.RESET}")
                return ("unknown", "timeout")

            # Đợi message với timeout theo thời gian còn lại
            try:
                await asyncio.wait_for(ctrl.server_message_event.wait(), timeout=remaining)
            except asyncio.TimeoutError:
                self._log(acc, f"{C.YELLOW}→ Timeout chờ phản hồi giftcode từ server.{C.RESET}")
                return ("unknown", "timeout")

            text = ctrl.last_server_message.lower()
            detail = ctrl.last_server_message

            # Kiểm tra message có chứa từ khóa giftcode không
            if not any(kw in text for kw in GIFTCODE_KEYWORDS):
                # Message không liên quan đến giftcode, chờ message tiếp theo
                ctrl.server_message_event.clear()
                continue

            # Từ khóa thành công
            if "thành công" in text or "chúc mừng" in text:
                return ("success", detail)
            # "nhận được" hoặc "tặng" kèm item/vật phẩm/ngọc/vàng
            if ("nhận được" in text or "tặng" in text) and (
                "item" in text or "vật phẩm" in text or "ngọc" in text or "vàng" in text
            ):
                return ("success", detail)

            # Từ khóa đã sử dụng
            if any(kw in text for kw in ["đã sử dụng", "da su dung", "đã dùng", "da dung"]):
                return ("used", detail)

            # Từ khóa hết hạn
            if any(kw in text for kw in ["hết hạn", "het han", "hết hiệu lực", "qua hạn"]):
                return ("expired", detail)

            # Từ khóa không tồn tại / sai
            if any(kw in text for kw in ["không tồn tại", "khong ton tai", "không đúng",
                                          "sai", "không hợp lệ", "khong hop le"]):
                return ("invalid", detail)

            # Có message nhưng không khớp keyword nào — chờ message tiếp theo
            ctrl.server_message_event.clear()
            continue

    async def _check_giftcode_items(self, acc, C):
        """Kiểm tra item 1680 trong inventory sau khi nhận giftcode."""
        try:
            await acc.service.request_me_info()
            await asyncio.sleep(0.3)
        except Exception:
            pass

        item_1680 = self._count_item(acc, ITEM_1680)
        if item_1680 > 0:
            self._log(acc, f"{C.GREEN}→ Giftcode thành công: có item 1680 ({item_1680}) trong balo.{C.RESET}")
        else:
            self._log(acc, f"{C.YELLOW}→ Giftcode đã nhập nhưng chưa thấy item 1680 trong balo.{C.RESET}")

    # ── Inventory helpers ──────────────────────

    def _count_beans(self, acc):
        count = 0
        for item in acc.char.arr_item_bag or []:
            if item is not None and item.item_id in BEAN_ITEM_IDS:
                count += item.quantity
        return count

    def _count_item(self, acc, item_id):
        count = 0
        for item in acc.char.arr_item_bag or []:
            if item is not None and item.item_id == item_id:
                count += item.quantity
        return count

    def _has_giftcode_items(self, acc):
        for item in acc.char.arr_item_bag or []:
            if item is not None and item.item_id in (457, 381, 382, 383, 384, 385, 386):
                return True
        return False

    def _count_bua_items(self, acc):
        found = set()
        for item in acc.char.arr_item_bag or []:
            if item is not None and item.item_id in BUA_ITEM_IDS:
                found.add(item.item_id)
        return len(found)

    # ══════════════════════════════════════════
    # GIFTCODE
    # ══════════════════════════════════════════

    async def _npc_giftcode(self, acc, npc_id, code, C):
        """Nhập giftcode tại NPC nhà (fallback tới Santa)."""
        ctrl = acc.controller

        # Thử tại NPC nhà
        if not await self._teleport_to_npc(acc, npc_id):
            self._log(acc, f"{C.YELLOW}→ Không tìm thấy NPC nhà.{C.RESET}")
            return False

        ctrl.ui_menu_event.clear()
        ctrl.input_form_received.clear()
        await acc.service.open_menu_npc(npc_id)
        try:
            await asyncio.wait_for(ctrl.ui_menu_event.wait(), timeout=3.0)
        except asyncio.TimeoutError:
            pass
        await asyncio.sleep(0.2)

        opts = ctrl.last_ui_options or []
        gift_opt = -1
        for i, opt in enumerate(opts):
            ol = opt.lower()
            if "giftcode" in ol or "quà tặng" in ol or "mã" in ol:
                gift_opt = i
                break

        if gift_opt != -1:
            await acc.service.confirm_menu_npc(npc_id, gift_opt)
            try:
                await asyncio.wait_for(ctrl.input_form_received.wait(), timeout=3.0)
                await asyncio.sleep(0.1)

                # Clear server message event before sending
                ctrl.server_message_event.clear()
                ctrl.last_server_message = ""

                await acc.service.send_client_input([code])

                # Wait for server response
                status, detail = await self._wait_giftcode_response(acc, ctrl, C)
                if status == "success":
                    self._log(acc, f"{C.GREEN}→ Giftcode '{code}' thành công!{C.RESET}")
                    # Kiểm tra item 1680 sau khi nhận giftcode
                    await self._check_giftcode_items(acc, C)
                    return True
                elif status == "used":
                    self._log(acc, f"{C.YELLOW}→ Giftcode '{code}' đã được sử dụng trước đó.{C.RESET}")
                    await self._check_giftcode_items(acc, C)
                    return True
                elif status == "expired":
                    self._log(acc, f"{C.RED}→ Giftcode '{code}' đã hết hạn.{C.RESET}")
                    return False
                elif status == "invalid":
                    self._log(acc, f"{C.RED}→ Giftcode '{code}' không tồn tại hoặc sai.{C.RESET}")
                    return False
                else:
                    self._log(acc, f"{C.GREEN}→ Giftcode '{code}' đã gửi (phản hồi: {detail}).{C.RESET}")
                    return True
            except asyncio.TimeoutError:
                self._log(acc, f"{C.YELLOW}→ Timeout chờ form nhập giftcode.{C.RESET}")
        else:
            self._log(acc, f"{C.YELLOW}→ NPC nhà không có tùy chọn Giftcode.{C.RESET}")

        # Fallback: tới Santa
        self._log(acc, f"{C.DIM}→ Chuyển tới Santa để nhập giftcode...{C.RESET}")
        return await self._npc_giftcode_santa(acc, code, C)

    async def _npc_giftcode_santa(self, acc, code, C):
        """Nhập giftcode tại Santa."""
        ctrl = acc.controller
        santa_map = SANTA_MAPS.get(acc.char.gender, 5)

        if ctrl.tile_map.map_id != santa_map:
            await ctrl.xmap.start(santa_map)
            for _ in range(45):
                if not acc.is_logged_in:
                    return False
                await asyncio.sleep(1)
                if not ctrl.xmap.is_xmapping:
                    break
                if ctrl.tile_map.map_id == santa_map:
                    ctrl.xmap.stop()
                    break

        if ctrl.tile_map.map_id != santa_map:
            self._log(acc, f"{C.RED}→ Không tới được map Santa {santa_map}.{C.RESET}")
            return False

        if not await self._teleport_to_npc(acc, NPC_SANTA):
            self._log(acc, f"{C.YELLOW}→ Không tìm thấy Santa.{C.RESET}")
            return False

        ctrl.ui_menu_event.clear()
        ctrl.input_form_received.clear()
        await acc.service.open_menu_npc(NPC_SANTA)
        try:
            await asyncio.wait_for(ctrl.ui_menu_event.wait(), timeout=3.0)
        except asyncio.TimeoutError:
            pass
        await asyncio.sleep(0.1)

        opts = ctrl.last_ui_options or []
        gift_opt = -1
        for i, opt in enumerate(opts):
            ol = opt.lower()
            if "giftcode" in ol or "quà tặng" in ol or "mã" in ol:
                gift_opt = i
                break

        if gift_opt != -1:
            await acc.service.confirm_menu_npc(NPC_SANTA, gift_opt)
            try:
                await asyncio.wait_for(ctrl.input_form_received.wait(), timeout=3.0)
                await asyncio.sleep(0.1)

                # Clear server message event before sending
                ctrl.server_message_event.clear()
                ctrl.last_server_message = ""

                await acc.service.send_client_input([code])

                # Wait for server response
                status, detail = await self._wait_giftcode_response(acc, ctrl, C)
                if status == "success":
                    self._log(acc, f"{C.GREEN}→ Giftcode '{code}' thành công tại Santa!{C.RESET}")
                    await self._check_giftcode_items(acc, C)
                    return True
                elif status == "used":
                    self._log(acc, f"{C.YELLOW}→ Giftcode '{code}' đã được sử dụng trước đó.{C.RESET}")
                    await self._check_giftcode_items(acc, C)
                    return True
                elif status == "expired":
                    self._log(acc, f"{C.RED}→ Giftcode '{code}' đã hết hạn tại Santa.{C.RESET}")
                    return False
                elif status == "invalid":
                    self._log(acc, f"{C.RED}→ Giftcode '{code}' không tồn tại hoặc sai.{C.RESET}")
                    return False
                else:
                    self._log(acc, f"{C.GREEN}→ Giftcode '{code}' đã gửi tại Santa (phản hồi: {detail}).{C.RESET}")
                    return True
            except asyncio.TimeoutError:
                self._log(acc, f"{C.YELLOW}→ Timeout chờ form giftcode tại Santa.{C.RESET}")

        self._log(acc, f"{C.RED}→ Không tìm thấy tùy chọn Giftcode tại Santa.{C.RESET}")
        return False

    # ══════════════════════════════════════════
    # STEP 6: FARM BEANS
    # ══════════════════════════════════════════

    async def _farm_magic_tree(self, acc, C, target_count=1000):
        """Farm đậu thần tại cây đậu trong nhà."""
        ctrl = acc.controller

        # Về nhà trước
        await self._go_home(acc, C)
        await asyncio.sleep(0.3)
        await self._teleport_to_npc(acc, NPC_DAU_THAN)
        await asyncio.sleep(0.3)

        bean_count = self._count_beans(acc)
        self._log(acc, f"{C.DIM}→ Đậu: {bean_count}/{target_count}{C.RESET}")

        if bean_count >= target_count:
            self._log(acc, f"{C.GREEN}→ Đủ đậu.{C.RESET}")
            return True

        prev_count = bean_count
        stuck = 0

        for r in range(300):
            if not acc.is_logged_in:
                self._log(acc, f"{C.RED}→ Mất kết nối, dừng farm đậu.{C.RESET}")
                return False

            ctrl.magic_tree_menu.clear()
            ctrl.magic_tree_options = []
            ctrl.ui_menu_event.clear()
            await acc.service.open_menu_npc(NPC_DAU_THAN)
            try:
                await asyncio.wait_for(ctrl.ui_menu_event.wait(), timeout=2.0)
            except asyncio.TimeoutError:
                pass
            await asyncio.sleep(0.1)

            opts = ctrl.magic_tree_options or ctrl.last_ui_options or []
            if not opts:
                await asyncio.sleep(0.1)
                continue

            lo = [o.lower().replace('\n', ' ') for o in opts]
            has_fast = any('kết hạt' in o for o in lo)
            has_harvest = any('thu' in o and 'hoạch' in o for o in lo)

            if has_fast:
                fi = next((i for i, o in enumerate(lo) if 'kết hạt' in o), None)
                if fi is not None:
                    self._log(acc, f"{C.DIM}[{r+1}] Kết hạt nhanh →{C.RESET}")
                    await acc.service.confirm_menu_npc(NPC_DAU_THAN, fi)
                    await asyncio.sleep(0.1)
            elif has_harvest:
                self._log(acc, f"{C.DIM}[{r+1}] Thu hoạch →{C.RESET}")
                await acc.service.confirm_menu_npc(NPC_DAU_THAN, 0)
                await asyncio.sleep(0.1)
            else:
                await acc.service.confirm_menu_npc(NPC_DAU_THAN, 0)
                await asyncio.sleep(0.1)

            bean_count = self._count_beans(acc)
            if r % 5 == 0 or bean_count >= target_count:
                self._log(acc, f"{C.DIM}  Đậu: {bean_count}/{target_count}{C.RESET}")
            if bean_count >= target_count:
                self._log(acc, f"{C.GREEN}→ Đủ đậu: {bean_count}.{C.RESET}")
                return True

            if bean_count == prev_count:
                stuck += 1
                if stuck >= 10:
                    self._log(acc, f"{C.YELLOW}→ Bị kẹt không tăng đậu.{C.RESET}")
                    break
            else:
                stuck = 0
            prev_count = bean_count

        bean_count = self._count_beans(acc)
        if bean_count >= target_count:
            self._log(acc, f"{C.GREEN}→ Đủ đậu: {bean_count}.{C.RESET}")
            return True

        self._log(acc, f"{C.YELLOW}→ Đậu: {bean_count}/{target_count}.{C.RESET}")
        return False

    # ══════════════════════════════════════════
    # STEP 7: BUY BUA
    # ══════════════════════════════════════════

    async def _buy_bua(self, acc, C) -> bool:
        """Mua bùa tại Bà Hạt Mít (Vách Núi Moori)."""
        ctrl = acc.controller

        # Di chuyển đến Vách Núi Moori
        if ctrl.tile_map.map_id != MAP_VACH_NUI:
            try:
                await ctrl.xmap.start(MAP_VACH_NUI)
                for _ in range(45):
                    if not acc.is_logged_in:
                        return False
                    await asyncio.sleep(1)
                    if not ctrl.xmap.is_xmapping:
                        break
                    if ctrl.tile_map.map_id == MAP_VACH_NUI:
                        ctrl.xmap.stop()
                        break
                if ctrl.tile_map.map_id != MAP_VACH_NUI:
                    self._log(acc, f"{C.YELLOW}→ Không đến được vách núi.{C.RESET}")
                    return False
                self._log(acc, f"{C.GREEN}→ Đã đến vách núi.{C.RESET}")
            except Exception as e:
                self._log(acc, f"{C.RED}→ Lỗi xmap: {e}{C.RESET}")
                return False

        await asyncio.sleep(0.5)

        # Teleport đến Bà Hạt Mít
        if not await self._teleport_to_npc(acc, NPC_BA_HAT_MIT):
            self._log(acc, f"{C.YELLOW}→ Không tìm thấy Bà Hạt Mít.{C.RESET}")
            return False

        await asyncio.sleep(0.1)

        # Mở menu → Cửa hàng bùa (option 2) → Bùa 1 tháng (option 2)
        ctrl.ui_menu_event.clear()
        await acc.service.open_menu_npc(NPC_BA_HAT_MIT)
        try:
            await asyncio.wait_for(ctrl.ui_menu_event.wait(), timeout=3.0)
        except asyncio.TimeoutError:
            pass
        await asyncio.sleep(0.1)

        self._log(acc, f"{C.DIM}→ Mở cửa hàng bùa...{C.RESET}")
        ctrl.ui_menu_event.clear()
        await acc.service.confirm_menu_npc(NPC_BA_HAT_MIT, 2)
        try:
            await asyncio.wait_for(ctrl.ui_menu_event.wait(), timeout=3.0)
        except asyncio.TimeoutError:
            pass
        await asyncio.sleep(0.1)

        self._log(acc, f"{C.DIM}→ Chọn bùa 1 tháng...{C.RESET}")
        await acc.service.confirm_menu_npc(NPC_BA_HAT_MIT, 2)
        await asyncio.sleep(0.1)

        # Mua từng item bùa chưa có
        bought = 0
        existing_buas = {item.item_id for item in (acc.char.arr_item_bag or []) if item is not None}
        for item_id in BUA_ITEM_IDS:
            if item_id in existing_buas:
                continue
            try:
                await acc.service.buy_item(0, item_id)
                bought += 1
                await asyncio.sleep(0.1)
            except Exception:
                pass

        if bought > 0:
            self._log(acc, f"{C.GREEN}→ Đã mua {bought} loại bùa.{C.RESET}")
        else:
            self._log(acc, f"{C.YELLOW}→ Không mua được bùa (có thể đã có đủ).{C.RESET}")

        # Bùa dùng xong không vào hành trang
        self._log(acc, f"{C.GREEN}→ Bùa không vào balo (đã mua {bought} loại).{C.RESET}")

        # Refresh thông tin
        try:
            await acc.service.request_me_info()
        except Exception:
            pass
        await asyncio.sleep(0.3)

        return True

    # ══════════════════════════════════════════
    # STEP 8: SANTA SHOP
    # ══════════════════════════════════════════

    async def _santa_shop(self, acc, C) -> bool:
        """Mua item tại Santa shop (Đảo Kame hoặc map Santa)."""
        ctrl = acc.controller
        santa_map = SANTA_MAPS.get(acc.char.gender, 5)

        # Di chuyển tới map Santa
        if ctrl.tile_map.map_id != santa_map:
            self._log(acc, f"{C.DIM}→ Di chuyển tới map Santa ({santa_map})...{C.RESET}")
            try:
                await ctrl.xmap.start(santa_map)
                for _ in range(45):
                    if not acc.is_logged_in:
                        return False
                    await asyncio.sleep(1)
                    if not ctrl.xmap.is_xmapping:
                        break
                    if ctrl.tile_map.map_id == santa_map:
                        ctrl.xmap.stop()
                        break
            except Exception as e:
                self._log(acc, f"{C.RED}→ Lỗi xmap: {e}{C.RESET}")
                return False

        if ctrl.tile_map.map_id != santa_map:
            self._log(acc, f"{C.YELLOW}→ Không đến được map Santa ({santa_map}).{C.RESET}")
            return False

        # Teleport tới Santa
        if not await self._teleport_to_npc(acc, NPC_SANTA):
            self._log(acc, f"{C.YELLOW}→ Không tìm thấy Santa.{C.RESET}")
            return False
        await asyncio.sleep(0.2)

        async def _open_and_buy(tab_keywords, tab_default, items) -> bool:
            for attempt in range(1, 4):
                if attempt > 1:
                    await asyncio.sleep(0.5)
                    if not await self._teleport_to_npc(acc, NPC_SANTA):
                        continue
                    await asyncio.sleep(0.2)

                # Mở menu Santa
                ctrl.ui_menu_event.clear()
                await acc.service.open_menu_npc(NPC_SANTA)
                try:
                    await asyncio.wait_for(ctrl.ui_menu_event.wait(), timeout=3.0)
                except asyncio.TimeoutError:
                    pass
                await asyncio.sleep(0.1)

                opts = ctrl.last_ui_options or []
                shop_opt = -1
                for i, opt in enumerate(opts):
                    ol = opt.lower()
                    if "cửa hàng" in ol or "hỗ trợ" in ol or "hotro" in ol:
                        shop_opt = i
                        break
                if shop_opt == -1:
                    shop_opt = 0

                # Chọn cửa hàng hỗ trợ
                ctrl.ui_menu_event.clear()
                await acc.service.confirm_menu_npc(NPC_SANTA, shop_opt)
                try:
                    await asyncio.wait_for(ctrl.ui_menu_event.wait(), timeout=3.0)
                except asyncio.TimeoutError:
                    pass
                await asyncio.sleep(0.1)

                # Chọn tab
                tab_opts = ctrl.last_ui_options or []
                tab_idx = -1
                for i, opt in enumerate(tab_opts):
                    for kw in tab_keywords:
                        if kw in opt.lower():
                            tab_idx = i
                            break
                    if tab_idx != -1:
                        break
                if tab_idx == -1:
                    tab_idx = tab_default

                ctrl.ui_menu_event.clear()
                await acc.service.confirm_menu_npc(NPC_SANTA, tab_idx)
                try:
                    await asyncio.wait_for(ctrl.ui_menu_event.wait(), timeout=3.0)
                except asyncio.TimeoutError:
                    pass
                await asyncio.sleep(0.1)

                # Mua items
                all_ok = True
                for item_id, qty in items:
                    count = self._count_item(acc, item_id)
                    need = max(0, qty - count)
                    if need <= 0:
                        self._log(acc, f"{C.GREEN}→ Đã có đủ item {item_id} ({count}).{C.RESET}")
                        continue
                    self._log(acc, f"{C.DIM}→ Mua {need} item {item_id} (có {count}/{qty})...{C.RESET}")
                    bought = 0
                    for i in range(need):
                        if not acc.is_logged_in:
                            break
                        try:
                            await acc.service.buy_item(0, item_id)
                            bought += 1
                            if bought % 50 == 0:
                                self._log(acc, f"{C.DIM}  Đã mua {bought}/{need} item {item_id}.{C.RESET}")
                            await asyncio.sleep(0.03)
                        except Exception:
                            break
                    if bought > 0:
                        self._log(acc, f"{C.GREEN}→ Đã mua {bought} item {item_id}.{C.RESET}")

                    if item_id not in SANTA_NO_BAG_ITEMS:
                        try:
                            await acc.service.request_me_info()
                        except Exception:
                            pass
                        await asyncio.sleep(0.3)
                        final_count = self._count_item(acc, item_id)
                        if final_count < qty:
                            self._log(acc, f"{C.YELLOW}  Còn thiếu {qty - final_count} item {item_id}.{C.RESET}")
                            all_ok = False

                if all_ok:
                    return True
            return False

        # Tab hỗ trợ
        self._log(acc, f"{C.DIM}→ Tab hỗ trợ: 517x100, 518x50...{C.RESET}")
        ok = await _open_and_buy(
            tab_keywords=["hỗ trợ", "hotro", "trợ"],
            tab_default=0,
            items=SANTA_ITEM_HO_TRO
        )
        if not ok:
            self._log(acc, f"{C.RED}→ Mua tab hỗ trợ không đủ.{C.RESET}")

        # Tab đặc biệt
        self._log(acc, f"{C.DIM}→ Tab đặc biệt: 402x6, 403x6...{C.RESET}")
        ok = await _open_and_buy(
            tab_keywords=["đặc biệt", "dac biet", "biệt", "special"],
            tab_default=1,
            items=SANTA_ITEM_DAC_BIET
        )
        if not ok:
            self._log(acc, f"{C.RED}→ Mua tab đặc biệt không đủ.{C.RESET}")

        return True

    # ══════════════════════════════════════════
    # STEP 9: USE SUPPORT ITEMS (1182, 1680)
    # ══════════════════════════════════════════

    async def _step_use_support_items(self, acc, C) -> bool:
        """
        - Item 1182: Dùng để nhận item 441. Mục tiêu: item 441 >= 20.
          Nếu item 441 < 20, dùng item 1182 cho đến khi đủ hoặc hết 1182.
        - Item 1680: Nếu còn tồn tại trong balo, dùng 1 lần.
        """
        # Refresh inventory
        try:
            await acc.service.request_me_info()
            await asyncio.sleep(0.3)
        except Exception:
            pass

        item_441_qty = self._count_item(acc, ITEM_441)
        item_1182_qty = self._count_item(acc, ITEM_1182)

        # Dùng item 1182 để có item 441
        if item_441_qty < 20 and item_1182_qty > 0:
            need = 20 - item_441_qty
            # Ước tính: mỗi 1 item 1182 cho ~1 item 441 (có thể cần nhiều hơn)
            use_count = min(item_1182_qty, need * 2)  # Dùng gấp đôi để đảm bảo
            self._log(acc, f"{C.DIM}→ Dùng tối đa {use_count} item 1182 để có item 441 ({item_441_qty}/20)...{C.RESET}")

            for i, item in enumerate(acc.char.arr_item_bag or []):
                if item is not None and item.item_id == ITEM_1182:
                    for _ in range(min(item.quantity, use_count)):
                        if not acc.is_logged_in:
                            break
                        try:
                            await acc.service.use_item(0, 1, i, -1)
                            use_count -= 1
                            await asyncio.sleep(0.1)
                            if use_count <= 0:
                                break
                        except Exception:
                            break
                    if use_count <= 0:
                        break

            # Refresh để kiểm tra kết quả
            try:
                await acc.service.request_me_info()
                await asyncio.sleep(0.3)
            except Exception:
                pass
            item_441_qty = self._count_item(acc, ITEM_441)

            if item_441_qty >= 20:
                self._log(acc, f"{C.GREEN}→ Đã đủ item 441 ({item_441_qty}).{C.RESET}")
            else:
                self._log(acc, f"{C.YELLOW}→ Item 441: {item_441_qty}/20 (có thể hết item 1182).{C.RESET}")
        elif item_441_qty >= 20:
            self._log(acc, f"{C.GREEN}→ Đã có đủ item 441 ({item_441_qty}).{C.RESET}")
        else:
            self._log(acc, f"{C.YELLOW}→ Không có item 1182 và item 441 < 20.{C.RESET}")

        # Dùng item 1680 (nếu còn)
        item_1680_qty = self._count_item(acc, ITEM_1680)
        if item_1680_qty > 0:
            self._log(acc, f"{C.DIM}→ Dùng 1 item 1680...{C.RESET}")
            for i, item in enumerate(acc.char.arr_item_bag or []):
                if item is not None and item.item_id == ITEM_1680:
                    try:
                        await acc.service.use_item(0, 1, i, -1)
                        await asyncio.sleep(0.3)
                        self._log(acc, f"{C.GREEN}→ Đã dùng item 1680.{C.RESET}")
                    except Exception as e:
                        self._log(acc, f"{C.RED}→ Lỗi dùng item 1680: {e}{C.RESET}")
                    break
        else:
            self._log(acc, f"{C.YELLOW}→ Không có item 1680 trong balo.{C.RESET}")

        return True

    # ══════════════════════════════════════════
    # STEP 10: ACTIVATE REWARD ITEMS
    # ══════════════════════════════════════════

    async def _step_activate_items(self, acc, C) -> bool:
        """Kích hoạt các item thưởng: 2000 (x2, chọn Set Liên Hoàn), 290, 1269, 1357, 1649, 1983, 1499, 1323."""
        ctrl = acc.controller

        # Refresh inventory
        try:
            await acc.service.request_me_info()
            await asyncio.sleep(0.3)
        except Exception:
            pass

        # ── Item 2000 (dùng 2 lần, chọn Set Liên Hoàn) ──
        # Mở item 2000 sẽ hiện menu với nhiều set (Set Thời Trang, Set Hè, Set Liên Hoàn, v.v.)
        # Phải chọn đúng "Set Liên Hoàn" để nhận Item 1 (nguyên liệu ép sao)
        count_2000 = self._count_item(acc, ITEM_2000)
        if count_2000 > 0:
            use_times = min(count_2000, ITEM_2000_USE_TIMES)
            self._log(acc, f"{C.DIM}→ Dùng item 2000 ({use_times} lần), chọn Set Liên Hoàn...{C.RESET}")

            for round_idx in range(use_times):
                if not acc.is_logged_in:
                    break

                item1_before = self._count_item(acc, ITEM_UPGRADE_16_CRYSTAL)
                self._log(acc, f"{C.DIM}  Lần {round_idx + 1}/{use_times}: Item 1 trước = {item1_before}.{C.RESET}")

                # Retry tối đa 3 lần cho mỗi lần dùng
                item2000_success = False
                for retry in range(1, 4):
                    if not acc.is_logged_in:
                        break

                    if retry > 1:
                        self._log(acc, f"{C.YELLOW}  Retry lần {retry}/3 mở item 2000...{C.RESET}")
                        await asyncio.sleep(0.5)
                        try:
                            await acc.service.request_me_info()
                            await asyncio.sleep(0.2)
                        except Exception:
                            pass

                    # Tìm và dùng item 2000
                    found_item = -1
                    for idx, item in enumerate(acc.char.arr_item_bag or []):
                        if item is not None and item.item_id == ITEM_2000:
                            found_item = idx
                            break

                    if found_item == -1:
                        self._log(acc, f"{C.YELLOW}  Hết item 2000 trong bag.{C.RESET}")
                        item2000_success = True  # Đã hết, skip
                        break

                    # Dùng item 2000
                    ctrl.ui_menu_event.clear()
                    ctrl.last_npc_template_id = 0
                    ctrl.last_ui_options = []
                    try:
                        self._log(acc, f"{C.DIM}  Dùng item 2000 tại bag index {found_item}...{C.RESET}")
                        await acc.service.use_item(0, 1, found_item, -1)
                        await asyncio.sleep(0.8)

                        # Đợi menu xuất hiện
                        try:
                            await asyncio.wait_for(ctrl.ui_menu_event.wait(), timeout=5.0)
                        except asyncio.TimeoutError:
                            self._log(acc, f"{C.YELLOW}    Timeout chờ menu item 2000.{C.RESET}")

                        opts = ctrl.last_ui_options or []
                        menu_npc = ctrl.last_npc_template_id
                        self._log(acc, f"{C.DIM}    Menu 2000: npc_id={menu_npc}, {len(opts)} options: {opts}{C.RESET}")

                        # Chỉ tìm "Set Liên Hoàn" — không match "bộ", "set", "trang bị" vì nhiều set khác cũng có từ này
                        target_idx = -1
                        for j, opt in enumerate(opts):
                            ol = opt.lower().replace('\n', ' ')
                            # Chỉ match chính xác "liên hoàn" hoặc "lien hoan"
                            if "liên hoàn" in ol or "lien hoan" in ol or "lienhoan" in ol:
                                target_idx = j
                                self._log(acc, f"{C.GREEN}    Tìm thấy 'Set Liên Hoàn' tại index {j}: '{opt}'.{C.RESET}")
                                break

                        if target_idx != -1:
                            # Dùng đúng npc_id từ server gửi xuống
                            npc_to_use = menu_npc if menu_npc > 0 else 0
                            self._log(acc, f"{C.DIM}    Chọn option {target_idx} với npc_id={npc_to_use}.{C.RESET}")
                            await acc.service.confirm_menu_npc(npc_to_use, target_idx)
                            await asyncio.sleep(2.0)  # Đợi lâu để server xử lý

                            # Refresh inventory
                            try:
                                await acc.service.request_me_info()
                                await asyncio.sleep(0.5)
                            except Exception:
                                pass

                            item1_after = self._count_item(acc, ITEM_UPGRADE_16_CRYSTAL)
                            if item1_after > item1_before:
                                self._log(acc, f"{C.GREEN}    ✓ Đã chọn Set Liên Hoàn: Item 1 +{item1_after - item1_before} (tổng: {item1_after}).{C.RESET}")
                                item2000_success = True
                                break
                            else:
                                self._log(acc, f"{C.YELLOW}    Item 1 không tăng (trước={item1_before}, sau={item1_after}), thử lại.{C.RESET}")
                        else:
                            # Không tìm thấy Set Liên Hoàn — KHÔNG CHỌN BỪA (sẽ làm mất Item 2000 vào set sai)
                            self._log(acc, f"{C.RED}    Không tìm thấy 'Set Liên Hoàn' trong menu! Options: {opts}{C.RESET}")
                            self._log(acc, f"{C.YELLOW}    => Không chọn option nào để tránh mất item 2000.{C.RESET}")
                    except Exception as e:
                        self._log(acc, f"{C.RED}    Lỗi: {e}.{C.RESET}")

                if not item2000_success:
                    self._log(acc, f"{C.YELLOW}  Không mở được Set Liên Hoàn sau retry.{C.RESET}")

                # Kiểm tra item cuối cùng
                item16_count = self._count_item(acc, ITEM_UPGRADE_16)
                item1_count = self._count_item(acc, ITEM_UPGRADE_16_CRYSTAL)
                self._log(acc, f"{C.DIM}  Sau Set Liên Hoàn lần {round_idx + 1}: Item 1={item1_count}, Item 16={item16_count}.{C.RESET}")
        else:
            self._log(acc, f"{C.YELLOW}→ Không có item 2000.{C.RESET}")

        # ── Các item kích hoạt (dùng 1 lần mỗi item) ──
        self._log(acc, f"{C.DIM}→ Dùng item kích hoạt: {ACTIVATE_ITEMS_ONCE}...{C.RESET}")
        for item_id in ACTIVATE_ITEMS_ONCE:
            if not acc.is_logged_in:
                break
            # Refresh trước khi check
            try:
                await acc.service.request_me_info()
                await asyncio.sleep(0.15)
            except Exception:
                pass

            count = self._count_item(acc, item_id)
            if count == 0:
                self._log(acc, f"{C.YELLOW}→ Không có item {item_id}.{C.RESET}")
                continue

            self._log(acc, f"{C.DIM}→ Dùng 1 item {item_id} (có {count})...{C.RESET}")
            for idx, item in enumerate(acc.char.arr_item_bag or []):
                if item is not None and item.item_id == item_id:
                    try:
                        await acc.service.use_item(0, 1, idx, -1)
                        await asyncio.sleep(0.15)
                        self._log(acc, f"{C.GREEN}→ Đã dùng item {item_id}.{C.RESET}")
                    except Exception as e:
                        self._log(acc, f"{C.RED}→ Lỗi dùng item {item_id}: {e}{C.RESET}")
                    break

        return True

    # ══════════════════════════════════════════
    # COMBINE HELPERS (dùng cho STEP 11 & 12)
    # ══════════════════════════════════════════

    async def _open_ep_sao_trang_bi(self, acc, C) -> bool:
        """
        Mở giao diện Ép Sao Trang Bị tại Bà Hạt Mít (Đảo Kame, map 5).
        Flow: Open NPC → "Chức năng pha lê" → "Ép sao trang bị"
        """
        ctrl = acc.controller

        # Đảm bảo đang ở Đảo Kame (map 5)
        if ctrl.tile_map.map_id != MAP_DAO_KAME:
            self._log(acc, f"{C.DIM}→ Di chuyển tới Đảo Kame (map {MAP_DAO_KAME})...{C.RESET}")
            try:
                await ctrl.xmap.start(MAP_DAO_KAME)
                for _ in range(45):
                    if not acc.is_logged_in:
                        return False
                    await asyncio.sleep(1)
                    if not ctrl.xmap.is_xmapping:
                        break
                    if ctrl.tile_map.map_id == MAP_DAO_KAME:
                        ctrl.xmap.stop()
                        break
            except Exception as e:
                self._log(acc, f"{C.RED}→ Lỗi xmap tới Đảo Kame: {e}{C.RESET}")
                return False

        if ctrl.tile_map.map_id != MAP_DAO_KAME:
            self._log(acc, f"{C.YELLOW}→ Không tới được Đảo Kame.{C.RESET}")
            return False

        # Teleport tới Bà Hạt Mít
        if not await self._teleport_to_npc(acc, NPC_BA_HAT_MIT):
            self._log(acc, f"{C.YELLOW}→ Không tìm thấy Bà Hạt Mít.{C.RESET}")
            return False
        await asyncio.sleep(0.2)

        # Mở menu Bà Hạt Mít
        ctrl.ui_menu_event.clear()
        await acc.service.open_menu_npc(NPC_BA_HAT_MIT)
        try:
            await asyncio.wait_for(ctrl.ui_menu_event.wait(), timeout=3.0)
        except asyncio.TimeoutError:
            pass
        await asyncio.sleep(0.2)

        opts = ctrl.last_ui_options or []
        self._log(acc, f"{C.DIM}→ Menu Bà Hạt Mít: {opts}{C.RESET}")

        # Tìm "pha lê" hoặc "chức năng" (flow: Pha Lê Hóa Trang Bị → Ép Sao Trang Bị)
        func_idx = -1
        for i, opt in enumerate(opts):
            ol = opt.lower()
            if "pha lê" in ol or "pha le" in ol or "chức năng" in ol or "chuc nang" in ol:
                func_idx = i
                break
        if func_idx == -1:
            func_idx = 0  # fallback: option đầu tiên

        self._log(acc, f"{C.DIM}→ Chọn '{opts[func_idx] if func_idx < len(opts) else func_idx}'.{C.RESET}")
        ctrl.ui_menu_event.clear()
        await acc.service.confirm_menu_npc(NPC_BA_HAT_MIT, func_idx)
        try:
            await asyncio.wait_for(ctrl.ui_menu_event.wait(), timeout=3.0)
        except asyncio.TimeoutError:
            pass
        await asyncio.sleep(0.3)

        opts2 = ctrl.last_ui_options or []
        self._log(acc, f"{C.DIM}→ Menu pha lê: {opts2}{C.RESET}")

        # Tìm "ép sao" hoặc "trang bị" (theo flow: Pha Lê Hóa → Ép Sao Trang Bị)
        ep_idx = -1
        """
        Flow từ user:
        1. Ấn "Pha Lê Hóa Trang Bị" (sub-menu index ~1)
        2. Ấn "Ép Sao Trang Bị" (sub-menu index ~0)
        """
        for i, opt in enumerate(opts2):
            ol = opt.lower()
            if "ép sao" in ol or "ep sao" in ol or "trang bị" in ol:
                ep_idx = i
                break
        if ep_idx == -1:
            ep_idx = 0  # fallback: option đầu tiên (ép sao)

        self._log(acc, f"{C.DIM}→ Chọn '{opts2[ep_idx] if ep_idx < len(opts2) else ep_idx}'.{C.RESET}")
        ctrl.ui_menu_event.clear()
        ctrl.combine_event.clear()
        ctrl.combine_result = ""
        await acc.service.confirm_menu_npc(NPC_BA_HAT_MIT, ep_idx)

        # Đợi server mở tab combine (Message -81 với OPEN_TAB_COMBINE)
        try:
            await asyncio.wait_for(ctrl.combine_event.wait(), timeout=3.0)
            self._log(acc, f"{C.GREEN}→ Tab combine đã mở.{C.RESET}")
        except asyncio.TimeoutError:
            self._log(acc, f"{C.YELLOW}→ Timeout chờ tab combine (vẫn tiếp tục).{C.RESET}")

        await asyncio.sleep(0.3)
        return True

    async def _do_one_upgrade(self, acc, C, main_item_id: int,
                              material_items: list[tuple[int, int]],
                              max_upgrades: int = 1,
                              clear_between: bool = True) -> int:
        """
        Thực hiện nâng cấp một item tại Ép Sao Trang Bị.
        Args:
            main_item_id: ID item chính cần nâng cấp
            material_items: [(item_id, quantity)] nguyên liệu
            max_upgrades: Số lần nâng cấp tối đa
            clear_between: True nếu cần clear items giữa các lần
        Returns:
            Số lần nâng cấp thành công
        """
        ctrl = acc.controller
        success_count = 0

        for upgrade_round in range(max_upgrades):
            if not acc.is_logged_in:
                break

            self._log(acc, f"{C.DIM}  Nâng cấp lần {upgrade_round + 1}/{max_upgrades} (main={main_item_id}, materials={material_items})...{C.RESET}")

            # Refresh inventory
            try:
                await acc.service.request_me_info()
                await asyncio.sleep(0.2)
            except Exception:
                pass

            # Tìm item chính trong bag
            main_indices = []
            for idx, item in enumerate(acc.char.arr_item_bag or []):
                if item is not None and item.item_id == main_item_id:
                    main_indices.append(idx)

            if not main_indices:
                self._log(acc, f"{C.YELLOW}  Không tìm thấy item {main_item_id} trong bag.{C.RESET}")
                break

            main_idx = main_indices[0]

            # Tìm nguyên liệu trong bag
            all_indices = [main_idx]
            all_ok = True
            for mat_id, mat_qty in material_items:
                mat_found = 0
                for idx, item in enumerate(acc.char.arr_item_bag or []):
                    if item is not None and item.item_id == mat_id:
                        if mat_found < mat_qty:
                            all_indices.append(idx)
                            mat_found += 1
                if mat_found < mat_qty:
                    self._log(acc, f"{C.YELLOW}  Thiếu nguyên liệu: item {mat_id} (cần {mat_qty}, có {mat_found}).{C.RESET}")
                    all_ok = False

            if not all_ok:
                break

            self._log(acc, f"{C.DIM}  Gửi indices {all_indices} lên combine...{C.RESET}")

            # Gửi item indices lên server
            ctrl.combine_event.clear()
            ctrl.combine_result = ""
            await acc.service.send_combine_items(all_indices)

            # Đợi server phản hồi (menu xác nhận hoặc lỗi)
            await asyncio.sleep(0.3)

            # Server sẽ gửi menu xác nhận qua Message(32) - OPEN_UI_CONFIRM
            # Tìm "nâng cấp" hoặc "cần (ngọc)" trong menu
            ctrl.ui_menu_event.clear()
            try:
                await asyncio.wait_for(ctrl.ui_menu_event.wait(), timeout=3.0)
            except asyncio.TimeoutError:
                pass
            await asyncio.sleep(0.2)

            opts = ctrl.last_ui_options or []
            self._log(acc, f"{C.DIM}  Menu combine: {opts}{C.RESET}")

            # Nếu không có menu, có thể items không hợp lệ
            if not opts:
                self._log(acc, f"{C.YELLOW}  Không có menu xác nhận (items không hợp lệ).{C.RESET}")
                # Nếu cần clear, teleport lại NPC và mở lại
                if clear_between:
                    await self._teleport_to_npc(acc, NPC_BA_HAT_MIT)
                    await asyncio.sleep(0.2)
                continue

            # Tìm "nâng cấp" / "cần" / "ngọc" trong options
            confirm_idx = -1
            for i, opt in enumerate(opts):
                ol = opt.lower()
                if "nâng cấp" in ol or "nang cap" in ol or "cần" in ol or "ngọc" in ol:
                    confirm_idx = i
                    break
            if confirm_idx == -1:
                confirm_idx = 0  # fallback

            self._log(acc, f"{C.DIM}  Chọn '{opts[confirm_idx]}'.{C.RESET}")

            # Gửi xác nhận nâng cấp
            ctrl.combine_event.clear()
            ctrl.combine_result = ""
            await acc.service.confirm_menu_npc(NPC_BA_HAT_MIT, confirm_idx)

            # Đợi kết quả từ server (Message -81 với COMBINE_SUCCESS/FAIL)
            try:
                await asyncio.wait_for(ctrl.combine_event.wait(), timeout=3.0)
            except asyncio.TimeoutError:
                pass

            result = ctrl.combine_result
            if result == "success":
                success_count += 1
                self._log(acc, f"{C.GREEN}  ✓ Nâng cấp thành công! (lần {upgrade_round + 1}).{C.RESET}")
            elif result == "fail":
                success_count += 1
                self._log(acc, f"{C.YELLOW}  Nâng cấp thất bại (lần {upgrade_round + 1}).{C.RESET}")
            else:
                self._log(acc, f"{C.GREEN}  Đã gửi yêu cầu nâng cấp (lần {upgrade_round + 1}).{C.RESET}")
                success_count += 1

            # Giữa các lần: Mở lại giao diện Ép Sao Trang Bị
            if clear_between and upgrade_round + 1 < max_upgrades:
                if not await self._open_ep_sao_trang_bi(acc, C):
                    self._log(acc, f"{C.YELLOW}  Không mở lại được Ép Sao Trang Bị.{C.RESET}")
                    return success_count

        return success_count

    # ══════════════════════════════════════════
    # STEP 11: UPGRADE ITEM 16 (Ép sao x11)
    # ══════════════════════════════════════════

    async def _step_upgrade_item_16(self, acc, C) -> bool:
        """
        Nâng cấp item ID 16 tại Bà Hạt Mít (Ép Sao Trang Bị) 11 lần.
        Mỗi lần: 1x ID 16 (chính) + 1x ID 1 (nguyên liệu)
        """
        # Mở giao diện Ép Sao Trang Bị
        if not await self._open_ep_sao_trang_bi(acc, C):
            return False

        # Kiểm tra số lượng item 16 hiện có
        try:
            await acc.service.request_me_info()
            await asyncio.sleep(0.2)
        except Exception:
            pass

        item_16_count = self._count_item(acc, ITEM_UPGRADE_16)
        item_1_count = self._count_item(acc, ITEM_UPGRADE_16_CRYSTAL)

        self._log(acc, f"{C.DIM}→ Item 16: {item_16_count}, Item 1 (nguyên liệu): {item_1_count}.{C.RESET}")

        if item_16_count == 0:
            self._log(acc, f"{C.YELLOW}→ Không có item 16 để nâng cấp.{C.RESET}")
            return True  # Skip nếu không có

        # Mỗi lần ép cần 2 item ID 1
        ITEM_1_PER_UPGRADE = 2
        upgrades_needed = min(ITEM_UPGRADE_16_TIMES, item_16_count)
        max_with_item1 = item_1_count // ITEM_1_PER_UPGRADE
        if max_with_item1 < upgrades_needed:
            self._log(acc, f"{C.YELLOW}→ Thiếu nguyên liệu: cần {upgrades_needed * ITEM_1_PER_UPGRADE} item 1, có {item_1_count} (đủ {max_with_item1}/{upgrades_needed} lần).{C.RESET}")
            upgrades_needed = max_with_item1

        if upgrades_needed <= 0:
            self._log(acc, f"{C.YELLOW}→ Không đủ nguyên liệu để ép item 16 (cần 2x Item 1/lần).{C.RESET}")
            return False

        self._log(acc, f"{C.DIM}→ Bắt đầu ép item 16 ({upgrades_needed} lần, mỗi lần 2x Item 1)...{C.RESET}")

        # Mỗi lần ép: 1x ID 16 (chính) + 2x ID 1 (nguyên liệu)
        done = await self._do_one_upgrade(
            acc, C,
            main_item_id=ITEM_UPGRADE_16,
            material_items=[(ITEM_UPGRADE_16_CRYSTAL, 2)],  # Cần 2 item ID 1 mỗi lần
            max_upgrades=upgrades_needed,
            clear_between=True
        )

        if done > 0:
            self._log(acc, f"{C.GREEN}→ Hoàn thành {done}/{upgrades_needed} lần ép item 16.{C.RESET}")
            return True

        self._log(acc, f"{C.RED}→ Không ép được item 16.{C.RESET}")
        return False

    # ══════════════════════════════════════════
    # STEP 12: UPGRADE OTHER ITEMS (1, 22, 28, 12)
    # ══════════════════════════════════════════

    async def _step_upgrade_other_items(self, acc, C) -> bool:
        """
        Nâng cấp các item còn lại (tối đa 10 lần mỗi item):
        - ID 1: ép 10 lần (mỗi lần 2x ID 1)
        - ID 22: ép 10 lần (mỗi lần 2x ID 22)
        - ID 28: ép 10 lần (mỗi lần 2x ID 28)
        - ID 12 first: 1x ID 12 + ID 16 đã ép
        - ID 12 second: 1x ID 12 + 2x ID 442 + 8x ID 441
        """
        # Mở giao diện Ép Sao Trang Bị
        if not await self._open_ep_sao_trang_bi(acc, C):
            self._log(acc, f"{C.RED}→ Không mở được Ép Sao Trang Bị.{C.RESET}")
            return False

        # Refresh inventory
        try:
            await acc.service.request_me_info()
            await asyncio.sleep(0.2)
        except Exception:
            pass

        overall_ok = True

        # ── Các item đơn giản (ID 1, 22, 28) — ép 10 lần mỗi item ──
        for item_id in UPGRADE_OTHER_ITEMS:
            count = self._count_item(acc, item_id)
            if count < 2:
                self._log(acc, f"{C.YELLOW}→ Item {item_id}: không đủ để ép (có {count}, cần >=2).{C.RESET}")
                continue

            # Ép tối đa 10 lần mỗi item (như áo)
            max_up = min(UPGRADE_TIMES_PER_PIECE, count // 2)
            self._log(acc, f"{C.DIM}→ Ép item {item_id} ({max_up} lần, có {count})...{C.RESET}")

            done = await self._do_one_upgrade(
                acc, C,
                main_item_id=item_id,
                material_items=[(item_id, 1)],  # 1x item+1x same item = 2 items total
                max_upgrades=max_up,
                clear_between=True
            )

            if done > 0:
                self._log(acc, f"{C.GREEN}  → Item {item_id}: ép thành công {done} lần.{C.RESET}")
            else:
                overall_ok = False
                self._log(acc, f"{C.YELLOW}  → Item {item_id}: không ép được.{C.RESET}")

            if not await self._ensure_logged_in(acc, C):
                return False

            # Mở lại giao diện ép sao cho item tiếp theo
            if not await self._open_ep_sao_trang_bi(acc, C):
                self._log(acc, f"{C.RED}→ Mất kết nối khi ép item {item_id}.{C.RESET}")
                return False

        # ── ID 12 first: 1x ID 12 + ID 16 đã ép từ STEP 11 ──
        if not await self._ensure_logged_in(acc, C):
            return False

        item_12_count = self._count_item(acc, ITEM_12)
        item_16_upgraded = self._count_item(acc, ITEM_UPGRADE_16)

        if item_12_count >= 1 and item_16_upgraded >= 1:
            self._log(acc, f"{C.DIM}→ Ép ID 12 first: ID 12 + ID 16 đã ép...{C.RESET}")

            # Mở lại giao diện ép sao (clear UI trước)
            if not await self._open_ep_sao_trang_bi(acc, C):
                self._log(acc, f"{C.YELLOW}  Không mở được ép sao.{C.RESET}")
            else:
                ctrl = acc.controller
                idx_12 = -1
                idx_16 = -1
                for idx, item in enumerate(acc.char.arr_item_bag or []):
                    if item is not None:
                        if item.item_id == ITEM_12 and idx_12 == -1:
                            idx_12 = idx
                        if item.item_id == ITEM_UPGRADE_16 and idx_16 == -1:
                            idx_16 = idx

                if idx_12 != -1 and idx_16 != -1:
                    ctrl.combine_event.clear()
                    ctrl.combine_result = ""
                    await acc.service.send_combine_items([idx_12, idx_16])
                    await asyncio.sleep(0.3)

                    ctrl.ui_menu_event.clear()
                    try:
                        await asyncio.wait_for(ctrl.ui_menu_event.wait(), timeout=3.0)
                    except asyncio.TimeoutError:
                        pass
                    await asyncio.sleep(0.2)

                    opts = ctrl.last_ui_options or []
                    if opts:
                        confirm_idx = 0
                        for i, opt in enumerate(opts):
                            if "nâng cấp" in opt.lower() or "cần" in opt.lower():
                                confirm_idx = i
                                break
                        await acc.service.confirm_menu_npc(NPC_BA_HAT_MIT, confirm_idx)
                        await asyncio.sleep(0.5)
                        self._log(acc, f"{C.GREEN}  → ID 12 first: đã gửi nâng cấp.{C.RESET}")
                    else:
                        self._log(acc, f"{C.YELLOW}  → ID 12 first: không có menu xác nhận.{C.RESET}")
        else:
            self._log(acc, f"{C.YELLOW}→ ID 12 first: thiếu item (12: {item_12_count}, 16: {item_16_upgraded}).{C.RESET}")

        # ── ID 12 second: 1x ID 12 + 2x ID 442 + 8x ID 441 ──
        if not await self._ensure_logged_in(acc, C):
            return False

        try:
            await acc.service.request_me_info()
            await asyncio.sleep(0.2)
        except Exception:
            pass

        item_12_remaining = self._count_item(acc, ITEM_12)
        item_442_count = self._count_item(acc, ITEM_442)
        item_441_count = self._count_item(acc, ITEM_441)

        if item_12_remaining >= 1 and item_442_count >= 2 and item_441_count >= 8:
            self._log(acc, f"{C.DIM}→ Ép ID 12 second: ID 12 + 2x ID 442 + 8x ID 441...{C.RESET}")

            # Clear combine UI trước: mở lại giao diện ép sao
            if not await self._open_ep_sao_trang_bi(acc, C):
                self._log(acc, f"{C.YELLOW}  Không mở được ép sao.{C.RESET}")
            else:
                ctrl = acc.controller
                indices = []
                # Tìm 1x ID 12, 2x ID 442, 8x ID 441
                for search_id, search_qty in [(ITEM_12, 1), (ITEM_442, 2), (ITEM_441, 8)]:
                    found = 0
                    for idx, item in enumerate(acc.char.arr_item_bag or []):
                        if item is not None and item.item_id == search_id:
                            if found < search_qty:
                                indices.append(idx)
                                found += 1

                self._log(acc, f"{C.DIM}  Gửi {len(indices)} indices: {indices}{C.RESET}")

                ctrl.combine_event.clear()
                ctrl.combine_result = ""
                await acc.service.send_combine_items(indices)
                await asyncio.sleep(0.3)

                ctrl.ui_menu_event.clear()
                try:
                    await asyncio.wait_for(ctrl.ui_menu_event.wait(), timeout=3.0)
                except asyncio.TimeoutError:
                    pass
                await asyncio.sleep(0.2)

                opts = ctrl.last_ui_options or []
                if opts:
                    confirm_idx = 0
                    for i, opt in enumerate(opts):
                        if "nâng cấp" in opt.lower() or "cần" in opt.lower():
                            confirm_idx = i
                            break
                    await acc.service.confirm_menu_npc(NPC_BA_HAT_MIT, confirm_idx)
                    await asyncio.sleep(0.5)
                    self._log(acc, f"{C.GREEN}  → ID 12 second: đã gửi nâng cấp.{C.RESET}")
                else:
                    self._log(acc, f"{C.YELLOW}  → ID 12 second: không có menu xác nhận.{C.RESET}")
        else:
            self._log(acc, f"{C.YELLOW}→ ID 12 second: thiếu nguyên liệu "
                       f"(12: {item_12_remaining}, 442: {item_442_count}/2, 441: {item_441_count}/8).{C.RESET}")

        if overall_ok:
            self._log(acc, f"{C.GREEN}→ Hoàn thành ép các item còn lại.{C.RESET}")
            return True

        self._log(acc, f"{C.YELLOW}→ Một số item không ép được (có thể thiếu nguyên liệu).{C.RESET}")
        return True  # Không coi là fail hoàn toàn, vì có thể thiếu item
