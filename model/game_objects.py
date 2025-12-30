
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

@dataclass
class Mob:
    mob_id: int = 0
    template_id: int = 0
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

        
class Char:
    _instance = None
    
    def __init__(self):
        self.char_id = 0
        self.name = ""
        self.c_hp = 0
        self.c_hp_full = 0
        self.c_mp = 0
        self.c_mp_full = 0
        self.cx = 0
        self.cy = 0
        self.cdir = 1
        
        # Movement state
        self.cxSend = 0
        self.cySend = 0
        
        self.mob_focus: Mob = None
        self.skills = [] # List[Skill]
        self.myskill: Skill = None # Selected skill
        
    @classmethod
    def my_charz(cls):
        if cls._instance is None:
            cls._instance = Char()
        return cls._instance
