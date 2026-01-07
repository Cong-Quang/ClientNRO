"""
Controller module - Tái cấu trúc từ controller.py
Tách message handlers thành các module riêng biệt để dễ bảo trì.
"""
from .controller import Controller

__all__ = ['Controller']
