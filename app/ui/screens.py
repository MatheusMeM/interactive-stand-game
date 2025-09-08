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
        Populates the screen widgets and resets their state for a new round.
        This is a command from the GameManager.
        """
        # Reset the dialog box to show the new question
        self.ids.question_label.text = question_data['question']
        
        options = question_data['options']
        answer_buttons = [self.ids.option_a, self.ids.option_b, self.ids.option_c, self.ids.option_d]
        
        # Prepare buttons for the new round
        for i, button in enumerate(answer_buttons):
            button.text = options[i]
            button.disabled = False
            # Reset button color to the default brand green using the ColorProperty
            button.button_color = (134/255, 188/255, 37/255, 1)

    def show_feedback(self, is_correct, correct_answer_text, selected_widget):
        """
        Executes the full feedback sequence based on the game logic's outcome.
        This method controls all visual and textual feedback on this screen.
        """
        # --- Textual Feedback ---
        if is_correct:
            self.ids.question_label.text = "Correto!"
        else:
            self.ids.question_label.text = f"Incorreto!\nA resposta correta era: {correct_answer_text}"

        # --- Visual Button Feedback ---
        answer_buttons = [self.ids.option_a, self.ids.option_b, self.ids.option_c, self.ids.option_d]
        
        for button in answer_buttons:
            # Rule 1: Disable all buttons after a choice is made to prevent multiple inputs.
            button.disabled = True
            
            if button.text == correct_answer_text:
                # Rule 2: The correct answer is always highlighted in green.
                button.button_color = (30/255, 180/255, 30/255, 1) # Feedback Green
            elif button == selected_widget:
                # Rule 3: If this is the selected widget AND it's wrong, it turns red.
                # (The `is_correct` check is implicitly handled by the first `if`).
                button.button_color = (200/255, 20/255, 20/255, 1) # Feedback Red
            else:
                # Rule 4: All other buttons become a neutral gray.
                button.button_color = (0.5, 0.5, 0.5, 1) # Disabled Gray

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