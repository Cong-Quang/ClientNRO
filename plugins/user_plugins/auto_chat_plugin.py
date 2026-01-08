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
        self.login_message = "hello"  # Tin nhắn khi login
        
        # Chat combo - danh sách tin nhắn sẽ chat liên tiếp
        self.chat_combo = [
            "hello",
            "chào mọi người",
            "mình mới vào",
        ]
        self.combo_delay = 2.0  # Delay giữa các tin nhắn (giây)
        self.use_combo = False  # Bật/tắt combo mode
    
    def on_enable(self) -> None:
        """Called when plugin is enabled"""
        super().on_enable()
        
        # Load config từ config system
        self.enabled_chat = self.api.get_config('auto_chat.enabled', True)
        self.login_message = self.api.get_config('auto_chat.login_message', 'hello')
        self.use_combo = self.api.get_config('auto_chat.use_combo', False)
        self.combo_delay = self.api.get_config('auto_chat.combo_delay', 2.0)
        
        # Load combo messages từ config
        combo_from_config = self.api.get_config('auto_chat.combo_messages', None)
        if combo_from_config:
            self.chat_combo = combo_from_config
        
        self.api.log_info("=" * 60)
        self.api.log_info("💬 Auto Chat Plugin enabled!")
        self.api.log_info(f"   Mode: {'Combo' if self.use_combo else 'Single'}")
        if self.use_combo:
            self.api.log_info(f"   Combo messages: {len(self.chat_combo)} messages")
            self.api.log_info(f"   Delay: {self.combo_delay}s")
        else:
            self.api.log_info(f"   Message: '{self.login_message}'")
        self.api.log_info("=" * 60)

        # Trigger cho các account đang online ngay lập tức
        online_accounts = self.api.get_online_accounts()
        if online_accounts:
            self.api.log_info(f"🔄 Triggering chat for {len(online_accounts)} online accounts...")
            for acc in online_accounts:
                self.on_account_login(acc)
    
    def on_disable(self) -> None:
        """Called when plugin is disabled"""
        self.api.log_info("💬 Auto Chat Plugin disabled!")
        super().on_disable()
    
    def on_account_login(self, account) -> None:
        """Called when an account logs in - Tự động chat"""
        if not self.enabled_chat:
            return
        
        # Schedule the chat task to run in the background without blocking
        asyncio.create_task(self._chat_task(account))
    
    async def _chat_task(self, account) -> None:
        """Async task to handle chatting with delays"""
        try:
            # Initial critical delay to ensure character is fully loaded in map
            # 5 seconds is safer than 1s for "login -> enter map" transition
            await asyncio.sleep(5.0)
            
            if not hasattr(account, 'service') or not account.service:
                self.api.log_warning(f"Aborting auto chat: Account {account.username} has no service")
                return

            if self.use_combo:
                # Combo mode
                for i, message in enumerate(self.chat_combo, 1):
                    if not account.is_connected(): # Check connection
                         break
                         
                    try:
                        await account.service.send_chat(message)
                        self.api.log_info(f"💬 [{account.username}] Combo {i}/{len(self.chat_combo)}: '{message}'")
                    except Exception as e:
                        self.api.log_error(f"Error sending combo message {i}: {e}")
                    
                    if i < len(self.chat_combo):
                        await asyncio.sleep(self.combo_delay)
            else:
                # Single mode
                try:
                    await account.service.send_chat(self.login_message)
                    self.api.log_info(f"💬 [{account.username}] Chat: '{self.login_message}'")
                except Exception as e:
                    self.api.log_error(f"Error sending chat: {e}")
                    
        except Exception as e:
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
# 3. CONFIG VIA JSON (nếu dùng config/settings.json):
#    Thêm vào config:
#    {
#      "auto_chat": {
#        "enabled": true,
#        "login_message": "hello",
#        "use_combo": false,
#        "combo_delay": 2.0,
#        "combo_messages": [
#          "hello",
#          "chào mọi người",
#          "mình mới vào"
#        ]
#      }
#    }
#
# 4. TẮT PLUGIN:
#    - Set self.enabled_chat = False
#    - Hoặc xóa file plugin khỏi user_plugins/
#
# ============================================================
