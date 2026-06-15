"""
Tiện ích thao tác với hành trang (inventory).
Cung cấp các hàm đếm item, kiểm tra item, tìm item trong balo.
Có thể tái sử dụng từ bất kỳ module nào.
"""

import asyncio


# ── Constants cụ thể của setup ──
BEAN_ITEM_IDS = [13, 60, 61, 62, 63, 64, 65, 352, 523, 595]
BUA_ITEM_IDS = [213, 214, 215, 216, 217, 218, 219, 522, 671, 672]
SET_LIEN_HOAN_ITEMS = [1, 7, 22, 28, 12]
GIFTCODE_ITEM_IDS = (457, 381, 382, 383, 384, 385, 386)


# ── Hàm đếm / tìm item ──

def count_item(acc, item_id: int) -> int:
    """Đếm số lượng item theo ID trong balo."""
    count = 0
    for item in acc.char.arr_item_bag or []:
        if item is not None and item.item_id == item_id:
            count += item.quantity
    return count


def find_item_index(acc, item_id: int) -> int:
    """Tìm index đầu tiên của item trong balo. Trả về -1 nếu không tìm thấy."""
    for idx, item in enumerate(acc.char.arr_item_bag or []):
        if item is not None and item.item_id == item_id:
            return idx
    return -1


def find_item_indices(acc, item_id: int, quantity: int = 1) -> list[int]:
    """Tìm nhiều index của item trong balo."""
    indices = []
    for idx, item in enumerate(acc.char.arr_item_bag or []):
        if item is not None and item.item_id == item_id:
            indices.append(idx)
            if len(indices) >= quantity:
                break
    return indices


def has_item(acc, item_id: int) -> bool:
    """Kiểm tra có item trong balo không."""
    for item in acc.char.arr_item_bag or []:
        if item is not None and item.item_id == item_id:
            return True
    return False


def count_item_by_ids(acc, item_ids: list[int]) -> dict[int, int]:
    """Đếm số lượng nhiều item IDs cùng lúc. Trả về {item_id: count}."""
    counts = {iid: 0 for iid in item_ids}
    for item in acc.char.arr_item_bag or []:
        if item is not None and item.item_id in counts:
            counts[item.item_id] += item.quantity
    return counts


async def refresh_inventory(acc):
    """Refresh lại thông tin inventory từ server."""
    try:
        await acc.service.request_me_info()
        await asyncio.sleep(0.3)
    except Exception:
        pass


# ── Hàm cụ thể của setup ──

def count_beans(acc) -> int:
    """Đếm tổng số đậu thần trong balo."""
    count = 0
    for item in acc.char.arr_item_bag or []:
        if item is not None and item.item_id in BEAN_ITEM_IDS:
            count += item.quantity
    return count


def has_giftcode_items(acc) -> bool:
    """Kiểm tra có item giftcode trong balo không."""
    for item in acc.char.arr_item_bag or []:
        if item is not None and item.item_id in GIFTCODE_ITEM_IDS:
            return True
    return False


def count_bua_items(acc) -> int:
    """Đếm số loại bùa đã có trong balo."""
    found = set()
    for item in acc.char.arr_item_bag or []:
        if item is not None and item.item_id in BUA_ITEM_IDS:
            found.add(item.item_id)
    return len(found)


def count_set_lien_hoan(acc) -> int:
    """Đếm số set trang bị Liên Hoàn (min của items 1,16,22,28,12)."""
    counts = [count_item(acc, item_id) for item_id in SET_LIEN_HOAN_ITEMS]
    return min(counts) if counts else 0
