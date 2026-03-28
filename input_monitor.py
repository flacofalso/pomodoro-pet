import time
from PyQt6.QtCore import QObject, QTimer, QPoint, pyqtSignal
from PyQt6.QtGui import QCursor


class InputMonitor(QObject):
    """
    Detects mouse and keyboard activity using:
    - Mouse: Qt cursor position polling (no extra dependencies needed)
    - Keyboard: pynput if available, otherwise mouse-only detection

    Emits:
      activity_detected   — user moved mouse or pressed a key during break
      inactivity_reached  — user has been still for INACTIVITY_THRESHOLD seconds
    """

    activity_detected  = pyqtSignal()
    inactivity_reached = pyqtSignal()

    INACTIVITY_THRESHOLD = 4    # seconds of silence = real rest
    CHECK_INTERVAL_MS    = 400  # how often we poll

    def __init__(self):
        super().__init__()
        self._last_activity   = time.time()
        self._last_cursor_pos = QCursor.pos()
        self._is_resting      = False
        self._monitoring      = False
        self._kb_listener     = None

        self._timer = QTimer()
        self._timer.setInterval(self.CHECK_INTERVAL_MS)
        self._timer.timeout.connect(self._poll)

    # ── Public API ─────────────────────────────────────────────────────────

    def start_monitoring(self):
        self._monitoring      = True
        self._last_activity   = time.time()
        self._last_cursor_pos = QCursor.pos()
        self._is_resting      = False
        self._try_start_keyboard_listener()
        self._timer.start()

    def stop_monitoring(self):
        self._monitoring = False
        self._timer.stop()
        self._stop_keyboard_listener()

    # ── Keyboard listener (optional, uses pynput) ──────────────────────────

    def _try_start_keyboard_listener(self):
        try:
            from pynput import keyboard
            self._kb_listener = keyboard.Listener(on_press=self._on_key)
            self._kb_listener.start()
        except Exception as e:
            print(f"[InputMonitor] Keyboard listener unavailable: {e}")
            self._kb_listener = None

    def _stop_keyboard_listener(self):
        if self._kb_listener and self._kb_listener.running:
            try:
                self._kb_listener.stop()
            except Exception:
                pass
        self._kb_listener = None

    def _on_key(self, key):
        """Called from pynput thread — just update timestamp."""
        self._last_activity = time.time()

    # ── Main polling loop (Qt thread) ──────────────────────────────────────

    def _poll(self):
        if not self._monitoring:
            return

        # Check mouse movement via Qt (always works, no extra permissions)
        current_pos = QCursor.pos()
        if self._cursor_moved(current_pos, self._last_cursor_pos):
            self._last_activity   = time.time()
            self._last_cursor_pos = current_pos

        elapsed = time.time() - self._last_activity

        if elapsed < self.INACTIVITY_THRESHOLD:
            # Active recently
            if self._is_resting:
                self._is_resting = False
                self.activity_detected.emit()
        else:
            # Enough silence
            if not self._is_resting:
                self._is_resting = True
                self.inactivity_reached.emit()

    @staticmethod
    def _cursor_moved(pos_a: QPoint, pos_b: QPoint, threshold: int = 5) -> bool:
        """Returns True if cursor moved more than `threshold` pixels."""
        dx = pos_a.x() - pos_b.x()
        dy = pos_a.y() - pos_b.y()
        return (dx * dx + dy * dy) > threshold * threshold
