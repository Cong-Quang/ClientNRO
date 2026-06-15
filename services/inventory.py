"""
InventoryService — Service tái sử dụng cho mọi thao tác kiểm tra hành trang (inventory).

Không phụ thuộc vào setup accounts, có thể dùng từ bất kỳ module nào.

Cách dùng:
  # Cách 1: Dùng class (khuyến nghị)
  svc = InventoryService(acc, log_func)
  count = svc.count_item(item_id=16)
  await svc.refresh()

  # Cách 2: Dùng free functions (backward compatible)
  from services.inventory import count_item, refresh_inventory
  count = count_item(acc, item_id=16)
  await refresh_inventory(acc)
"""

import asyncio
from typing import Callable, Optional


# ═══════════════════════════════════════════════
# FREE FUNCTIONS (backward compatible)
# ═══════════════════════════════════════════════


def count_item(acc, item_id: int) -> int:
    """Đếm số lượng item theo ID trong balo (free function)."""
    count = 0
    for item in acc.char.arr_item_bag or []:
        if item is not None and item.item_id == item_id:
            count += item.quantity
    return count


def find_item_index(acc, item_id: int) -> int:
    """Tìm index đầu tiên của item trong balo. Trả về -1 nếu không."""
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


def count_items_by_ids(acc, item_ids: list[int]) -> dict[int, int]:
    """Đếm số lượng nhiều item IDs cùng lúc. Trả về {item_id: count}."""
    counts = {iid: 0 for iid in item_ids}
    for item in acc.char.arr_item_bag or []:
        if item is not None and item.item_id in counts:
            counts[item.item_id] += item.quantity
    return counts


async def refresh_inventory(acc):
    """Refresh lại thông tin inventory từ server (free function)."""
    try:
        acc.controller.me_load_all_event.clear()
        await acc.service.request_me_info()
        await asyncio.wait_for(acc.controller.me_load_all_event.wait(), timeout=1.5)
    except Exception:
        # Fallback to a tiny sleep in case of failure/timeout
        await asyncio.sleep(0.05)


# ═══════════════════════════════════════════════
# CLASS
# ═══════════════════════════════════════════════


class InventoryService:
    """Dịch vụ thao tác với hành trang — tái sử dụng cho mọi module."""

    def __init__(self, acc, log_func: Optional[Callable] = None):
        """
        Args:
            acc: Account object
            log_func: Hàm log(msg) tùy chọn
        """
        self.acc = acc
        self.log = log_func or (lambda msg: None)

    # ═══════════════════════════════════════════════
    # ĐẾM / TÌM ITEM
    # ═══════════════════════════════════════════════

    def count_item(self, item_id: int) -> int:
        """Đếm số lượng item theo ID trong balo."""
        return count_item(self.acc, item_id)

    def find_item_index(self, item_id: int) -> int:
        """Tìm index đầu tiên của item trong balo. Trả về -1 nếu không tìm thấy."""
        return find_item_index(self.acc, item_id)

    def find_item_indices(self, item_id: int, quantity: int = 1) -> list[int]:
        """Tìm nhiều index của item trong balo."""
        return find_item_indices(self.acc, item_id, quantity)

    def has_item(self, item_id: int) -> bool:
        """Kiểm tra có item trong balo không."""
        return has_item(self.acc, item_id)

    def count_items_by_ids(self, item_ids: list[int]) -> dict[int, int]:
        """Đếm số lượng nhiều item IDs cùng lúc. Trả về {item_id: count}."""
        return count_items_by_ids(self.acc, item_ids)

    # ═══════════════════════════════════════════════
    # REFRESH
    # ═══════════════════════════════════════════════

    async def refresh(self):
        """Refresh lại thông tin inventory từ server."""
        await refresh_inventory(self.acc)
