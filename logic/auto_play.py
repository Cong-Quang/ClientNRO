import asyncio
import math
from logs.logger_config import logger 
from model.game_objects import Char, Mob, Skill
from network.service import Service

# logger = logging.getLogger(__name__)

class AutoPlay:
    def __init__(self, controller):
        self.controller = controller
        self.interval = False # Trạng thái hoạt động
        self.task: asyncio.Task = None
        self.target_mobs = set() # Set chứa các template_id của quái cần đánh

    def start(self):
        if not self.interval:
            self.interval = True
            self.task = asyncio.create_task(self.loop())
            logger.info("Bắt đầu Tự động tấn công (Auto Attack).")
            return self.task
        return None

    def stop(self):
        if self.interval:
            self.interval = False
            if self.task:
                self.task.cancel()
            logger.info("Đã dừng Tự động tấn công.")

    async def loop(self):
        logger.info("Vòng lặp Tự động chơi đang chạy...")

        while self.interval:
            try:
                await self.tansat()
                await asyncio.sleep(0.01) # Vòng lặp nhanh để tăng độ phản hồi
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Lỗi trong vòng lặp Tự động chơi: {e}")
                await asyncio.sleep(0.05)

    async def tansat(self):
        my_char = self.controller.account.char
        service = self.controller.account.service
        
        # 0. Kiểm tra nếu nhân vật chết -> Hồi sinh và quay về map cũ
        # statusMe == 14 = Trạng thái chết trong game
        # Kiểm tra cả c_hp == 0 VÀ statusMe == 14 để tránh false positive khi data chưa load
        if my_char.c_hp == 0 and my_char.statusMe == 14:
            current_map_id = self.controller.tile_map.map_id
            logger.info(f"Auto: Nhân vật chết tại map {current_map_id}. Đang hồi sinh...")
            
            # Gọi lệnh về làng khi chết
            await service.return_town_from_dead()
            
            # Chờ hồi sinh xong (chờ tối đa 5 giây)
            for _ in range(50):
                await asyncio.sleep(0.1)
                if my_char.c_hp > 0 or my_char.statusMe != 14:
                    break
            
            # Nếu đã hồi sinh và đang ở map khác, dùng xmap quay về map cũ
            if my_char.c_hp > 0 or my_char.statusMe != 14:
                new_map_id = self.controller.tile_map.map_id
                if new_map_id != current_map_id:
                    logger.info(f"Auto: Đã hồi sinh tại map {new_map_id}. Quay về map {current_map_id}...")
                    await self.controller.xmap.start(current_map_id)
                    
                    # Chờ xmap hoàn thành
                    while self.controller.xmap.is_xmapping:
                        await asyncio.sleep(0.5)
                    
                    logger.info(f"Auto: Đã quay về map {current_map_id}.")
            return  # Kết thúc lượt này, vòng lặp tiếp theo sẽ tiếp tục tấn công
        
        # 1. Xác thực Mục tiêu Hiện tại (Focus)
        mob_focus = my_char.mob_focus
        target_valid = False
        
        if mob_focus:
            current_mob_data = self.controller.mobs.get(mob_focus.mob_id)
            if (current_mob_data and 
                current_mob_data.status > 1 and 
                current_mob_data.hp > 0):
                
                # Kiểm tra lại xem mục tiêu hiện tại có còn nằm trong danh sách target (nếu có lọc)
                if not self.target_mobs or current_mob_data.template_id in self.target_mobs:
                    target_valid = True
                    if current_mob_data != mob_focus:
                        my_char.mob_focus = current_mob_data
                        mob_focus = current_mob_data
                else:
                    target_valid = False
            else:
                my_char.mob_focus = None
                mob_focus = None

        # 2. Tìm mục tiêu mới nếu mục tiêu cũ không hợp lệ
        force_move = False  # Cờ buộc di chuyển khi chọn mục tiêu mới
        if not target_valid:
            best_mob = None
            min_dist = 999999
            
            for mob_id, mob in self.controller.mobs.items():
                if mob.status <= 1 or mob.hp <= 0 or mob.is_mob_me:
                    continue
                
                # Lọc theo danh sách ID nếu có
                if self.target_mobs and mob.template_id not in self.target_mobs:
                    continue

                dist = math.sqrt((mob.x - my_char.cx)**2 + (mob.y - my_char.cy)**2)
                if dist < min_dist:
                    min_dist = dist
                    best_mob = mob
            
            if best_mob:
                my_char.mob_focus = best_mob
                mob_focus = best_mob
                force_move = True  # Buộc di chuyển đến mục tiêu mới
                # logger.info(f"Auto: Tìm thấy mục tiêu {best_mob.mob_id}")
            else:
                return

        # 3. Dịch chuyển và Tấn công (Teleport & Attack)
        if mob_focus:
            # Tính khoảng cách hiện tại
            dist = math.sqrt((mob_focus.x - my_char.cx)**2 + (mob_focus.y - my_char.cy)**2)
            if mob_focus.status <= 1 or mob_focus.hp <= 0:
                return
            # Nếu ở quá xa (ví dụ > 60px), thực hiện dịch chuyển tức thời
            # Kiểm tra khoảng cách X và Y riêng biệt
            dist_x = abs(mob_focus.x - my_char.cx)
            dist_y = abs(mob_focus.y - my_char.cy) # cho quoái bay
            
            # Y luôn phải bằng với Y của mob khi tấn công
            # force_move = True khi chọn mục tiêu mới để đảm bảo di chuyển đến mob ngay lập tức
            if force_move or dist_y > 10 or dist_x > 60:
                # Khi chọn mục tiêu mới, teleport về 100,100 trước để fix bug phát đầu tiên
                if force_move:
                    my_char.cx = 100
                    my_char.cy = 100
                    await service.char_move()
                    await asyncio.sleep(0.01)
                
                logger.info(f"Auto: Dịch chuyển tới Quái {mob_focus.mob_id}")
                my_char.cx = mob_focus.x
                my_char.cy = mob_focus.y  # Y luôn bằng Y của mob
                # Cập nhật hướng quay mặt về phía quái
                my_char.cdir = 1 if mob_focus.x > my_char.cx else -1
                
                # Gửi gói tin di chuyển tới server
                await service.char_move()
                # Nghỉ một chút siêu ngắn để server cập nhật vị trí trước khi tấn công
                await asyncio.sleep(0.01)

            # Thực hiện tấn công
            skill = self.find_best_skill()
            if skill:
                await service.select_skill(skill.template.id) 
                
                # Vòng lặp tấn công
                for i in range(20):
                    if mob_focus.hp > -1: # Kiểm tra quái còn sống không trước khi đánh tiếp
                        await service.send_player_attack([mob_focus.mob_id])
                        # logger.info(f"Auto: Tấn công phát {i+1} vào Mob {mob_focus.mob_id}")
                        
                        # Nghỉ rất ngắn để tránh bị server drop packet (hủy gói tin)
                        await asyncio.sleep(0.02)

    def find_best_skill(self) -> Skill:
        my_char = self.controller.account.char
        if not my_char.skills:
            # Trả về đòn đánh mặc định (đấm) nếu chưa tải kỹ năng
            s = Skill()
            s.template.id = 0
            s.mana_use = 0
            s.cool_down = 50
            return s

        best_skill = None
        
        # Trong C#: GameScr.onScreenSkill (Thường là các phím tắt)
        # Ở đây chúng ta lặp qua tất cả các kỹ năng có sẵn cho đơn giản.
        
        for s in my_char.skills:
            if s is None: continue
            
            # Kiểm tra ID không hợp lệ (theo logic C#)
            # id == 10 || id == 11 || id == 14 || id == 23 || id == 7
            # tid = s.template.id
            # if tid in [10, 11, 14, 23, 7]:
            #     continue
                
            # Kiểm tra loại Mana sử dụng (theo logic C#)
            # type != 0 && type != 1 && type != 2
            mt = s.template.mana_use_type
            if mt not in [0, 1, 2]:
                continue
                
            # Kiểm tra năng lượng (Mana)
            mana_use = s.mana_use
            if mt == 1: # % MP (Năng lượng tối đa)
                mana_use = int(mana_use * my_char.max_mp / 100)
            elif mt == 2:
                mana_use = 1
            
            if my_char.mp >= mana_use:
                # Logic: Chọn kỹ năng có thời gian hồi (cooldown) cao hơn (thường là kỹ năng mạnh hơn)
                if best_skill is None or best_skill.cool_down < s.cool_down:
                    best_skill = s
        
        # Nếu không tìm thấy kỹ năng nào (ví dụ: hết mana), trả về kỹ năng đầu tiên (đấm)
        if best_skill is None:
             for s in my_char.skills:
                 return s
        
        return best_skill