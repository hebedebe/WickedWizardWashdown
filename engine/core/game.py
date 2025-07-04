#Library imports
import pygame
import moderngl
import time
import numpy as np

# Local imports
from .rendering.shader import Shader

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

        self.shaders = {}
        self.postprocess_chain = []  # 🆕 List of Shader objects in order
        self.init_framebuffers()
        self.init_fullscreen_quad()

    def init_framebuffers(self):
        self.main_color = self.ctx.texture((self.width, self.height), components=4)
        self.main_depth = self.ctx.depth_renderbuffer((self.width, self.height))
        self.scene_fbo = self.ctx.framebuffer(color_attachments=[self.main_color], depth_attachment=self.main_depth)

        # 🆕 ping-pong FBOs for post-processing
        self.ping_tex = self.ctx.texture((self.width, self.height), components=4)
        self.pong_tex = self.ctx.texture((self.width, self.height), components=4)
        self.ping_fbo = self.ctx.framebuffer(color_attachments=[self.ping_tex])
        self.pong_fbo = self.ctx.framebuffer(color_attachments=[self.pong_tex])

    def init_fullscreen_quad(self):
        quad = np.array([
            -1.0, -1.0,
             1.0, -1.0,
            -1.0,  1.0,
            -1.0,  1.0,
             1.0, -1.0,
             1.0,  1.0,
        ], dtype='f4')
        self.quad_vbo = self.ctx.buffer(quad.tobytes())
        self.quad_vao_cache = {}  # 🆕 Cache VAOs per shader

    def get_quad_vao(self, shader):
        if shader.name not in self.quad_vao_cache:
            vao = self.ctx.simple_vertex_array(shader.program, self.quad_vbo, 'in_position')
            self.quad_vao_cache[shader.name] = vao
        return self.quad_vao_cache[shader.name]

    def load_shader(self, name, vert, frag):
        shader = Shader(self.ctx, vert, frag, name)
        self.shaders[name] = shader
        return shader

    def add_postprocess_shader(self, shader: Shader):
        self.postprocess_chain.append(shader)

    def get_shader(self, name):
        return self.shaders.get(name)

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.VIDEORESIZE:
            self.width, self.height = event.size
            pygame.display.set_mode((self.width, self.height), pygame.OPENGL | pygame.DOUBLEBUF | pygame.RESIZABLE)
            self.ctx.viewport = (0, 0, self.width, self.height)
            self.init_framebuffers()

    def update(self, dt):
        pass  # override

    def render_scene(self):
        pass  # override

    def render(self):
        # 🧱 Step 1: Draw to scene framebuffer
        self.scene_fbo.use()
        self.ctx.clear(0, 0, 0, 1)
        self.render_scene()

        # 🧱 Step 2: Postprocess chain
        src_tex = self.main_color
        for i, shader in enumerate(self.postprocess_chain):
            # Last shader outputs to screen
            if i == len(self.postprocess_chain) - 1:
                self.ctx.screen.use()
            else:
                dst_fbo = self.ping_fbo if i % 2 == 0 else self.pong_fbo
                dst_fbo.use()

            shader.program['screen_texture'].value = 0
            src_tex.use(location=0)

            vao = self.get_quad_vao(shader)
            vao.render()

            # Next input is current output
            src_tex = self.ping_tex if i % 2 == 0 else self.pong_tex

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
