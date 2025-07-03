import pygame

DEFAULT_FPS = 1/24

class Frame:
    def __init__(self):
        self.surface: pygame.Surface = None
        self.frame_time = DEFAULT_FPS
        self.timer=0

class Animation:
    def __init__(self):
        self.frames: Frame = []