# 🐾 Pomodoro Pet

Una mascota de escritorio que vive sobre todas tus ventanas y te ayuda a respetar el método Pomodoro.

---

## Instalación

```bash
# 1. Crea entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows

# 2. Instala dependencias
pip install -r requirements.txt

# 3. Ejecuta
python main.py
```

### Permisos en macOS
`pynput` necesita acceso a **Accesibilidad** para detectar el teclado/mouse globalmente.
Ve a: **Preferencias del Sistema → Privacidad y Seguridad → Accesibilidad** y agrega tu terminal o Python.

---

## Uso

| Acción | Cómo |
|--------|------|
| Mover la mascota | Click y arrastrar |
| Ver controles | Pasar el cursor sobre la mascota |
| Iniciar timer | Botón ▶ en el panel |
| Pausar | Botón ⏸ |
| Reiniciar | Botón ↺ |
| Cambiar tiempos | Botón ⚙ |

---

## Estados de la mascota

| Estado | Cuándo ocurre |
|--------|---------------|
| 😊 **Trabajando** | Timer de trabajo activo |
| 😩 **Cansada** | Tiempo de trabajo agotado — necesita pausa |
| 😴 **Descansando** | Pausa activa + tú sin tocar mouse/teclado |
| 🎉 **Celebrando** | Completaste una pausa real |

> **Importante:** Si mueves el mouse o teclado durante la pausa, la mascota vuelve al estado cansado. ¡Tienes que alejarte de verdad!

---

## Agregar tu mascota personalizada

Coloca tus sprites en la carpeta `assets/`:

```
assets/
├── working.png       ← Estado activo / feliz
├── tired.png         ← Estado cansado / agobiado
├── resting.png       ← Descansando de verdad
└── celebrating.png   ← Pomodoro completado
```

### Formato de cada PNG

- **Fondo transparente** (canal alpha)
- **Tira horizontal** de frames: todos del mismo tamaño
- **Tamaño recomendado:** 200×200 px por frame

```
┌──────────┬──────────┬──────────┬──────────┐
│  frame 1 │  frame 2 │  frame 3 │  frame 4 │
│  200×200 │  200×200 │  200×200 │  200×200 │
└──────────┴──────────┴──────────┴──────────┘
← ancho total = 200 × 4 = 800 px →
```

El número de frames es detectado automáticamente por el código.

### Velocidad de animación

En `animation_engine.py` cambia el valor de `fps` (default: 8):
```python
AnimationEngine(frame_size=200, fps=8)
```

---

## Estructura del proyecto

```
pomodoro-pet/
├── main.py              # Entrada principal
├── pet_window.py        # Ventana transparente con la mascota
├── control_panel.py     # Mini panel flotante de controles
├── timer_engine.py      # Lógica del pomodoro
├── input_monitor.py     # Detecta inactividad con pynput
├── animation_engine.py  # Renderiza sprite sheets
├── state_machine.py     # Enum de estados
├── requirements.txt
└── assets/              # Tus PNGs van aquí
```
