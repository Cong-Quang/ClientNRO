import struct
from logs.logger_config import logger

class Reader:
    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0

    def read_byte(self) -> int:
        # logger.debug(f"Reading 1 byte (signed) at position {self.pos}")
        val = struct.unpack_from('>b', self.data, self.pos)[0]
        self.pos += 1
        return val

    def read_ubyte(self) -> int:
        # logger.debug(f"Reading 1 byte (unsigned) at position {self.pos}")
        val = struct.unpack_from('>B', self.data, self.pos)[0]
        self.pos += 1
        return val

    def read_short(self) -> int:
        # logger.debug(f"Reading 2 bytes (short) at position {self.pos}")
        val = struct.unpack_from('>h', self.data, self.pos)[0]
        self.pos += 2
        return val

    def read_ushort(self) -> int:
        # logger.debug(f"Reading 2 bytes (ushort) at position {self.pos}")
        val = struct.unpack_from('>H', self.data, self.pos)[0]
        self.pos += 2
        return val

    def read_int(self) -> int:
        # logger.debug(f"Reading 4 bytes (int) at position {self.pos}")
        val = struct.unpack_from('>i', self.data, self.pos)[0]
        self.pos += 4
        return val

    def read_int3(self) -> int:
        if self.pos + 3 > len(self.data):
            return 0
        val = (self.data[self.pos] << 16) | (self.data[self.pos + 1] << 8) | self.data[self.pos + 2]
        self.pos += 3
        return val

    def read_long(self) -> int:
        # logger.debug(f"Reading 8 bytes (long) at position {self.pos}")
        val = struct.unpack_from('>q', self.data, self.pos)[0]
        self.pos += 8
        return val

    def read_bool(self) -> bool:
        return self.read_byte() != 0

    def read_utf(self) -> str:
        length = self.read_ushort() # UTF length is an unsigned short
        # logger.debug(f"Reading UTF string of length {length} at position {self.pos}")
        if length + self.pos > len(self.data):
             # logger.warning(f"UTF read overrun: length {length} at pos {self.pos} exceeds buffer size {len(self.data)}")
             return ""
        val = self.data[self.pos : self.pos + length].decode('utf-8', errors='replace')
        self.pos += length
        return val

    def read_bytes(self, length: int) -> bytes:
        val = self.data[self.pos : self.pos + length]
        self.pos += length
        return val

    def available(self) -> int:
        return len(self.data) - self.pos

    def read_remaining(self) -> bytes:
        val = self.data[self.pos:]
        self.pos = len(self.data)
        return val
