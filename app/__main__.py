import os

# --- CRITICAL FIX FOR RASPBERRY PI AUDIO HANG ---
# This must be set BEFORE any kivy modules are imported.
# It forces Kivy's underlying SDL2 library to use the ALSA audio driver,
# preventing an auto-detection hang.
os.environ['SDL_AUDIODRIVER'] = 'alsa'
# --- END OF FIX ---

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager

from app.ui.screens import (WelcomeScreen, InstructionsScreen, AgilityGameScreen,
                            QuizGameScreen, ScoreScreen, LeaderboardScreen)
from app.game_manager import GameManager

class GameApp(App):
    """The main Kivy application class."""
    def build(self):
        # Load the KV file that defines our screen layouts
        Builder.load_file('app/ui/screens.kv')

        # Create the screen manager
        sm = ScreenManager()
        sm.add_widget(WelcomeScreen(name='welcome'))
        sm.add_widget(InstructionsScreen(name='instructions'))
        sm.add_widget(AgilityGameScreen(name='agility_game'))
        sm.add_widget(QuizGameScreen(name='quiz_game'))
        sm.add_widget(ScoreScreen(name='score'))
        sm.add_widget(LeaderboardScreen(name='leaderboard'))
        
        # Instantiate the GameManager and pass it the screen manager
        self.game_manager = GameManager(sm)
        
        return sm

    def on_stop(self):
        """This method is called when the application is closed."""
        print("Application is closing. Cleaning up resources.")
        self.game_manager.cleanup()

if __name__ == '__main__':
    GameApp().run()