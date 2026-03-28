import os
from PyQt6.QtWidgets import QWidget, QLabel, QApplication
from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import QCursor

from state_machine import PetState
from animation_engine import AnimationEngine
from timer_engine import TimerEngine
from input_monitor import InputMonitor
from control_panel import ControlPanel
from notifier import notify


class PetWindow(QWidget):
    CELEBRATING_DURATION_MS = 4_000

    def __init__(self):
        super().__init__()
        self._state = PetState.WORKING
        self._drag_origin: QPoint | None = None

        self._build_window()
        self._build_subsystems()
        self._wire_signals()
        self._set_state(PetState.WORKING)

        self._hover_poll = QTimer()
        self._hover_poll.setInterval(120)
        self._hover_poll.timeout.connect(self._poll_hover)
        self._hover_poll.start()

    def _build_window(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setAttribute(Qt.WidgetAttribute.WA_MacAlwaysShowToolWindow)
        self.setFixedSize(200, 200)

        screen = QApplication.primaryScreen().availableGeometry()
        self.move(screen.right() - 220, screen.bottom() - 220)

        self._pet_label = QLabel(self)
        self._pet_label.setGeometry(0, 0, 200, 200)
        self._pet_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def _build_subsystems(self):
        assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
        self._anim = AnimationEngine(frame_size=200)
        self._anim.load_sprites(assets_dir)
        self._anim.set_callback(self._pet_label.setPixmap)
        self._timer = TimerEngine()
        self._monitor = InputMonitor()
        self._panel = ControlPanel(self._timer)
        self._panel.hide()

    def _wire_signals(self):
        self._timer.work_finished.connect(self._on_work_finished)
        self._timer.break_finished.connect(self._on_break_finished)
        self._monitor.activity_detected.connect(self._on_activity_during_break)
        self._monitor.inactivity_reached.connect(self._on_inactivity_during_break)
        self._panel.start_requested.connect(self._on_user_start)
        self._panel.pause_requested.connect(self._on_user_pause)
        self._panel.reset_requested.connect(self._on_user_reset)

    def _set_state(self, state: PetState):
        self._state = state
        self._anim.set_state(state.value)

    # ── Timer events ───────────────────────────────────────────────────────

    def _on_work_finished(self):
        self._set_state(PetState.TIRED)
        self._panel.notify_work_finished()
        self._timer.start_break()
        self._monitor.start_monitoring()
        notify("¡Tiempo de descanso! 😩", "Tu mascota está agotada. Aléjate del computador.")

    def _on_break_finished(self):
        self._monitor.stop_monitoring()
        self._panel.notify_break_finished()
        if self._state == PetState.RESTING:
            self._set_state(PetState.CELEBRATING)
            notify("¡Excelente pausa! 🎉", "Descansaste de verdad. ¡A trabajar con energía!")
            QTimer.singleShot(self.CELEBRATING_DURATION_MS, self._start_next_cycle)
        else:
            self._set_state(PetState.WORKING)
            notify("Pausa terminada 😔", "No descansaste bien… intenta alejarte en la próxima.")

    # ── Input monitor events ───────────────────────────────────────────────

    def _on_inactivity_during_break(self):
        if self._state == PetState.TIRED:
            self._set_state(PetState.RESTING)
            notify("Descansando 😴", "Detecté que te alejaste. ¡Sigue así!")

    def _on_activity_during_break(self):
        if self._state == PetState.RESTING:
            self._set_state(PetState.TIRED)
            notify("¡Hey, necesito descansar! 😩", "Detecté actividad. Aléjate para que pueda recuperarme.")

    # ── Panel events ───────────────────────────────────────────────────────

    def _on_user_start(self):
        self._set_state(PetState.WORKING)
        self._timer.start()
        work_min = self._timer.work_duration // 60
        notify("¡Pomodoro iniciado! 🍅", f"Tienes {work_min} minutos de trabajo enfocado.")

    def _on_user_pause(self):
        self._timer.pause()
        notify("Timer pausado ⏸", "El pomodoro está en pausa.")

    def _on_user_reset(self):
        self._monitor.stop_monitoring()
        self._timer.reset()
        self._set_state(PetState.WORKING)

    def _start_next_cycle(self):
        self._set_state(PetState.WORKING)

    # ── Hover ──────────────────────────────────────────────────────────────

    def _poll_hover(self):
        cursor = QCursor.pos()
        over_pet   = self.geometry().contains(cursor)
        over_panel = self._panel.isVisible() and self._panel.geometry().contains(cursor)
        if over_pet or over_panel:
            if not self._panel.isVisible():
                self._reposition_panel()
                self._panel.show()
                self._panel.raise_()
        else:
            if self._panel.isVisible():
                self._panel.hide()

    def _reposition_panel(self):
        pet = self.geometry()
        panel_w = self._panel.sizeHint().width()
        panel_h = self._panel.sizeHint().height()
        screen = QApplication.primaryScreen().availableGeometry()
        x = pet.x() + (pet.width() - panel_w) // 2
        y = pet.y() - panel_h - 8
        x = max(screen.left(), min(x, screen.right()  - panel_w))
        y = max(screen.top(),  min(y, screen.bottom() - panel_h))
        self._panel.move(x, y)

    # ── Drag ───────────────────────────────────────────────────────────────

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_origin = (
                event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            )

    def mouseMoveEvent(self, event):
        if self._drag_origin and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_origin)
            if self._panel.isVisible():
                self._reposition_panel()

    def mouseReleaseEvent(self, event):
        self._drag_origin = None
