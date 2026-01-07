from abc import ABC, abstractmethod
from typing import Any

class Command(ABC):
    """The base class for all commands."""
    @abstractmethod
    async def execute(self, *args, **kwargs) -> Any:
        """
        Executes the command.
        
        Returns:
            Any: A result that the main loop can use. 
                 For example, a boolean to indicate exit, 
                 or another object for further processing.
        """
        pass
