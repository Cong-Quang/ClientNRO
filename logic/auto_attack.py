import asyncio
import time
import math
from logs.logger_config import logger


class AutoAttack:
    """
    Auto Attack service - Tự động tấn công mobs VÀ chars (bosses/players)
    Based on C# AutoAttack implementation
    """
    
    def __init__(self, controller):
        self.controller = controller
        self.is_running = False
        self.task = None
        self.interval = 0.123  # 123ms như C# code
        self.last_attack_time = 0
        self.max_target_distance = 100  # Khoảng cách tối đa để tìm target (px)
        self.auto_retarget = True  # Tự động tìm target mới khi target chết
        self.last_target_type = "both"  # Lưu loại target cuối cùng (mob/char/both)
    
    def start(self):
        """Bật Auto Attack"""
        if not self.is_running:
            self.is_running = True
            self.task = asyncio.create_task(self._attack_loop())
            logger.info("Đã bật Auto Attack (Universal)")
    
    def stop(self):
        """Tắt Auto Attack"""
        if self.is_running:
            self.is_running = False
            if self.task:
                self.task.cancel()
            logger.info("Đã tắt Auto Attack")
    
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
        Update logic - giống C# AutoAttack.Update()
        Check mob_focus và char_focus, attack target nào có
        """
        my_char = self.controller.account.char
        service = self.controller.account.service
        
        mob_focus = my_char.mob_focus
        char_focus = my_char.char_focus
        
        # Kiểm tra có target không (mob hoặc char)
        if mob_focus is None and char_focus is None:
            # Nếu bật auto-retarget, tự động tìm target mới
            if self.auto_retarget:
                self.set_target_nearest(self.last_target_type)
            return
        
        # Check cooldown (có thể attack không)
        if not self._can_use_skill(my_char):
            return
        
        # Prepare attack parameters
        mob_ids = []
        char_ids = []
        need_retarget = False
        
        # Add mob target
        if mob_focus:
            # Validate mob còn sống (> -1 để đánh cho đến khi chết hoàn toàn)
            mob_data = self.controller.mobs.get(mob_focus.mob_id)
            if mob_data and mob_data.hp > -1 and mob_data.status > 1:
                mob_ids.append(mob_focus.mob_id)
            else:
                # Mob chết hoặc không hợp lệ
                my_char.mob_focus = None
                need_retarget = True
        
        # Add char target (boss/player)
        if char_focus:
            char_id = char_focus.get('id')
            
            # Validate char còn sống (> -1 để đánh cho đến khi chết hoàn toàn)
            current_char = self.controller.chars.get(char_id)
            if current_char and current_char.get('hp', 0) > -1:
                char_ids.append(char_id)
            else:
                # Char chết hoặc không hợp lệ
                my_char.char_focus = None
                need_retarget = True
        
        # Send attack nếu có target - Gửi nhiều lần để đảm bảo target chết
        if mob_ids or char_ids:
           # Kiểm tra lại target còn sống không trước mỗi đợt attack
            if mob_ids:
                mob_data = self.controller.mobs.get(mob_ids[0])
                if not (mob_data and mob_data.hp > -1 and mob_data.status > 1):
                    break
            
            if char_ids:
                current_char = self.controller.chars.get(char_ids[0])
                if not (current_char and current_char.get('hp', 0) > -1):
                    break
                
            await service.send_player_attack(
                mob_ids=mob_ids if mob_ids else None,
                char_ids=char_ids if char_ids else None
            )
            
            self.last_attack_time = time.time()
        elif need_retarget and self.auto_retarget:
            # Target chết, tự động tìm target mới
            self.set_target_nearest(self.last_target_type)
    
    def _can_use_skill(self, my_char) -> bool:
        """
        Kiểm tra có thể attack không (cooldown check)
        Tương tự C# CanUseSkill()
        """
        # Check skill cooldown
        if not my_char.skills or len(my_char.skills) == 0:
            return True  # Luôn cho phép đấm
        
        # Get current skill
        current_skill = my_char.skills[0]  # Skill đầu tiên
        if not current_skill:
            return True
        
        current_time = time.time()
        cooldown = current_skill.cool_down / 1000.0  # Convert ms to seconds
        
        # Check nếu đã qua thời gian cooldown
        return (current_time - self.last_attack_time) > cooldown
    
    def set_target_nearest(self, target_type: str = "both") -> bool:
        """
        Tìm và focus vào mob/char gần nhất trong khoảng cách max_target_distance
        Args:
            target_type: "mob", "char", hoặc "both"
        Returns:
            True nếu tìm thấy target, False nếu không
        """
        my_char = self.controller.account.char
        nearest_mob = None
        nearest_char = None
        min_mob_dist = float('inf')
        min_char_dist = float('inf')
        
        # Lưu loại target để dùng cho auto-retarget
        self.last_target_type = target_type
        
        # Tìm mob gần nhất
        if target_type in ["mob", "both"]:
            for mob_id, mob in self.controller.mobs.items():
                if mob.hp > 0 and mob.status > 1:
                    dist = math.sqrt((mob.x - my_char.cx)**2 + (mob.y - my_char.cy)**2)
                    if dist <= self.max_target_distance and dist < min_mob_dist:
                        min_mob_dist = dist
                        nearest_mob = mob
        
        # Tìm char gần nhất
        if target_type in ["char", "both"]:
            for char_id, char_data in self.controller.chars.items():
                if char_data.get('hp', 0) > 0:
                    char_x = char_data.get('x', 0)
                    char_y = char_data.get('y', 0)
                    dist = math.sqrt((char_x - my_char.cx)**2 + (char_y - my_char.cy)**2)
                    if dist <= self.max_target_distance and dist < min_char_dist:
                        min_char_dist = dist
                        nearest_char = char_data
        
        # Set focus vào target gần nhất
        if target_type == "mob" and nearest_mob:
            my_char.mob_focus = nearest_mob
            logger.info(f"AutoAttack: Target Mob {nearest_mob.mob_id} (khoảng cách: {min_mob_dist:.1f}px)")
            return True
        elif target_type == "char" and nearest_char:
            my_char.char_focus = nearest_char
            logger.info(f"AutoAttack: Target Char {nearest_char.get('id')} (khoảng cách: {min_char_dist:.1f}px)")
            return True
        elif target_type == "both":
            # Ưu tiên target gần hơn
            if nearest_mob and (not nearest_char or min_mob_dist <= min_char_dist):
                my_char.mob_focus = nearest_mob
                logger.info(f"AutoAttack: Auto-target Mob {nearest_mob.mob_id} (khoảng cách: {min_mob_dist:.1f}px)")
                return True
            elif nearest_char:
                my_char.char_focus = nearest_char
                logger.info(f"AutoAttack: Auto-target Char {nearest_char.get('id')} (khoảng cách: {min_char_dist:.1f}px)")
                return True
        
        return False
    
    def set_target_mob(self, mob_id: int) -> bool:
        """
        Focus vào mob cụ thể bằng ID
        Args:
            mob_id: ID của mob cần target
        Returns:
            True nếu mob tồn tại, False nếu không
        """
        my_char = self.controller.account.char
        mob = self.controller.mobs.get(mob_id)
        
        if mob and mob.hp > 0 and mob.status > 1:
            my_char.mob_focus = mob
            logger.info(f"AutoAttack: Target Mob {mob_id}")
            return True
        else:
            logger.warning(f"AutoAttack: Mob {mob_id} không tồn tại hoặc đã chết")
            return False
    
    def set_target_char(self, char_id: int) -> bool:
        """
        Focus vào char cụ thể bằng ID (boss/player)
        Args:
            char_id: ID của char cần target
        Returns:
            True nếu char tồn tại, False nếu không
        """
        my_char = self.controller.account.char
        char_data = self.controller.chars.get(char_id)
        
        if char_data and char_data.get('hp', 0) > 0:
            my_char.char_focus = char_data
            logger.info(f"AutoAttack: Target Char {char_id}")
            return True
        else:
            logger.warning(f"AutoAttack: Char {char_id} không tồn tại hoặc đã chết")
            return False
    
    def clear_target(self):
        """Xóa tất cả target hiện tại"""
        my_char = self.controller.account.char
        my_char.mob_focus = None
        my_char.char_focus = None
        logger.info("AutoAttack: Đã xóa target")
    
    def set_target_by_name(self, name: str, target_type: str = "both") -> bool:
        """
        Focus vào mob/char theo tên (hỗ trợ fuzzy matching)
        Args:
            name: Tên hoặc một phần tên cần tìm (case-insensitive)
            target_type: "mob", "char", hoặc "both"
        Returns:
            True nếu tìm thấy, False nếu không
        """
        my_char = self.controller.account.char
        name_lower = name.lower()
        found_targets = []
        
        # Tìm mob theo tên
        if target_type in ["mob", "both"]:
            for mob_id, mob in self.controller.mobs.items():
                if mob.hp > 0 and mob.status > 1:
                    mob_name = mob.name.lower()
                    if name_lower in mob_name:
                        dist = math.sqrt((mob.x - my_char.cx)**2 + (mob.y - my_char.cy)**2)
                        found_targets.append(("mob", mob, dist, mob.name))
        
        # Tìm char theo tên
        if target_type in ["char", "both"]:
            for char_id, char_data in self.controller.chars.items():
                if char_data.get('hp', 0) > 0:
                    char_name = char_data.get('name', '').lower()
                    if name_lower in char_name:
                        char_x = char_data.get('x', 0)
                        char_y = char_data.get('y', 0)
                        dist = math.sqrt((char_x - my_char.cx)**2 + (char_y - my_char.cy)**2)
                        found_targets.append(("char", char_data, dist, char_data.get('name', 'Unknown')))
        
        if not found_targets:
            logger.warning(f"AutoAttack: Không tìm thấy '{name}' trong {target_type}")
            return False
        
        # Nếu có nhiều kết quả, chọn target gần nhất
        found_targets.sort(key=lambda x: x[2])  # Sort by distance
        target_info = found_targets[0]
        target_kind = target_info[0]
        target_obj = target_info[1]
        target_dist = target_info[2]
        target_name = target_info[3]
        
        if target_kind == "mob":
            my_char.mob_focus = target_obj
            logger.info(f"AutoAttack: Target Mob '{target_name}' ID={target_obj.mob_id} (khoảng cách: {target_dist:.1f}px)")
        else:  # char
            my_char.char_focus = target_obj
            logger.info(f"AutoAttack: Target Char '{target_name}' ID={target_obj.get('id')} (khoảng cách: {target_dist:.1f}px)")
        
        # Hiển thị các target khác nếu có
        if len(found_targets) > 1:
            other_targets = [f"{t[3]} ({t[2]:.1f}px)" for t in found_targets[1:4]]  # Show max 3 more
            logger.info(f"AutoAttack: Tìm thấy thêm {len(found_targets)-1} target khác: {', '.join(other_targets)}")
        
        return True
