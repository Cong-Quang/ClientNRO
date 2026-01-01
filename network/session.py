import asyncio
import struct
import logging
from typing import Optional
from network.message import Message
from config import Config
from cmd import Cmd

logger = logging.getLogger(__name__)

class Session:
    def __init__(self, controller=None):
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None
        self.connected = False
        self.key: Optional[bytearray] = None
        self.cur_r = 0
        self.cur_w = 0
        self.get_key_complete = False
        self.controller = controller

    async def connect(self, host: str, port: int):
        try:
            logger.info(f"Đang kết nối tới {host}:{port}...")
            self.reader, self.writer = await asyncio.open_connection(host, port)
            self.connected = True
            logger.info("Đã kết nối!")
            
            # Bắt đầu vòng lặp lắng nghe và trả về task để quản lý
            listen_task = asyncio.create_task(self.listen())
            
            msg = Message(-27)
            await self.send_message(msg)
            return listen_task

        except Exception as e:
            logger.error(f"Kết nối thất bại: {e}")
            self.connected = False
        return None

    def disconnect(self):
        """Closes the connection."""
        self.connected = False
        if self.writer:
            try:
                self.writer.close()
            except Exception as e:
                logger.error(f"Lỗi khi đóng writer: {e}")
        logger.info("Đã ngắt kết nối.")


    async def send_message(self, msg: Message):
        if not self.writer:
            return

        command = msg.command
        payload = msg.get_data()
        
        logger.debug(f"Đang chuẩn bị MSG: {command}, Độ dài Payload: {len(payload)}")
        
        buffer = bytearray()

        if self.get_key_complete:
            buffer.append(self.write_key(command))
        else:
            buffer.extend(struct.pack('>b', command))

        length = len(payload)
        
        if self.get_key_complete:
            buffer.append(self.write_key((length >> 8) & 0xFF))
            buffer.append(self.write_key(length & 0xFF))
            for b in payload:
                buffer.append(self.write_key(b))
        else:
            buffer.extend(struct.pack('>H', length))
            buffer.extend(payload)

        # GHI NHẬT KÝ HEX
        logger.debug(f"GỬI [Mã hóa={self.get_key_complete}][Chỉ mục_W={self.cur_w}]: {buffer.hex()}")

        self.writer.write(buffer)
        await self.writer.drain()
        logger.info(f"Đã gửi tin nhắn: {command}, Độ dài: {length} bytes")

    async def listen(self):
        logger.info("Đang lắng nghe tin nhắn...")
        while self.connected:
            try:
                # Đọc lệnh (Command)
                cmd_raw = await self.reader.readexactly(1)
                cmd_unsigned = cmd_raw[0]

                # Gỡ lỗi dữ liệu thô (RAW)
                logger.debug(f"NHẬN BYTE (CMD): {cmd_raw.hex()}")

                if self.get_key_complete:
                    cmd_unsigned = self.read_key(cmd_unsigned)
                
                # Chuyển đổi byte không dấu cuối cùng thành ID lệnh có dấu
                cmd = cmd_unsigned - 256 if cmd_unsigned > 127 else cmd_unsigned

                logger.debug(f"Lệnh sau khi giải mã (Decrypted CMD): {cmd}")

                # Đọc độ dài (Length)
                length = 0
                if cmd in [-32, -66, 11, -67, -74, -87, 66]:
                    logger.debug("Đang đọc độ dài gói tin lớn (Big Packet)...")
                    if self.get_key_complete:
                        b1_raw = await self.reader.readexactly(1)
                        b1_u = self.read_key(struct.unpack('B', b1_raw)[0])
                        b1 = (b1_u - 256 if b1_u > 127 else b1_u) + 128
                        logger.debug(f"Độ dài Byte 1: {b1_u} -> {b1}")
                        
                        b2_raw = await self.reader.readexactly(1)
                        b2_u = self.read_key(struct.unpack('B', b2_raw)[0])
                        b2 = (b2_u - 256 if b2_u > 127 else b2_u) + 128
                        logger.debug(f"Độ dài Byte 2: {b2_u} -> {b2}")
                        
                        b3_raw = await self.reader.readexactly(1)
                        b3_u = self.read_key(struct.unpack('B', b3_raw)[0])
                        b3 = (b3_u - 256 if b3_u > 127 else b3_u) + 128
                        logger.debug(f"Độ dài Byte 3: {b3_u} -> {b3}")
                        
                        length = (b3 * 65536) + (b2 * 256) + b1
                    else:
                        pass 
                    logger.debug(f"Độ dài gói tin lớn: {length}")
                elif self.get_key_complete:
                    b1_raw = await self.reader.readexactly(1)
                    b2_raw = await self.reader.readexactly(1)
                    b1 = self.read_key(struct.unpack('B', b1_raw)[0])
                    b2 = self.read_key(struct.unpack('B', b2_raw)[0])
                    length = ((b1 & 0xFF) << 8) | (b2 & 0xFF)
                else:
                    len_raw = await self.reader.readexactly(2)
                    length = struct.unpack('>H', len_raw)[0]

                # Đọc dữ liệu tải (Payload)
                if length > 0:
                    logger.debug(f"Đang đọc Payload kích thước {length}...")
                    payload_raw = await self.reader.readexactly(length)
                    logger.debug("Đã đọc xong Payload.")
                    if self.get_key_complete:
                        decrypted = bytearray()
                        for b in payload_raw:
                            decrypted.append(self.read_key(b))
                        payload = bytes(decrypted)
                    else:
                        payload = payload_raw
                else:
                    payload = b""

                logger.debug(f"NHẬN MSG (Thô): {cmd}, Dài: {length}, Payload: {payload_raw.hex()}")
                
                msg = Message(cmd, payload)
                await self.on_message(msg)

            except asyncio.IncompleteReadError:
                acc_name = "Unknown"
                if self.controller and hasattr(self.controller, 'account') and hasattr(self.controller.account, 'username'):
                    acc_name = self.controller.account.username
                logger.error(f"[{acc_name}] Kết nối đã bị đóng bởi máy chủ (IncompleteReadError).")
                self.connected = False
                break
            except Exception as e:
                logger.error(f"Lỗi trong vòng lặp lắng nghe: {e}")
                import traceback
                traceback.print_exc()
                self.connected = False
                break

    async def on_message(self, msg: Message):
        # Lọc các lệnh tài nguyên/nhiễu
        if msg.command in [Cmd.GET_IMG_BY_NAME, Cmd.GET_IMAGE_SOURCE]:
            logger.debug(f"Đã bỏ qua tin nhắn tài nguyên: {msg.command}, Độ dài: {len(msg.get_data())}")
            return

        logger.info(f"Đã nhận tin nhắn: {msg.command}")
        
        if msg.command == Cmd.GET_SESSION_ID: # -27
            self.process_key_message(msg)
        elif self.controller:
            self.controller.on_message(msg)
        else:
            # Xử lý các tin nhắn khác
            pass

    def process_key_message(self, msg: Message):
        try:
            reader = msg.reader()
            key_len = reader.read_byte() 
            self.key = bytearray(reader.read_bytes(key_len))
            
            # Tính toán Khóa (Key Derivation): key[i+1] ^= key[i]
            for i in range(len(self.key) - 1):
                self.key[i + 1] ^= self.key[i]
            
            self.get_key_complete = True
            logger.info("Hoàn tất trao đổi khóa. Đã kích hoạt mã hóa.")

            # Đọc dữ liệu bắt tay còn lại (Session_ME.cs getKey)
            if reader.available() > 0:
                try:
                    ip2 = reader.read_utf()
                    port2 = reader.read_int()
                    is_connect2 = reader.read_bool()
                    logger.info(f"Thông tin bổ sung bắt tay - IP2: {ip2}, Cổng2: {port2}, Kết nối2: {is_connect2}")
                except Exception as e:
                    logger.warning(f"Không thể đọc thông tin bổ sung bắt tay: {e}")
            else:
                logger.debug("Không có thông tin bổ sung bắt tay.")

        except Exception as e:
            logger.error(f"Xử lý khóa thất bại: {e}")

    def read_key(self, b: int) -> int:
        # b được mong đợi là từ 0-255 (unsigned byte nhận từ mạng)
        # các byte khóa là signed sbyte trong C#, nhưng ở đây chúng ta xử lý như 0-255
        
        # C#: (sbyte)((array[num] & 0xFF) ^ (b & 0xFF))
        # Logic: XOR byte hiện tại với byte khóa hiện tại
        
        k = self.key[self.cur_r]
        result = (k & 0xFF) ^ (b & 0xFF)
        
        self.cur_r += 1
        if self.cur_r >= len(self.key):
            self.cur_r %= len(self.key)
            
        return result

    def write_key(self, b: int) -> int:
        # b có thể là có dấu hoặc không dấu, chúng ta chỉ quan tâm đến các bit
        k = self.key[self.cur_w]
        result = (k & 0xFF) ^ (b & 0xFF)
        
        self.cur_w += 1
        if self.cur_w >= len(self.key):
            self.cur_w %= len(self.key)
            
        return result