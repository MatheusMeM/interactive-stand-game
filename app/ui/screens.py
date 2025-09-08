from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import StringProperty, ColorProperty

# Create a custom widget for a single leaderboard entry
class LeaderboardEntry(BoxLayout):
    rank_text = StringProperty('')
    name_text = StringProperty('')
    score_text = StringProperty('')

# Custom button for quiz with controllable background color
class QuizButton(Button):
    button_bg_color = ColorProperty((216/255, 206/255, 205/255, 1))  # Default light gray

class WelcomeScreen(Screen):
    pass

class InstructionsScreen(Screen):
    def update_content(self, title, body, button_text):
        """Updates the text of the labels and button on the screen."""
        self.ids.title_label.text = title
        self.ids.body_label.text = body
        self.ids.action_button.text = button_text

class AgilityGameScreen(Screen):
    pass

class QuizGameScreen(Screen):
    def display_question(self, question_data):
        """
        Populates the screen widgets for a new round.
        Buttons are set to the new default light gray color.
        """
        self.ids.question_label.text = question_data['question']
        
        options = question_data['options']
        answer_buttons = [self.ids.option_a, self.ids.option_b, self.ids.option_c, self.ids.option_d]
        
        for i, button in enumerate(answer_buttons):
            button.text = options[i]
            button.disabled = False
            # --- NEW DEFAULT STATE: Light Gray ---
            # This color is defined in screens.kv as color_light_gray
            button.button_bg_color = (216/255, 206/255, 205/255, 1)

    def show_feedback(self, is_correct, correct_answer_text, selected_widget):
        """
        Executes the feedback sequence.
        All buttons turn dark gray after any selection is made.
        """
        if is_correct:
            self.ids.question_label.text = "Correto!"
        else:
            self.ids.question_label.text = f"Incorreto!\nA resposta correta era: {correct_answer_text}"

        answer_buttons = [self.ids.option_a, self.ids.option_b, self.ids.option_c, self.ids.option_d]
        
        for button in answer_buttons:
            # Rule 1: Disable all buttons post-interaction.
            button.disabled = True
            
            # --- NEW FEEDBACK STATE: All buttons become Dark Gray ---
            # This color is defined in screens.kv as color_dark_gray
            button.button_bg_color = (137/255, 137/255, 137/255, 1)

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
