
VERTEX_SHADER = """
#version 330
in vec2 position;
in vec2 texcoord;
out vec2 v_texcoord;
void main() {
    gl_Position = vec4(position, 0.0, 1.0);
    v_texcoord = texcoord;
}
"""

FRAGMENT_SHADER = """
#version 330
in vec2 v_texcoord;
out vec4 fragColor;
uniform sampler2D tex;
void main() {
    vec4 texColor = texture(tex, v_texcoord);
    fragColor = texColor * vec4(1.0, 0.5, 0.5, 1.0); // red tint
}
"""