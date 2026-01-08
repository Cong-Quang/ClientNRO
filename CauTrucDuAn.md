# Cấu Trúc Dự Án ClientNRO

## Tổng Quan
Dự án ClientNRO là một game client automation tool được viết bằng Python, hỗ trợ đa tài khoản, AI agent, và nhiều tính năng tự động hóa.

**Tổng số file Python:** 108 files

---

## 📁 Cấu Trúc Thư Mục

```
ClientNRO/
├── main.py                      # File chính - Entry point của ứng dụng
├── config.py                    # Cấu hình toàn cục
├── accounts.txt                 # Danh sách tài khoản
├── proxy.txt                    # Danh sách proxy
├── mob_data.txt                 # Dữ liệu quái vật
├── ai_core/                     # Module AI (Neural Network)
├── commands/                    # Lệnh điều khiển chung
├── targeted_commands/           # Lệnh điều khiển theo target
├── constants/                   # Hằng số
├── controller/                  # Controller và message handlers
├── core/                        # Core classes (Account, AccountManager)
├── handlers/                    # AI command handler
├── logic/                       # Game logic (auto play, auto boss, etc.)
├── logs/                        # Logger configuration
├── model/                       # Game objects models
├── network/                     # Network layer (Session, Message, Service)
├── services/                    # Game services (Movement, Pet)
├── train/                       # AI training
├── ui/                          # UI display components
├── utils/                       # Utilities
└── test_*.py                    # Test files
```

---

## 📄 File Chính

### `main.py`
**Mô tả:** Entry point của ứng dụng, quản lý command loop và khởi tạo hệ thống

**Functions:**
- `load_mob_names()` - Tải danh sách tên quái vật từ file
- `clean_pycache()` - Tìm và xóa tất cả thư mục __pycache__
- `load_proxies()` - Đọc danh sách proxy từ file proxy.txt và chuyển đổi sang định dạng URL chuẩn
- `command_loop(manager: AccountManager)` - Vòng lặp lệnh tương tác chính để quản lý nhiều tài khoản
- `main()` - Hàm main khởi tạo và chạy ứng dụng

### `config.py`
**Mô tả:** Cấu hình toàn cục cho ứng dụng

**Class:**
- `Config` - Chứa tất cả cấu hình:
  - `DEFAULT_CHAR_GENDER` - Giới tính nhân vật mặc định (0: Trái Đất, 1: Namek, 2: Xayda)
  - `DEFAULT_CHAR_HAIR` - ID kiểu tóc mặc định
  - `HOST` - Địa chỉ server
  - `PORT` - Cổng server
  - `VERSION` - Phiên bản client
  - `MAX_ACCOUNTS` - Số tài khoản tối đa chạy đồng thời
  - `AUTO_LOGIN` - Tự động đăng nhập lại khi mất kết nối
  - `DEFAULT_LOGIN` - Danh sách index tài khoản login mặc định
  - `LOGIN_BLACKLIST` - Danh sách tài khoản bỏ qua khi login all
  - `USE_LOCAL_IP_FIRST` - Ưu tiên IP local trước khi dùng proxy
  - `ACCOUNTS` - Danh sách tài khoản
  - `AI_ENABLED` - Bật/tắt AI
  - `AI_WEIGHTS_PATH` - Đường dẫn weights của neural network
  - `AI_STATE_DIM` - Số chiều state vector
  - `AI_ACTION_COUNT` - Số lượng actions
  - `AI_DECISION_INTERVAL` - Khoảng thời gian giữa các quyết định AI

---

## 📁 ai_core/ - AI Neural Network Module

### `brain.py`
**Class:**
- `InferenceEngine` - Pure Python neural network inference engine
  - `__init__()` - Khởi tạo engine
  - `set_weights_from_dict()` - Load weights từ dictionary
  - `load_weights()` - Load neural network weights từ JSON file
  - `_init_random_weights()` - Khởi tạo random weights cho testing
  - `_forward_pass()` - Forward pass qua network
  - `_linear()` - Linear transformation: y = Wx + b
  - `_relu()` - ReLU activation
  - `_softmax()` - Softmax activation với numerical stability
  - `_apply_mask()` - Apply action mask lên logits
  - `get_model_info()` - Trả về thông tin architecture và status
  - `_count_parameters()` - Đếm tổng số trainable parameters

### `action_decoder.py`
**Class:**
- `ActionDecoder` - Giải mã AI action index thành game commands
  - `__init__(controller, service)` - Khởi tạo với controller và service
  - `_find_nearest_alive_mob()` - Tìm quái vật sống gần nhất
  - `decode(action_index)` - Giải mã action index thành lệnh game

**Action Space:** 32 actions được tổ chức theo category

### `state_builder.py`
**Class:**
- `StateBuilder` - Chuyển đổi game state thành normalized feature vector
  - `__init__()` - Khởi tạo
  - `build_state(controller)` - Build temporal state vector (60D: 3 frames x 20D)
  - `_build_single_frame()` - Build single 20D state frame
  - `_find_nearest_mob()` - Tìm quái vật gần nhất và khoảng cách
  - `_count_mobs_in_range()` - Đếm quái vật sống trong range
  - `_normalize_ratio()` - Normalize ratio về [0, 1]
  - `_normalize_coord()` - Normalize tọa độ về [0, 1]
  - `_normalize_distance()` - Normalize khoảng cách về [-1, 1]
  - `_normalize_count()` - Normalize count về [0, 1]
  - `_get_average_mob_hp()` - Lấy HP ratio trung bình của quái trong range
  - `_get_recent_damage_taken()` - Lấy damage nhận trong 1 giây gần đây
  - `_get_recent_damage_dealt()` - Lấy damage gây ra trong 1 giây gần đây
  - `_get_time_since_kill()` - Lấy thời gian từ lần kill cuối
  - `record_damage_taken()` - Ghi nhận damage nhận
  - `record_damage_dealt()` - Ghi nhận damage gây ra
  - `record_kill()` - Ghi nhận mob kill

### `online_training.py`
**Class:**
- `OnlineTrainer` - Online training manager - Train AI trong khi bot chơi
  - `__init__(ai_agent, enable_training)` - Khởi tạo
  - `calculate_reward(state, action, next_state)` - Tính reward dựa trên state transition
  - `_train_batch()` - Single training batch (chạy trong thread pool)
  - `save_checkpoint()` - Lưu model weights hiện tại
  - `auto_save_loop()` - Auto-save model định kỳ
  - `get_stats()` - Lấy training statistics

### `shared_memory.py`
**Class:**
- `SharedMemory` - Singleton pattern shared memory cho multi-agent coordination
  - `__new__()` - Singleton constructor
  - `__init__()` - Khởi tạo
  - `broadcast_target()` - Broadcast target (boss, mob, location) cho tất cả bots
  - `get_shared_targets()` - Lấy danh sách shared targets từ bots khác
  - `clear_targets()` - Xóa tất cả shared targets
  - `set_team_leader()` - Chỉ định team leader
  - `get_team_leader()` - Lấy team leader hiện tại
  - `register_bot()` - Đăng ký bot với capabilities (tank/dps/support)
  - `get_team_formation()` - Lấy team formation hiện tại
  - `assign_to_group()` - Gán bot vào group (1-5 users/group)
  - `get_group_members()` - Lấy danh sách bots trong group
  - `set_active_groups()` - Set groups nào được AI điều khiển
  - `is_bot_in_active_group()` - Kiểm tra bot có trong active group không
  - `assign_zone()` - Gán bot vào zone thủ công
  - `get_zone_distribution()` - Lấy zone distribution cho map
  - `auto_distribute_zones()` - Auto phân bổ bots qua zones (round-robin)
  - `set_global_goal()` - Set global goal cho team
  - `get_current_goal()` - Lấy global goal hiện tại
  - `update_goal_progress()` - Cập nhật progress cho account
  - `clear_goal()` - Xóa goal hiện tại
  - `update_status()` - Cập nhật bot status
  - `get_team_status()` - Lấy status của tất cả bots

### `shared_training.py`
**Class:**
- `SharedTrainer` - Singleton Trainer thu thập experience từ TẤT CẢ agents
  - `__new__()` - Singleton constructor
  - `__init__()` - Khởi tạo
  - `enable()` - Bật shared training
  - `disable()` - Tắt shared training
  - `register_agent()` - Đăng ký agent để đóng góp vào shared training
  - `_train_batch()` - Chạy training batch (sync function)
  - `get_stats()` - Lấy shared training stats

---

## 📁 commands/ - Lệnh Điều Khiển Chung

### `base_command.py`
**Class:**
- `Command` - Base class cho tất cả commands
  - `execute(manager, args)` - Method phải override

### `autologin_command.py`
**Class:**
- `AutoLoginCommand` - Bật/tắt auto login
  - `execute(manager, args)` - Thực thi lệnh

### `clear_command.py`
**Class:**
- `ClearCommand` - Xóa màn hình console
  - `execute(manager, args)` - Thực thi lệnh

### `exit_command.py`
**Class:**
- `ExitCommand` - Thoát ứng dụng
  - `execute(manager, args)` - Thực thi lệnh

### `group_command.py`
**Class:**
- `GroupCommand` - Quản lý groups tài khoản
  - `execute(manager, args)` - Thực thi lệnh
  - `_list_groups()` - Liệt kê groups
  - `_create_group()` - Tạo group mới
  - `_delete_group()` - Xóa group
  - `_add_to_group()` - Thêm tài khoản vào group
  - `_remove_from_group()` - Xóa tài khoản khỏi group

### `help_command.py`
**Class:**
- `HelpCommand` - Hiển thị help
  - `execute(manager, args)` - Thực thi lệnh

### `list_command.py`
**Class:**
- `ListCommand` - Liệt kê tài khoản
  - `execute(manager, args)` - Thực thi lệnh

### `login_command.py`
**Class:**
- `LoginCommand` - Đăng nhập tài khoản
  - `execute(manager, args)` - Thực thi lệnh

### `logout_command.py`
**Class:**
- `LogoutCommand` - Đăng xuất tài khoản
  - `execute(manager, args)` - Thực thi lệnh

### `proxy_command.py`
**Class:**
- `ProxyCommand` - Quản lý proxy
  - `execute(manager, args)` - Thực thi lệnh
  - `_list_proxies()` - Liệt kê proxies

### `sleep_command.py`
**Class:**
- `SleepCommand` - Sleep một khoảng thời gian
  - `execute(manager, args)` - Thực thi lệnh

### `target_command.py`
**Class:**
- `TargetCommand` - Chọn target tài khoản hoặc group
  - `execute(manager, args)` - Thực thi lệnh

### `command_loader.py`
**Functions:**
- `load_commands()` - Load tất cả commands và trả về dictionary

---

## 📁 targeted_commands/ - Lệnh Điều Khiển Theo Target

### `base_targeted_command.py`
**Class:**
- `TargetedCommand` - Base class cho targeted commands
  - `execute(accounts, args)` - Method phải override

### `aiagent_command.py`
**Class:**
- `AIAgentCommand` - Bật/tắt AI Agent
  - `execute(accounts, args)` - Thực thi lệnh

### `andau_command.py`
**Class:**
- `AnDauCommand` - Lệnh ăn đậu
  - `execute(accounts, args)` - Thực thi lệnh

### `autoattack_command.py`
**Class:**
- `AutoAttackCommand` - Bật/tắt auto attack
  - `execute(accounts, args)` - Thực thi lệnh

### `autobomong_command.py`
**Class:**
- `AutoBoMongCommand` - Bật/tắt auto Bò Mộng
  - `execute(accounts, args)` - Thực thi lệnh

### `autoboss_command.py`
**Class:**
- `AutoBossCommand` - Bật/tắt auto boss
  - `execute(accounts, args)` - Thực thi lệnh

### `autopet_command.py`
**Class:**
- `AutoPetCommand` - Bật/tắt auto pet
  - `execute(accounts, args)` - Thực thi lệnh

### `autoplay_command.py`
**Class:**
- `AutoPlayCommand` - Bật/tắt auto play
  - `execute(accounts, args)` - Thực thi lệnh

### `blacklist_command.py`
**Class:**
- `BlacklistCommand` - Quản lý blacklist
  - `execute(accounts, args)` - Thực thi lệnh

### `findmob_command.py`
**Class:**
- `FindMobCommand` - Tìm quái vật
  - `execute(accounts, args)` - Thực thi lệnh

### `findnpc_command.py`
**Class:**
- `FindNPCCommand` - Tìm NPC
  - `execute(accounts, args)` - Thực thi lệnh

### `gomap_command.py`
**Class:**
- `GoMapCommand` - Di chuyển đến map
  - `execute(accounts, args)` - Thực thi lệnh

### `hit_command.py`
**Class:**
- `HitCommand` - Đánh quái/người chơi
  - `execute(accounts, args)` - Thực thi lệnh

### `khu_command.py`
**Class:**
- `KhuCommand` - Quản lý khu vực (zones)
  - `execute(accounts, args)` - Thực thi lệnh

### `logger_command.py`
**Class:**
- `LoggerCommand` - Bật/tắt logger
  - `execute(accounts, args)` - Thực thi lệnh

### `pet_command.py`
**Class:**
- `PetCommand` - Quản lý pet
  - `execute(accounts, args)` - Thực thi lệnh

### `show_command.py`
**Class:**
- `ShowCommand` - Hiển thị thông tin (char, bag, task, boss, pet, zone)
  - `execute(accounts, args)` - Thực thi lệnh

### `teleport_command.py`
**Class:**
- `TeleportCommand` - Teleport đến tọa độ
  - `execute(accounts, args)` - Thực thi lệnh

### `teleportnpc_command.py`
**Class:**
- `TeleportNPCCommand` - Teleport đến NPC
  - `execute(accounts, args)` - Thực thi lệnh

### `targeted_command_loader.py`
**Functions:**
- `load_targeted_commands()` - Load tất cả targeted commands

---

## 📁 constants/ - Hằng Số

### `cmd.py`
**Class:**
- `Cmd` - Chứa tất cả command codes của game protocol
  - `NOT_LOGIN = -29` - Command khi chưa login
  - `NOT_MAP = -28` - Command khi chưa vào map
  - `MESSAGE_SERVER = -4` - Message từ server
  - `GET_SESSION_ID = -127` - Lấy session ID
  - `LOGIN2 = -100` - Login command
  - Và nhiều constants khác...

---

## 📁 controller/ - Controller và Message Handlers

### `controller.py`
**Class:**
- `Controller` - Quản lý xử lý tin nhắn và trạng thái game cho một tài khoản
  - `__init__(account)` - Khởi tạo Controller
  - `toggle_auto_quest(enabled)` - Bật/tắt Auto Quest
  - `toggle_autoplay(enabled)` - Bật/tắt AutoPlay
  - `toggle_auto_pet(enabled)` - Bật/tắt AutoPet
  - `toggle_auto_attack(enabled)` - Bật/tắt Auto Attack
  - `toggle_auto_boss(enabled, boss_name)` - Bật/tắt Auto Boss
  - `toggle_ai_agent(enabled)` - Bật/tắt AI Agent
  - `on_message(msg)` - Chuyển tiếp tin nhắn đến handler tương ứng
  - `eat_pea()` - Tìm và ăn đậu khi HP/MP thấp
  - `find_item_in_bag(item_id)` - Tìm item trong hành trang
  - `use_item_by_id(item_id, action_type)` - Sử dụng item theo ID
  - `attack_nearest_mob()` - Tấn công quái vật gần nhất
  - `auto_upgrade_stats(target_hp, target_mp, target_sd)` - Tự động cộng điểm

### `handlers/base_handler.py`
**Class:**
- `BaseHandler` - Base class cho tất cả message handlers
  - `__init__(controller)` - Khởi tạo handler
  - `handle(msg)` - Xử lý message (phải override)

### `handlers/login_handler.py`
**Class:**
- `LoginHandler` - Xử lý login messages
  - `handle(msg)` - Xử lý login message

### `handlers/character_handler.py`
**Class:**
- `CharacterHandler` - Xử lý character messages
  - `handle(msg)` - Xử lý character message

### `handlers/map_handler.py`
**Class:**
- `MapHandler` - Xử lý map messages
  - `handle(msg)` - Xử lý map message

### `handlers/combat_handler.py`
**Class:**
- `CombatHandler` - Xử lý combat messages
  - `handle(msg)` - Xử lý combat message

### `handlers/player_handler.py`
**Class:**
- `PlayerHandler` - Xử lý player messages
  - `handle(msg)` - Xử lý player message

### `handlers/task_handler.py`
**Class:**
- `TaskHandler` - Xử lý task/quest messages
  - `handle(msg)` - Xử lý task message

### `handlers/inventory_handler.py`
**Class:**
- `InventoryHandler` - Xử lý inventory messages
  - `handle(msg)` - Xử lý inventory message

### `handlers/npc_handler.py`
**Class:**
- `NPCHandler` - Xử lý NPC messages
  - `handle(msg)` - Xử lý NPC message

### `handlers/notification_handler.py`
**Class:**
- `NotificationHandler` - Xử lý notification messages
  - `handle(msg)` - Xử lý notification message

### `handlers/misc_handler.py`
**Class:**
- `MiscHandler` - Xử lý miscellaneous messages
  - `handle(msg)` - Xử lý misc message

---

## 📁 core/ - Core Classes

### `account.py`
**Class:**
- `Account` - Đóng gói tất cả objects và data cho một game account session
  - `__init__(username, password, version, host, port, proxy)` - Khởi tạo account
  - `login()` - Kết nối và thực hiện login sequence
  - `handle_disconnect()` - Xử lý disconnect event, trigger auto-reconnect
  - `stop_tasks()` - Dừng tất cả asyncio tasks
  - `stop()` - Dừng tất cả tasks và disconnect session

**Attributes:**
- `username`, `password` - Thông tin đăng nhập
- `char` - Đối tượng nhân vật (Char)
- `pet` - Đối tượng pet (Pet)
- `controller` - Controller instance
- `session` - Network session
- `service` - Network service
- `is_logged_in` - Trạng thái đăng nhập
- `tasks` - Danh sách asyncio tasks

### `account_manager.py`
**Class:**
- `AccountManager` - Quản lý nhiều accounts
  - `__init__()` - Khởi tạo manager
  - `load_accounts()` - Load account credentials từ Config
  - `start_all()` - Bắt đầu login process cho tất cả accounts
  - `stop_all()` - Dừng tất cả accounts
  - `get_active_account_count()` - Đếm số accounts đang active
  - `get_target_accounts()` - Resolve command_target thành list accounts

**Attributes:**
- `accounts` - Danh sách Account objects
- `groups` - Dictionary các groups
- `command_target` - Target hiện tại (int index hoặc str group name)

---

## 📁 handlers/ - AI Command Handler

### `ai_command_handler.py`
**Class:**
- `AICommandHandler` - Xử lý AI commands từ natural language
  - Phân tích lệnh bằng AI và thực thi

---

## 📁 logic/ - Game Logic

### `auto_play.py`
**Class:**
- `AutoPlay` - Logic tự động chơi
  - `run()` - Vòng lặp auto play chính

### `auto_attack.py`
**Class:**
- `AutoAttack` - Logic tự động đánh
  - `run()` - Vòng lặp auto attack

### `auto_boss.py`
**Class:**
- `AutoBoss` - Logic tự động đánh boss
  - `run()` - Vòng lặp auto boss

### `auto_pet.py`
**Class:**
- `AutoPet` - Logic tự động quản lý pet
  - `run()` - Vòng lặp auto pet

### `auto_NVBoMong.py`
**Class:**
- `AutoNVBoMong` - Logic tự động nhiệm vụ Bò Mộng
  - `run()` - Vòng lặp auto Bò Mộng

### `auto_giftcode.py`
**Class:**
- `AutoGiftcode` - Logic tự động nhập giftcode
  - `run()` - Vòng lặp auto giftcode

### `boss_manager.py`
**Class:**
- `BossManager` - Quản lý thông tin boss
  - `get_boss_list()` - Lấy danh sách boss
  - `find_boss()` - Tìm boss theo tên

### `map_data.py`
**Data:**
- Chứa dữ liệu về maps, zones, waypoints

### `target_utils.py`
**Functions:**
- Các utility functions để tìm và quản lý targets

### `xmap.py`
**Class:**
- `XMap` - Xử lý di chuyển giữa các maps
  - `go_to_map()` - Di chuyển đến map
  - `find_path()` - Tìm đường đi

---

## 📁 logs/ - Logger Configuration

### `logger_config.py`
**Exports:**
- `logger` - Logger instance
- `TerminalColors` - Class chứa color codes
- `Box` - Class vẽ box
- `print_header()` - In header
- `print_separator()` - In separator

---

## 📁 model/ - Game Objects Models

### `game_objects.py`
**Classes:**
- `Char` - Model cho nhân vật
  - Attributes: `id`, `name`, `cx`, `cy`, `hp`, `max_hp`, `mp`, `max_mp`, `level`, `exp`, `power`, `potential`, `bag`, `box`, `skills`, etc.
  
- `Mob` - Model cho quái vật
  - Attributes: `id`, `template_id`, `name`, `cx`, `cy`, `hp`, `max_hp`, `level`, `status`, etc.
  
- `OtherChar` - Model cho người chơi khác
  - Attributes: `id`, `name`, `cx`, `cy`, `hp`, `max_hp`, `level`, etc.
  
- `Item` - Model cho item
  - Attributes: `id`, `template_id`, `quantity`, `info`, `options`, etc.
  
- `Skill` - Model cho skill
  - Attributes: `id`, `template_id`, `point`, `cooldown`, etc.

### `pet.py`
**Class:**
- `Pet` - Model cho pet
  - Attributes: `id`, `name`, `status`, `hp`, `max_hp`, `mp`, `max_mp`, `level`, `exp`, `power`, `skills`, etc.

### `map_objects.py`
**Classes:**
- `NPC` - Model cho NPC
  - Attributes: `id`, `template_id`, `name`, `cx`, `cy`, `status`, etc.
  
- `ItemMap` - Model cho item trên map
  - Attributes: `id`, `item_id`, `cx`, `cy`, etc.

---

## 📁 network/ - Network Layer

### `session.py`
**Class:**
- `Session` - Quản lý kết nối TCP với server
  - `__init__(controller, proxy)` - Khởi tạo session
  - `connect(host, port)` - Kết nối đến server
  - `disconnect()` - Ngắt kết nối
  - `send_message(msg)` - Gửi message đến server
  - `_listen()` - Lắng nghe messages từ server
  - `_read_message()` - Đọc message từ stream

**Attributes:**
- `reader`, `writer` - StreamReader/Writer
- `connected` - Trạng thái kết nối
- `controller` - Controller reference
- `proxy` - Proxy configuration

### `message.py`
**Class:**
- `Message` - Đại diện cho một message trong protocol
  - `__init__(command)` - Tạo message với command
  - `writer()` - Lấy MessageWriter
  - `reader()` - Lấy MessageReader

**Attributes:**
- `command` - Command code
- `data` - Message data (bytes)

### `reader.py`
**Class:**
- `MessageReader` - Đọc data từ message
  - `read_byte()` - Đọc 1 byte
  - `read_short()` - Đọc 2 bytes (short)
  - `read_int()` - Đọc 4 bytes (int)
  - `read_long()` - Đọc 8 bytes (long)
  - `read_bool()` - Đọc boolean
  - `read_utf()` - Đọc UTF string
  - `read_bytes()` - Đọc byte array
  - `available()` - Số bytes còn lại

### `writer.py`
**Class:**
- `MessageWriter` - Ghi data vào message
  - `write_byte(value)` - Ghi 1 byte
  - `write_short(value)` - Ghi 2 bytes (short)
  - `write_int(value)` - Ghi 4 bytes (int)
  - `write_long(value)` - Ghi 8 bytes (long)
  - `write_bool(value)` - Ghi boolean
  - `write_utf(value)` - Ghi UTF string
  - `write_bytes(value)` - Ghi byte array

### `service.py`
**Class:**
- `Service` - Cung cấp high-level game actions
  - `__init__(session, char)` - Khởi tạo service
  - `char_move()` - Di chuyển nhân vật
  - `attack_mob(mob)` - Tấn công quái vật
  - `attack_char(char)` - Tấn công người chơi
  - `pick_item(item)` - Nhặt item
  - `use_skill(skill, target)` - Sử dụng skill
  - `talk_npc(npc_id)` - Nói chuyện với NPC
  - `select_menu(menu_id)` - Chọn menu NPC
  - `request_change_zone(zone_id)` - Đổi zone
  - `request_change_map()` - Đổi map
  - `send_chat(text)` - Gửi chat
  - `use_item(item_id, action)` - Sử dụng item
  - `throw_item(item_id)` - Vứt item
  - `split_item(item_id, quantity)` - Tách item
  - `combine_item()` - Ghép item
  - `upgrade_item()` - Nâng cấp item
  - `accept_task()` - Nhận nhiệm vụ
  - `finish_task()` - Hoàn thành nhiệm vụ
  - `pet_fusion()` - Hợp thể pet
  - `pet_rest()` - Cho pet nghỉ
  - `pet_attack()` - Cho pet tấn công
  - `pet_protect()` - Cho pet bảo vệ
  - Và nhiều methods khác...

---
## 📁 log/ - Log Files

### `log.py`
**Functions:**
**Class:**
 - TerminalColors - Class chứa color codes
 - Box - Class vẽ box
 - print_header() - In header
 - print_separator() - In separator
 - print_section_header() - In section header
 - ColoredFormatter - Class định dạng log
 - setup_logger() - Hàm khởi tạo logger
 - set_logger_status() - Hàm bật/tắt logger
 - logger - Logger instance


---
## 📁 services/ - Game Services

### `movement.py`
**Functions:**
- `calculate_path(from_x, from_y, to_x, to_y)` - Tính đường đi
- `move_to(service, char, x, y)` - Di chuyển đến tọa độ

### `pet_service.py`
**Class:**
- `PetService` - Service quản lý pet
  - `call_pet()` - Gọi pet
  - `feed_pet()` - Cho pet ăn
  - `train_pet()` - Luyện pet

---

## 📁 train/ - AI Training

### `train_pytorch.py`
**Functions/Classes:**
- Code để train neural network bằng PyTorch
- Tạo training data
- Train model
- Export weights sang JSON

---

## 📁 ui/ - UI Display Components

### `character_display.py`
**Functions:**
- `display_character(char)` - Hiển thị thông tin nhân vật

### `item_display.py`
**Functions:**
- `display_bag(bag)` - Hiển thị hành trang
- `display_box(box)` - Hiển thị rương đồ

### `task_display.py`
**Functions:**
- `display_tasks(tasks)` - Hiển thị nhiệm vụ

### `pet_display.py`
**Functions:**
- `display_pet(pet)` - Hiển thị thông tin pet

### `pet_status.py`
**Functions:**
- `display_pet_status(pet)` - Hiển thị trạng thái pet

### `zone_display.py`
**Functions:**
- `display_zones(zones)` - Hiển thị danh sách zones

### `help_display.py`
**Functions:**
- `display_help()` - Hiển thị help

### `formatters.py`
**Functions:**
- Các hàm format dữ liệu để hiển thị

### `table_headers.py`
**Constants:**
- Định nghĩa headers cho tables

### `table_utils.py`
**Functions:**
- Utility functions để vẽ tables

---

## 📁 utils/ - Utilities

### `autocomplete.py`
**Class:**
- `AutoCompleter` - Auto complete cho command line
  - `get_completions()` - Lấy completions

### `macro_interpreter.py`
**Class:**
- `MacroInterpreter` - Thông dịch macro commands
  - `parse()` - Parse macro
  - `execute()` - Thực thi macro

---

## 📁 test_*.py - Test Files

### `test_ai_commands.py`
**Mô tả:** Test AI command processing

### `test_ai_pipeline.py`
**Mô tả:** Test AI pipeline (state building, inference, action decoding)

---

## 🔄 Luồng Hoạt Động Chính

### 1. Khởi động ứng dụng
```
main.py
  ├─> load_mob_names()
  ├─> clean_pycache()
  ├─> load_proxies()
  ├─> AccountManager.load_accounts()
  └─> command_loop()
```

### 2. Đăng nhập tài khoản
```
Account.login()
  ├─> Session.connect()
  ├─> Gửi setClientType (Cmd -29, SubCmd 2)
  ├─> Gửi android pack (Cmd 126)
  ├─> Gửi login credentials (Cmd -29, SubCmd 0)
  └─> Chờ login_event
```

### 3. Xử lý messages
```
Session._listen()
  ├─> Session._read_message()
  ├─> Controller.on_message(msg)
  └─> Handler.handle(msg)
      ├─> LoginHandler
      ├─> CharacterHandler
      ├─> MapHandler
      ├─> CombatHandler
      ├─> PlayerHandler
      ├─> TaskHandler
      ├─> InventoryHandler
      ├─> NPCHandler
      ├─> NotificationHandler
      └─> MiscHandler
```

### 4. AI Agent (nếu bật)
```
Controller.toggle_ai_agent(True)
  └─> AIAgent loop:
      ├─> StateBuilder.build_state()
      ├─> InferenceEngine._forward_pass()
      ├─> ActionDecoder.decode()
      └─> Service.execute_action()
```

### 5. Auto features
```
Controller.toggle_autoplay(True)
  └─> AutoPlay.run()
      ├─> Tìm quái
      ├─> Di chuyển
      ├─> Tấn công
      ├─> Nhặt item
      └─> Ăn đậu khi cần
```

---

## 📊 Thống Kê Dự Án

- **Tổng số files Python:** 108
- **Tổng số classes:** ~80+
- **Tổng số functions:** ~200+
- **Modules chính:** 13 (ai_core, commands, targeted_commands, controller, core, logic, model, network, services, ui, utils, handlers, logs)

---

## 🎯 Các Tính Năng Chính

1. **Multi-Account Management** - Quản lý nhiều tài khoản đồng thời
2. **AI Agent** - Neural Network điều khiển bot tự động
3. **Auto Play** - Tự động chơi (farm, level up)
4. **Auto Boss** - Tự động đánh boss
5. **Auto Pet** - Tự động quản lý pet
6. **Auto Attack** - Tự động tấn công
7. **Proxy Support** - Hỗ trợ proxy
8. **Group Management** - Quản lý groups tài khoản
9. **Zone Distribution** - Phân bổ tài khoản theo zones
10. **Shared Memory** - Multi-agent coordination
11. **Online Training** - Train AI trong khi chơi
12. **Macro System** - Hệ thống macro
13. **Command System** - Hệ thống lệnh mạnh mẽ

---

## 🔧 Công Nghệ Sử dụng

- **Python 3.8+** - Ngôn ngữ chính
- **asyncio** - Async I/O cho network và multi-tasking
- **Pure Python Neural Network** - Không cần PyTorch/TensorFlow cho inference
- **TCP Sockets** - Network communication
- **JSON** - Lưu trữ config và AI weights
- **Threading** - Multi-threading cho training

---

## 📝 Ghi Chú

- Dự án được tổ chức theo kiến trúc modular, dễ mở rộng
- Sử dụng design patterns: Singleton, Strategy, Command, Observer
- Code được document bằng tiếng Việt và tiếng Anh
- Hỗ trợ auto-reconnect khi mất kết nối ( đang lỗi ở 1 vài điểm)
- Có logging system đầy đủ
- UI/UX thân thiện với tables và colors

---

**Tài liệu này được tạo tự động bởi analyze_project.py**
**Ngày tạo:** 2026-01-08
