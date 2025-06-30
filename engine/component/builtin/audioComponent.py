from engine.component.component import Component

class AudioComponent(Component):
    """
    AudioComponent handles audio playback for actors.
    It can play sound effects and music tracks.
    """
    
    def __init__(self, sound_file: str):
        super().__init__()
        self.sound_file = sound_file
        self.is_playing = False

    def play(self):
        """Play the audio file."""
        if not self.is_playing:
            # Logic to play the sound file
            print(f"Playing sound: {self.sound_file}")
            self.is_playing = True

    def stop(self):
        """Stop the audio playback."""
        if self.is_playing:
            # Logic to stop the sound file
            print(f"Stopping sound: {self.sound_file}")
            self.is_playing = False