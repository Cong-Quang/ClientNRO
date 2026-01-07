"""Module chứa các hàm format và utilities cơ bản."""


def short_number(num: int) -> str:
    """Định dạng số ngắn gọn (VD: 1.2tr, 5.5tỷ)."""
    if num >= 1_000_000_000:
        return f"{num/1_000_000_000:.1f}tỷ".replace('.0tỷ', 'tỷ')
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}tr".replace('.0tr', 'tr')
    if num >= 1_000:
        return f"{num/1_000:.1f}k".replace('.0k', 'k')
    return str(num)
