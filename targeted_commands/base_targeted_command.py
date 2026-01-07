from abc import ABC, abstractmethod
from typing import Any
from account import Account

class TargetedCommand(ABC):
    @abstractmethod
    async def execute(self, account: Account, *args, **kwargs) -> Any:
        pass
