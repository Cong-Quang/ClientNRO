import struct

class Writer:
    def __init__(self):
        self.buffer = bytearray()

    def write_byte(self, value: int):
        # sbyte in C# is -128 to 127
        self.buffer.extend(struct.pack('>b', value))

    def write_ubyte(self, value: int):
        # byte in C# is 0 to 255
        self.buffer.extend(struct.pack('>B', value))

    def write_short(self, value: int):
        self.buffer.extend(struct.pack('>h', value))

    def write_ushort(self, value: int):
        self.buffer.extend(struct.pack('>H', value))

    def write_int(self, value: int):
        self.buffer.extend(struct.pack('>i', value))

    def write_bool(self, value: bool):
        self.write_byte(1 if value else 0)

    def write_utf(self, value: str):
        encoded = value.encode('utf-8')
        length = len(encoded)
        self.write_short(length)
        self.buffer.extend(encoded)

    def get_data(self) -> bytes:
        return bytes(self.buffer)
