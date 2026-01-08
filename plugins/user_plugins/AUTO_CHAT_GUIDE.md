# Auto Chat Plugin - Quick Guide

## 🎯 Tính năng

Plugin tự động chat khi login với 2 modes:

1. **Single Mode** - Chat 1 tin nhắn (mặc định)
2. **Combo Mode** - Chat nhiều tin nhắn liên tiếp

## 🚀 Cách sử dụng

### Mode 1: Single Chat (Mặc định)

Plugin sẽ tự động chat "hello" khi login.

**Để thay đổi tin nhắn:**

Mở file `auto_chat_plugin.py` và sửa:
```python
self.login_message = "hello"  # Đổi thành tin nhắn bạn muốn
```

### Mode 2: Combo Chat

Chat nhiều tin nhắn liên tiếp với delay.

**Bật combo mode:**

Mở file `auto_chat_plugin.py` và sửa:
```python
self.use_combo = True  # Đổi từ False thành True
```

**Tùy chỉnh combo:**
```python
# Danh sách tin nhắn
self.chat_combo = [
    "hello",
    "chào mọi người", 
    "mình mới vào",
    "ai chơi cùng không?"  # Thêm tin nhắn
]

# Delay giữa các tin nhắn (giây)
self.combo_delay = 2.0  # Thay đổi delay
```

## ⚙️ Config qua JSON (Nâng cao)

Nếu dùng `config/settings.json`, thêm:

```json
{
  "auto_chat": {
    "enabled": true,
    "login_message": "hello",
    "use_combo": false,
    "combo_delay": 2.0,
    "combo_messages": [
      "hello",
      "chào mọi người",
      "mình mới vào"
    ]
  }
}
```

Copy từ `config/settings.example.json` để xem ví dụ đầy đủ.

## 🎮 Ví dụ sử dụng

### Ví dụ 1: Chat đơn giản
```python
self.use_combo = False
self.login_message = "xin chào"
```
→ Khi login: Chat "xin chào"

### Ví dụ 2: Chat combo 3 câu
```python
self.use_combo = True
self.chat_combo = [
    "hello",
    "ai online không?",
    "đi săn boss nào"
]
self.combo_delay = 1.5
```
→ Khi login: 
- Chat "hello"
- Đợi 1.5s
- Chat "ai online không?"
- Đợi 1.5s
- Chat "đi săn boss nào"

### Ví dụ 3: Combo dài với delay khác nhau
```python
self.use_combo = True
self.chat_combo = [
    "hello mọi người",
    "mình mới vào",
    "level bao nhiêu rồi?",
    "ai đi cùng không?",
    "mình đang ở map X"
]
self.combo_delay = 3.0  # 3 giây giữa mỗi câu
```

## 🛑 Tắt plugin

**Cách 1:** Tắt trong code
```python
self.enabled_chat = False
```

**Cách 2:** Xóa file plugin
```bash
del plugins\user_plugins\auto_chat_plugin.py
```

**Cách 3:** Tắt qua config
```json
{
  "auto_chat": {
    "enabled": false
  }
}
```

## 💡 Tips

- ✅ Delay nên >= 1.5s để tránh spam
- ✅ Không chat quá nhiều tin nhắn (tối đa 5-7 câu)
- ✅ Test với 1 account trước khi dùng cho nhiều accounts
- ✅ Có thể dùng emoji trong tin nhắn: "hello 👋"

## ⚠️ Lưu ý

- Plugin chat ngay khi login, đảm bảo đã vào map
- Nếu chat không hoạt động, check logs để xem lỗi
- Delay quá ngắn có thể bị server chặn (spam)
- Mỗi account sẽ chat khi login của chính nó

## 🔧 Troubleshooting

**Không chat được?**
- Kiểm tra `self.enabled_chat = True`
- Kiểm tra account đã login thành công chưa
- Xem logs để tìm error message

**Chat bị spam?**
- Tăng `self.combo_delay` lên (ví dụ: 3.0)
- Giảm số tin nhắn trong combo

**Muốn chat khác nhau cho từng account?**
- Hiện tại plugin chat giống nhau cho tất cả accounts
- Để custom, cần sửa code thêm logic check username
