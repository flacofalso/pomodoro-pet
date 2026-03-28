from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QLabel,
    QDialog, QVBoxLayout, QFormLayout, QSpinBox,
    QGraphicsDropShadowEffect,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor

from timer_engine import TimerEngine


class ControlPanel(QWidget):
    start_requested = pyqtSignal()
    pause_requested = pyqtSignal()
    reset_requested = pyqtSignal()

    PANEL_STYLE = """
        QWidget#panel {
            background: rgba(15, 15, 20, 235);
            border-radius: 20px;
            border: 1.5px solid rgba(255, 255, 255, 180);
        }
        QPushButton {
            background: rgba(255, 255, 255, 40);
            border: 1.5px solid rgba(255, 255, 255, 160);
            border-radius: 10px;
            color: white;
            font-size: 15px;
            min-width: 32px;
            min-height: 32px;
            padding: 2px 8px;
        }
        QPushButton:hover {
            background: rgba(255, 255, 255, 90);
            border: 1.5px solid rgba(255, 255, 255, 230);
        }
        QPushButton:disabled {
            color: rgba(255, 255, 255, 60);
            border: 1.5px solid rgba(255, 255, 255, 50);
            background: rgba(255, 255, 255, 10);
        }
        QLabel {
            color: white;
            background: transparent;
            padding: 0 4px;
        }
    """

    def __init__(self, timer_engine: TimerEngine, parent=None):
        super().__init__(parent)
        self._engine = timer_engine
        self._is_running = False
        self._setup_ui()
        self._engine.tick.connect(self._on_tick)

    def _setup_ui(self):
        self.setObjectName("panel")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet(self.PANEL_STYLE)

        # Drop shadow so the panel floats visibly over any background
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(18)
        shadow.setOffset(0, 3)
        shadow.setColor(QColor(0, 0, 0, 160))
        self.setGraphicsEffect(shadow)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 9, 14, 9)
        layout.setSpacing(7)

        self._lbl_phase = QLabel("trabajo")
        self._lbl_phase.setFont(QFont("Helvetica Neue", 9))
        self._lbl_phase.setStyleSheet(
            "color: rgba(255,255,255,180); background:transparent;"
        )

        self._lbl_time = QLabel(self._fmt(self._engine.work_duration))
        self._lbl_time.setFont(QFont("Helvetica Neue", 14, QFont.Weight.Medium))
        self._lbl_time.setMinimumWidth(54)
        self._lbl_time.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._btn_start  = QPushButton("▶")
        self._btn_pause  = QPushButton("⏸")
        self._btn_reset  = QPushButton("↺")
        self._btn_config = QPushButton("⚙")

        self._btn_pause.setEnabled(False)

        self._btn_start.clicked.connect(self._on_start)
        self._btn_pause.clicked.connect(self._on_pause)
        self._btn_reset.clicked.connect(self._on_reset)
        self._btn_config.clicked.connect(self._open_settings)

        # Divider label
        sep = QLabel("|")
        sep.setStyleSheet("color: rgba(255,255,255,60); background:transparent;")

        for w in (self._lbl_phase, self._lbl_time, sep,
                  self._btn_start, self._btn_pause,
                  self._btn_reset, self._btn_config):
            layout.addWidget(w)

        self.adjustSize()

    # ── Slots ──────────────────────────────────────────────────────────────

    def _on_tick(self, remaining: int):
        self._lbl_time.setText(self._fmt(remaining))
        self._lbl_phase.setText("pausa" if not self._engine.is_work_phase else "trabajo")

    def _on_start(self):
        self._is_running = True
        self._btn_start.setEnabled(False)
        self._btn_pause.setEnabled(True)
        self.start_requested.emit()

    def _on_pause(self):
        self._is_running = False
        self._btn_start.setEnabled(True)
        self._btn_pause.setEnabled(False)
        self.pause_requested.emit()

    def _on_reset(self):
        self._is_running = False
        self._btn_start.setEnabled(True)
        self._btn_pause.setEnabled(False)
        self._lbl_time.setText(self._fmt(self._engine.work_duration))
        self._lbl_phase.setText("trabajo")
        self.reset_requested.emit()

    def notify_work_finished(self):
        self._is_running = True
        self._btn_start.setEnabled(False)
        self._btn_pause.setEnabled(False)

    def notify_break_finished(self):
        self._is_running = False
        self._btn_start.setEnabled(True)
        self._btn_pause.setEnabled(False)
        self._lbl_time.setText(self._fmt(self._engine.work_duration))
        self._lbl_phase.setText("trabajo")

    def _open_settings(self):
        dlg = SettingsDialog(self._engine, self)
        if dlg.exec():
            if not self._is_running:
                self._lbl_time.setText(self._fmt(self._engine.work_duration))

    @staticmethod
    def _fmt(seconds: int) -> str:
        m, s = divmod(max(0, seconds), 60)
        return f"{m:02d}:{s:02d}"


class SettingsDialog(QDialog):
    STYLE = """
        QDialog        { background: #1a1a2e; border-radius: 12px; }
        QLabel         { color: #e0e0e0; font-size: 13px; }
        QSpinBox {
            background: #2a2a3e;
            color: #ffffff;
            border: 1.5px solid #5566aa;
            border-radius: 6px;
            padding: 4px 8px;
            font-size: 13px;
        }
        QSpinBox::up-button, QSpinBox::down-button { width: 18px; }
        QPushButton {
            background: #5C7AEA;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 7px 24px;
            font-size: 13px;
        }
        QPushButton:hover { background: #4a69d4; }
    """

    def __init__(self, engine: TimerEngine, parent=None):
        super().__init__(parent)
        self._engine = engine
        self.setWindowTitle("Configuración del Pomodoro")
        self.setFixedSize(260, 170)
        self.setStyleSheet(self.STYLE)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowStaysOnTopHint)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 16, 20, 16)

        form = QFormLayout()
        form.setSpacing(10)

        self._spin_work = QSpinBox()
        self._spin_work.setRange(1, 120)
        self._spin_work.setValue(engine.work_duration // 60)
        self._spin_work.setSuffix(" min")

        self._spin_break = QSpinBox()
        self._spin_break.setRange(1, 60)
        self._spin_break.setValue(engine.break_duration // 60)
        self._spin_break.setSuffix(" min")

        form.addRow("⏱  Trabajo:", self._spin_work)
        form.addRow("☕  Pausa:",   self._spin_break)
        layout.addLayout(form)

        btn = QPushButton("Guardar")
        btn.clicked.connect(self._save)
        layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

    def _save(self):
        self._engine.set_durations(self._spin_work.value(), self._spin_break.value())
        self.accept()
