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
            logger.info(f"Connecting to {host}:{port}...")
            self.reader, self.writer = await asyncio.open_connection(host, port)
            self.connected = True
            logger.info("Connected!")
            
            # Start listening loop
            asyncio.create_task(self.listen())
            
            # In C#, it sends a Message(-27) immediately after connect?
            # Session_ME.cs: doSendMessage(new Message(-27));
            # Note: This message likely triggers the key exchange from the server?
            # Or the server sends the key first?
            # Looking at Session_ME.cs: 
            # "doConnect... connecting = false; doSendMessage(new Message(-27));"
            # It seems the client initiates the handshake packet.
            
            msg = Message(-27)
            await self.send_message(msg)

        except Exception as e:
            logger.error(f"Connection failed: {e}")
            self.connected = False

    async def send_message(self, msg: Message):
        if not self.writer:
            return

        command = msg.command
        payload = msg.get_data()
        
        logger.debug(f"Preparing MSG: {command}, Payload Len: {len(payload)}")
        
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

        # HEX LOGGING
        logger.debug(f"SEND [Encrypted={self.get_key_complete}][W_Index={self.cur_w}]: {buffer.hex()}")

        self.writer.write(buffer)
        await self.writer.drain()
        logger.info(f"Sent Message: {command}, Length: {length} bytes")

    async def listen(self):
        logger.info("Listening for messages...")
        while self.connected:
            try:
                # Read Command
                cmd_raw = await self.reader.readexactly(1)
                cmd = struct.unpack('>b', cmd_raw)[0]
                
                # Debug RAW
                logger.debug(f"RECV BYTE (CMD): {cmd_raw.hex()}")

                if self.get_key_complete:
                    cmd = self.read_key(cmd)
                    if cmd > 127: cmd -= 256
                
                logger.debug(f"Decrypted CMD: {cmd}")

                # Read Length
                length = 0
                if cmd in [-32, -66, 11, -67, -74, -87, 66]:
                    logger.debug("Reading Big Packet Length...")
                    if self.get_key_complete:
                        b1_raw = await self.reader.readexactly(1)
                        b1_u = self.read_key(struct.unpack('B', b1_raw)[0])
                        b1 = (b1_u - 256 if b1_u > 127 else b1_u) + 128
                        logger.debug(f"Len Byte 1: {b1_u} -> {b1}")
                        
                        b2_raw = await self.reader.readexactly(1)
                        b2_u = self.read_key(struct.unpack('B', b2_raw)[0])
                        b2 = (b2_u - 256 if b2_u > 127 else b2_u) + 128
                        logger.debug(f"Len Byte 2: {b2_u} -> {b2}")
                        
                        b3_raw = await self.reader.readexactly(1)
                        b3_u = self.read_key(struct.unpack('B', b3_raw)[0])
                        b3 = (b3_u - 256 if b3_u > 127 else b3_u) + 128
                        logger.debug(f"Len Byte 3: {b3_u} -> {b3}")
                        
                        length = (b3 * 65536) + (b2 * 256) + b1
                    else:
                        pass 
                    logger.debug(f"Big Packet Length: {length}")
                elif self.get_key_complete:
                    b1_raw = await self.reader.readexactly(1)
                    b2_raw = await self.reader.readexactly(1)
                    b1 = self.read_key(struct.unpack('B', b1_raw)[0])
                    b2 = self.read_key(struct.unpack('B', b2_raw)[0])
                    length = ((b1 & 0xFF) << 8) | (b2 & 0xFF)
                else:
                    len_raw = await self.reader.readexactly(2)
                    length = struct.unpack('>H', len_raw)[0]

                # Read Payload
                if length > 0:
                    logger.debug(f"Reading Payload of size {length}...")
                    payload_raw = await self.reader.readexactly(length)
                    logger.debug("Payload read complete.")
                    if self.get_key_complete:
                        decrypted = bytearray()
                        for b in payload_raw:
                            decrypted.append(self.read_key(b))
                        payload = bytes(decrypted)
                    else:
                        payload = payload_raw
                else:
                    payload = b""

                logger.debug(f"RECV MSG (Raw): {cmd}, Len: {length}, Payload: {payload_raw.hex()}")
                
                msg = Message(cmd, payload)
                await self.on_message(msg)

            except asyncio.IncompleteReadError:
                logger.error("Connection closed by server (IncompleteReadError).")
                self.connected = False
                break
            except Exception as e:
                logger.error(f"Error in listen loop: {e}")
                import traceback
                traceback.print_exc()
                self.connected = False
                break

    async def on_message(self, msg: Message):
        # Filter noise/resource commands
        if msg.command in [Cmd.GET_IMG_BY_NAME, Cmd.GET_IMAGE_SOURCE]:
            logger.debug(f"Ignored Resource Message: {msg.command}, Length: {len(msg.get_data())}")
            return

        logger.info(f"Received Message: {msg.command}")
        
        if msg.command == Cmd.GET_SESSION_ID: # -27
            self.process_key_message(msg)
        elif self.controller:
            self.controller.on_message(msg)
        else:
            # Handle other messages
            pass

    def process_key_message(self, msg: Message):
        try:
            reader = msg.reader()
            key_len = reader.read_byte() 
            self.key = bytearray(reader.read_bytes(key_len))
            
            # Key Derivation: key[i+1] ^= key[i]
            for i in range(len(self.key) - 1):
                self.key[i + 1] ^= self.key[i]
            
            self.get_key_complete = True
            logger.info("Key exchange complete. Encryption enabled.")

            # Read remaining handshake data (Session_ME.cs getKey)
            if reader.available() > 0:
                try:
                    ip2 = reader.read_utf()
                    port2 = reader.read_int()
                    is_connect2 = reader.read_bool()
                    logger.info(f"Handshake Extra Info - IP2: {ip2}, Port2: {port2}, Connect2: {is_connect2}")
                except Exception as e:
                    logger.warning(f"Could not read extra handshake info: {e}")
            else:
                logger.debug("No extra handshake info available.")

        except Exception as e:
            logger.error(f"Failed to process key: {e}")

    def read_key(self, b: int) -> int:
        # b is expected to be 0-255 (unsigned byte from wire)
        # key bytes are signed sbyte in C#, but here we treat as 0-255
        
        # C#: (sbyte)((array[num] & 0xFF) ^ (b & 0xFF))
        # Logic: XOR the byte with current key byte
        
        k = self.key[self.cur_r]
        result = (k & 0xFF) ^ (b & 0xFF)
        
        self.cur_r += 1
        if self.cur_r >= len(self.key):
            self.cur_r %= len(self.key)
            
        return result

    def write_key(self, b: int) -> int:
        # b can be signed or unsigned, we only care about bits
        k = self.key[self.cur_w]
        result = (k & 0xFF) ^ (b & 0xFF)
        
        self.cur_w += 1
        if self.cur_w >= len(self.key):
            self.cur_w %= len(self.key)
            
        return result
