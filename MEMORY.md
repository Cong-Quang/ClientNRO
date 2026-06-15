# MEMORY.md - Setup Accounts Refactor

## Ngày: 2026-06-15

---

## ĐÃ FIX (2026-06-15)

### 0. **COMBINE NOW WORKS!** ✅ (Live test confirmed)
- **Step 11 đã chạy thành công:** Item 16 (crystal) 999→996 (3 consumed), Item 1 stars 0→1→2→3
- **Server chấp nhận 2 items** (1 trangBi + 1 daPhaLe) thay vì từ chối với "Đóng"

### 1. **ROOT CAUSE: Step 11 gửi 3 items, server chỉ chấp nhận 2** 🐞 (BUG CHÍNH)
- **Server:** `EpSaoTrangBi.showInfoCombine` kiểm tra `itemsCombine.size() == 2`
- **Client cũ:** `main=16, materials=[(1,2)]` → gửi 3 indices [16_idx, 1_idx, 1_idx]
- **Server:** size=3 != 2 → hiện "Đóng"
- **Fix:** `main=1 (trangBi), materials=[(16,1)] (đá pha lê)` → gửi đúng 2 items
- **Server:** Nhận 2 items → hiện "Nâng cấp..." → ép thành công

### 2. **Star detection fallback sai option 107** 🐞
- **Server:** Option 102 = ép sao star count; Option 107 = max slots (PhaLeHoaTrangBi)
- **Lỗi:** `_get_item_stars` fallback về 107 khi không có 102 → items chưa ép bị báo "đã 10 sao" → `is_fully_upgraded` return True sai → bỏ qua upgrade
- **Fix:** Chỉ đọc option 102, KHÔNG fallback về 107 — items chưa ép trả về 0 sao

### 3. **Set 2 Item 12 gửi 11 items** 🐞
- Ép sao chỉ chấp nhận 2 items. Item 441/442 (id > 20) không phải đá pha lê (daPhaLe)
- **Fix:** Log warning + skip. Cần combine type khác ("Nâng cấp vật phẩm"?) để xử lý sau

### 4. **Stale last_ui_options** 🐞 (đã fix trước)
- Clear `ctrl.last_ui_options` trước khi gửi; await `ui_menu_event` thay poll

### 5. **Race condition reopen** 🐞 (đã fix trước)
- `combine_result == "reopen"` = success (reopen = thành công + mở lại tab)

### 6. **retry_utils log_func sai signature** 🐞
- **Lỗi:** `retry_operation` gọi `log_func(msg)` với 1 tham số, nhưng `_log(acc, msg)` cần 2
- **Kết quả:** `TypeError: _log() missing 1 required positional argument: 'msg'` khi timeout
- **Fix:** Đổi `log_func(msg)` → `log_func(acc, msg)` (3 chỗ)

---

## FIX SESSION 3 (2026-06-15): Rada ép chỉ số + MAX_STAR=9 + TĂNG TỐC + SHOW EQUIP

### 14. **TĂNG TỐC ĐỘ SETUP** 🚀

### 15. **NEW: show equip_master & show equip_pet** 🆕
- **`show equip_master`** / `show body_master`: Hiển thị chi tiết trang bị sư phụ đang mặc
  - Hiển thị từng item trên body (item_id, tên, số sao, options)
  - Với rada (item 12): hiển thị option 95 (sức đánh) và 96 (hút KI)
  - Nếu không có: ghi "Không có"
- **`show equip_pet`** / `show body_pet`: Hiển thị chi tiết trang bị đệ tử đang mặc
  - Request pet info trước khi hiển thị
  - Hiển thị giống equip_master
  - Nếu không có đệ tử: ghi "Không có đệ tử"
- **`show equip`**: Đã thêm phần hiển thị tổng quan body master + pet
- **Refactor**: Helper methods `_show_body_equip()`, `_show_body_items()`, `_show_pet_equip()` tránh duplicate

### 16. **Equip master/pet fallback đồ chưa ép** 🛡️
- Thêm fallback thứ 3: nếu không có đồ full ép (9⭐) hay đồ đã ép (1+⭐) thì mặc đồ chưa ép (0⭐)
- Đảm bảo sư phụ và đệ tử luôn có đồ dù upgrade chưa chạy

### 17. **Fix combine timeout 3.0s→5.0s** ⏱️
- combine_event.wait() timeout tăng từ 3.0s lên 5.0s để server kịp xử lý
- Giảm `asyncio.sleep` trong farm beans loop: 0.1s → 0.03s (tiết kiệm ~21s cho 300 lần)
- Giảm sleeps khi mua item Santa: 0.03s → 0.01s (tiết kiệm ~3s cho 170 items)
- Giảm sleeps khi dùng item: 0.2s → 0.1s (equip), 0.3s → 0.15s (đệ tử)
- Giảm timeouts: menu 3.0s→2.0s, combine 4.0s→3.0s, result 5.0s→3.0s
- Giảm retry base_delay: 1.0s→0.5s (hoặc 0.3s cho step đơn giản)
- Giảm retry max_delay và backoff để retry nhanh hơn

### 10. **Rada (Item 12) ép chỉ số 441/442 bị từ chối vì isDaPhaLe()** 🐞
- **Root cause:** Server `CombineSystem.isDaPhaLe()` chỉ check type==30 hoặc id 14-20
- Items 441-447 (Sao pha lê) có id > 20 nên không được nhận diện là đá pha lê
- `EpSaoTrangBi.showInfoCombine` không tìm thấy daPhaLe → hiện "Đóng"
- **Fix `CombineSystem.java`:** Thêm `|| (item.template.id >= 441 && item.template.id <= 447)`

### 11. **Rada mặc định có option 107=10 bị chặn ở EpSaoTrangBi** 🐞
- **Root cause:** Server check `starEmpty <= MAX_STAR` (MAX_STAR=9), rada mặc định có 107=10 → 10<=9=false
- **Fix `EpSaoTrangBi.java` showInfoCombine:** Thêm `star == 0 ||` để items mới chưa ép vượt qua check
- **Bổ sung:** Thêm `star > 0 &&` trước `CheckSlot` để items mới không bị chặn ở slot check
- **Fix `EpSaoTrangBi.java` epSaoTrangBi:** Cũng thêm `star > 0 &&` cho CheckSlot

### 12. **MAX_STAR=9 nhưng client dùng 10** 🐞
- **Root cause:** Server `EpSaoTrangBi.MAX_STAR=9`, `CombineService.MAX_STAR_ITEM=9`
- Client `UPGRADE_TIMES_PER_PIECE=10` → cố ép lên 10 sao nhưng server max=9
- Kết quả: chỉ đạt 27% sức đánh (9×3%) thay vì 30%
- **Fix `constants.py`:** `UPGRADE_TIMES_PER_PIECE = 9`
- **Fix `combine_service.py`:** `is_item_fully_upgraded` check `>= 9` thay `>= 10`
- **Fix defaults:** `check_item_slots`, `is_fully_upgraded`, `print_status` default target_stars=9

### 13. **Full test acc poopooi06 — ALL 14 STEPS PASSED** ✅
- Step 11: Ép Item 16 thành công
- Step 12: Ép Item 1/22/28/12 (rada 442+441) thành công
- Step 13: Mặc đồ cho sư phụ thành công
- Step 14: Mặc đồ cho đệ tử thành công

---

## REFACTOR: Tách Service Classes (2026-06-15)

### services/ — Reusable Service Layer (MỚI)
```
services/
├── __init__.py                      ← Export tất cả services
├── combine_service.py               ← CombineService (ép sao, đập đồ)
├── giftcode_service.py              ← GiftcodeService (nhập giftcode)
├── navigation.py                    ← NavigationService + free functions (MỚI)
├── inventory.py                     ← InventoryService + free functions (MỚI)
└── retry.py                         ← RetryConfig + retry_operation() (MỚI)
```

**NavigationService** (`services/navigation.py`):
- `find_npc(npc_id)` / `find_npc_by_name(name)` — tìm NPC
- `teleport_to_npc(npc_id)` — teleport đến NPC
- `open_menu(npc_id)` / `confirm_menu(npc_id, option_idx)` / `open_input_form(npc_id, option_idx)` — menu NPC
- `find_menu_option(options, *keywords)` — tìm option trong menu (static)
- `go_home()` / `move_to_map(target_map_id)` — di chuyển map

**InventoryService** (`services/inventory.py`):
- `count_item(item_id)` / `find_item_index(item_id)` / `find_item_indices(item_id, quantity)` — đếm/tìm item
- `has_item(item_id)` / `count_items_by_ids(item_ids)` — kiểm tra item
- `refresh()` — refresh inventory từ server

**RetryService** (`services/retry.py`):
- `RetryConfig(max_attempts, base_delay, max_delay, backoff)` — cấu hình retry
- `retry_operation(acc, log_func, label, coro_factory, config, timeout)` — retry wrapper
- `run_with_timeout(coro, timeout, default_return)` — timeout wrapper

**CombineService** (`services/combine_service.py`):
- `open_combine(npc_id, map_id, menu_keywords, submenu_keywords)` — mở tab combine
- `do_combine(main_item_id, materials, max_times, bag_index)` — thực hiện ép (hỗ trợ ép theo index)
- `check_item_slots(item_id, target_stars)` — check trạng thái sao
- `get_item_stars(item_id)` / `get_item_star_at_index(bag_index)` — lấy số sao
- `is_fully_upgraded(item_id, target_stars)` — kiểm tra đã ép đủ chưa
- `print_status(item_ids, target_stars)` — tổng kết
- `send_and_confirm(indices, npc_id)` — gửi + xác nhận combine 1 lần
- `find_item_indices(item_id, quantity)` / `dump_item_options(item_id)` / `get_item_details(item_id)` — tiện ích

**GiftcodeService** (`services/giftcode_service.py`):
- `submit_giftcode(code, npc_id, santa_map)` — nhập code (auto fallback Santa)
- `wait_response(timeout)` — đợi phản hồi server
- `check_reward_items()` — kiểm tra item nhận được

### Thin wrappers (backward compatible)
Các file cũ trong `commands/setup/` giờ là thin wrapper re-export từ `services/*`:
- `commands/setup/retry_utils.py` → re-export từ `services.retry`
- `commands/setup/inventory_helpers.py` → re-export từ `services.inventory` + giữ helpers setup-specific (`count_beans`, `count_bua_items`, `count_set_lien_hoan`, `has_giftcode_items`)
- `commands/setup/navigation_helpers.py` → re-export từ `services.navigation`
- `commands/setup/combine_helper.py` → re-export từ `services.combine_service`
- `commands/setup/step_giftcode.py` → delegate lên `services.giftcode_service`
- `commands/setup/step_upgrade.py` → dùng `services.combine_service` trực tiếp
- `commands/setup/step_rewards.py` → dùng `services.giftcode_service` trực tiếp

Mọi import cũ (`from commands.setup.navigation_helpers import ...`) vẫn hoạt động.

### Cách dùng services từ module khác
```python
# Cách 1: Dùng class (khuyến nghị)
from services.navigation import NavigationService
from services.inventory import InventoryService
from services.combine_service import CombineService
nav = NavigationService(acc, log_func)
inv = InventoryService(acc, log_func)
svc = CombineService(acc, log_func)

await nav.go_home()
count = inv.count_item(16)
await svc.open_combine()
done = await svc.do_combine(main_item_id=1, materials=[(16, 1)], max_times=10)

from services.giftcode_service import GiftcodeService
gsvc = GiftcodeService(acc, log_func)
status = await gsvc.submit_giftcode("tdstudio")

# Cách 2: Dùng free function (backward compatible)
from services.inventory import count_item, refresh_inventory
from services.navigation import teleport_to_npc, move_to_map
from services.retry import RetryConfig, retry_operation

count = count_item(acc, 16)
await refresh_inventory(acc)
await teleport_to_npc(acc, 21)
await move_to_map(acc, 5, log_func)
ok = await retry_operation(acc, log_func, "label", lambda: do_stuff())
```

---

## CẤU TRÚC FILE HIỆN TẠI

```
services/
├── __init__.py                      ← Export tất cả
├── combine_service.py               ← CombineService (REUSABLE)
├── giftcode_service.py              ← GiftcodeService (REUSABLE)
├── navigation.py                    ← NavigationService + free functions (REUSABLE)
├── inventory.py                     ← InventoryService + free functions (REUSABLE)
└── retry.py                         ← RetryConfig + retry_operation (REUSABLE)

commands/setup_accounts_command.py   ← Main orchestrator (~280 dòng)
commands/setup/
├── __init__.py
├── constants.py                     ← Hằng số game
├── state_manager.py                 ← Quản lý trạng thái JSON
├── retry_utils.py                   ← THIN WRAPPER → services.retry
├── inventory_helpers.py             ← THIN WRAPPER → services.inventory + setup helpers
├── navigation_helpers.py            ← THIN WRAPPER → services.navigation
├── combine_helper.py                ← Wrapper → services.combine_service
├── step_character.py                ← Tạo/chọn nhân vật
├── step_rewards.py                  ← Nhận thưởng (dùng GiftcodeService)
├── step_giftcode.py                 ← Wrapper → services.giftcode_service
├── step_farm_beans.py               ← Farm đậu thần
├── step_buy_bua.py                  ← Mua bùa
├── step_santa_shop.py               ← Santa shop
├── step_support_items.py            ← Dùng item hỗ trợ
├── step_activate_items.py           ← Kích hoạt item 2000 + đơn
└── step_upgrade.py                  ← Ép sao trang bị (dùng CombineService)
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

## FIX: Ép từng bản sao riêng (2026-06-15)

### Vấn đề
Khi có 2 set (2+ bản sao mỗi trang bị), `do_combine` luôn ép cái đầu tiên tìm thấy.
`get_item_stars` trả về max → sau 1 cái max 9⭐ thì tưởng đã xong, bỏ qua các bản sao còn lại.

### Fix
- `combine_service.py`: Thêm `bag_index` param vào `do_combine` — nếu >=0 thì ép theo index cụ thể
- `step_upgrade.py`: Set 1 tìm tất cả bản sao chưa max, ép từng cái riêng với `bag_index`
- Set 2 Item 12 cũng ép từng copy riêng: 2x442 + 8x441

### Test
- Accounts 05-10: 6/6 OK, ép từng bản sao hoạt động
- Items sao_max=9/9 (đầy đủ)

---

## CÁC BUG ĐÃ FIX (2026-06-15 - Session 2)

### 7. **equip_master dùng sai action type** 🐞
- **Lỗi:** `equip_master` dùng `use_item(1, 1, ...)` (type=1 = "đeo vào" — dùng cho cải trang)
- **Đúng:** Cần `use_item(0, 1, ...)` (type=0 = "sử dụng" — mặc đồ cho bản thân)
- **Fix:** Đổi `use_item(1, 1, idx, -1)` → `use_item(0, 1, idx, -1)`
- **Chi tiết:** Trong NRO, type=1 là "đeo vào" (chỉ dùng cho item cải trang 290). Với trang bị thường (1,7,22,28,12), type=0 = "sử dụng" mới đúng để equip lên body master.

### 8. **Rada (Item 12) chỉ ép được 1 copy** 🐞
- **Lỗi:** Set 2 code mở combine tab 1 lần, ép xong 1 rada thì tab bị close, rada thứ 2 không ép được
- **Stat cần đạt:** Option 95 param=40 (40% hút HP), Option 96 param=10 (10% hút KI)
- **Fix:** Chuyển sang while loop:
  ```
  while True:
      tìm 1 rada chưa có 95/96
      nếu hết → break
      kiểm tra material (2x442 + 8x441)
      mở tab combine MỚI cho copy này
      ép 2x442 + 8x441
  ```
- **Cải tiến `_rada_combine_one`:**
  - Thêm param `use_item_upgrade` — biết dùng tab nào khi retry
  - Retry > 0 thì tự động reopen tab (tránh close tab giữa chừng)

### 9. **Duplicate code `_is_upgraded`** 🐞
- **Lỗi:** Hàm `_is_upgraded()` giống hệt nhau trong cả `step_equip_master.py` và `step_equip_pet.py`
- **Fix:** 
  - Thêm `is_item_upgraded()` vào `services/combine_service.py`
  - Cả 2 file import từ chỗ dùng chung
  - `ITEM_12` import dư trong `step_equip_master.py` đã xóa

---

## THAY ĐỔI CODE (2026-06-15 Session 2)

### `services/combine_service.py` — Mới
- **`open_item_upgrade()`**: Mở tab combine khác cho items 441/442 (ID>20 không dùng được "Ép sao trang bị")
  - Path 1: "Nâng cấp vật phẩm" (direct)
  - Path 2: "Chức năng pha lê" → "Pha lê hóa trang bị"
  - Path 3: "Chức năng pha lê" → fallback (non-"ép sao")
- **`is_item_upgraded(item)`**: Hàm dùng chung kiểm tra item đã ép

### `commands/setup/step_equip_master.py` — Fix
- `use_item(1, 1, ...)` → `use_item(0, 1, ...)`
- Import `is_item_upgraded` từ services thay vì local copy

### `commands/setup/step_equip_pet.py` — Refactor
- Import `is_item_upgraded` từ services thay vì local copy
- Xóa import `ITEM_12` dư

### `commands/setup/step_upgrade.py` — Rewrite Set 2
- While loop thay vì for loop trên list static
- Mở tab mới cho mỗi copy rada
- `_rada_combine_one` nhận tham số `use_item_upgrade` để reopen đúng tab
- Refresh inventory giữa mỗi lần ép
- Kiểm tra material (2x442 + 8x441) trước mỗi copy

### `commands/setup/step_santa_shop.py` — Mở rộng
- Mua 402x20, 403x20 (từ 6 lên 20)
- Sau khi mua, dùng mỗi loại 6 lần (use_item type=0)
- Import `SANTA_ITEM_USE`

### `commands/setup/constants.py` — Mở rộng
- `SANTA_ITEM_DAC_BIET`: 402(6→20), 403(6→20)
- Thêm `SANTA_ITEM_USE = [(402, 6), (403, 6)]`

---

## CHECK RADA OPTIONS (acc 06 - 2026-06-15)

Chạy `tests/check_rada_options.py` trên acc poopooi06:

| Vị trí | Item 12 | Option 95 (hút HP) | Option 96 (hút KI) |
|--------|---------|-------------------|-------------------|
| Balo idx 23 | Default rada | ❌ | ❌ |
| Balo idx 27 | Default rada | ❌ | ❌ |
| Body Master | — | (trống) | (trống) |
| PetBody[4] | Đã ép | ✅ 40% | ✅ 10% |

**Default rada options:** `[14:2], [107:10], [30:0], [131:0], [143:0], [40:0]`

**Kết luận:**
- 2 rada trong balo là hàng default chưa ép (không có 95/96) — step 12 chưa ép được
- Master không có đồ — step 13 không hoạt động vì sai use_item type
- Pet có 1 rada đã ép từ lần test trước khi reset

---

## TEST RESULTS (2026-06-15)

### Full test acc 06 (old code - trước fix)
- All 14 steps thành công (syntax pass)
- Nhưng rada không ép được, master không có đồ
- Pet vẫn có rada cũ từ trước

---

## CẤU TRÚC FILE HIỆN TẠI (bổ sung)

```
commands/setup/
├── ...
├── step_equip_master.py             ← MỚI: mặc đồ cho sư phụ
├── step_equip_pet.py                ← MỚI: mặc đồ cho đệ tử
└── ...

services/
├── ...
├── combine_service.py               ← THÊM: open_item_upgrade(), is_item_upgraded()
└── ...

tests/
├── run_full_setup_06.py             ← Test full 14 steps cho acc 06
├── check_rada_options.py            ← Diagnostic: check rada options
└── ...
```

---

### 18. **Thêm show equip_master & equip_pet vào help + autocomplete** 🆕
- **`utils/autocomplete.py`**: Thêm `equip_master`, `body_master`, `equip_pet`, `body_pet` vào danh sách gợi ý của `show` → gõ `show ` + Tab sẽ thấy
- **`ui/help_display.py`**: Thêm 3 dòng help cho `show equip`, `show equip_master`, `show equip_pet`

---

## LỆNH THƯỜNG DÙNG

```
setup_accounts 5 10              # Chạy setup từ step 1
setup_accounts 5 10 start_step=7 # Chạy từ step 7 (Mua bùa)
setup_accounts 5 10 reset        # Reset trạng thái
show equip                       # Xem tổng quan ép sao + body sư phụ/đệ tử
show equip_master                # Xem chi tiết trang bị sư phụ đang mặc
show equip_pet                   # Xem chi tiết trang bị đệ tử đang mặc
show balo                        # Xem hành trang
python tests/check_rada_options.py  # Check options rada acc 06
python tests/run_full_setup_06.py   # Full setup test acc 06
```
