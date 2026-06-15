"""
Bước 4 & 5: Mở NPC Muri và nhận thưởng.
- Step 4: Teleport tới NPC Ông Muri và mở menu
- Step 5: Nhận vàng miễn phí → ngọc miễn phí → giftcode → đệ tử miễn phí
"""

import asyncio

from logs.logger_config import TerminalColors
from commands.setup.constants import HOME_NPC
from commands.setup.navigation_helpers import teleport_to_npc, go_home, open_menu_npc
from commands.setup.inventory_helpers import has_giftcode_items


async def open_muri(acc, log_func) -> bool:
    """Teleport tới NPC Ông Muri và mở menu."""
    C = TerminalColors
    npc_id = HOME_NPC.get(acc.char.gender, 2)

    if not await teleport_to_npc(acc, npc_id):
        log_func(f"{C.YELLOW}→ Không tìm thấy NPC (template={npc_id}).{C.RESET}")
        await go_home(acc, log_func)
        await asyncio.sleep(1)
        if not await teleport_to_npc(acc, npc_id):
            log_func(f"{C.RED}→ Vẫn không tìm thấy NPC.{C.RESET}")
            return False

    ctrl = acc.controller
    ctrl.ui_menu_event.clear()
    await acc.service.open_menu_npc(npc_id)
    try:
        await asyncio.wait_for(ctrl.ui_menu_event.wait(), timeout=3.0)
    except asyncio.TimeoutError:
        pass
    await asyncio.sleep(0.2)

    opts = ctrl.last_ui_options or []
    log_func(f"{C.DIM}→ Menu NPC: {opts}{C.RESET}")
    if not opts:
        log_func(f"{C.YELLOW}→ Menu rỗng, thử mở lại...{C.RESET}")
        return False

    return True


async def claim_rewards(acc, state_mgr, log_func, force: bool) -> bool:
    """
    Nhận thưởng: vàng miễn phí → ngọc miễn phí → giftcode → đệ tử miễn phí.
    Kiểm tra state_mgr để tránh nhận trùng.
    """
    C = TerminalColors
    npc_id = HOME_NPC.get(acc.char.gender, 2)

    if not await teleport_to_npc(acc, npc_id):
        log_func(f"{C.YELLOW}→ Không tìm thấy NPC để nhận thưởng.{C.RESET}")
        return False

    # ── Nhận vàng miễn phí ──
    if force or not state_mgr.get(acc.username).gold_claimed:
        log_func(f"{C.DIM}→ Nhận vàng miễn phí...{C.RESET}")
        await _claim_gold(acc, log_func)
        state_mgr.set_attribute(acc.username, gold_claimed=True)
    else:
        log_func(f"{C.GREEN}→ Đã nhận vàng trước đó.{C.RESET}")

    from commands.setup.retry_utils import retry_operation, RetryConfig
    from commands.setup.constants import STEP_CLAIM_REWARDS
    # Kiểm tra đăng nhập lại
    if not acc.is_logged_in:
        return False

    # ── Nhận ngọc miễn phí ──
    if force or not state_mgr.get(acc.username).gem_claimed:
        log_func(f"{C.DIM}→ Nhận ngọc miễn phí...{C.RESET}")
        await _claim_gem(acc, npc_id, log_func)
        state_mgr.set_attribute(acc.username, gem_claimed=True)
    else:
        log_func(f"{C.GREEN}→ Đã nhận ngọc trước đó.{C.RESET}")

    if not acc.is_logged_in:
        return False

    # ── Giftcode ──
    from commands.setup.step_giftcode import submit_giftcode
    if force or not state_mgr.get(acc.username).giftcode_done:
        has_gift = has_giftcode_items(acc)
        if has_gift and not force:
            log_func(f"{C.GREEN}→ Đã có item giftcode, bỏ qua.{C.RESET}")
        else:
            from commands.setup.constants import GIFTCODES
            for code in GIFTCODES:
                if not acc.is_logged_in:
                    return False
                await submit_giftcode(acc, npc_id, code, log_func)
        state_mgr.set_attribute(acc.username, giftcode_done=True)
    else:
        log_func(f"{C.GREEN}→ Đã nhập giftcode trước đó.{C.RESET}")

    if not acc.is_logged_in:
        return False

    # ── Nhận đệ tử miễn phí ──
    if force or not state_mgr.get(acc.username).disciple_claimed:
        log_func(f"{C.DIM}→ Nhận đệ tử miễn phí...{C.RESET}")
        await _claim_disciple(acc, npc_id, log_func)
        state_mgr.set_attribute(acc.username, disciple_claimed=True)
    else:
        log_func(f"{C.GREEN}→ Đã nhận đệ tử trước đó.{C.RESET}")

    return True


async def _claim_gold(acc, log_func):
    """Nhận vàng từ NPC nhà."""
    C = TerminalColors
    ctrl = acc.controller
    home_npc = HOME_NPC.get(acc.char.gender, 2)

    for attempt in range(1, 4):
        if not acc.is_logged_in:
            return

        if attempt > 1:
            log_func(f"{C.YELLOW}→ Retry nhận vàng lần {attempt}/3...{C.RESET}")
            await asyncio.sleep(1)

        gold_before = getattr(acc.char, 'xu', 0)

        if not await teleport_to_npc(acc, home_npc, y_offset=-1):
            log_func(f"{C.YELLOW}→ Không tìm thấy NPC nhà.{C.RESET}")
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
            log_func(f"{C.DIM}→ Chọn nhận vàng ở vị trí {gold_opt_idx}.{C.RESET}")
            await acc.service.confirm_menu_npc(home_npc, gold_opt_idx)
            await asyncio.sleep(1.0)

            try:
                await acc.service.request_me_info()
                await asyncio.sleep(0.5)
            except Exception:
                pass

            gold_after = getattr(acc.char, 'xu', 0)
            if gold_after > gold_before:
                log_func(f"{C.GREEN}→ Nhận vàng: +{gold_after - gold_before} (tổng: {gold_after}).{C.RESET}")
                return
            elif gold_after > 0:
                log_func(f"{C.GREEN}→ Vàng hiện tại: {gold_after}.{C.RESET}")
                return
        else:
            log_func(f"{C.YELLOW}→ Không tìm thấy tùy chọn vàng (options: {opts}).{C.RESET}")
            break

    log_func(f"{C.YELLOW}→ Không nhận được vàng (có thể đã nhận trước).{C.RESET}")


async def _claim_gem(acc, npc_id, log_func):
    """Nhận ngọc xanh miễn phí từ NPC nhà."""
    C = TerminalColors
    ctrl = acc.controller

    if not await teleport_to_npc(acc, npc_id):
        log_func(f"{C.YELLOW}→ Không tìm thấy NPC.{C.RESET}")
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
        log_func(f"{C.DIM}→ Chọn nhận ngọc xanh ở vị trí {gem_opt_idx}.{C.RESET}")
        await acc.service.confirm_menu_npc(npc_id, gem_opt_idx)
        await asyncio.sleep(0.5)
        log_func(f"{C.GREEN}→ Đã nhận ngọc xanh.{C.RESET}")
    else:
        log_func(f"{C.YELLOW}→ Không tìm thấy tùy chọn ngọc, dùng option 2.{C.RESET}")
        await acc.service.confirm_menu_npc(npc_id, 2)
        await asyncio.sleep(0.5)


async def _claim_disciple(acc, npc_id, log_func):
    """Nhận đệ tử miễn phí từ NPC nhà."""
    C = TerminalColors
    ctrl = acc.controller

    if acc.char.have_pet or acc.pet.have_pet:
        log_func(f"{C.GREEN}→ Đã có đệ tử.{C.RESET}")
        return

    if not await teleport_to_npc(acc, npc_id):
        log_func(f"{C.YELLOW}→ Không tìm thấy NPC.{C.RESET}")
        return

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
        log_func(f"{C.YELLOW}→ Không tìm thấy tùy chọn đệ tử (options: {opts}).{C.RESET}")
        return

    ctrl.ui_menu_event.clear()
    await acc.service.confirm_menu_npc(npc_id, disciple_opt)
    try:
        await asyncio.wait_for(ctrl.ui_menu_event.wait(), timeout=3.0)
    except asyncio.TimeoutError:
        pass
    await asyncio.sleep(0.5)

    # Nếu có menu con thì chọn tiếp
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
        log_func(f"{C.GREEN}→ Nhận đệ tử thành công.{C.RESET}")
    else:
        log_func(f"{C.YELLOW}→ Có thể chưa nhận được đệ tử (server chưa cập nhật).{C.RESET}")
