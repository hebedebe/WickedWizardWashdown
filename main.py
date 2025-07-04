from engine.core.game import Game


POST_VERT = """
#version 330

in vec2 in_position;
out vec2 uv;

void main() {
    // Convert from clip space [-1, 1] to UV space [0, 1]
    uv = (in_position + 1.0) * 0.5;
    gl_Position = vec4(in_position, 0.0, 1.0);
}
"""

POST_FRAG = """
#version 330
in vec2 uv;
out vec4 fragColor;
uniform sampler2D screen_texture;
void main() {
    vec3 col = texture(screen_texture, uv).rgb;
    float gray = dot(col, vec3(0.299, 0.587, 0.114));
    
    // Use the grayscale value
    fragColor = vec4(gray, gray, gray, 1.0);
    fragColor = vec4(1.0, col.g, 0.0, 1.0);
    // Or use the original texture color
    //fragColor = texture(screen_texture, uv);
}
"""

def main():
    """Run main"""
    game = Game(1280, 720)

    shader = game.load_shader("postprocess", POST_VERT, POST_FRAG)
    game.add_postprocess_shader(shader)

    game.run()

if __name__ == "__main__":
    main()
