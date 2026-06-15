"""
Package setup accounts — tự động setup tài khoản mới hoàn chỉnh.

Module structure:
- constants: Hằng số game
- state_manager: Quản lý trạng thái
- step_* handlers: Các bước setup (character, rewards, farm, bua, santa, upgrade, etc.)

Các tiện ích dùng chung đã được tách ra services/ để tái sử dụng:
  services/retry.py          ← commands/setup/retry_utils.py (now thin wrapper)
  services/inventory.py      ← commands/setup/inventory_helpers.py (now thin wrapper)
  services/navigation.py     ← commands/setup/navigation_helpers.py (now thin wrapper)
  services/combine_service.py
  services/giftcode_service.py
"""
