"""
Controller - Quản lý xử lý tin nhắn và trạng thái game cho một tài khoản.

Đã được tái cấu trúc để tách message handlers thành các module riêng biệt.
"""
from logs.logger_config import logger
from network.message import Message
from constants.cmd import Cmd
from model.map_objects import TileMap
from services.movement import MovementService
from logic.auto_play import AutoPlay
from logic.auto_pet import AutoPet
from logic.xmap import XMap
from logic.auto_NVBoMong import AutoQuest
from logic.auto_giftcode import AutoGiftcode
from logic.auto_boss import AutoBoss

# Import handlers
from .handlers import (
    LoginHandler,
    CharacterHandler,
    MapHandler,
    CombatHandler,
    PlayerHandler,
    TaskHandler,
    InventoryHandler,
    NPCHandler,
    NotificationHandler,
    MiscHandler,
)


class Controller:
    """Quản lý xử lý tin nhắn và trạng thái game cho một tài khoản.

    Thuộc tính chính:
      - account: đối tượng tài khoản đang điều khiển
      - tile_map, mobs, npcs: trạng thái bản đồ và thực thể
      - movement, auto_play, auto_pet, xmap: các dịch vụ liên quan
    """
    def __init__(self, account):
        """Khởi tạo Controller cho `account`: thiết lập trạng thái và các dịch vụ liên quan."""
        self.account = account
        self.char_info = {}
        self.map_info = {}
        self.mobs = {}
        self.npcs = {}
        self.chars = {}  # Danh sách characters khác trong map (bao gồm bosses)
        self.tile_map = TileMap()
        self.zone_list = []  # Lưu danh sách zone cho auto_boss
        self.movement = MovementService(self)
        self.auto_play = AutoPlay(self)
        self.auto_attack = None  # Will be imported lazily to avoid circular import
        self.auto_pet = AutoPet(self)
        self.xmap = XMap(self)
        self.auto_quest = AutoQuest(self)
        self.auto_giftcode = AutoGiftcode(self)
        self.auto_boss = AutoBoss(self)
        self.ai_agent = None  # AI Agent (will be initialized lazily)
        
        # Initialize handlers
        self.login_handler = LoginHandler(self)
        self.character_handler = CharacterHandler(self)
        self.map_handler = MapHandler(self)
        self.combat_handler = CombatHandler(self)
        self.player_handler = PlayerHandler(self)
        self.task_handler = TaskHandler(self)
        self.inventory_handler = InventoryHandler(self)
        self.npc_handler = NPCHandler(self)
        self.notification_handler = NotificationHandler(self)
        self.misc_handler = MiscHandler(self)

    def toggle_auto_quest(self, enabled: bool):
        """Bật hoặc tắt chế độ Auto Quest."""
        if enabled:
            self.auto_quest.start()
        else:
            self.auto_quest.stop()

    def toggle_autoplay(self, enabled: bool):
        """Bật hoặc tắt chế độ AutoPlay; khi bật, thêm task AutoPlay vào `account.tasks` nếu có."""
        if enabled:
            task = self.auto_play.start()
            if task:
                self.account.tasks.append(task)
        else:
            self.auto_play.stop()

    def toggle_auto_pet(self, enabled: bool):
        """Bật hoặc tắt chế độ AutoPet; khi bật, thêm task AutoPet vào `account.tasks` nếu có."""
        if enabled:
            task = self.auto_pet.start()
            if task:
                self.account.tasks.append(task)
        else:
            self.auto_pet.stop()
    
    def toggle_auto_attack(self, enabled: bool):
        """Bật hoặc tắt Auto Attack (Universal - cho cả mobs và chars)"""
        # Lazy import to avoid circular dependency
        if self.auto_attack is None:
            from logic.auto_attack import AutoAttack
            self.auto_attack = AutoAttack(self)
        
        if enabled:
            self.auto_attack.start()
        else:
            self.auto_attack.stop()
    
    def toggle_auto_boss(self, enabled: bool, boss_name: str = ""):
        """Bật hoặc tắt chế độ Auto Boss."""
        if enabled:
            if boss_name:
                self.auto_boss.start(boss_name)
            else:
                logger.warning("Cần chỉ định tên boss để bắt đầu Auto Boss")
        else:
            self.auto_boss.stop()
    
    def toggle_ai_agent(self, enabled: bool):
        """Bật hoặc tắt AI Agent (Neural Network control)"""
        # Lazy import to avoid circular dependency
        if self.ai_agent is None:
            from ai_agent import AIAgent
            from config import Config
            self.ai_agent = AIAgent(
                controller=self,
                service=self.account.service,
                account_id=self.account.username
            )
            # Load weights on first initialization
            self.ai_agent.load_weights(Config.AI_WEIGHTS_PATH)
        
        if enabled:
            task = self.ai_agent.start()
            if task:
                self.account.tasks.append(task)
                logger.info(f"[AI] AI Agent enabled for {self.account.username}")
        else:
            self.ai_agent.stop()
            logger.info(f"[AI] AI Agent disabled for {self.account.username}")

    def on_message(self, msg: Message):
        """Chuyển tiếp tin nhắn theo `msg.command` đến handler tương ứng."""
        try:
            cmd = msg.command
            
            # Login & Map Setup
            if cmd == Cmd.NOT_LOGIN:
                self.login_handler.message_not_login(msg)
            elif cmd == Cmd.NOT_MAP:
                self.login_handler.message_not_map(msg)
            elif cmd == Cmd.MAP_INFO:
                self.map_handler.process_map_info(msg)
            elif cmd == Cmd.OPEN_UI_ZONE:
                self.map_handler.process_zone_list(msg)
            elif cmd == Cmd.MAP_OFFLINE:
                self.map_handler.process_map_offline(msg)
            elif cmd == Cmd.UPDATE_DATA:
                self.map_handler.process_update_data(msg)
            elif cmd == Cmd.UPDATE_MAP:
                self.map_handler.process_update_map(msg)
            elif cmd == Cmd.MAP_CLEAR:
                logger.info(f"Received MAP_CLEAR (Cmd {cmd}).")
                
            # Character Info
            elif cmd == Cmd.SUB_COMMAND:
                self.character_handler.process_sub_command(msg)
            elif cmd == Cmd.ME_LOAD_POINT:
                self.character_handler.process_me_load_point(msg)
            elif cmd == Cmd.POWER_INFO:
                self.character_handler.process_power_info(msg)
            elif cmd == Cmd.PLAYER_UP_EXP:
                self.character_handler.process_player_up_exp(msg)
                
            # Combat
            elif cmd == Cmd.MOB_HP:
                self.combat_handler.process_mob_hp(msg)
            elif cmd == Cmd.NPC_DIE:
                self.combat_handler.process_npc_die(msg)
            elif cmd == Cmd.NPC_LIVE:
                self.combat_handler.process_npc_live(msg)
            elif cmd == Cmd.PLAYER_ATTACK_NPC:
                self.combat_handler.process_player_attack_npc(msg)
                
            # Players
            elif cmd == Cmd.PLAYER_ADD:
                self.player_handler.process_player_add(msg)
            elif cmd == Cmd.PLAYER_MOVE:
                self.player_handler.process_player_move(msg)
            elif cmd == Cmd.PLAYER_DIE:
                self.player_handler.process_player_die(msg)
            elif cmd == 18:  # REQUEST_PLAYERS response
                self.player_handler.process_player_list_update(msg)
                
            # Tasks
            elif cmd == Cmd.TASK_GET:
                self.task_handler.process_task_get(msg)
            elif cmd == Cmd.TASK_UPDATE:
                self.task_handler.process_task_update(msg)
            elif cmd == Cmd.TASK_NEXT:
                self.task_handler.process_task_next(msg)
                
            # Inventory
            elif cmd == Cmd.BAG:
                self.inventory_handler.process_bag_info(msg)
            elif cmd == Cmd.PET_INFO:
                self.inventory_handler.process_pet_info(msg)
                
            # NPCs
            elif cmd == Cmd.NPC_CHAT:
                self.npc_handler.process_npc_chat(msg)
            elif cmd == Cmd.NPC_ADD_REMOVE:
                self.npc_handler.process_npc_add_remove(msg)
            elif cmd == Cmd.OPEN_UI_CONFIRM:
                self.npc_handler.process_open_ui_confirm(msg)
                
            # Notifications & Boss
            elif cmd == Cmd.SERVER_MESSAGE:
                self.notification_handler.process_server_message(msg)
            elif cmd == Cmd.CHAT_THEGIOI_SERVER:
                self.notification_handler.process_chat_server(msg)
            elif cmd == Cmd.CHAT_MAP:
                self.notification_handler.process_chat_map(msg)
            elif cmd == Cmd.SERVER_ALERT:
                self.notification_handler.process_server_alert(msg)
            elif cmd == Cmd.BIG_MESSAGE:
                self.notification_handler.process_big_message(msg)
            elif cmd == Cmd.CHAT_VIP:
                self.notification_handler.process_chat_vip(msg)
            elif cmd == Cmd.BIG_BOSS:
                self.notification_handler.process_big_boss(msg, 1)
            elif cmd == Cmd.BIG_BOSS_2:
                self.notification_handler.process_big_boss(msg, 2)
                
            # Misc
            elif cmd == Cmd.GAME_INFO:
                self.misc_handler.process_game_info(msg)
            elif cmd == Cmd.SPEACIAL_SKILL:
                self.misc_handler.process_special_skill(msg)
            elif cmd == Cmd.MESSAGE_TIME:
                self.misc_handler.process_message_time(msg)
            elif cmd == Cmd.CHANGE_FLAG:
                self.misc_handler.process_change_flag(msg)
            elif cmd == Cmd.MAXSTAMINA:
                self.misc_handler.process_max_stamina(msg)
            elif cmd == Cmd.STAMINA:
                self.misc_handler.process_stamina(msg)
            elif cmd == Cmd.UPDATE_ACTIVEPOINT:
                self.misc_handler.process_update_active_point(msg)
            elif cmd == Cmd.THACHDAU:
                self.misc_handler.process_thach_dau(msg)
            elif cmd == Cmd.AUTOPLAY:
                self.misc_handler.process_autoplay(msg)
            elif cmd == Cmd.MABU:
                self.misc_handler.process_mabu(msg)
            elif cmd == Cmd.THELUC:
                self.misc_handler.process_the_luc(msg)
            elif cmd == Cmd.CREATE_PLAYER:
                self.misc_handler.process_create_player(msg)
                
            # Ignored/Logged only
            elif cmd == Cmd.GET_SESSION_ID:
                pass
            elif cmd == Cmd.ANDROID_PACK:
                logger.info(f"Received ANDROID_PACK (Cmd {cmd}).")
            elif cmd == Cmd.ITEM_BACKGROUND:
                logger.info(f"Received ITEM_BACKGROUND (Cmd {cmd}), len={len(msg.get_data())}")
            elif cmd == Cmd.BGITEM_VERSION:
                logger.info(f"Received BGITEM_VERSION (Cmd {cmd}), len={len(msg.get_data())}")
            elif cmd == Cmd.TILE_SET:
                logger.info(f"Received TILE_SET (Cmd {cmd}), len={len(msg.get_data())}")
            elif cmd == Cmd.MOB_ME_UPDATE:
                logger.info(f"Received MOB_ME_UPDATE (Cmd {cmd}).")
            elif cmd == Cmd.UPDATE_COOLDOWN:
                logger.info(f"Received UPDATE_COOLDOWN (Cmd {cmd}).")
            elif cmd == Cmd.ME_BACK:
                logger.info(f"Received ME_BACK (Cmd {cmd}).")
            else:
                logger.info(f"Unhandled command: {cmd}, len={len(msg.get_data())}, hex={msg.get_data().hex()}")
                
        except Exception as e:
            logger.error(f"Error handling message {msg.command}: {e}")
            import traceback
            traceback.print_exc()

    # Helper methods delegated to handlers
    async def eat_pea(self):
        """Tìm và ăn đậu trong hành trang khi HP/MP thấp."""
        return await self.inventory_handler.eat_pea()

    def find_item_in_bag(self, item_id: int):
        """Tìm item trong hành trang và trả về danh sách kết quả."""
        return self.inventory_handler.find_item_in_bag(item_id)

    async def use_item_by_id(self, item_id: int, action_type: int):
        """Tìm và thực hiện hành động với item theo ID."""
        return await self.inventory_handler.use_item_by_id(item_id, action_type)

    async def attack_nearest_mob(self):
        """Tấn công quái vật gần nhất một lần."""
        return await self.misc_handler.attack_nearest_mob()

    async def auto_upgrade_stats(self, target_hp: int, target_mp: int, target_sd: int):
        """Tự động cộng chỉ số tiềm năng cho đến khi đạt mục tiêu."""
        return await self.misc_handler.auto_upgrade_stats(target_hp, target_mp, target_sd)
