"""
Bước 13: Mặc đồ cho sư phụ.

Chỉ equip trang bị đã ép (có option 102 > 0 hoặc option 95/96 cho rada).
Không equip đồ mặc định chưa ép.
"""

import asyncio

from logs.logger_config import TerminalColors
from commands.setup.constants import ITEM_EQUIP
from commands.setup.inventory_helpers import count_item, refresh_inventory
from services.combine_service import CombineService, is_item_upgraded, is_item_fully_upgraded


async def equip_master(acc, log_func, C=None) -> bool:
    """
    Mặc đồ cho sư phụ: tìm bản sao đã ép của mỗi item và equip lên body.
    Chỉ equip items đã ép (có option 102 hoặc 95/96).
    """
    if C is None:
        C = TerminalColors

    await refresh_inventory(acc)
    svc = CombineService(acc, log_func)

    items_to_equip = ITEM_EQUIP

    all_ok = True
    for item_id in items_to_equip:
        if not acc.is_logged_in:
            return False

        # Kiểm tra xem sư phụ đã mặc bản FULL upgrade này chưa trên người
        already_equipped = False
        body_items = getattr(acc.char, 'arr_item_body', None) or []
        for item in body_items:
            if item is not None and item.item_id == item_id and is_item_fully_upgraded(item):
                already_equipped = True
                break

        if already_equipped:
            log_func(f"{C.GREEN}  → Item {item_id}: Sư phụ đã mặc bản đã ép trên người.{C.RESET}")
            continue

        # Tìm bản sao đã ép trong balo
        found_idx = -1
        for idx, item in enumerate(acc.char.arr_item_bag or []):
            if item is not None and item.item_id == item_id and is_item_fully_upgraded(item):
                found_idx = idx
                break

        if found_idx < 0:
            log_func(f"{C.YELLOW}  → Item {item_id}: không tìm thấy bản ép full trong balo. Thử tìm bản ép thường...{C.RESET}")
            for idx, item in enumerate(acc.char.arr_item_bag or []):
                if item is not None and item.item_id == item_id and is_item_upgraded(item):
                    found_idx = idx
                    break
        # Fallback cuối: mặc bất kỳ bản nào (kể cả chưa ép)
        # Đảm bảo sư phụ luôn có đồ dù upgrade chưa chạy
        if found_idx < 0:
            log_func(f"{C.YELLOW}  → Item {item_id}: không tìm thấy bản đã ép. Lấy bản chưa ép làm fallback...{C.RESET}")
            for idx, item in enumerate(acc.char.arr_item_bag or []):
                if item is not None and item.item_id == item_id:
                    found_idx = idx
                    break
            if found_idx < 0:
                log_func(f"{C.YELLOW}  → Item {item_id}: không có trong balo, bỏ qua.{C.RESET}")
                continue

        # Equip: type=0 (sử dụng), where=1 (bản thân)
        # 🔴 QUAN TRỌNG: type=1 là "đeo vào" (dùng cho cải trang), type=0 là "sử dụng" (mặc đồ cho sư phụ)
        log_func(f"{C.DIM}  → Equip Item {item_id} (idx {found_idx}) đã ép...{C.RESET}")
        try:
            await acc.service.use_item(0, 1, found_idx, -1)
            await asyncio.sleep(0.15)
            log_func(f"{C.GREEN}    ✓ Đã equip Item {item_id}.{C.RESET}")
        except Exception as e:
            log_func(f"{C.RED}    ✗ Lỗi equip Item {item_id}: {e}{C.RESET}")
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
