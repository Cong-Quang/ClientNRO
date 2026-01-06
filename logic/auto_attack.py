import asyncio
import time
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
            return
        
        # Check cooldown (có thể attack không)
        if not self._can_use_skill(my_char):
            return
        
        # Prepare attack parameters
        mob_ids = []
        char_ids = []
        
        # Add mob target
        if mob_focus:
            # Validate mob còn sống
            mob_data = self.controller.mobs.get(mob_focus.mob_id)
            if mob_data and mob_data.hp > 0 and mob_data.status > 1:
                mob_ids.append(mob_focus.mob_id)
        
        # Add char target (boss/player)
        if char_focus:
            char_id = char_focus.get('id')
            char_hp = char_focus.get('hp', 0)
            
            # Validate char còn sống
            current_char = self.controller.chars.get(char_id)
            if current_char and current_char.get('hp', 0) > 0:
                char_ids.append(char_id)
        
        # Send attack nếu có target
        if mob_ids or char_ids:
            await service.send_player_attack(
                mob_ids=mob_ids if mob_ids else None,
                char_ids=char_ids if char_ids else None
            )
            self.last_attack_time = time.time()
    
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
