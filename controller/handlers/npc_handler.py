"""
NPC Handler - Xử lý các message liên quan đến NPC
"""
import re
from network.message import Message
from logs.logger_config import logger, TerminalColors as C
from logic.auto_NVBoMong import BO_MONG_NPC_TEMPLATE_ID
from .base_handler import BaseHandler


class NPCHandler(BaseHandler):
    """Handler xử lý NPC chat, menu, add/remove."""
    
    def process_npc_chat(self, msg: Message):
        """Ghi log nội dung chat của NPC (NPC_CHAT)."""
        try:
            reader = msg.reader()
            npc_id = reader.read_short()
            message = reader.read_utf()
            
            bo_mong_template_id = 17
            npc_data = self.controller.npcs.get(npc_id)
            if npc_data and npc_data.get('template_id') == bo_mong_template_id:
                pass

        except Exception as e:
            logger.error(f"Lỗi khi phân tích NPC_CHAT: {e}")

    def process_npc_add_remove(self, msg: Message):
        """Xử lý lệnh thêm/bớt NPC (hiện chỉ đọc template id và không hành động thêm)."""
        try:
            reader = msg.reader()
            npc_template_id = reader.read_byte()
            pass
        except Exception as e:
            logger.error(f"Lỗi khi phân tích NPC_ADD_REMOVE: {e}")

    def process_open_ui_confirm(self, msg: Message):
        """Xử lý menu NPC (OPEN_UI_CONFIRM): đọc template id, nội dung menu và các lựa chọn."""
        try:
            reader = msg.reader()
            npc_template_id = reader.read_short()
            menu_chat = reader.read_utf()
            num_options = reader.read_byte()
            options = []
            for _ in range(num_options):
                options.append(reader.read_utf())

            # Common formatting for the chat content
            formatted_chat = re.sub(r'\|\d+\|', '\n- ', menu_chat)

            if self.account.last_opennpc_compact:
                # Compact mode for multi-account view
                summary = formatted_chat.replace('\n', ' ').strip()
                if summary.startswith('- '):
                    summary = summary[2:]
                if len(summary) > 50:
                    summary = summary[:47] + "..."
                
                # Create a single-line summary for options
                options_summary = ", ".join([f"[{i}]{opt.replace('\n', ' ').strip()}" for i, opt in enumerate(options)])
                if len(options_summary) > 60:
                     options_summary = options_summary[:57] + "..."

                print(f"[{C.YELLOW}{self.account.username:<10}{C.RESET}] {C.CYAN}NPC {npc_template_id:<3}{C.RESET} | {C.WHITE}{summary:<50}{C.RESET} | {C.GREEN}Options: {options_summary}{C.RESET}")
                self.account.last_opennpc_compact = False

            if npc_template_id == BO_MONG_NPC_TEMPLATE_ID:
                self.controller.auto_quest.parse_quest_info(menu_chat)
                
        except Exception as e:
            logger.error(f"Lỗi khi phân tích OPEN_UI_CONFIRM: {e}")
