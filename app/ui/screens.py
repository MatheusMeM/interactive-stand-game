from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.properties import StringProperty

# Create a custom widget for a single leaderboard entry
class LeaderboardEntry(BoxLayout):
    rank_text = StringProperty('')
    name_text = StringProperty('')
    score_text = StringProperty('')

class WelcomeScreen(Screen):
    pass

class InstructionsScreen(Screen):
    pass

class AgilityGameScreen(Screen):
    pass

class QuizGameScreen(Screen):
    def display_question(self, question_data):
        """Populates the screen widgets with the question and options."""
        self.ids.question_label.text = question_data['question']
        options = question_data['options']
        self.ids.option_1.text = options[0]
        self.ids.option_2.text = options[1]
        self.ids.option_3.text = options[2]
        self.ids.option_4.text = options[3]
        self.ids.feedback_label.text = "" # Clear previous feedback

class ScoreScreen(Screen):
    pass

class LeaderboardScreen(Screen):
    def update_leaderboard(self, scores, player_name=None):
        """Clears and rebuilds the leaderboard display."""
        grid = self.ids.leaderboard_grid
        grid.clear_widgets()

        # Sort scores descending
        sorted_scores = sorted(scores, key=lambda x: x['score'], reverse=True)
        
        # Add header
        grid.add_widget(Label(text='Rank', bold=True))
        grid.add_widget(Label(text='Name', bold=True))
        grid.add_widget(Label(text='Score', bold=True))

        # Add top scores
        for i, entry in enumerate(sorted_scores[:15]):
            is_player = player_name and entry.get('name') == player_name
            
            rank_label = Label(text=str(i + 1))
            name_label = Label(text=entry.get('name', 'N/A'))
            score_label = Label(text=str(entry.get('score', 0)))

            if is_player:
                # Highlight the current player's entry
                rank_label.color = (0, 1, 0, 1) # Green
                name_label.color = (0, 1, 0, 1)
                score_label.color = (0, 1, 0, 1)

            grid.add_widget(rank_label)
            grid.add_widget(name_label)
            grid.add_widget(score_label)