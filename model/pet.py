from typing import List, Optional

class ItemOption:
    def __init__(self, option_template_id: int, param: int):
        self.option_template_id = option_template_id
        self.param = param

    def __str__(self):
        # Sẽ cần một cách để dịch option_template_id thành mô tả cụ thể
        return f"Option ID: {self.option_template_id}, Param: {self.param}"

class Item:
    def __init__(self):
        self.template_id: int = -1
        self.quantity: int = 0
        self.info: str = ""
        self.content: str = ""
        self.options: List[ItemOption] = []

    def __str__(self):
        return f"Template ID: {self.template_id}, Quantity: {self.quantity}"

class Skill:
    def __init__(self):
        self.skill_id: int = -1
        self.more_info: str = ""

    def __str__(self):
        if self.skill_id != -1:
            return f"Skill ID: {self.skill_id}"
        return f"Thông tin khác: {self.more_info}"

class Pet:
    """
    Lớp dữ liệu để lưu trữ tất cả thông tin về đệ tử.
    """
    def __init__(self):
        self.has_pet: bool = False
        self.head_id: int = -1
        self.body_id: int = -1
        self.leg_id: int = -1
        self.items_body: List[Item] = []
        self.hp: int = 0
        self.hp_full: int = 0
        self.mp: int = 0
        self.mp_full: int = 0
        self.damage_full: int = 0
        self.name: str = ""
        self.level_str: str = ""
        self.power: int = 0
        self.potential: int = 0
        self.status: int = -1
        self.stamina: int = 0
        self.max_stamina: int = 0
        self.critical_full: int = 0
        self.defence_full: int = 0
        self.skills: List[Skill] = []

    def get_status_vietnamese(self) -> str:
        """
        Trả về trạng thái của đệ tử bằng tiếng Việt.
        """
        status_map = {
            0: "Đi theo",
            1: "Bảo vệ",
            2: "Tấn công",
            3: "Về nhà",
            4: "Hợp thể",
            5: "Hợp thể vĩnh viễn"
        }
        return status_map.get(self.status, f"Không xác định ({self.status})")

    def __str__(self) -> str:
        if not self.has_pet:
            return "Không có đệ tử."

        info = f"--- Thông Tin Đệ Tử: {self.name} ---"
        info += f"Tên: {self.name}\n"
        info += f"Trạng thái: {self.get_status_vietnamese()} <--- (Đây là trạng thái có thể đang bị bug)\n"
        info += f"HP: {self.hp} / {self.hp_full}\n"
        info += f"MP: {self.mp} / {self.mp_full}\n"
        info += f"Sức mạnh: {self.power:,}\n"
        info += f"Tiềm năng: {self.potential:,}\n"
        info += f"Sát thương: {self.damage_full}\n"
        info += f"Phòng thủ: {self.defence_full}\n"
        info += f"Chí mạng: {self.critical_full}%\n"
        info += f"Thể lực: {self.stamina} / {self.max_stamina}\n"
        
        info += "\n--- Kỹ năng ---"
        if self.skills:
            for skill in self.skills:
                info += f"- {skill}\n"
        else:
            info += "Không có kỹ năng.\n"
            
        info += "\n--- Trang bị ---"
        if self.items_body:
            for item in self.items_body:
                if item:
                    info += f"- {item}\n"
        else:
            info += "Không có trang bị.\n"

        return info

# Để sử dụng, bạn sẽ tạo một instance của Pet và điền dữ liệu vào đó
# my_pet = Pet()
# my_pet.name = "Goku"
# print(my_pet)