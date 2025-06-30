import pygame
from typing import Any

class UIEvent:
    """UI event data structure."""
    
    def __init__(self, event_type: str, widget: 'Widget', data: Any = None):
        self.type = event_type
        self.widget = widget
        self.data = data