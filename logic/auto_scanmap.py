import asyncio
import json
import time
from logs.logger_config import logger

class AutoScanMap:
    def __init__(self, account):
        self.account = account
        self.is_running = False
        self.start_id = -1
        self.end_id = -1
        self.task = None

    async def start(self, start_id: int, end_id: int):
        if self.is_running:
            print("[ScanMap] Đang trong quá trình quét, vui lòng stop trước khi chạy mới.")
            return
        
        self.start_id = start_id
        self.end_id = end_id
        self.is_running = True
        print(f"[ScanMap] Bắt đầu quét từ map {start_id} đến {end_id}.")
        self.task = asyncio.create_task(self._scan_loop())

    async def stop(self):
        if not self.is_running:
            return
        self.is_running = False
        if self.task and not self.task.done():
            self.task.cancel()
        print("[ScanMap] Đã DỪNG quá trình quét map.")

    def _update_config(self, map_id, map_name, mobs):
        try:
            config = {"maps": []}
            try:
                with open('maps_config.json', 'r', encoding='utf-8') as f:
                    config = json.load(f)
            except Exception:
                pass
            
            # Xóa map cũ nếu có
            config['maps'] = [m for m in config.get('maps', []) if m.get('map_id') != map_id]
            
            # Thêm map mới
            mob_counts = {}
            for mob_id_key, mob in mobs.items():
                if hasattr(mob, 'template_id'):
                    mob_counts[mob.template_id] = mob_counts.get(mob.template_id, 0) + 1

            mob_list = []
            seen_ids = set()
            for mob_id_key, mob in mobs.items():
                if not hasattr(mob, 'template_id'): continue
                if mob.template_id not in seen_ids:
                    seen_ids.add(mob.template_id)
                    from main import MOB_NAMES # Lấy global dictionary
                    
                    # Ưu tiên lấy tên thật từ game object mob.name nếu có
                    mob_name = getattr(mob, 'name', '')
                    if not mob_name:
                        mob_name = MOB_NAMES.get(mob.template_id, f"Mob_{mob.template_id}")
                    
                    mob_list.append({
                        "mob_id": mob.template_id,
                        "mob_name": mob_name,
                        "count": mob_counts[mob.template_id]
                    })
            
            config['maps'].append({
                "map_id": map_id,
                "map_name": map_name,
                "mobs": mob_list
            })
            
            with open('maps_config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"[ScanMap] Lỗi khi cập nhật maps_config.json: {e}")

    async def _scan_loop(self):
        try:
            step = 1 if self.start_id <= self.end_id else -1
            for current_target in range(self.start_id, self.end_id + step, step):
                if not self.is_running:
                    break
                    
                print(f"\n[ScanMap] Đang di chuyển tới Map ID: {current_target}...")
                
                # Gọi xmap
                if hasattr(self.account.controller, 'xmap'):
                    await self.account.controller.xmap.start(current_target)
                else:
                    print("[ScanMap] Không tìm thấy XMap. Hủy bỏ quét.")
                    break
                
                # Chờ xmap hoàn thành (timeout 60s)
                timeout = 60
                elapsed = 0
                while self.account.controller.xmap.is_xmapping and elapsed < timeout and self.is_running:
                    await asyncio.sleep(0.2)
                    elapsed += 1
                    
                if not self.is_running:
                    break
                    
                if self.account.char.map_id != current_target:
                    print(f"[ScanMap] Lỗi hoặc kẹt đường khi tới Map {current_target}. Bỏ qua!")
                    continue
                    
                # Đã tới nơi, chờ quái load
                print(f"[ScanMap] Đã tới Map {current_target}. Chờ load quái...")
                await asyncio.sleep(3)
                
                # Quét và lưu
                map_info = self.account.controller.map_info
                map_name = map_info.get('name', f"Map_{current_target}") if isinstance(map_info, dict) else getattr(map_info, 'name', f"Map_{current_target}")
                mobs = self.account.controller.mobs
                
                self._update_config(current_target, map_name, mobs)
                print(f"[ScanMap] Đã thêm {len(mobs)} quái vào maps_config.json cho Map: {map_name} ({current_target})")
                
                await asyncio.sleep(0.2)
                
            print("\n[ScanMap] Đã hoàn thành quá trình quét map!")
            self.is_running = False
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"[ScanMap] Lỗi loop: {e}")
            self.is_running = False
