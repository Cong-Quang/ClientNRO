"""
Bước 10: Kích hoạt vật phẩm thưởng.
- Item 2000: Dùng tối đa 2 lần, chọn "Set Liên Hoàn" (kiểm tra đã đủ 2 set chưa)
- Các item kích hoạt đơn: 290, 1269, 1357, 1649, 1983, 1499, 1323 (dùng 1 lần mỗi item)
"""

import asyncio

from logs.logger_config import TerminalColors
from commands.setup.constants import (
    ITEM_2000, ITEM_2000_USE_TIMES,
    ITEM_UPGRADE_16_CRYSTAL, ITEM_UPGRADE_16, ITEM_12,
    ACTIVATE_ITEMS_ONCE, SET_LIEN_HOAN_ITEMS, SETS_NEEDED,
)
from commands.setup.inventory_helpers import count_item, count_set_lien_hoan, refresh_inventory


async def activate_items(acc, log_func) -> bool:
    """
    Kích hoạt các item thưởng:
    1. Item 2000 (x2, chọn Set Liên Hoàn) — kiểm tra balo trước, nếu đủ 2 set thì bỏ qua
    2. Các item kích hoạt đơn (dùng 1 lần mỗi item)
    """
    C = TerminalColors
    ctrl = acc.controller

    await refresh_inventory(acc)

    # ── Item 2000 ──
    await _activate_item_2000(acc, ctrl, log_func)

    # ── Các item kích hoạt đơn ──
    log_func(f"{C.DIM}→ Dùng item kích hoạt: {ACTIVATE_ITEMS_ONCE}...{C.RESET}")
    for item_id in ACTIVATE_ITEMS_ONCE:
        if not acc.is_logged_in:
            break
        await refresh_inventory(acc)

        count = count_item(acc, item_id)
        if count == 0:
            log_func(f"{C.YELLOW}→ Không có item {item_id}.{C.RESET}")
            continue

        log_func(f"{C.DIM}→ Dùng 1 item {item_id} (có {count})...{C.RESET}")
        for idx, item in enumerate(acc.char.arr_item_bag or []):
            if item is not None and item.item_id == item_id:
                try:
                    # Item 290 là cải trang → cần type=1 (đeo vào) thay vì type=0 (dùng)
                    if item_id == 290:
                        await acc.service.use_item(1, 1, idx, -1)
                        log_func(f"{C.GREEN}→ Đã mặc cải trang item {item_id}.{C.RESET}")
                    else:
                        await acc.service.use_item(0, 1, idx, -1)
                        log_func(f"{C.GREEN}→ Đã dùng item {item_id}.{C.RESET}")
                except Exception as e:
                    log_func(f"{C.RED}→ Lỗi xử lý item {item_id}: {e}{C.RESET}")
                break

    return True


async def _activate_item_2000(acc, ctrl, log_func):
    """
    Dùng item 2000, chọn "Set Liên Hoàn".
    Kiểm tra balo trước: nếu đã đủ 2 set thì bỏ qua.
    Mỗi lần mở item 2000 sẽ hiện menu với nhiều set, phải chọn đúng "Set Liên Hoàn".
    """
    C = TerminalColors

    # Kiểm tra trong balo đã có đủ 2 set chưa
    existing_sets = count_set_lien_hoan(acc)
    if existing_sets >= SETS_NEEDED:
        log_func(f"{C.GREEN}→ Đã có đủ {existing_sets} set trang bị Liên Hoàn trong balo, bỏ qua item 2000.{C.RESET}")
        return

    count_2000 = count_item(acc, ITEM_2000)
    if count_2000 <= 0:
        log_func(f"{C.YELLOW}→ Không có item 2000.{C.RESET}")
        return

    log_func(f"{C.DIM}→ Cần thêm {SETS_NEEDED - existing_sets} set (hiện có {existing_sets}), mở item 2000...{C.RESET}")

    sets_received = 0
    max_sets_needed = SETS_NEEDED - existing_sets

    for round_idx in range(min(count_2000, ITEM_2000_USE_TIMES)):
        if not acc.is_logged_in:
            break

        total_sets = existing_sets + sets_received
        if total_sets >= SETS_NEEDED:
            log_func(f"{C.GREEN}→ Đã đủ {SETS_NEEDED} set trang bị Liên Hoàn ({total_sets} set), không mở thêm.{C.RESET}")
            break

        item1_before = count_item(acc, ITEM_UPGRADE_16_CRYSTAL)
        log_func(f"{C.DIM}  Lần {round_idx + 1}: Đã có {total_sets}/{SETS_NEEDED} set, Item 1 trước = {item1_before}.{C.RESET}")

        item2000_success = False
        for retry in range(1, 4):
            if not acc.is_logged_in:
                break

            if retry > 1:
                log_func(f"{C.YELLOW}  Retry lần {retry}/3 mở item 2000...{C.RESET}")
                await asyncio.sleep(0.2)
                await refresh_inventory(acc)

            # Tìm và dùng item 2000
            found_item = -1
            for idx, item in enumerate(acc.char.arr_item_bag or []):
                if item is not None and item.item_id == ITEM_2000:
                    found_item = idx
                    break

            if found_item == -1:
                log_func(f"{C.YELLOW}  Hết item 2000 trong bag.{C.RESET}")
                item2000_success = True
                break

            # Dùng item 2000
            ctrl.ui_menu_event.clear()
            ctrl.last_npc_template_id = 0
            ctrl.last_ui_options = []
            try:
                log_func(f"{C.DIM}  Dùng item 2000 tại bag index {found_item}...{C.RESET}")
                await acc.service.use_item(0, 1, found_item, -1)
                await asyncio.sleep(0.4)

                try:
                    await asyncio.wait_for(ctrl.ui_menu_event.wait(), timeout=3.0)
                except asyncio.TimeoutError:
                    log_func(f"{C.YELLOW}    Timeout chờ menu item 2000.{C.RESET}")

                opts = ctrl.last_ui_options or []
                menu_npc = ctrl.last_npc_template_id
                log_func(f"{C.DIM}    Menu 2000: npc_id={menu_npc}, {len(opts)} options: {opts}{C.RESET}")

                # Tìm "Set Liên Hoàn"
                target_idx = -1
                for j, opt in enumerate(opts):
                    ol = opt.lower().replace('\n', ' ')
                    if "liên hoàn" in ol or "lien hoan" in ol or "lienhoan" in ol:
                        target_idx = j
                        log_func(f"{C.GREEN}    Tìm thấy 'Set Liên Hoàn' tại index {j}: '{opt}'.{C.RESET}")
                        break

                if target_idx != -1:
                    npc_to_use = menu_npc if menu_npc > 0 else 0
                    log_func(f"{C.DIM}    Chọn option {target_idx} với npc_id={npc_to_use}.{C.RESET}")
                    await acc.service.confirm_menu_npc(npc_to_use, target_idx)
                    await asyncio.sleep(1.0)

                    await refresh_inventory(acc)

                    item1_after = count_item(acc, ITEM_UPGRADE_16_CRYSTAL)
                    if item1_after > item1_before:
                        sets_received += 1
                        total_sets = existing_sets + sets_received
                        log_func(f"{C.GREEN}    ✓ Set Liên Hoàn #{sets_received}: Item 1 +{item1_after - item1_before} (tổng: {item1_after}).{C.RESET}")
                        item2000_success = True
                        if total_sets >= SETS_NEEDED:
                            log_func(f"{C.GREEN}    Đã đủ {SETS_NEEDED} set ({total_sets}), dừng mở item 2000.{C.RESET}")
                            break
                    else:
                        log_func(f"{C.YELLOW}    Item 1 không tăng (trước={item1_before}, sau={item1_after}), thử lại.{C.RESET}")
                else:
                    log_func(f"{C.RED}    Không tìm thấy 'Set Liên Hoàn' trong menu! Options: {opts}{C.RESET}")
                    log_func(f"{C.YELLOW}    => Không chọn option nào để tránh mất item 2000.{C.RESET}")
            except Exception as e:
                log_func(f"{C.RED}    Lỗi: {e}.{C.RESET}")

        if not item2000_success:
            log_func(f"{C.YELLOW}  Không mở được Set Liên Hoàn sau retry.{C.RESET}")

        item16_count = count_item(acc, ITEM_UPGRADE_16)
        item1_count = count_item(acc, ITEM_UPGRADE_16_CRYSTAL)
        log_func(f"{C.DIM}  Sau lần {round_idx + 1}: Đã có {existing_sets + sets_received} set, Item 1={item1_count}, Item 16={item16_count}.{C.RESET}")

    # Tổng kết
    total_final = existing_sets + sets_received
    if total_final >= SETS_NEEDED:
        log_func(f"{C.GREEN}→ Đã nhận đủ {total_final} set trang bị Liên Hoàn.{C.RESET}")
    elif sets_received > 0:
        log_func(f"{C.YELLOW}→ Nhận thêm {sets_received} set, tổng {total_final}/{SETS_NEEDED}.{C.RESET}")
