"""
Bước 11 & 12: Ép sao trang bị tại Bà Hạt Mít (Đảo Kame).

Step 11: Ép Item 16 (x11 lần, mỗi lần 1x Item 16 + 2x Item 1)
Step 12: Ép trang bị (items 1, 7, 22, 28, 12)
  - Set 1: mỗi trang bị ép với Item 16 (x10 lần mỗi món)
  - Set 2: Item 12 đặc biệt — 12 + 2x 442 + 8x 441

Dùng CombineHelper để tái sử dụng.
"""

import asyncio

from logs.logger_config import TerminalColors
from commands.setup.constants import (
    MAP_DAO_KAME, NPC_BA_HAT_MIT,
    ITEM_UPGRADE_16, ITEM_UPGRADE_16_CRYSTAL, ITEM_UPGRADE_16_TIMES,
    ITEM_12, ITEM_442, ITEM_441, ITEM_EQUIP, UPGRADE_TIMES_PER_PIECE,
)
from commands.setup.inventory_helpers import count_item, refresh_inventory
from commands.setup.combine_helper import CombineHelper


# ── STEP 11: Ép Item 16 ──

async def upgrade_item_16(acc, log_func, C=None) -> bool:
    """
    Ép Item 16: 1x Item 16 + 2x Item 1 → Item 16 upgraded.
    Check đã đủ 11 sao chưa, nếu đủ thì bỏ qua.
    """
    if C is None:
        C = TerminalColors

    helper = CombineHelper(acc, log_func)

    # Check đã ép đủ chưa
    if helper.is_fully_upgraded(ITEM_UPGRADE_16, ITEM_UPGRADE_16_TIMES):
        stars = helper.get_item_stars(ITEM_UPGRADE_16)
        log_func(f"{C.GREEN}→ Item 16 đã đủ {stars} sao, bỏ qua.{C.RESET}")
        return True

    if not await helper.open_combine():
        return False

    await refresh_inventory(acc)

    item16_count = helper.count_item(ITEM_UPGRADE_16)
    item1_count = helper.count_item(ITEM_UPGRADE_16_CRYSTAL)
    current_stars = helper.get_item_stars(ITEM_UPGRADE_16)

    log_func(f"{C.DIM}→ Item 16: {item16_count} (sao: {current_stars}/{ITEM_UPGRADE_16_TIMES}), Item 1: {item1_count}.{C.RESET}")

    if item16_count == 0:
        log_func(f"{C.YELLOW}→ Không có Item 16.{C.RESET}")
        return True

    need = ITEM_UPGRADE_16_TIMES - current_stars
    if need <= 0:
        log_func(f"{C.GREEN}→ Item 16 đã đủ sao.{C.RESET}")
        return True

    max_up = min(need, item16_count, item1_count // 2)
    if max_up <= 0:
        log_func(f"{C.YELLOW}→ Không đủ Item 1 (cần {need * 2}, có {item1_count}).{C.RESET}")
        return False

    log_func(f"{C.DIM}→ Ép Item 16 x{max_up} lần (cần thêm {need} sao)...{C.RESET}")

    done = await helper.do_combine(
        main_item_id=ITEM_UPGRADE_16,
        materials=[(ITEM_UPGRADE_16_CRYSTAL, 2)],
        max_times=max_up,
    )

    if done > 0:
        log_func(f"{C.GREEN}→ Item 16: xong {done}/{max_up} lần.{C.RESET}")
        return True
    log_func(f"{C.RED}→ Không ép được Item 16.{C.RESET}")
    return False


# ── STEP 12: Ép trang bị ──

async def upgrade_other_items(acc, log_func, C=None) -> bool:
    """
    Ép trang bị (items 1, 7, 22, 28, 12):
    - Set 1: mỗi trang bị ép với Item 16 (x10 lần mỗi món)
    - Set 2: Item 12 đặc biệt — 12 + 2x 442 + 8x 441
    Check đã đủ sao chưa trước khi ép.
    """
    if C is None:
        C = TerminalColors

    helper = CombineHelper(acc, log_func)
    overall_ok = True

    # ── Set 1: Ép từng trang bị với Item 16 ──
    for item_id in ITEM_EQUIP:
        if not acc.is_logged_in:
            return False

        # Check đã ép đủ chưa
        if helper.is_fully_upgraded(item_id, UPGRADE_TIMES_PER_PIECE):
            stars = helper.get_item_stars(item_id)
            log_func(f"{C.GREEN}→ Item {item_id} đã đủ {stars} sao, bỏ qua.{C.RESET}")
            continue

        item_count = helper.count_item(item_id)
        item16_count = helper.count_item(ITEM_UPGRADE_16)
        current_stars = helper.get_item_stars(item_id)

        if item_count < 1:
            log_func(f"{C.YELLOW}→ Item {item_id}: không có.{C.RESET}")
            continue

        need = UPGRADE_TIMES_PER_PIECE - current_stars
        if need <= 0:
            log_func(f"{C.GREEN}→ Item {item_id} đã đủ sao ({current_stars}).{C.RESET}")
            continue

        max_up = min(need, item_count, item16_count)
        if max_up <= 0:
            log_func(f"{C.YELLOW}→ Item {item_id}: thiếu Item 16 ({item16_count}), sao: {current_stars}/{UPGRADE_TIMES_PER_PIECE}.{C.RESET}")
            continue

        if not await helper.open_combine():
            log_func(f"{C.RED}→ Không mở được ép sao cho item {item_id}.{C.RESET}")
            overall_ok = False
            continue

        log_func(f"{C.DIM}→ Ép item {item_id} x{max_up} lần (sao: {current_stars}/{UPGRADE_TIMES_PER_PIECE}, item:{item_count}, 16:{item16_count})...{C.RESET}")

        done = await helper.do_combine(
            main_item_id=item_id,
            materials=[(ITEM_UPGRADE_16, 1)],
            max_times=max_up,
        )

        if done > 0:
            log_func(f"{C.GREEN}  → Item {item_id}: xong {done} lần.{C.RESET}")
        else:
            overall_ok = False
            log_func(f"{C.YELLOW}  → Item {item_id}: không ép được.{C.RESET}")

        if not acc.is_logged_in:
            return False

    # ── Set 2: Item 12 đặc biệt (12 + 2x 442 + 8x 441) ──
    if not acc.is_logged_in:
        return False

    await refresh_inventory(acc)

    item12_count = helper.count_item(ITEM_12)
    item442_count = helper.count_item(ITEM_442)
    item441_count = helper.count_item(ITEM_441)

    if item12_count < 1 or item442_count < 2 or item441_count < 8:
        log_func(f"{C.YELLOW}→ Set 2 Item 12: thiếu "
                   f"(12:{item12_count}, 442:{item442_count}/2, 441:{item441_count}/8).{C.RESET}")
    else:
        if not await helper.open_combine():
            log_func(f"{C.RED}→ Không mở được ép sao cho Set 2 Item 12.{C.RESET}")
        else:
            log_func(f"{C.DIM}→ Set 2 Item 12: 12 + 442x2 + 441x8...{C.RESET}")

            ctrl = acc.controller
            indices = []
            for search_id, search_qty in [(ITEM_12, 1), (ITEM_442, 2), (ITEM_441, 8)]:
                found = 0
                for idx, item in enumerate(acc.char.arr_item_bag or []):
                    if item is not None and item.item_id == search_id:
                        if found < search_qty:
                            indices.append(idx)
                            found += 1

            log_func(f"{C.DIM}  Gửi {len(indices)} items: {indices}{C.RESET}")

            ctrl.combine_event.clear()
            ctrl.combine_result = ""
            ctrl.ui_menu_event.clear()
            await acc.service.send_combine_items(indices)
            await asyncio.sleep(0.5)

            try:
                await asyncio.wait_for(ctrl.ui_menu_event.wait(), timeout=3.0)
            except asyncio.TimeoutError:
                pass
            await asyncio.sleep(0.3)

            opts = ctrl.last_ui_options or []
            if opts:
                confirm_idx = 0
                for i, opt in enumerate(opts):
                    if "nâng cấp" in opt.lower() or "cần" in opt.lower():
                        confirm_idx = i
                        break
                ctrl.combine_event.clear()
                ctrl.combine_result = ""
                await acc.service.confirm_menu_npc(NPC_BA_HAT_MIT, confirm_idx)
                try:
                    await asyncio.wait_for(ctrl.combine_event.wait(), timeout=5.0)
                except asyncio.TimeoutError:
                    pass
                await asyncio.sleep(0.3)
                log_func(f"{C.GREEN}  → Set 2 Item 12: {ctrl.combine_result}.{C.RESET}")
            else:
                log_func(f"{C.YELLOW}  → Set 2 Item 12: không có menu.{C.RESET}")

    # ── Tổng kết ──
    helper.print_status(ITEM_EQUIP, UPGRADE_TIMES_PER_PIECE)

    if overall_ok:
        log_func(f"{C.GREEN}→ Hoàn thành ép trang bị.{C.RESET}")
    else:
        log_func(f"{C.YELLOW}→ Một số item không ép được.{C.RESET}")
    return True
