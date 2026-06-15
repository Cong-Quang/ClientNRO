"""
RetryService — Service tái sử dụng cho retry, timeout và exponential backoff.

Không phụ thuộc vào setup accounts, có thể dùng từ bất kỳ module nào.

Cách dùng:
  from services.retry import RetryConfig, retry_operation, run_with_timeout

  cfg = RetryConfig(max_attempts=3, base_delay=1.0, max_delay=5.0, backoff=2.0)
  ok = await retry_operation(acc, log_func, "ép sao", lambda: do_stuff(), cfg)
  result = await run_with_timeout(some_coro(), timeout=10.0, default_return=None)
"""

import asyncio
from typing import Awaitable, Callable, Optional

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
                          config: Optional[RetryConfig] = None,
                          timeout: float = 15.0) -> bool:
    """
    Retry wrapper: thực thi coroutine với retry + timeout + backoff.

    Args:
        acc: Account object (kiểm tra is_logged_in)
        log_func: Hàm log (acc, msg)
        label: Nhãn thao tác (dùng trong log)
        coro_factory: Hàm trả về coroutine cần thực thi
        config: Cấu hình retry (None = RetryConfig mặc định)
        timeout: Timeout cho mỗi lần thử (giây)

    Returns:
        True nếu thành công, False nếu thất bại sau tất cả retry
    """
    if config is None:
        config = RetryConfig()

    for attempt in range(1, config.max_attempts + 1):
        if not acc.is_logged_in:
            log_func(acc, f"{TerminalColors.RED}→ Mất kết nối khi {label}.{TerminalColors.RESET}")
            return False
        try:
            result = await asyncio.wait_for(coro_factory(), timeout=timeout)
            if result:
                return True
        except asyncio.TimeoutError:
            log_func(acc, f"{TerminalColors.YELLOW}→ {label}: timeout lần "
                          f"{attempt}/{config.max_attempts}.{TerminalColors.RESET}")
        except Exception as e:
            log_func(acc, f"{TerminalColors.YELLOW}→ {label}: lỗi lần "
                          f"{attempt}/{config.max_attempts}: {e}.{TerminalColors.RESET}")
        if attempt < config.max_attempts:
            delay = min(config.base_delay * (config.backoff ** (attempt - 1)),
                        config.max_delay)
            await asyncio.sleep(delay)
    return False
