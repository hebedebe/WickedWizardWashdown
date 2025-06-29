from engine import Scene

class MultiplayerSelectScene(Scene):
    """Multiplayer selection scene where players can join or create lobbies."""

    def __init__(self):
        super().__init__("MultiplayerSelectScene")