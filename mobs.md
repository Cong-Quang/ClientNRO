# 📋 Phân Tích Toàn Diện Hệ Thống Quái (Mob) trong Game NRO

> **Phân tích từ:** Mã nguồn C# GameGoc + Mod + Python Bot  
> **Ngày:** 13/06/2026

---

## MỤC LỤC

1. [Tổng quan kiến trúc](#1-tổng-quan-kiến-trúc)
2. [Chức năng tàn sát (Auto-kill / Massacre)](#2-chức-năng-tàn-sát-auto-kill--massacre)
3. [Chức năng Radar / Show Mob](#3-chức-năng-radar--show-mob)
4. [Mod PickMob - Tự động đánh quái nâng cao](#4-mod-pickmob---tự-động-đánh-quái-nâng-cao)
5. [Mod Auto - Các chức năng tự động khác](#5-mod-auto---các-chức-năng-tự-động-khác)
6. [Boss Manager & Xmap](#6-boss-manager--xmap)
7. [Python Bot - Auto Attack từ bên ngoài](#7-python-bot---auto-attack-từ-bên-ngoài)
8. [Bảng tổng kết tất cả class liên quan](#8-bảng-tổng-kết-tất-cả-class-liên-quan)
9. [Gợi ý tối ưu & cải tiến](#9-gợi-ý-tối-ưu--cải-tiến)

---

## 1. Tổng quan kiến trúc

### 1.1 Cấu trúc dữ liệu Mob (Game Client C#)

```
GameScr.vMob (MyVector chứa Mob[])
  ├── Mob.mobId        -> ID duy nhất của quái (do server cấp)
  ├── Mob.templateId   -> ID loại quái (từ MobTemplate)
  ├── Mob.mobName      -> Tên quái (có thể null)
  ├── Mob.hp / maxHp   -> Máu hiện tại / tối đa
  ├── Mob.x / y        -> Tọa độ hiện tại
  ├── Mob.xFirst / yFirst -> Tọa độ ban đầu khi spawn
  ├── Mob.status       -> Trạng thái (0=chết, 1=chết bay, 2=đứng, 3=tấn công, 4=đứng bay, 5=đi, 6=rơi, 7=injure)
  ├── Mob.isBoss       -> Flag boss
  ├── Mob.levelBoss    -> Cấp độ boss (0=thường)
  ├── Mob.isMobMe      -> Quái của bản thân (mobMe)
  ├── Mob.sys          -> Hệ (0=Trái Đất, 1=Namek, 2=Xayda)
  └── Mob.isDie        -> Trạng thái chết
```

### 1.2 MobTemplate (Định nghĩa loại quái)

```csharp
MobTemplate {
    mobTemplateId  -> ID loại quái
    rangeMove      -> Phạm vi di chuyển
    speed          -> Tốc độ
    type           -> 0=đứng yên, 1=đi bộ, 4=biết bay
    hp             -> Máu mặc định
    name           -> Tên loại quái
    data           -> EffectData (ảnh, frame)
    dartType       -> Loại đạn (nếu đánh xa)
}
```

### 1.3 MonsterType (Mod Constants)

```csharp
MonsterType {
    Stand = 0  -> Quái đứng yên (cọc gỗ, Destron Gas, ...)
    Walk  = 1  -> Quái đi bộ (lợn rừng, Bulon, Robot thép, ...)
    Fly   = 4  -> Quái bay (Thằn lằn bay, Rồng bay, ...)
}
```

---

## 2. Chức năng tàn sát (Auto-kill / Massacre)

### 2.1 Game Client gốc (GameScr.cs)

#### autoPlay() - Hàm tự động đánh gốc của game

**File:** `GameScr.cs` → method `autoPlay()`

**Luồng xử lý:**

```
1. Kiểm tra timeSkill > 0 → giảm dần
2. Kiểm tra canAutoPlay, isChangeZone, trạng thái chết/charge → return nếu không hợp lệ
3. Duyệt GameScr.vMob để kiểm tra còn mob sống không
4. Kiểm tra và xin đậu thần nếu hết (gameTick % 150 == 0)
5. Auto uống đậu nếu HP/MP < 20%
6. Tìm mob:
   - Nếu mobFocus == null hoặc là mobMe:
     → Duyệt vMob, tìm mob có status != 0 && status != 1 && hp > 0 && !isMobMe
     → Gán mobFocus = mob tìm được, teleport cx,cy = mob.x, mob.y
7. Nếu mob đã chết → clear mobFocus
8. Chọn skill:
   - Touch: duyệt onScreenSkill, ưu tiên cooldown thấp nhất
   - Phím: duyệt keySkill, ưu tiên cooldown thấp nhất
9. Gọi doDoubleClickToObj(mobFocus) để tấn công
```

#### isAttack() - Kiểm tra có thể tấn công không

**File:** `GameScr.cs`

Kiểm tra hàng loạt điều kiện:
- Không có skill paint đang chạy
- Mob không chết (status != 1 && status != 0)
- Nếu là BigBoss, check status != 4
- Check `isMeCanAttackMob()` → kiểm tra flag PK
- Check đủ MP
- Check khoảng cách với skill.dx/dy

#### isMeCanAttackMob()

```csharp
- Nếu cTypePk == 5 (tự do) → true
- Nếu đang flag hòa bình && !mob.isMobMe → false
- Nếu mob là mobMe của mình → false
- Tìm Char sở hữu mob (findCharInMap): nếu không có → true
- Nếu chủ mob flag tự do → true
- Nếu có thể đánh chủ mob → true
```

#### isAttacPlayerStatus() - Kiểm tra flag PK

Kiểm tra `cTypePk`:
- 5 = Tự do (đánh được tất cả)
- 1 = Phe (đánh phe khác)
- 2 = Bang (đánh bang khác)
- 3 = Thi đấu
- 4 = Luyện tập

#### char.findClickToMOB() - Click chọn quái

**File:** `GameScr.cs`

```
1. Duyệt toàn bộ vMob
2. Lọc mob.isInvisible() + mob.isMobMe
3. Tính khoảng cách (|px-x| + |py-y|) theo pixel
4. Chọn mob gần nhất với click position
```

#### char.searchFocus() - Auto focus mục tiêu

**File:** `Char.cs`

Tự động focus vào mob/npc/char/item gần nhất khi di chuyển hoặc đứng gần.

#### char.focusManualTo() - Focus thủ công

Khi click vào đối tượng, gán mobFocus = mob, đồng thời dừng di chuyển.

### 2.2 Các sub-class Boss đặc biệt

#### NewBoss (kế thừa Mob)

**File:** `NewBoss.cs`

- Boss có animation riêng qua `frameArr` (17 loại frame: stand=0, moveFra=1, attack1-10=2-11, hurt=12, die=13, fly=14, adddame=15, typeEff=16)
- Có `xTo/yTo` để di chuyển mượt
- `move(short xMoveTo, short yMoveTo)` → di chuyển boss đến tọa độ
- `setAttack(Char[] cAttack, int[] dame, sbyte type)` → đánh nhiều mục tiêu cùng lúc

#### BigBoss, BigBoss2, BachTuoc

Các lớp boss riêng với animation và cơ chế đặc biệt.

---

## 3. Chức năng Radar / Show Mob

### 3.1 RadarScr (UI Radar)

**File:** `RadarScr.cs`

**Class:** `RadarScr : mScreen`

Hệ thống radar là giao diện dạng thẻ bài (card system) do server gửi dữ liệu về.

**Cấu trúc UI:**
```
┌─────────────────────────────────┐
│        Tên thẻ (focus_card)      │
│  ┌─────────────────────────┐    │
│  │   Animation Mob/Nhân vật │    │
│  │   (paintInfo)            │    │
│  └─────────────────────────┘    │
│  Rank: ★★★                    │
│  Thanh tiến trình (amount/max)  │
│  ┌─────────────────────────┐    │
│  │  Mô tả chi tiết (cp)     │    │
│  └─────────────────────────┘    │
│  ◀ [1] [2] [3] [4] [5] ▶     │
│    [Đổi] [Sử dụng] [Quay lại]   │
└─────────────────────────────────┘
```

**Các method chính:**
- `SetRadarScr(MyVector list, int num, int numMax)` → Khởi tạo radar với danh sách thẻ
- `updateKey()` → Xử lý phím điều hướng
- `doChangeUI()` → Chuyển đổi giữa "Tất cả" và "Đang sử dụng"
- `listIndex()` → Cập nhật danh sách 5 thẻ hiển thị
- `doClickArrow(dir)` → Chuyển trang

**Luồng dữ liệu:**
```
1. Server gửi danh sách Info_RadaScr qua message
2. Client lưu vào RadarScr.list (MyVector)
3. RadarScr.SetRadarScr() → chia trang, set index
4. Mỗi frame update: focus_card = Info_RadaScr.GetInfo(list, index[indexFocus])
5. Paint: vẽ thông tin thẻ + 5 icon nhỏ phía dưới
```

### 3.2 Info_RadaScr (Thông tin thẻ)

**File:** `Info_RadaScr.cs`

```csharp
Info_RadaScr {
    TYPE_MONSTER = 0   -> Loại quái
    TYPE_CHARPART = 1  -> Loại trang bị

    id              -> ID thẻ
    no              -> Số thứ tự
    idIcon          -> ID icon nhỏ
    rank            -> Hạng (0-6)
    typeMonster     -> Loại (0=quái, 1=trang bị)
    name            -> Tên
    info            -> Mô tả
    level           -> Cấp độ
    isUse           -> Đang sử dụng?
    amount/max_amount -> Số lượng sưu tập
    mobInfo         -> Mob template để render animation
    charInfo        -> Char info để render nhân vật
    itemOption[]    -> Options của thẻ
    cp (ChatPopup)  -> Nội dung mô tả chi tiết
}
```

**Method quan trọng:**
- `paintInfo(g, x, y)` → Vẽ animation quái hoặc nhân vật
- `addItemDetail()` → Tạo nội dung mô tả chi tiết từ itemOption
- `SetEff()` → Tạo hiệu ứng khi đã sưu tập đủ
- `GetInfo(MyVector vec, int id)` → Tìm thẻ theo ID

---

## 4. Mod PickMob - Tự động đánh quái nâng cao

### 4.1 PickMobController (Điều khiển chính)

**File:** `Mod/PickMob/PickMobController.cs`

**Class:** `PickMobController`

**Chức năng chính:**
1. `autoAttack()` → Tự động đánh quái
2. `autoPickItem()` → Tự động nhặt vật phẩm
3. `autoAvoidSuperMob()` → Né siêu quái

**Cấu trúc điều khiển:**
```csharp
PickMobController {
    // Danh sách quái được phép đánh
    static List<int> monsterIds            -> Danh sách ID quái
    static List<int> monsterTypeIds        -> Danh sách loại quái
    static List<int> skillIds              -> Danh sách skill sử dụng

    // Danh sách vật phẩm
    static List<int> autoPickItemIds       -> Chỉ nhặt các item này
    static List<int> autoPickItemTypeIds   -> Chỉ nhặt loại item này
    static List<int> blockPickItemIds      -> Chặn không nhặt
    static List<int> blockPickItemTypeIds  -> Chặn không nhặt loại

    // Cấu hình
    static bool isAutoMob                  -> Bật tàn sát
    static bool isAutoPickItem             -> Bật tự động nhặt
    static bool isAvoidSuperMob            -> Né siêu quái
    static bool isVDH                      -> Vượt địa hình
    static bool isOnlyPickMyItem           -> Chỉ nhặt đồ mình
    static bool isLimitedPick              -> Giới hạn số lần nhặt
    static bool isAttackBySendCommand      -> Đánh bằng lệnh (ko cần click)
}
```

**Cơ chế autoAttack():**
```
1. Kiểm tra isAutoMob, trạng thái nhân vật
2. Tìm mob gần nhất thỏa mãn:
   - status > 1 (còn sống)
   - hp > 0
   - Nếu có monsterIds: chỉ đánh mob trong danh sách
   - Nếu có monsterTypeIds: chỉ đánh loại quái trong danh sách
   - Nếu isAvoidSuperMob: bỏ qua siêu quái (levelBoss > 0)
3. Chọn skill tốt nhất từ skillIds (hoặc mặc định)
4. Tự động di chuyển đến mob
5. Tấn công
```

### 4.2 Pk9rPickMob (Phiên bản Pk9r)

**File:** `Mod/PickMob/Pk9rPickMob.cs`

Là implementation cụ thể của PickMob, có thể có các cải tiến riêng so với bản gốc.

### 4.3 Các lệnh chat (từ README)

| Lệnh | Chức năng |
|------|-----------|
| `ts` | Bật/Tắt tự động đánh quái |
| `nsq` | Bật/Tắt né siêu quái |
| `addmX` | Thêm/Xóa quái ID X vào danh sách |
| `addtmX` | Thêm/Xóa loại quái X |
| `clrm` | Xóa danh sách tàn sát |
| `skillX` | Thêm skill thứ X vào danh sách |
| `skillidX` | Thêm skill ID X |
| `clrs` | Reset danh sách skill mặc định |
| `vdh` | Bật/Tắt vượt địa hình |
| `add` | Thêm quái/vật phẩm đang trỏ vào |
| `addt` | Thêm loại quái/vật phẩm đang trỏ |

---

## 5. Mod Auto - Các chức năng tự động khác

### 5.1 AutoSendAttack

**File:** `Mod/Auto/AutoSendAttack.cs`

**Chức năng:** Gửi lệnh tấn công tới mob mục tiêu mà không cần click chuột. Sử dụng `Service.gI().sendPlayerAttack()`.

### 5.2 AutoGoback

**File:** `Mod/Auto/AutoGoback.cs`

**Chức năng:** Tự động quay lại vị trí cũ sau khi chết.

**Chế độ:**
- `GoBackToWhereIDied` → Quay lại chỗ chết
- `GoBackToFixedLocation` → Quay lại tọa độ cố định đã lưu

### 5.3 AutoSkill

**File:** `Mod/Auto/AutoSkill.cs`

**Chức năng:** Tự động hồi sinh (trị thương) cho đồng đội.

**TargetMode:**
- Everyone: Trị tất cả
- OnlyClanMembers: Chỉ thành viên bang
- OnlyPet: Chỉ đệ tử
- OnlyMyPet: Chỉ đệ tử của mình

### 5.4 AutoLogin

**File:** `Mod/Auto/AutoLogin.cs`

Tự động đăng nhập lại khi mất kết nối và quay về vị trí cũ.

### 5.5 AutoTrainNewAccount

**File:** `Mod/Auto/AutoTrainNewAccount.cs`

Tự động train tài khoản mới đến khi vào bang.

### 5.6 AutoPean

**File:** `Mod/Auto/AutoPean.cs`

Tự động xin/vặt/cho đậu thần.

### 5.7 ThreadAction Framework

**File:** `Mod/ModHelper/ThreadAction.cs`, `ThreadActionUpdate.cs`

Cung cấp cơ chế thread cho các chức năng tự động:
- `ThreadAction<T>` → Singleton thread base class
- `ThreadActionUpdate<T>` → Thread lặp vô hạn với interval

---

## 6. Boss Manager & Xmap

### 6.1 Boss Manager (Python)

**File:** `logic/boss_manager.py`

Theo dõi và quản lý boss:
- `boss_manager.py` chứa danh sách boss theo map
- Kết nối với `controller.mobs` để detect boss spawn
- Sử dụng `auto_boss.py` để tự động săn boss

### 6.2 Xmap Controller (C# Mod)

**File:** `Mod/Xmap/XmapController.cs`

**Chức năng:** Tự động di chuyển giữa các map.
- Sử dụng thuật toán A* (tùy chọn)
- Dùng capsule để dịch chuyển
- Timeout trước khi chuyển sang chế độ dịch chuyển

### 6.3 Xmap (Python)

**File:** `logic/xmap.py`

Phiên bản Python của Xmap → tự động chuyển map qua các waypoint.

---

## 7. Python Bot - Auto Attack từ bên ngoài

### 7.1 auto_play.py

**File:** `logic/auto_play.py`

Class `AutoPlay` với method chính `tansat()`:

```python
def tansat(self):
    """Vòng lặp tàn sát chính"""
    1. Kiểm tra nhân vật chết → hồi sinh
    2. Kiểm tra char_focus (boss/player) → đánh trước
    3. Xác thực mob_focus hiện tại:
       - Lấy mob từ controller.mobs.get(mob_focus.mob_id)
       - Kiểm tra status > 1 AND hp > 0
    4. Nếu mob_focus không hợp lệ → tìm mob mới:
       - Duyệt toàn bộ controller.mobs.items()
       - Lọc: status > 1, hp > 0, không phải pet
       - Lọc theo target_mobs set (nếu có)
       - Chọn mob gần nhất (Euclidean distance)
    5. Teleport đến mob (gán cx, cy = mob.x, mob.y)
    6. Gửi char_move() → gửi send_player_attack()
```

**Phương thức bổ trợ:**
- `_attack_char_focus()` → Đánh boss/player focus
- `find_best_skill()` → Chọn skill tối ưu nhất
- `_calculate_distance(x1, y1, x2, y2)` → Tính khoảng cách

### 7.2 auto_attack.py

**File:** `logic/auto_attack.py`

Class `AutoAttack` với priority system:
```python
AutoAttack {
    priority_mode: "nearest" | "boss_first" | "name_match"
    
    _update():
        - Chạy theo interval
        - Dựa vào priority để chọn mục tiêu
        - nearest: mob gần nhất
        - boss_first: ưu tiên boss
        - name_match: match theo tên
}
```

### 7.3 target_utils.py

**File:** `logic/target_utils.py`

```python
focus_nearest_mob(controller, target_mobs=None)
    → Tìm mob gần nhất (Euclidean)

focus_by_id(controller, mob_id=None, char_id=None)
    → Focus mob theo ID (O(1) lookup)

focus_by_name(controller, name, target_type="both", max_distance=100)
    → Fuzzy match tên (IN thay vì ==)
    → "Fide" match được "Fide 1", "Fide 2"
```

### 7.4 auto_boss.py

**File:** `logic/auto_boss.py`

Tự động săn boss dựa trên dữ liệu từ `boss_manager.py` và `mob_data.txt`.

### 7.5 model/game_objects.py

**File:** `model/game_objects.py`

```python
class MobObject:
    mob_id          # ID quái (server)
    template_id     # ID loại quái
    name            # Tên
    hp              # Máu
    max_hp          # Máu tối đa
    x, y            # Tọa độ
    status          # Trạng thái
    is_boss         # Flag boss
```

### 7.6 model/map_objects.py

**File:** `model/map_objects.py`

Bản đồ và dữ liệu mob trong map.

---

## 8. Bảng tổng kết tất cả class liên quan

### 8.1 Game Client C# (gốc)

| File | Class/Method | Vai trò |
|------|-------------|---------|
| `Mob.cs` | `Mob` | Class quái chính (fields: mobId, templateId, hp, x, y, status, isBoss, isDie, ...) |
| `Mob.cs` | `Mob.startDie()` | Xử lý quái chết |
| `Mob.cs` | `Mob.setAttack(Char)` | Quái tấn công nhân vật |
| `Mob.cs` | `Mob.attackOtherMob(Mob)` | Quái đánh quái khác |
| `Mob.cs` | `Mob.update()` | Update chính theo status |
| `Mob.cs` | `Mob.updateMobStandWait()` | Đứng chờ |
| `Mob.cs` | `Mob.updateMobWalk()` | Đi bộ |
| `Mob.cs` | `Mob.updateMobAttack()` | Tấn công |
| `Mob.cs` | `Mob.updateHp_bar()` | Cập nhật thanh máu |
| `Mob.cs` | `Mob.isPaint()` | Kiểm tra có vẽ được không |
| `Mob.cs` | `Mob.isUpdate()` | Kiểm tra có update được không |
| `Mob.cs` | `Mob.checkIsBoss()` | Kiểm tra có phải boss |
| `MobTemplate.cs` | `MobTemplate` | Template định nghĩa loại quái |
| `NewBoss.cs` | `NewBoss : Mob` | Boss class với frameArr 17 loại |
| `Char.cs` | `Char.mobFocus` | Focus mob hiện tại |
| `Char.cs` | `Char.searchFocus()` | Tự động tìm focus |
| `Char.cs` | `Char.focusManualTo()` | Focus thủ công |
| `GameScr.cs` | `GameScr.vMob` | Vector chứa tất cả mob trong map |
| `GameScr.cs` | `GameScr.autoPlay()` | Auto play gốc của game |
| `GameScr.cs` | `GameScr.isAttack()` | Kiểm tra có thể tấn công |
| `GameScr.cs` | `GameScr.isMeCanAttackMob()` | Kiểm tra flag PK |
| `GameScr.cs` | `GameScr.findClickToMOB()` | Click chọn quái |
| `GameScr.cs` | `GameScr.checkAuto()` | Tự động bắn khi auto > 0 |
| `RadarScr.cs` | `RadarScr` | UI Radar (card system) |
| `Info_RadaScr.cs` | `Info_RadaScr` | Thông tin thẻ radar |
| `Position.cs` | `Position` | Class tọa độ đơn giản |

### 8.2 Mod C# (PickMob)

| File | Class | Vai trò |
|------|-------|---------|
| `Mod/PickMob/PickMobController.cs` | `PickMobController` | Điều khiển auto attack/pick item |
| `Mod/PickMob/Pk9rPickMob.cs` | `Pk9rPickMob` | Implementation cụ thể |
| `Mod/Auto/AutoSendAttack.cs` | `AutoSendAttack` | Gửi lệnh tấn công không cần click |
| `Mod/Auto/AutoGoback.cs` | `AutoGoback` | Quay lại chỗ cũ sau khi chết |
| `Mod/Auto/AutoSkill.cs` | `AutoSkill` | Tự động trị thương |
| `Mod/Constants/MonsterType.cs` | `MonsterType` | Hằng số loại quái |
| `Mod/Xmap/XmapController.cs` | `XmapController` | Tự động chuyển map |

### 8.3 Python Bot

| File | Class/Function | Vai trò |
|------|---------------|---------|
| `logic/auto_play.py` | `AutoPlay.tansat()` | Main attack loop |
| `logic/auto_play.py` | `AutoPlay.find_best_skill()` | Chọn skill tối ưu |
| `logic/auto_attack.py` | `AutoAttack._update()` | Auto attack priority system |
| `logic/target_utils.py` | `focus_nearest_mob()` | Tìm mob gần nhất |
| `logic/target_utils.py` | `focus_by_id()` | Focus theo ID |
| `logic/target_utils.py` | `focus_by_name()` | Focus theo tên (fuzzy) |
| `logic/auto_boss.py` | `AutoBoss` | Tự động săn boss |
| `logic/boss_manager.py` | `BossManager` | Quản lý boss theo map |
| `logic/xmap.py` | `Xmap` | Tự động chuyển map |
| `model/game_objects.py` | `MobObject` | Data class mob |
| `model/map_objects.py` | Map objects | Dữ liệu map |

---

## 9. Gợi ý tối ưu & cải tiến

### 9.1 Tìm kiếm mob hiệu quả hơn

**Hiện tại:** Bot Python duyệt toàn bộ `controller.mobs.items()` mỗi lần tìm.

**Gợi ý:** Dùng grid-based spatial hash để tìm mob gần nhất trong O(1):
```python
# Ý tưởng: chia map thành grid cells
grid_size = 100  # pixel
mob_grid = defaultdict(list)

def update_grid(mobs):
    for mob in mobs:
        cell_x = mob.x // grid_size
        cell_y = mob.y // grid_size
        mob_grid[(cell_x, cell_y)].append(mob)

def find_nearest_mob(char_x, char_y):
    cell_x, cell_y = char_x // grid_size, char_y // grid_size
    # Chỉ check 9 cells xung quanh
    for dx, dy in [(0,0), (-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]:
        for mob in mob_grid[(cell_x+dx, cell_y+dy)]:
            # tính distance
```

### 9.2 Cải thiện fuzzy name matching

**Hiện tại:** Dùng `in` để match tên (dễ false positive).

**Gợi ý:** Dùng `difflib` hoặc `rapidfuzz`:
```python
from rapidfuzz import fuzz, process

def focus_by_name_fuzzy(controller, name, threshold=70):
    mobs = controller.mobs.values()
    names = {m.mob_name: m for m in mobs if m.mob_name}
    best_match = process.extractOne(name, names.keys(), scorer=fuzz.WRatio)
    if best_match and best_match[1] >= threshold:
        return names[best_match[0]]
```

### 9.3 Teleport mượt mà (tránh bị dirtyPos)

**Hiện tại:** Bot gán `cx, cy = mob.x, mob.y` → dễ bị server phát hiện dirty position.

**Gợi ý:** Dùng `currentMovePoint` để di chuyển từ từ:
```python
def teleport_smooth(controller, target_x, target_y, steps=5):
    current_x, current_y = controller.char.cx, controller.char.cy
    for i in range(1, steps + 1):
        intermediate_x = current_x + (target_x - current_x) * i // steps
        intermediate_y = current_y + (target_y - current_y) * i // steps
        controller.char.cx = intermediate_x
        controller.char.cy = intermediate_y
        controller.service.char_move()
        time.sleep(0.05)
```

### 9.4 Kiểm tra HP/Status chính xác hơn

**Hiện tại:** Bot kiểm tra `hp > -1`, game dùng `status == 0 || status == 1` cho chết.

**Gợi ý:** Kết hợp cả 2 điều kiện:
```python
def is_mob_alive(mob):
    return mob.status > 1 and mob.hp > 0 and not mob.is_die
```

### 9.5 Priority system mở rộng

Thêm các chế độ ưu tiên:
```python
class PriorityMode(Enum):
    NEAREST = "nearest"          # Gần nhất
    BOSS_FIRST = "boss_first"    # Boss trước
    NAME_MATCH = "name_match"    # Theo tên
    LOWEST_HP = "lowest_hp"      # Máu thấp nhất
    HIGHEST_LEVEL = "highest_level" # Cấp cao nhất
    BY_TYPE = "by_type"          # Theo loại quái
```

### 9.6 Tích hợp thông báo Boss

Sử dụng `NotificationHandler.process_server_message()` và `check_boss_notification()` để phát hiện boss spawn và tự động chuyển map đến boss.

---

## Phụ lục: Các hằng số trạng thái Mob

```csharp
// Mob status
MA_INHELL = 0      // Trong địa ngục (chết)
MA_DEADFLY = 1     // Chết bay
MA_STANDWAIT = 2   // Đứng chờ
MA_ATTACK = 3      // Đang tấn công
MA_STANDFLY = 4    // Đứng bay
MA_WALK = 5        // Đi
MA_FALL = 6        // Rơi
MA_INJURE = 7      // Bị thương

// Mob type (template)
TYPE_DUNG = 0      // Đứng yên
TYPE_DI = 1        // Đi bộ
TYPE_NHAY = 2      // Nhảy
TYPE_LET = 3       // Lết
TYPE_BAY = 4       // Bay
TYPE_BAY_DAU = 5   // Bay đậu

// Mob gender (hệ)
SYS_TRAIDAT = 0
SYS_NAMEC = 1
SYS_XAYDA = 2

// Mob movement types (MonsterType - Mod)
Stand = 0   // Đứng yên (cọc gỗ)
Walk = 1    // Đi bộ (lợn rừng)
Fly = 4     // Bay (thằn lằn bay)
```
