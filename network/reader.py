import struct

class Reader:
    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0

    def read_byte(self) -> int:
        val = struct.unpack_from('>b', self.data, self.pos)[0]
        self.pos += 1
        return val

    def read_ubyte(self) -> int:
        val = struct.unpack_from('>B', self.data, self.pos)[0]
        self.pos += 1
        return val

    def read_short(self) -> int:
        val = struct.unpack_from('>h', self.data, self.pos)[0]
        self.pos += 2
        return val

    def read_ushort(self) -> int:
        val = struct.unpack_from('>H', self.data, self.pos)[0]
        self.pos += 2
        return val

    def read_int(self) -> int:
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
        val = struct.unpack_from('>q', self.data, self.pos)[0]
        self.pos += 8
        return val

    def read_bool(self) -> bool:
        return self.read_byte() != 0

    def read_utf(self) -> str:
        length = self.read_ushort() # UTF length is usually unsigned short
        if length + self.pos > len(self.data):
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