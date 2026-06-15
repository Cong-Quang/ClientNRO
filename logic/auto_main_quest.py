"""
Auto Main Quest - Tự động làm nhiệm vụ chính
=============================================
Dựa trên phân tích server code (TaskService.java, ConstTask.java, ConstNpc.java, ConstMob.java)
và SQL database.

Chiến lược:
- State Machine pattern (giống auto_NVBoMong.py)
- Phân tích task.sub_names để xác định bước cần làm
- Gender-based transform cho NPC và map
- Tận dụng tối đa: xmap, auto_play, auto_attack, movement, service
"""

import asyncio
import json
import math
import time
import re
import unicodedata
from enum import Enum
from logs.logger_config import logger

# =============================================================================
# CONSTANTS from server code analysis
# =============================================================================

# Gender constants (từ ConstPlayer.java)
TRAI_DAT = 0
NAMEC = 1
XAYDA = 2

# =============================================================================
# NPC TEMPLATE IDs (từ ConstNpc.java)
# =============================================================================
NPC = {
    "ONG_GOHAN": 0,
    "ONG_PARAGUS": 1,
    "ONG_MOORI": 2,
    "BUNMA": 7,
    "DENDE": 8,
    "APPULE": 9,
    "DR_DRIEF": 10,
    "CARGO": 11,
    "CUI": 12,
    "QUY_LAO_KAME": 13,
    "TRUONG_LAO_GURU": 14,
    "VUA_VEGETA": 15,
    "BO_MONG": 17,
    "THAN_MEO_KARIN": 18,
    "THUONG_DE": 19,
    "THAN_VU_TRU": 20,
    "QUOC_VUONG": 42,
    "TO_SU_KAIO": 43,
    "OSIN": 44,
    "BUNMA_TL": 37,
    "CALICK": 38,
    "MR_POPO": 67,
}

# Gender-based NPC transform (từ TaskService.transformNpcId)
# key: server_const, values: (trai_dat_id, namec_id, xayda_id)
GENDER_NPC_MAP = {
    "NPC_NHA": (NPC["ONG_GOHAN"], NPC["ONG_MOORI"], NPC["ONG_PARAGUS"]),
    "NPC_TTVT": (NPC["DR_DRIEF"], NPC["CARGO"], NPC["CUI"]),
    "NPC_SHOP_LANG": (NPC["BUNMA"], NPC["DENDE"], NPC["APPULE"]),
    "NPC_QUY_LAO": (NPC["QUY_LAO_KAME"], NPC["TRUONG_LAO_GURU"], NPC["VUA_VEGETA"]),
}

# Gender-based MAP transform (từ TaskService.transformMapId)
GENDER_MAP_MAP = {
    "MAP_NHA": (21, 22, 23),
    "MAP_200": (1, 8, 15),
    "MAP_VACH_NUI": (39, 40, 41),
    "MAP_TTVT": (24, 25, 26),
    "MAP_QUAI_BAY_600": (3, 11, 17),
    "MAP_LANG": (0, 7, 14),
    "MAP_QUY_LAO": (5, 13, 20),
}

# Gender name transforms (tên cho từng hành tinh)
GENDER_NAMES = {
    "LANG": {TRAI_DAT: "Làng Aru", NAMEC: "Làng Mori", XAYDA: "Làng Kakarot"},
    "NPC_NHA": {TRAI_DAT: "ông Gôhan", NAMEC: "ông Moori", XAYDA: "ông Paragus"},
    "NPC_QUY_LAO": {TRAI_DAT: "Quy Lão Kame", NAMEC: "Trưởng lão Guru", XAYDA: "Vua Vegeta"},
    "MAP_200": {TRAI_DAT: "Đồi hoa cúc", NAMEC: "Đồi nấm tím", XAYDA: "Đồi hoang"},
    "MAP_QUY_LAO": {TRAI_DAT: "Đảo Kamê", NAMEC: "Đảo Guru", XAYDA: "Vách núi đen"},
    "QUAI_BAY": {TRAI_DAT: "thằn lằn bay", NAMEC: "phi long", XAYDA: "quỷ bay"},
    "QUAI_1000": {TRAI_DAT: "phi long mẹ", NAMEC: "quỷ bay mẹ", XAYDA: "thằn lằn mẹ"},
    "QUAI_200": {TRAI_DAT: "khủng long", NAMEC: "lợn lòi", XAYDA: "quỷ đất"},
    "QUAI_3000": {TRAI_DAT: "ốc mượn hồn", NAMEC: "ốc sên", XAYDA: "heo Xayda mẹ"},
}

# =============================================================================
# COMPLETE NPC REPORT CONFIG (dựa trên checkDoneTaskTalkNpc và ConstTask)
# Mỗi mục: (npc_template_id, npc_name_in_vietnamese)
# =============================================================================
REPORT_NPC_MAP = {
    # Elder NPCs - Gender specific
    "ông gôhan": lambda g: (NPC["ONG_GOHAN"],),
    "ông moori": lambda g: (NPC["ONG_MOORI"],),
    "ông paragus": lambda g: (NPC["ONG_PARAGUS"],),
    "ông già": lambda g: (NPC["ONG_GOHAN"],),
    "ông nội": lambda g: (NPC["ONG_GOHAN"],),
    
    # Master NPCs - Gender specific
    "quy lão kame": lambda g: (NPC["QUY_LAO_KAME"],),
    "quy lão": lambda g: (NPC["QUY_LAO_KAME"],),
    "trưởng lão guru": lambda g: (NPC["TRUONG_LAO_GURU"],),
    "trưởng lão": lambda g: (NPC["TRUONG_LAO_GURU"],),
    "vua vegeta": lambda g: (NPC["VUA_VEGETA"],),
    
    # Shop NPCs - Gender specific
    "bunma": lambda g: (NPC["BUNMA"],),
    "dende": lambda g: (NPC["DENDE"],),
    "appule": lambda g: (NPC["APPULE"],),
    "cô bunma": lambda g: (NPC["BUNMA"],),
    
    # Spaceport NPCs
    "dr. brief": lambda g: (NPC["DR_DRIEF"],),
    "dr brief": lambda g: (NPC["DR_DRIEF"],),
    "cargo": lambda g: (NPC["CARGO"],),
    "cui": lambda g: (NPC["CUI"],),
    
    # Future NPCs
    "bunma tương lai": lambda g: (NPC["BUNMA_TL"],),
    "bunma tl": lambda g: (NPC["BUNMA_TL"],),
    "bulma tương lai": lambda g: (NPC["BUNMA_TL"],),
    "calick": lambda g: (NPC["CALICK"],),
    "ca lích": lambda g: (NPC["CALICK"],),
    
    # Later game NPCs
    "thần mèo karin": lambda g: (NPC["THAN_MEO_KARIN"],),
    "thần mèo": lambda g: (NPC["THAN_MEO_KARIN"],),
    "karin": lambda g: (NPC["THAN_MEO_KARIN"],),
    "thượng đế": lambda g: (NPC["THUONG_DE"],),
    "thần vũ trụ": lambda g: (NPC["THAN_VU_TRU"],),
    "quốc vương": lambda g: (NPC["QUOC_VUONG"],),
    "tổ sư kaio": lambda g: (NPC["TO_SU_KAIO"],),
    "ô sin": lambda g: (NPC["OSIN"],),
    "osin": lambda g: (NPC["OSIN"],),
    "mr popo": lambda g: (NPC["MR_POPO"],),
}

# =============================================================================
# COMPLETE BOSS CONFIG (dựa trên checkDoneTaskKillBoss)
# Mỗi mục: [spawn_maps, npc_cui_index, min_hp, min_dam]
# =============================================================================
BOSS_CONFIG = {
    # Task 19: Kuku, Map Dau Dinh, Rambo
    "kuku": {"spawn_maps": [68, 69, 70, 71, 72], "cui_tid": 12, "cui_menu_idx": 1, 
             "required_task": "TASK_19_0", "boss_id": "KUKU", "min_hp": 150000, "min_dam": 10000},
    "mập đầu đinh": {"spawn_maps": [63, 64, 65, 66, 67], "cui_tid": 12, "cui_menu_idx": 0,
                     "required_task": "TASK_19_1", "boss_id": "MAP_DAU_DINH", "min_hp": 150000, "min_dam": 10000},
    "map dau dinh": {"spawn_maps": [63, 64, 65, 66, 67], "cui_tid": 12, "cui_menu_idx": 0,
                     "required_task": "TASK_19_1", "boss_id": "MAP_DAU_DINH", "min_hp": 150000, "min_dam": 10000},
    "rambo": {"spawn_maps": [73, 74, 75, 76, 77], "cui_tid": 12, "cui_menu_idx": 1,
              "required_task": "TASK_19_2", "boss_id": "RAMBO", "min_hp": 150000, "min_dam": 10000},
              
    # Task 20: Tiểu đội sát thủ (Số 4, 3, 2, 1, Tiểu Đội Trưởng)
    # Spawn maps từ BossesData.java: new int[]{79, 81, 82, 83}
    "số 4": {"spawn_maps": [79, 81, 82, 83], "cui_tid": -1, "cui_menu_idx": 0,
             "required_task": "TASK_20_1", "boss_id": "SO_4", "min_hp": 500000, "min_dam": 30000},
    "so 4": {"spawn_maps": [79, 81, 82, 83], "cui_tid": -1, "cui_menu_idx": 0,
             "required_task": "TASK_20_1", "boss_id": "SO_4", "min_hp": 500000, "min_dam": 30000},
    "số 3": {"spawn_maps": [79, 81, 82, 83], "cui_tid": -1, "cui_menu_idx": 0,
             "required_task": "TASK_20_2", "boss_id": "SO_3", "min_hp": 500000, "min_dam": 30000},
    "so 3": {"spawn_maps": [79, 81, 82, 83], "cui_tid": -1, "cui_menu_idx": 0,
             "required_task": "TASK_20_2", "boss_id": "SO_3", "min_hp": 500000, "min_dam": 30000},
    "số 2": {"spawn_maps": [79, 81, 82, 83], "cui_tid": -1, "cui_menu_idx": 0,
             "required_task": "TASK_20_3", "boss_id": "SO_2", "min_hp": 500000, "min_dam": 30000},
    "so 2": {"spawn_maps": [79, 81, 82, 83], "cui_tid": -1, "cui_menu_idx": 0,
             "required_task": "TASK_20_3", "boss_id": "SO_2", "min_hp": 500000, "min_dam": 30000},
    "số 1": {"spawn_maps": [79, 81, 82, 83], "cui_tid": -1, "cui_menu_idx": 0,
             "required_task": "TASK_20_4", "boss_id": "SO_1", "min_hp": 500000, "min_dam": 30000},
    "so 1": {"spawn_maps": [79, 81, 82, 83], "cui_tid": -1, "cui_menu_idx": 0,
             "required_task": "TASK_20_4", "boss_id": "SO_1", "min_hp": 500000, "min_dam": 30000},
    "tiểu đội sát thủ": {"spawn_maps": [79, 81, 82, 83], "cui_tid": -1, "cui_menu_idx": 0,
                        "required_task": "TASK_20_5", "boss_id": "TIEU_DOI_TRUONG", "min_hp": 1000000, "min_dam": 50000},
    "tiểu đội trưởng": {"spawn_maps": [79, 81, 82, 83], "cui_tid": -1, "cui_menu_idx": 0,
                       "required_task": "TASK_20_5", "boss_id": "TIEU_DOI_TRUONG", "min_hp": 1000000, "min_dam": 50000},
                         
    # Task 21: Fide (3 levels) - spawn map từ BossesData.java: new int[]{80}
    "fide": {"spawn_maps": [80], "cui_tid": -1, "cui_menu_idx": 0,
             "required_task": "TASK_21_1", "boss_id": "FIDE_0", "min_hp": 2000000, "min_dam": 100000},
    "fide 1": {"spawn_maps": [80], "cui_tid": -1, "cui_menu_idx": 0,
               "required_task": "TASK_21_1", "boss_id": "FIDE_0", "min_hp": 2000000, "min_dam": 100000},
    "fide đại ca": {"spawn_maps": [80], "cui_tid": -1, "cui_menu_idx": 0,
                    "required_task": "TASK_21_1", "boss_id": "FIDE_0", "min_hp": 2000000, "min_dam": 100000},
    "fide 2": {"spawn_maps": [80], "cui_tid": -1, "cui_menu_idx": 0,
               "required_task": "TASK_21_2", "boss_id": "FIDE_1", "min_hp": 3000000, "min_dam": 200000},
    "fide 3": {"spawn_maps": [80], "cui_tid": -1, "cui_menu_idx": 0,
               "required_task": "TASK_21_3", "boss_id": "FIDE_2", "min_hp": 5000000, "min_dam": 300000},
               
    # Task 23: Android 19, Dr.Kore - dùng xmap
    "android 19": {"spawn_maps": [92, 93, 94], "cui_tid": -1, "cui_menu_idx": 0,
                   "required_task": "TASK_23_1", "boss_id": "ANDROID_19", "min_hp": 5000000, "min_dam": 300000},
    "dr.kore": {"spawn_maps": [104], "cui_tid": -1, "cui_menu_idx": 0,
                "required_task": "TASK_23_2", "boss_id": "DR_KORE", "min_hp": 5000000, "min_dam": 300000},
    "dr kore": {"spawn_maps": [104], "cui_tid": -1, "cui_menu_idx": 0,
                "required_task": "TASK_23_2", "boss_id": "DR_KORE", "min_hp": 5000000, "min_dam": 300000},
    "dr.kôrê": {"spawn_maps": [104], "cui_tid": -1, "cui_menu_idx": 0,
                "required_task": "TASK_23_2", "boss_id": "DR_KORE", "min_hp": 5000000, "min_dam": 300000},
                
    # Task 24: Android 15, 14, 13 - dùng xmap
    "android 15": {"spawn_maps": [104], "cui_tid": -1, "cui_menu_idx": 0,
                   "required_task": "TASK_24_1", "boss_id": "ANDROID_15", "min_hp": 8000000, "min_dam": 500000},
    "android 14": {"spawn_maps": [104], "cui_tid": -1, "cui_menu_idx": 0,
                   "required_task": "TASK_24_2", "boss_id": "ANDROID_14", "min_hp": 8000000, "min_dam": 500000},
    "android 13": {"spawn_maps": [104], "cui_tid": -1, "cui_menu_idx": 0,
                   "required_task": "TASK_24_3", "boss_id": "ANDROID_13", "min_hp": 12000000, "min_dam": 800000},
                   
    # Task 25: Poc, Pic, King Kong - dùng xmap
    "poc": {"spawn_maps": [96, 97, 98], "cui_tid": -1, "cui_menu_idx": 0,
            "required_task": "TASK_25_1", "boss_id": "POC", "min_hp": 8000000, "min_dam": 500000},
    "pic": {"spawn_maps": [96, 97, 98], "cui_tid": -1, "cui_menu_idx": 0,
            "required_task": "TASK_25_2", "boss_id": "PIC", "min_hp": 8000000, "min_dam": 500000},
    "king kong": {"spawn_maps": [96, 97, 98], "cui_tid": -1, "cui_menu_idx": 0,
                  "required_task": "TASK_25_3", "boss_id": "KING_KONG", "min_hp": 12000000, "min_dam": 800000},
                  
    # Task 26: Xen Bo Hung - dùng xmap
    "xên bọ hung": {"spawn_maps": [103], "cui_tid": -1, "cui_menu_idx": 0,
                    "required_task": "TASK_26_1", "boss_id": "XEN_BO_HUNG", "min_hp": 20000000, "min_dam": 1500000},
    "xen bo hung": {"spawn_maps": [103], "cui_tid": -1, "cui_menu_idx": 0,
                    "required_task": "TASK_26_1", "boss_id": "XEN_BO_HUNG", "min_hp": 20000000, "min_dam": 1500000},
                    
    # Task 28: Drabura, Bui Bui, Ya Con, Mabu - dùng xmap tới đấu trường
    "drabura": {"spawn_maps": [152, 153, 154, 155], "cui_tid": -1, "cui_menu_idx": 0,
                "required_task": "TASK_28_1", "boss_id": "DRABURA", "min_hp": 15000000, "min_dam": 1000000},
    "bui bui": {"spawn_maps": [152, 153, 154, 155], "cui_tid": -1, "cui_menu_idx": 0,
                "required_task": "TASK_28_2", "boss_id": "BUI_BUI", "min_hp": 15000000, "min_dam": 1000000},
    "ya con": {"spawn_maps": [152, 153, 154, 155], "cui_tid": -1, "cui_menu_idx": 0,
               "required_task": "TASK_28_4", "boss_id": "YA_CON", "min_hp": 15000000, "min_dam": 1000000},
    "yacon": {"spawn_maps": [152, 153, 154, 155], "cui_tid": -1, "cui_menu_idx": 0,
              "required_task": "TASK_28_4", "boss_id": "YA_CON", "min_hp": 15000000, "min_dam": 1000000},
    "mabu": {"spawn_maps": [152, 153, 154, 155], "cui_tid": -1, "cui_menu_idx": 0,
             "required_task": "TASK_28_6", "boss_id": "MABU_12H", "min_hp": 20000000, "min_dam": 1500000},
    "mabư": {"spawn_maps": [152, 153, 154, 155], "cui_tid": -1, "cui_menu_idx": 0,
             "required_task": "TASK_28_6", "boss_id": "MABU_12H", "min_hp": 20000000, "min_dam": 1500000},
}

# =============================================================================
# MOB TEMPLATE ID -> NAME mapping (từ ConstMob.java)
# =============================================================================
MOB_TEMPLATE_NAMES = {
    0: "mộc nhân", 1: "khủng long", 2: "lợn lòi", 3: "quỷ đất",
    4: "khủng long mẹ", 5: "lợn lòi mẹ", 6: "quỷ đất mẹ",
    7: "thằn lằn bay", 8: "phi long", 9: "quỷ bay",
    10: "thằn lằn mẹ", 11: "phi long mẹ", 12: "quỷ bay mẹ",
    13: "ốc mượn hồn", 14: "ốc sên", 15: "heo xayda mẹ",
    16: "heo rừng", 17: "heo da xanh", 18: "heo xayda",
    19: "heo rừng mẹ", 20: "heo xanh mẹ", 21: "alien",
    22: "bulon", 23: "ukulele", 24: "quỷ mập",
    25: "tambourine", 26: "drum", 27: "akkuman",
    31: "không tặc", 32: "quỷ đầu to", 33: "quỷ địa ngục",
    34: "lính độc nhãn", 35: "lính độc nhãn",
    39: "nappa", 40: "soldier", 41: "appule", 42: "raspberry", 43: "thằn lằn xanh",
    44: "quỷ đầu nhọn", 45: "quỷ đầu vàng", 46: "quỷ da tím", 47: "quỷ già",
    48: "cá sấu", 49: "dơi da xanh", 50: "quỷ chim",
    51: "lính đầu trọc", 52: "lính tai dài", 53: "lính vũ trụ",
    54: "khỉ lông đen", 55: "khỉ giáp sắt", 56: "khỉ lông đỏ", 57: "khỉ lông vàng",
    58: "xên con cấp 1", 59: "xên con cấp 2", 60: "xên con cấp 3",
    61: "xên con cấp 4", 62: "xên con cấp 5", 63: "xên con cấp 6",
    64: "xên con cấp 7", 65: "xên con cấp 8",
    66: "tai tím", 67: "abo", 68: "kado", 69: "da xanh",
}

# Mob template ID -> Map ID mapping (kết hợp từ auto_NVBoMong.MOB_LOCATION_DATA + maps_config.json + phân tích)
MOB_LOCATION_DATA = {
    "mộc nhân": (14, 0), "khủng long": (1, 1), "lợn lòi": (8, 2), "quỷ đất": (15, 3),
    "khủng long mẹ": (2, 4), "lợn lòi mẹ": (9, 5), "quỷ đất mẹ": (16, 6),
    "thằn lằn bay": (3, 7), "phi long": (11, 8), "quỷ bay": (17, 9), "thằn lằn mẹ": (4, 10),
    "phi long mẹ": (12, 11), "quỷ bay mẹ": (18, 12),
    "ốc mượn hồn": (29, 13), "ốc sên": (33, 14), "heo xayda mẹ": (37, 15),
    "heo rừng": (28, 16), "heo da xanh": (32, 17), "heo xayda": (36, 18),
    "heo rừng mẹ": (6, 19), "heo xanh mẹ": (10, 20), "alien": (19, 21),
    "bulon": (30, 22), "ukulele": (34, 23), "quỷ mập": (38, 24),
    "tambourine": (6, 25), "drum": (10, 26), "akkuman": (19, 27),
    "không tặc": (29, 31), "quỷ đầu to": (33, 32), "quỷ địa ngục": (37, 33),
    "nappa": (68, 39), "soldier": (70, 40), "appule": (71, 41), "raspberry": (71, 42),
    "thằn lằn xanh": (72, 43), "quỷ đầu nhọn": (64, 44), "quỷ đầu vàng": (63, 45),
    "quỷ da tím": (66, 46), "quỷ già": (67, 47), "cá sấu": (73, 48),
    "dơi da xanh": (67, 49), "quỷ chim": (81, 50), "lính đầu trọc": (74, 51),
    "lính tai dài": (76, 52), "lính vũ trụ": (77, 53), "khỉ lông đen": (82, 54),
    "khỉ giáp sắt": (83, 55), "khỉ lông đỏ": (79, 56), "khỉ lông vàng": (80, 57),
    "xên con cấp 1": (92, 58), "xên con cấp 2": (93, 59), "xên con cấp 3": (94, 60),
    "xên con cấp 4": (96, 61), "xên con cấp 5": (97, 62), "xên con cấp 6": (98, 63),
    "xên con cấp 7": (99, 64), "xên con cấp 8": (100, 65), "tai tím": (106, 66),
    "abo": (107, 67), "kado": (109, 68), "da xanh": (110, 69),
    "khỉ lông xanh": (155, 78), "taburine đỏ": (155, 79),
    "ếch mặt đỏ": (166, 86), "jinai": (166, 87),
}

# Map ID -> name lookup (từ map_data.py)
# Imported at runtime to avoid circular import
MAP_ID_TO_NAME = {}

# NPC Template ID -> Map ID (nơi NPC đó đứng)
NPC_LOCATION_MAP = {
    NPC["CUI"]: 19,           # Thành phố Vegeta
    NPC["QUY_LAO_KAME"]: 5,   # Đảo Kame
    NPC["TRUONG_LAO_GURU"]: 13, # Đảo Guru
    NPC["VUA_VEGETA"]: 20,    # Vách núi đen
    NPC["ONG_GOHAN"]: 21,     # Nhà Gôhan
    NPC["ONG_MOORI"]: 22,     # Nhà Moori
    NPC["ONG_PARAGUS"]: 23,   # Nhà Broly
    NPC["BUNMA"]: 0,          # Làng Aru
    NPC["DENDE"]: 7,          # Làng Mori
    NPC["APPULE"]: 14,        # Làng Kakarot
    NPC["DR_DRIEF"]: 24,      # Trạm tàu vũ trụ
    NPC["CARGO"]: 25,         # Trạm tàu vũ trụ
    NPC["CALICK"]: 27,        # Rừng Bamboo (Tương Lai)
    NPC["BUNMA_TL"]: 102,     # Nhà Bunma (Tương Lai)
    NPC["THAN_MEO_KARIN"]: 46, # Tháp Karin
    NPC["THUONG_DE"]: 45,     # Thần điện
    NPC["QUOC_VUONG"]: 43,    # Vách núi Moori
    NPC["OSIN"]: 52,          # Đại hội võ thuật
    NPC["MR_POPO"]: 45,       # Thần điện
}


# =============================================================================
# ENUMS
# =============================================================================

class AutoQuestState(Enum):
    IDLE = "Chờ"
    ANALYZE_TASK = "Phân tích nhiệm vụ"
    HANDLE_REPORT = "Báo cáo NPC"
    HANDLE_MOB_KILL = "Giết quái"
    HANDLE_BOSS = "Săn boss"
    HANDLE_ENTER_MAP = "Vào bản đồ"
    HANDLE_STAT = "Tăng sức mạnh"
    WAITING = "Đang chờ"


# =============================================================================
# MAIN CLASS
# =============================================================================

class AutoMainQuest:
    def __init__(self, account):
        self.account = account
        self.is_running = False
        self.task = None
        self.state = AutoQuestState.IDLE
        self.current_status_msg = "Đang tắt"
        
        # Config data
        self.config_data = self._load_config()
        self._load_map_names()
        
        # Boss tracking
        self._boss_map_id = None
        self._boss_step_index = -1
        self._boss_skip = False
        self.boss_blacklist_time = {}
        
        # Mob tracking
        self.blacklist_mobs = {}
        self._mob_target_info = None  # (map_id, mob_template_id, count_needed)
        
        # Stats
        self.quests_completed = 0
        self.total_kills = 0
        self.start_time = None
        
        # Auto MSM reference
        self._auto_msm = None

    def _load_config(self):
        """Load maps_config.json để biết map nào có quái gì"""
        try:
            with open('maps_config.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {"maps": []}

    def _load_map_names(self):
        """Load map name data"""
        global MAP_ID_TO_NAME
        try:
            from logic.map_data import MAP_ID_TO_NAME as _map_names
            MAP_ID_TO_NAME.update(_map_names)
        except Exception:
            pass

    # ── Gender Helpers ──────────────────────────────────────────

    def _get_gender_npc(self, key: str) -> int:
        """Lấy NPC template ID theo gender"""
        gender = self.account.char.gender
        if key in GENDER_NPC_MAP:
            vals = GENDER_NPC_MAP[key]
            if gender < len(vals):
                return vals[gender]
        return -1

    def _get_gender_map(self, key: str) -> int:
        """Lấy map ID theo gender"""
        gender = self.account.char.gender
        if key in GENDER_MAP_MAP:
            vals = GENDER_MAP_MAP[key]
            if gender < len(vals):
                return vals[gender]
        return -1

    def _get_gender_name(self, key: str) -> str:
        """Lấy tên theo gender"""
        gender = self.account.char.gender
        if key in GENDER_NAMES and gender in GENDER_NAMES[key]:
            return GENDER_NAMES[key][gender]
        return ""

    # ── NPC Detection ────────────────────────────────────────────

    def _find_report_npc(self, step_name: str):
        """
        Phân tích sub_name của task để tìm NPC cần báo cáo.
        Trả về (npc_template_id, map_id) hoặc None.
        """
        step_lower = step_name.lower().strip()
        
        # 1. Check các từ khóa báo cáo
        report_keywords = ["báo cáo", "báo tin", "gặp", "nói chuyện", "hỏi", 
                          "trả lời", "tìm", "quay về", "về gặp", "đến gặp",
                          "tới gặp", "về chỗ", "về nhà"]
        is_report = any(kw in step_lower for kw in report_keywords)
        
        # 2. Check trong REPORT_NPC_MAP
        for npc_key, resolver in REPORT_NPC_MAP.items():
            if npc_key in step_lower:
                result = resolver(self.account.char.gender)
                npc_tid = result[0]
                map_id = NPC_LOCATION_MAP.get(npc_tid, -1)
                return (npc_tid, map_id)
        
        # 3. Nếu không match keyword NPC, thử parse gender-based
        # "về nhà" -> Nhà NPC
        if "về nhà" in step_lower or "về làng" in step_lower:
            npc_tid = self._get_gender_npc("NPC_NHA")
            map_id = NPC_LOCATION_MAP.get(npc_tid, -1)
            if npc_tid != -1 and map_id != -1:
                return (npc_tid, map_id)
        
        # "báo cáo với sư phụ" -> Quy Lão
        if is_report and ("sư phụ" in step_lower or "thầy" in step_lower):
            npc_tid = self._get_gender_npc("NPC_QUY_LAO")
            map_id = NPC_LOCATION_MAP.get(npc_tid, -1)
            if npc_tid != -1 and map_id != -1:
                return (npc_tid, map_id)
        
        # 4. Check trong NPC_LOCATION_MAP as fallback
        for npc_name, npc_tid in NPC.items():
            npc_name_lower = npc_name.lower().replace("_", " ")
            if npc_name_lower in step_lower and npc_tid in NPC_LOCATION_MAP:
                return (npc_tid, NPC_LOCATION_MAP[npc_tid])
        
        return None

    # ── Boss Detection ──────────────────────────────────────────

    def _find_boss_in_step(self, step_name: str):
        """Tìm boss trong sub_name của task"""
        step_lower = step_name.lower()
        for boss_name, config in BOSS_CONFIG.items():
            if boss_name in step_lower:
                return (boss_name, config["spawn_maps"], config["cui_tid"],
                        config["min_hp"], config["min_dam"])
        return None

    # ── Mob Detection ───────────────────────────────────────────

    def _find_mob_in_step(self, step_name: str):
        """
        Tìm quái cần tiêu diệt trong sub_name.
        Parse dạng: "Hạ X <tên quái>"
        Trả về (mob_name, count_to_kill) hoặc None
        """
        step_lower = step_name.lower()
        
        # Parse "Hạ X <tên quái>" hoặc "đánh X", "tiêu diệt X", "giết X"
        match = re.search(r"(?:hạ|đánh|tiêu diệt|giết|diệt)\s+(\d+)\s+(.+)", step_lower)
        if match:
            count = int(match.group(1))
            mob_name_raw = match.group(2).strip()
            
            # Tìm trong MOB_LOCATION_DATA
            for mob_key, (map_id, mob_tid) in MOB_LOCATION_DATA.items():
                if mob_key in mob_name_raw or mob_name_raw in mob_key:
                    return (map_id, mob_tid, count, mob_key)
            
            # Fallback: fuzzy match
            for mob_key, (map_id, mob_tid) in MOB_LOCATION_DATA.items():
                # Tách từ, so sánh từng từ
                mob_words = mob_key.split()
                name_words = mob_name_raw.split()
                common = set(mob_words) & set(name_words)
                if len(common) >= max(1, len(mob_words) - 1):
                    return (map_id, mob_tid, count, mob_key)
        
        # Fallback: chỉ tìm tên quái
        for mob_key, (map_id, mob_tid) in MOB_LOCATION_DATA.items():
            if mob_key in step_lower:
                # Tìm số lượng
                count_match = re.search(r"(\d+)", step_lower)
                cnt = int(count_match.group(1)) if count_match else 999
                return (map_id, mob_tid, cnt, mob_key)
        
        # Check maps_config.json
        for map_info in self.config_data.get("maps", []):
            for mob in map_info.get("mobs", []):
                mob_name = mob["mob_name"].lower()
                if mob_name in step_lower:
                    return (map_info["map_id"], mob["mob_id"], mob.get("count", 1), mob_name)
        
        return None

    def _find_enter_map_in_step(self, step_name: str):
        """
        Tìm map cần vào trong sub_name.
        Trả về map_id hoặc None
        """
        step_lower = step_name.lower()
        
        # Đã ở bước enter map, kiểm tra xem có map keyword không
        from logic.map_data import MAP_NAME_TO_ID as name_to_id
        for map_name, map_id in name_to_id.items():
            if map_name.lower() in step_lower:
                return map_id
        
        # Gender-based maps
        for key, vals in GENDER_MAP_MAP.items():
            if key in step_lower.upper():
                gender = self.account.char.gender
                if gender < len(vals):
                    return vals[gender]
        
        return None

    # ── Helper: Find Boss Target ────────────────────────────────

    def _find_boss_target(self, boss_name: str):
        """Tìm boss trong chars hoặc mobs theo tên"""
        # 1. Check chars trước (một số boss là character)
        for cid, cdata in self.account.controller.chars.items():
            if boss_name.lower() in cdata.get('name', '').lower():
                return ("char", cid, cdata)
        # 2. Check mobs (hầu hết boss là mob)
        for mid, mob in self.account.controller.mobs.items():
            if boss_name.lower() in mob.name.lower():
                return ("mob", mid, mob)
        # 3. Fallback: check mob name không dấu
        boss_ascii = ''.join(c for c in unicodedata.normalize('NFD', boss_name.lower())
                            if unicodedata.category(c) != 'Mn')
        for mid, mob in self.account.controller.mobs.items():
            mob_ascii = ''.join(c for c in unicodedata.normalize('NFD', mob.name.lower())
                               if unicodedata.category(c) != 'Mn')
            if boss_ascii in mob_ascii:
                return ("mob", mid, mob)
        return None

    def _get_boss_hp(self, target: tuple) -> int:
        """Lấy HP của boss từ target tuple (type, id, data)"""
        if not target:
            return 0
        ttype, tid, tdata = target
        if ttype == "char":
            return tdata.get('hp', 0)
        else:  # mob
            return tdata.hp if hasattr(tdata, 'hp') else 0

    def _get_boss_pos(self, target: tuple) -> tuple:
        """Lấy tọa độ (x, y) của boss"""
        if not target:
            return (0, 0)
        ttype, tid, tdata = target
        if ttype == "char":
            return (tdata.get('x', 0), tdata.get('y', 0))
        else:  # mob
            return (tdata.x if hasattr(tdata, 'x') else 0,
                    tdata.y if hasattr(tdata, 'y') else 0)

    def _get_boss_name(self, target: tuple) -> str:
        """Lấy tên boss"""
        if not target:
            return ""
        ttype, tid, tdata = target
        if ttype == "char":
            return tdata.get('name', 'Unknown')
        else:  # mob
            return tdata.name if hasattr(tdata, 'name') else f"Mob_{tid}"

    # ── State: Analyze Task ─────────────────────────────────────

    async def _analyze_task(self):
        """Phân tích task hiện tại và chọn state phù hợp"""
        task = self.account.char.task
        if not task or task.index >= len(task.sub_names):
            await asyncio.sleep(5)
            return
        
        step_name = task.sub_names[task.index]
        username = self.account.username
        controller = self.account.controller
        
        # ⚡ Dừng combat modes khi chuyển bước (tránh auto_play chạy khi cần NPC)
        if controller.auto_play.interval:
            controller.toggle_autoplay(False)
        if controller.auto_attack and controller.auto_attack.is_running:
            controller.toggle_auto_attack(False)
        # Tắt auto MSM nếu còn chạy (tránh xung đột khi chuyển sang boss/mob/NPC)
        if self._auto_msm and self._auto_msm.is_running:
            self._auto_msm.stop()
            self._auto_msm = None
        
        logger.info(f"[{username}] [AutoQuest] Phân tích bước {task.index}: '{step_name}'")
        
        # 1. Check báo cáo NPC
        npc_info = self._find_report_npc(step_name)
        if npc_info:
            self.current_status_msg = f"Báo cáo NPC (TID:{npc_info[0]})"
            await self._handle_report_npc(npc_info[0], npc_info[1], step_name)
            return
        
        # 2. Check boss
        boss_info = self._find_boss_in_step(step_name)
        if boss_info:
            boss_name, spawn_maps, cui_tid, min_hp, min_dam = boss_info
            if self._boss_step_index >= 0 and task.index > self._boss_step_index:
                self._boss_step_index = -1
                self._boss_skip = False
            if not self._boss_skip:
                await self._handle_boss_task(boss_name, spawn_maps, cui_tid, step_name)
            else:
                self.current_status_msg = "Bỏ qua boss (stats không đủ)"
                await asyncio.sleep(5)
            return
        
        # 3. Check giết quái
        mob_info = self._find_mob_in_step(step_name)
        if mob_info:
            map_id, mob_tid, count, mob_name = mob_info
            self._mob_target_info = mob_info
            await self._handle_mob_kill(map_id, mob_tid, count, mob_name, step_name)
            return
        
        # 4. Check vào bản đồ
        map_id = self._find_enter_map_in_step(step_name)
        if map_id is not None:
            await self._handle_enter_map(map_id)
            return
        
        # 5. Check stat requirement ("Đạt X sức mạnh", "Đạt X tỷ sức mạnh")
        stat_info = self._check_stat_task(step_name)
        if stat_info:
            await self._handle_stat_task(stat_info[0], stat_info[1])
            return
        
        # 6. Không xác định
        if getattr(self, '_last_missing', None) != step_name:
            logger.info(f"[{username}] [AutoQuest] ❓ Không xác định được bước: '{step_name}'")
            self._last_missing = step_name
        await asyncio.sleep(10)

    # ── Handler: Report NPC ─────────────────────────────────────

    async def _handle_report_npc(self, npc_tid: int, target_map: int, step_name: str):
        """Xử lý báo cáo với NPC"""
        username = self.account.username
        char = self.account.char
        
        # Nếu chưa biết map, thử tìm NPC trong map hiện tại
        if target_map <= 0:
            for _, npc_data in self.account.controller.npcs.items():
                if npc_data.get('template_id') == npc_tid:
                    target_map = self.account.char.map_id
                    break
            if target_map <= 0:
                # Fallback: quét tất cả NPC có template_id này
                target_map = self.account.char.map_id  # giả định NPC ở map hiện tại
        
        self.current_status_msg = f"Báo cáo NPC TID:{npc_tid} (Map {target_map})"
        
        # Di chuyển tới map của NPC
        if char.map_id != target_map and target_map > 0:
            logger.info(f"[{username}] [AutoQuest] Di chuyển tới Map {target_map} để báo cáo NPC...")
            if not self.account.controller.xmap.is_xmapping:
                await self.account.controller.xmap.start(target_map)
            await asyncio.sleep(2)
            return
        
        # Tìm NPC trong map
        npc_data = None
        for _, info in self.account.controller.npcs.items():
            if info.get('template_id') == npc_tid:
                npc_data = info
                break
        
        # Teleport tới NPC
        if npc_data:
            await self.account.controller.movement.teleport_to(npc_data['x'], npc_data['y'] - 3)
        else:
            ok = await self.account.controller.movement.teleport_to_npc(npc_tid, search_by_template=True)
            if not ok:
                await asyncio.sleep(2)
                return
        await asyncio.sleep(0.2)
        
        # Mở menu NPC và thử các option để báo cáo
        cur_idx = self.account.char.task.index
        self.account.controller.ui_menu_event.clear()
        await self.account.service.open_menu_npc(npc_tid)
        try:
            await asyncio.wait_for(self.account.controller.ui_menu_event.wait(), timeout=5.0)
            opts = self.account.controller.last_ui_options
            if opts:
                # Thử option 0, nếu task chưa chuyển thì thử option 1
                for try_idx in [0, 1]:
                    if try_idx >= len(opts):
                        break
                    self.account.controller.ui_menu_event.clear()
                    await self.account.service.confirm_menu_npc(npc_tid, try_idx)
                    await asyncio.sleep(1.5)
                    if self.account.char.task.index > cur_idx:
                        logger.info(f"[{username}] [AutoQuest] Báo cáo thành công (option {try_idx}).")
                        break
        except asyncio.TimeoutError:
            if self.account.char.task.index > cur_idx:
                logger.info(f"[{username}] [AutoQuest] Task đã hoàn thành (silent update).")
        await asyncio.sleep(0.2)

    # ── Handler: Mob Kill ───────────────────────────────────────

    async def _handle_mob_kill(self, target_map: int, mob_tid: int, count: int, mob_name: str, step_name: str):
        """Xử lý giết quái để hoàn thành nhiệm vụ"""
        username = self.account.username
        char = self.account.char
        task = self.account.char.task
        
        self.current_status_msg = f"Giết {mob_name} ({count} con)"
        
        # Cập nhật target cho auto_play (chỉ khi cần)
        controller = self.account.controller
        if mob_tid not in controller.auto_play.target_mobs or len(controller.auto_play.target_mobs) != 1:
            controller.auto_play.target_mobs.clear()
            controller.auto_play.target_mobs.add(mob_tid)
        
        # Di chuyển tới map
        if char.map_id != target_map and target_map > 0:
            self.current_status_msg = f"Di chuyển Map {target_map} ({mob_name})"
            if not controller.xmap.is_xmapping:
                await controller.xmap.start(target_map)
            await asyncio.sleep(2)
            return
        
        # Đã ở đúng map, bật auto_play để đánh
        if not controller.auto_play.interval:
            logger.info(f"[{username}] [AutoQuest] Bật auto_play để giết {mob_name}")
            controller.toggle_autoplay(True)
        
        # Kiểm tra tiến độ
        if task.count >= task.counts[task.index] if task.index < len(task.counts) else 999:
            controller.toggle_autoplay(False)
            return
        
        await asyncio.sleep(0.2)

    # ── Handler: Boss ───────────────────────────────────────────

    async def _handle_boss_task(self, boss_name: str, spawn_maps: list, cui_tid: int, step_name: str):
        """Xử lý săn boss cho nhiệm vụ"""
        username = self.account.username
        char = self.account.char
        task = self.account.char.task
        self._boss_step_index = task.index
        
        # Kiểm tra stats
        if char.c_hp_full < 150000:
            logger.info(f"[{username}] [AutoQuest] ⛔ HP max ({char.c_hp_full:,}) < 150k. Bỏ qua boss.")
            self.current_status_msg = "HP < 150k - Bỏ qua boss"
            self._boss_skip = True
            return
        if char.c_dam_full < 10000:
            logger.info(f"[{username}] [AutoQuest] ⛔ Dame ({char.c_dam_full:,}) < 10k. Bỏ qua boss.")
            self.current_status_msg = "Dame < 10k - Bỏ qua boss"
            self._boss_skip = True
            return
        self._boss_skip = False
        
        # Chết → hồi sinh
        if char.c_hp == 0:
            logger.info(f"[{username}] [AutoQuest] Chết! Hồi sinh...")
            await self.account.service.return_town_from_dead()
            await asyncio.sleep(3)
            if self._boss_map_id and self._boss_map_id in spawn_maps:
                if not self.account.controller.xmap.is_xmapping:
                    await self.account.controller.xmap.start(self._boss_map_id)
                while self.account.controller.xmap.is_xmapping:
                    await asyncio.sleep(0.2)
            return
        
        # Nếu có cui_tid > 0, ưu tiên dùng Cui teleport
        # (Luôn dùng Cui vì boss có thể không ở cùng map/zone với nhân vật)
        if cui_tid > 0:
            # Chưa ở map 19 → di chuyển tới 19
            if char.map_id != 19:
                logger.info(f"[{username}] [AutoQuest] Di chuyển tới Map 19 (Cui) để tele tới {boss_name}...")
                if not self.account.controller.xmap.is_xmapping:
                    await self.account.controller.xmap.start(19)
                await asyncio.sleep(2)
                return
            
            # Đã ở Map 19 → dùng Cui tele
            await self._use_cui_teleport(boss_name, spawn_maps, cui_tid)
            await asyncio.sleep(2)
            
            # Đã tele xong, kiểm tra lại map
            if char.map_id in spawn_maps:
                self._boss_map_id = char.map_id
                await self._boss_fight_loop(boss_name, spawn_maps)
            else:
                logger.info(f"[{username}] [AutoQuest] Tele chưa thành công. Map hiện tại: {char.map_id}")
                await asyncio.sleep(0.2)
            return
        
        # Không có Cui, dùng xmap trực tiếp
        # Nếu đã ở spawn map thì kiểm tra boss hiện diện
        if char.map_id in spawn_maps:
            # Kiểm tra xem boss có ở map này không
            target = self._find_boss_target(boss_name)
            if target:
                self._boss_map_id = char.map_id
                await self._boss_fight_loop(boss_name, spawn_maps)
                return
            else:
                # Boss không ở map này, thử map khác trong spawn list
                logger.info(f"[{username}] [AutoQuest] Không thấy {boss_name} ở Map {char.map_id}, thử map khác...")
        
        # Di chuyển tới spawn map đầu tiên
        target_boss_map = spawn_maps[0]
        if char.map_id != target_boss_map:
            if not self.account.controller.xmap.is_xmapping:
                await self.account.controller.xmap.start(target_boss_map)
            await asyncio.sleep(2)

    async def _use_cui_teleport(self, boss_name: str, spawn_maps: list, cui_tid: int):
        """Sử dụng NPC Cui để teleport tới boss"""
        username = self.account.username
        
        # Tìm Cui
        cui_npc = None
        for _, info in self.account.controller.npcs.items():
            if info.get('template_id') == cui_tid:
                cui_npc = info
                break
        if not cui_npc:
            await asyncio.sleep(0.2)
            return
        
        await self.account.controller.movement.teleport_to(cui_npc['x'], cui_npc['y'] - 3)
        await asyncio.sleep(0.2)
        
        logger.info(f"[{username}] [AutoQuest] Mở menu Cui để tele tới {boss_name}...")
        self.account.controller.ui_menu_event.clear()
        await self.account.service.open_menu_npc(cui_tid)
        try:
            await asyncio.wait_for(self.account.controller.ui_menu_event.wait(), timeout=5.0)
            opts = self.account.controller.last_ui_options
            
            # Tìm đúng menu chứa tên boss
            target_idx = 0
            for i, opt in enumerate(opts):
                opt_clean = opt.lower().replace("\n", " ").strip()
                if boss_name.lower() in opt_clean:
                    target_idx = i
                    break
            
            await self.account.service.confirm_menu_npc(cui_tid, target_idx)
            await asyncio.sleep(2)
        except asyncio.TimeoutError:
            pass

    async def _boss_fight_loop(self, boss_name: str, spawn_maps: list):
        """Vòng lặp chiến đấu với boss"""
        username = self.account.username
        char = self.account.char
        task = self.account.char.task
        atk_count = 0
        death_count = 0
        last_pl_time = 0
        last_hp = 0
        same_hp_count = 0
        MAX_DEATHS = 3
        MAX_ATTACKS = 500
        
        logger.info(f"[{username}] [AutoQuest] ⚔️ Fight {boss_name}")
        
        # Thiết lập auto_attack trước khi vào loop
        controller_local = self.account.controller
        if controller_local.auto_attack is None:
            from logic.auto_attack import AutoAttack
            controller_local.auto_attack = AutoAttack(controller_local)
        controller_local.auto_attack.set_priority_mode("name_match", names=[boss_name])
        if not controller_local.auto_attack.is_running:
            controller_local.toggle_auto_attack(True)
        
        while self.is_running:
            # Task chuyển bước → boss đã chết
            if task.index != self._boss_step_index:
                logger.info(f"[{username}] [AutoQuest] ✅ Boss {boss_name} đã chết! Task chuyển bước.")
                self.current_status_msg = f"Hoàn thành: {boss_name}"
                if self.account.controller.auto_attack and self.account.controller.auto_attack.is_running:
                    self.account.controller.toggle_auto_attack(False)
                return
            
            # Chết
            if char.c_hp == 0:
                death_count += 1
                if death_count >= MAX_DEATHS:
                    logger.info(f"[{username}] [AutoQuest] ⛔ Chết {MAX_DEATHS} lần. Dừng boss.")
                    self.current_status_msg = f"Chết {MAX_DEATHS} lần - Dừng"
                    return
                self.current_status_msg = f"Chết lần {death_count}"
                await self.account.service.return_town_from_dead()
                await asyncio.sleep(3)
                if self._boss_map_id and self._boss_map_id in spawn_maps:
                    if not self.account.controller.xmap.is_xmapping:
                        await self.account.controller.xmap.start(self._boss_map_id)
                    while self.account.controller.xmap.is_xmapping:
                        await asyncio.sleep(0.2)
                await asyncio.sleep(0.2)
                atk_count = 0
                continue
            
            # Request player list để update HP boss
            now = time.time()
            if now - last_pl_time > 2:
                await self.account.service.request_players()
                last_pl_time = now
            
            # Tìm boss trong chars HOẶC mobs
            target = self._find_boss_target(boss_name)
            
            if not target:
                atk_count += 1
                if atk_count > MAX_ATTACKS:
                    logger.info(f"[{username}] [AutoQuest] ⚠️ Không tìm thấy {boss_name} sau {atk_count} đòn.")
                    self._boss_map_id = None
                    return
                self.current_status_msg = f"Đang tìm {boss_name}..."
                await asyncio.sleep(0.2)
                continue
            
            boss_hp = self._get_boss_hp(target)
            boss_x, boss_y = self._get_boss_pos(target)
            boss_display_name = self._get_boss_name(target)
            
            # Boss HP=0
            if boss_hp <= 0:
                logger.info(f"[{username}] [AutoQuest] {boss_name} HP=0! Chờ task update...")
                self.current_status_msg = f"{boss_name} HP=0"
                await asyncio.sleep(3)
                if task.index == self._boss_step_index:
                    self._boss_map_id = None
                return
            
            # HP không đổi
            if boss_hp == last_hp:
                same_hp_count += 1
                if same_hp_count > 50:
                    logger.info(f"[{username}] [AutoQuest] ⚠️ HP không đổi ({boss_hp}) quá lâu.")
                    self._boss_map_id = None
                    return
            else:
                same_hp_count = 0
                last_hp = boss_hp
            
            await asyncio.sleep(0.1)
            
            # Fallback: tele gần boss nếu auto_attack chưa theo kịp
            dist = math.hypot(boss_x - char.cx, boss_y - char.cy)
            if dist > 5:
                char.cx = boss_x
                char.cy = boss_y
                char.cdir = 1
                await self.account.service.char_move()
            
            atk_count += 1
            if atk_count % 10 == 0:
                logger.info(f"[{username}] [AutoQuest] ⚔️ {boss_display_name} HP:{boss_hp} deaths:{death_count} #{atk_count}")
            self.current_status_msg = f"{boss_name} HP:{boss_hp} #{atk_count}"
            
            await asyncio.sleep(0.1)

    # ── Handler: Enter Map ──────────────────────────────────────

    async def _handle_enter_map(self, target_map: int):
        """Xử lý vào một bản đồ (task yêu cầu chỉ cần vào map là hoàn thành)"""
        username = self.account.username
        char = self.account.char
        
        if char.map_id == target_map:
            self.current_status_msg = f"Đã ở Map {target_map}"
            await asyncio.sleep(0.2)
            return
        
        self.current_status_msg = f"Đi tới Map {target_map}"
        if not self.account.controller.xmap.is_xmapping:
            await self.account.controller.xmap.start(target_map)
        await asyncio.sleep(2)

    # ── Stat Check ────────────────────────────────────────────────

    def _check_stat_task(self, step_name: str):
        """Kiểm tra xem bước có yêu cầu đạt sức mạnh X không"""
        step_lower = step_name.lower()
        
        # Pattern: "Đạt X sức mạnh" hoặc "cần X sức mạnh"
        # Yêu cầu có cả từ khóa (đạt/cần) và "sức mạnh" để tránh false positive
        match = re.search(r"(?:đạt|cần)\s+([\d,.]+)\s*(tr|tỷ|triệu|tỉ)?\s*sức mạnh", step_lower)
        if match:
            raw_num = match.group(1).replace(",", "").replace(".", "")
            unit = match.group(2) if match.group(2) else ""
            try:
                num = int(raw_num)
                if unit in ("tỷ", "tỉ"):
                    power_needed = num * 1_000_000_000
                elif unit in ("tr", "triệu"):
                    power_needed = num * 1_000_000
                else:
                    power_needed = num
                return ("power", power_needed)
            except ValueError:
                pass
        
        # Fallback: check "sức mạnh" + số
        if "sức mạnh" in step_lower:
            nums = re.findall(r"(\d+)", step_lower)
            for num_str in nums:
                num = int(num_str)
                if num >= 10000:
                    return ("power", num)
        
        return None

    async def _handle_stat_task(self, stat_type: str, required_value: int):
        """Xử lý task yêu cầu đạt chỉ số (sức mạnh, HP, etc)"""
        username = self.account.username
        char = self.account.char
        
        self.current_status_msg = f"Cần {stat_type} >= {required_value:,}"
        
        if stat_type == "power":
            current_power = char.c_power or 0
            logger.info(f"[{username}] [AutoQuest] Sức mạnh hiện tại: {current_power:,}, cần: {required_value:,}")
            
            if current_power >= required_value:
                self.current_status_msg = f"Đã đủ sức mạnh ({current_power:,}/{required_value:,})"
                # Dừng auto MSM nếu đang chạy trước khi trigger
                if self._auto_msm and self._auto_msm.is_running:
                    self._auto_msm.stop()
                # Server tự động hoàn thành task... nhưng nếu chưa, ra Nappa đánh 1 con để trigger
                await asyncio.sleep(2)
                # Kiểm tra xem task đã chuyển chưa
                task_now = self.account.char.task
                if task_now and task_now.sub_names and task_now.index < len(task_now.sub_names):
                    cur_step = task_now.sub_names[task_now.index]
                    # Nếu vẫn ở bước stat cũ, đánh 1 con quái ở Nappa (map 68) để trigger
                    if self._check_stat_task(cur_step):
                        logger.info(f"[{username}] [AutoQuest] Đủ sức mạnh nhưng task chưa chuyển. Ra Nappa đánh quái trigger...")
                        self.current_status_msg = "Trigger task: ra Nappa đánh quái"
                        # Đi tới map 68 (Nappa) có quái nappa (TID 39)
                        if char.map_id != 68:
                            if not self.account.controller.xmap.is_xmapping:
                                await self.account.controller.xmap.start(68)
                            await asyncio.sleep(2)
                            return
                        # Đã ở map 68, bật auto_play đánh 1 con quái nappa (TID 39)
                        ctrl = self.account.controller
                        ctrl.auto_play.target_mobs.clear()
                        ctrl.auto_play.target_mobs.add(39)  # nappa TID
                        if not ctrl.auto_play.interval:
                            ctrl.toggle_autoplay(True)
                        await asyncio.sleep(5)
                        # Tắt auto_play sau khi đánh 1 con
                        ctrl.toggle_autoplay(False)
                        return
                # Nếu task đã chuyển hoặc không còn stat nữa, ok
                await asyncio.sleep(0.2)
                return
            
            # Chưa đủ sức mạnh → thử dùng auto MSM
            self.current_status_msg = f"Tăng sức mạnh ({current_power:,} -> {required_value:,})"
            self.state = AutoQuestState.HANDLE_STAT
            logger.info(f"[{username}] [AutoQuest] Chưa đủ sức mạnh, kích hoạt auto MSM...")
            
            # Sử dụng auto MSM có sẵn (tự động nâng sức mạnh)
            from logic.auto_msm import AutoMsm
            if self._auto_msm is None:
                self._auto_msm = AutoMsm(self.account.controller)
            
            # Bật auto MSM
            if not self._auto_msm.is_running:
                self._auto_msm.start()
            
            # Chờ và kiểm tra định kỳ
            await asyncio.sleep(10)
            return
        
        await asyncio.sleep(5)

    # ── Helper: Get Nearest Valid Mob ───────────────────────────

    def _get_nearest_valid_mob(self, target_mob_id: int):
        """Tìm quái hợp lệ gần nhất"""
        mobs = self.account.controller.mobs
        char = self.account.char
        best = None
        best_dist = float('inf')
        now = time.time()
        for mid, mob in mobs.items():
            if mob.template_id != target_mob_id or mob.hp <= 0 or mob.status <= 1:
                continue
            if mid in self.blacklist_mobs and now < self.blacklist_mobs[mid]:
                continue
            d = math.hypot(mob.x - char.cx, mob.y - char.cy)
            if d < best_dist:
                best_dist = d
                best = mob
        return best

    # ── Start / Stop ────────────────────────────────────────────

    async def start(self):
        if self.is_running:
            return
        self.config_data = self._load_config()
        self._load_map_names()
        self.is_running = True
        self.state = AutoQuestState.ANALYZE_TASK
        self._boss_map_id = None
        self._boss_step_index = -1
        self._boss_skip = False
        self.start_time = time.time()
        self.current_status_msg = "Khởi động..."
        logger.info(f"[{self.account.username}] [AutoQuest] BẬT tự động làm nhiệm vụ chính.")
        self.task = asyncio.create_task(self._quest_loop())

    async def stop(self):
        if not self.is_running:
            return
        self.is_running = False
        self.state = AutoQuestState.IDLE
        self.current_status_msg = "Đã tắt"
        logger.info(f"[{self.account.username}] [AutoQuest] TẮT tự động làm nhiệm vụ chính.")
        
        # Tắt auto_play, auto_attack và auto MSM
        controller = self.account.controller
        if controller.auto_play.interval:
            controller.toggle_autoplay(False)
        if controller.auto_attack and controller.auto_attack.is_running:
            controller.toggle_auto_attack(False)
        if self._auto_msm and self._auto_msm.is_running:
            self._auto_msm.stop()
        
        # Clear mob target
        self._mob_target_info = None
        
        if self.task and not self.task.done():
            self.task.cancel()

    def get_status(self):
        if not self.is_running:
            return "Đang tắt"
        state_name = self.state.value if hasattr(self.state, 'value') else str(self.state)
        msg = getattr(self, 'current_status_msg', "Không rõ")
        return f"{state_name}: {msg}"

    def get_stats(self) -> dict:
        elapsed = 0
        if self.start_time:
            elapsed = int(time.time() - self.start_time)
        hours = elapsed // 3600
        minutes = (elapsed % 3600) // 60
        seconds = elapsed % 60
        if hours > 0:
            time_str = f"{hours}h{minutes:02d}m{seconds:02d}s"
        elif minutes > 0:
            time_str = f"{minutes}m{seconds:02d}s"
        else:
            time_str = f"{seconds}s"
        return {
            "quests_completed": self.quests_completed,
            "total_kills": self.total_kills,
            "time_str": time_str,
        }

    # ── Main Loop ───────────────────────────────────────────────

    async def _quest_loop(self):
        """Vòng lặp chính"""
        while self.is_running:
            try:
                if not self.account.is_logged_in:
                    await asyncio.sleep(0.2)
                    continue
                
                char = self.account.char
                if not char:
                    await asyncio.sleep(0.2)
                    continue
                
                task = char.task
                if not task:
                    await asyncio.sleep(0.2)
                    continue
                
                # Nếu task index vượt quá số sub_names, đã hoàn thành task này
                if task.index >= len(task.sub_names):
                    self.current_status_msg = "Đã hoàn tất nhiệm vụ chính!"
                    await asyncio.sleep(5)
                    continue
                
                # Chết → hồi sinh
                if char.c_hp == 0 and getattr(char, 'statusMe', 0) == 14:
                    logger.info(f"[{self.account.username}] [AutoQuest] Nhân vật chết. Hồi sinh...")
                    await self.account.service.return_town_from_dead()
                    await asyncio.sleep(3)
                    continue
                
                # Phân tích và xử lý task
                await self._analyze_task()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[{self.account.username}] [AutoQuest] Lỗi: {e}", exc_info=True)
                await asyncio.sleep(2)
        
        logger.info(f"[{self.account.username}] [AutoQuest] Vòng lặp kết thúc.")
