"""
Nhập giftcode — Wrapper tương thích ngược cho setup accounts.

Tái export từ services.giftcode_service.
Các module mới nên import trực tiếp từ services.giftcode_service.
"""

from services.giftcode_service import GiftcodeService

# ── Từ khóa nhận diện phản hồi giftcode ──
GIFTCODE_KEYWORDS = [
    "thành công", "chúc mừng", "nhận được", "tặng", "giftcode",
    "đã sử dụng", "da su dung", "hết hạn", "het han",
    "không tồn tại", "khong ton tai", "sai mã", "mã quà",
]


# ── Hàm tương thích ngược ──

async def wait_giftcode_response(acc, ctrl, log_func, timeout: float = 5.0):
    """Tương thích ngược: gọi GiftcodeService.wait_response."""
    log_func = log_func or (lambda msg: None)
    svc = GiftcodeService(acc, log_func)
    svc.ctrl = ctrl  # Override controller
    return await svc.wait_response(timeout)


async def check_giftcode_items(acc, log_func):
    """Tương thích ngược: gọi GiftcodeService.check_reward_items."""
    svc = GiftcodeService(acc, log_func)
    await svc.check_reward_items()


async def submit_giftcode(acc, npc_id: int, code: str, log_func) -> bool:
    """Tương thích ngược: gọi GiftcodeService.submit_giftcode.
    Returns True nếu thành công hoặc đã dùng.
    """
    svc = GiftcodeService(acc, log_func)
    status = await svc.submit_giftcode(code, npc_id=npc_id)
    return status in ("success", "used")


async def _submit_giftcode_santa(acc, code: str, log_func) -> bool:
    """Tương thích ngược: gọi GiftcodeService.submit_giftcode với Santa fallback."""
    svc = GiftcodeService(acc, log_func)
    # submit_giftcode tự động fallback tới Santa khi npc_id=None
    status = await svc.submit_giftcode(code, npc_id=None)
    return status in ("success", "used")
