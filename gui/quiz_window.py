
# import required modules 
import os
import sqlite3
from datetime import datetime

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QPushButton,
    QComboBox,
    QSpinBox,
    QProgressBar,
    QFrame,
    QRadioButton,
    QButtonGroup,
    QMessageBox,
    QStackedWidget,
    QFileDialog,
    QScrollArea,
)

from nlp.question_generator import QuestionGenerator

# The QuizWindow class manages the main quiz interface, including question display, answer submission, timer, and results handling using PyQt6.
class QuizWindow(QWidget):
    def __init__(self, username="Student"):
        super().__init__()

        self.username = username
        self.question_generator = QuestionGenerator()

        self.questions = []
        self.current_index = 0
        self.answers = []
        self.submitted_answers = []
        self.score = 0
        self.time_left = 0
        self.score_saved = False

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)

        self.setWindowTitle(f"Quiz Knight - {self.username}")
        self.resize(1200, 750)

        self.setStyleSheet(self.get_stylesheet())

        self.stack = QStackedWidget()

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.stack)
        self.setLayout(main_layout)

        self.create_input_page()
        self.create_quiz_page()
        self.create_results_page()
        self.create_review_page()

        self.stack.setCurrentWidget(self.input_page)

  # function to return the CSS stylesheet for the application, defining styles for various UI elements  
    def create_input_page(self):
        self.input_page = QWidget()

        layout = QVBoxLayout()
        layout.setSpacing(16)

        title = QLabel("Quiz Knight")
        title.setObjectName("titleLabel")

        subtitle = QLabel(
            f"Welcome, {self.username}. Paste your study text or upload a file to generate exam-style questions."
        )
        subtitle.setObjectName("subtitleLabel")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        settings_layout = QHBoxLayout()

        mode_card = self.create_setting_card("Mode")
        self.mode_box = QComboBox()
        self.mode_box.addItems([
            "General / Article",
            "Science",
            "Business",
            "History",
            "Novel / Literature"
        ])
        mode_card.layout().addWidget(self.mode_box)

        question_card = self.create_setting_card("Questions")
        self.question_count = QSpinBox()
        self.question_count.setMinimum(1)
        self.question_count.setMaximum(30)
        self.question_count.setValue(5)
        question_card.layout().addWidget(self.question_count)

        timer_card = self.create_setting_card("Time Limit (minutes)")
        self.time_limit = QSpinBox()
        self.time_limit.setMinimum(1)
        self.time_limit.setMaximum(120)
        self.time_limit.setValue(5)
        timer_card.layout().addWidget(self.time_limit)

        settings_layout.addWidget(mode_card)
        settings_layout.addWidget(question_card)
        settings_layout.addWidget(timer_card)

        layout.addLayout(settings_layout)

        upload_layout = QHBoxLayout()

        self.upload_button = QPushButton("Upload TXT / PDF / DOCX")
        self.upload_button.clicked.connect(self.upload_file)

        self.clear_button = QPushButton("Clear Text")
        self.clear_button.clicked.connect(self.clear_text)

        upload_layout.addWidget(self.upload_button)
        upload_layout.addWidget(self.clear_button)

        layout.addLayout(upload_layout)

        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText(
            "Paste your article, textbook page, science text, business text, history text, or novel extract here..."
        )
        self.text_input.textChanged.connect(self.update_word_count)

        layout.addWidget(self.text_input)

        self.word_count_label = QLabel("Words: 0")
        self.word_count_label.setObjectName("smallLabel")

        layout.addWidget(self.word_count_label)

        self.generate_button = QPushButton("Generate Quiz")
        self.generate_button.setObjectName("primaryButton")
        self.generate_button.clicked.connect(self.start_quiz)

        layout.addWidget(self.generate_button)

        self.input_page.setLayout(layout)
        self.stack.addWidget(self.input_page)
# Helper function to create a styled card for settings, containing a title and a layout for input widgets
    def create_setting_card(self, title_text):
        card = QFrame()
        card.setObjectName("settingCard")

        layout = QVBoxLayout()

        label = QLabel(title_text)
        label.setObjectName("settingLabel")

        layout.addWidget(label)

        card.setLayout(layout)

        return card
# Update the word count label whenever the text in the input area changes, counting the number of words and displaying it to the user
    def update_word_count(self):
        text = self.text_input.toPlainText()
        words = len(text.split())
        self.word_count_label.setText(f"Words: {words}")

    def clear_text(self):
        self.text_input.clear()

    
    # function to handle file uploads
   

    def upload_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Upload Study File",
            "",
            "Supported Files (*.txt *.pdf *.docx);;Text Files (*.txt);;PDF Files (*.pdf);;Word Documents (*.docx)"
        )

        if not file_path:
            return

        try:
            extracted_text = self.extract_text_from_file(file_path)

            if not extracted_text.strip():
                QMessageBox.warning(
                    self,
                    "No Text Found",
                    "No readable text was found in this file. Please try another file."
                )
                return

            self.text_input.setPlainText(extracted_text)

            QMessageBox.information(
                self,
                "File Uploaded",
                "The file text has been loaded successfully."
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Upload Error",
                f"Could not read the file:\n{error}"
            )
# function to extract text from a file based on its extension, supporting TXT, PDF, and DOCX formats, and returning the extracted text as a string
    def extract_text_from_file(self, file_path):
        extension = os.path.splitext(file_path)[1].lower()

        if extension == ".txt":
            return self.extract_text_from_txt(file_path)

        if extension == ".pdf":
            return self.extract_text_from_pdf(file_path)

        if extension == ".docx":
            return self.extract_text_from_docx(file_path)

        raise ValueError("Unsupported file type. Please upload a TXT, PDF, or DOCX file.")
# helper function to extract text from a TXT file by reading its contents and returning it as a string
    def extract_text_from_txt(self, file_path):
        with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
            return file.read()

    def extract_text_from_pdf(self, file_path):
        import pdfplumber

        text = ""

        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()

                if page_text:
                    text += page_text + "\n"

        return text.strip()

    def extract_text_from_docx(self, file_path):
        from docx import Document

        document = Document(file_path)

        paragraphs = []

        for paragraph in document.paragraphs:
            if paragraph.text.strip():
                paragraphs.append(paragraph.text.strip())

        return "\n".join(paragraphs)

   
    # function to create the quiz page, which includes the question display, answer options, progress indicators, timer, and navigation buttons for submitting answers and moving to the next question
   
    def create_quiz_page(self):
        self.quiz_page = QWidget()

        layout = QVBoxLayout()
        layout.setSpacing(14)

        top_layout = QHBoxLayout()

        self.progress_label = QLabel("Question 1 of 1")
        self.progress_label.setObjectName("smallLabel")

        self.timer_label = QLabel("Time: 00:00")
        self.timer_label.setObjectName("timerLabel")

        top_layout.addWidget(self.progress_label)
        top_layout.addStretch()
        top_layout.addWidget(self.timer_label)

        layout.addLayout(top_layout)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)

        layout.addWidget(self.progress_bar)

        self.question_card = QFrame()
        self.question_card.setObjectName("questionCard")

        question_layout = QVBoxLayout()

        self.question_type_label = QLabel("")
        self.question_type_label.setObjectName("questionTypeLabel")

        self.question_label = QLabel("")
        self.question_label.setWordWrap(True)
        self.question_label.setObjectName("questionLabel")

        question_layout.addWidget(self.question_type_label)
        question_layout.addWidget(self.question_label)

        self.question_card.setLayout(question_layout)

        layout.addWidget(self.question_card)

        self.option_group = QButtonGroup()
        self.option_group.setExclusive(True)

        self.option_buttons = []
        self.option_frames = []

        for index in range(4):
            frame = QFrame()
            frame.setObjectName("optionFrame")

            frame_layout = QHBoxLayout()

            radio = QRadioButton("")
            radio.setObjectName("optionRadio")
            radio.clicked.connect(self.update_option_styles)

            self.option_group.addButton(radio, index)

            frame_layout.addWidget(radio)
            frame.setLayout(frame_layout)

            self.option_frames.append(frame)
            self.option_buttons.append(radio)

            layout.addWidget(frame)

        self.feedback_label = QLabel("")
        self.feedback_label.setWordWrap(True)
        self.feedback_label.setObjectName("feedbackLabel")
        self.feedback_label.hide()

        layout.addWidget(self.feedback_label)

        self.context_label = QLabel("")
        self.context_label.setWordWrap(True)
        self.context_label.setObjectName("contextLabel")
        self.context_label.hide()

        layout.addWidget(self.context_label)

        button_layout = QHBoxLayout()

        self.end_button = QPushButton("End Quiz")
        self.end_button.clicked.connect(self.confirm_end_quiz)

        self.submit_button = QPushButton("Submit Answer")
        self.submit_button.setObjectName("primaryButton")
        self.submit_button.clicked.connect(self.submit_answer)

        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.next_question)
        self.next_button.hide()

        button_layout.addWidget(self.end_button)
        button_layout.addStretch()
        button_layout.addWidget(self.submit_button)
        button_layout.addWidget(self.next_button)

        layout.addLayout(button_layout)

        self.quiz_page.setLayout(layout)
        self.stack.addWidget(self.quiz_page)

   
    # function to create the results page, which displays the user's final score, percentage, and options to review answers, view the leaderboard, or start a new quiz
   
    def create_results_page(self):
        self.results_page = QWidget()

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(18)

        self.result_title = QLabel("Quiz Complete")
        self.result_title.setObjectName("titleLabel")
        self.result_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.result_score_label = QLabel("")
        self.result_score_label.setObjectName("resultScoreLabel")
        self.result_score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.result_percent_label = QLabel("")
        self.result_percent_label.setObjectName("subtitleLabel")
        self.result_percent_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.review_button = QPushButton("Review Answers")
        self.review_button.clicked.connect(self.show_review_page)

        self.leaderboard_button = QPushButton("Show Leaderboard")
        self.leaderboard_button.clicked.connect(self.show_leaderboard)

        self.new_quiz_button = QPushButton("New Quiz")
        self.new_quiz_button.setObjectName("primaryButton")
        self.new_quiz_button.clicked.connect(self.reset_to_input)

        layout.addWidget(self.result_title)
        layout.addWidget(self.result_score_label)
        layout.addWidget(self.result_percent_label)
        layout.addWidget(self.review_button)
        layout.addWidget(self.leaderboard_button)
        layout.addWidget(self.new_quiz_button)

        self.results_page.setLayout(layout)
        self.stack.addWidget(self.results_page)

   
    # function to create the review page, which allows users to go through each question, see their selected answer, the correct answer, and explanations for each question, with navigation back to the results page
   
    def create_review_page(self):
        self.review_page = QWidget()

        layout = QVBoxLayout()

        title = QLabel("Answer Review")
        title.setObjectName("titleLabel")

        self.review_scroll = QScrollArea()
        self.review_scroll.setWidgetResizable(True)

        self.review_content = QWidget()

        self.review_content_layout = QVBoxLayout()
        self.review_content.setLayout(self.review_content_layout)

        self.review_scroll.setWidget(self.review_content)

        back_button = QPushButton("Back to Results")
        back_button.clicked.connect(lambda: self.stack.setCurrentWidget(self.results_page))

        layout.addWidget(title)
        layout.addWidget(self.review_scroll)
        layout.addWidget(back_button)

        self.review_page.setLayout(layout)
        self.stack.addWidget(self.review_page)

    
    # function to start the quiz by validating the input text, generating questions using the QuestionGenerator, initializing quiz state variables, and switching to the quiz page to display the first question
   
    def start_quiz(self):
        text = self.text_input.toPlainText().strip()

        if len(text.split()) < 30:
            QMessageBox.warning(
                self,
                "Text Too Short",
                "Please paste or upload a longer educational text before generating the quiz."
            )
            return

        number_of_questions = self.question_count.value()
        mode = self.mode_box.currentText()

        self.generate_button.setText("Generating questions...")
        self.generate_button.setEnabled(False)

        try:
            try:
                generated_questions = self.question_generator.generate_questions(
                    text,
                    number_of_questions=number_of_questions,
                    mode=mode
                )
            except TypeError:
                generated_questions = self.question_generator.generate_questions(
                    text,
                    number_of_questions,
                    mode
                )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Generation Error",
                f"Could not generate questions:\n{error}"
            )
            self.generate_button.setText("Generate Quiz")
            self.generate_button.setEnabled(True)
            return

        self.generate_button.setText("Generate Quiz")
        self.generate_button.setEnabled(True)

        if not generated_questions:
            QMessageBox.warning(
                self,
                "No Questions Generated",
                "The system could not generate enough questions from this text. Try a clearer or longer passage."
            )
            return

        self.questions = generated_questions
        self.current_index = 0
        self.answers = [None for _ in self.questions]
        self.submitted_answers = [False for _ in self.questions]
        self.score = 0
        self.score_saved = False

        self.time_left = self.time_limit.value() * 60
        self.timer.start(1000)

        self.stack.setCurrentWidget(self.quiz_page)
        self.show_question()

   
    # function to display the current question and answer options on the quiz page, updating progress indicators and resetting styles for a new question, and handling the end of the quiz when all questions have been answered
   
    def show_question(self):
        if self.current_index >= len(self.questions):
            self.finish_quiz()
            return

        question = self.questions[self.current_index]

        self.option_group.setExclusive(False)

        for button in self.option_buttons:
            button.setChecked(False)
            button.setEnabled(True)

        self.option_group.setExclusive(True)

        self.feedback_label.hide()
        self.context_label.hide()
        self.next_button.hide()

        self.submit_button.show()
        self.submit_button.setEnabled(True)

        question_number = self.current_index + 1
        total_questions = len(self.questions)

        self.progress_label.setText(f"Question {question_number} of {total_questions}")

        progress_value = int((self.current_index / total_questions) * 100)
        self.progress_bar.setValue(progress_value)

        self.question_type_label.setText(question.get("type", "Quiz Question"))
        self.question_label.setText(question.get("question", "Question missing"))

        options = question.get("options", [])

        for index, button in enumerate(self.option_buttons):
            if index < len(options):
                button.setText(options[index])
                button.show()
                self.option_frames[index].show()
            else:
                button.hide()
                self.option_frames[index].hide()

        self.reset_option_styles()

    def update_option_styles(self):
        selected_index = self.option_group.checkedId()

        for index, frame in enumerate(self.option_frames):
            if index == selected_index:
                frame.setObjectName("selectedOptionFrame")
            else:
                frame.setObjectName("optionFrame")

            frame.style().unpolish(frame)
            frame.style().polish(frame)

    def reset_option_styles(self):
        for frame in self.option_frames:
            frame.setObjectName("optionFrame")
            frame.style().unpolish(frame)
            frame.style().polish(frame)

   
    # function to handle answer submission by checking the selected answer against the correct answer, updating the score, providing feedback, showing explanations and context,
    
    def submit_answer(self):
        selected_index = self.option_group.checkedId()

        if selected_index == -1:
            QMessageBox.warning(
                self,
                "No Answer Selected",
                "Please select an answer before submitting."
            )
            return

        question = self.questions[self.current_index]
        correct_index = self.get_correct_index(question)

        self.answers[self.current_index] = selected_index
        self.submitted_answers[self.current_index] = True

        if selected_index == correct_index:
            self.score += 1
            self.feedback_label.setText("Correct answer.")
            self.feedback_label.setObjectName("correctFeedback")
        else:
            correct_text = question["options"][correct_index]
            self.feedback_label.setText(f"Incorrect. Correct answer: {correct_text}")
            self.feedback_label.setObjectName("wrongFeedback")

        self.feedback_label.style().unpolish(self.feedback_label)
        self.feedback_label.style().polish(self.feedback_label)
        self.feedback_label.show()

        explanation = question.get("explanation", "No explanation available.")
        context = question.get("context", "")

        if context:
            self.context_label.setText(
                f"Ground-truth source sentence:\n{context}\n\nExplanation:\n{explanation}"
            )
        else:
            self.context_label.setText(
                f"Explanation:\n{explanation}"
            )

        self.context_label.show()

        for index, frame in enumerate(self.option_frames):
            if index == correct_index:
                frame.setObjectName("correctOptionFrame")
            elif index == selected_index:
                frame.setObjectName("wrongOptionFrame")
            else:
                frame.setObjectName("optionFrame")

            frame.style().unpolish(frame)
            frame.style().polish(frame)

        for button in self.option_buttons:
            button.setEnabled(False)

        self.submit_button.hide()

        if self.current_index == len(self.questions) - 1:
            self.next_button.setText("Finish Quiz")
        else:
            self.next_button.setText("Next")

        self.next_button.show()

    def get_correct_index(self, question):
        answer = question.get("answer", 0)
        options = question.get("options", [])

        if isinstance(answer, int):
            if 0 <= answer < len(options):
                return answer

        if isinstance(answer, str):
            for index, option in enumerate(options):
                if option.strip().lower() == answer.strip().lower():
                    return index

        correct = question.get("correct", "")

        if isinstance(correct, str):
            for index, option in enumerate(options):
                if option.strip().lower() == correct.strip().lower():
                    return index

        return 0

    def next_question(self):
        self.current_index += 1

        if self.current_index >= len(self.questions):
            self.finish_quiz()
        else:
            self.show_question()

    def confirm_end_quiz(self):
        confirm = QMessageBox.question(
            self,
            "End Quiz",
            "Are you sure you want to end the quiz now?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            self.finish_quiz()

    
    # function to update the quiz timer every second, decreasing the time left, updating the timer display, and automatically finishing the quiz when time runs out
   

    def update_timer(self):
        self.time_left -= 1

        minutes = self.time_left // 60
        seconds = self.time_left % 60

        self.timer_label.setText(f"Time: {minutes:02d}:{seconds:02d}")

        if self.time_left <= 0:
            self.timer.stop()

            QMessageBox.information(
                self,
                "Time Up",
                "The time limit is over. Your quiz will now finish."
            )

            self.finish_quiz()

    
    # function to finish the quiz by stopping the timer, calculating the final score and percentage, updating the results display, saving the score to the database, and switching to the results page
    

    def finish_quiz(self):
        self.timer.stop()

        total = len(self.questions)

        if total == 0:
            return

        percentage = round((self.score / total) * 100, 1)

        self.result_score_label.setText(f"{self.score} / {total}")
        self.result_percent_label.setText(f"Score: {percentage}%")

        self.progress_bar.setValue(100)

        self.save_score()

        self.stack.setCurrentWidget(self.results_page)

    def ensure_scores_table(self, cursor):
        required_columns = {
            "id",
            "username",
            "score",
            "total_questions",
            "percentage",
            "created_at"
        }

        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='scores'
        """)

        table_exists = cursor.fetchone() is not None

        if table_exists:
            cursor.execute("PRAGMA table_info(scores)")
            table_info = cursor.fetchall()

            existing_columns = {column[1] for column in table_info}

            has_required_columns = required_columns.issubset(existing_columns)

            old_required_columns = []

            for column in table_info:
                column_name = column[1]
                not_null = column[3]
                default_value = column[4]
                primary_key = column[5]

                if (
                    column_name not in required_columns
                    and not_null == 1
                    and default_value is None
                    and primary_key == 0
                ):
                    old_required_columns.append(column_name)

            if not has_required_columns or old_required_columns:
                cursor.execute("DROP TABLE IF EXISTS scores")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT DEFAULT 'Student',
                score INTEGER DEFAULT 0,
                total_questions INTEGER DEFAULT 0,
                percentage REAL DEFAULT 0,
                created_at TEXT DEFAULT ''
            )
        """)

        cursor.execute("PRAGMA table_info(scores)")
        existing_columns = [column[1] for column in cursor.fetchall()]

        if "username" not in existing_columns:
            cursor.execute("ALTER TABLE scores ADD COLUMN username TEXT DEFAULT 'Student'")

        if "score" not in existing_columns:
            cursor.execute("ALTER TABLE scores ADD COLUMN score INTEGER DEFAULT 0")

        if "total_questions" not in existing_columns:
            cursor.execute("ALTER TABLE scores ADD COLUMN total_questions INTEGER DEFAULT 0")

        if "percentage" not in existing_columns:
            cursor.execute("ALTER TABLE scores ADD COLUMN percentage REAL DEFAULT 0")

        if "created_at" not in existing_columns:
            cursor.execute("ALTER TABLE scores ADD COLUMN created_at TEXT DEFAULT ''")


    def save_score(self):
        if self.score_saved:
            return

        total = len(self.questions)

        if total == 0:
            return

        percentage = round((self.score / total) * 100, 1)

        conn = sqlite3.connect("quiz_knight.db")
        cursor = conn.cursor()

        self.ensure_scores_table(cursor)

        cursor.execute("""
            INSERT INTO scores (username, score, total_questions, percentage, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            self.username,
            self.score,
            total,
            percentage,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        conn.commit()
        conn.close()

        self.score_saved = True


    def show_leaderboard(self):
        conn = sqlite3.connect("quiz_knight.db")
        cursor = conn.cursor()

        self.ensure_scores_table(cursor)

        cursor.execute("""
            SELECT username, score, total_questions, percentage, created_at
            FROM scores
            ORDER BY percentage DESC, score DESC
            LIMIT 10
        """)

        rows = cursor.fetchall()

        conn.close()

        if not rows:
            QMessageBox.information(
                self,
                "Leaderboard",
                "No scores saved yet."
            )
            return

        leaderboard_text = "Top Scores:\n\n"

        for index, row in enumerate(rows, start=1):
            username, score, total, percentage, created_at = row

            leaderboard_text += (
                f"{index}. {username} - {score}/{total} "
                f"({percentage}%) - {created_at}\n"
            )

        QMessageBox.information(
            self,
            "Leaderboard",
            leaderboard_text
        )
        QMessageBox.information(
            self,
            "Leaderboard",
            leaderboard_text
        )

    def reset_to_input(self):
        self.timer.stop()

        self.questions = []
        self.current_index = 0
        self.answers = []
        self.submitted_answers = []
        self.score = 0
        self.score_saved = False

        self.stack.setCurrentWidget(self.input_page)

    
    def show_review_page(self):
        self.clear_review_layout()

        for index, question in enumerate(self.questions):
            review_card = QFrame()
            review_card.setObjectName("reviewCard")

            card_layout = QVBoxLayout()

            question_label = QLabel(
                f"Question {index + 1}: {question.get('question', '')}"
            )
            question_label.setWordWrap(True)
            question_label.setObjectName("reviewQuestionLabel")

            options = question.get("options", [])
            selected_index = self.answers[index]
            correct_index = self.get_correct_index(question)

            selected_text = "Not answered"

            if selected_index is not None and 0 <= selected_index < len(options):
                selected_text = options[selected_index]

            if options and 0 <= correct_index < len(options):
                correct_text = options[correct_index]
            else:
                correct_text = "Missing correct answer"

            if selected_index == correct_index:
                result_text = "Result: Correct"
            else:
                result_text = "Result: Incorrect"

            answer_label = QLabel(
                f"{result_text}\n"
                f"Your answer: {selected_text}\n"
                f"Correct answer: {correct_text}"
            )
            answer_label.setWordWrap(True)
            answer_label.setObjectName("reviewAnswerLabel")

            context = question.get("context", "")
            explanation = question.get("explanation", "No explanation available.")

            explanation_label = QLabel(
                f"Ground-truth source sentence:\n{context}\n\nExplanation:\n{explanation}"
            )
            explanation_label.setWordWrap(True)
            explanation_label.setObjectName("reviewExplanationLabel")

            card_layout.addWidget(question_label)
            card_layout.addWidget(answer_label)
            card_layout.addWidget(explanation_label)

            review_card.setLayout(card_layout)

            self.review_content_layout.addWidget(review_card)

        self.review_content_layout.addStretch()

        self.stack.setCurrentWidget(self.review_page)

    def clear_review_layout(self):
        while self.review_content_layout.count():
            item = self.review_content_layout.takeAt(0)

            widget = item.widget()

            if widget:
                widget.deleteLater()


    def get_stylesheet(self):
        return """
        QWidget {
            background-color: #0f172a;
            color: #e5e7eb;
            font-family: Arial;
            font-size: 14px;
        }

        #titleLabel {
            color: #a855f7;
            font-size: 34px;
            font-weight: bold;
        }

        #subtitleLabel {
            color: #e5e7eb;
            font-size: 15px;
        }

        #smallLabel {
            color: #cbd5e1;
            font-size: 13px;
        }

        #timerLabel {
            color: #facc15;
            font-size: 16px;
            font-weight: bold;
        }

        #settingCard {
            background-color: #1e293b;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 10px;
        }

        #settingLabel {
            color: #e5e7eb;
            font-size: 13px;
            font-weight: bold;
        }

        QTextEdit {
            background-color: #1e293b;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 12px;
            color: #f8fafc;
            font-size: 14px;
        }

        QComboBox, QSpinBox {
            background-color: #334155;
            border: 1px solid #475569;
            border-radius: 8px;
            padding: 7px;
            color: #f8fafc;
        }

        QPushButton {
            background-color: #334155;
            border: 1px solid #475569;
            border-radius: 10px;
            padding: 10px;
            color: #f8fafc;
            font-weight: bold;
        }

        QPushButton:hover {
            background-color: #475569;
        }

        #primaryButton {
            background-color: #9333ea;
            border: 1px solid #a855f7;
            color: white;
            font-weight: bold;
        }

        #primaryButton:hover {
            background-color: #a855f7;
        }

        QProgressBar {
            background-color: #1e293b;
            border: 1px solid #334155;
            border-radius: 8px;
            text-align: center;
            color: white;
            height: 18px;
        }

        QProgressBar::chunk {
            background-color: #9333ea;
            border-radius: 8px;
        }

        #questionCard {
            background-color: #1e293b;
            border: 1px solid #334155;
            border-radius: 14px;
            padding: 14px;
        }

        #questionTypeLabel {
            color: #a855f7;
            font-size: 13px;
            font-weight: bold;
        }

        #questionLabel {
            color: #f8fafc;
            font-size: 20px;
            font-weight: bold;
        }

        #optionFrame {
            background-color: #1e293b;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 8px;
        }

        #selectedOptionFrame {
            background-color: #312e81;
            border: 2px solid #8b5cf6;
            border-radius: 12px;
            padding: 8px;
        }

        #correctOptionFrame {
            background-color: #14532d;
            border: 2px solid #22c55e;
            border-radius: 12px;
            padding: 8px;
        }

        #wrongOptionFrame {
            background-color: #7f1d1d;
            border: 2px solid #ef4444;
            border-radius: 12px;
            padding: 8px;
        }

        #optionRadio {
            color: #f8fafc;
            font-size: 15px;
        }

        #feedbackLabel {
            background-color: #1e293b;
            border-radius: 10px;
            padding: 10px;
        }

        #correctFeedback {
            background-color: #14532d;
            border: 1px solid #22c55e;
            border-radius: 10px;
            padding: 10px;
            color: #dcfce7;
            font-weight: bold;
        }

        #wrongFeedback {
            background-color: #7f1d1d;
            border: 1px solid #ef4444;
            border-radius: 10px;
            padding: 10px;
            color: #fee2e2;
            font-weight: bold;
        }

        #contextLabel {
            background-color: #020617;
            border: 1px solid #334155;
            border-radius: 10px;
            padding: 10px;
            color: #cbd5e1;
        }

        #resultScoreLabel {
            color: #a855f7;
            font-size: 48px;
            font-weight: bold;
        }

        #reviewCard {
            background-color: #1e293b;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 12px;
            margin-bottom: 10px;
        }

        #reviewQuestionLabel {
            color: #f8fafc;
            font-size: 16px;
            font-weight: bold;
        }

        #reviewAnswerLabel {
            color: #e5e7eb;
            font-size: 14px;
        }

        #reviewExplanationLabel {
            color: #cbd5e1;
            font-size: 13px;
        }
        """