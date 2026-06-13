"""Module chứa các hàm format và utilities cơ bản."""


def short_number(num: int) -> str:
    """Định dạng số ngắn gọn (VD: 1.2tr, 5.5tỷ)."""
    if num >= 1_000_000_000:
        return f"{num/1_000_000_000:.1f}b".replace('.0b', 'b')
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}m".replace('.0m', 'm')
    if num >= 1_000:
        return f"{num/1_000:.1f}k".replace('.0k', 'k')
    return str(num)
