import pygame
import time
from typing import Dict, List, Optional, Callable
from math import sin, cos, radians, degrees, log

from .rendering import *
from .actor.actor import Actor
from .component import *
from .input.inputManager import InputManager
from .resources.assetManager import AssetManager
from .scene import *
from .ui import *
from .logger import Logger, LogType


serialization_registry = {}

def register_serializer(type_, to_json, from_json):
    serialization_registry[type_] = (to_json, from_json)

### Default Serializers ###

register_serializer(
    pygame.Vector2,
    lambda v: [v.x, v.y],
    lambda data: pygame.Vector2(*data)
)

register_serializer(
    pygame.Rect,
    lambda r: [r.x, r.y, r.width, r.height],
    lambda data: pygame.Rect(*data)
)

register_serializer(
    pygame.Color,
    lambda c: [c.r, c.g, c.b, c.a],
    lambda data: pygame.Color(*data)
)