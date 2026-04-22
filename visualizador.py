import curses
import sounddevice as sd
import numpy as np
import time
import signal
import sys

# Configuración
SAMPLE_RATE = 44100
BLOCK_SIZE = 2048
CALIBRATION_SILENCE_TIME = 1.0
CALIBRATION_VOICE_TIME = 2.0
AMPLITUD_VISUAL = 16.0  # Ligeramente aumentado para mejor visibilidad
SUAVIZADO_GLOBAL = 0.25  # Más rápido para palabras cortas (era 0.15)
SUAVIZADO_LOCAL = 0.6

class Visualizador:
    def __init__(self):
        self.running = True
        self.audio_buffer = np.zeros(BLOCK_SIZE)
        self.umbral_ruido = 0.02
        self.rango_voz_max = 0.3
        self.prev_heights = []
        self.velocidades = []
        self.nivel_voz_actual = 0.0
        self.calibrando_silencio = True
        self.calibrando_voz = False
        self.muestras_silencio = []
        self.muestras_voz = []
        self.stdscr = None
        
        # Configurar manejador de señales para Ctrl+C
        signal.signal(signal.SIGINT, self.signal_handler)
    
    def signal_handler(self, sig, frame):
        """Manejador para Ctrl+C"""
        self.running = False
        if self.stdscr:
            try:
                height, width = self.stdscr.getmaxyx()
                self.stdscr.erase()
                msg = "Saliendo..."
                self.stdscr.addstr(height // 2, (width - len(msg)) // 2, msg, curses.A_BOLD)
                self.stdscr.refresh()
                curses.napms(500)
            except:
                pass

    def audio_callback(self, indata, frames, time_info, status):
        if status:
            pass
        
        # Guardar buffer completo de forma de onda
        self.audio_buffer = indata[:, 0].copy()
        
        # Calibración de silencio
        if self.calibrando_silencio:
            rms = np.sqrt(np.mean(indata**2))
            self.muestras_silencio.append(rms)
        
        # Calibración de voz
        if self.calibrando_voz:
            rms = np.sqrt(np.mean(indata**2))
            self.muestras_voz.append(rms)

    def calibrar(self, stdscr):
        """Calibración en dos pasos: silencio y voz."""
        height, width = stdscr.getmaxyx()
        
        # Paso 1: Calibrar silencio
        stdscr.erase()
        msg1 = "Paso 1/2: Calibrando silencio..."
        msg2 = "(Permanece en silencio)"
        stdscr.addstr(height // 2 - 1, (width - len(msg1)) // 2, msg1, curses.A_BOLD)
        stdscr.addstr(height // 2 + 1, (width - len(msg2)) // 2, msg2)
        stdscr.refresh()
        
        time.sleep(CALIBRATION_SILENCE_TIME)
        
        if self.muestras_silencio:
            promedio = np.mean(self.muestras_silencio)
            desviacion = np.std(self.muestras_silencio)
            self.umbral_ruido = promedio + (desviacion * 2.5)
        
        self.calibrando_silencio = False
        
        # Paso 2: Calibrar voz
        stdscr.erase()
        msg1 = "Paso 2/2: Calibrando tu voz..."
        msg2 = "(Habla normalmente durante 2 segundos)"
        stdscr.addstr(height // 2 - 1, (width - len(msg1)) // 2, msg1, curses.A_BOLD)
        stdscr.addstr(height // 2 + 1, (width - len(msg2)) // 2, msg2, curses.color_pair(2))
        stdscr.refresh()
        
        self.calibrando_voz = True
        time.sleep(CALIBRATION_VOICE_TIME)
        self.calibrando_voz = False
        
        # Calcular rango de voz
        if self.muestras_voz:
            # Filtrar solo las muestras que superan el umbral de ruido
            muestras_voz_limpia = [m for m in self.muestras_voz if m > self.umbral_ruido]
            if muestras_voz_limpia:
                # Usar el percentil 70 como referencia (balance)
                self.rango_voz_max = np.percentile(muestras_voz_limpia, 70)

    def run(self, stdscr):
        self.stdscr = stdscr  # Guardar referencia para el manejador de señales
        curses.curs_set(0)
        curses.use_default_colors()
        curses.start_color()
        stdscr.nodelay(True)
        
        # Colores
        curses.init_pair(1, curses.COLOR_WHITE, -1)
        curses.init_pair(2, curses.COLOR_CYAN, -1)
        curses.init_pair(3, curses.COLOR_BLUE, -1)

        try:
            stream = sd.InputStream(
                callback=self.audio_callback, 
                channels=1, 
                samplerate=SAMPLE_RATE, 
                blocksize=BLOCK_SIZE
            )
            stream.start()
        except Exception as e:
            stdscr.addstr(0, 0, f"Error: {e}")
            stdscr.refresh()
            curses.napms(3000)
            return

        # Calibración inicial
        self.calibrar(stdscr)

        while self.running:
            c = stdscr.getch()
            if c == ord('q'):
                self.running = False
                break

            stdscr.erase()
            height, width = stdscr.getmaxyx()
            center_y = height // 2

            # Obtener snapshot del buffer
            data = self.audio_buffer.copy()
            
            # Calcular RMS global para noise gate
            rms_global = np.sqrt(np.mean(data**2))
            
            # Inicializar arrays si es necesario (ANTES de usarlos)
            if len(self.prev_heights) != width:
                self.prev_heights = [0] * width
                self.velocidades = [0.0] * width
            
            # Calcular nivel objetivo
            if rms_global < self.umbral_ruido:
                nivel_objetivo = 0.0
            else:
                nivel_voz_crudo = max(0, rms_global - self.umbral_ruido)
                nivel_voz_normalizado = min(1.0, nivel_voz_crudo / self.rango_voz_max)
                # Curva suave para expansión gradual
                nivel_objetivo = np.power(nivel_voz_normalizado, 0.7)
            
            # Aplicar rampa suave (aceleración/desaceleración)
            # En lugar de saltar al objetivo, nos acercamos gradualmente
            self.nivel_voz_actual += (nivel_objetivo - self.nivel_voz_actual) * SUAVIZADO_GLOBAL
            
            # Usar el nivel suavizado para toda la visualización
            nivel_voz = self.nivel_voz_actual
            
            # Si no hay voz, mostrar línea plana
            if nivel_voz < 0.01:
                for x in range(width):
                    self.prev_heights[x] = 0
                    self.velocidades[x] = 0
                    try:
                        stdscr.addch(center_y, x, '─', curses.color_pair(3))
                    except curses.error:
                        pass
            else:
                # Distribuir con forma suave
                step = len(data) // width
                if step < 1:
                    step = 1
                
                for x in range(width):
                    # Forma gaussiana para suavidad
                    norm_x = (x - (width / 2)) / (width / 2)
                    forma_base = np.exp(-3 * norm_x**2)
                    
                    # Agregar variación de waveform sutil
                    idx = x * step
                    if idx < len(data):
                        variacion = abs(data[idx]) * 0.2
                    else:
                        variacion = 0
                    
                    # Combinar
                    energia_combinada = (nivel_voz * forma_base * 0.8) + (variacion * 0.2)
                    
                    # Calcular altura objetivo (ajustado al tamaño de terminal)
                    max_altura = height // 2 - 1
                    target_h = int(energia_combinada * AMPLITUD_VISUAL * max_altura / 10.0)
                    target_h = max(0, min(max_altura, target_h))
                    
                    # Suavizado local con velocidad
                    diff = target_h - self.prev_heights[x]
                    self.velocidades[x] += diff * SUAVIZADO_LOCAL
                    self.velocidades[x] *= 0.8  # Fricción
                    self.prev_heights[x] += self.velocidades[x]
                    
                    curr_h = int(self.prev_heights[x])
                    curr_h = max(0, min(max_altura, curr_h))
                    
                    # Dibujar
                    if curr_h > 0:
                        for y_off in range(curr_h):
                            # Color basado en altura (degradado)
                            color = 3  # Azul por defecto
                            if y_off < curr_h * 0.3: 
                                color = 1  # Blanco en centro
                            elif y_off < curr_h * 0.6: 
                                color = 2  # Cyan en medio
                            
                            try:
                                stdscr.addch(center_y - y_off, x, '█', curses.color_pair(color))
                                stdscr.addch(center_y + y_off, x, '█', curses.color_pair(color))
                            except curses.error:
                                pass
                    else:
                        try:
                            stdscr.addch(center_y, x, '─', curses.color_pair(3))
                        except curses.error:
                            pass

            stdscr.refresh()
            curses.napms(30)

        stream.stop()
        stream.close()

def main():
    viz = Visualizador()
    curses.wrapper(viz.run)

if __name__ == "__main__":
    main()
