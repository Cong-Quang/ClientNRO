"""
Quản lý trạng thái setup cho từng account.
Lưu trạng thái vào file JSON để có thể resume khi bị gián đoạn.
"""

import json
import os
from dataclasses import dataclass, field, asdict

from commands.setup.constants import ALL_STEPS

STATE_FILE = "setup_state.json"


@dataclass
class StepState:
    """Trạng thái của một bước setup."""
    completed: bool = False       # Bước đã hoàn thành chưa
    skipped: bool = False         # Bước đã bị bỏ qua chưa
    retry_count: int = 0          # Số lần retry đã thực hiện
    error: str = ""               # Lỗi cuối cùng (nếu có)


@dataclass
class AccountSetupState:
    """Trạng thái setup tổng thể của một account."""
    username: str = ""
    steps: dict = field(default_factory=dict)
    has_character: bool = False
    has_pet: bool = False
    gold_claimed: bool = False    # Đã nhận vàng miễn phí chưa
    gem_claimed: bool = False     # Đã nhận ngọc miễn phí chưa
    giftcode_done: bool = False   # Đã nhập giftcode chưa
    disciple_claimed: bool = False  # Đã nhận đệ tử chưa


class SetupStateManager:
    """Quản lý trạng thái setup cho từng account, lưu vào file JSON để resume."""

    def __init__(self):
        self._states: dict[str, AccountSetupState] = {}

    def load(self):
        """Tải trạng thái từ file JSON."""
        if not os.path.exists(STATE_FILE):
            return
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                raw = json.load(f)
            for username, data in raw.items():
                state = AccountSetupState(**data)
                # Đảm bảo tất cả step keys đều tồn tại
                for s in ALL_STEPS:
                    if str(s) not in state.steps:
                        state.steps[str(s)] = StepState().__dict__
                self._states[username] = state
        except (json.JSONDecodeError, IOError, TypeError):
            pass

    def save(self):
        """Lưu trạng thái ra file JSON."""
        try:
            raw = {u: asdict(s) for u, s in self._states.items()}
            with open(STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(raw, f, indent=2, ensure_ascii=False)
        except IOError:
            pass

    def get(self, username: str) -> AccountSetupState:
        """Lấy trạng thái của account, tự tạo mới nếu chưa có."""
        if username not in self._states:
            state = AccountSetupState(username=username)
            state.steps = {str(s): StepState().__dict__ for s in ALL_STEPS}
            self._states[username] = state
        return self._states[username]

    def mark_step(self, username: str, step: int, completed: bool = True,
                  skipped: bool = False, error: str = ""):
        """Đánh dấu trạng thái bước setup."""
        state = self.get(username)
        s = state.steps.get(str(step), StepState().__dict__)
        s["completed"] = completed
        s["skipped"] = skipped
        s["error"] = error
        state.steps[str(step)] = s
        self.save()

    def is_step_completed(self, username: str, step: int) -> bool:
        """Kiểm tra bước đã hoàn thành chưa."""
        state = self.get(username)
        s = state.steps.get(str(step), {})
        return s.get("completed", False)

    def is_step_skipped(self, username: str, step: int) -> bool:
        """Kiểm tra bước đã bị bỏ qua chưa."""
        state = self.get(username)
        s = state.steps.get(str(step), {})
        return s.get("skipped", False)

    def is_step_done(self, username: str, step: int) -> bool:
        """Bước đã hoàn thành hoặc đã skip."""
        return self.is_step_completed(username, step) or self.is_step_skipped(username, step)

    def reset(self, username: str):
        """Reset trạng thái của một account."""
        if username in self._states:
            del self._states[username]
            self.save()

    def reset_all(self):
        """Reset trạng thái của tất cả accounts."""
        self._states.clear()
        self.save()

    def set_attribute(self, username: str, **kwargs):
        """Thiết lập attribute tùy ý trên trạng thái account."""
        state = self.get(username)
        for k, v in kwargs.items():
            if hasattr(state, k):
                setattr(state, k, v)
        self.save()
