"""
Bước 13: Mặc đồ cho sư phụ.

Chỉ equip các item thưởng (accessories) — KHÔNG equip set items (1,7,22,28,12)
vì get_item(type=4) làm mất items khỏi balo mà không equip được lên body.
Set items sẽ được giữ lại trong balo để đưa cho đệ tử ở Step 14.
"""

import asyncio

from logs.logger_config import TerminalColors
from commands.setup.inventory_helpers import refresh_inventory, use_item_for_master

# Chỉ equip các item thưởng (accessories), KHÔNG phải set items
MASTER_EQUIP_ITEMS = [290, 1269, 1357, 1649, 1983, 1499, 1323]


async def equip_master(acc, log_func, C=None) -> bool:
    """
    Mặc đồ cho sư phụ: chỉ equip các item thưởng (accessories).
    Set items (1,7,22,28,12) được giữ lại trong balo cho đệ tử.
    """
    if C is None:
        C = TerminalColors

    await refresh_inventory(acc)

    all_ok = True
    for item_id in MASTER_EQUIP_ITEMS:
        if not acc.is_logged_in:
            return False

        await refresh_inventory(acc)

        # Kiểm tra xem sư phụ đã mặc item này chưa
        already_equipped = False
        body_items = getattr(acc.char, 'arr_item_body', None) or []
        for item in body_items:
            if item is not None and item.item_id == item_id:
                already_equipped = True
                break

        if already_equipped:
            log_func(f"{C.GREEN}  → Item {item_id}: Sư phụ đã mặc trên người.{C.RESET}")
            continue

        # Tìm item trong balo
        found_idx = -1
        for idx, item in enumerate(acc.char.arr_item_bag or []):
            if item is not None and item.item_id == item_id:
                found_idx = idx
                break

        if found_idx < 0:
            log_func(f"{C.YELLOW}  → Item {item_id}: không có trong balo, bỏ qua.{C.RESET}")
            continue

        log_func(f"{C.DIM}  → Equip Item {item_id} (idx {found_idx}) cho sư phụ...{C.RESET}")
        ok = await use_item_for_master(acc, found_idx, log_func)
        if ok:
            await asyncio.sleep(0.01)
            log_func(f"{C.GREEN}    ✓ Đã equip Item {item_id}.{C.RESET}")
        else:
            log_func(f"{C.RED}    ✗ Lỗi equip Item {item_id}.{C.RESET}")
            all_ok = False

    await refresh_inventory(acc)
    log_func(f"{C.DIM}→ Equip xong. Kiểm tra body items...{C.RESET}")

    # In ra items đã equip trên body
    body_items = getattr(acc.char, 'arr_item_body', None) or []
    if body_items:
        for idx, item in enumerate(body_items):
            if item is not None:
                log_func(f"{C.DIM}  Body[{idx}]: Item {item.item_id} - {item.info or ''}{C.RESET}")

    if all_ok:
        log_func(f"{C.GREEN}→ Đã mặc đồ cho sư phụ.{C.RESET}")
    else:
        log_func(f"{C.YELLOW}→ Một số item không equip được.{C.RESET}")

    return True
