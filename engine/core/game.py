#Library imports
import pygame
import moderngl
import time
import numpy as np

# Local imports
from .singleton import singleton
from .rendering.shader import Shader, DEFAULT_VERT, DEFAULT_FRAG

@singleton
class Game:
    def __init__(self, width=1280, height=720, title="OpenGL Game"):
        print("Initializing Game...")

        pygame.init()
        pygame.display.set_mode((width, height), pygame.OPENGL | pygame.DOUBLEBUF)
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

        self.scenes = {}
        self.current_scene = None
        self.scene_stack = []

        self.init_framebuffers()
        self.init_fullscreen_quad()
        self.shaders = {}
        self.postprocess_chain = []  # 🆕 List of Shader objects in order
        
        self.buffer = pygame.Surface((width, height), pygame.SRCALPHA)

        self.init_default_shader()  # Initialize the default shader

#region OpenGL

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
        shader = Shader(vert, frag, name)
        self.shaders[name] = shader
        return shader
    
    def init_default_shader(self):
        self.load_shader('default', DEFAULT_VERT, DEFAULT_FRAG)

        self.add_postprocess_shader(self.get_shader('default'))  # Add default shader to post-process chain

    def add_postprocess_shader(self, shader: Shader):
        if shader in self.postprocess_chain:
            print(f"Prevented duplicate shader addition of shader '{shader.name}'.")
            return
        self.postprocess_chain.append(shader)

    def remove_postprocess_shader(self, shader: Shader):
        """Remove a shader from the post-process chain."""
        if shader in self.postprocess_chain:
            self.postprocess_chain.remove(shader)
        else:
            print(f"Shader '{shader.name}' not found in post-process chain.")

    def get_shader(self, name):
        return self.shaders.get(name)

#endregion

#region Scene Management
    def add_scene(self, scene):
        self.scenes[scene.name] = scene

    def remove_scene(self, scene_name):
        """Remove a scene by name."""
        if scene_name in self.scenes:
            del self.scenes[scene_name]
        else:
            raise ValueError(f"Scene '{scene_name}' not found.")

    def push_scene(self, scene_name):
        if self.current_scene:
            self.current_scene.on_pause()
        self.current_scene = self.scenes[scene_name]
        self.current_scene.on_enter()
        self.scene_stack.append(self.current_scene)

    def pop_scene(self):
        if not self.scene_stack:
            raise ValueError("No scenes to pop.")
        self.current_scene.on_exit()
        self.scene_stack.pop()
        if self.scene_stack:
            self.current_scene = self.scene_stack[-1]
            self.current_scene.on_resume()
        else:
            self.current_scene = None

    def load_scene(self, scene_name):
        self.scene_stack.clear()  # Clear stack before loading new scene
        if self.current_scene:
            self.current_scene.on_exit()
        self.current_scene = self.scenes[scene_name]
        self.current_scene.on_enter()

# endregion

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.VIDEORESIZE:
            self.width, self.height = event.size
            pygame.display.set_mode((self.width, self.height), pygame.OPENGL | pygame.DOUBLEBUF | pygame.RESIZABLE)
            self.ctx.viewport = (0, 0, self.width, self.height)
            self.init_framebuffers()
        elif self.current_scene:
            self.current_scene.handle_event(event)

    def update(self, dt):
        if self.current_scene:
            self.current_scene.update(dt)
            self.current_scene.phys_update(dt)
            self.current_scene.late_update(dt)

    def render_scene(self):
        self.current_scene.render() if self.current_scene else None

    def render(self):
        # 🧱 Step 1: Draw to scene framebuffer
        self.scene_fbo.use()
        self.buffer.fill((0, 0, 0, 255))  # Clear buffer with black
        self.render_scene()

        buffer_data = pygame.image.tobytes(self.buffer, 'RGBA', True)
        self.main_color.write(buffer_data)

        # 🧱 Step 2: Postprocess chain
        src_tex = self.main_color
        for i, _shader in enumerate(self.postprocess_chain):
            shader = _shader.get()
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
