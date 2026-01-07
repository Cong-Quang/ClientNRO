from targeted_commands.base_targeted_command import TargetedCommand
from typing import Any
from core.account import Account
from logs.logger_config import TerminalColors
from main import MOB_NAMES

class FindmobCommand(TargetedCommand):
    def __init__(self):
        self.C = TerminalColors

    async def execute(self, account: Account, *args, **kwargs) -> Any:
        mobs = account.controller.mobs.values()
        if not mobs:
            print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Không có quái vật nào trên bản đồ.")
            return

        aggregated_mobs = {}
        for mob in mobs:
            # Bỏ qua pet của người chơi khác hoặc của chính mình
            if mob.is_mob_me:
                continue

            template_id = mob.template_id
            if template_id not in aggregated_mobs:
                aggregated_mobs[template_id] = {
                    # Lưu ý: 'mob_id' là index cục bộ của mob trong list của client.
                    # 'template_id' là ID mẫu của loại mob.
                    # Theo yêu cầu, cột 'ID' trong output sẽ hiển thị 'template_id'.
                    'mob_id': mob.mob_id, 
                    'template_id': template_id,
                    'hp': mob.hp,
                    'max_hp': mob.max_hp,
                    'status': mob.status,
                    'count': 0
                }
            aggregated_mobs[template_id]['count'] += 1

        if not aggregated_mobs:
            print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] Không có quái vật nào (chỉ có pet) trên bản đồ.")
            return

        print(f"[{self.C.YELLOW}{account.username}{self.C.RESET}] {self.C.CYAN}--- Danh sách quái vật trên bản đồ ---{self.C.RESET}")
        print(f"{self.C.PURPLE}{'ID':<5} | {'Tên':<15} | {'HP':<15} | {'Trạng thái':<10} | {'Số lượng':<5}{self.C.RESET}")
        print("-" * 70)

        for data in aggregated_mobs.values():
            status_map = {0: f"{self.C.RED}Đã chết{self.C.RESET}", 1: f"{self.C.YELLOW}Hấp hối{self.C.RESET}"}
            status_text = status_map.get(data['status'], f"{self.C.GREEN}Sống{self.C.RESET}")
            
            hp_text = f"{data['hp']}/{data['max_hp']}"
            
            # Lấy tên từ Mob object (đại diện bằng mob_id đầu tiên tìm được)
            mob_name = MOB_NAMES.get(data['template_id'])
            if not mob_name:
                mob_obj = account.controller.mobs.get(data['mob_id'])
                mob_name = mob_obj.name if mob_obj and mob_obj.name else f"{data['template_id']}"
            
            print(f"{data['template_id']:<5} | {mob_name:<15} | {hp_text:<15} | {status_text:<18} | {data['count']:<5}")
        return True, "OK"
