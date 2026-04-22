# Terminal Visualizations

Simulaciones gráficas avanzadas renderizadas directamente en terminal usando caracteres ASCII y escape codes.

> **Zero dependencies for core simulations** — solo Python estándar + numpy. La versión web usa Three.js.

---

## 🌌 Agujero Negro (`agujero_negro.py`)

Simulación 3D en tiempo real de un agujero negro con disco de acreción.

**Features:**
- **Disco de acreción** con brazos espirales animados
- **Lente gravitacional** — distorsión de estrellas cercanas al horizonte de eventos
- **Efecto Doppler** — gradiente de temperatura (azul → amarillo → rojo)
- **Rotación orbital** con perspectiva 3D controlable
- **Z-buffer** para oclusión correcta (parte trasera del disco oculta)

**Controles:**
- `↑↓←→` — Rotar cámara
- `Q` — Salir

```bash
python agujero_negro.py
```

https://github.com/user-attachments/assets/blackhole-demo.mp4

---

## 🎤 Visualizador de Audio (`visualizador.py`)

Visualizador de forma de onda en tiempo real con calibración automática.

**Features:**
- **Calibración automática** de umbral de ruido y rango de voz
- **Noise gate** — silencia cuando no hay audio
- **Suavizado físico** — inercia en las barras para movimiento orgánico
- **Gradiente de color** — blanco (centro) → cyan → azul (exterior)

**Requisitos:**
```bash
pip install sounddevice numpy
```

**Uso:**
```bash
python visualizador.py
```

---

## 🪐 Sistema Solar Web (`sistema-solar-web/`)

Simulación 3D interactiva del sistema solar usando Three.js.

**Features:**
- Órbitas proporcionales con velocidades reales escaladas
- Texturas planetarias (sol, mercurio, venus, tierra, marte, júpiter, saturno)
- **Post-processing bloom** para el sol
- Labels orbitales que siguen planetas en 3D
- Controles de órbita (zoom, rotar, pan)

```bash
cd sistema-solar-web
npm install
npm run dev
```

---

## Tech Stack

| Componente | Tecnología |
|------------|------------|
| Terminal rendering | Python `curses` + escape codes |
| Matemáticas 3D | Numpy (proyección perspectiva manual) |
| Audio | `sounddevice` (portaudio bindings) |
| Web 3D | Three.js + Vite |

---

## Por qué esto existe

Demostración de que la "computación gráfica" no requiere GPUs ni motores complejos. Con:
- Proyección perspectiva manual (matrices 4×4 no requeridas)
- Z-buffer en software
- Física de partículas simplificada
- Señales de audio procesadas en bloques

Todo renderizado a **30 FPS en una terminal**.

---

## Licencia

MIT — Usa, modifica, rompe.
