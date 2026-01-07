"""
Base Handler - Class cơ sở cho tất cả message handlers
"""
from network.message import Message
from logs.logger_config import logger


class BaseHandler:
    """Base class cho tất cả message handlers.
    
    Cung cấp access đến controller và các thuộc tính thường dùng.
    """
    
    def __init__(self, controller):
        """Khởi tạo handler với controller reference.
        
        Args:
            controller: Controller instance chứa state và services
        """
        self.controller = controller
        self.account = controller.account
        
    def handle(self, msg: Message):
        """Xử lý message - phải được override bởi subclass.
        
        Args:
            msg: Message object cần xử lý
            
        Raises:
            NotImplementedError: Nếu subclass không implement method này
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement handle() method")
