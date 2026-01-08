from typing import Optional
from model.game_objects import Task

class QuestMapper:
    """Helper class giúp map nhiệm vụ sang Boss tương ứng"""
    
    # Từ khóa trong task detail/name -> Tên Boss
    # Cần cập nhật thêm dựa trên thực tế game
    KEYWORD_TO_BOSS = {
        "số 4": "Số 4",
        "số 3": "Số 3",
        "số 2": "Số 2",
        "số 1": "Số 1",
        "tiểu đội sát thủ": "Tiểu đội sát thủ", 
        "fide 1": "Fide 1",
        "fide 2": "Fide 2",
        "fide 3": "Fide 3",
        "fide": "Fide",
        "kuku": "Kuku",
        "mập đầu đinh": "Mập đầu đinh",
        "rambo": "Rambo",
    }

    @staticmethod
    def get_boss_from_task(task: Task) -> Optional[str]:
        """
        Phân tích nhiệm vụ và trả về tên Boss cần săn.
        Trả về None nếu không tìm thấy hoặc nhiệm vụ không yêu cầu boss.
        """
        if not task:
            return None
            
        # 1. Check sub_names (name of current step)
        if task.index < len(task.sub_names):
            current_step = task.sub_names[task.index].lower()
            for keyword, boss_name in QuestMapper.KEYWORD_TO_BOSS.items():
                if keyword in current_step:
                    return boss_name.strip()

        # 2. Check task detail
        detail_lower = task.detail.lower()
        for keyword, boss_name in QuestMapper.KEYWORD_TO_BOSS.items():
            if keyword in detail_lower:
                return boss_name.strip()

        # 3. Check task name (least specific)
        name_lower = task.name.lower()
        for keyword, boss_name in QuestMapper.KEYWORD_TO_BOSS.items():
            if keyword in name_lower:
                return boss_name.strip()
        
        return None
