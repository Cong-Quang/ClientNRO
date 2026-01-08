"""
Auto Chat Plugin - Tự động chat khi login và hỗ trợ combo chat
"""
from plugins.base_plugin import BasePlugin
import asyncio


class AutoChatPlugin(BasePlugin):
    """Plugin tự động chat khi login và hỗ trợ chat combo"""
    
    def __init__(self):
        super().__init__()
        self.name = "AutoChatPlugin"
        self.version = "1.0.0"
        self.author = "ClientNRO Team"
        self.description = "Tự động chat khi login và hỗ trợ chat combo"
        
        # Cấu hình
        self.enabled_chat = True
        self.login_message = "Binh đoàn da xanh"  # Tin nhắn khi login
        
        # Chat combo - danh sách tin nhắn sẽ chat liên tiếp
        self.chat_combo = [
            "Binh đoàn da xanh",
            "Con C",
            "Da Xanh",
        ]
        self.combo_delay = 1.0  # Delay giữa các tin nhắn (giây)
        self.use_combo = False  # Bật/tắt combo mode
        self._tasks = []
        self._tasks = []
    
    def on_enable(self) -> None:
        """Called when plugin is enabled"""
        super().on_enable()
        
        import json
        import os
        
        # Define default config path and data
        config_path = "config/auto_chat.json"
        
        # ... (Config loading logic maintained implicitly if I don't touch it, but wait, I'm replacing a chunk)
        # To avoid re-writing the whole config logic which is long, I should split the edits.
        # But wait, self._tasks init needs to be in __init__.
        # So I will do multiple chunks.

    # Chunk 1: Update __init__ to include self._tasks
    # Chunk 2: Update on_disable to cancel tasks
    # Chunk 3: Update on_account_login to track tasks
    # Chunk 4: Update _chat_task to fix logic
    
    def on_enable(self) -> None:
        """Called when plugin is enabled"""
        super().on_enable()
        
        import json
        import os
        
        # Define default config path and data
        config_path = "config/auto_chat.json"
        default_config = {
            "enabled": True,
            "login_message": "Binh đoàn da xanh",
            "use_combo": False,
            "combo_delay": 1.0,
            "loop_chat": False,
            "loop_delay": 5.0,
            "combo_messages": [
                "Binh đoàn da xanh",
                "Con C",
                "Da Xanh"
            ]
        }
        
        # Ensure config directory exists
        os.makedirs("config", exist_ok=True)
        
        # Check if config file exists, if not create it
        if not os.path.exists(config_path):
            try:
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=4, ensure_ascii=False)
                self.api.log_info(f"Created default config file at: {config_path}")
            except Exception as e:
                self.api.log_error(f"Failed to create config file: {e}")
        
        # Force load from this specific file
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
                
            # Update plugin attributes
            self.enabled_chat = loaded_config.get('enabled', True)
            self.login_message = loaded_config.get('login_message', default_config['login_message'])
            self.use_combo = loaded_config.get('use_combo', False)
            self.combo_delay = loaded_config.get('combo_delay', 1.0)
            self.loop_chat = loaded_config.get('loop_chat', False)
            self.loop_delay = loaded_config.get('loop_delay', 5.0)
            self.chat_combo = loaded_config.get('combo_messages', default_config['combo_messages'])
            
            self.api.log_info(f"Loaded config from: {config_path}")
            
        except Exception as e:
            self.api.log_error(f"Error loading config from {config_path}: {e}")
            # Fallback to defaults (already set in __init__)
        
        self.api.log_info("=" * 60)
        self.api.log_info("Auto Chat Plugin enabled!")
        self.api.log_info(f"   Mode: {'Combo' if self.use_combo else 'Single'}")
        if self.use_combo:
            self.api.log_info(f"   Combo messages: {len(self.chat_combo)} messages")
            self.api.log_info(f"   Delay: {self.combo_delay}s")
        else:
            self.api.log_info(f"   Message: '{self.login_message}'")
        
        if self.loop_chat:
             self.api.log_info(f"   Loop: Enabled (Delay {self.loop_delay}s)")
        
        self.api.log_info("=" * 60)

        # Trigger cho các account đang online ngay lập tức
        online_accounts = self.api.get_online_accounts()
        if online_accounts:
            self.api.log_info(f"Triggering chat for {len(online_accounts)} online accounts...")
            for acc in online_accounts:
                self.on_account_login(acc)
    
    def on_disable(self) -> None:
        """Called when plugin is disabled"""
        if self.api:
            self.api.log_info("Auto Chat Plugin disabled!")
        
        # Cancel all background tasks
        for task in self._tasks:
            if not task.done():
                task.cancel()
        self._tasks = []
        
        super().on_disable()
    
    def on_account_login(self, account) -> None:
        """Called when an account logs in - Tự động chat"""
        if not self.enabled_chat:
            return
        
        # Schedule the chat task to run in the background without blocking
        # Schedule the chat task to run in the background without blocking
        task = asyncio.create_task(self._chat_task(account))
        self._tasks.append(task)
        # Remove task from list when done
        task.add_done_callback(lambda t: self._tasks.remove(t) if t in self._tasks else None)
    
    async def _chat_task(self, account) -> None:
        """Async task to handle chatting with delays"""
        try:
            # Initial critical delay
            # If triggered by reload (already online), 2s is enough.
            await asyncio.sleep(2.0)
            
            if not self.api: # Safety check if plugin disabled/unloaded
                return

            if not hasattr(account, 'service') or not account.service:
                if self.api:
                    self.api.log_warning(f"Aborting auto chat: Account {account.username} has no service")
                return

            while True:  # Chat Loop
                if not account.is_logged_in:
                    break

                if self.use_combo:
                    # Combo mode
                    for i, message in enumerate(self.chat_combo, 1):
                        # Fix: use is_logged_in instead of is_connected()
                        if not account.is_logged_in: 
                             break
                             
                        try:
                            await account.service.send_chat(message)
                            if self.api:
                                self.api.log_info(f"[{account.username}] Combo {i}/{len(self.chat_combo)}: '{message}'")
                        except Exception as e:
                            if self.api:
                                self.api.log_error(f"Error sending combo message {i}: {e}")
                        
                        if i < len(self.chat_combo):
                            await asyncio.sleep(self.combo_delay)
                else:
                    # Single mode
                    try:
                        await account.service.send_chat(self.login_message)
                        if self.api:
                            self.api.log_info(f"[{account.username}] Chat: '{self.login_message}'")
                    except Exception as e:
                        if self.api:
                            self.api.log_error(f"Error sending chat: {e}")
                
                # Check loop condition
                if not self.loop_chat:
                    break
                    
                # Delay provided before next loop iteration
                await asyncio.sleep(self.loop_delay)
                    
        except asyncio.CancelledError:
            pass # Task cancelled normally
        except Exception as e:
            if self.api:
                self.api.log_error(f"Error in auto chat task for {account.username}: {e}")


# ============================================================
# HƯỚNG DẪN SỬ DỤNG
# ============================================================
#
# 1. SINGLE MODE (mặc định):
#    - Plugin sẽ chat "hello" khi login
#    - Để thay đổi tin nhắn, sửa self.login_message
#
# 2. COMBO MODE:
#    - Set self.use_combo = True
#    - Sửa self.chat_combo để thêm/bớt tin nhắn
#    - Sửa self.combo_delay để thay đổi delay giữa các tin nhắn
#
# 3. CONFIG FILE (Tự động sinh ra):
#    Plugin sẽ tự tạo file: config/auto_chat.json
#    Bạn hãy mở file đó để chỉnh sửa:
#    {
#        "enabled": true,
#        "login_message": "Binh đoàn da xanh",
#        "use_combo": false,
#        "combo_delay": 1.0,
#        "combo_messages": [...]
#    }
#    Sau khi sửa xong, chạy `config reload` hoặc `plugin reload auto_chat` để cập nhật.
#
# 4. TẮT PLUGIN:
#    - Set self.enabled_chat = False
#    - Hoặc xóa file plugin khỏi user_plugins/
#
# ============================================================
