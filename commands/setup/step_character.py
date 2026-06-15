"""
Bước 1 & 2: Tạo nhân vật và chọn nhân vật (vào game).
- Step 1: Tạo nhân vật mới nếu chưa có
- Step 2: Chọn nhân vật mặc định và vào game
"""

import asyncio
import re

from logs.logger_config import TerminalColors
from config import Config
from commands.setup.constants import (
    GENDER_NAMEK, HAIR_BY_GENDER,
)


async def create_character(acc, log_func) -> bool:
    """
    Tạo nhân vật mới nếu chưa có.
    Đợi character data load xong sau login (tối đa 15s) trước khi quyết định.
    """
    C = TerminalColors

    # Đợi character data load xong — request_me_info nhiều lần
    for attempt in range(15):
        if acc.char.c_power > 0:
            log_func(f"{C.GREEN}→ Đã có nhân vật (SM={acc.char.c_power}).{C.RESET}")
            return True
        try:
            await acc.service.request_me_info()
        except Exception:
            pass
        await asyncio.sleep(1.0)

    # Vẫn c_power = 0 sau 15s — thử 1 lần cuối
    if acc.char.c_power > 0:
        log_func(f"{C.GREEN}→ Đã có nhân vật (SM={acc.char.c_power}).{C.RESET}")
        return True

    # Thực sự chưa có — tạo mới
    acc._suppress_auto_create = True

    try:
        match = re.search(r'(\d+)$', acc.username)
        raw_suffix = match.group(1) if match else "001"
        char_name = f"hentz{raw_suffix}"

        gender = getattr(Config, 'DEFAULT_CHAR_GENDER', GENDER_NAMEK)
        hair = HAIR_BY_GENDER.get(gender, 9)

        log_func(f"{C.DIM}→ Tạo nhân vật: name='{char_name}', gender={gender}, hair={hair}{C.RESET}")

        await acc.service.create_character(char_name, gender, hair)
        await asyncio.sleep(3.0)

        try:
            await asyncio.wait_for(acc.login_event.wait(), timeout=10.0)
        except asyncio.TimeoutError:
            pass
        await asyncio.sleep(1.0)

        try:
            await acc.service.request_me_info()
            await asyncio.sleep(0.5)
        except Exception:
            pass

        if acc.char.c_power > 0:
            log_func(f"{C.GREEN}→ Tạo nhân vật '{char_name}' thành công.{C.RESET}")
            return True

        log_func(f"{C.YELLOW}→ Thử lần 2.{C.RESET}")
        await acc.service.create_character(char_name, gender, hair)
        await asyncio.sleep(3.0)

        try:
            await asyncio.wait_for(acc.login_event.wait(), timeout=10.0)
        except asyncio.TimeoutError:
            pass
        await asyncio.sleep(1.0)

        try:
            await acc.service.request_me_info()
            await asyncio.sleep(0.5)
        except Exception:
            pass

        if acc.char.c_power > 0:
            log_func(f"{C.GREEN}→ Tạo nhân vật thành công (lần 2).{C.RESET}")
            return True

        log_func(f"{C.RED}→ Không thể tạo nhân vật sau 2 lần thử.{C.RESET}")
        return False
    finally:
        acc._suppress_auto_create = False


async def select_character(acc, log_func) -> bool:
    """
    Chọn nhân vật mặc định và vào game.
    Đợi cho đến khi map_id > 0 và c_power > 0.
    """
    C = TerminalColors

    if acc.is_logged_in and acc.char.c_power > 0 and acc.controller.tile_map.map_id > 0:
        log_func(f"{C.GREEN}→ Đã ở trong game (map {acc.controller.tile_map.map_id}).{C.RESET}")
        return True

    log_func(f"{C.DIM}→ Đợi vào game...{C.RESET}")

    for attempt in range(30):
        if not acc.is_logged_in:
            await asyncio.sleep(1)
            continue
        if acc.controller.tile_map.map_id > 0 and acc.char.c_power > 0:
            log_func(f"{C.GREEN}→ Vào game OK (map={acc.controller.tile_map.map_id}, SM={acc.char.c_power}).{C.RESET}")
            return True
        if attempt == 5:
            try:
                await acc.service.request_me_info()
            except Exception:
                pass
        if attempt == 10:
            try:
                await acc.service.request_change_map()
            except Exception:
                pass
        await asyncio.sleep(1)

    log_func(f"{C.RED}→ Không vào được game sau 30s.{C.RESET}")
    return False
