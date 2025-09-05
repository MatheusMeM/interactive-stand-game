# app/audio_manager.py
from kivy.core.audio import SoundLoader

class AudioManager:
    """Handles loading and playing all sound effects."""
    def __init__(self, sounds_path="assets/sounds/"):
        self.sounds = {}
        self.sound_files = {
            'start': 'start.wav',
            'correct': 'correct.wav',
            'wrong': 'wrong.wav',
            'submit': 'submit.wav'
        }
        
        for key, filename in self.sound_files.items():
            try:
                sound = SoundLoader.load(f"{sounds_path}{filename}")
                if sound:
                    self.sounds[key] = sound
                else:
                    print(f"Warning: Could not load sound '{filename}'.")
            except Exception as e:
                print(f"Error loading sound '{filename}': {e}")
        
        print(f"AudioManager initialized. Loaded {len(self.sounds)} sounds.")

    def play(self, sound_key):
        """Plays a pre-loaded sound by its key."""
        if sound_key in self.sounds:
            self.sounds[sound_key].play()
        else:
            print(f"Warning: Sound key '{sound_key}' not found.")