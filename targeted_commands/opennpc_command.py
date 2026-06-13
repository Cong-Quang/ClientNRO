import asyncio
from targeted_commands.base_targeted_command import TargetedCommand
from logs.logger_config import TerminalColors as C, logger

class OpenNpcCommand(TargetedCommand):
    async def execute(self, account, *args, **kwargs):
        parts = kwargs.get('parts', [])
        if len(parts) < 2:
            print(f"[{account.username}] Sử dụng: opennpc <id_npc> [index1] [index2]...")
            return
            
        controller = account.controller
        try:
            npc_id = int(parts[1])
            
            # Smart lookup for target NPC
            target_npc = None
            # Try 1: Treat as 1-based index (printed ID from findnpc)
            idx_1based = npc_id - 1
            if idx_1based in controller.npcs:
                target_npc = controller.npcs[idx_1based]
            
            # Try 2: Treat as template ID
            if not target_npc:
                for n_idx, npc_data in controller.npcs.items():
                    if npc_data.get('template_id') == npc_id:
                        target_npc = npc_data
                        break
                        
            if not target_npc:
                print(f"[{controller.account.username}] Không tìm thấy NPC {npc_id} trong map hiện tại.")
                return
                
            npc_template_id = target_npc.get('template_id')
            npc_name = target_npc.get('name', f"NPC {npc_template_id}")
            print(f"[{account.username}] Đang tương tác {npc_name} (Template ID: {npc_template_id})...")
            
            # Teleport slightly above the NPC
            await controller.movement.teleport_to(target_npc['x'], target_npc['y'] - 3)
            
            controller.ui_menu_event.clear()
            await controller.account.service.open_menu_npc(npc_template_id)
            
            try:
                await asyncio.wait_for(controller.ui_menu_event.wait(), timeout=2.0)
                options = controller.last_ui_options
                
                # Nếu chỉ mở để xem
                if len(parts) == 2:
                    print(f"\n+-- [MENU {npc_name}] ---------------------------------")
                    for i, opt in enumerate(options):
                        clean_opt = opt.replace('\n', ' ').strip()
                        print(f"  [{i}] {clean_opt}")
                    print(f"---------------------------------------------------\n")
                
                # Nếu truyền thêm index để bấm
                else:
                    for arg in parts[2:]:
                        idx = int(arg)
                        controller.ui_menu_event.clear()
                        await controller.account.service.confirm_menu_npc(npc_template_id, idx)
                        print(f"[{controller.account.username}] Đã chọn menu index: {idx}")
                        
                        # Đợi menu tiếp theo nếu có nhiều tham số
                        if arg != parts[-1]:
                            try:
                                await asyncio.wait_for(controller.ui_menu_event.wait(), timeout=2.0)
                            except asyncio.TimeoutError:
                                break
                            
            except asyncio.TimeoutError:
                print(f"[{controller.account.username}] Timeout: Không nhận được menu từ {npc_name}.")
                
        except ValueError:
            print(f"[{controller.account.username}] Lỗi cú pháp. ID/Index phải là số.")
        except Exception as e:
            logger.error(f"Lỗi lệnh opennpc: {e}")
