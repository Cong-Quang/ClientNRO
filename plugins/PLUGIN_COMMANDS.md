# Plugin Commands - Quick Guide

## 🎮 Cách sử dụng Plugin Commands

Giờ bạn có thể quản lý plugins ngay trong app mà không cần restart!

### 📋 Liệt kê plugins

```
> plugin list
```

Hiển thị:
```
============================================================
📦 DANH SÁCH PLUGINS
============================================================
✅ Enabled | AutoChatPlugin v1.0.0
         Author: ClientNRO Team
         Tự động chat khi login và hỗ trợ chat combo
--------------------------------------------------------------------
❌ Disabled | HelloPlugin v1.0.0
         Author: ClientNRO Team
         Simple hello world plugin example
--------------------------------------------------------------------

Tổng: 2 plugins (1 enabled)
============================================================
```

### ✅ Enable plugin

```
> plugin enable HelloPlugin
```

Plugin sẽ được bật ngay lập tức!

### ❌ Disable plugin

```
> plugin disable AutoChatPlugin
```

Plugin sẽ bị tắt ngay lập tức!

### ℹ️ Xem thông tin plugin

```
> plugin info AutoChatPlugin
```

Hiển thị:
```
============================================================
📦 THÔNG TIN PLUGIN: AutoChatPlugin
============================================================
Name:        AutoChatPlugin
Version:     1.0.0
Author:      ClientNRO Team
Description: Tự động chat khi login và hỗ trợ chat combo
Status:      ✅ Enabled
============================================================
```

### 🔄 Reload plugin

```
> plugin reload AutoChatPlugin
```

> **Lưu ý:** Reload hiện tại chỉ unload plugin. Để load lại cần restart app.

---

## 🚀 Workflow đơn giản

### Test plugin mới:

1. **Tạo plugin** trong `plugins/user_plugins/`
2. **Restart app** (lần đầu)
3. **Check:** `plugin list`
4. **Test:** Login và xem plugin hoạt động
5. **Disable nếu cần:** `plugin disable PluginName`
6. **Enable lại:** `plugin enable PluginName`

### Quản lý plugins:

```bash
# Xem có plugins nào
> plugin list

# Tắt plugin không cần
> plugin disable HelloPlugin

# Bật lại khi cần
> plugin enable HelloPlugin

# Xem thông tin
> plugin info AutoChatPlugin
```

---

## 💡 Tips

- ✅ Dùng `plugin list` để xem tên chính xác của plugin
- ✅ Tên plugin phân biệt hoa/thường (case-sensitive)
- ✅ Enable/Disable ngay lập tức, không cần restart
- ✅ Reload cần restart app để load lại code mới

---

## 📝 Ví dụ thực tế

### Scenario 1: Test AutoChatPlugin

```bash
# 1. Check plugin có load không
> plugin list

# 2. Xem thông tin
> plugin info AutoChatPlugin

# 3. Login để test
> login 0

# 4. Nếu muốn tắt
> plugin disable AutoChatPlugin

# 5. Login lại → không chat nữa
> logout 0
> login 0

# 6. Bật lại
> plugin enable AutoChatPlugin
```

### Scenario 2: Quản lý nhiều plugins

```bash
# Xem tất cả
> plugin list

# Tắt plugins không dùng
> plugin disable HelloPlugin
> plugin disable NotificationPlugin

# Chỉ giữ AutoChatPlugin
> plugin list
# → Chỉ còn AutoChatPlugin enabled
```

---

## ❓ FAQ

**Q: Tại sao cần restart để load plugin mới?**  
A: Plugin loader chỉ chạy lúc khởi động. Sau khi tạo plugin mới, cần restart 1 lần.

**Q: Enable/Disable có cần restart không?**  
A: KHÔNG! Enable/Disable ngay lập tức.

**Q: Reload có load lại code mới không?**  
A: Hiện tại chưa. Cần restart app để load code mới.

**Q: Làm sao biết plugin đang enabled?**  
A: Dùng `plugin list` hoặc `plugin info <name>`

---

Giờ việc test plugin đơn giản hơn nhiều rồi! 🎉
