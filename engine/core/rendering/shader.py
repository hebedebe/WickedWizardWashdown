class Shader:
    def __init__(self, ctx, vertex_src, fragment_src, name="unnamed"):
        self.name = name
        self.program = ctx.program(vertex_shader=vertex_src, fragment_shader=fragment_src)

    def set_uniform(self, name, value):
        if name in self.program:
            self.program[name].value = value
        else:
            raise KeyError(f"Uniform '{name}' not found in shader '{self.name}'")
