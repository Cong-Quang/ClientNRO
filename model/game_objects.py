
from dataclasses import dataclass

class SkillTemplate:
    def __init__(self):
        self.id = 0
        self.name = ""
        self.max_point = 0
        self.mana_use_type = 0
        self.type = 0
        self.icon_id = 0
        self.description = ""

class Skill:
    def __init__(self):
        self.template = SkillTemplate()
        self.skill_id = 0
        self.point = 0
        self.pow_require = 0
        self.mana_use = 0
        self.cool_down = 0
        self.dx = 0
        self.dy = 0
        self.max_fight = 0
        self.damage = 0
        self.price = 0
        self.more_info = ""
        
        # State
        self.last_time_use_this_skill = 0
        self.paint_can_not_use_skill = False

MOB_TEMPLATES = {}

@dataclass
class MobTemplate:
    mob_template_id: int = 0
    type: int = 0
    name: str = ""
    hp: int = 0
    range_move: int = 0
    speed: int = 0
    dart_type: int = 0

@dataclass
class Mob:
    mob_id: int = 0
    template_id: int = 0
    # Ghi chú: Thuộc tính 'name' đã bị xóa vì không có dữ liệu tên mob được gửi trực tiếp từ server
    # trong các gói tin hiện tại mà client xử lý để tạo/cập nhật đối tượng Mob.
    # Để có tên mob, cần phải có cơ chế tải/tra cứu riêng (ví dụ: từ MobTemplate data).
    x: int = 0
    y: int = 0
    x_first: int = 0
    y_first: int = 0
    hp: int = 0
    max_hp: int = 0
    status: int = 0 # 0=Dead, 1=Dying, >1=Alive (5=Respawned)
    is_disable: bool = False
    is_dont_move: bool = False
    is_fire: bool = False
    is_ice: bool = False
    is_wind: bool = False
    sys: int = 0
    level_boss: int = 0
    is_boss: bool = False
    is_mob_me: bool = False # Is this a player's pet mob?

    @property
    def name(self) -> str:
        if self.template_id in MOB_TEMPLATES:
            return MOB_TEMPLATES[self.template_id].name
        return f"Quái {self.template_id}"

        
@dataclass
class ItemOption:
    option_template_id: int = 0
    param: int = 0

class Item:
    def __init__(self):
        self.template = None
        self.item_id = 0
        self.quantity = 0
        self.info = ""
        self.content = ""
        self.item_option = [] # List[ItemOption]
        self.index_ui = 0

class Task:
    def __init__(self):
        self.task_id = 0
        self.index = 0
        self.name = ""
        self.detail = ""
        self.sub_names = []
        self.counts = []
        self.content_info = []
        self.count = 0 

class Char:
    def __init__(self):
        self.char_id = 0
        self.name = ""
        self.c_hp = 0
        self.c_hp_full = 0
        self.c_mp = 0
        self.c_mp_full = 0
        self.c_dam_full = 0
        self.c_def_full = 0
        self.c_critical_full = 0
        self.cx = 0
        self.cy = 0
        self.cdir = 1
        
        # State
        self.statusMe = 0
        
        # Movement state
        self.cxSend = 0
        self.cySend = 0
        
        self.mob_focus: Mob = None
        self.char_focus = None  # Dict chứa thông tin char được target (boss/player)
        self.skills = [] # List[Skill]
        self.myskill: Skill = None # Selected skill

        # Pet related
        self.have_pet = False
        self.is_pet = False
        self.head = 0
        self.body = 0
        self.leg = 0
        self.bag = 0
        self.arr_item_body = [] # List[Item]
        self.arr_item_bag = [] # List[Item]
        self.curr_str_level = ""
        self.c_power = 0
        self.c_tiem_nang = 0
        self.pet_status = 0
        self.c_stamina = 0
        self.c_max_stamina = 0
        self.arr_pet_skill = [] # List[Skill]
        self.map_id = 0
        
        self.task = Task() # Current task info
        
    def set_default_part(self):
        # Placeholder for setDefaultPart logic in C#
        pass

    @property
    def is_die(self) -> bool:
        """Convenience property to check if the character is dead (HP == 0)."""
        return self.c_hp == 0

    # Backward-compatible names for users coming from Java/C# style
    def isDie(self) -> bool:
        """Compatibility method matching `isDie` (C# style)."""
        return self.is_die

class Pet(Char):
    def __init__(self):
        super().__init__()
        self.is_pet = True

