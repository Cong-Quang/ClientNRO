# Hướng Dẫn Train 10 Acc Cùng Lúc (Shared Training)

## ⚠️ QUAN TRỌNG: Cập Nhật Code
**Bạn cần KHỞI ĐỘNG LẠI TOOL (Thoát và chạy lại `python main.py`) để áp dụng bản sửa lỗi mới nhất.** 
Nếu không restart, lệnh `ai group auto` sẽ báo lỗi `Manager not available`.

---

## Bước 1: Khởi động hệ thống
(Copy toàn bộ đoạn bên dưới và paste vào terminal game sau khi đã restart tool)

```bash
# 1. Đăng nhập 10 acc
login all

# 2. Bật chế độ Shared Training (Training tập trung)
ai trainer shared on

# 3. Tự động gom nhóm (Tất cả acc online -> Group 1)
# Lệnh này sẽ báo: [AI] Auto-assigned X logged-in accounts to Group 1
ai group auto

# 4. Kích hoạt nhóm hoạt động
ai group set 1
```

## Bước 2: Kích hoạt AI cho 10 acc
(Copy paste đoạn này để bật AI cho từng acc)

```bash
# Set mục tiêu chung
ai goal set farm_items 471,965,1634,1694 mob=56

target 0
aiagent on
aiagent train on

target 1
aiagent on
aiagent train on

target 2
aiagent on
aiagent train on

target 3
aiagent on
aiagent train on

target 4
aiagent on
aiagent train on

target 5
aiagent on
aiagent train on

target 6
aiagent on
aiagent train on

target 7
aiagent on
aiagent train on

target 8
aiagent on
aiagent train on

target 9
aiagent on
aiagent train on
```

## Bước 3: Kiểm tra & Lưu
```bash
# Kiểm tra acc bất kỳ
target 0
aiagent status
# Phải thấy dòng: in_active_group: True

# Lưu model (chỉ cần chạy trên 1 acc bất kỳ)
aiagent save shared_10acc_model
```


login all
ai trainer shared on
ai group auto
target all
aiagent on



login all
ai trainer shared on
ai group auto
ai goal set farm_items 471,965,1634,1694 mob=56
target all
aiagent on
combo chiakhu
 