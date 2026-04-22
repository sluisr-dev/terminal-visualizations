# Terminal Visualizations

Advanced graphics simulations rendered directly in the terminal using ASCII characters and escape codes.

> **Zero dependencies for core simulations** — just standard Python + numpy. Web version uses Three.js.

---

## 🌌 Black Hole (`agujero_negro.py`)

Real-time 3D simulation of a black hole with accretion disk.

**Features:**
- **Accretion disk** with animated spiral arms
- **Gravitational lensing** — distortion of stars near the event horizon
- **Doppler effect** — temperature gradient (blue → yellow → red)
- **Orbital rotation** with controllable 3D perspective
- **Z-buffer** for correct occlusion (back of disk hidden)

**Controls:**
- `↑↓←→` — Rotate camera
- `Q` — Exit

```bash
python agujero_negro.py
```

https://github.com/user-attachments/assets/blackhole-demo.mp4

---

## 🎤 Audio Visualizer (`visualizador.py`)

Real-time waveform visualizer with automatic calibration.

**Features:**
- **Automatic calibration** of noise threshold and voice range
- **Noise gate** — silences when there's no audio
- **Physical smoothing** — inertia in bars for organic movement
- **Color gradient** — white (center) → cyan → blue (outer)

**Requirements:**
```bash
pip install sounddevice numpy
```

**Usage:**
```bash
python visualizador.py
```

---

## 🪐 Solar System Web (`sistema-solar-web/`)

Interactive 3D solar system simulation using Three.js.

**Features:**
- Proportional orbits with scaled real velocities
- Planetary textures (sun, mercury, venus, earth, mars, jupiter, saturn)
- **Post-processing bloom** for the sun
- Orbital labels that follow planets in 3D
- Orbit controls (zoom, rotate, pan)

```bash
cd sistema-solar-web
npm install
npm run dev
```

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Terminal rendering | Python `curses` + escape codes |
| 3D Math | Numpy (manual perspective projection) |
| Audio | `sounddevice` (portaudio bindings) |
| Web 3D | Three.js + Vite |

---

## Why This Exists

A demonstration that "computer graphics" doesn't require GPUs or complex engines. With:
- Manual perspective projection (no 4×4 matrices required)
- Software Z-buffer
- Simplified particle physics
- Block-processed audio signals

All rendered at **30 FPS in a terminal**.

---

## License

MIT — Use, modify, break.
