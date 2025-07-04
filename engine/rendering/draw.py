# util for tasks that would have been easy in pygame but need more boilerplate in opengl

import pygame
import moderngl
import numpy as np

from ..game.game import Game

def surface_to_texture(ctx, surface):
    width, height = surface.get_size()
    data = pygame.image.tobytes(surface, "RGB", True)  # Flip vertically
    texture = ctx.texture((width, height), 3, data)
    texture.build_mipmaps()
    return texture