import asyncio
import time
import math
from logs.logger_config import logger
from logic.target_utils import (
    focus_nearest_mob,
    focus_nearest_char,
    focus_nearest_target,
    focus_by_name,
    focus_by_id,
    clear_focus,
    get_focused_target
)


class AutoAttack:
    """
    Auto Attack service - Tự động tấn công mobs VÀ chars (bosses/players)
    Based on C# AutoSendAttack implementation
    """
    
    def __init__(self, controller):
        self.controller = controller
        self.is_running = False
        self.task = None
        self.interval = 0.1  # 100ms interval như C# code
        self.max_target_distance = 100  # Khoảng cách tối đa để tìm target (px)
        self.auto_retarget = True  # Tự động tìm target mới khi target chết
        self.last_target_type = "both"  # Lưu loại target cuối cùng (mob/char/both)
        
        # Priority targeting system
        self.priority_mode = "nearest"  # nearest, boss_first, name_match
        self.priority_names = []  # Danh sách tên ưu tiên (VD: ["Fide", "Android"])
        self.prefer_boss = False  # Ưu tiên boss hơn mob khi khoảng cách tương đương
    
    def start(self):
        """Bật Auto Attack"""
        if not self.is_running:
            self.is_running = True
            self.task = asyncio.create_task(self._attack_loop())
            logger.info("Auto Attack: ON")
    
    def stop(self):
        """Tắt Auto Attack"""
        if self.is_running:
            self.is_running = False
            if self.task:
                self.task.cancel()
            logger.info("Auto Attack: OFF")
    
    def toggle(self):
        """Toggle Auto Attack on/off - giống C# toggleAutoAttack()"""
        if self.is_running:
            self.stop()
        else:
            self.start()
    
    async def _attack_loop(self):
        """Main attack loop - chạy liên tục"""
        while self.is_running:
            try:
                await self._update()
                await asyncio.sleep(self.interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Lỗi trong Auto Attack loop: {e}")
                await asyncio.sleep(0.5)
    
    async def _update(self):
        """
        Update logic - giống C# AutoSendAttack.update()
        Logic:
        1. Tạo vMob và vChar vectors
        2. Nếu có mob_focus -> add vào vMob
        3. Else nếu có char_focus -> add vào vChar
        4. Nếu có target, check cooldown rồi send attack với type = -1 (auto)
        """
        my_char = self.controller.account.char
        service = self.controller.account.service
        
        # Prepare vectors (lists) - giống C# MyVector
        v_mob = []
        v_char = []
        
        # Check mob_focus first, else check char_focus (giống C# logic)
        if my_char.mob_focus is not None:
            v_mob.append(my_char.mob_focus)
        elif my_char.char_focus is not None:
            v_char.append(my_char.char_focus)
        
        # Nếu có target (mob hoặc char)
        if len(v_mob) > 0 or len(v_char) > 0:
            # Get current skill (myskill)
            my_skill = self._get_current_skill(my_char)
            
            # Get current time in milliseconds
            current_time_millis = int(time.time() * 1000)
            
            # Check cooldown: currentTimeMillis - lastTimeUseThisSkill > coolDown
            if my_skill and hasattr(my_skill, 'last_time_use'):
                time_since_last_use = current_time_millis - my_skill.last_time_use
                if time_since_last_use <= my_skill.cool_down:
                    return  # Still on cooldown
            
            # Prepare mob_ids and char_ids for attack
            mob_ids = []
            char_ids = []
            
            # Validate và add mob targets (theo logic auto_play.py)
            for mob in v_mob:
                # Lấy mob data mới nhất từ controller
                mob_data = self.controller.mobs.get(mob.mob_id)
                if mob_data:
                    # Check khoảng cách - nếu quá xa (teleport), clear focus để tìm target mới
                    dist = math.sqrt((mob_data.x - my_char.cx)**2 + (mob_data.y - my_char.cy)**2)
                    if dist > self.max_target_distance:
                        # Target quá xa (đã teleport), clear focus
                        my_char.mob_focus = None
                        logger.info(f"AutoAttack: Mob {mob_data.mob_id} quá xa ({dist:.1f}px), clear focus")
                        continue
                    
                    # Check theo auto_play.py: hp > -1 (không phải hp > 0)
                    # Mob chết có thể có HP = -1, không phải 0
                    if mob_data.hp > -1:
                        mob_ids.append(mob.mob_id)
                    else:
                        # Mob chết, clear focus
                        my_char.mob_focus = None
            
            # Validate và add char targets
            for char in v_char:
                char_id = char.get('id')
                current_char = self.controller.chars.get(char_id)
                if current_char:
                    # Check khoảng cách cho char
                    char_x = current_char.get('x', 0)
                    char_y = current_char.get('y', 0)
                    dist = math.sqrt((char_x - my_char.cx)**2 + (char_y - my_char.cy)**2)
                    if dist > self.max_target_distance:
                        # Char quá xa, clear focus
                        my_char.char_focus = None
                        logger.info(f"AutoAttack: Char {char_id} quá xa ({dist:.1f}px), clear focus")
                        continue
                    
                    # Check HP > -1 tương tự
                    if current_char.get('hp', 0) > -1:
                        char_ids.append(char_id)
                    else:
                        # Char chết, clear focus
                        my_char.char_focus = None
            
            # Send attack nếu có target hợp lệ
            if mob_ids or char_ids:
                await service.send_player_attack(
                    mob_ids=mob_ids if mob_ids else None,
                    char_ids=char_ids if char_ids else None
                )
                
                # Update lastTimeUseThisSkill
                if my_skill:
                    my_skill.last_time_use = current_time_millis
        else:
            # Không có target, tự động focus theo priority mode
            if self.auto_retarget:
                self._auto_focus_by_priority()
    
    def _get_current_skill(self, my_char):
        """
        Lấy skill hiện tại (myskill trong C# code)
        Returns: Skill object hoặc None
        """
        if not my_char.skills or len(my_char.skills) == 0:
            return None
        
        # Get current skill (skill đầu tiên hoặc skill đang chọn)
        current_skill = my_char.skills[0]
        
        # Initialize last_time_use nếu chưa có
        if not hasattr(current_skill, 'last_time_use'):
            current_skill.last_time_use = 0
        
        return current_skill
    
    def _auto_focus_by_priority(self):
        """
        Tự động focus target theo priority mode
        Internal method được gọi bởi _update()
        """
        if self.priority_mode == "boss_first":
            # Ưu tiên boss/char trước
            if not focus_nearest_char(self.controller, self.max_target_distance):
                # Không có char, tìm mob
                focus_nearest_mob(self.controller, self.max_target_distance)
        elif self.priority_mode == "name_match" and self.priority_names:
            # Tìm theo tên ưu tiên
            for name in self.priority_names:
                if focus_by_name(self.controller, name, "both", self.max_target_distance):
                    break
        else:
            # Mode "nearest" - tìm target gần nhất
            focus_nearest_target(self.controller, self.prefer_boss, self.max_target_distance)
    
    def set_priority_mode(self, mode: str, names: list[str] = None, prefer_boss: bool = False):
        """
        Thiết lập chế độ ưu tiên target
        
        Args:
            mode: Chế độ ưu tiên
                - "nearest": Gần nhất (default)
                - "boss_first": Ưu tiên boss/char trước, không có mới tìm mob
                - "name_match": Tìm theo tên trong priority_names
            names: Danh sách tên ưu tiên (dùng cho mode "name_match")
            prefer_boss: Ưu tiên boss khi khoảng cách tương đương (dùng cho mode "nearest")
        """
        self.priority_mode = mode
        if names:
            self.priority_names = names
        self.prefer_boss = prefer_boss
        logger.info(f"AutoAttack: Priority mode = {mode}, names = {names}, prefer_boss = {prefer_boss}")
    
    def set_target_nearest(self, target_type: str = "both") -> bool:
        """
        Tìm và focus vào mob/char gần nhất trong khoảng cách max_target_distance
        Wrapper method sử dụng target_utils
        
        Args:
            target_type: "mob", "char", hoặc "both"
        Returns:
            True nếu tìm thấy target, False nếu không
        """
        self.last_target_type = target_type
        
        if target_type == "mob":
            return focus_nearest_mob(self.controller, self.max_target_distance)
        elif target_type == "char":
            return focus_nearest_char(self.controller, self.max_target_distance)
        else:  # "both"
            return focus_nearest_target(self.controller, self.prefer_boss, self.max_target_distance)
    
    def set_target_mob(self, mob_id: int) -> bool:
        """
        Focus vào mob cụ thể bằng ID
        Wrapper method sử dụng target_utils
        
        Args:
            mob_id: ID của mob cần target
        Returns:
            True nếu mob tồn tại, False nếu không
        """
        return focus_by_id(self.controller, mob_id=mob_id)
    
    def set_target_char(self, char_id: int) -> bool:
        """
        Focus vào char cụ thể bằng ID (boss/player)
        Wrapper method sử dụng target_utils
        
        Args:
            char_id: ID của char cần target
        Returns:
            True nếu char tồn tại, False nếu không
        """
        return focus_by_id(self.controller, char_id=char_id)
    
    def clear_target(self):
        """Xóa tất cả target hiện tại - Wrapper method sử dụng target_utils"""
        clear_focus(self.controller)
        logger.info("AutoAttack: Đã xóa target")
    
    def set_target_by_name(self, name: str, target_type: str = "both") -> bool:
        """
        Focus vào mob/char theo tên (hỗ trợ fuzzy matching)
        Wrapper method sử dụng target_utils
        
        Args:
            name: Tên hoặc một phần tên cần tìm (case-insensitive)
            target_type: "mob", "char", hoặc "both"
        Returns:
            True nếu tìm thấy, False nếu không
        """
        return focus_by_name(self.controller, name, target_type, self.max_target_distance)
