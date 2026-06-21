from PyQt6.QtCore import QObject, QTimer, pyqtSignal

# Manages the quiz timer, emitting signals for time updates and when time runs out
class QuizTimer(QObject):
    time_updated = pyqtSignal(int)
    time_finished = pyqtSignal()
# Initialize the timer with a specified number of seconds, setting up the QTimer and connecting signals
    def __init__(self, seconds):
        super().__init__()

        self.total_seconds = seconds
        self.remaining_seconds = seconds

        self.timer = QTimer()
        self.timer.timeout.connect(self._tick)
# Start the timer, which will call the _tick method every second
    def start(self):
        self.timer.start(1000)
# Stop the timer, halting the countdown
    def stop(self):
        self.timer.stop()

    def reset(self):
        self.remaining_seconds = self.total_seconds
        self.time_updated.emit(self.remaining_seconds)

    def _tick(self):
        self.remaining_seconds -= 1
        self.time_updated.emit(self.remaining_seconds)

        if self.remaining_seconds <= 0:
            self.timer.stop()
            self.time_finished.emit()

    def get_time_taken(self):
        return self.total_seconds - self.remaining_seconds