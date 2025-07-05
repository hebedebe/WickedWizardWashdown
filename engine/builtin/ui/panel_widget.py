import pygame
from engine.core.ui import UIElement

class Panel(UIElement):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def render(self, screen):
        super().render(screen)
        for child in self.children:
            child.render(screen)

    def handle_event(self, event):
        for child in self.children:
            child.handle_event(event)