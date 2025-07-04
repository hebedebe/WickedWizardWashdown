#version 330
in vec2 v_texcoord;
out vec4 fragColor;
uniform sampler2D tex;
void main() {
    vec4 texColor = texture(tex, v_texcoord);
    fragColor = texColor * vec4(1.0, 1.0, 1.0, 1.0);
}