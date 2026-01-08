# Plugin System - Quick Start

## 🚀 Bắt đầu nhanh trong 3 bước

### Bước 1: Test với example plugin

```bash
# Copy example plugin vào user_plugins
copy examples\hello_plugin.py user_plugins\

# Chạy app
python main.py
```

Bạn sẽ thấy:
```
✅ Plugin system initialized: 1 plugin(s) enabled
🎉 Hello from HelloPlugin!
```

### Bước 2: Tạo plugin của riêng bạn

Tạo file `user_plugins/my_first_plugin.py`:

```python
from plugins.base_plugin import BasePlugin

class MyFirstPlugin(BasePlugin):
    def __init__(self):
        super().__init__()
        self.name = "MyFirstPlugin"
        self.version = "1.0.0"
        self.author = "Your Name"
        self.description = "My first plugin!"
    
    def on_enable(self):
        super().on_enable()
        self.api.log_info("🎉 My first plugin is running!")
    
    def on_account_login(self, account):
        self.api.log_info(f"✅ {account.username} logged in!")
```

Restart app → Plugin tự động load!

### Bước 3: Khám phá thêm

- **Xem examples:** `examples/` folder có 3 example plugins
- **Đọc docs:** `README.md` có hướng dẫn chi tiết
- **Tạo plugin phức tạp:** Xem `examples/custom_command_plugin.py`

## 📁 Cấu trúc folder

```
plugins/
├── base_plugin.py              # System - Không sửa
├── plugin_manager.py           # System - Không sửa
├── plugin_loader.py            # System - Không sửa
├── plugin_api.py               # System - Không sửa
├── plugin_hooks.py             # System - Không sửa
├── __init__.py                 # System - Không sửa
├── README.md                   # Documentation
├── QUICKSTART.md               # This file
├── examples/                   # Example plugins
│   ├── hello_plugin.py
│   ├── custom_command_plugin.py
│   └── notification_plugin.py
└── user_plugins/               # ← ĐẶT PLUGINS CỦA BẠN VÀO ĐÂY
    ├── README.md
    └── (your plugins here)
```

## ⚡ Available Hooks

Plugins có thể hook vào các events:

```python
def on_account_login(self, account):
    """Khi account login"""
    
def on_account_logout(self, account):
    """Khi account logout"""
    
def on_mob_killed(self, account, mob):
    """Khi giết mob (cần thêm trigger)"""
    
def on_level_up(self, account, new_level):
    """Khi lên level (cần thêm trigger)"""
    
def on_item_picked(self, account, item):
    """Khi nhặt item (cần thêm trigger)"""
```

## 🎯 Plugin API

```python
# Logging
self.api.log_info("Message")
self.api.log_warning("Warning")
self.api.log_error("Error")

# Accounts
accounts = self.api.get_accounts()
online = self.api.get_online_accounts()
acc = self.api.get_account_by_username("username")

# Config
value = self.api.get_config('server.host')
self.api.set_config('my_plugin.setting', 'value')

# Custom Commands
self.api.register_command('mycommand', self.handler, "Description")
```

## 💡 Tips

- ✅ Luôn đặt plugins vào `user_plugins/` folder
- ✅ Không sửa system files
- ✅ Test plugin trước khi share
- ✅ Đọc `README.md` để biết thêm chi tiết

## 🆘 Troubleshooting

**Plugin không load?**
- Kiểm tra file có trong `user_plugins/` không
- Kiểm tra class kế thừa từ `BasePlugin`
- Xem logs để tìm errors

**Hook không được gọi?**
- Một số hooks cần thêm trigger trong code
- Hiện tại chỉ có `on_account_login` và `on_account_logout` hoạt động

**Cần help?**
- Đọc `README.md`
- Xem examples trong `examples/`
- Check logs để debug
