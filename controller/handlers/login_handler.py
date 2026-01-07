"""
Login Handler - Xử lý các message liên quan đến login
"""
from network.message import Message
from logs.logger_config import logger
from .base_handler import BaseHandler


class LoginHandler(BaseHandler):
    """Handler xử lý NOT_LOGIN và NOT_MAP messages."""
    
    def message_not_login(self, msg: Message):
        """Xử lý các sub-command của NOT_LOGIN (ví dụ server list, login fail...)."""
        try:
            from cmd import Cmd
            reader = msg.reader()
            sub_cmd = reader.read_byte()
            logger.info(f"NOT_LOGIN subcmd: {sub_cmd}")

            if sub_cmd == 2:
                server_list_str = reader.read_utf()
                logger.info(f"Server list received: {server_list_str}")
                try:
                    servers = server_list_str.split(',')
                    parsed_servers = []
                    for s in servers:
                        parts = s.split(':')
                        if len(parts) >= 3:
                            parsed_servers.append({'name': parts[0], 'ip': parts[1], 'port': int(parts[2])})
                    if parsed_servers:
                        logger.info(f"Parsed servers: {parsed_servers}")
                    else:
                        logger.warning(f"Failed to parse server list: {server_list_str}")

                    if reader.available() > 0:
                        can_nap_tien = (reader.read_byte() == 1)
                        logger.info(f"Admin enabled: {can_nap_tien}")
                        if reader.available() > 0:
                            admin_link = reader.read_byte()
                            logger.info(f"Admin link flag: {admin_link}")
                except Exception as parse_e:
                    logger.warning(f"Error parsing server list: {parse_e}")

            elif sub_cmd == Cmd.LOGINFAIL:
                reason = reader.read_utf()
                logger.error(f"Login failed: {reason}")
            elif sub_cmd == Cmd.LOGIN_DE:
                logger.info("Login DE confirmed.")
            elif sub_cmd == Cmd.LOGIN:
                logger.info("Received NOT_LOGIN subcmd 0.")
            else:
                logger.info(f"Unhandled NOT_LOGIN subcmd: {sub_cmd}, payload={msg.get_data().hex()}")
        except Exception as e:
            logger.error(f"Error parsing NOT_LOGIN: {e}")
            import traceback
            traceback.print_exc()

    def message_not_map(self, msg: Message):
        """Xử lý NOT_MAP sub-commands (ví dụ: UPDATE_VERSION)."""
        try:
            import asyncio
            reader = msg.reader()
            sub_cmd = reader.read_byte()
            logger.info(f"NOT_MAP subcmd: {sub_cmd}")

            if sub_cmd == 4:
                vsData = reader.read_byte()
                vsMap = reader.read_byte()
                vsSkill = reader.read_byte()
                vsItem = reader.read_byte()
                logger.info(f"Server versions: data={vsData}, map={vsMap}, skill={vsSkill}, item={vsItem}")
                asyncio.create_task(self.account.service.client_ok())
                
            else:
                logger.info(f"Unhandled NOT_MAP subcmd: {sub_cmd}, payload={msg.get_data().hex()}")
        except Exception as e:
            logger.error(f"Error parsing NOT_MAP: {e}")
            import traceback
            traceback.print_exc()
