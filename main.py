import sys

from PyQt6.QtWidgets import QApplication

from database.database import create_tables
from gui.login_window import LoginWindow
from gui.styles import DARK_THEME

# Main function to initialize the database, set up the application, and display the login window for the Quiz Knight application
def main():
    create_tables()

    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_THEME)

    window = LoginWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()