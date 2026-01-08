# User Plugins Folder

## 📁 Đây là nơi đặt plugins của bạn!

Tất cả plugins tự tạo hoặc tải về nên đặt vào folder này.

### ✅ Cách sử dụng:

1. **Tạo plugin mới:**
   - Tạo file `.py` trong folder này
   - Ví dụ: `my_plugin.py`

2. **Copy plugin từ examples:**
   ```bash
   copy ..\examples\hello_plugin.py .
   ```

3. **Tải plugin từ internet:**
   - Download file `.py`
   - Đặt vào folder này

4. **Restart app:**
   - Plugins sẽ tự động load

### 📂 Cấu trúc:

```
plugins/
├── base_plugin.py          # System file - KHÔNG SỬA
├── plugin_manager.py       # System file - KHÔNG SỬA
├── plugin_loader.py        # System file - KHÔNG SỬA
├── plugin_api.py           # System file - KHÔNG SỬA
├── plugin_hooks.py         # System file - KHÔNG SỬA
├── examples/               # Example plugins - Tham khảo
│   ├── hello_plugin.py
│   ├── custom_command_plugin.py
│   └── notification_plugin.py
└── user_plugins/           # ← ĐẶT PLUGINS CỦA BẠN VÀO ĐÂY
    ├── my_plugin.py
    ├── telegram_bot.py
    └── ...
```

### 🎯 Lợi ích:

- ✅ **Tách biệt rõ ràng** - User plugins riêng, system files riêng
- ✅ **Dễ quản lý** - Biết file nào là của mình, file nào là system
- ✅ **An toàn** - Không vô tình sửa/xóa system files
- ✅ **Dễ backup** - Chỉ cần backup folder `user_plugins/`

### 📝 Ví dụ plugin đơn giản:

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
        super().on_enable()
        self.api.log_info("MyPlugin enabled!")
    
    def on_account_login(self, account):
        self.api.log_info(f"{account.username} logged in!")
```

### 📚 Tài liệu:

- Xem `../README.md` để biết cách tạo plugin
- Xem `../examples/` để xem ví dụ
- Xem `../../config/README.md` để config plugin settings

### ⚠️ Lưu ý:

- **KHÔNG** đặt plugins vào folder `plugins/` gốc
- **KHÔNG** sửa các file system (`base_plugin.py`, `plugin_manager.py`, v.v.)
- **CHỈ** đặt plugins vào `user_plugins/` folder này
