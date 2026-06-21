# manages the quiz state, including current question, score, and answer tracking
class ScoreManager:
    def __init__(self):
        self.score = 0
        self.correct_answers = 0
        self.wrong_answers = 0

    def add_correct_answer(self):
        self.correct_answers += 1
        self.score += 10

    def add_wrong_answer(self):
        self.wrong_answers += 1

    def get_score(self):
        return self.score

    def get_correct_answers(self):
        return self.correct_answers

    def get_wrong_answers(self):
        return self.wrong_answers