"""
Backward-compatible wrapper — re-export từ services.inventory.

Code cũ vẫn import được:
  from commands.setup.inventory_helpers import count_item, refresh_inventory

Code mới nên import trực tiếp từ services.inventory.
"""

from services.inventory import (  # noqa: F401
    count_item, find_item_index, find_item_indices, has_item,
    count_items_by_ids, refresh_inventory, InventoryService,
)

# Legacy constants (giữ nguyên để không break imports)
BEAN_ITEM_IDS = [13, 60, 61, 62, 63, 64, 65, 352, 523, 595]
BUA_ITEM_IDS = [213, 214, 215, 216, 217, 218, 219, 522, 671, 672]
SET_LIEN_HOAN_ITEMS = [1, 7, 22, 28, 12]
GIFTCODE_ITEM_IDS = (457, 381, 382, 383, 384, 385, 386)

# Legacy setup-specific helpers (vẫn giữ ở đây vì phụ thuộc setup logic)


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


# ── Item Usage Helpers ──
# use_item_for_master(): Sử dụng item bình thường hoặc cho sư phụ (type=4 hoặc type=0)
# use_item_for_pet():    Sử dụng item cho đệ tử (type=6)


async def use_item_for_master(acc, bag_index: int, log_func=None) -> bool:
    """
    Sử dụng item bình thường hoặc cho sư phụ.
    - Nếu là item tiêu hao: dùng use_item(type=0)
    - Nếu là trang bị: dùng get_item(type=4) để equip
    
    Args:
        acc: Account object
        bag_index: Index của item trong balo
        log_func: Hàm log (optional)
    Returns:
        True nếu thành công
    """
    from logs.logger_config import TerminalColors
    C = TerminalColors
    log = log_func or (lambda msg: None)
    
    try:
        # Thử dùng get_item(type=4) trước (equip cho sư phụ)
        await acc.service.get_item(4, bag_index)
        return True
    except Exception as e:
        log(f"{C.YELLOW}    get_item(4) thất bại: {e}, thử use_item...{C.RESET}")
        try:
            await acc.service.use_item(0, 1, bag_index, -1)
            return True
        except Exception as e2:
            log(f"{C.RED}    use_item cũng thất bại: {e2}{C.RESET}")
            return False


async def use_item_for_pet(acc, bag_index: int, log_func=None) -> bool:
    """
    Sử dụng item cho đệ tử (get_item type=6).
    
    Args:
        acc: Account object
        bag_index: Index của item trong balo
        log_func: Hàm log (optional)
    Returns:
        True nếu thành công
    """
    try:
        await acc.service.get_item(6, bag_index)
        return True
    except Exception as e:
        if log_func:
            from logs.logger_config import TerminalColors
            log_func(f"{TerminalColors.RED}Lỗi đưa item cho đệ tử: {e}{TerminalColors.RESET}")
        return False
