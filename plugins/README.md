# Plugin Development Guide

## Giới Thiệu

Plugin system cho phép bạn mở rộng chức năng của ClientNRO mà không cần sửa đổi code gốc. Plugins có thể:

- Lắng nghe các sự kiện game (login, logout, level up, mob kill, v.v.)
- Thêm custom commands
- Truy cập thông tin accounts và config
- Gửi notifications (console, Telegram, Discord, v.v.)

## Cấu Trúc Plugin

### Plugin Cơ Bản

Mỗi plugin phải kế thừa từ `BasePlugin` và đặt trong folder `user_plugins/`:

**File:** `plugins/user_plugins/my_plugin.py`

```python
from plugins.base_plugin import BasePlugin

class MyPlugin(BasePlugin):
    def __init__(self):
        super().__init__()
        self.name = "MyPlugin"
        self.version = "1.0.0"
        self.author = "Your Name"
        self.description = "My awesome plugin"
    
    def on_enable(self):
        """Called when plugin is enabled"""
        super().on_enable()
        self.api.log_info("MyPlugin enabled!")
    
    def on_disable(self):
        """Called when plugin is disabled"""
        self.api.log_info("MyPlugin disabled!")
        super().on_disable()
```

### 📁 Folder Structure

```
plugins/
├── base_plugin.py              # System - KHÔNG SỬA
├── plugin_manager.py           # System - KHÔNG SỬA  
├── plugin_loader.py            # System - KHÔNG SỬA
├── plugin_api.py               # System - KHÔNG SỬA
├── plugin_hooks.py             # System - KHÔNG SỬA
├── __init__.py                 # System - KHÔNG SỬA
├── README.md                   # Documentation
├── QUICKSTART.md               # Quick start guide
├── examples/                   # Example plugins (tham khảo)
│   ├── hello_plugin.py
│   ├── custom_command_plugin.py
│   └── notification_plugin.py
└── user_plugins/               # ← ĐẶT PLUGINS CỦA BẠN VÀO ĐÂY
    ├── README.md
    ├── __init__.py
    └── (your plugins here)
```

> **⚠️ QUAN TRỌNG:** Luôn đặt plugins vào `user_plugins/` folder, KHÔNG đặt trực tiếp vào `plugins/` folder!

### Lifecycle Hooks

Plugins có 4 lifecycle hooks chính:

1. **`on_load(plugin_api)`** - Được gọi khi plugin được load (trước khi enable)
2. **`on_enable()`** - Được gọi khi plugin được enable
3. **`on_disable()`** - Được gọi khi plugin được disable
4. **`on_unload()`** - Được gọi khi plugin được unload (sau khi disable)

## Event Hooks

Plugins có thể override các event hooks để phản ứng với các sự kiện game:

### `on_account_login(account)`
Được gọi khi một account đăng nhập thành công.

```python
def on_account_login(self, account):
    self.api.log_info(f"Account {account.username} logged in!")
```

### `on_account_logout(account)`
Được gọi khi một account đăng xuất.

```python
def on_account_logout(self, account):
    self.api.log_info(f"Account {account.username} logged out!")
```

### `on_mob_killed(account, mob)`
Được gọi khi một mob bị giết.

```python
def on_mob_killed(self, account, mob):
    self.api.log_info(f"{account.username} killed {mob.name}!")
```

### `on_level_up(account, new_level)`
Được gọi khi nhân vật lên level.

```python
def on_level_up(self, account, new_level):
    self.api.log_info(f"{account.username} reached level {new_level}!")
```

### `on_item_picked(account, item)`
Được gọi khi nhặt được item.

```python
def on_item_picked(self, account, item):
    self.api.log_info(f"{account.username} picked up an item!")
```

### `on_command_executed(command, args)`
Được gọi khi một command được thực thi.

```python
def on_command_executed(self, command, args):
    self.api.log_info(f"Command executed: {command}")
```

## Plugin API

Plugin API cung cấp các methods để tương tác với hệ thống:

### Account Management

```python
# Get all accounts
accounts = self.api.get_accounts()

# Get online accounts only
online = self.api.get_online_accounts()

# Get account by username
acc = self.api.get_account_by_username("username")
```

### Configuration

```python
# Get config value
host = self.api.get_config('server.host')
ai_enabled = self.api.get_config('ai.enabled', False)

# Set config value
self.api.set_config('my_plugin.setting', 'value')
```

### Logging

```python
self.api.log_debug("Debug message")
self.api.log_info("Info message")
self.api.log_warning("Warning message")
self.api.log_error("Error message")
```

### Custom Commands

```python
def on_enable(self):
    super().on_enable()
    # Register custom command
    self.api.register_command('mycommand', self.handle_command, "My custom command")

def handle_command(self, args):
    """Handle custom command"""
    self.api.log_info(f"Command called with args: {args}")
    return "Command executed!"

def on_disable(self):
    # Unregister command
    self.api.unregister_command('mycommand')
    super().on_disable()
```

## Ví Dụ Plugins

### 1. Hello Plugin (Simple)

File: `plugins/examples/hello_plugin.py`

Plugin đơn giản in ra thông báo khi enable/disable và khi có sự kiện.

### 2. Custom Command Plugin

File: `plugins/examples/custom_command_plugin.py`

Plugin thêm custom commands: `hello`, `status`, `count`

### 3. Notification Plugin

File: `plugins/examples/notification_plugin.py`

Plugin gửi notifications cho các sự kiện quan trọng và track statistics.

## Cài Đặt Plugin

### Cách 1: Tự động (Auto-load) - RECOMMENDED

1. Tạo file plugin trong thư mục `plugins/user_plugins/`
   ```bash
   # Ví dụ: tạo my_plugin.py
   notepad plugins\user_plugins\my_plugin.py
   ```

2. Plugin sẽ tự động được load khi khởi động

### Cách 2: Copy từ Examples

```bash
# Copy example plugin vào user_plugins
copy plugins\examples\hello_plugin.py plugins\user_plugins\
```

### Cách 3: Tải từ Internet

1. Download file plugin (`.py`)
2. Đặt vào `plugins/user_plugins/`
3. Restart app

> **Lưu ý:** KHÔNG đặt plugins trực tiếp vào `plugins/` folder. Luôn dùng `plugins/user_plugins/`!

## Best Practices

### 1. Error Handling

Luôn wrap code trong try-except để tránh crash:

```python
def on_mob_killed(self, account, mob):
    try:
        # Your code here
        pass
    except Exception as e:
        self.api.log_error(f"Error in on_mob_killed: {e}")
```

### 2. Resource Cleanup

Cleanup resources trong `on_disable()`:

```python
def on_enable(self):
    super().on_enable()
    self.timer = Timer(60, self.periodic_task)
    self.timer.start()

def on_disable(self):
    if self.timer:
        self.timer.cancel()
    super().on_disable()
```

### 3. Configuration

Lưu plugin settings trong config:

```python
def on_enable(self):
    super().on_enable()
    # Get plugin-specific config
    self.interval = self.api.get_config('my_plugin.interval', 60)
    self.enabled_features = self.api.get_config('my_plugin.features', [])
```

### 4. Logging

Sử dụng logging thay vì print():

```python
# Good
self.api.log_info("Plugin started")

# Bad
print("Plugin started")
```

## Advanced Topics

### Telegram Notifications

```python
import requests

def send_telegram(self, message):
    bot_token = self.api.get_config('telegram.bot_token')
    chat_id = self.api.get_config('telegram.chat_id')
    
    if bot_token and chat_id:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        requests.post(url, json={'chat_id': chat_id, 'text': message})

def on_level_up(self, account, new_level):
    self.send_telegram(f"🎉 {account.username} reached level {new_level}!")
```

### Discord Webhooks

```python
import requests

def send_discord(self, message):
    webhook_url = self.api.get_config('discord.webhook_url')
    
    if webhook_url:
        requests.post(webhook_url, json={'content': message})

def on_mob_killed(self, account, mob):
    if mob.is_boss:
        self.send_discord(f"⚔️ {account.username} killed boss {mob.name}!")
```

### Database Integration

```python
import sqlite3

def on_enable(self):
    super().on_enable()
    self.db = sqlite3.connect('plugin_data.db')
    self.db.execute('''
        CREATE TABLE IF NOT EXISTS kills (
            account TEXT,
            mob_name TEXT,
            timestamp INTEGER
        )
    ''')

def on_mob_killed(self, account, mob):
    import time
    self.db.execute(
        'INSERT INTO kills VALUES (?, ?, ?)',
        (account.username, mob.name, int(time.time()))
    )
    self.db.commit()
```

## Troubleshooting

### Plugin không load

- Kiểm tra plugin có kế thừa từ `BasePlugin` không
- Kiểm tra tên file không phải là `__init__.py` hoặc `base_plugin.py`
- Kiểm tra syntax errors trong plugin code

### Plugin crash

- Kiểm tra logs để xem error message
- Thêm try-except để catch errors
- Test plugin riêng lẻ trước khi enable tất cả

### Hook không được gọi

- Kiểm tra plugin đã được enable chưa
- Kiểm tra tên method hook đúng không
- Kiểm tra hook có được trigger trong code chính không

## Tài Liệu Tham Khảo

- `plugins/base_plugin.py` - Base plugin class
- `plugins/plugin_api.py` - Plugin API interface
- `plugins/examples/` - Example plugins
- `config/README.md` - Configuration guide

## Đóng Góp

Nếu bạn tạo plugin hữu ích, hãy chia sẻ với cộng đồng!

1. Test kỹ plugin
2. Viết documentation
3. Share trên GitHub/Discord/Forum
