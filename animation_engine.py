import os
from PyQt6.QtCore import QTimer, QRect
from PyQt6.QtGui import QPixmap, QPainter, QColor, QBrush, QPen, QFont
from state_machine import PetState

# ── Placeholder fallback (used only if PNG assets are missing) ─────────────

_PLACEHOLDER_COLORS = {
    "working":     (QColor("#5CDB95"), QColor("#05386B")),
    "tired":       (QColor("#E84545"), QColor("#2B2E4A")),
    "resting":     (QColor("#6A8EAE"), QColor("#2B2E4A")),
    "celebrating": (QColor("#FFD166"), QColor("#2B2E4A")),
}
_PLACEHOLDER_EMOJI = {
    "working":     ["(^_^)", "(^o^)", "( ^ω^)", "(≧◡≦)"],
    "tired":       ["(；△；)", "(>_<)", "(T_T)", "(ó_ò)"],
    "resting":     ["(ᴗ_ ᴗ)", "( ˘ω˘ )", "(¬_¬)", "(=_=)"],
    "celebrating": ["\\(^▽^)/", "(ﾉ◕ヮ◕)ﾉ", "★(^▽^)★", "ヽ(★ω★)ﾉ"],
}

# ── FPS rules ──────────────────────────────────────────────────────────────
# Fewer frames → slower cycle so the animation doesn't look jittery.
# These are ms-per-frame values, not FPS.

def _ms_per_frame(n_frames: int) -> int:
    """Return milliseconds per frame based on how many frames the state has."""
    if n_frames <= 1:
        return 2000   # static
    if n_frames == 2:
        return 1000   # 1 fps
    if n_frames == 3:
        return 500    # 2 fps
    if n_frames <= 8:
        return 200    # 5 fps
    return 160        # ~6 fps for 12 frames


class AnimationEngine:
    """
    Loads sprite sheets (horizontal strips of equally-sized frames)
    and cycles through them at an adaptive speed.

    Each PNG is a horizontal strip: width = frame_size × N, height = frame_size.
    Background must be transparent (RGBA).
    """

    def __init__(self, frame_size: int = 200):
        self.frame_size = frame_size

        self._sprites: dict[str, tuple[QPixmap, int]] = {}
        self._current_state: str | None = None
        self._current_frame: int = 0
        self._frame_count: int = 0
        self._on_frame: callable | None = None

        self._timer = QTimer()
        self._timer.timeout.connect(self._advance_frame)

    # ── Public API ─────────────────────────────────────────────────────────

    def load_sprites(self, assets_dir: str):
        for state in ["working", "tired", "resting", "celebrating"]:
            path = os.path.join(assets_dir, f"{state}.png")
            if os.path.exists(path):
                sheet = QPixmap(path)
                if not sheet.isNull():
                    n = max(1, sheet.width() // self.frame_size)
                    self._sprites[state] = (sheet, n)
                    print(f"[Anim] {state}.png — {n} frame(s), {_ms_per_frame(n)}ms/frame")
                    continue
            self._sprites[state] = self._make_placeholder(state)
            print(f"[Anim] No {state}.png — placeholder")

    def set_callback(self, fn: callable):
        self._on_frame = fn

    def set_state(self, state_name: str):
        if state_name == self._current_state:
            return
        self._current_state = state_name
        self._current_frame = 0
        self._timer.stop()

        if state_name in self._sprites:
            _, count = self._sprites[state_name]
            self._frame_count = count
            self._push_frame()
            self._timer.start(_ms_per_frame(count))

    # ── Internal ───────────────────────────────────────────────────────────

    def _advance_frame(self):
        self._current_frame = (self._current_frame + 1) % self._frame_count
        self._push_frame()

    def _push_frame(self):
        if self._current_state not in self._sprites:
            return
        sheet, _ = self._sprites[self._current_state]
        x = self._current_frame * self.frame_size
        frame = sheet.copy(QRect(x, 0, self.frame_size, self.frame_size))
        if self._on_frame:
            self._on_frame(frame)

    def _make_placeholder(self, state: str) -> tuple[QPixmap, int]:
        emojis = _PLACEHOLDER_EMOJI.get(state, ["(?_?)"] * 4)
        n = len(emojis)
        size = self.frame_size
        bg_color, fg_color = _PLACEHOLDER_COLORS.get(
            state, (QColor("#888888"), QColor("#ffffff"))
        )
        sheet = QPixmap(size * n, size)
        sheet.fill(QColor(0, 0, 0, 0))
        painter = QPainter(sheet)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        for i, emoji in enumerate(emojis):
            x_off = i * size
            painter.setBrush(QBrush(bg_color))
            painter.setPen(QPen(QColor(0, 0, 0, 0)))
            painter.drawEllipse(x_off + 20, 20, size - 40, size - 40)
            font = QFont("Arial", 22, QFont.Weight.Bold)
            painter.setFont(font)
            painter.setPen(QPen(fg_color))
            painter.drawText(QRect(x_off, 0, size, size), 0x0084, emoji)
        painter.end()
        return (sheet, n)
