from typing import Optional
from network.writer import Writer
from network.reader import Reader

class Message:
    def __init__(self, command: int, data: bytes = None):
        self.command = command
        self._writer = Writer()
        if data:
            self._reader = Reader(data)
        else:
            self._reader = None
        
        # If created with existing data, we assume it's for reading
        # If created without data, we assume it's for writing

    def writer(self) -> Writer:
        return self._writer

    def reader(self) -> Reader:
        if not self._reader:
            raise Exception("No data to read")
        return self._reader

    def get_data(self) -> bytes:
        return self._writer.get_data()

    def cleanup(self):
        pass
