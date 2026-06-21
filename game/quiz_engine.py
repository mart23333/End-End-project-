
from game.scoring import ScoreManager

# QuizEngine class managing the quiz flow
class QuizEngine:
    def __init__(self, questions):
        self.questions = questions
        self.current_index = 0
        self.score_manager = ScoreManager()
# Get the current question based on the current index, or return None if finished
    def get_current_question(self):
        if self.current_index < len(self.questions):
            return self.questions[self.current_index]

        return None
# Submit the user's answer and update the score accordingly, returning True if correct, False otherwise
    def submit_answer(self, selected_index):
        current_question = self.get_current_question()

        if current_question is None:
            return False

        correct_index = current_question["answer"]

        if selected_index == correct_index:
            self.score_manager.add_correct_answer()
            return True

        self.score_manager.add_wrong_answer()
        return False
# Move to the next question by incrementing the current index
    def move_next(self):
        self.current_index += 1
# Check if the quiz is finished by comparing the current index to the total number of questions
    def is_finished(self):
        return self.current_index >= len(self.questions)
# Get the current score from the score manager
    def get_score(self):
        return self.score_manager.get_score()
# Get the number of correct answers from the score manager
    def get_correct_answers(self):
        return self.score_manager.get_correct_answers()
# Get the number of wrong answers from the score manager
    def get_total_questions(self):
        return len(self.questions)
# Get the current question number
    def get_question_number(self):
        return self.current_index + 1