# 🗺️ BẢN ĐỒ CẤU TRÚC HỆ THỐNG SOURCE CODE

## 🌳 Cây thư mục tổng quan
```text
.
├── ai_core
│   ├── weights
│   │   └── demo_trained_weights.json
│   ├── __init__.py
│   ├── action_decoder.py
│   ├── brain.py
│   ├── online_training.py
│   ├── shared_memory.py
│   ├── shared_training.py
│   └── state_builder.py
├── commands
│   ├── setup
│   │   ├── __init__.py
│   │   ├── constants.py
│   │   ├── inventory_helpers.py
│   │   ├── navigation_helpers.py
│   │   ├── retry_utils.py
│   │   ├── state_manager.py
│   │   ├── step_activate_items.py
│   │   ├── step_buy_bua.py
│   │   ├── step_character.py
│   │   ├── step_farm_beans.py
│   │   ├── step_giftcode.py
│   │   ├── step_rewards.py
│   │   ├── step_santa_shop.py
│   │   ├── step_support_items.py
│   │   └── step_upgrade.py
│   ├── __init__.py
│   ├── autologin_command.py
│   ├── base_command.py
│   ├── clear_command.py
│   ├── combo_command.py
│   ├── command_loader.py
│   ├── config_command.py
│   ├── exit_command.py
│   ├── group_command.py
│   ├── help_command.py
│   ├── list_command.py
│   ├── login_command.py
│   ├── logout_command.py
│   ├── plugin_command.py
│   ├── proxy_command.py
│   ├── setup_accounts_command.py
│   ├── sleep_command.py
│   ├── target_command.py
│   └── wait_command.py
├── config
│   ├── auto_chat.json
│   └── gold_config.json
├── config_system
│   ├── __init__.py
│   ├── config_loader.py
│   ├── config_validator.py
│   ├── default.json
│   └── README.md
├── constants
│   ├── __init__.py
│   └── cmd.py
├── controller
│   ├── handlers
│   │   ├── __init__.py
│   │   ├── base_handler.py
│   │   ├── character_handler.py
│   │   ├── combat_handler.py
│   │   ├── inventory_handler.py
│   │   ├── login_handler.py
│   │   ├── map_handler.py
│   │   ├── misc_handler.py
│   │   ├── notification_handler.py
│   │   ├── npc_handler.py
│   │   ├── player_handler.py
│   │   └── task_handler.py
│   ├── __init__.py
│   └── controller.py
├── core
│   ├── __init__.py
│   ├── account.py
│   └── account_manager.py
├── data
│   ├── item_data.txt
│   └── mob_data.txt
├── handlers
│   ├── __init__.py
│   └── ai_command_handler.py
├── logic
│   ├── __init__.py
│   ├── auto_attack.py
│   ├── auto_boss.py
│   ├── auto_giftcode.py
│   ├── auto_item.py
│   ├── auto_main_quest.py
│   ├── auto_msm.py
│   ├── auto_NVBoMong.py
│   ├── auto_pet.py
│   ├── auto_play.py
│   ├── auto_scanmap.py
│   ├── boss_manager.py
│   ├── map_data.py
│   ├── npc_names.py
│   ├── quest_mapper.py
│   ├── target_utils.py
│   └── xmap.py
├── logs
│   ├── logger_config.py
│   └── setup_test_report.md
├── macros
│   ├── chia_khu.txt
│   ├── setup_all.txt
│   └── test.txt
├── model
│   ├── __init__.py
│   ├── game_objects.py
│   ├── map_objects.py
│   └── pet.py
├── network
│   ├── __init__.py
│   ├── message.py
│   ├── reader.py
│   ├── service.py
│   ├── session.py
│   └── writer.py
├── plugins
│   ├── user_plugins
│   │   ├── __init__.py
│   │   └── auto_chat_plugin.py
│   ├── __init__.py
│   ├── base_plugin.py
│   ├── plugin_api.py
│   ├── PLUGIN_COMMANDS.md
│   ├── plugin_hooks.py
│   ├── plugin_loader.py
│   ├── plugin_manager.py
│   ├── QUICKSTART.md
│   └── README.md
├── scripts
│   ├── analyze_project.py
│   └── project_structure.json
├── services
│   ├── __init__.py
│   ├── movement.py
│   └── pet_service.py
├── targeted_commands
│   ├── __init__.py
│   ├── aiagent_command.py
│   ├── andau_command.py
│   ├── autoattack_command.py
│   ├── autobomong_command.py
│   ├── autoboss_command.py
│   ├── autoitem_command.py
│   ├── automsm_command.py
│   ├── autopet_command.py
│   ├── autoplay_command.py
│   ├── autoquest_command.py
│   ├── base_targeted_command.py
│   ├── blacklist_command.py
│   ├── congcs_command.py
│   ├── findboss_command.py
│   ├── findmob_command.py
│   ├── findnpc_command.py
│   ├── gomap_command.py
│   ├── hit_command.py
│   ├── khu_command.py
│   ├── logger_command.py
│   ├── opennpc_command.py
│   ├── pet_command.py
│   ├── scanmap_command.py
│   ├── show_command.py
│   ├── tansat_command.py
│   ├── tapchat_command.py
│   ├── targeted_command_loader.py
│   ├── teleport_command.py
│   ├── teleportnpc_command.py
│   └── useitem_command.py
├── tests
│   ├── debug_boss_match.py
│   ├── live_test_setup.py
│   ├── test_ai_commands.py
│   ├── test_ai_pipeline.py
│   ├── test_login.py
│   └── test_setup_flow.py
├── train
│   └── train_pytorch.py
├── ui
│   ├── __init__.py
│   ├── character_display.py
│   ├── formatters.py
│   ├── help_display.py
│   ├── item_display.py
│   ├── pet_display.py
│   ├── pet_status.py
│   ├── table_headers.py
│   ├── table_utils.py
│   ├── task_display.py
│   └── zone_display.py
├── utils
│   ├── __init__.py
│   ├── autocomplete.py
│   └── macro_interpreter.py
├── __init__.py
├── accounts.txt
├── config.py
├── main.py
├── mapfile.py
├── maps_config.json
├── project_summary.json
├── project_summary.md
├── proxy.txt
├── README.md
├── requirements-train.txt
└── setup_state.json
```
==================================================

## 🔍 Chi tiết các file và hàm xử lý
### 📄 File: `.gitignore`
- *(File cấu hình hoặc file rỗng, không chứa hàm)*

------------------------------

### 📄 File: `README.md`
- *(File cấu hình hoặc file rỗng, không chứa hàm)*

------------------------------

### 📄 File: `__init__.py`
- *(File cấu hình hoặc file rỗng, không chứa hàm)*

------------------------------

### 📄 File: `accounts.txt`
- *(File cấu hình hoặc file rỗng, không chứa hàm)*

------------------------------

### 📄 File: `ai_core/__init__.py`
- *(File cấu hình hoặc file rỗng, không chứa hàm)*

------------------------------

### 📄 File: `ai_core/action_decoder.py`
- **Class `ActionDecoder`** (Dòng 11)
  > *Mô tả:* Decodes AI action index into game commands.
Action space: 32 actions organized by category.
  - `method`: **`__init__(controller, service, shared_memory)`** (Dòng 23)
    > *Chi tiết:* Args:
    controller: Game controller instance
    service: Network service for sending commands
    shared_memory: SharedMemory instance for coordination
  - `async_method`: **`execute_action(action_index: int, context: Optional[Dict[str, Any]])`** (Dòng 37)
    > *Chi tiết:* Execute the selected action.

Args:
    action_index: Action to execute (0-31)
    context: Optional context data (item_ids, mob_id, etc.)

Returns:
    bool: True if action executed successfully
  - `async_method`: **`_execute_basic_action(action_index: int)`** (Dòng 71)
    > *Chi tiết:* Execute basic game actions
  - `async_method`: **`_execute_multiagent_action(action_index: int, context: Dict)`** (Dòng 110)
    > *Chi tiết:* Execute multi-agent coordination actions
  - `async_method`: **`_execute_boss_hunting_action(action_index: int, context: Dict)`** (Dòng 134)
    > *Chi tiết:* Execute boss hunting actions
  - `async_method`: **`_execute_goal_based_action(action_index: int, context: Dict)`** (Dòng 158)
    > *Chi tiết:* Execute goal-based actions with context
  - `async_method`: **`_attack_nearest_mob()`** (Dòng 182)
    > *Chi tiết:* Attack the nearest alive mob
  - `async_method`: **`_move_to_nearest_mob()`** (Dòng 194)
    > *Chi tiết:* Move towards nearest mob
  - `async_method`: **`_use_best_skill()`** (Dòng 208)
    > *Chi tiết:* Use highest damage skill
  - `async_method`: **`_retreat()`** (Dòng 219)
    > *Chi tiết:* Run away from danger
  - `async_method`: **`_pick_up_items()`** (Dòng 241)
    > *Chi tiết:* Pick up nearby items
  - `async_method`: **`_use_hp_potion()`** (Dòng 246)
    > *Chi tiết:* Use HP potion/item
  - `async_method`: **`_return_to_safe_zone()`** (Dòng 251)
    > *Chi tiết:* Return to safe zone/spawn point
  - `async_method`: **`_broadcast_target()`** (Dòng 256)
    > *Chi tiết:* Share current target with team
  - `async_method`: **`_follow_leader()`** (Dòng 276)
    > *Chi tiết:* Follow team leader
  - `async_method`: **`_call_for_help()`** (Dòng 284)
    > *Chi tiết:* Broadcast help request to team
  - `async_method`: **`_form_formation()`** (Dòng 292)
    > *Chi tiết:* Organize team formation
  - `async_method`: **`_search_for_boss(context: Dict)`** (Dòng 297)
    > *Chi tiết:* Search for boss on map
  - `async_method`: **`_coordinate_boss_attack()`** (Dòng 303)
    > *Chi tiết:* Attack boss in coordination with team
  - `async_method`: **`_tank_boss()`** (Dòng 312)
    > *Chi tiết:* Tank boss (stay close, take damage)
  - `async_method`: **`_support_teammates()`** (Dòng 317)
    > *Chi tiết:* Support team (healing, buffs)
  - `async_method`: **`_farm_items(context: Dict)`** (Dòng 322)
    > *Chi tiết:* Farm items by killing specific mobs
  - `async_method`: **`_hunt_specific_mob(context: Dict)`** (Dòng 334)
    > *Chi tiết:* Hunt specific mob type
  - `async_method`: **`_gather_resources()`** (Dòng 340)
    > *Chi tiết:* Gather resources from map
  - `async_method`: **`_complete_quest_objective(context: Dict)`** (Dòng 344)
    > *Chi tiết:* Work on quest objective
  - `method`: **`_find_nearest_alive_mob()`** (Dòng 350)
    > *Chi tiết:* Find nearest alive mob (helper)

------------------------------

### 📄 File: `ai_core/brain.py`
- **Class `InferenceEngine`** (Dòng 13)
  > *Mô tả:* Pure Python neural network inference engine.
Loads weights from JSON and performs forward pass using only standard library.
  - `method`: **`__init__()`** (Dòng 19)
  - `method`: **`set_weights_from_dict(data: dict)`** (Dòng 25)
    > *Chi tiết:* Load weights directly from dictionary (for sharing)
  - `method`: **`load_weights(weights_path: str)`** (Dòng 37)
    > *Chi tiết:* Load neural network weights from JSON file.

Format:
{
    "architecture": [20, 64, 64, 32],
    "layers": [
        {"W": [[...], ...], "b": [...]},
        {"W": [[...], ...], "b": [...]},
        ...
    ]
}
  - `method`: **`_init_random_weights()`** (Dòng 81)
    > *Chi tiết:* Initialize random weights for testing (when no weights file exists)
  - `async_method`: **`predict(state: List[float], action_mask: List[bool])`** (Dòng 104)
    > *Chi tiết:* Async inference - predict best action from state.

Args:
    state: Input state vector (length 20)
    action_mask: Optional boolean mask for valid actions (length 32)
                True = valid action, False = masked (invalid)

Returns:
    (action_index, confidence) tuple
  - `method`: **`_forward_pass(state: List[float], action_mask: List[bool])`** (Dòng 129)
    > *Chi tiết:* Forward pass through network (synchronous).
Optimized with list comprehensions for speed.
  - `method`: **`_linear(x: List[float], W: List[List[float]], b: List[float])`** (Dòng 158)
    > *Chi tiết:* Linear transformation: y = Wx + b
Optimized with list comprehension and zip.

W shape: (out_features, in_features)
x shape: (in_features,)
b shape: (out_features,)
Returns: (out_features,)
  - `method`: **`_relu(x: List[float])`** (Dòng 173)
    > *Chi tiết:* ReLU activation: max(0, x)
  - `method`: **`_softmax(x: List[float])`** (Dòng 177)
    > *Chi tiết:* Softmax activation with numerical stability.
exp(x - max(x)) / sum(exp(x - max(x)))
  - `method`: **`_apply_mask(logits: List[float], mask: List[bool])`** (Dòng 192)
    > *Chi tiết:* Apply action mask to logits.
Masked actions (False) get -inf logit → 0 probability after softmax.
  - `method`: **`get_model_info()`** (Dòng 203)
    > *Chi tiết:* Return model architecture and status
  - `method`: **`_count_parameters()`** (Dòng 213)
    > *Chi tiết:* Count total trainable parameters

------------------------------

### 📄 File: `ai_core/online_training.py`
- **Class `OnlineTrainer`** (Dòng 11)
  > *Mô tả:* Online training manager - Trains AI while bot is playing
Collects experience from real gameplay and trains in background
  - `method`: **`__init__(ai_agent, enable_training)`** (Dòng 17)
    > *Chi tiết:* Args:
    ai_agent: AIAgent instance
    enable_training: Enable background training
  - `method`: **`calculate_reward(old_state_dict, new_state_dict, action: int, state_builder)`** (Dòng 40)
    > *Chi tiết:* Calculate reward based on state transition

Enhanced reward structure:
- Base survival: +0.05 per step
- Aggressive action bonus: +0.1 for attack/move/skill
- Combat efficiency: -0.3 if no kill in 1s (VERY AGGRESSIVE!)
- Kill mob: +1.0
- Damage mob: +0.2
- Gain XP: +0.5
- Pick gold: +0.3
- Take damage (fighting): -0.05
- Take damage (not fighting): -0.1
- Idle: -0.2 (4x stronger)
- Die: -1.0
  - `async_method`: **`collect_step(state, action, controller)`** (Dòng 147)
    > *Chi tiết:* Collect single experience step from gameplay
Called after each AI decision
  - `async_method`: **`collect_step_shared(state, action, controller, shared_trainer)`** (Dòng 211)
    > *Chi tiết:* Collect step and push to SharedTrainer
  - `async_method`: **`_background_train()`** (Dòng 257)
    > *Chi tiết:* Train in background without blocking gameplay
  - `method`: **`_train_batch()`** (Dòng 269)
    > *Chi tiết:* Single training batch (runs in thread pool)
  - `method`: **`save_checkpoint(path: str)`** (Dòng 278)
    > *Chi tiết:* Save current model weights
  - `method`: **`auto_save_loop(interval_minutes)`** (Dòng 283)
    > *Chi tiết:* Auto-save model periodically
  - `method`: **`get_stats()`** (Dòng 293)
    > *Chi tiết:* Get training statistics

------------------------------

### 📄 File: `ai_core/shared_memory.py`
- **Class `SharedMemory`** (Dòng 11)
  > *Mô tả:* Singleton pattern shared memory for multi-agent coordination.
Thread-safe with threading.Lock for concurrent access.
  - `method`: **`__new__()`** (Dòng 20)
  - `method`: **`__init__()`** (Dòng 28)
  - `method`: **`broadcast_target(account_id: str, target_info: Dict[str, Any])`** (Dòng 64)
    > *Chi tiết:* Broadcast a target (boss, mob, location) to all bots
  - `method`: **`get_shared_targets()`** (Dòng 74)
    > *Chi tiết:* Get list of shared targets from other bots
  - `method`: **`clear_targets()`** (Dòng 79)
    > *Chi tiết:* Clear all shared targets
  - `method`: **`set_team_leader(account_id: str)`** (Dòng 86)
    > *Chi tiết:* Designate a team leader
  - `method`: **`get_team_leader()`** (Dòng 92)
    > *Chi tiết:* Get current team leader
  - `method`: **`register_bot(account_id: str, capabilities: Dict[str, Any])`** (Dòng 97)
    > *Chi tiết:* Register a bot with its capabilities (tank/dps/support)
  - `method`: **`get_team_formation()`** (Dòng 102)
    > *Chi tiết:* Get current team formation
  - `method`: **`assign_to_group(account_id: str, group_id: int)`** (Dòng 112)
    > *Chi tiết:* Assign bot to a group (1-5 users per group)
  - `method`: **`get_group_members(group_id: int)`** (Dòng 127)
    > *Chi tiết:* Get list of bots in a group
  - `method`: **`set_active_groups(group_ids: List[int])`** (Dòng 132)
    > *Chi tiết:* Set which groups are AI-controlled
  - `method`: **`is_bot_in_active_group(account_id: str)`** (Dòng 138)
    > *Chi tiết:* Check if bot is in an active group
  - `method`: **`assign_zone(account_id: str, zone_id: int)`** (Dòng 148)
    > *Chi tiết:* Manually assign bot to a zone
  - `method`: **`get_zone_distribution(map_id: int)`** (Dòng 153)
    > *Chi tiết:* Get zone distribution for a map
  - `method`: **`auto_distribute_zones(map_id: int, bot_ids: List[str], num_zones: int)`** (Dòng 158)
    > *Chi tiết:* Auto distribute bots across zones using round-robin
  - `method`: **`set_global_goal(goal_type: str, goal_data: Dict[str, Any])`** (Dòng 173)
    > *Chi tiết:* Set global goal for team.
goal_type: 'farm_items', 'hunt_boss', 'complete_quest'
goal_data: {'item_ids': [1,5,10]} or {'boss_name': 'Fide'}
  - `method`: **`get_current_goal()`** (Dòng 187)
    > *Chi tiết:* Get current global goal
  - `method`: **`update_goal_progress(account_id: str, progress: Any)`** (Dòng 192)
    > *Chi tiết:* Update progress for an account
  - `method`: **`clear_goal()`** (Dòng 197)
    > *Chi tiết:* Clear current goal
  - `method`: **`update_status(account_id: str, status: Dict[str, Any])`** (Dòng 205)
    > *Chi tiết:* Update bot status
  - `method`: **`get_team_status()`** (Dòng 210)
    > *Chi tiết:* Get status of all bots
- **Class `ZoneDensityManager`** (Dòng 216)
  > *Mô tả:* Hive Architecture - Mental Map chia sẻ về mật độ zone.
Ngăn chặn "dẫm đạp" khi nhiều bot cùng chọn 1 zone trống.
  - `method`: **`__init__()`** (Dòng 222)
  - `method`: **`register_intent(account_id: str, map_id: int, zone_id: int)`** (Dòng 238)
    > *Chi tiết:* Đăng ký ý định di chuyển đến zone (ngăn race condition)
  - `method`: **`update_real_position(account_id: str, map_id: int, zone_id: int)`** (Dòng 248)
    > *Chi tiết:* Cập nhật vị trí thực tế của bot
  - `method`: **`mark_zone_scanned(account_id: str, map_id: int, zone_id: int)`** (Dòng 264)
    > *Chi tiết:* Đánh dấu zone đã được quét (cho Auto Boss)
  - `method`: **`_clean_expired_intents()`** (Dòng 274)
    > *Chi tiết:* Xóa các intent đã hết hạn (internal, gọi trong lock)
  - `method`: **`get_zone_density(map_id: int, zone_id: int)`** (Dòng 285)
    > *Chi tiết:* Tính mật độ zone (số bot hiện tại + số bot dự định đến).
Returns: số lượng bot trong zone (thực tế + ý định)
  - `method`: **`is_zone_recently_scanned(map_id: int, zone_id: int)`** (Dòng 312)
    > *Chi tiết:* Kiểm tra zone đã được quét gần đây chưa
  - `method`: **`get_zone_score(map_id: int, zone_id: int, current_num_players: int, max_players: int, normalize: bool)`** (Dòng 324)
    > *Chi tiết:* Chấm điểm zone dựa trên nhiều yếu tố.

Score càng CAO = zone càng TỐT để chọn.

Factors:
- Mật độ bot (càng ít càng tốt)
- Số người chơi khác trong zone (càng ít càng tốt)
- Lịch sử quét (đã quét gần đây = điểm thấp)
  - `method`: **`get_best_zone(map_id: int, zone_list: List[Dict[str, Any]], account_id: str)`** (Dòng 365)
    > *Chi tiết:* Chọn zone TỐT NHẤT từ danh sách.

zone_list format: [{'zone_id': 0, 'num_players': 5, 'max_players': 15}, ...]

Returns: zone_id tốt nhất, hoặc None nếu không có
  - `method`: **`clear_account_data(account_id: str)`** (Dòng 401)
    > *Chi tiết:* Xóa toàn bộ dữ liệu của 1 account (khi logout)

------------------------------

### 📄 File: `ai_core/shared_training.py`
- **Class `SharedTrainer`** (Dòng 11)
  > *Mô tả:* Singleton Trainer that collects experience from ALL agents.
Manages a central AITrainer instance (PyTorch) and syncs weights to agents.
  - `method`: **`__new__()`** (Dòng 19)
  - `method`: **`__init__()`** (Dòng 27)
  - `method`: **`enable()`** (Dòng 42)
    > *Chi tiết:* Enable shared training
  - `method`: **`disable()`** (Dòng 65)
    > *Chi tiết:* Disable shared training
  - `method`: **`register_agent(agent)`** (Dòng 70)
    > *Chi tiết:* Register an agent to contribute to shared training
  - `async_method`: **`collect_step(state, action, reward, next_state, done)`** (Dòng 77)
    > *Chi tiết:* Collect experience from any agent
  - `async_method`: **`_shared_training_worker()`** (Dòng 86)
    > *Chi tiết:* Background worker loop
  - `method`: **`_train_batch()`** (Dòng 108)
    > *Chi tiết:* Run training batch (sync function)
  - `async_method`: **`_sync_weights_to_agents()`** (Dòng 116)
    > *Chi tiết:* Push updated weights to all agents
  - `method`: **`get_stats()`** (Dòng 140)
    > *Chi tiết:* Get shared training stats

------------------------------

### 📄 File: `ai_core/state_builder.py`
- **Class `StateBuilder`** (Dòng 13)
  > *Mô tả:* Converts game state (from controller) into normalized feature vector with temporal context.
Output: 60-dimensional float vector (3 frames × 20D base features)

Temporal context helps AI recognize:
- HP/MP trends (increasing/decreasing)
- Mob movement patterns
- Combat momentum
  - `method`: **`__init__(state_dim: int, history_frames: int)`** (Dòng 24)
  - `method`: **`build_state(controller)`** (Dòng 44)
    > *Chi tiết:* Build temporal state vector from game controller.

Returns 60D vector: [frame_t-2, frame_t-1, frame_t] (3 frames × 20D)

Base features per frame (20 dims):
0: HP ratio (c_hp / c_hp_full)
1: MP ratio (c_mp / c_mp_full)
2-3: Position (cx, cy) normalized
4-5: Nearest mob distance (dx, dy) normalized
6: Nearest mob HP ratio
7: Mob count in range
8-9: Skill cooldown status (2 skills)
10: Is character dead (0/1)
11: Pet status (has pet: 0/1)
12-13: Distance to waypoint/target
14-19: Reserved for future features

Temporal context enables AI to detect:
- HP trend: frame_t[0] > frame_t-1[0] = healing
- Mob approaching: frame_t[4] < frame_t-1[4] = getting closer
- Combat momentum: consecutive damage = aggressive combat
  - `method`: **`_build_single_frame(controller)`** (Dòng 90)
    > *Chi tiết:* Build single 20D state frame (internal helper)
  - `method`: **`_find_nearest_mob(controller, char)`** (Dòng 174)
    > *Chi tiết:* Find nearest alive mob and distance
  - `method`: **`_count_mobs_in_range(controller, char, range_px: int)`** (Dòng 199)
    > *Chi tiết:* Count alive mobs within range
  - `method`: **`_normalize_ratio(current: float, maximum: float)`** (Dòng 218)
    > *Chi tiết:* Normalize ratio to [0, 1]
  - `method`: **`_normalize_coord(coord: float)`** (Dòng 224)
    > *Chi tiết:* Normalize coordinate to [0, 1]
  - `method`: **`_normalize_distance(distance: float)`** (Dòng 228)
    > *Chi tiết:* Normalize distance to [-1, 1]
  - `method`: **`_normalize_count(count: int, max_count: int)`** (Dòng 232)
    > *Chi tiết:* Normalize count to [0, 1]
  - `method`: **`_get_average_mob_hp(controller, char, range_px: int)`** (Dòng 236)
    > *Chi tiết:* Get average HP ratio of mobs in range
  - `method`: **`_get_recent_damage_taken()`** (Dòng 258)
    > *Chi tiết:* Get damage taken in last 1 second, normalized
  - `method`: **`_get_recent_damage_dealt()`** (Dòng 271)
    > *Chi tiết:* Get damage dealt in last 1 second, normalized
  - `method`: **`_get_time_since_kill()`** (Dòng 284)
    > *Chi tiết:* Get time since last kill, normalized to 30 seconds
  - `method`: **`record_damage_taken(amount: float)`** (Dòng 296)
    > *Chi tiết:* Record damage taken for feature tracking
  - `method`: **`record_damage_dealt(amount: float)`** (Dòng 300)
    > *Chi tiết:* Record damage dealt for feature tracking
  - `method`: **`record_kill()`** (Dòng 304)
    > *Chi tiết:* Record mob kill for feature tracking

------------------------------

### 📄 File: `ai_core/weights/demo_trained_weights.json`
- *(File cấu hình hoặc file rỗng, không chứa hàm)*

------------------------------

### 📄 File: `commands/__init__.py`
- *(File cấu hình hoặc file rỗng, không chứa hàm)*

------------------------------

### 📄 File: `commands/autologin_command.py`
- **Class `AutoLoginCommand`** (Dòng 5)
  - `method`: **`__init__()`** (Dòng 6)
  - `async_method`: **`execute(*args, **kwargs)`** (Dòng 9)

------------------------------

### 📄 File: `commands/base_command.py`
- **Class `Command`** (Dòng 4)
  > *Mô tả:* The base class for all commands.
  - `async_method`: **`execute(*args, **kwargs)`** (Dòng 7)
    > *Chi tiết:* Executes the command.

Returns:
    Any: A result that the main loop can use. 
         For example, a boolean to indicate exit, 
         or another object for further processing.

------------------------------

### 📄 File: `commands/clear_command.py`
- **Class `ClearCommand`** (Dòng 4)
  - `async_method`: **`execute(*args, **kwargs)`** (Dòng 5)

------------------------------

### 📄 File: `commands/combo_command.py`
- **Class `ComboCommand`** (Dòng 8)
  > *Mô tả:* Execute a combo/macro from a file.
Usage: combo <macro_name>
  - `method`: **`__init__(manager)`** (Dòng 13)
  - `async_method`: **`execute(parts)`** (Dòng 19)
  - `method`: **`_list_macros()`** (Dòng 51)

------------------------------

### 📄 File: `commands/command_loader.py`
- `function`: **`load_commands(manager, proxy_list, combo_engine)`** (Dòng 5)

------------------------------

### 📄 File: `commands/config_command.py`
- **Class `ConfigCommand`** (Dòng 7)
  > *Mô tả:* Lệnh quản lý cấu hình:
- config reload: Tải lại cấu hình từ file
- config get <key>: Xem giá trị cấu hình
- config set <key> <value>: Đặt giá trị cấu hình (Lưu ý: Chỉ int, bool, str)
  - `method`: **`__init__(manager)`** (Dòng 14)
  - `async_method`: **`execute(parts)`** (Dòng 18)
  - `method`: **`_show_help()`** (Dòng 73)

------------------------------

### 📄 File: `commands/exit_command.py`
- **Class `ExitCommand`** (Dòng 3)
  - `method`: **`__init__(manager)`** (Dòng 4)
  - `async_method`: **`execute(*args, **kwargs)`** (Dòng 7)

------------------------------

### 📄 File: `commands/group_command.py`
- **Class `GroupCommand`** (Dòng 5)
  - `method`: **`__init__(manager)`** (Dòng 6)
  - `async_method`: **`execute(*args, **kwargs)`** (Dòng 10)
  - `method`: **`_list_groups()`** (Dòng 32)
  - `method`: **`_create_group(name: str, ids_str: str)`** (Dòng 38)
  - `method`: **`_delete_group(name: str)`** (Dòng 52)
  - `method`: **`_add_to_group(name: str, ids_str: str)`** (Dòng 61)
  - `method`: **`_remove_from_group(name: str, ids_str: str)`** (Dòng 80)

------------------------------

### 📄 File: `commands/help_command.py`
- **Class `HelpCommand`** (Dòng 4)
  - `async_method`: **`execute(*args, **kwargs)`** (Dòng 5)

------------------------------

### 📄 File: `commands/list_command.py`
- **Class `ListCommand`** (Dòng 4)
  - `method`: **`__init__(manager)`** (Dòng 5)
  - `async_method`: **`execute(*args, **kwargs)`** (Dòng 10)

------------------------------

### 📄 File: `commands/login_command.py`
- **Class `LoginCommand`** (Dòng 7)
  - `method`: **`__init__(manager, proxy_list)`** (Dòng 8)
  - `async_method`: **`execute(*args, **kwargs)`** (Dòng 13)

------------------------------

### 📄 File: `commands/logout_command.py`
- **Class `LogoutCommand`** (Dòng 5)
  - `method`: **`__init__(manager)`** (Dòng 6)
  - `async_method`: **`execute(*args, **kwargs)`** (Dòng 10)

------------------------------

### 📄 File: `commands/plugin_command.py`
- **Class `PluginCommand`** (Dòng 7)
  > *Mô tả:* Command để quản lý plugins
  - `method`: **`__init__(manager)`** (Dòng 10)
    > *Chi tiết:* Initialize with account manager
  - `async_method`: **`execute(parts)`** (Dòng 14)
    > *Chi tiết:* Execute plugin command

Usage:
    plugin list              - Liệt kê tất cả plugins
    plugin enable <name>     - Enable plugin
    plugin disable <name>    - Disable plugin
    plugin reload <name>     - Reload plugin
    plugin info <name>       - Xem thông tin plugin
  - `method`: **`_list_plugins(plugin_manager)`** (Dòng 63)
    > *Chi tiết:* Liệt kê tất cả plugins
  - `method`: **`_enable_plugin(plugin_manager, name)`** (Dòng 86)
    > *Chi tiết:* Enable plugin
  - `method`: **`_disable_plugin(plugin_manager, name)`** (Dòng 105)
    > *Chi tiết:* Disable plugin
  - `method`: **`_reload_plugin(plugin_manager, name)`** (Dòng 122)
    > *Chi tiết:* Reload plugin
  - `method`: **`_show_info(plugin_manager, name)`** (Dòng 130)
    > *Chi tiết:* Hiển thị thông tin chi tiết plugin
  - `method`: **`_show_help()`** (Dòng 149)
    > *Chi tiết:* Hiển thị help

------------------------------

### 📄 File: `commands/proxy_command.py`
- **Class `ProxyCommand`** (Dòng 6)
  - `method`: **`__init__(manager, proxy_list)`** (Dòng 7)
  - `async_method`: **`execute(*args, **kwargs)`** (Dòng 13)
  - `method`: **`_list_proxies()`** (Dòng 21)

------------------------------

### 📄 File: `commands/setup/__init__.py`
- *(File cấu hình hoặc file rỗng, không chứa hàm)*

------------------------------

### 📄 File: `commands/setup/constants.py`
- *(File cấu hình hoặc file rỗng, không chứa hàm)*

------------------------------

### 📄 File: `commands/setup/inventory_helpers.py`
- `function`: **`count_item(acc, item_id: int)`** (Dòng 19)
  > *Mô tả:* Đếm số lượng item theo ID trong balo.
- `function`: **`find_item_index(acc, item_id: int)`** (Dòng 28)
  > *Mô tả:* Tìm index đầu tiên của item trong balo. Trả về -1 nếu không tìm thấy.
- `function`: **`find_item_indices(acc, item_id: int, quantity: int)`** (Dòng 36)
  > *Mô tả:* Tìm nhiều index của item trong balo.
- `function`: **`has_item(acc, item_id: int)`** (Dòng 47)
  > *Mô tả:* Kiểm tra có item trong balo không.
- `function`: **`count_item_by_ids(acc, item_ids: list[int])`** (Dòng 55)
  > *Mô tả:* Đếm số lượng nhiều item IDs cùng lúc. Trả về {item_id: count}.
- `async_function`: **`refresh_inventory(acc)`** (Dòng 64)
  > *Mô tả:* Refresh lại thông tin inventory từ server.
- `function`: **`count_beans(acc)`** (Dòng 75)
  > *Mô tả:* Đếm tổng số đậu thần trong balo.
- `function`: **`has_giftcode_items(acc)`** (Dòng 84)
  > *Mô tả:* Kiểm tra có item giftcode trong balo không.
- `function`: **`count_bua_items(acc)`** (Dòng 92)
  > *Mô tả:* Đếm số loại bùa đã có trong balo.
- `function`: **`count_set_lien_hoan(acc)`** (Dòng 101)
  > *Mô tả:* Đếm số set trang bị Liên Hoàn (min của items 1,16,22,28,12).

------------------------------

### 📄 File: `commands/setup/navigation_helpers.py`
- `function`: **`find_npc(acc, npc_id: int)`** (Dòng 17)
  > *Mô tả:* Tìm NPC theo template_id trong bản đồ hiện tại.
- `function`: **`find_npc_by_name(acc, name: str)`** (Dòng 28)
  > *Mô tả:* Tìm NPC theo tên (không phân biệt hoa thường).
- `async_function`: **`teleport_to_npc(acc, npc_id: int, y_offset: int)`** (Dòng 40)
  > *Mô tả:* Teleport đến gần NPC. Thử tìm trong bản đồ trước, fallback movement service.
- `async_function`: **`open_menu_npc(acc, npc_id: int, timeout: float)`** (Dòng 60)
  > *Mô tả:* Mở menu NPC, trả về danh sách tùy chọn (list[str]).
- `async_function`: **`confirm_menu_npc(acc, npc_id: int, option_idx: int, wait_next: bool, timeout: float)`** (Dòng 73)
  > *Mô tả:* Xác nhận tùy chọn trong menu NPC. Nếu wait_next=True thì đợi menu tiếp theo.
- `async_function`: **`open_input_form(acc, npc_id: int, option_idx: int, timeout: float)`** (Dòng 91)
  > *Mô tả:* Mở menu NPC → chọn option → đợi input form xuất hiện.
- `function`: **`find_menu_option(options: list[str], *keywords)`** (Dòng 112)
  > *Mô tả:* Tìm index tùy chọn trong menu chứa bất kỳ từ khóa nào. Trả về -1 nếu không.
- `async_function`: **`go_home(acc, log_func)`** (Dòng 124)
  > *Mô tả:* Di chuyển về nhà theo giới tính nhân vật.
- `async_function`: **`move_to_map(acc, target_map_id: int, log_func)`** (Dòng 152)
  > *Mô tả:* Di chuyển đến map theo ID bằng xmap.

------------------------------

### 📄 File: `commands/setup/retry_utils.py`
- **Class `RetryConfig`** (Dòng 13)
  > *Mô tả:* Cấu hình retry cho mỗi thao tác.
  - `method`: **`__init__(max_attempts: int, base_delay: float, max_delay: float, backoff: float)`** (Dòng 15)
- `async_function`: **`run_with_timeout(coro: Awaitable, timeout: float, default_return)`** (Dòng 23)
  > *Mô tả:* Chạy coroutine với timeout, trả về default nếu timeout.
- `async_function`: **`retry_operation(acc, log_func, label: str, coro_factory: Callable, config: RetryConfig, timeout: float)`** (Dòng 32)
  > *Mô tả:* Retry wrapper: thực thi coroutine với retry + timeout + backoff.
Args:
    acc: Account object (kiểm tra is_logged_in)
    log_func: Hàm log (acc, msg)
    label: Nhãn thao tác (dùng trong log)
    coro_factory: Hàm trả về coroutine cần thực thi
    config: Cấu hình retry
    timeout: Timeout cho mỗi lần thử (giây)
Returns:
    True nếu thành công, False nếu thất bại sau tất cả retry

------------------------------

### 📄 File: `commands/setup/state_manager.py`
- **Class `StepState`** (Dòng 16)
  > *Mô tả:* Trạng thái của một bước setup.
- **Class `AccountSetupState`** (Dòng 25)
  > *Mô tả:* Trạng thái setup tổng thể của một account.
- **Class `SetupStateManager`** (Dòng 37)
  > *Mô tả:* Quản lý trạng thái setup cho từng account, lưu vào file JSON để resume.
  - `method`: **`__init__()`** (Dòng 40)
  - `method`: **`load()`** (Dòng 43)
    > *Chi tiết:* Tải trạng thái từ file JSON.
  - `method`: **`save()`** (Dòng 60)
    > *Chi tiết:* Lưu trạng thái ra file JSON.
  - `method`: **`get(username: str)`** (Dòng 69)
    > *Chi tiết:* Lấy trạng thái của account, tự tạo mới nếu chưa có.
  - `method`: **`mark_step(username: str, step: int, completed: bool, skipped: bool, error: str)`** (Dòng 77)
    > *Chi tiết:* Đánh dấu trạng thái bước setup.
  - `method`: **`is_step_completed(username: str, step: int)`** (Dòng 88)
    > *Chi tiết:* Kiểm tra bước đã hoàn thành chưa.
  - `method`: **`is_step_skipped(username: str, step: int)`** (Dòng 94)
    > *Chi tiết:* Kiểm tra bước đã bị bỏ qua chưa.
  - `method`: **`is_step_done(username: str, step: int)`** (Dòng 100)
    > *Chi tiết:* Bước đã hoàn thành hoặc đã skip.
  - `method`: **`reset(username: str)`** (Dòng 104)
    > *Chi tiết:* Reset trạng thái của một account.
  - `method`: **`reset_all()`** (Dòng 110)
    > *Chi tiết:* Reset trạng thái của tất cả accounts.
  - `method`: **`set_attribute(username: str, **kwargs)`** (Dòng 115)
    > *Chi tiết:* Thiết lập attribute tùy ý trên trạng thái account.

------------------------------

### 📄 File: `commands/setup/step_activate_items.py`
- `async_function`: **`activate_items(acc, log_func)`** (Dòng 18)
  > *Mô tả:* Kích hoạt các item thưởng:
1. Item 2000 (x2, chọn Set Liên Hoàn) — kiểm tra balo trước, nếu đủ 2 set thì bỏ qua
2. Các item kích hoạt đơn (dùng 1 lần mỗi item)
- `async_function`: **`_activate_item_2000(acc, ctrl, log_func)`** (Dòng 58)
  > *Mô tả:* Dùng item 2000, chọn "Set Liên Hoàn".
Kiểm tra balo trước: nếu đã đủ 2 set thì bỏ qua.
Mỗi lần mở item 2000 sẽ hiện menu với nhiều set, phải chọn đúng "Set Liên Hoàn".

------------------------------

### 📄 File: `commands/setup/step_buy_bua.py`
- `async_function`: **`buy_bua(acc, log_func)`** (Dòng 13)
  > *Mô tả:* Mua bùa tại Bà Hạt Mít (Vách Núi Moori).

------------------------------

### 📄 File: `commands/setup/step_character.py`
- `async_function`: **`create_character(acc, log_func)`** (Dòng 17)
  > *Mô tả:* Tạo nhân vật mới nếu chưa có.
Tên nhân vật: hentz + hậu tố số từ username.
Suppress auto-creation trong misc_handler để tránh race condition.
- `async_function`: **`select_character(acc, log_func)`** (Dòng 81)
  > *Mô tả:* Chọn nhân vật mặc định và vào game.
Đợi cho đến khi map_id > 0 và c_power > 0.

------------------------------

### 📄 File: `commands/setup/step_farm_beans.py`
- `async_function`: **`farm_magic_tree(acc, log_func, target_count: int)`** (Dòng 14)
  > *Mô tả:* Farm đậu thần tại cây đậu trong nhà.
Flow: Về nhà → Teleport NPC đậu thần → Kết hạt nhanh / Thu hoạch lặp lại.

------------------------------

### 📄 File: `commands/setup/step_giftcode.py`
- `async_function`: **`wait_giftcode_response(acc, ctrl, log_func, timeout: float)`** (Dòng 26)
  > *Mô tả:* Đợi phản hồi server sau khi gửi giftcode.
Xử lý race condition: nếu message không liên quan → chờ message tiếp.
Returns: (status, detail)其中 status: 'success'|'used'|'expired'|'invalid'|'unknown'
- `async_function`: **`check_giftcode_items(acc, log_func)`** (Dòng 72)
  > *Mô tả:* Kiểm tra item 1680 trong inventory sau khi nhận giftcode.
- `async_function`: **`submit_giftcode(acc, npc_id: int, code: str, log_func)`** (Dòng 83)
  > *Mô tả:* Nhập giftcode tại NPC nhà (fallback tới Santa).
Có thể tái sử dụng: truyền npc_id của bất kỳ NPC nào có chức năng giftcode.
- `async_function`: **`_submit_giftcode_santa(acc, code: str, log_func)`** (Dòng 132)
  > *Mô tả:* Nhập giftcode tại Santa (fallback khi NPC nhà không có).

------------------------------

### 📄 File: `commands/setup/step_rewards.py`
- `async_function`: **`open_muri(acc, log_func)`** (Dòng 15)
  > *Mô tả:* Teleport tới NPC Ông Muri và mở menu.
- `async_function`: **`claim_rewards(acc, state_mgr, log_func, force: bool)`** (Dòng 46)
  > *Mô tả:* Nhận thưởng: vàng miễn phí → ngọc miễn phí → giftcode → đệ tử miễn phí.
Kiểm tra state_mgr để tránh nhận trùng.
- `async_function`: **`_claim_gold(acc, log_func)`** (Dòng 113)
  > *Mô tả:* Nhận vàng từ NPC nhà.
- `async_function`: **`_claim_gem(acc, npc_id, log_func)`** (Dòng 177)
  > *Mô tả:* Nhận ngọc xanh miễn phí từ NPC nhà.
- `async_function`: **`_claim_disciple(acc, npc_id, log_func)`** (Dòng 213)
  > *Mô tả:* Nhận đệ tử miễn phí từ NPC nhà.

------------------------------

### 📄 File: `commands/setup/step_santa_shop.py`
- `async_function`: **`santa_shop(acc, log_func)`** (Dòng 17)
  > *Mô tả:* Mua item tại Santa shop (tab hỗ trợ + tab đặc biệt).

------------------------------

### 📄 File: `commands/setup/step_support_items.py`
- `async_function`: **`use_support_items(acc, log_func)`** (Dòng 14)
  > *Mô tả:* Dùng item hỗ trợ:
- Item 1182: Dùng để nhận item 441. Nếu item 441 < 20, dùng 1182 cho đến khi đủ.
- Item 1680: Nếu còn trong balo, dùng 1 lần.

------------------------------

### 📄 File: `commands/setup/step_upgrade.py`
- `async_function`: **`open_ep_sao_trang_bi(acc, log_func)`** (Dòng 19)
  > *Mô tả:* Mở giao diện Ép Sao Trang Bị tại Bà Hạt Mít (Đảo Kame, map 5).
Flow: Di chuyển Đảo Kame → Teleport NPC → "Chức năng pha lê" → "Ép Sao Trang Bị"
- `async_function`: **`do_one_upgrade(acc, log_func, main_item_id: int, material_items: list[tuple[int, int]], max_upgrades: int, clear_between: bool)`** (Dòng 101)
  > *Mô tả:* Thực hiện nâng cấp một item tại Ép Sao Trang Bị.
Args:
    main_item_id: ID item chính cần nâng cấp
    material_items: [(item_id, quantity)] nguyên liệu
    max_upgrades: Số lần nâng cấp tối đa
    clear_between: True nếu cần clear items giữa các lần
Returns:
    Số lần nâng cấp thành công
- `async_function`: **`upgrade_item_16(acc, log_func, C)`** (Dòng 227)
  > *Mô tả:* Nâng cấp item ID 16 tại Bà Hạt Mít (Ép Sao Trang Bị) 11 lần.
Mỗi lần: 1x ID 16 (chính) + 2x ID 1 (nguyên liệu)
- `async_function`: **`upgrade_other_items(acc, log_func, C)`** (Dòng 278)
  > *Mô tả:* Nâng cấp các item còn lại:
- ID 1, 22, 28: ép tối đa 10 lần mỗi item (mỗi lần 2x cùng item)
- ID 12 first: 1x ID 12 + ID 16 đã ép
- ID 12 second: 1x ID 12 + 2x ID 442 + 8x ID 441

------------------------------

### 📄 File: `commands/setup_accounts_command.py`
- **Class `SetupAccountsCommand`** (Dòng 59)
  > *Mô tả:* Lệnh tự động setup tài khoản mới — dựa trên state machine.
  - `method`: **`__init__(manager)`** (Dòng 62)
  - `method`: **`_log(acc, msg: str)`** (Dòng 70)
  - `method`: **`_step_log(acc, step: int, msg: str)`** (Dòng 76)
  - `async_method`: **`execute(*args, **kwargs)`** (Dòng 82)
  - `async_method`: **`_setup_one(acc, idx, end_idx, force)`** (Dòng 152)
  - `async_method`: **`_run_step(acc, step: int, force: bool)`** (Dòng 204)
    > *Chi tiết:* Dispatch tới step handler tương ứng.
  - `async_method`: **`_ensure_logged_in(acc, C)`** (Dòng 238)
  - `async_method`: **`_wait_game_ready(acc, C, timeout)`** (Dòng 253)

------------------------------

### 📄 File: `commands/sleep_command.py`
- **Class `SleepCommand`** (Dòng 4)
  - `async_method`: **`execute(*args, **kwargs)`** (Dòng 5)

------------------------------

### 📄 File: `commands/target_command.py`
- **Class `TargetCommand`** (Dòng 5)
  - `method`: **`__init__(manager)`** (Dòng 6)
  - `async_method`: **`execute(*args, **kwargs)`** (Dòng 10)

------------------------------

### 📄 File: `commands/wait_command.py`
- **Class `WaitCommand`** (Dòng 4)
  > *Mô tả:* Pause execution for a specified duration (in seconds).
Usage: wait <seconds>
  - `async_method`: **`execute(parts)`** (Dòng 9)

------------------------------

### 📄 File: `config.py`
- **Class `Config`** (Dòng 11)
  - `method`: **`init()`** (Dòng 87)
    > *Chi tiết:* Initialize config loader from JSON if available
  - `method`: **`get(key: str, default)`** (Dòng 134)
    > *Chi tiết:* Get config value from new system (with fallback to class attributes)

Args:
    key: Configuration key (dot notation, e.g., 'server.host')
    default: Default value if not found
    
Returns:
    Configuration value
  - `method`: **`set(key: str, value)`** (Dòng 150)
    > *Chi tiết:* Set config value in new system

Args:
    key: Configuration key (dot notation)
    value: Value to set

------------------------------

### 📄 File: `config/auto_chat.json`
- *(File cấu hình hoặc file rỗng, không chứa hàm)*

------------------------------

### 📄 File: `config/gold_config.json`
- *(File cấu hình hoặc file rỗng, không chứa hàm)*

------------------------------

### 📄 File: `config_system/README.md`
- *(File cấu hình hoặc file rỗng, không chứa hàm)*

------------------------------

### 📄 File: `config_system/__init__.py`
- *(File cấu hình hoặc file rỗng, không chứa hàm)*

------------------------------

### 📄 File: `config_system/config_loader.py`
- **Class `ConfigLoader`** (Dòng 11)
  > *Mô tả:* Singleton configuration loader with hot-reload support
  - `method`: **`__new__()`** (Dòng 16)
  - `method`: **`__init__()`** (Dòng 22)
  - `method`: **`get_instance()`** (Dòng 32)
    > *Chi tiết:* Get singleton instance
  - `method`: **`load(config_path: str)`** (Dòng 36)
    > *Chi tiết:* Load configuration from JSON file

Args:
    config_path: Path to config file (JSON)
    
Returns:
    Loaded configuration dictionary
  - `method`: **`_apply_env_overrides()`** (Dòng 62)
    > *Chi tiết:* Apply environment variable overrides (CLIENTNRO_* variables)
  - `method`: **`reload()`** (Dòng 72)
    > *Chi tiết:* Reload configuration from file
  - `method`: **`get(key: str, default)`** (Dòng 84)
    > *Chi tiết:* Get configuration value using dot notation

Args:
    key: Configuration key (e.g., 'server.host', 'ai.enabled')
    default: Default value if key not found
    
Returns:
    Configuration value or default
  - `method`: **`set(key: str, value: Any)`** (Dòng 106)
    > *Chi tiết:* Set configuration value using dot notation

Args:
    key: Configuration key (e.g., 'server.host')
    value: Value to set
  - `method`: **`get_all()`** (Dòng 126)
    > *Chi tiết:* Get entire configuration dictionary
  - `method`: **`watch(callback: Callable[[dict], None])`** (Dòng 130)
    > *Chi tiết:* Register a callback to be called when config is reloaded

Args:
    callback: Function to call with new config dict
  - `method`: **`save(config_path: Optional[str])`** (Dòng 139)
    > *Chi tiết:* Save current configuration to file

Args:
    config_path: Path to save to (uses loaded path if None)
  - `method`: **`merge(other_config: dict)`** (Dòng 153)
    > *Chi tiết:* Merge another config dict into current config

Args:
    other_config: Dictionary to merge
  - `method`: **`_deep_merge(base: dict, update: dict)`** (Dòng 162)
    > *Chi tiết:* Deep merge update dict into base dict
- `function`: **`get_config(key: str, default)`** (Dòng 172)
  > *Mô tả:* Quick access to config value

Args:
    key: Configuration key (dot notation)
    default: Default value if not found
    
Returns:
    Configuration value

------------------------------

### 📄 File: `config_system/config_validator.py`
- **Class `ConfigValidator`** (Dòng 7)
  > *Mô tả:* Validates configuration against schema and rules
  - `method`: **`validate(config: dict)`** (Dòng 79)
    > *Chi tiết:* Validate entire configuration

Args:
    config: Configuration dictionary to validate
    
Returns:
    Tuple of (is_valid, list_of_errors)
  - `method`: **`_validate_section(section_name: str, section_data: Any, schema: dict)`** (Dòng 107)
    > *Chi tiết:* Validate a configuration section
  - `method`: **`_validate_field(field_path: str, value: Any, schema: dict)`** (Dòng 138)
    > *Chi tiết:* Validate a single field
  - `method`: **`validate_field(key: str, value: Any)`** (Dòng 172)
    > *Chi tiết:* Validate a single field by key path

Args:
    key: Field key (e.g., 'server.port')
    value: Value to validate
    
Returns:
    Tuple of (is_valid, error_message)
- `function`: **`validate_config(config: dict)`** (Dòng 205)
  > *Mô tả:* Convenience function to validate configuration

Args:
    config: Configuration dictionary
    
Returns:
    Tuple of (is_valid, list_of_errors)

------------------------------

### 📄 File: `config_system/default.json`
- *(File cấu hình hoặc file rỗng, không chứa hàm)*

------------------------------

### 📄 File: `constants/__init__.py`
- *(File cấu hình hoặc file rỗng, không chứa hàm)*

------------------------------

### 📄 File: `constants/cmd.py`
- **Class `Cmd`** (Dòng 1)

------------------------------

### 📄 File: `controller/__init__.py`
- *(File cấu hình hoặc file rỗng, không chứa hàm)*

------------------------------

### 📄 File: `controller/controller.py`
- **Class `Controller`** (Dòng 37)
  > *Mô tả:* Quản lý xử lý tin nhắn và trạng thái game cho một tài khoản.

Thuộc tính chính:
  - account: đối tượng tài khoản đang điều khiển
  - tile_map, mobs, npcs: trạng thái bản đồ và thực thể
  - movement, auto_play, auto_pet, xmap: các dịch vụ liên quan
  - `method`: **`__init__(account)`** (Dòng 45)
    > *Chi tiết:* Khởi tạo Controller cho `account`: thiết lập trạng thái và các dịch vụ liên quan.
  - `method`: **`toggle_auto_quest(enabled: bool)`** (Dòng 100)
    > *Chi tiết:* Bật hoặc tắt chế độ Auto Quest.
  - `method`: **`toggle_autoplay(enabled: bool)`** (Dòng 107)
    > *Chi tiết:* Bật hoặc tắt chế độ AutoPlay; khi bật, thêm task AutoPlay vào `account.tasks` nếu có.
  - `method`: **`toggle_auto_pet(enabled: bool)`** (Dòng 116)
    > *Chi tiết:* Bật hoặc tắt chế độ AutoPet; khi bật, thêm task AutoPet vào `account.tasks` nếu có.
  - `method`: **`toggle_auto_attack(enabled: bool)`** (Dòng 125)
    > *Chi tiết:* Bật hoặc tắt Auto Attack (Universal - cho cả mobs và chars)
  - `method`: **`toggle_auto_boss(enabled: bool, boss_name: str)`** (Dòng 137)
    > *Chi tiết:* Bật hoặc tắt chế độ Auto Boss.
  - `method`: **`toggle_auto_item(enabled: bool, item_id: int)`** (Dòng 147)
    > *Chi tiết:* Bật hoặc tắt chế độ Auto Item.
  - `method`: **`toggle_ai_agent(enabled: bool)`** (Dòng 159)
    > *Chi tiết:* Bật hoặc tắt AI Agent (Neural Network control)
  - `method`: **`on_message(msg: Message)`** (Dòng 182)
    > *Chi tiết:* Chuyển tiếp tin nhắn theo `msg.command` đến handler tương ứng.
  - `method`: **`_handle_magic_tree(msg: Message)`** (Dòng 339)
    > *Chi tiết:* Xử lý magic tree menu (Cmd -34 sub_cmd 1).
  - `method`: **`_handle_input_form(msg: Message)`** (Dòng 357)
    > *Chi tiết:* Xử lý input form từ server (Cmd -125).
  - `method`: **`_handle_combine_msg(msg: Message)`** (Dòng 373)
    > *Chi tiết:* Xử lý server combine message (Cmd -81).
Sub-types:
  0 = OPEN_TAB_COMBINE (mở tab combine)
  1 = REOPEN_TAB_COMBINE (mở lại tab combine)
  2 = COMBINE_SUCCESS (ép thành công)
  3 = COMBINE_FAIL (ép thất bại)
  5 = COMBINE_DRAGON_BALL
  6 = OPEN_ITEM
  - `async_method`: **`eat_pea()`** (Dòng 407)
    > *Chi tiết:* Tìm và ăn đậu trong hành trang khi HP/MP thấp.
  - `method`: **`find_item_in_bag(item_id: int)`** (Dòng 411)
    > *Chi tiết:* Tìm item trong hành trang và trả về danh sách kết quả.
  - `async_method`: **`use_item_by_id(item_id: int, action_type: int)`** (Dòng 415)
    > *Chi tiết:* Tìm và thực hiện hành động với item theo ID.
  - `async_method`: **`attack_nearest_mob()`** (Dòng 419)
    > *Chi tiết:* Tấn công quái vật gần nhất một lần.
  - `async_method`: **`auto_upgrade_stats(target_hp: int, target_mp: int, target_sd: int)`** (Dòng 423)
    > *Chi tiết:* Tự động cộng chỉ số tiềm năng cho đến khi đạt mục tiêu.

------------------------------

### 📄 File: `controller/handlers/__init__.py`
- *(File cấu hình hoặc file rỗng, không chứa hàm)*

------------------------------

### 📄 File: `controller/handlers/base_handler.py`
- **Class `BaseHandler`** (Dòng 8)
  > *Mô tả:* Base class cho tất cả message handlers.

Cung cấp access đến controller và các thuộc tính thường dùng.
  - `method`: **`__init__(controller)`** (Dòng 14)
    > *Chi tiết:* Khởi tạo handler với controller reference.

Args:
    controller: Controller instance chứa state và services
  - `method`: **`handle(msg: Message)`** (Dòng 23)
    > *Chi tiết:* Xử lý message - phải được override bởi subclass.

Args:
    msg: Message object cần xử lý
    
Raises:
    NotImplementedError: Nếu subclass không implement method này

------------------------------

### 📄 File: `controller/handlers/character_handler.py`
- **Class `CharacterHandler`** (Dòng 9)
  > *Mô tả:* Handler xử lý character stats, power, exp updates.
  - `method`: **`_read_gold(reader, char)`** (Dòng 12)
    > *Chi tiết:* Đọc giá trị vàng từ packet. Server version >= 214 gửi writeLong (8 bytes).
  - `method`: **`process_me_load_point(msg: Message)`** (Dòng 16)
    > *Chi tiết:* Đọc thông tin chỉ số nhân vật khi vào map hoặc load point và cập nhật thuộc tính `char`.
  - `method`: **`process_sub_command(msg: Message)`** (Dòng 59)
    > *Chi tiết:* Xử lý SUB_COMMAND với nhiều trường hợp con (tải thông tin nhân vật, cập nhật HP/MP, tài sản, items).
  - `method`: **`process_power_info(msg: Message)`** (Dòng 210)
    > *Chi tiết:* Xử lý thông tin sức mạnh (POWER_INFO -115).
  - `method`: **`process_player_up_exp(msg: Message)`** (Dòng 223)
    > *Chi tiết:* Xử lý cập nhật EXP/Sức mạnh theo loại gói tin PLAYER_UP_EXP.
  - `method`: **`process_item_buy(msg: Message)`** (Dòng 243)
    > *Chi tiết:* Xử lý cập nhật tài sản khi mua/bán item (Cmd 6).
  - `method`: **`process_me_change_coin(msg: Message)`** (Dòng 257)
    > *Chi tiết:* Xử lý thay đổi xu từ server (Cmd -1).
  - `method`: **`process_me_up_coin_bag(msg: Message)`** (Dòng 267)
    > *Chi tiết:* Xử lý tăng/giảm xu trong hành trang trực tiếp (Cmd 95).

------------------------------

### 📄 File: `controller/handlers/combat_handler.py`
- **Class `CombatHandler`** (Dòng 9)
  > *Mô tả:* Handler xử lý mob HP, death, respawn, attacks.
  - `method`: **`process_mob_hp(msg: Message)`** (Dòng 12)
    > *Chi tiết:* Cập nhật HP của mob (MOB_HP), xử lý các dữ liệu bổ sung nếu có.
  - `method`: **`process_npc_die(msg: Message)`** (Dòng 37)
    > *Chi tiết:* Xử lý sự kiện mob chết (NPC_DIE) và cập nhật trạng thái trong `self.mobs`.
  - `method`: **`process_npc_live(msg: Message)`** (Dòng 60)
    > *Chi tiết:* Xử lý NPC_LIVE: cập nhật HP và trạng thái khi quái vật hồi sinh.
  - `method`: **`process_player_attack_npc(msg: Message)`** (Dòng 86)
    > *Chi tiết:* Xử lý sự kiện người chơi tấn công NPC (PLAYER_ATTACK_NPC).

------------------------------

### 📄 File: `controller/handlers/inventory_handler.py`
- **Class `InventoryHandler`** (Dòng 10)
  > *Mô tả:* Handler xử lý bag, pet info, item usage.
  - `method`: **`process_bag_info(msg: Message)`** (Dòng 13)
    > *Chi tiết:* Cập nhật dữ liệu túi đồ (BAG): xử lý danh sách ô, cập nhật số lượng hoặc thay đổi ô trong túi.
  - `method`: **`process_box_info(msg: Message)`** (Dòng 86)
    > *Chi tiết:* Cập nhật dữ liệu rương đồ (BOX): xử lý danh sách ô, cập nhật số lượng hoặc thay đổi ô trong rương.
  - `method`: **`process_pet_info(msg: Message)`** (Dòng 159)
    > *Chi tiết:* Đọc thông tin đệ tử (PET_INFO) và cập nhật đối tượng pet trong account.
  - `async_method`: **`eat_pea()`** (Dòng 242)
    > *Chi tiết:* Tìm và ăn đậu trong hành trang khi HP/MP thấp.
  - `method`: **`find_item_in_bag(item_id: int)`** (Dòng 277)
    > *Chi tiết:* Tìm item trong hành trang và trả về danh sách kết quả.
  - `async_method`: **`use_item_by_id(item_id: int, action_type: int)`** (Dòng 289)
    > *Chi tiết:* Tìm và thực hiện hành động với item theo ID (sử dụng hoặc bán).
:param item_id: ID template của item.
:param action_type: 0 = Sử dụng, 1 = Bán.

------------------------------

### 📄 File: `controller/handlers/login_handler.py`
- **Class `LoginHandler`** (Dòng 9)
  > *Mô tả:* Handler xử lý NOT_LOGIN và NOT_MAP messages.
  - `method`: **`message_not_login(msg: Message)`** (Dòng 12)
    > *Chi tiết:* Xử lý các sub-command của NOT_LOGIN (ví dụ server list, login fail...).
  - `method`: **`message_not_map(msg: Message)`** (Dòng 58)
    > *Chi tiết:* Xử lý NOT_MAP sub-commands (ví dụ: UPDATE_VERSION).

------------------------------

### 📄 File: `controller/handlers/map_handler.py`
- **Class `MapHandler`** (Dòng 12)
  > *Mô tả:* Handler xử lý map info, zones, updates.
  - `method`: **`process_map_info(msg: Message)`** (Dòng 15)
    > *Chi tiết:* Đọc MAP_INFO và cập nhật: bản đồ, tọa độ nhân vật, waypoints, mobs và NPCs.
  - `method`: **`process_zone_list(msg: Message)`** (Dòng 103)
    > *Chi tiết:* Xử lý gói tin danh sách khu vực (Cmd 29).
  - `method`: **`process_map_offline(msg: Message)`** (Dòng 143)
    > *Chi tiết:* Xử lý thông báo bản đồ chuyển sang chế độ offline (MAP_OFFLINE).
  - `method`: **`process_update_data(msg: Message)`** (Dòng 155)
    > *Chi tiết:* Xử lý gói tin UPDATE_DATA (-87).
  - `method`: **`process_update_map(msg: Message)`** (Dòng 177)
    > *Chi tiết:* Xử lý gói tin UPDATE_MAP để cập nhật MobTemplate.

------------------------------

### 📄 File: `controller/handlers/misc_handler.py`
- **Class `MiscHandler`** (Dòng 11)
  > *Mô tả:* Handler xử lý các messages còn lại.
  - `method`: **`process_game_info(msg: Message)`** (Dòng 14)
    > *Chi tiết:* Đọc và ghi log chuỗi thông tin do server gửi (GAME_INFO).
  - `method`: **`process_special_skill(msg: Message)`** (Dòng 23)
    > *Chi tiết:* Phân tích thông tin kỹ năng đặc biệt (các kiểu khác nhau theo `special_type`).
  - `method`: **`process_message_time(msg: Message)`** (Dòng 39)
    > *Chi tiết:* Đọc thông báo thời gian (MESSAGE_TIME) và ghi log nội dung cùng thời hạn.
  - `method`: **`process_change_flag(msg: Message)`** (Dòng 50)
    > *Chi tiết:* Xử lý thay đổi cờ trạng thái của nhân vật (CHANGE_FLAG).
  - `method`: **`process_max_stamina(msg: Message)`** (Dòng 62)
    > *Chi tiết:* Cập nhật giá trị thể lực tối đa của người chơi (MAXSTAMINA).
  - `method`: **`process_stamina(msg: Message)`** (Dòng 71)
    > *Chi tiết:* Cập nhật thể lực hiện tại (STAMINA).
  - `method`: **`process_update_active_point(msg: Message)`** (Dòng 80)
    > *Chi tiết:* Cập nhật điểm hoạt động/năng động của người chơi (UPDATE_ACTIVEPOINT).
  - `method`: **`process_thach_dau(msg: Message)`** (Dòng 89)
    > *Chi tiết:* Xử lý thông tin thách đấu (THACHDAU) từ server.
  - `method`: **`process_autoplay(msg: Message)`** (Dòng 98)
    > *Chi tiết:* Nhận trạng thái hoặc cấu hình chế độ tự động từ server (AUTOPLAY).
  - `method`: **`process_mabu(msg: Message)`** (Dòng 107)
    > *Chi tiết:* Xử lý gói tin liên quan đến Mabu và ghi lại trạng thái (MABU).
  - `method`: **`process_the_luc(msg: Message)`** (Dòng 116)
    > *Chi tiết:* Xử lý thông tin thể lực (THELUC) nhận từ server.
  - `method`: **`process_create_player(msg: Message)`** (Dòng 125)
    > *Chi tiết:* Xử lý yêu cầu tạo nhân vật từ server (Cmd 2).
  - `async_method`: **`attack_nearest_mob()`** (Dòng 159)
    > *Chi tiết:* Tấn công quái vật gần nhất một lần.
  - `async_method`: **`auto_upgrade_stats(target_hp: int, target_mp: int, target_sd: int)`** (Dòng 186)
    > *Chi tiết:* Tự động cộng chỉ số tiềm năng cho đến khi đạt mục tiêu.

------------------------------

### 📄 File: `controller/handlers/notification_handler.py`
- **Class `NotificationHandler`** (Dòng 9)
  > *Mô tả:* Handler xử lý server messages, chat, boss notifications.
  - `method`: **`process_server_message(msg: Message)`** (Dòng 12)
    > *Chi tiết:* Xử lý thông báo từ server (Cmd -25).
  - `method`: **`process_chat_server(msg: Message)`** (Dòng 31)
    > *Chi tiết:* Xử lý chat thế giới từ server (Cmd 92).
  - `method`: **`process_chat_map(msg: Message)`** (Dòng 40)
    > *Chi tiết:* Xử lý chat trong map (Cmd 44).
  - `method`: **`process_server_alert(msg: Message)`** (Dòng 50)
    > *Chi tiết:* Xử lý thông báo server (Cmd 94).
  - `method`: **`process_chat_vip(msg: Message)`** (Dòng 68)
    > *Chi tiết:* Xử lý chat VIP (Cmd 93) - Kênh chính thông báo Boss.
  - `method`: **`process_big_message(msg: Message)`** (Dòng 77)
    > *Chi tiết:* Xử lý thông báo lớn (Cmd -70).
  - `method`: **`process_big_boss(msg: Message, type: int)`** (Dòng 90)
    > *Chi tiết:* Xử lý thông tin Big Boss (Cmd 101, 102).
  - `method`: **`check_boss_notification(text: str, source: str)`** (Dòng 97)
    > *Chi tiết:* Kiểm tra nội dung chat xem có phải thông báo boss xuất hiện không.

------------------------------

### 📄 File: `controller/handlers/npc_handler.py`
- **Class `NPCHandler`** (Dòng 11)
  > *Mô tả:* Handler xử lý NPC chat, menu, add/remove.
  - `method`: **`process_npc_chat(msg: Message)`** (Dòng 14)
    > *Chi tiết:* Ghi log nội dung chat của NPC (NPC_CHAT).
  - `method`: **`process_npc_add_remove(msg: Message)`** (Dòng 29)
    > *Chi tiết:* Xử lý lệnh thêm/bớt NPC (hiện chỉ đọc template id và không hành động thêm).
  - `method`: **`process_open_ui_confirm(msg: Message)`** (Dòng 38)
    > *Chi tiết:* Xử lý menu NPC (OPEN_UI_CONFIRM): đọc template id, nội dung menu và các lựa chọn.

------------------------------

### 📄 File: `controller/handlers/player_handler.py`
- **Class `PlayerHandler`** (Dòng 11)
  > *Mô tả:* Handler xử lý player add, move, die, list updates.
  - `method`: **`process_player_add(msg: Message)`** (Dòng 14)
    > *Chi tiết:* Đọc thông tin khi có player mới xuất hiện trên map và ghi log cơ bản.
  - `method`: **`read_char_info(reader: Reader)`** (Dòng 32)
    > *Chi tiết:* Đọc thông tin cơ bản của một nhân vật từ `reader` và trả về dict chứa giá trị như level, tên, vị trí, hiệu ứng.
  - `method`: **`process_player_move(msg: Message)`** (Dòng 65)
    > *Chi tiết:* Cập nhật vị trí khi server gửi thông tin di chuyển của một người chơi.
  - `method`: **`process_player_die(msg: Message)`** (Dòng 76)
    > *Chi tiết:* Xử lý khi một người chơi chết; nếu là nhân vật local thì thực hiện bước revive/return flow.
  - `async_method`: **`_handle_revive_and_return(target_map_id: int, resume_auto_play: bool, resume_auto_pet: bool)`** (Dòng 100)
    > *Chi tiết:* Xử lý hồi sinh, đợi về nhà, quay lại map cũ (khu ngẫu nhiên) và tiếp tục auto.
  - `method`: **`process_player_list_update(msg: Message)`** (Dòng 133)
    > *Chi tiết:* Xử lý phản hồi REQUEST_PLAYERS (Cmd 18) - cập nhật vị trí và HP người chơi.

------------------------------

### 📄 File: `controller/handlers/task_handler.py`
- **Class `TaskHandler`** (Dòng 9)
  > *Mô tả:* Handler xử lý task get, update, next.
  - `method`: **`process_task_get(msg: Message)`** (Dòng 12)
    > *Chi tiết:* Phân tích gói TASK_GET và lưu thông tin nhiệm vụ vào nhân vật.
  - `method`: **`process_task_update(msg: Message)`** (Dòng 53)
    > *Chi tiết:* Cập nhật tiến độ nhiệm vụ (TASK_UPDATE).
  - `method`: **`process_task_next(msg: Message)`** (Dòng 85)
    > *Chi tiết:* Xử lý chuyển bước nhiệm vụ (TASK_NEXT - 41).

------------------------------

### 📄 File: `core/__init__.py`
- *(File cấu hình hoặc file rỗng, không chứa hàm)*

------------------------------

### 📄 File: `core/account.py`
- **Class `Account`** (Dòng 14)
  > *Mô tả:* Encapsulates all objects and data for a single game account session.
  - `method`: **`__init__(username, password, version, host, port, proxy)`** (Dòng 18)
  - `async_method`: **`login()`** (Dòng 48)
    > *Chi tiết:* Connects and performs the login sequence for this account.
  - `async_method`: **`handle_disconnect()`** (Dòng 130)
    > *Chi tiết:* Handles the disconnection event, triggering auto-reconnect if configured.
  - `method`: **`stop_tasks()`** (Dòng 165)
    > *Chi tiết:* Stops all running asyncio tasks for this account without a full logout.
  - `method`: **`stop()`** (Dòng 172)
    > *Chi tiết:* Stops all running tasks and disconnects the session for this account.
This is considered a manual stop, so auto-reconnect is disabled.

------------------------------

### 📄 File: `core/account_manager.py`
- **Class `AccountManager`** (Dòng 6)
  - `method`: **`__init__()`** (Dòng 7)
  - `method`: **`load_accounts()`** (Dòng 15)
    > *Chi tiết:* Loads account credentials from Config and creates Account objects.
  - `async_method`: **`start_all()`** (Dòng 36)
    > *Chi tiết:* Starts the login process for all loaded accounts concurrently (respecting limit).
  - `method`: **`stop_all()`** (Dòng 57)
    > *Chi tiết:* Stops all accounts.
  - `method`: **`get_active_account_count()`** (Dòng 63)
  - `method`: **`get_target_accounts()`** (Dòng 66)
    > *Chi tiết:* Resolves the command_target to a list of account objects.

------------------------------

### 📄 File: `data/item_data.txt`
- *(File cấu hình hoặc file rỗng, không chứa hàm)*

------------------------------

### 📄 File: `data/mob_data.txt`
- *(File cấu hình hoặc file rỗng, không chứa hàm)*

------------------------------

### 📄 File: `handlers/__init__.py`
- *(File cấu hình hoặc file rỗng, không chứa hàm)*

------------------------------

### 📄 File: `handlers/ai_command_handler.py`
- **Class `AICommandHandler`** (Dòng 11)
  > *Mô tả:* Handles all AI-related terminal commands
  - `method`: **`__init__()`** (Dòng 14)
  - `method`: **`load_weights(weights_path: str)`** (Dòng 26)
    > *Chi tiết:* Load AI weights from file
  - `method`: **`register_account(account_id: str, controller, service)`** (Dòng 35)
    > *Chi tiết:* Register an account for AI control
  - `async_method`: **`handle_ai_command(parts: list[str], manager)`** (Dòng 45)
    > *Chi tiết:* Handle AI commands.
Returns True if command was handled, False otherwise.
  - `method`: **`_handle_trainer_commands(parts: list[str])`** (Dòng 104)
    > *Chi tiết:* Handle shared trainer commands
  - `method`: **`_show_ai_help()`** (Dòng 134)
    > *Chi tiết:* Show AI command help
  - `method`: **`_show_status()`** (Dòng 164)
    > *Chi tiết:* Show AI system status
  - `method`: **`_show_info()`** (Dòng 180)
    > *Chi tiết:* Show AI model info
  - `async_method`: **`_ai_on(parts: list[str], manager)`** (Dòng 192)
    > *Chi tiết:* Enable AI for account(s)
  - `async_method`: **`_ai_off(parts: list[str], manager)`** (Dòng 198)
    > *Chi tiết:* Disable AI for account(s)
  - `async_method`: **`_ai_toggle(parts: list[str], manager)`** (Dòng 203)
    > *Chi tiết:* Toggle AI status
  - `method`: **`_load_weights(parts: list[str])`** (Dòng 209)
    > *Chi tiết:* Load weights from file
  - `method`: **`_reset_weights()`** (Dòng 221)
    > *Chi tiết:* Reset to default weights
  - `method`: **`_handle_goal_commands(parts: list[str])`** (Dòng 226)
    > *Chi tiết:* Handle goal management commands
  - `method`: **`_parse_goal_params(goal_type: str, params_str: str)`** (Dòng 262)
    > *Chi tiết:* Parse goal parameters from string
  - `method`: **`_handle_ai_group_commands(parts: list[str], manager)`** (Dòng 284)
    > *Chi tiết:* Handle AI group commands
  - `method`: **`_handle_zone_commands(parts: list[str])`** (Dòng 343)
    > *Chi tiết:* Handle zone distribution commands
  - `method`: **`_handle_team_commands(parts: list[str])`** (Dòng 379)
    > *Chi tiết:* Handle team coordination commands

------------------------------

### 📄 File: `logic/__init__.py`
- *(File cấu hình hoặc file rỗng, không chứa hàm)*

------------------------------

### 📄 File: `logic/auto_NVBoMong.py`
- **Class `AutoState`** (Dòng 35)
- **Class `QuestInfo`** (Dòng 43)
  - `method`: **`__init__()`** (Dòng 44)
  - `method`: **`current_progress()`** (Dòng 55)
  - `method`: **`__str__()`** (Dòng 58)
- **Class `AutoQuest`** (Dòng 64)
  - `method`: **`__init__(controller)`** (Dòng 65)
  - `method`: **`start()`** (Dòng 81)
  - `method`: **`stop()`** (Dòng 98)
  - `method`: **`get_stats()`** (Dòng 109)
    > *Chi tiết:* Trả về thống kê hiện tại
  - `async_method`: **`_interact_with_npc_menu(npc_template_id: int, menu_options: list[int])`** (Dòng 134)
    > *Chi tiết:* Hàm helper chung để tương tác với NPC:
1. Kiểm tra vị trí & khoảng cách (tự động teleport nếu > 60px).
2. Mở menu NPC.
3. Lần lượt chọn các option trong menu_options (nếu có).
  - `async_method`: **`refresh_quest_info()`** (Dòng 191)
    > *Chi tiết:* Query NPC Bố Mộng để lấy thông tin quest hiện tại.
Sử dụng helper _interact_with_npc_menu.
  - `async_method`: **`transition_to(new_state: AutoState)`** (Dòng 208)
  - `async_method`: **`_run_loop()`** (Dòng 213)
  - `async_method`: **`update()`** (Dòng 227)
  - `async_method`: **`handle_idle()`** (Dòng 256)
  - `async_method`: **`handle_get_quest()`** (Dòng 259)
  - `async_method`: **`handle_navigate_to_map()`** (Dòng 277)
  - `async_method`: **`handle_select_zone()`** (Dòng 299)
    > *Chi tiết:* Chọn khu vực tối ưu dựa trên Hive Scoring
  - `async_method`: **`handle_execute_quest()`** (Dòng 350)
  - `async_method`: **`handle_report_quest()`** (Dòng 376)
  - `method`: **`parse_quest_info(menu_text: str)`** (Dòng 422)
  - `method`: **`increment_kill_count(mob_template_id: int)`** (Dòng 477)
  - `method`: **`get_quest_target_ids()`** (Dòng 503)
  - `method`: **`_can_access_map(map_id: int)`** (Dòng 522)
    > *Chi tiết:* Kiểm tra xem nhân vật có thể vào map đích không dựa trên điều kiện.
  - `async_method`: **`_cancel_and_get_new_quest()`** (Dòng 530)
    > *Chi tiết:* Huỷ nhiệm vụ hiện tại và nhận nhiệm vụ mới.
  - `async_method`: **`go_to_map(map_id: int)`** (Dòng 564)

------------------------------

### 📄 File: `logic/auto_attack.py`
- **Class `AutoAttack`** (Dòng 16)
  > *Mô tả:* Auto Attack service - Tự động tấn công mobs VÀ chars (bosses/players)
Based on C# AutoSendAttack implementation
  - `method`: **`__init__(controller)`** (Dòng 22)
  - `method`: **`start()`** (Dòng 36)
    > *Chi tiết:* Bật Auto Attack
  - `method`: **`stop()`** (Dòng 43)
    > *Chi tiết:* Tắt Auto Attack
  - `method`: **`toggle()`** (Dòng 51)
    > *Chi tiết:* Toggle Auto Attack on/off - giống C# toggleAutoAttack()
  - `async_method`: **`_attack_loop()`** (Dòng 58)
    > *Chi tiết:* Main attack loop - chạy liên tục
  - `async_method`: **`_update()`** (Dòng 70)
    > *Chi tiết:* Update logic - giống C# AutoSendAttack.update()
Logic:
1. Tạo vMob và vChar vectors
2. Nếu có mob_focus -> add vào vMob
3. Else nếu có char_focus -> add vào vChar
4. Nếu có target, check cooldown rồi send attack với type = -1 (auto)
  - `method`: **`_get_current_skill(my_char)`** (Dòng 168)
    > *Chi tiết:* Lấy skill hiện tại (myskill trong C# code)
Returns: Skill object hoặc None
  - `method`: **`_auto_focus_by_priority()`** (Dòng 185)
    > *Chi tiết:* Tự động focus target theo priority mode
Internal method được gọi bởi _update()
  - `method`: **`set_priority_mode(mode: str, names: list[str], prefer_boss: bool)`** (Dòng 204)
    > *Chi tiết:* Thiết lập chế độ ưu tiên target

Args:
    mode: Chế độ ưu tiên
        - "nearest": Gần nhất (default)
        - "boss_first": Ưu tiên boss/char trước, không có mới tìm mob
        - "name_match": Tìm theo tên trong priority_names
    names: Danh sách tên ưu tiên (dùng cho mode "name_match")
    prefer_boss: Ưu tiên boss khi khoảng cách tương đương (dùng cho mode "nearest")
  - `method`: **`set_target_nearest(target_type: str)`** (Dòng 222)
    > *Chi tiết:* Tìm và focus vào mob/char gần nhất trong khoảng cách max_target_distance
Wrapper method sử dụng target_utils

Args:
    target_type: "mob", "char", hoặc "both"
Returns:
    True nếu tìm thấy target, False nếu không
  - `method`: **`set_target_mob(mob_id: int)`** (Dòng 241)
    > *Chi tiết:* Focus vào mob cụ thể bằng ID
Wrapper method sử dụng target_utils

Args:
    mob_id: ID của mob cần target
Returns:
    True nếu mob tồn tại, False nếu không
  - `method`: **`set_target_char(char_id: int)`** (Dòng 253)
    > *Chi tiết:* Focus vào char cụ thể bằng ID (boss/player)
Wrapper method sử dụng target_utils

Args:
    char_id: ID của char cần target
Returns:
    True nếu char tồn tại, False nếu không
  - `method`: **`clear_target()`** (Dòng 265)
    > *Chi tiết:* Xóa tất cả target hiện tại - Wrapper method sử dụng target_utils
  - `method`: **`set_target_by_name(name: str, target_type: str)`** (Dòng 270)
    > *Chi tiết:* Focus vào mob/char theo tên (hỗ trợ fuzzy matching)
Wrapper method sử dụng target_utils

Args:
    name: Tên hoặc một phần tên cần tìm (case-insensitive)
    target_type: "mob", "char", hoặc "both"
Returns:
    True nếu tìm thấy, False nếu không

------------------------------

### 📄 File: `logic/auto_boss.py`
- **Class `BossRole`** (Dòng 10)
- **Class `BossState`** (Dòng 15)
  > *Mô tả:* Enum cho các trạng thái của Auto Boss
- **Class `BossHuntCoordinator`** (Dòng 26)
  > *Mô tả:* Singleton quản lý phối hợp giữa nhiều user khi săn boss.
Chỉ phối hợp giữa các user trong cùng group.
  - `method`: **`__new__()`** (Dòng 33)
  - `method`: **`__init__()`** (Dòng 39)
  - `method`: **`register_hunter(boss_name: str, hunter: 'AutoBoss')`** (Dòng 58)
    > *Chi tiết:* Đăng ký user vào nhóm săn boss
  - `method`: **`unregister_hunter(boss_name: str, hunter: 'AutoBoss')`** (Dòng 67)
    > *Chi tiết:* Hủy đăng ký user
  - `method`: **`get_hunters_in_group(boss_name: str, group_id: str)`** (Dòng 81)
    > *Chi tiết:* Lấy danh sách hunters trong cùng group
  - `method`: **`assign_zones(boss_name: str, group_id: str, total_zones: int)`** (Dòng 88)
    > *Chi tiết:* Chia zone cho các hunter - ROUND-ROBIN để spread out
Returns: Dict mapping username -> list of zone IDs
  - `method`: **`mark_ready(boss_name: str, group_id: str, username: str)`** (Dòng 130)
    > *Chi tiết:* Mark hunter as ready for zone assignment
  - `async_method`: **`wait_for_all_ready(boss_name: str, group_id: str, timeout: float)`** (Dòng 140)
    > *Chi tiết:* Wait for all registered hunters to mark ready
Returns True if all ready, False if timeout
  - `method`: **`broadcast_boss_found(boss_name: str, group_id: str, map_id: int, zone_id: int)`** (Dòng 169)
    > *Chi tiết:* Thông báo tìm thấy boss tới tất cả hunters trong group
  - `method`: **`get_boss_location(boss_name: str, group_id: str)`** (Dòng 180)
    > *Chi tiết:* Lấy vị trí boss nếu đã tìm thấy (trong group)
  - `method`: **`is_boss_found(boss_name: str, group_id: str)`** (Dòng 185)
    > *Chi tiết:* Kiểm tra boss đã được tìm thấy chưa (trong group)
  - `method`: **`get_hunter_count(boss_name: str, group_id: str)`** (Dòng 190)
    > *Chi tiết:* Đếm số user trong group đang săn boss này
- **Class `AutoBoss`** (Dòng 195)
  > *Mô tả:* State machine quản lý quy trình săn boss cho 1 user.
Bao gồm: tìm boss, di chuyển, quét zone, tập hợp team, attack.
  - `method`: **`__init__(controller)`** (Dòng 201)
  - `method`: **`start(boss_name: str)`** (Dòng 244)
    > *Chi tiết:* Bắt đầu săn boss (single mode)
  - `method`: **`start_quest_mode()`** (Dòng 264)
    > *Chi tiết:* Bắt đầu săn boss dựa trên nhiệm vụ hiện tại
  - `method`: **`start_support(boss_name: str, owner_name: str)`** (Dòng 286)
    > *Chi tiết:* Bắt đầu hỗ trợ người khác săn boss
  - `method`: **`add_to_queue(boss_name: str, use_fuzzy: bool)`** (Dòng 296)
    > *Chi tiết:* Thêm boss vào queue, hỗ trợ fuzzy matching
  - `method`: **`clear_queue()`** (Dòng 330)
    > *Chi tiết:* Xóa toàn bộ queue
  - `method`: **`show_queue()`** (Dòng 336)
    > *Chi tiết:* Hiển thị queue hiện tại
  - `method`: **`start_queue()`** (Dòng 347)
    > *Chi tiết:* Bắt đầu săn boss theo queue
  - `method`: **`stop()`** (Dòng 373)
    > *Chi tiết:* Dừng auto boss
  - `method`: **`_get_group_id()`** (Dòng 407)
    > *Chi tiết:* Xác định group_id - TẤT CẢ hunters săn cùng boss = cùng group!
Để enable zone distribution cooperation
  - `async_method`: **`_main_loop()`** (Dòng 415)
    > *Chi tiết:* Main async loop xử lý state machine
  - `async_method`: **`_check_boss_alive()`** (Dòng 467)
    > *Chi tiết:* Kiểm tra boss còn sống trong BossManager
  - `async_method`: **`_state_searching()`** (Dòng 493)
    > *Chi tiết:* State: Tìm boss trong BossManager
  - `method`: **`_find_boss_in_manager()`** (Dòng 520)
    > *Chi tiết:* Tìm boss 'Sống' trong BossManager (case-insensitive)
  - `async_method`: **`_state_navigating()`** (Dòng 544)
    > *Chi tiết:* State: Di chuyển tới map boss
  - `async_method`: **`_state_zone_scanning()`** (Dòng 562)
    > *Chi tiết:* State: Quét các zone được assign (với Hive coordination)
  - `async_method`: **`_initialize_zone_scanning()`** (Dòng 646)
    > *Chi tiết:* Khởi tạo zone scanning: lấy danh sách zone và assign
  - `async_method`: **`_request_zone_change_with_verify(zone_id: int)`** (Dòng 684)
    > *Chi tiết:* Request đổi zone và verify thành công. Returns True nếu thành công.
  - `async_method`: **`_check_zone_for_boss()`** (Dòng 707)
    > *Chi tiết:* Kiểm tra chars (characters/bosses) trong zone có boss target không
  - `async_method`: **`_state_gathering()`** (Dòng 751)
    > *Chi tiết:* State: Tập hợp team về zone có boss
  - `async_method`: **`_wait_for_team()`** (Dòng 774)
    > *Chi tiết:* Đợi team tập hợp, sau đó chuyển sang ATTACKING
  - `async_method`: **`_state_attacking()`** (Dòng 797)
    > *Chi tiết:* State: Attack boss
  - `async_method`: **`_state_recovering()`** (Dòng 874)
    > *Chi tiết:* State: Recovery sau khi chết
  - `async_method`: **`_handle_death()`** (Dòng 894)
    > *Chi tiết:* Xử lý khi character chết
  - `async_method`: **`_on_boss_found_by_team(map_id: int, zone_id: int)`** (Dòng 911)
    > *Chi tiết:* Callback khi team tìm thấy boss
  - `async_method`: **`_is_boss_killed()`** (Dòng 924)
    > *Chi tiết:* Kiểm tra boss còn trong zone không (dùng để detect kill)
  - `async_method`: **`_get_target_boss_in_zone()`** (Dòng 929)
    > *Chi tiết:* Lấy boss target trong zone (sequential kill logic).
Nếu có nhiều boss cùng tên, chỉ trả về 1 boss (HP thấp nhất) để attack.
  - `async_method`: **`_next_boss_in_queue()`** (Dòng 958)
    > *Chi tiết:* Chuyển sang boss tiếp theo trong queue

------------------------------

### 📄 File: `logic/auto_giftcode.py`
- **Class `AutoGiftcode`** (Dòng 7)
  - `method`: **`__init__(controller)`** (Dòng 8)
  - `method`: **`start(codes: list[str])`** (Dòng 16)
  - `method`: **`stop()`** (Dòng 26)
  - `async_method`: **`process()`** (Dòng 30)

------------------------------

### 📄 File: `logic/auto_item.py`
- **Class `AutoItem`** (Dòng 7)
  - `method`: **`__init__(controller)`** (Dòng 8)
  - `method`: **`start(item_id: int)`** (Dòng 15)
    > *Chi tiết:* Starts the auto-item task with specified item ID.
  - `method`: **`stop()`** (Dòng 28)
    > *Chi tiết:* Stops the auto-item task.
  - `method`: **`get_status()`** (Dòng 38)
    > *Chi tiết:* Returns current status information.
  - `async_method`: **`loop()`** (Dòng 52)
    > *Chi tiết:* The main loop for auto-using items every 30 minutes.
  - `async_method`: **`use_item()`** (Dòng 77)
    > *Chi tiết:* Find and use the specified item from inventory.

------------------------------

### 📄 File: `logic/auto_main_quest.py`
- **Class `AutoQuestState`** (Dòng 325)
- **Class `AutoMainQuest`** (Dòng 340)
  - `method`: **`__init__(account)`** (Dòng 341)
  - `method`: **`_load_config()`** (Dòng 370)
    > *Chi tiết:* Load maps_config.json để biết map nào có quái gì
  - `method`: **`_load_map_names()`** (Dòng 378)
    > *Chi tiết:* Load map name data
  - `method`: **`_get_gender_npc(key: str)`** (Dòng 389)
    > *Chi tiết:* Lấy NPC template ID theo gender
  - `method`: **`_get_gender_map(key: str)`** (Dòng 398)
    > *Chi tiết:* Lấy map ID theo gender
  - `method`: **`_get_gender_name(key: str)`** (Dòng 407)
    > *Chi tiết:* Lấy tên theo gender
  - `method`: **`_find_report_npc(step_name: str)`** (Dòng 416)
    > *Chi tiết:* Phân tích sub_name của task để tìm NPC cần báo cáo.
Trả về (npc_template_id, map_id) hoặc None.
  - `method`: **`_find_boss_in_step(step_name: str)`** (Dòng 462)
    > *Chi tiết:* Tìm boss trong sub_name của task
  - `method`: **`_find_mob_in_step(step_name: str)`** (Dòng 473)
    > *Chi tiết:* Tìm quái cần tiêu diệt trong sub_name.
Parse dạng: "Hạ X <tên quái>"
Trả về (mob_name, count_to_kill) hoặc None
  - `method`: **`_find_enter_map_in_step(step_name: str)`** (Dòng 518)
    > *Chi tiết:* Tìm map cần vào trong sub_name.
Trả về map_id hoặc None
  - `method`: **`_find_boss_target(boss_name: str)`** (Dòng 542)
    > *Chi tiết:* Tìm boss trong chars hoặc mobs theo tên
  - `method`: **`_get_boss_hp(target: tuple)`** (Dòng 562)
    > *Chi tiết:* Lấy HP của boss từ target tuple (type, id, data)
  - `method`: **`_get_boss_pos(target: tuple)`** (Dòng 572)
    > *Chi tiết:* Lấy tọa độ (x, y) của boss
  - `method`: **`_get_boss_name(target: tuple)`** (Dòng 583)
    > *Chi tiết:* Lấy tên boss
  - `async_method`: **`_analyze_task()`** (Dòng 595)
    > *Chi tiết:* Phân tích task hiện tại và chọn state phù hợp
  - `async_method`: **`_handle_report_npc(npc_tid: int, target_map: int, step_name: str)`** (Dòng 667)
    > *Chi tiết:* Xử lý báo cáo với NPC
  - `async_method`: **`_handle_mob_kill(target_map: int, mob_tid: int, count: int, mob_name: str, step_name: str)`** (Dòng 734)
    > *Chi tiết:* Xử lý giết quái để hoàn thành nhiệm vụ
  - `async_method`: **`_handle_boss_task(boss_name: str, spawn_maps: list, cui_tid: int, step_name: str)`** (Dòng 770)
    > *Chi tiết:* Xử lý săn boss cho nhiệm vụ
  - `async_method`: **`_use_cui_teleport(boss_name: str, spawn_maps: list, cui_tid: int)`** (Dòng 846)
    > *Chi tiết:* Sử dụng NPC Cui để teleport tới boss
  - `async_method`: **`_boss_fight_loop(boss_name: str, spawn_maps: list)`** (Dòng 883)
    > *Chi tiết:* Vòng lặp chiến đấu với boss
  - `async_method`: **`_handle_enter_map(target_map: int)`** (Dòng 997)
    > *Chi tiết:* Xử lý vào một bản đồ (task yêu cầu chỉ cần vào map là hoàn thành)
  - `method`: **`_check_stat_task(step_name: str)`** (Dòng 1014)
    > *Chi tiết:* Kiểm tra xem bước có yêu cầu đạt sức mạnh X không
  - `async_method`: **`_handle_stat_task(stat_type: str, required_value: int)`** (Dòng 1046)
    > *Chi tiết:* Xử lý task yêu cầu đạt chỉ số (sức mạnh, HP, etc)
  - `method`: **`_get_nearest_valid_mob(target_mob_id: int)`** (Dòng 1114)
    > *Chi tiết:* Tìm quái hợp lệ gần nhất
  - `async_method`: **`start()`** (Dòng 1134)
  - `async_method`: **`stop()`** (Dòng 1149)
  - `method`: **`get_status()`** (Dòng 1172)
  - `method`: **`get_stats()`** (Dòng 1179)
  - `async_method`: **`_quest_loop()`** (Dòng 1200)
    > *Chi tiết:* Vòng lặp chính

------------------------------

### 📄 File: `logic/auto_msm.py`
- **Class `AutoMsm`** (Dòng 5)
  - `method`: **`__init__(controller)`** (Dòng 6)
  - `method`: **`start(target)`** (Dòng 22)
  - `method`: **`stop()`** (Dòng 33)
  - `method`: **`on_server_message(text: str)`** (Dòng 42)
  - `async_method`: **`_run_loop()`** (Dòng 52)
  - `async_method`: **`_tick()`** (Dòng 62)

------------------------------

### 📄 File: `logic/auto_pet.py`
- **Class `AutoPet`** (Dòng 10)
  - `method`: **`__init__(controller)`** (Dòng 11)
  - `method`: **`start()`** (Dòng 16)
    > *Chi tiết:* Starts the auto-pet leveling task.
  - `method`: **`stop()`** (Dòng 30)
    > *Chi tiết:* Stops the auto-pet leveling task.
  - `async_method`: **`loop()`** (Dòng 38)
    > *Chi tiết:* The main loop for checking pet status and taking action.
  - `async_method`: **`check_and_feed()`** (Dòng 61)
    > *Chi tiết:* Kiểm tra thể lực của đệ tử và cho ăn đậu nếu cần.

------------------------------

### 📄 File: `logic/auto_play.py`
- **Class `AutoPlay`** (Dòng 9)
  - `method`: **`__init__(controller)`** (Dòng 10)
  - `method`: **`start()`** (Dòng 16)
  - `method`: **`stop()`** (Dòng 24)
  - `async_method`: **`loop()`** (Dòng 31)
  - `async_method`: **`tansat()`** (Dòng 44)
  - `async_method`: **`_attack_char_focus(char_focus: dict, service, my_char)`** (Dòng 179)
    > *Chi tiết:* Tấn công char_focus (Boss hoặc Player)
char_focus là dict chứa thông tin char từ controller.chars
  - `method`: **`find_best_skill()`** (Dòng 225)

------------------------------

### 📄 File: `logic/auto_scanmap.py`
- **Class `AutoScanMap`** (Dòng 6)
  - `method`: **`__init__(account)`** (Dòng 7)
  - `async_method`: **`start(start_id: int, end_id: int)`** (Dòng 14)
  - `async_method`: **`stop()`** (Dòng 25)
  - `method`: **`_update_config(map_id, map_name, mobs)`** (Dòng 33)
  - `async_method`: **`_scan_loop()`** (Dòng 82)

------------------------------

### 📄 File: `logic/boss_manager.py`
- **Class `BossManager`** (Dòng 4)
  - `method`: **`__new__()`** (Dòng 8)
  - `method`: **`add_boss(name: str, map_name: str, zone_id: int)`** (Dòng 16)
    > *Chi tiết:* Thêm boss mới vào danh sách.
  - `method`: **`mark_boss_dead(boss_name: str)`** (Dòng 56)
    > *Chi tiết:* Đánh dấu boss đã bị tiêu diệt.
  - `method`: **`get_bosses()`** (Dòng 67)
    > *Chi tiết:* Trả về danh sách boss, sắp xếp mới nhất trước.
  - `method`: **`find_bosses_by_keyword(keyword: str)`** (Dòng 71)
    > *Chi tiết:* Tìm tất cả boss có tên chứa keyword (case-insensitive).
Trả về list của boss đang sống, sắp xếp theo thời gian mới nhất.

Ví dụ: keyword="Super Broly" sẽ match "Super Broly 1", "Super Broly 25"
  - `method`: **`clear_expired(minutes: int)`** (Dòng 85)
    > *Chi tiết:* Xóa boss đã xuất hiện quá lâu.

------------------------------

### 📄 File: `logic/map_data.py`
- *(File cấu hình hoặc file rỗng, không chứa hàm)*

------------------------------

### 📄 File: `logic/npc_names.py`
- *(File cấu hình hoặc file rỗng, không chứa hàm)*

------------------------------

### 📄 File: `logic/quest_mapper.py`
- **Class `QuestMapper`** (Dòng 4)
  > *Mô tả:* Helper class giúp map nhiệm vụ sang Boss tương ứng
  - `method`: **`get_boss_from_task(task: Task)`** (Dòng 25)
    > *Chi tiết:* Phân tích nhiệm vụ và trả về tên Boss cần săn.
Trả về None nếu không tìm thấy hoặc nhiệm vụ không yêu cầu boss.

------------------------------

### 📄 File: `logic/target_utils.py`
- `function`: **`focus_nearest_mob(controller, max_distance: float)`** (Dòng 9)
  > *Mô tả:* Focus vào mob gần nhất trong khoảng cách max_distance

Args:
    controller: Controller instance chứa account.char và mobs
    max_distance: Khoảng cách tối đa (pixels)

Returns:
    True nếu tìm thấy và focus thành công, False nếu không
- `function`: **`focus_nearest_char(controller, max_distance: float)`** (Dòng 41)
  > *Mô tả:* Focus vào char/boss gần nhất trong khoảng cách max_distance

Args:
    controller: Controller instance chứa account.char và chars
    max_distance: Khoảng cách tối đa (pixels)

Returns:
    True nếu tìm thấy và focus thành công, False nếu không
- `function`: **`focus_nearest_target(controller, prefer_boss: bool, max_distance: float)`** (Dòng 75)
  > *Mô tả:* Focus vào target gần nhất (mob hoặc char)

Args:
    controller: Controller instance
    prefer_boss: Nếu True, ưu tiên char/boss hơn mob khi khoảng cách tương đương
    max_distance: Khoảng cách tối đa (pixels)

Returns:
    True nếu tìm thấy và focus thành công, False nếu không
- `function`: **`focus_by_name(controller, name: str, target_type: str, max_distance: float)`** (Dòng 141)
  > *Mô tả:* Focus vào target theo tên (fuzzy matching, case-insensitive)

Args:
    controller: Controller instance
    name: Tên hoặc một phần tên cần tìm
    target_type: "mob", "char", hoặc "both"
    max_distance: Khoảng cách tối đa (pixels)

Returns:
    True nếu tìm thấy và focus thành công, False nếu không
- `function`: **`focus_by_id(controller, mob_id: int, char_id: int)`** (Dòng 197)
  > *Mô tả:* Focus vào target theo ID cụ thể

Args:
    controller: Controller instance
    mob_id: ID của mob cần focus (optional)
    char_id: ID của char cần focus (optional)

Returns:
    True nếu tìm thấy và focus thành công, False nếu không
- `function`: **`clear_focus(controller)`** (Dòng 237)
  > *Mô tả:* Xóa tất cả focus hiện tại (mob_focus và char_focus)

Args:
    controller: Controller instance
- `function`: **`get_focused_target(controller)`** (Dòng 250)
  > *Mô tả:* Lấy target hiện tại đang focus

Args:
    controller: Controller instance

Returns:
    ("mob", mob_obj) nếu đang focus mob
    ("char", char_obj) nếu đang focus char
    (None, None) nếu không focus gì

------------------------------

### 📄 File: `logic/xmap.py`
- **Class `NextMap`** (Dòng 9)
  > *Mô tả:* Cấu trúc dữ liệu lưu thông tin để di chuyển sang bản đồ kế tiếp
  - `method`: **`__init__(map_id: int, npc_id: int, select_name: str, select_name2: str, select_name3: str, walk: bool, x: int, y: int, item_id: int, index_npc: int, index_npc2: int, index_npc3: int, capsule_index: int)`** (Dòng 11)
- **Class `XMap`** (Dòng 29)
  - `method`: **`__init__(controller)`** (Dòng 30)
  - `method`: **`init_map_data()`** (Dòng 64)
    > *Chi tiết:* Khởi tạo dữ liệu kết nối giữa các bản đồ
  - `method`: **`add_link_maps(*args)`** (Dòng 229)
    > *Chi tiết:* Tạo chuỗi liên kết 2 chiều giữa các bản đồ: map1 <-> map2 <-> map3...
  - `method`: **`add_npc_link(current, next_map, npc_id, select_name, select_name2, select_name3, walk, x, y, item_id, index_npc, index_npc2, index_npc3, capsule_index)`** (Dòng 245)
    > *Chi tiết:* Thêm một liên kết chuyển map cụ thể thông qua NPC hoặc đi bộ tọa độ
  - `method`: **`add_portal_group(from_map, to_maps, npc_id, indices)`** (Dòng 253)
    > *Chi tiết:* Hỗ trợ thêm nhanh nhóm liên kết từ một trạm tàu đến nhiều hành tinh khác
  - `method`: **`get_map_direction(current_id: int, next_id: int)`** (Dòng 259)
    > *Chi tiết:* Xác định hướng của bản đồ kế tiếp (Trái, Phải, hoặc Giữa) dựa trên map_groups
  - `method`: **`check_has_capsule()`** (Dòng 273)
    > *Chi tiết:* Kiểm tra xem nhân vật có Capsule (ID 194 hoặc 193) không. Trả về (Has, BagIndex).
  - `method`: **`get_capsule_destinations()`** (Dòng 291)
    > *Chi tiết:* Trả về danh sách các điểm đến của Capsule với Index ĐỘNG.
Logic: 
1. Lấy danh sách map chuẩn từ server.
2. Lọc ra các map trùng với map hiện tại.
3. Xác định index dựa trên việc có "Về chỗ cũ" hay không.
  - `async_method`: **`start(map_id: int, keep_dangerous: bool)`** (Dòng 347)
    > *Chi tiết:* Bắt đầu tiến trình XMap đến bản đồ mục tiêu với thuật toán tối ưu (Dijkstra + Capsule)
  - `async_method`: **`go_home()`** (Dòng 404)
    > *Chi tiết:* Tự động xác định map nhà dựa trên hành tinh (gender) và di chuyển về.
  - `async_method`: **`run_loop()`** (Dòng 412)
    > *Chi tiết:* Vòng lặp chính duy trì trạng thái XMap
  - `method`: **`finish()`** (Dòng 418)
    > *Chi tiết:* Kết thúc XMap và hiển thị lộ trình đã đi
  - `method`: **`_has_item(item_id: int)`** (Dòng 447)
    > *Chi tiết:* Kiểm tra nhân vật có vật phẩm cụ thể không.
  - `method`: **`_is_map_accessible(map_id: int, char)`** (Dòng 457)
    > *Chi tiết:* Kiểm tra xem một bản đồ có thể truy cập được không dựa trên các yêu cầu.
  - `method`: **`find_path(start: int, end: int)`** (Dòng 510)
    > *Chi tiết:* Thuật toán tìm đường đi ngắn nhất (Dijkstra) kết hợp đi bộ và Capsule.
- Chi phí đi bộ/npc: 1
- Chi phí dùng capsule: 1.5 (Ưu tiên hơn đi bộ 2 map, nhưng kém hơn đi bộ 1 map)
  - `async_method`: **`update()`** (Dòng 583)
    > *Chi tiết:* Cập nhật trạng thái nhân vật và thực hiện bước di chuyển tiếp theo
  - `method`: **`handle_death()`** (Dòng 711)
  - `async_method`: **`process_next_map(next_map: NextMap)`** (Dòng 722)
    > *Chi tiết:* Quyết định phương thức di chuyển
  - `async_method`: **`handle_capsule_move(next_map: NextMap)`** (Dòng 764)
    > *Chi tiết:* Thực hiện quy trình sử dụng Capsule
  - `async_method`: **`handle_waypoint_move(next_map: NextMap)`** (Dòng 789)
    > *Chi tiết:* Xử lý di chuyển qua các điểm chuyển map (Waypoints)
  - `async_method`: **`handle_npc_move(next_map: NextMap)`** (Dòng 844)
    > *Chi tiết:* Xử lý tương tác với NPC để chuyển map (Sử dụng cả tên text để né Boss)
  - `async_method`: **`handle_walk_move(next_map: NextMap)`** (Dòng 908)

------------------------------

### 📄 File: `logs/logger_config.py`
- **Class `TerminalColors`** (Dòng 4)
  > *Mô tả:* Mã màu ANSI cho Terminal
- **Class `Box`** (Dòng 29)
  > *Mô tả:* ASCII box drawing characters - Compatible with all terminals
- **Class `ColoredFormatter`** (Dòng 90)
  > *Mô tả:* Formatter tùy chỉnh để gán màu cho từng Level log
  - `method`: **`format(record)`** (Dòng 104)
- `function`: **`print_header(title: str, width: int, color: str)`** (Dòng 53)
  > *Mô tả:* In header với box style.
- `function`: **`print_separator(width: int, char: str, color: str)`** (Dòng 69)
  > *Mô tả:* In đường phân cách.
- `function`: **`print_section_header(title: str, width: int, color: str)`** (Dòng 77)
  > *Mô tả:* In section header nhỏ gọn.
- `function`: **`setup_logger(name, level)`** (Dòng 109)
  > *Mô tả:* Hàm khởi tạo logger để sử dụng ở các file khác
- `function`: **`set_logger_status(is_enabled: bool)`** (Dòng 125)
  > *Mô tả:* Bật hoặc tắt logger.

------------------------------

### 📄 File: `logs/setup_test_report.md`
- *(File cấu hình hoặc file rỗng, không chứa hàm)*

------------------------------

### 📄 File: `macros/chia_khu.txt`
- *(File cấu hình hoặc file rỗng, không chứa hàm)*

------------------------------

### 📄 File: `macros/setup_all.txt`
- *(File cấu hình hoặc file rỗng, không chứa hàm)*

------------------------------

### 📄 File: `macros/test.txt`
- *(File cấu hình hoặc file rỗng, không chứa hàm)*

------------------------------

### 📄 File: `main.py`
- `function`: **`load_mob_names()`** (Dòng 33)
- `function`: **`load_item_names()`** (Dòng 59)
- `function`: **`clean_pycache()`** (Dòng 77)
  > *Mô tả:* Tìm và xóa tất cả thư mục __pycache__ trong thư mục hiện tại và thư mục con.
- `function`: **`load_proxies()`** (Dòng 99)
  > *Mô tả:* Đọc danh sách proxy từ file proxy.txt và chuyển đổi sang định dạng URL chuẩn.
- `async_function`: **`command_loop(manager: AccountManager)`** (Dòng 128)
  > *Mô tả:* The main interactive command loop for managing multiple accounts.
- `async_function`: **`main()`** (Dòng 274)

------------------------------

### 📄 File: `mapfile.py`
- **Class `AdvancedRAGSourceAnalyzer`** (Dòng 6)
  - `method`: **`__init__(root_dir, ignore_dirs, ignore_extensions)`** (Dòng 7)
  - `method`: **`_should_ignore(path: Path)`** (Dòng 13)
    > *Chi tiết:* Kiểm tra file hoặc thư mục có thuộc danh sách bỏ qua không.
  - `method`: **`get_function_args(node)`** (Dòng 17)
    > *Chi tiết:* Trích xuất danh sách tham số của hàm kèm theo type hinting (nếu có).
  - `method`: **`parse_python_file(file_path: Path)`** (Dòng 37)
    > *Chi tiết:* Phân tích cú pháp file Python bằng AST để trích xuất Class, Hàm và Tham số.
  - `method`: **`generate_text_tree()`** (Dòng 88)
    > *Chi tiết:* Tạo sơ đồ cây thư mục trực quan trực tiếp theo cấu trúc thư mục.
  - `method`: **`scan_project()`** (Dòng 112)
    > *Chi tiết:* Quét đệ quy toàn bộ thư mục và lưu thông tin chi tiết.
  - `method`: **`generate_markdown_summary(structure_data, tree_str)`** (Dòng 145)
    > *Chi tiết:* Tạo file Markdown chi tiết để nhét vào Context Prompt của Agent.

------------------------------

### 📄 File: `maps_config.json`
- *(File cấu hình hoặc file rỗng, không chứa hàm)*

------------------------------

### 📄 File: `model/__init__.py`
- *(File cấu hình hoặc file rỗng, không chứa hàm)*

------------------------------

### 📄 File: `model/game_objects.py`
- **Class `SkillTemplate`** (Dòng 4)
  - `method`: **`__init__()`** (Dòng 5)
- **Class `Skill`** (Dòng 14)
  - `method`: **`__init__()`** (Dòng 15)
- **Class `MobTemplate`** (Dòng 37)
- **Class `Mob`** (Dòng 47)
  - `method`: **`name()`** (Dòng 71)
- **Class `ItemOption`** (Dòng 78)
- **Class `Item`** (Dòng 82)
  - `method`: **`__init__()`** (Dòng 83)
- **Class `Task`** (Dòng 92)
  - `method`: **`__init__()`** (Dòng 93)
- **Class `Char`** (Dòng 103)
  - `method`: **`__init__()`** (Dòng 104)
  - `method`: **`set_default_part()`** (Dòng 151)
  - `method`: **`is_die()`** (Dòng 156)
    > *Chi tiết:* Convenience property to check if the character is dead (HP == 0).
  - `method`: **`isDie()`** (Dòng 161)
    > *Chi tiết:* Compatibility method matching `isDie` (C# style).
- **Class `Pet`** (Dòng 165)
  - `method`: **`__init__()`** (Dòng 166)

------------------------------

### 📄 File: `model/map_objects.py`
- **Class `Waypoint`** (Dòng 5)
  - `method`: **`center_x()`** (Dòng 15)
  - `method`: **`center_y()`** (Dòng 19)
- **Class `TileMap`** (Dòng 22)
  - `method`: **`__init__()`** (Dòng 46)
  - `method`: **`set_map_info(map_id, planet_id, tile_id, bg_id, type_map, map_name, zone_id)`** (Dòng 61)
  - `method`: **`add_waypoint(wp: Waypoint)`** (Dòng 70)
  - `method`: **`is_tile_type_at(px: int, py: int, t: int)`** (Dòng 73)
    > *Chi tiết:* Check if tile at pixel (px, py) has type t.

------------------------------

### 📄 File: `model/pet.py`
- **Class `ItemOption`** (Dòng 3)
  - `method`: **`__init__(option_template_id: int, param: int)`** (Dòng 4)
  - `method`: **`__str__()`** (Dòng 8)
- **Class `Item`** (Dòng 12)
  - `method`: **`__init__()`** (Dòng 13)
  - `method`: **`__str__()`** (Dòng 20)
- **Class `Skill`** (Dòng 23)
  - `method`: **`__init__()`** (Dòng 24)
  - `method`: **`__str__()`** (Dòng 28)
- **Class `Pet`** (Dòng 33)
  > *Mô tả:* Lớp dữ liệu để lưu trữ tất cả thông tin về đệ tử.
  - `method`: **`__init__()`** (Dòng 37)
  - `method`: **`get_status_vietnamese()`** (Dòng 59)
    > *Chi tiết:* Trả về trạng thái của đệ tử bằng tiếng Việt.
  - `method`: **`__str__()`** (Dòng 73)

------------------------------

### 📄 File: `network/__init__.py`
- *(File cấu hình hoặc file rỗng, không chứa hàm)*

------------------------------

### 📄 File: `network/message.py`
- **Class `Message`** (Dòng 5)
  - `method`: **`__init__(command: int, data: bytes)`** (Dòng 6)
  - `method`: **`writer()`** (Dòng 17)
  - `method`: **`reader()`** (Dòng 20)
  - `method`: **`get_data()`** (Dòng 25)
  - `method`: **`cleanup()`** (Dòng 28)

------------------------------

### 📄 File: `network/reader.py`
- **Class `Reader`** (Dòng 4)
  - `method`: **`__init__(data: bytes)`** (Dòng 5)
  - `method`: **`read_byte()`** (Dòng 9)
  - `method`: **`read_ubyte()`** (Dòng 15)
  - `method`: **`read_short()`** (Dòng 21)
  - `method`: **`read_ushort()`** (Dòng 27)
  - `method`: **`read_int()`** (Dòng 33)
  - `method`: **`read_int3()`** (Dòng 39)
  - `method`: **`read_long()`** (Dòng 46)
  - `method`: **`read_double()`** (Dòng 52)
  - `method`: **`read_bool()`** (Dòng 58)
  - `method`: **`read_utf()`** (Dòng 61)
  - `method`: **`read_bytes(length: int)`** (Dòng 71)
  - `method`: **`available()`** (Dòng 76)
  - `method`: **`read_remaining()`** (Dòng 79)

------------------------------

### 📄 File: `network/service.py`
- **Class `Service`** (Dòng 10)
  - `method`: **`__init__(session: Session, char_data: Char)`** (Dòng 11)
  - `async_method`: **`pet_info()`** (Dòng 15)
    > *Chi tiết:* Yêu cầu thông tin đệ tử (Cmd -107)
  - `async_method`: **`pet_status(status: int)`** (Dòng 24)
    > *Chi tiết:* Thay đổi trạng thái đệ tử (Cmd -108)
0: Đi theo, 1: Bảo vệ, 2: Tấn công, 3: Về nhà, 4: Hợp thể, 5: Hợp thể vĩnh viễn
  - `async_method`: **`char_move()`** (Dòng 36)
  - `async_method`: **`request_task_info()`** (Dòng 68)
    > *Chi tiết:* Gửi yêu cầu cập nhật thông tin nhiệm vụ.
  - `async_method`: **`request_change_map()`** (Dòng 92)
  - `async_method`: **`get_map_offline()`** (Dòng 98)
  - `async_method`: **`send_player_attack(mob_ids: list[int], cdir: int)`** (Dòng 104)
    > *Chi tiết:* Gửi lệnh tấn công quái (Cmd 54 - PLAYER_ATTACK_NPC)
- mob_ids: Danh sách ID của mobs cần tấn công
  - `async_method`: **`attack_player(player_id: int)`** (Dòng 118)
    > *Chi tiết:* Gửi lệnh tấn công người chơi/boss (Cmd -60 - PLAYER_ATTACK_PLAYER)
- player_id: ID của player/boss cần tấn công
  - `async_method`: **`select_skill(skill_template_id: int)`** (Dòng 128)
  - `async_method`: **`request_change_zone(zone_id: int, index_ui: int)`** (Dòng 136)
    > *Chi tiết:* Gửi yêu cầu đổi khu vực (Zone)
Mã lệnh (CMD): 21
  - `async_method`: **`open_zone_ui()`** (Dòng 154)
    > *Chi tiết:* Gửi yêu cầu mở giao diện chọn khu vực (Zone UI)
Mã lệnh (CMD): 29
  - `async_method`: **`request_players()`** (Dòng 166)
    > *Chi tiết:* Yêu cầu danh sách người chơi trong map hiện tại (Cmd 18 - REQUEST_PLAYERS)
Server sẽ trả về danh sách ID, vị trí và HP của tất cả người chơi
  - `async_method`: **`finish_load_map()`** (Dòng 178)
    > *Chi tiết:* Gửi FINISH_LOADMAP packet để báo server client đã sẵn sàng (Cmd -39)
Server sẽ trả về PLAYER_ADD packets cho tất cả người chơi trong map
  - `async_method`: **`use_item(type: int, where: int, index: int, template_id: int)`** (Dòng 192)
    > *Chi tiết:* Sử dụng một vật phẩm. (Cmd -43)
:param type: 0: sử dụng từ túi đồ, 1: đeo vào, ...
:param where: 1: sử dụng cho bản thân, ...
:param index: vị trí trong túi đồ (-1 nếu dùng template_id)
:param template_id: ID mẫu của vật phẩm
  - `async_method`: **`sale_item(action: int, type: int, index: int)`** (Dòng 216)
    > *Chi tiết:* Bán vật phẩm (Cmd 7).
:param action: 1 = bán
:param type: 1 = bán từ hành trang
:param index: vị trí ô đồ cần bán
  - `async_method`: **`get_item(type: int, index: int)`** (Dòng 234)
    > *Chi tiết:* Lấy hoặc sử dụng một vật phẩm trên đối tượng khác (VD: đệ tử). (Cmd -40)
:param type: 6: Dùng vật phẩm trong túi đồ cho đệ tử (BAG_PET)
:param index: Vị trí của vật phẩm trong túi đồ
  - `async_method`: **`open_menu(npc_id: int)`** (Dòng 250)
    > *Chi tiết:* Mở menu NPC (Cmd 27 - OPEN_MENU_ID)
  - `async_method`: **`confirm_menu(npc_id: int, select: int)`** (Dòng 260)
    > *Chi tiết:* Xác nhận chọn menu (Cmd 22 - MENU)
  - `async_method`: **`send_client_input(inputs: list[str])`** (Dòng 272)
    > *Chi tiết:* Gửi dữ liệu nhập từ client (Cmd -125 - CLIENT_INPUT)
  - `async_method`: **`buy_item(shop_type: int, item_id: int)`** (Dòng 285)
    > *Chi tiết:* Mua item từ shop (Cmd 6 - ITEM_BUY)
  - `async_method`: **`open_menu_npc(npc_id: int)`** (Dòng 297)
    > *Chi tiết:* Mở menu NPC (Cmd 33 - OPEN_MENU)
  - `async_method`: **`confirm_menu_npc(npc_id: int, select: int)`** (Dòng 307)
  - `async_method`: **`up_potential(type_potential: int, num: int)`** (Dòng 313)
    > *Chi tiết:* Nâng chỉ số tiềm năng.
type_potential: 0=HP, 1=MP, 2=Sức đánh
num: Số lượng (1, 10, 100)
  - `async_method`: **`request_me_info()`** (Dòng 331)
    > *Chi tiết:* Gửi yêu cầu cập nhật thông tin nhân vật (Cmd -30, sub 0).
  - `async_method`: **`request_map_select(selected: int)`** (Dòng 341)
    > *Chi tiết:* Yêu cầu chọn bản đồ (Cmd -91)
  - `async_method`: **`return_town_from_dead()`** (Dòng 351)
    > *Chi tiết:* Gửi lệnh về nhà khi chết (Cmd ME_BACK = -15).
  - `async_method`: **`client_ok()`** (Dòng 360)
    > *Chi tiết:* Gửi gói tin clientOk để xác nhận với server (Cmd -28, sub 13).
  - `async_method`: **`chat(text: str)`** (Dòng 370)
    > *Chi tiết:* Chat thông thường (Cmd 44 - CHAT_MAP)
  - `async_method`: **`send_chat(text: str)`** (Dòng 381)
  - `async_method`: **`create_character(name: str, gender: int, hair: int)`** (Dòng 384)
    > *Chi tiết:* Tạo nhân vật mới (Cmd -28, sub 2).
:param name: Tên nhân vật
:param gender: Giới tính (0: Trái đất, 1: Namek, 2: Sayda)
:param hair: ID tóc
  - `async_method`: **`send_combine_items(indices: list[int])`** (Dòng 403)
    > *Chi tiết:* Gửi item indices lên giao diện combine/ép sao (Cmd -81 - COMBINNE).
:param indices: Danh sách vị trí item trong bag (byte mỗi index)
Packet format:
  - byte: 0 (ignored by server)
  - byte: count
  - bytes: item bag indices

------------------------------

### 📄 File: `network/session.py`
- **Class `Session`** (Dòng 11)
  - `method`: **`__init__(controller, proxy)`** (Dòng 12)
  - `async_method`: **`connect(host: str, port: int)`** (Dòng 23)
  - `method`: **`disconnect()`** (Dòng 85)
    > *Chi tiết:* Closes the connection.
  - `async_method`: **`send_message(msg: Message)`** (Dòng 96)
  - `async_method`: **`listen()`** (Dòng 134)
  - `async_method`: **`on_message(msg: Message)`** (Dòng 226)
  - `method`: **`process_key_message(msg: Message)`** (Dòng 242)
  - `method`: **`read_key(b: int)`** (Dòng 270)
  - `method`: **`write_key(b: int)`** (Dòng 286)

------------------------------

### 📄 File: `network/writer.py`
- **Class `Writer`** (Dòng 3)
  - `method`: **`__init__()`** (Dòng 4)
  - `method`: **`write_byte(value: int)`** (Dòng 7)
  - `method`: **`write_ubyte(value: int)`** (Dòng 12)
  - `method`: **`write_short(value: int)`** (Dòng 16)
  - `method`: **`write_ushort(value: int)`** (Dòng 19)
  - `method`: **`write_int(value: int)`** (Dòng 22)
  - `method`: **`write_bool(value: bool)`** (Dòng 25)
  - `method`: **`write_utf(value: str)`** (Dòng 28)
  - `method`: **`get_data()`** (Dòng 34)

------------------------------

### 📄 File: `plugins/PLUGIN_COMMANDS.md`
- *(File cấu hình hoặc file rỗng, không chứa hàm)*

------------------------------

### 📄 File: `plugins/QUICKSTART.md`
- *(File cấu hình hoặc file rỗng, không chứa hàm)*

------------------------------

### 📄 File: `plugins/README.md`
- *(File cấu hình hoặc file rỗng, không chứa hàm)*

------------------------------

### 📄 File: `plugins/__init__.py`
- *(File cấu hình hoặc file rỗng, không chứa hàm)*

------------------------------

### 📄 File: `plugins/base_plugin.py`
- **Class `BasePlugin`** (Dòng 11)
  > *Mô tả:* Base class for all plugins

Plugins should inherit from this class and implement the lifecycle hooks.
  - `method`: **`__init__()`** (Dòng 18)
    > *Chi tiết:* Initialize plugin metadata
  - `method`: **`on_load(plugin_api: 'PluginAPI')`** (Dòng 27)
    > *Chi tiết:* Called when plugin is loaded (before enable)

Args:
    plugin_api: API interface for interacting with the system
  - `method`: **`on_enable()`** (Dòng 37)
    > *Chi tiết:* Called when plugin is enabled
Override this to register commands, hooks, etc.
  - `method`: **`on_disable()`** (Dòng 46)
    > *Chi tiết:* Called when plugin is disabled
Override this to cleanup resources
  - `method`: **`on_unload()`** (Dòng 55)
    > *Chi tiết:* Called when plugin is unloaded (after disable)
Override this for final cleanup
  - `method`: **`on_account_login(account)`** (Dòng 66)
    > *Chi tiết:* Called when an account logs in
  - `method`: **`on_account_logout(account)`** (Dòng 70)
    > *Chi tiết:* Called when an account logs out
  - `method`: **`on_message_received(account, message)`** (Dòng 74)
    > *Chi tiết:* Called when a message is received from server
  - `method`: **`on_combat_start(account, target)`** (Dòng 78)
    > *Chi tiết:* Called when combat starts
  - `method`: **`on_mob_killed(account, mob)`** (Dòng 82)
    > *Chi tiết:* Called when a mob is killed
  - `method`: **`on_level_up(account, new_level: int)`** (Dòng 86)
    > *Chi tiết:* Called when character levels up
  - `method`: **`on_item_picked(account, item)`** (Dòng 90)
    > *Chi tiết:* Called when an item is picked up
  - `method`: **`on_command_executed(command: str, args: list)`** (Dòng 94)
    > *Chi tiết:* Called when a command is executed
  - `method`: **`__str__()`** (Dòng 98)
  - `method`: **`__repr__()`** (Dòng 101)

------------------------------

### 📄 File: `plugins/plugin_api.py`
- **Class `PluginAPI`** (Dòng 12)
  > *Mô tả:* API interface provided to plugins for interacting with the system
  - `method`: **`__init__(manager: 'AccountManager', config: 'ConfigLoader', logger: logging.Logger)`** (Dòng 17)
    > *Chi tiết:* Initialize Plugin API

Args:
    manager: Account manager instance
    config: Configuration loader instance
    logger: Logger instance
  - `method`: **`get_accounts()`** (Dòng 34)
    > *Chi tiết:* Get list of all accounts

Returns:
    List of Account objects
  - `method`: **`get_online_accounts()`** (Dòng 43)
    > *Chi tiết:* Get list of online accounts

Returns:
    List of online Account objects
  - `method`: **`get_account_by_username(username: str)`** (Dòng 52)
    > *Chi tiết:* Get account by username

Args:
    username: Account username
    
Returns:
    Account object or None
  - `method`: **`get_config(key: str, default)`** (Dòng 69)
    > *Chi tiết:* Get configuration value

Args:
    key: Configuration key (dot notation)
    default: Default value if not found
    
Returns:
    Configuration value
  - `method`: **`set_config(key: str, value: Any)`** (Dòng 82)
    > *Chi tiết:* Set configuration value

Args:
    key: Configuration key (dot notation)
    value: Value to set
  - `method`: **`log_debug(message: str)`** (Dòng 94)
    > *Chi tiết:* Log debug message
  - `method`: **`log_info(message: str)`** (Dòng 98)
    > *Chi tiết:* Log info message
  - `method`: **`log_warning(message: str)`** (Dòng 102)
    > *Chi tiết:* Log warning message
  - `method`: **`log_error(message: str)`** (Dòng 106)
    > *Chi tiết:* Log error message
  - `method`: **`register_command(name: str, handler: Callable, description: str)`** (Dòng 112)
    > *Chi tiết:* Register a custom command

Args:
    name: Command name
    handler: Function to handle command (receives args list)
    description: Command description
    
Returns:
    True if registered successfully
  - `method`: **`unregister_command(name: str)`** (Dòng 135)
    > *Chi tiết:* Unregister a custom command

Args:
    name: Command name
    
Returns:
    True if unregistered successfully
  - `method`: **`get_custom_commands()`** (Dòng 151)
    > *Chi tiết:* Get all registered custom commands
  - `method`: **`execute_custom_command(name: str, args: list)`** (Dòng 155)
    > *Chi tiết:* Execute a custom command

Args:
    name: Command name
    args: Command arguments
    
Returns:
    Command result
  - `method`: **`subscribe_event(event_name: str, callback: Callable)`** (Dòng 178)
    > *Chi tiết:* Subscribe to an event

Args:
    event_name: Name of event to subscribe to
    callback: Function to call when event occurs
  - `method`: **`unsubscribe_event(event_name: str, callback: Callable)`** (Dòng 192)
    > *Chi tiết:* Unsubscribe from an event

Args:
    event_name: Name of event
    callback: Callback function to remove
  - `method`: **`emit_event(event_name: str, *args, **kwargs)`** (Dòng 207)
    > *Chi tiết:* Emit an event to all subscribers

Args:
    event_name: Name of event
    *args: Event arguments
    **kwargs: Event keyword arguments

------------------------------

### 📄 File: `plugins/plugin_hooks.py`
- **Class `PluginHooks`** (Dòng 10)
  > *Mô tả:* Centralized hook system for triggering plugin events
  - `method`: **`__init__(plugin_manager: 'PluginManager')`** (Dòng 13)
    > *Chi tiết:* Initialize plugin hooks

Args:
    plugin_manager: Plugin manager instance
  - `method`: **`on_account_login(account)`** (Dòng 22)
    > *Chi tiết:* Trigger when account logs in

Args:
    account: Account that logged in
  - `method`: **`on_account_logout(account)`** (Dòng 31)
    > *Chi tiết:* Trigger when account logs out

Args:
    account: Account that logged out
  - `method`: **`on_message_received(account, message)`** (Dòng 40)
    > *Chi tiết:* Trigger when message is received from server

Args:
    account: Account that received message
    message: Message object
  - `method`: **`on_combat_start(account, target)`** (Dòng 50)
    > *Chi tiết:* Trigger when combat starts

Args:
    account: Account starting combat
    target: Combat target (mob or character)
  - `method`: **`on_mob_killed(account, mob)`** (Dòng 60)
    > *Chi tiết:* Trigger when mob is killed

Args:
    account: Account that killed mob
    mob: Mob that was killed
  - `method`: **`on_level_up(account, new_level: int)`** (Dòng 70)
    > *Chi tiết:* Trigger when character levels up

Args:
    account: Account that leveled up
    new_level: New level
  - `method`: **`on_item_picked(account, item)`** (Dòng 80)
    > *Chi tiết:* Trigger when item is picked up

Args:
    account: Account that picked item
    item: Item that was picked
  - `method`: **`on_command_executed(command: str, args: list)`** (Dòng 90)
    > *Chi tiết:* Trigger when command is executed

Args:
    command: Command name
    args: Command arguments

------------------------------

### 📄 File: `plugins/plugin_loader.py`
- **Class `PluginLoader`** (Dòng 14)
  > *Mô tả:* Discovers and loads plugins from the plugins directory
  - `method`: **`__init__(logger: Optional[logging.Logger])`** (Dòng 17)
    > *Chi tiết:* Initialize plugin loader

Args:
    logger: Logger instance
  - `method`: **`discover_plugins(plugin_dir: str)`** (Dòng 26)
    > *Chi tiết:* Discover all plugin files in directory

Args:
    plugin_dir: Directory to search for plugins
    
Returns:
    List of plugin file paths
  - `method`: **`load_plugin(plugin_path: str)`** (Dòng 61)
    > *Chi tiết:* Load a plugin from file path

Args:
    plugin_path: Path to plugin file
    
Returns:
    Plugin instance or None if failed
  - `method`: **`validate_plugin(plugin: BasePlugin)`** (Dòng 115)
    > *Chi tiết:* Validate that plugin meets requirements

Args:
    plugin: Plugin instance to validate
    
Returns:
    True if valid
  - `method`: **`load_all_plugins(plugin_dir: str)`** (Dòng 144)
    > *Chi tiết:* Discover and load all plugins from directory

Args:
    plugin_dir: Directory to load plugins from
    
Returns:
    List of loaded plugin instances

------------------------------

### 📄 File: `plugins/plugin_manager.py`
- **Class `PluginManager`** (Dòng 16)
  > *Mô tả:* Manages plugin lifecycle, registry, and hooks
  - `method`: **`__init__(config: 'ConfigLoader', manager: Optional['AccountManager'], logger: Optional[logging.Logger])`** (Dòng 19)
    > *Chi tiết:* Initialize plugin manager

Args:
    config: Configuration loader instance
    manager: Account manager instance (can be set later)
    logger: Logger instance
  - `method`: **`set_manager(manager: 'AccountManager')`** (Dòng 37)
    > *Chi tiết:* Set account manager (for late initialization)

Args:
    manager: Account manager instance
  - `method`: **`load_all_plugins()`** (Dòng 48)
    > *Chi tiết:* Load all plugins from configured plugin directory
  - `method`: **`register_plugin(plugin: BasePlugin)`** (Dòng 72)
    > *Chi tiết:* Register a plugin

Args:
    plugin: Plugin instance to register
    
Returns:
    True if registered successfully
  - `method`: **`enable_plugin(name: str)`** (Dòng 98)
    > *Chi tiết:* Enable a plugin

Args:
    name: Plugin name
    
Returns:
    True if enabled successfully
  - `method`: **`disable_plugin(name: str)`** (Dòng 126)
    > *Chi tiết:* Disable a plugin

Args:
    name: Plugin name
    
Returns:
    True if disabled successfully
  - `method`: **`unload_plugin(name: str)`** (Dòng 154)
    > *Chi tiết:* Unload a plugin

Args:
    name: Plugin name
    
Returns:
    True if unloaded successfully
  - `method`: **`get_plugin(name: str)`** (Dòng 183)
    > *Chi tiết:* Get plugin by name

Args:
    name: Plugin name
    
Returns:
    Plugin instance or None
  - `method`: **`get_all_plugins()`** (Dòng 195)
    > *Chi tiết:* Get all registered plugins
  - `method`: **`get_enabled_plugins()`** (Dòng 199)
    > *Chi tiết:* Get list of enabled plugins
  - `method`: **`trigger_hook(hook_name: str, *args, **kwargs)`** (Dòng 203)
    > *Chi tiết:* Trigger a hook on all enabled plugins

Args:
    hook_name: Name of hook method to call
    *args: Arguments to pass to hook
    **kwargs: Keyword arguments to pass to hook
  - `method`: **`reload_plugin(name: str)`** (Dòng 220)
    > *Chi tiết:* Reload a plugin (unload and load again)

Args:
    name: Plugin name
    
Returns:
    True if reloaded successfully
  - `method`: **`list_plugins()`** (Dòng 262)
    > *Chi tiết:* Get formatted list of all plugins

Returns:
    Formatted string with plugin information

------------------------------

### 📄 File: `plugins/user_plugins/__init__.py`
- *(File cấu hình hoặc file rỗng, không chứa hàm)*

------------------------------

### 📄 File: `plugins/user_plugins/auto_chat_plugin.py`
- **Class `AutoChatPlugin`** (Dòng 8)
  > *Mô tả:* Plugin tự động chat khi login và hỗ trợ chat combo
  - `method`: **`__init__()`** (Dòng 11)
  - `method`: **`on_enable()`** (Dòng 33)
    > *Chi tiết:* Called when plugin is enabled
  - `method`: **`on_enable()`** (Dòng 53)
    > *Chi tiết:* Called when plugin is enabled
  - `method`: **`on_disable()`** (Dòng 129)
    > *Chi tiết:* Called when plugin is disabled
  - `method`: **`on_account_login(account)`** (Dòng 142)
    > *Chi tiết:* Called when an account logs in - Tự động chat
  - `async_method`: **`_chat_task(account)`** (Dòng 154)
    > *Chi tiết:* Async task to handle chatting with delays

------------------------------

### 📄 File: `project_summary.json`
- *(File cấu hình hoặc file rỗng, không chứa hàm)*

------------------------------

### 📄 File: `project_summary.md`
- *(File cấu hình hoặc file rỗng, không chứa hàm)*

------------------------------

### 📄 File: `proxy.txt`
- *(File cấu hình hoặc file rỗng, không chứa hàm)*

------------------------------

### 📄 File: `requirements-train.txt`
- *(File cấu hình hoặc file rỗng, không chứa hàm)*

------------------------------

### 📄 File: `scripts/analyze_project.py`
- `function`: **`analyze_file(filepath)`** (Dòng 5)
  > *Mô tả:* Phân tích một file Python và trích xuất cấu trúc
- `function`: **`main()`** (Dòng 55)

------------------------------

### 📄 File: `scripts/project_structure.json`
- *(File cấu hình hoặc file rỗng, không chứa hàm)*

------------------------------

### 📄 File: `services/__init__.py`
- *(File cấu hình hoặc file rỗng, không chứa hàm)*

------------------------------

### 📄 File: `services/movement.py`
- **Class `MovementService`** (Dòng 10)
  - `method`: **`__init__(controller)`** (Dòng 11)
  - `async_method`: **`move_to(target_x: int, target_y: int)`** (Dòng 16)
    > *Chi tiết:* Moves the character to target coordinates.
Uses simple linear interpolation for now.
  - `method`: **`stop_moving()`** (Dòng 26)
  - `async_method`: **`_move_loop(tx: int, ty: int)`** (Dòng 31)
  - `async_method`: **`teleport_to(target_x: int, target_y: int)`** (Dòng 68)
    > *Chi tiết:* Teleports the character to target coordinates immediately with 'wiggle' to ensure server sync.
  - `async_method`: **`enter_waypoint(waypoint_name: str, waypoint_index: int)`** (Dòng 90)
    > *Chi tiết:* Move to a waypoint and attempt to enter it.
  - `async_method`: **`teleport_to_npc(npc_id: int, search_by_template: bool)`** (Dòng 137)
    > *Chi tiết:* Finds an NPC by its map ID or template ID and teleports to them.
Returns True if successful, False otherwise.

------------------------------

### 📄 File: `services/pet_service.py`
- `function`: **`request_pet_info(session: Session)`** (Dòng 13)
  > *Mô tả:* Gửi yêu cầu đến server để nhận thông tin đệ tử.
- `function`: **`handle_pet_info_response(msg: Message)`** (Dòng 24)
  > *Mô tả:* Xử lý phản hồi từ server chứa thông tin đệ tử.
Hàm này sẽ được gọi bởi bộ điều khiển message chính khi nhận được message có ID là -107.
- `function`: **`display_pet_info()`** (Dòng 112)
  > *Mô tả:* Hiển thị thông tin đệ tử đã được lưu trữ.

------------------------------

### 📄 File: `setup_state.json`
- *(File cấu hình hoặc file rỗng, không chứa hàm)*

------------------------------

### 📄 File: `targeted_commands/__init__.py`
- *(File cấu hình hoặc file rỗng, không chứa hàm)*

------------------------------

### 📄 File: `targeted_commands/aiagent_command.py`
- **Class `AiagentCommand`** (Dòng 6)
  - `method`: **`__init__()`** (Dòng 7)
  - `async_method`: **`execute(account: Account, *args, **kwargs)`** (Dòng 10)

------------------------------

### 📄 File: `targeted_commands/andau_command.py`
- **Class `AndauCommand`** (Dòng 5)
  - `async_method`: **`execute(account: Account, *args, **kwargs)`** (Dòng 6)

------------------------------

### 📄 File: `targeted_commands/autoattack_command.py`
- **Class `AutoattackCommand`** (Dòng 6)
  - `method`: **`__init__()`** (Dòng 7)
  - `async_method`: **`execute(account: Account, *args, **kwargs)`** (Dòng 10)

------------------------------

### 📄 File: `targeted_commands/autobomong_command.py`
- **Class `AutobomongCommand`** (Dòng 7)
  - `method`: **`__init__()`** (Dòng 8)
  - `async_method`: **`execute(account: Account, *args, **kwargs)`** (Dòng 12)

------------------------------

### 📄 File: `targeted_commands/autoboss_command.py`
- **Class `AutobossCommand`** (Dòng 6)
  - `method`: **`__init__()`** (Dòng 7)
  - `async_method`: **`execute(account: Account, *args, **kwargs)`** (Dòng 10)

------------------------------

### 📄 File: `targeted_commands/autoitem_command.py`
- **Class `AutoitemCommand`** (Dòng 6)
  - `method`: **`__init__()`** (Dòng 7)
  - `async_method`: **`execute(account: Account, *args, **kwargs)`** (Dòng 10)

------------------------------

### 📄 File: `targeted_commands/automsm_command.py`
- **Class `AutomsmCommand`** (Dòng 6)
  - `async_method`: **`execute(account: Account, *args, **kwargs)`** (Dòng 7)

------------------------------

### 📄 File: `targeted_commands/autopet_command.py`
- **Class `AutopetCommand`** (Dòng 6)
  - `method`: **`__init__()`** (Dòng 7)
  - `async_method`: **`execute(account: Account, *args, **kwargs)`** (Dòng 10)

------------------------------

### 📄 File: `targeted_commands/autoplay_command.py`
- **Class `AutoplayCommand`** (Dòng 6)
  - `method`: **`__init__()`** (Dòng 7)
  - `async_method`: **`execute(account: Account, *args, **kwargs)`** (Dòng 10)

------------------------------

### 📄 File: `targeted_commands/autoquest_command.py`
- **Class `AutoQuestCommand`** (Dòng 7)
  > *Mô tả:* Bật/tắt chế độ tự động làm nhiệm vụ.
Cú pháp: autoquest <on|off>
  - `method`: **`__init__()`** (Dòng 12)
  - `async_method`: **`execute(account: Account, *args, **kwargs)`** (Dòng 15)

------------------------------

### 📄 File: `targeted_commands/base_targeted_command.py`
- **Class `TargetedCommand`** (Dòng 5)
  - `async_method`: **`execute(account: Account, *args, **kwargs)`** (Dòng 7)

------------------------------

### 📄 File: `targeted_commands/blacklist_command.py`
- **Class `BlacklistCommand`** (Dòng 6)
  - `async_method`: **`execute(account: Account, *args, **kwargs)`** (Dòng 7)

------------------------------

### 📄 File: `targeted_commands/congcs_command.py`
- **Class `CongcsCommand`** (Dòng 7)
  - `method`: **`__init__()`** (Dòng 8)
  - `async_method`: **`execute(account: Account, *args, **kwargs)`** (Dòng 12)
  - `async_method`: **`_auto_congcs(account: Account, hp: int, mp: int, sd: int)`** (Dòng 42)

------------------------------

### 📄 File: `targeted_commands/findboss_command.py`
- **Class `FindbossCommand`** (Dòng 7)
  > *Mô tả:* Lệnh tìm và liệt kê tất cả boss/chars trong map hiện tại
  - `method`: **`__init__()`** (Dòng 10)
  - `async_method`: **`execute(account: Account, *args, **kwargs)`** (Dòng 13)
    > *Chi tiết:* Liệt kê tất cả characters (bao gồm bosses) trong map hiện tại.
Yêu cầu cập nhật vị trí từ server trước khi hiển thị.

------------------------------

### 📄 File: `targeted_commands/findmob_command.py`
- **Class `FindmobCommand`** (Dòng 7)
  - `method`: **`__init__()`** (Dòng 8)
  - `async_method`: **`execute(account: Account, *args, **kwargs)`** (Dòng 11)

------------------------------

### 📄 File: `targeted_commands/findnpc_command.py`
- **Class `FindnpcCommand`** (Dòng 6)
  - `method`: **`__init__()`** (Dòng 7)
  - `async_method`: **`execute(account: Account, *args, **kwargs)`** (Dòng 10)

------------------------------

### 📄 File: `targeted_commands/gomap_command.py`
- **Class `GomapCommand`** (Dòng 6)
  - `method`: **`__init__()`** (Dòng 7)
  - `async_method`: **`execute(account: Account, *args, **kwargs)`** (Dòng 10)

------------------------------

### 📄 File: `targeted_commands/hit_command.py`
- **Class `HitCommand`** (Dòng 5)
  - `async_method`: **`execute(account: Account, *args, **kwargs)`** (Dòng 6)

------------------------------

### 📄 File: `targeted_commands/khu_command.py`
- **Class `KhuCommand`** (Dòng 6)
  > *Mô tả:* Lệnh quản lý khu vực (zone)
- khu: Hiển thị danh sách khu vực
- khu <id>: Chuyển đến khu vực
  - `method`: **`__init__()`** (Dòng 11)
  - `async_method`: **`execute(account: Account, *args, **kwargs)`** (Dòng 14)

------------------------------

### 📄 File: `targeted_commands/logger_command.py`
- **Class `LoggerCommand`** (Dòng 6)
  - `async_method`: **`execute(account: Account, *args, **kwargs)`** (Dòng 7)

------------------------------

### 📄 File: `targeted_commands/opennpc_command.py`
- **Class `OpenNpcCommand`** (Dòng 5)
  - `async_method`: **`execute(account, *args, **kwargs)`** (Dòng 6)

------------------------------

### 📄 File: `targeted_commands/pet_command.py`
- **Class `PetCommand`** (Dòng 8)
  - `method`: **`__init__()`** (Dòng 9)
  - `async_method`: **`execute(account: Account, *args, **kwargs)`** (Dòng 12)

------------------------------

### 📄 File: `targeted_commands/scanmap_command.py`
- **Class `ScanMapCommand`** (Dòng 7)
  > *Mô tả:* Quét danh sách quái vật trong một khoảng Map ID và tự động lưu vào maps_config.json.
Cú pháp: scanmap <start_id> <end_id> | stop
  - `method`: **`__init__()`** (Dòng 12)
  - `async_method`: **`execute(account: Account, *args, **kwargs)`** (Dòng 15)

------------------------------

### 📄 File: `targeted_commands/show_command.py`
- **Class `ShowCommand`** (Dòng 9)
  - `method`: **`__init__()`** (Dòng 10)
  - `async_method`: **`execute(account: Account, *args, **kwargs)`** (Dòng 13)

------------------------------

### 📄 File: `targeted_commands/tansat_command.py`
- **Class `TansatCommand`** (Dòng 6)
  - `method`: **`__init__()`** (Dòng 7)
  - `async_method`: **`execute(account: Account, *args, **kwargs)`** (Dòng 10)

------------------------------

### 📄 File: `targeted_commands/tapchat_command.py`
- **Class `TapChatCommand`** (Dòng 3)
  - `method`: **`__init__()`** (Dòng 4)
  - `async_method`: **`execute(account, parts, compact_mode, idx)`** (Dòng 7)

------------------------------

### 📄 File: `targeted_commands/targeted_command_loader.py`
- `function`: **`load_targeted_commands()`** (Dòng 5)

------------------------------

### 📄 File: `targeted_commands/teleport_command.py`
- **Class `TeleportCommand`** (Dòng 6)
  - `method`: **`__init__()`** (Dòng 7)
  - `async_method`: **`execute(account: Account, *args, **kwargs)`** (Dòng 10)

------------------------------

### 📄 File: `targeted_commands/teleportnpc_command.py`
- **Class `TeleportnpcCommand`** (Dòng 6)
  - `method`: **`__init__()`** (Dòng 7)
  - `async_method`: **`execute(account: Account, *args, **kwargs)`** (Dòng 10)

------------------------------

### 📄 File: `targeted_commands/useitem_command.py`
- **Class `UseitemCommand`** (Dòng 7)
  - `method`: **`__init__()`** (Dòng 8)
  - `async_method`: **`execute(account: Account, *args, **kwargs)`** (Dòng 11)

------------------------------

### 📄 File: `tests/debug_boss_match.py`
- `function`: **`debug_matching()`** (Dòng 4)

------------------------------

### 📄 File: `tests/live_test_setup.py`
- `async_function`: **`run_test(start_idx, end_idx, force, reset)`** (Dòng 22)

------------------------------

### 📄 File: `tests/test_ai_commands.py`
- **Class `MockAccount`** (Dòng 14)
  - `method`: **`__init__(username)`** (Dòng 15)
- **Class `MockManager`** (Dòng 20)
  - `method`: **`__init__()`** (Dòng 21)
- `async_function`: **`test_ai_commands()`** (Dòng 30)
  > *Mô tả:* Test all AI commands

------------------------------

### 📄 File: `tests/test_ai_pipeline.py`
- **Class `MockChar`** (Dòng 10)
  > *Mô tả:* Mock character for testing
  - `method`: **`__init__()`** (Dòng 12)
- **Class `MockMob`** (Dòng 23)
  > *Mô tả:* Mock mob for testing
  - `method`: **`__init__(mob_id, x, y, hp, max_hp)`** (Dòng 25)
- **Class `MockAccount`** (Dòng 35)
  > *Mô tả:* Mock account for testing
  - `method`: **`__init__()`** (Dòng 37)
- **Class `MockController`** (Dòng 42)
  > *Mô tả:* Mock controller with game state
  - `method`: **`__init__()`** (Dòng 44)
- **Class `MockService`** (Dòng 53)
  > *Mô tả:* Mock network service for testing
  - `async_method`: **`send_attack(mob_id, skill)`** (Dòng 55)
  - `async_method`: **`char_move()`** (Dòng 58)
  - `async_method`: **`select_skill(index)`** (Dòng 61)
- `async_function`: **`test_full_pipeline()`** (Dòng 65)
  > *Mô tả:* Test complete AI pipeline
- `function`: **`_get_action_category(action: int)`** (Dòng 181)
  > *Mô tả:* Get action category name
- `function`: **`_describe_action(action: int)`** (Dòng 194)
  > *Mô tả:* Get action description

------------------------------

### 📄 File: `tests/test_login.py`
- `async_function`: **`run_test()`** (Dòng 5)

------------------------------

### 📄 File: `tests/test_setup_flow.py`
- *(File cấu hình hoặc file rỗng, không chứa hàm)*

------------------------------

### 📄 File: `train/train_pytorch.py`
- **Class `PolicyNetwork`** (Dòng 17)
  > *Mô tả:* PyTorch MLP for policy learning [60 → 64 → 64 → 32] with temporal context
  - `method`: **`__init__(state_dim, action_dim)`** (Dòng 20)
  - `method`: **`forward(x)`** (Dòng 27)
- **Class `ExperienceReplay`** (Dòng 34)
  > *Mô tả:* Experience replay buffer for training
  - `method`: **`__init__(capacity)`** (Dòng 37)
  - `method`: **`add(state, action, reward, next_state, done)`** (Dòng 40)
    > *Chi tiết:* Add experience to buffer
  - `method`: **`sample(batch_size)`** (Dòng 44)
    > *Chi tiết:* Sample random batch from buffer
  - `method`: **`__len__()`** (Dòng 56)
- **Class `AITrainer`** (Dòng 60)
  > *Mô tả:* AI Training Manager
  - `method`: **`__init__(state_dim, action_dim, lr)`** (Dòng 63)
  - `method`: **`collect_experience(state, action, reward, next_state, done)`** (Dòng 87)
    > *Chi tiết:* Add experience to replay buffer
  - `method`: **`train_step(batch_size)`** (Dòng 92)
    > *Chi tiết:* Single training step with mini-batch using Supervised Learning
  - `method`: **`train_episode(num_steps, batch_size)`** (Dòng 129)
    > *Chi tiết:* Train for multiple steps
  - `method`: **`export_weights_to_dict()`** (Dòng 153)
    > *Chi tiết:* Export model weights to dictionary for in-memory sync
  - `method`: **`export_weights(output_path)`** (Dòng 181)
    > *Chi tiết:* Export model weights to JSON format for Pure Python inference
  - `method`: **`load_weights(json_path)`** (Dòng 215)
    > *Chi tiết:* Load weights from JSON
  - `method`: **`get_stats()`** (Dòng 238)
    > *Chi tiết:* Get training statistics
- `function`: **`demo_training()`** (Dòng 250)
  > *Mô tả:* Demo training with random data

------------------------------

### 📄 File: `ui/__init__.py`
- *(File cấu hình hoặc file rỗng, không chứa hàm)*

------------------------------

### 📄 File: `ui/character_display.py`
- `function`: **`display_character_base_info(account)`** (Dòng 7)
  > *Mô tả:* Hiển thị thông tin cơ bản của tài khoản.
- `function`: **`display_character_status(account, compact, idx: int)`** (Dòng 40)
  > *Mô tả:* Hiển thị thông tin trạng thái của một tài khoản.
- `function`: **`display_character_base_stats(account, compact, idx: int)`** (Dòng 143)
  > *Mô tả:* Hiển thị thông tin chỉ số GỐC của nhân vật.

------------------------------

### 📄 File: `ui/formatters.py`
- `function`: **`short_number(num: int)`** (Dòng 4)
  > *Mô tả:* Định dạng số ngắn gọn (VD: 1.2tr, 5.5tỷ).

------------------------------

### 📄 File: `ui/help_display.py`
- `function`: **`display_help()`** (Dòng 6)
  > *Mô tả:* Hiển thị menu trợ giúp với định dạng đẹp.
- `function`: **`display_macro_help()`** (Dòng 108)
  > *Mô tả:* Hiển thị hướng dẫn sử dụng hệ thống Macro mới.

------------------------------

### 📄 File: `ui/item_display.py`
- `function`: **`display_found_items(items, username, template_id)`** (Dòng 6)
  > *Mô tả:* Hiển thị kết quả tìm kiếm item.

------------------------------

### 📄 File: `ui/pet_display.py`
- `function`: **`display_pet_info(pet, username, compact, idx: int)`** (Dòng 9)
  > *Mô tả:* Hiển thị thông tin chi tiết của đệ tử.
- `function`: **`display_pet_help()`** (Dòng 63)
  > *Mô tả:* Hiển thị các lệnh có sẵn cho đệ tử.

------------------------------

### 📄 File: `ui/pet_status.py`
- `function`: **`get_pet_status_vietnamese(status: int)`** (Dòng 6)
  > *Mô tả:* Trả về trạng thái của đệ tử bằng tiếng Việt có màu.
- `function`: **`get_pet_status_short(status: int)`** (Dòng 19)
  > *Mô tả:* Trả về trạng thái ngắn gọn có màu.
- `function`: **`get_pet_status_short_raw(status: int)`** (Dòng 32)
  > *Mô tả:* Trả về trạng thái ngắn gọn không màu (dùng để căn chỉnh).

------------------------------

### 📄 File: `ui/table_headers.py`
- `function`: **`print_compact_header_show()`** (Dòng 6)
  > *Mô tả:* Print header for compact 'show' command.
- `function`: **`print_compact_header_pet()`** (Dòng 25)
  > *Mô tả:* Print header for compact 'pet info' command.
- `function`: **`print_compact_header_csgoc()`** (Dòng 42)
  > *Mô tả:* Print header for compact 'show csgoc' command.
- `function`: **`print_compact_header_task()`** (Dòng 59)
  > *Mô tả:* Print header for compact 'show nhiemvu' command.
- `function`: **`print_compact_header_autoquest()`** (Dòng 74)
  > *Mô tả:* Print header for compact 'autoquest status' command.
- `function`: **`print_compact_footer(width: int, color: str)`** (Dòng 90)
  > *Mô tả:* Print footer line for compact tables.

------------------------------

### 📄 File: `ui/table_utils.py`
- `function`: **`pad_colored(text: str, raw_text: str, width: int, align: str)`** (Dòng 6)
  > *Mô tả:* Pad a colored string based on its raw (uncolored) length.
- `function`: **`print_table_header(columns: list, widths: list, sep: str)`** (Dòng 17)
  > *Mô tả:* Print a formatted table header with box drawing.
- `function`: **`print_compact_divider(width: int)`** (Dòng 28)
  > *Mô tả:* Print a subtle divider line.

------------------------------

### 📄 File: `ui/task_display.py`
- `function`: **`display_task_info(account, compact, idx: int, print_output)`** (Dòng 6)
  > *Mô tả:* Hiển thị thông tin nhiệm vụ.

------------------------------

### 📄 File: `ui/zone_display.py`
- `function`: **`display_zone_list(zones_data: list, map_name: str, account_name: str, current_zone_id: int, map_id: int)`** (Dòng 7)
  > *Mô tả:* Hiển thị danh sách khu vực và số lượng người chơi.
- `function`: **`display_boss_list(bosses: list)`** (Dòng 56)
  > *Mô tả:* Hiển thị danh sách Boss đã xuất hiện.

------------------------------

### 📄 File: `utils/__init__.py`
- *(File cấu hình hoặc file rỗng, không chứa hàm)*

------------------------------

### 📄 File: `utils/autocomplete.py`
- `function`: **`set_plugin_list_callback(callback)`** (Dòng 67)
  > *Mô tả:* Set callback function to provide list of plugin names
- `function`: **`set_macro_list_callback(callback)`** (Dòng 74)
  > *Mô tả:* Set callback function to provide list of macro names
- `function`: **`common_prefix(strings)`** (Dòng 79)
  > *Mô tả:* Tìm tiền tố chung dài nhất.
- `function`: **`get_candidates(buffer_str)`** (Dòng 88)
  > *Mô tả:* Xác định danh sách gợi ý dựa trên bộ đệm hiện tại.
Trả về: (list_candidates, prefix_current_word)
- `function`: **`get_input_with_autocomplete(prompt, commands)`** (Dòng 202)

------------------------------

### 📄 File: `utils/macro_interpreter.py`
- **Class `MacroInterpreter`** (Dòng 6)
  - `method`: **`__init__(name: str, lines: list[str], manager)`** (Dòng 7)
  - `method`: **`is_running()`** (Dòng 17)
  - `method`: **`substitute_variables(text: str)`** (Dòng 20)
    > *Chi tiết:* Replaces ${var} with variable values.
  - `method`: **`evaluate_expression(expr: str)`** (Dòng 46)
    > *Chi tiết:* Evaluates a python-like expression with variables substituted.
  - `method`: **`next_command()`** (Dòng 94)
    > *Chi tiết:* Executes logic until a game command (yieldable) is found or end of script.
  - `method`: **`skip_block(start_keyword, end_keyword)`** (Dòng 170)
    > *Chi tiết:* Skips lines until matching end_keyword, handling nesting.

------------------------------
