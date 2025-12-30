import asyncio
import math
import logging
from model.game_objects import Char, Mob, Skill
from network.service import Service

logger = logging.getLogger(__name__)

class AutoPlay:
    def __init__(self, controller):
        self.controller = controller
        self.interval = False # Active state
        self.task: asyncio.Task = None

    def start(self):
        if not self.interval:
            self.interval = True
            self.task = asyncio.create_task(self.loop())
            logger.info("Auto Attack Started.")

    def stop(self):
        if self.interval:
            self.interval = False
            if self.task:
                self.task.cancel()
            logger.info("Auto Attack Stopped.")

    async def loop(self):
        logger.info("AutoPlay Loop Running...")

        await Service.gI().request_change_zone(1,-1)

        while self.interval:
            try:
                await self.tansat()
                await asyncio.sleep(0.05) # Faster loop for responsiveness
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in AutoPlay loop: {e}")
                await asyncio.sleep(0.05)

    async def tansat(self):
        my_char = Char.my_charz()
        
        # 1. Validate Current Focus
        mob_focus = my_char.mob_focus
        target_valid = False
        
        if mob_focus:
            current_mob_data = self.controller.mobs.get(mob_focus.mob_id)
            if (current_mob_data and 
                current_mob_data.status > 1 and 
                current_mob_data.hp > 0):
                target_valid = True
                if current_mob_data != mob_focus:
                    my_char.mob_focus = current_mob_data
                    mob_focus = current_mob_data
            else:
                my_char.mob_focus = None
                mob_focus = None

        # 2. Tìm mục tiêu mới nếu mục tiêu cũ không hợp lệ
        if not target_valid:
            best_mob = None
            min_dist = 999999
            
            for mob_id, mob in self.controller.mobs.items():
                if mob.status <= 1 or mob.hp <= 0 or mob.is_mob_me:
                    continue
                
                dist = math.sqrt((mob.x - my_char.cx)**2 + (mob.y - my_char.cy)**2)
                if dist < min_dist:
                    min_dist = dist
                    best_mob = mob
            
            if best_mob:
                my_char.mob_focus = best_mob
                mob_focus = best_mob
                logger.info(f"Auto: Tìm thấy mục tiêu {best_mob.mob_id}")
            else:
                return

        # 3. Dịch chuyển và Tấn công (Teleport & Attack)
        if mob_focus:
            # Tính khoảng cách hiện tại
            dist = math.sqrt((mob_focus.x - my_char.cx)**2 + (mob_focus.y - my_char.cy)**2)
            
            # Nếu ở quá xa (ví dụ > 60px), thực hiện dịch chuyển tức thời
            if dist > 60:
                logger.info(f"Auto: Dịch chuyển tới Quái {mob_focus.mob_id}")
                my_char.cx = mob_focus.x
                my_char.cy = mob_focus.y
                # Cập nhật hướng quay mặt về phía quái
                my_char.cdir = 1 if mob_focus.x > my_char.cx else -1
                
                # Gửi gói tin di chuyển tới server
                await Service.gI().char_move()
                # Nghỉ một chút siêu ngắn để server cập nhật vị trí trước khi đấm
                await asyncio.sleep(0.05)

            # Thực hiện tấn công
            skill = self.find_best_skill()
            if skill:
                await Service.gI().select_skill(skill.template.id) 
                
                # Vòng lặp đấm 2 cái
                for i in range(20):
                    if mob_focus.hp > -1: # Kiểm tra quái còn sống không trước khi đấm phát 2
                        await Service.gI().send_player_attack([mob_focus.mob_id])
                       # logger.info(f"Auto: Tấn công phát {i+1} vào Mob {mob_focus.mob_id}")
                        # Nếu muốn đấm cực nhanh thì không cần sleep, 
                        # hoặc sleep rất ngắn (0.05s) để tránh bị server drop packet.
                        await asyncio.sleep(0.05)

    def find_best_skill(self) -> Skill:
        my_char = Char.my_charz()
        if not my_char.skills:
            # Fallback to default punch if no skills loaded
            s = Skill()
            s.template.id = 0
            s.mana_use = 0
            s.cool_down = 50
            return s

        best_skill = None
        
        # In C#: GameScr.onScreenSkill (Shortcut keys usually)
        # Here we just iterate all available skills for simplicity or define a shortcut list later.
        # For now, iterate all skills.
        
        for s in my_char.skills:
            if s is None: continue
            
            # Invalid ID check (from C#)
            # id == 10 || id == 11 || id == 14 || id == 23 || id == 7
            # tid = s.template.id
            # if tid in [10, 11, 14, 23, 7]:
            #     continue
                
            # Invalid Type check (from C#)
            # type != 0 && type != 1 && type != 2
            mt = s.template.mana_use_type
            if mt not in [0, 1, 2]:
                continue
                
            # Mana Check
            mana_use = s.mana_use
            if mt == 1: # % MP
                mana_use = int(mana_use * my_char.max_mp / 100)
            elif mt == 2:
                mana_use = 1
            
            if my_char.mp >= mana_use:
                # Logic: pick skill with higher cooldown (usually stronger)
                if best_skill is None or best_skill.cool_down < s.cool_down:
                    best_skill = s
        
        # If no skill found (e.g. out of mana), maybe return first skill (punch) or None?
        # C# returns null if none found.
        # But we need something to attack.
        if best_skill is None:
             # Try to find at least a valid punch/basic skill?
             for s in my_char.skills:
                 #if s.template.id == 0:
                     return s
        
        return best_skill