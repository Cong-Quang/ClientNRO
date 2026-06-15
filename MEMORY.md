# MEMORY.md - Setup Accounts Refactor

## Ngày: 2026-06-15

---

## ĐÃ LÀM ĐƯỢC

### 1. Refactor setup_accounts_command.py
- File gốc 2258 dòng → tách thành 16 module trong `commands/setup/`
- Tách: constants, state_manager, retry_utils, inventory_helpers, navigation_helpers
- Tách step: character, rewards, giftcode, farm_beans, buy_bua, santa_shop, support_items, activate_items, upgrade

### 2. Fix logic tạo nhân vật
- Thêm đợi 15s load character data sau login (trước đó chỉ 5s)
- Thêm request_me_info() nhiều lần để server gửi data về

### 3. Fix logic item 2000 (Set Liên Hoàn)
- Thêm check `has_character` trong state để skip step 1 đúng cách
- Fix `SET_LIEN_HOAN_ITEMS = [1, 7, 22, 28, 12]` (trước đó sai có item 16)

### 4. Fix logic ép sao trang bị
- **Trang bị:** Items 1, 7, 22, 28, 12
- **Nguyên liệu:** Item 16 (cho set 1), 442 + 441 (cho set 2)
- Set 1: mỗi trang bị ép riêng với Item 16 (x10 lần mỗi món)
- Set 2: Item 12 đặc biệt — 12 + 2x 442 + 8x 441
- Fix bug `used_indices` trong `_do_one_upgrade` (trùng index khi main_item == material)
- Fix item 12 không nằm trong vòng lặp đơn giản nữa

### 5. Thêm CombineHelper class
- File: `commands/setup/combine_helper.py`
- Class tái sử dụng cho mọi thao tác ép sao/combine
- Methods: check_item_slots, get_item_stars, is_fully_upgraded, do_combine, open_combine, print_status, dump_item_options

### 6. Thêm start_step parameter
- `setup_accounts 5 10 start_step=7` — chạy từ step cụ thể
- Tự động đánh dấu các step trước đó là done
- Acc 05-15: steps 1-6 done, chạy từ step 7

### 7. Thêm show equip
- Lệnh `show equip` hoặc `show trangbi` — hiển thị trạng thái trang bị chi tiết

### 8. Fix log_func binding
- `_log` là bound method nhưng step functions gọi `log(msg)` thiếu `acc`
- Fix: `log = lambda msg: self._log(acc, msg)`

### 9. Fix step失败 không dừng
- Trước: step thất bại → return False → dừng toàn bộ
- Sau: step thất bại → continue → chạy step tiếp theo

---

## ĐANG GẶP KHÓ KHĂN

### 1. **COMBINE FLOW KHÔNG HOẠT ĐỘNG** (ƯU TIÊN CAO NHẤT)
- **Vấn đề:** Sau khi `send_combine_items`, server luôn hiện menu "Đóng" thay vì confirm upgrade
- **Kết quả:** Item 16 không bị consume, sao không tăng, upgrade thất bại
- **Flow hiện tại (sai):**
  ```
  NPC → "Pha lê hóa trang bị" → sub-menu ["Ép sao trang bị", "Pha lê hóa trang bị"]
  → Chọn "Ép sao trang bị" → Tab combine mở → send_combine_items
  → Menu hiện "Đóng" → không process
  ```
- **Flow đúng (theo user):**
  ```
  NPC → "Pha lê hóa trang bị" → interface mở → bỏ trang bị + nguyên liệu → ép
  ```
- **Nghi ngờ:** Có thể bot đang mở sai tab/interface. "Pha lê hóa trang bị" vs "Ép sao trang bị" có thể là 2 flow khác nhau
- **Cần làm:** Test thêm, có thể cần dùng `send_combine_items` với đúng format slot, hoặc flow khác

### 2. **Star detection chưa chính xác 100%**
- Option 102: param = stars - 1 (đã confirm: param=2 → 3 sao, param=6 → 7 sao)
- Nhưng một số items không có option 102 → fallback về option 107 (max stars)
- Một số items có option 102=0 nhưng thực tế 0 sao → OK
- Cần verify thêm với items đã upgrade đầy đủ

---

## CẤU TRÚC FILE HIỆN TẠI

```
commands/setup_accounts_command.py   ← Main orchestrator (~280 dòng)
commands/setup/
├── __init__.py
├── constants.py                     ← Hằng số game
├── state_manager.py                 ← Quản lý trạng thái JSON
├── retry_utils.py                   ← Retry + backoff
├── inventory_helpers.py             ← Đếm/tìm item
├── navigation_helpers.py            ← NPC, teleport, xmap
├── combine_helper.py                ← Class ép sao/combine (tái sử dụng)
├── step_character.py                ← Tạo/chọn nhân vật
├── step_rewards.py                  ← Nhận thưởng
├── step_giftcode.py                 ← Nhập giftcode
├── step_farm_beans.py               ← Farm đậu thần
├── step_buy_bua.py                  ← Mua bùa
├── step_santa_shop.py               ← Santa shop
├── step_support_items.py            ← Dùng item hỗ trợ
├── step_activate_items.py           ← Kích hoạt item 2000 + đơn
└── step_upgrade.py                  ← Ép sao trang bị
```

---

## CẤU HÌNH STATE HIỆN TẠI

- Acc 05-15: steps 1-6 done, `has_character: true`
- Acc 14: steps 1-9 done
- Command: `setup_accounts 5 10 start_step=7`

---

## ITEM IDs QUAN TRỌNG

- **Trang bị:** 1, 7, 22, 28, 12
- **Nguyên liệu chính:** Item 16 (ép cho từng trang bị)
- **Nguyên liệu đặc biệt:** 442, 441 (cho Item 12 set 2)
- **Item 2000:** Đá Linh Hồn (chọn Set Liên Hoàn)

---

## OPTION IDs (NRO Server)

- **Option 102:** param = stars - 1 (ví dụ param=2 → 3 sao)
- **Option 107:** max stars (param=10)
- **Option 50:** Stat bonus (damage/HP/etc)

---

## LỆNH THƯỜNG DÙNG

```
setup_accounts 5 10              # Chạy setup từ step 1
setup_accounts 5 10 start_step=7 # Chạy từ step 7 (Mua bùa)
setup_accounts 5 10 reset        # Reset trạng thái
show equip                       # Xem trạng thái trang bị
show balo                        # Xem hành trang
```
