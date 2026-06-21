
# This file defines the LeaderboardWindow class, which displays the quiz leaderboard using PyQt6.
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QPushButton
)

from database.database import get_leaderboard

# The LeaderboardWindow class displays the quiz leaderboard, showing top users and their scores
class LeaderboardWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Quiz Knight - Leaderboard")
        self.setGeometry(350, 220, 650, 450)

        self.login_window = None

        self.title_label = QLabel("Quiz Knight Leaderboard")
        self.title_label.setStyleSheet(
            "font-size: 24px; font-weight: bold; color: #f5f3ff;"
        )

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "Username",
            "High Score",
            "Games Played",
            "Total Score"
        ])

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.load_leaderboard)

        self.back_button = QPushButton("Back to Main Menu")
        self.back_button.clicked.connect(self.back_to_main_menu)

        layout = QVBoxLayout()
        layout.addWidget(self.title_label)
        layout.addWidget(self.table)
        layout.addWidget(self.refresh_button)
        layout.addWidget(self.back_button)

        self.setLayout(layout)

        self.load_leaderboard()
# Load the leaderboard data from the database and populate the table widget
    def load_leaderboard(self):
        leaderboard = get_leaderboard()

        self.table.setRowCount(len(leaderboard))

        for row_index, row_data in enumerate(leaderboard):
            username, high_score, games_played, total_score = row_data

            self.table.setItem(row_index, 0, QTableWidgetItem(str(username)))
            self.table.setItem(row_index, 1, QTableWidgetItem(str(high_score)))
            self.table.setItem(row_index, 2, QTableWidgetItem(str(games_played)))
            self.table.setItem(row_index, 3, QTableWidgetItem(str(total_score)))

        self.table.resizeColumnsToContents()
# Navigate back to the main menu by opening the LoginWindow and closing the current leaderboard window
    def back_to_main_menu(self):
        from gui.login_window import LoginWindow

        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()