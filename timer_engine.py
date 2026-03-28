from PyQt6.QtCore import QObject, QTimer, pyqtSignal


class TimerEngine(QObject):
    tick = pyqtSignal(int)        # remaining seconds
    work_finished = pyqtSignal()
    break_finished = pyqtSignal()

    def __init__(self, work_minutes: int = 25, break_minutes: int = 5):
        super().__init__()
        self.work_duration = work_minutes * 60
        self.break_duration = break_minutes * 60
        self.remaining = self.work_duration
        self.is_work_phase = True
        self.running = False

        self._timer = QTimer()
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._tick)

    # ── Public API ─────────────────────────────────────────────────────────

    def start(self):
        if not self.running:
            self.running = True
            self._timer.start()

    def pause(self):
        self.running = False
        self._timer.stop()

    def reset(self):
        self._timer.stop()
        self.running = False
        self.is_work_phase = True
        self.remaining = self.work_duration
        self.tick.emit(self.remaining)

    def start_break(self):
        self.is_work_phase = False
        self.remaining = self.break_duration
        self.running = True
        self._timer.start()

    def set_durations(self, work_minutes: int, break_minutes: int):
        self.work_duration = work_minutes * 60
        self.break_duration = break_minutes * 60
        if not self.running:
            self.remaining = self.work_duration
            self.tick.emit(self.remaining)

    # ── Internal ───────────────────────────────────────────────────────────

    def _tick(self):
        self.remaining -= 1
        self.tick.emit(self.remaining)
        if self.remaining <= 0:
            self._timer.stop()
            self.running = False
            if self.is_work_phase:
                self.work_finished.emit()
            else:
                self.break_finished.emit()
