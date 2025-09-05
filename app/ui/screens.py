from kivy.uix.screenmanager import Screen

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
    pass