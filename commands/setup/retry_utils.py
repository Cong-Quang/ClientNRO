"""
Tiện ích retry và timeout dùng chung.
Cung cấp cơ chế retry với exponential backoff và timeout.
Có thể tái sử dụng từ bất kỳ module nào.
"""

import asyncio
from typing import Callable, Awaitable

from logs.logger_config import TerminalColors


class RetryConfig:
    """Cấu hình retry cho mỗi thao tác."""
    def __init__(self, max_attempts: int = 3, base_delay: float = 1.0,
                 max_delay: float = 5.0, backoff: float = 2.0):
        self.max_attempts = max_attempts   # Số lần thử tối đa
        self.base_delay = base_delay       # Thời gian chờ ban đầu (giây)
        self.max_delay = max_delay         # Thời gian chờ tối đa (giây)
        self.backoff = backoff             # Hệ số nhân delay sau mỗi lần retry


async def run_with_timeout(coro: Awaitable, timeout: float = 10.0,
                           default_return=None):
    """Chạy coroutine với timeout, trả về default nếu timeout."""
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        return default_return


async def retry_operation(acc, log_func, label: str, coro_factory: Callable,
                          config: RetryConfig, timeout: float = 15.0) -> bool:
    """
    Retry wrapper: thực thi coroutine với retry + timeout + backoff.
    Args:
        acc: Account object (kiểm tra is_logged_in)
        log_func: Hàm log (acc, msg)
        label: Nhãn thao tác (dùng trong log)
        coro_factory: Hàm trả về coroutine cần thực thi
        config: Cấu hình retry
        timeout: Timeout cho mỗi lần thử (giây)
    Returns:
        True nếu thành công, False nếu thất bại sau tất cả retry
    """
    for attempt in range(1, config.max_attempts + 1):
        if not acc.is_logged_in:
            log_func(f"{TerminalColors.RED}→ Mất kết nối khi {label}.{TerminalColors.RESET}")
            return False
        try:
            result = await asyncio.wait_for(coro_factory(), timeout=timeout)
            if result:
                return True
        except asyncio.TimeoutError:
            log_func(f"{TerminalColors.YELLOW}→ {label}: timeout lần {attempt}/{config.max_attempts}.{TerminalColors.RESET}")
        except Exception as e:
            log_func(f"{TerminalColors.YELLOW}→ {label}: lỗi lần {attempt}/{config.max_attempts}: {e}.{TerminalColors.RESET}")
        if attempt < config.max_attempts:
            delay = min(config.base_delay * (config.backoff ** (attempt - 1)), config.max_delay)
            await asyncio.sleep(delay)
    return False
