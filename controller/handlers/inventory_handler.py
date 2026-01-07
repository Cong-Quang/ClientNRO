"""
Inventory Handler - Xử lý các message liên quan đến túi đồ và pet
"""
import asyncio
from network.message import Message
from logs.logger_config import logger
from .base_handler import BaseHandler


class InventoryHandler(BaseHandler):
    """Handler xử lý bag, pet info, item usage."""
    
    def process_bag_info(self, msg: Message):
        """Cập nhật dữ liệu túi đồ (BAG): xử lý danh sách ô, cập nhật số lượng hoặc thay đổi ô trong túi."""
        try:
            reader = msg.reader()
            action = reader.read_byte()
            logger.info(f"Thông tin túi đồ (Cmd {msg.command}): Hành động={action}")

            if action == 0:
                from model.game_objects import Item, ItemOption
                my_char = self.account.char

                if reader.available() < 1: return
                bag_size = reader.read_ubyte()
                my_char.arr_item_bag = [None] * bag_size
                logger.info(f"Đang xử lý {bag_size} ô trong túi đồ.")

                for i in range(bag_size):
                    if reader.available() < 2: break 
                    template_id = reader.read_short()
                    if template_id == -1:
                        continue

                    item = Item()
                    item.item_id = template_id
                    
                    if reader.available() < 4: break
                    item.quantity = reader.read_int()

                    if reader.available() < 2: break
                    item.info = reader.read_utf()
                    
                    if reader.available() < len(item.info.encode('utf-8')) + 1: break

                    if reader.available() < 2: break
                    item.content = reader.read_utf()
                    
                    if reader.available() < len(item.content.encode('utf-8')) + 1: break
                    
                    item.index_ui = i
                    
                    if reader.available() < 1: break
                    num_options = reader.read_ubyte()
                    if num_options > 0:
                        item.item_option = []
                        for _ in range(num_options):
                            if reader.available() < 3: break
                            option_id = reader.read_ubyte()
                            param = reader.read_ushort()
                            if option_id != 255:
                                item.item_option.append(ItemOption(option_id, param))
                    
                    my_char.arr_item_bag[i] = item
                
                logger.info(f"Đã cập nhật thành công túi đồ với {sum(1 for i in my_char.arr_item_bag if i is not None)} vật phẩm.")

            elif action == 2:
                if reader.available() < 5: return
                index = reader.read_byte()
                quantity = reader.read_int()
                logger.info(f"Cập nhật số lượng vật phẩm tại vị trí {index} thành {quantity}.")
                my_char = self.account.char
                if index < len(my_char.arr_item_bag) and my_char.arr_item_bag[index] is not None:
                    my_char.arr_item_bag[index].quantity = quantity
                    if quantity == 0:
                        my_char.arr_item_bag[index] = None
                else:
                    logger.warning(f"Nhận được cập nhật số lượng cho vật phẩm không hợp lệ tại vị trí {index}.")

        except Exception as e:
            logger.error(f"Lỗi khi phân tích BAG_INFO (Cmd -36): {e}")
            import traceback
            traceback.print_exc()

    def process_pet_info(self, msg: Message):
        """Đọc thông tin đệ tử (PET_INFO) và cập nhật đối tượng pet trong account."""
        try:
            reader = msg.reader()
            from model.game_objects import Item, ItemOption, Skill
            
            b_pet = reader.read_byte()
            if b_pet == 0:
                self.account.char.have_pet = False
                self.account.pet.have_pet = False
                logger.info("Nhân vật không có đệ tử.")
            if b_pet == 1:
                self.account.char.have_pet = True
                self.account.pet.have_pet = True
                logger.info("Nhân vật có đệ tử.")
            
            if b_pet != 2:
                return

            pet = self.account.pet
            pet.have_pet = True
            pet.head = reader.read_short()
            pet.set_default_part()
            
            num_body = reader.read_ubyte()
            pet.arr_item_body = [None] * num_body
            for i in range(num_body):
                template_id = reader.read_short()
                if template_id == -1:
                    continue
                
                item = Item()
                item.item_id = template_id
                item.quantity = reader.read_int()
                item.info = reader.read_utf()
                item.content = reader.read_utf()
                
                num_options = reader.read_ubyte()
                if num_options != 0:
                    item.item_option = []
                    for _ in range(num_options):
                        opt_id = reader.read_ubyte()
                        opt_param = reader.read_ushort()
                        if opt_id != 255:
                             item.item_option.append(ItemOption(opt_id, opt_param))
                
                pet.arr_item_body[i] = item
            
            pet.c_hp = reader.read_int()
            pet.c_hp_full = reader.read_int()
            pet.c_mp = reader.read_int()
            pet.c_mp_full = reader.read_int()
            pet.c_dam_full = reader.read_int()
            pet.name = reader.read_utf()
            pet.curr_str_level = reader.read_utf()
            pet.c_power = reader.read_long()
            pet.c_tiem_nang = reader.read_long()
            pet.pet_status = reader.read_byte()
            pet.c_stamina = reader.read_short()
            pet.c_max_stamina = reader.read_short()
            pet.c_critical_full = reader.read_byte()
            pet.c_def_full = reader.read_short()
            
            num_skills = reader.read_byte()
            pet.arr_pet_skill = [None] * num_skills
            for i in range(num_skills):
                skill_id = reader.read_short()
                if skill_id != -1:
                    s = Skill()
                    s.skill_id = skill_id
                    pet.arr_pet_skill[i] = s
                else:
                    s = Skill()
                    s.more_info = reader.read_utf()
                    pet.arr_pet_skill[i] = s
            
            logger.info(f"Đã cập nhật thông tin Đệ tử: {pet.name} | HP: {pet.c_hp}/{pet.c_hp_full} | Sức mạnh: {pet.c_power}")

        except Exception as e:
            logger.error(f"Lỗi khi phân tích PET_INFO: {e}")
            import traceback
            traceback.print_exc()

    async def eat_pea(self):
        """Tìm và ăn đậu trong hành trang khi HP/MP thấp."""
        PEAN_IDS = [595]
        char = self.account.char
        needs_eat = False
        reasons = []

        if char.c_hp_full > 0 and (char.c_hp / char.c_hp_full) < 0.8:
            needs_eat = True
            reasons.append(f"HP thấp ({int(char.c_hp/char.c_hp_full*100)}%)")
            
        if char.c_mp_full > 0 and (char.c_mp / char.c_mp_full) < 0.8:
            needs_eat = True
            reasons.append(f"MP thấp ({int(char.c_mp/char.c_mp_full*100)}%)")
        
        if not needs_eat:
            logger.info(f"[{self.account.username}] Không cần ăn đậu (HP/MP > 80%, Thể lực > 20%).")
            return

        logger.info(f"[{self.account.username}] Quyết định ăn đậu. Lý do: {', '.join(reasons)}")

        found_index = -1
        
        if char.arr_item_bag:
            for i, item in enumerate(char.arr_item_bag):
                if item and item.item_id in PEAN_IDS:
                    found_index = i
                    break
        
        if found_index != -1:
            logger.info(f"[{self.account.username}] Sử dụng đậu thần tại vị trí {found_index}...")
            await self.account.service.use_item(0, 1, found_index, -1)
        else:
            logger.warning(f"[{self.account.username}] Cần ăn đậu nhưng không tìm thấy trong hành trang.")

    def find_item_in_bag(self, item_id: int):
        """Tìm item trong hành trang và trả về danh sách kết quả."""
        results = []
        char = self.account.char
        if not char.arr_item_bag:
            return results
            
        for i, item in enumerate(char.arr_item_bag):
            if item and item.item_id == item_id:
                results.append(item)
        return results

    async def use_item_by_id(self, item_id: int, action_type: int):
        """
        Tìm và thực hiện hành động với item theo ID (sử dụng hoặc bán).
        :param item_id: ID template của item.
        :param action_type: 0 = Sử dụng, 1 = Bán.
        """
        char = self.account.char
        if not char.arr_item_bag:
            logger.warning(f"[{self.account.username}] Hành trang chưa tải hoặc rỗng.")
            return

        found = False
        count_action = 0
        for i, item in enumerate(char.arr_item_bag):
            if item and item.item_id == item_id:
                found = True
                try:
                    if action_type == 0:
                        await self.account.service.use_item(0, 1, i, -1)
                        count_action += 1
                        await asyncio.sleep(0.1)
                    elif action_type == 1:
                        await self.account.service.sale_item(1, 1, i)
                        count_action += 1
                        await asyncio.sleep(0.1)
                except Exception as e:
                    logger.error(f"[{self.account.username}] Lỗi khi xử lý item {item_id} tại index {i}: {e}")
        
        if not found:
            logger.warning(f"[{self.account.username}] Không tìm thấy item ID {item_id} trong hành trang.")
        else:
            action_str = "Sử dụng" if action_type == 0 else "Bán"
            logger.info(f"[{self.account.username}] Đã gửi yêu cầu {action_str} {count_action} item ID {item_id}.")
