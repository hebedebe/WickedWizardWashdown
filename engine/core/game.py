from .singleton import singleton

import pygame
import moderngl
import time

class Game:
    def __init__(self, width=1280, height=720, title="OpenGL Game"):
        pygame.init()
        pygame.display.set_mode((width, height), pygame.OPENGL | pygame.DOUBLEBUF | pygame.RESIZABLE)
        pygame.display.set_caption(title)

        self.ctx = moderngl.create_context()
        self.ctx.enable(moderngl.BLEND)
        self.ctx.blend_func = (moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA)

        self.clock = pygame.time.Clock()
        self.running = True

        self.width = width
        self.height = height

        self.last_time = time.time()
        self.delta_time = 0.0

        self.init()

    def init(self):
        """Override this method to set up shaders, VAOs, resources, etc."""
        pass

    def handle_event(self, event):
        """Override this for event handling"""
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.VIDEORESIZE:
            self.width, self.height = event.size
            pygame.display.set_mode((self.width, self.height), pygame.OPENGL | pygame.DOUBLEBUF | pygame.RESIZABLE)
            self.ctx.viewport = (0, 0, self.width, self.height)

    def update(self, dt):
        """Override this to update your game logic"""
        pass

    def render(self):
        """Override this to render the frame"""
        self.ctx.clear(0.1, 0.1, 0.1, 1.0)

    def run(self):
        while self.running:
            now = time.time()
            self.delta_time = now - self.last_time
            self.last_time = now

            for event in pygame.event.get():
                self.handle_event(event)

            self.update(self.delta_time)
            self.render()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
