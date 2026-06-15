"""
Bước 9: Dùng item hỗ trợ.
- Item 1182: Dùng để nhận item 441 (mục tiêu >= 20)
- Item 1680: Dùng 1 lần
"""

import asyncio

from logs.logger_config import TerminalColors
from commands.setup.constants import ITEM_1182, ITEM_441, ITEM_1680
from commands.setup.inventory_helpers import count_item, refresh_inventory


async def use_support_items(acc, log_func) -> bool:
    """
    Dùng item hỗ trợ:
    - Item 1182: Dùng để nhận item 441. Nếu item 441 < 20, dùng 1182 cho đến khi đủ.
    - Item 1680: Nếu còn trong balo, dùng 1 lần.
    """
    C = TerminalColors

    await refresh_inventory(acc)

    item_441_qty = count_item(acc, ITEM_441)
    item_1182_qty = count_item(acc, ITEM_1182)

    # Dùng item 1182 để có item 441
    if item_441_qty < 20 and item_1182_qty > 0:
        need = 20 - item_441_qty
        use_count = min(item_1182_qty, need * 2)  # Dùng gấp đôi để đảm bảo
        log_func(f"{C.DIM}→ Dùng tối đa {use_count} item 1182 để có item 441 ({item_441_qty}/20)...{C.RESET}")

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

        await refresh_inventory(acc)
        item_441_qty = count_item(acc, ITEM_441)

        if item_441_qty >= 20:
            log_func(f"{C.GREEN}→ Đã đủ item 441 ({item_441_qty}).{C.RESET}")
        else:
            log_func(f"{C.YELLOW}→ Item 441: {item_441_qty}/20 (có thể hết item 1182).{C.RESET}")
    elif item_441_qty >= 20:
        log_func(f"{C.GREEN}→ Đã có đủ item 441 ({item_441_qty}).{C.RESET}")
    else:
        log_func(f"{C.YELLOW}→ Không có item 1182 và item 441 < 20.{C.RESET}")

    # Dùng item 1680 (nếu còn)
    item_1680_qty = count_item(acc, ITEM_1680)
    if item_1680_qty > 0:
        log_func(f"{C.DIM}→ Dùng 1 item 1680...{C.RESET}")
        for i, item in enumerate(acc.char.arr_item_bag or []):
            if item is not None and item.item_id == ITEM_1680:
                try:
                    await acc.service.use_item(0, 1, i, -1)
                    await asyncio.sleep(0.3)
                    log_func(f"{C.GREEN}→ Đã dùng item 1680.{C.RESET}")
                except Exception as e:
                    log_func(f"{C.RED}→ Lỗi dùng item 1680: {e}{C.RESET}")
                break
    else:
        log_func(f"{C.YELLOW}→ Không có item 1680 trong balo.{C.RESET}")

    return True
