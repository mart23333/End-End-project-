# This file defines the LoginWindow class, which serves as the main entry point for users to log in and start the quiz or view the leaderboard.
from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QMessageBox
)

from database.database import add_user
from gui.quiz_window import QuizWindow
from gui.leaderboard_window import LeaderboardWindow
# The LoginWindow class provides a user interface for logging in, starting the quiz, and accessing the leaderboard

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Quiz Knight - Login")
        self.setGeometry(300, 200, 420, 280)

        self.quiz_window = None
        self.leaderboard_window = None

        self.title_label = QLabel("Quiz Knight")
        self.title_label.setStyleSheet("font-size: 30px; font-weight: bold; color: #a78bfa;")

        self.subtitle_label = QLabel(" Quiz  Generator  from text, PDFs, DOCX files, and novel chapters.")

        self.username_label = QLabel("Enter Username:")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Example: Mar")

        self.start_button = QPushButton("Start Quiz")
        self.start_button.clicked.connect(self.start_quiz)

        self.leaderboard_button = QPushButton("View Leaderboard")
        self.leaderboard_button.clicked.connect(self.open_leaderboard)

        layout = QVBoxLayout()
        layout.addWidget(self.title_label)
        layout.addWidget(self.subtitle_label)
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.start_button)
        layout.addWidget(self.leaderboard_button)

        self.setLayout(layout)
# Start the quiz by validating the username, adding the user to the database, and opening the QuizWindow
    def start_quiz(self):
        username = self.username_input.text().strip()

        if not username:
            QMessageBox.warning(self, "Invalid Username", "Please enter a username.")
            return

        add_user(username)

        self.quiz_window = QuizWindow(username)
        self.quiz_window.showMaximized()
        self.close()
# Open the leaderboard by creating an instance of LeaderboardWindow and displaying it
    def open_leaderboard(self):
        self.leaderboard_window = LeaderboardWindow()
        self.leaderboard_window.show()