"""
convert_video.py — Convierte un video a sprite sheet PNG para la app Pomodoro Pet.

Uso:
    python3 convert_video.py <video.mp4> <estado>

Ejemplo:
    python3 convert_video.py animacion_working.mp4 working

Estados válidos: working, tired, resting, celebrating

El resultado se guarda automáticamente en assets/<estado>.png
"""

import sys
import os

def install_if_missing(package, import_name=None):
    import importlib
    name = import_name or package
    try:
        importlib.import_module(name)
    except ImportError:
        import subprocess
        print(f"Instalando {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install_if_missing("opencv-python", "cv2")
install_if_missing("Pillow", "PIL")

import cv2
from PIL import Image

VALID_STATES = ["working", "tired", "resting", "celebrating"]
FRAME_SIZE   = 200
MAX_FRAMES   = 8     # máximo frames a extraer del video
TARGET_FPS   = 4     # cuántos frames por segundo del video capturar


def extract_frames(video_path: str, target_fps: int, max_frames: int) -> list:
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: no se pudo abrir {video_path}")
        sys.exit(1)

    video_fps = cap.get(cv2.CAP_PROP_FPS)
    total     = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration  = total / video_fps if video_fps > 0 else 0

    print(f"Video: {os.path.basename(video_path)}")
    print(f"  {video_fps:.1f} fps · {total} frames · {duration:.1f}s")

    # Capture one frame every N original frames
    step = max(1, int(video_fps / target_fps))
    frames = []
    idx = 0

    while len(frames) < max_frames:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ok, frame = cap.read()
        if not ok:
            break
        # BGR → RGBA
        frame_rgb  = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_img    = Image.fromarray(frame_rgb).convert("RGBA")
        frames.append(pil_img)
        idx += step

    cap.release()
    print(f"  Extraídos {len(frames)} frames")
    return frames


def remove_bg(img: Image.Image) -> Image.Image:
    """Auto-detect and remove black or white background."""
    w, h = img.size
    corners = [img.getpixel((0,0)), img.getpixel((w-1,0)),
               img.getpixel((0,h-1)), img.getpixel((w-1,h-1))]
    dark  = sum(1 for p in corners if p[0]<50 and p[1]<50 and p[2]<50)
    light = sum(1 for p in corners if p[0]>200 and p[1]>200 and p[2]>200)
    bg = "black" if dark >= light else "white"

    pixels = list(img.getdata())
    result = []
    for r,g,b,a in pixels:
        if bg == "black":
            if r<45 and g<45 and b<45:
                result.append((0,0,0,0))
            else:
                result.append((r,g,b,a))
        else:
            if r>220 and g>220 and b>220:
                result.append((0,0,0,0))
            else:
                result.append((r,g,b,a))
    img.putdata(result)
    return img


def to_frame(img: Image.Image, size: int = FRAME_SIZE) -> Image.Image:
    img = remove_bg(img)
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
    img.thumbnail((size, size), Image.LANCZOS)
    canvas = Image.new("RGBA", (size, size), (0,0,0,0))
    ox = (size - img.width)  // 2
    oy = (size - img.height) // 2
    canvas.paste(img, (ox, oy), img)
    return canvas


def build_sheet(frames: list, size: int = FRAME_SIZE) -> Image.Image:
    sheet = Image.new("RGBA", (size * len(frames), size), (0,0,0,0))
    for i, f in enumerate(frames):
        sheet.paste(to_frame(f, size), (i * size, 0))
    return sheet


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    video_path = sys.argv[1]
    state      = sys.argv[2].lower()

    if not os.path.exists(video_path):
        print(f"Error: no encontré el archivo {video_path}")
        sys.exit(1)

    if state not in VALID_STATES:
        print(f"Estado inválido: '{state}'. Usa uno de: {', '.join(VALID_STATES)}")
        sys.exit(1)

    frames = extract_frames(video_path, TARGET_FPS, MAX_FRAMES)
    sheet  = build_sheet(frames)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    out_path   = os.path.join(script_dir, "assets", f"{state}.png")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    sheet.save(out_path, "PNG")

    print(f"\n✓ Guardado en {out_path}")
    print(f"  {len(frames)} frames · {sheet.width}x{sheet.height}px")
    print(f"\nReinicia la app con: python3 main.py")
