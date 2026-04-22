import curses
import numpy as np
import time
import math
import signal
import random

# Configuración
FPS = 30
FRAME_DELAY = int(1000 / FPS)

class AgujeroNegro:
    def __init__(self):
        self.running = True
        self.time = 0.0
        self.stdscr = None
        signal.signal(signal.SIGINT, self.signal_handler)
        
        # Generar mapa de materia para DISCO COMPLETO (sin huecos)
        self.num_anillos = 80  # Más anillos para mayor densidad
        self.num_sectores = 360  # Un sector por grado para cobertura total
        self.materia = np.zeros((self.num_anillos, self.num_sectores))
        
        # Crear disco COMPLETO con brazos espirales superpuestos
        for r_idx in range(self.num_anillos):
            r_norm = r_idx / self.num_anillos
            for theta_idx in range(self.num_sectores):
                theta = (theta_idx / self.num_sectores) * 2 * math.pi
                
                # ESPIRALES: Dos brazos espirales bien definidos
                dist_1 = (theta - 4.5 * r_norm) % (2 * math.pi)
                val_1 = math.exp(-4 * min((dist_1 - math.pi)**2, (dist_1 + math.pi)**2))
                
                dist_2 = (theta - 4.5 * r_norm + math.pi) % (2 * math.pi)
                val_2 = math.exp(-4 * min((dist_2 - math.pi)**2, (dist_2 + math.pi)**2))
                
                intensidad_espirales = max(val_1, val_2)
                
                # DISCO CENTRAL: ELIMINADO para evitar "círculo estático"
                # Ahora todo es espiral, lo que hará que el borde interior se mueva y rote
                
                # Zona general: Espirales + Ruido
                ruido = random.random() * 0.15
                self.materia[r_idx, theta_idx] = intensidad_espirales + ruido
                
                # AJUSTE 5: Relleno central RUIDOSO
                # Para que el anillo amarillo se vea alrededor de TODO el agujero, no solo en las alas
                # CORRECCIÓN: Reducir radio para que NO llegue a la zona roja (r_factor > 1.5)
                # r_factor = 1.05 + r_norm * 6.5. Queremos r_factor < 1.5 => r_norm < 0.07
                if r_norm < 0.08: 
                    # Base aleatoria para que no sea un círculo perfecto, pero rellene los huecos
                    relleno = 0.3 + random.random() * 0.4
                    self.materia[r_idx, theta_idx] = max(self.materia[r_idx, theta_idx], relleno)

        # Fondo de estrellas
        self.num_stars = 100
        self.stars = []
        for _ in range(self.num_stars):
            self.stars.append({
                'x': random.random(),
                'y': random.random(),
                'brightness': random.random(),
                'speed': random.random() * 0.0005 + 0.0001
            })
        
        # MEJORA: Acreción Variable - Hotspots que se mueven
        self.num_hotspots = 3
        self.hotspots = []
        for _ in range(self.num_hotspots):
            self.hotspots.append({
                'angle': random.random() * 2 * math.pi,
                'radius': random.random() * 0.3,
                'intensity': 0.5 + random.random() * 0.5,
                'lifetime': random.random() * 5.0
            })

    def signal_handler(self, sig, frame):
        self.running = False
    
    def run(self, stdscr):
        self.stdscr = stdscr
        curses.curs_set(0)
        curses.use_default_colors()
        curses.start_color()
        stdscr.nodelay(True)
        
        # Paleta "Cosmic" vibrante
        curses.init_pair(1, curses.COLOR_BLACK, -1)    # Vacío
        curses.init_pair(2, curses.COLOR_MAGENTA, -1)  # Núcleo caliente
        curses.init_pair(3, curses.COLOR_CYAN, -1)     # Medio brillante
        curses.init_pair(4, curses.COLOR_WHITE, -1)    # Bordes resplandecientes
        curses.init_pair(5, curses.COLOR_BLUE, -1)     # Lente
        curses.init_pair(6, curses.COLOR_RED, -1)      # Disco exterior frío
        curses.init_pair(7, curses.COLOR_YELLOW, -1)   # Disco medio
        
        # Ángulo de cámara DE FRENTE con ligera inclinación para ver 3D (30 grados)
        pitch = math.radians(30)  # Inclinación suave para ver profundidad
        yaw = math.radians(0)     # Sin rotación lateral, vista frontal
        
        cos_pitch = math.cos(pitch)
        sin_pitch = math.sin(pitch)
        cos_yaw = math.cos(yaw)
        sin_yaw = math.sin(yaw)
        
        while self.running:
            c = stdscr.getch()
            if c == ord('q'):
                self.running = False
                break
            elif c == curses.KEY_UP:
                pitch = min(pitch + 0.05, math.pi/2)
            elif c == curses.KEY_DOWN:
                pitch = max(pitch - 0.05, -math.pi/2)
            elif c == curses.KEY_LEFT:
                yaw -= 0.05
            elif c == curses.KEY_RIGHT:
                yaw += 0.05
            
            # Recalcular trig
            cos_pitch = math.cos(pitch)
            sin_pitch = math.sin(pitch)
            cos_yaw = math.cos(yaw)
            sin_yaw = math.sin(yaw)
            
            stdscr.erase()
            height, width = stdscr.getmaxyx()
            center_x = width // 2
            center_y = height // 2
            
            # --- MEJORA 1: EFECTO "RESPIRACIÓN" (PULSO) ---
            pulso = math.sin(self.time * 1.5) * 0.05 + 1.0
            radio_esfera = min(height, width // 2) * 0.18 * pulso
            z_buffer = {}
            
            # --- MEJORA 2: ESTRELLAS "WARP SPEED" CON LENTE GRAVITACIONAL ---
            for star in self.stars:
                dx = star['x'] - 0.5
                dy = star['y'] - 0.5
                dist = math.sqrt(dx*dx + dy*dy)
                
                speed = (dist * 0.05) + 0.002
                
                if dist > 0:
                    star['x'] += (dx / dist) * speed
                    star['y'] += (dy / dist) * speed
                
                if star['x'] < 0 or star['x'] > 1 or star['y'] < 0 or star['y'] > 1:
                    angle = random.random() * 2 * math.pi
                    r_start = random.random() * 0.1
                    star['x'] = 0.5 + r_start * math.cos(angle)
                    star['y'] = 0.5 + r_start * math.sin(angle)
                
                sx = int(star['x'] * width)
                sy = int(star['y'] * height)
                
                # LENTE GRAVITACIONAL: Distorsionar estrellas cerca del agujero
                dx_screen = sx - center_x
                dy_screen = sy - center_y
                dist_screen = math.sqrt((dx_screen/2)**2 + dy_screen**2)
                
                if dist_screen < radio_esfera * 3:
                    # Curvatura gravitacional
                    factor_curva = (radio_esfera * 2.5 - dist_screen) / (radio_esfera * 2.5)
                    if factor_curva > 0:
                        angle_screen = math.atan2(dy_screen, dx_screen/2)
                        angle_screen += factor_curva * 0.5
                        sx = int(center_x + dist_screen * 2 * math.cos(angle_screen))
                        sy = int(center_y + dist_screen * math.sin(angle_screen))
                
                if 0 <= sy < height and 0 <= sx < width:
                    if random.random() > 0.1:
                        char = '.' if star['brightness'] < 0.5 else '·'
                        try:
                            stdscr.addch(sy, sx, char, curses.color_pair(4) | curses.A_DIM)
                        except:
                            pass
            
            # --- MEJORA 3: ACRECIÓN VARIABLE (Actualizar hotspots) ---
            for hotspot in self.hotspots:
                hotspot['lifetime'] -= 0.05
                if hotspot['lifetime'] <= 0:
                    # Regenerar hotspot
                    hotspot['angle'] = random.random() * 2 * math.pi
                    hotspot['radius'] = random.random() * 0.3
                    hotspot['intensity'] = 0.5 + random.random() * 0.5
                    hotspot['lifetime'] = random.random() * 5.0
            
            # --- 1. CALCULAR PARTÍCULAS DEL DISCO PRIMERO ---
            particulas_disco = []
            
            for r_idx in range(self.num_anillos):
                r_factor = 1.05 + (r_idx / self.num_anillos) * 6.5  # Alas GRANDES, anillo central PEQUEÑO
                r = radio_esfera * r_factor
                
                # Rotación sólida uniforme (mantiene las espirales coherentes)
                velocidad_angular = 2.0  # Velocidad constante para todos los radios
                angulo_rotacion = self.time * velocidad_angular
                
                # Paso angular más fino para densidad
                for theta_deg in range(0, 360, 1):
                    theta_idx = int((theta_deg / 360) * self.num_sectores) % self.num_sectores
                    
                    intensidad = self.materia[r_idx, theta_idx]
                    
                    # Definir theta_rad primero
                    theta_rad = math.radians(theta_deg)
                    
                    # ACRECIÓN VARIABLE: Aplicar boost de hotspots
                    r_norm = r_idx / self.num_anillos
                    for hotspot in self.hotspots:
                        # Distancia angular al hotspot
                        diff_angle = abs(theta_rad - hotspot['angle'])
                        diff_angle = min(diff_angle, 2*math.pi - diff_angle)
                        diff_radius = abs(r_norm - hotspot['radius'])
                        
                        # Si está cerca del hotspot, aumentar intensidad
                        if diff_angle < 0.5 and diff_radius < 0.1:
                            boost = hotspot['intensity'] * (1.0 - diff_angle/0.5) * (1.0 - diff_radius/0.1)
                            intensidad += boost
                    
                    if intensidad < 0.2: continue  # Solo espirales y disco central
                    
                    theta_actual = theta_rad + angulo_rotacion
                    
                    # Coordenadas 3D - DISCO HORIZONTAL (en plano XZ)
                    x_disk = r * math.cos(theta_actual)
                    z_disk = r * math.sin(theta_actual)
                    # Grosor mínimo del disco
                    y_disk = (intensidad - 0.5) * 0.1 * radio_esfera
                    
                    # Rotación de cámara (pitch y yaw)
                    # Primero rotar en Y (yaw)
                    x_yaw = x_disk * cos_yaw - z_disk * sin_yaw
                    z_yaw = x_disk * sin_yaw + z_disk * cos_yaw
                    
                    # Luego rotar en X (pitch)
                    x_rot = x_yaw
                    y_rot = y_disk * cos_pitch - z_yaw * sin_pitch
                    z_rot = y_disk * sin_pitch + z_yaw * cos_pitch
                    
                    # Proyección perspectiva
                    dist_cam = radio_esfera * 8
                    if z_rot > dist_cam: continue
                    
                    factor = dist_cam / (dist_cam + z_rot)
                    
                    # Proyección en pantalla
                    x_screen = int(center_x + x_rot * factor * 2.0)
                    y_screen = int(center_y + y_rot * factor * 1.0)
                    
                    if 0 <= y_screen < height and 0 <= x_screen < width:
                        particulas_disco.append({
                            'x': x_screen,
                            'y': y_screen,
                            'z': z_rot,
                            'intensidad': intensidad,
                            'r_factor': r_factor,
                            'x_rot': x_rot,
                            'y_rot': y_rot,
                            'z_disk': z_disk  # Guardar Z original del disco
                        })
            
            # --- 2. RENDERIZAR ESFERA NEGRA (HORIZONTE) ---
            r_visual = int(radio_esfera)
            for y_off in range(-r_visual, r_visual + 1):
                x_span = int(math.sqrt(max(0, radio_esfera**2 - y_off**2)) * 2)
                for x_off in range(-x_span, x_span + 1):
                    y = center_y + y_off
                    x = center_x + x_off
                    
                    if 0 <= y < height and 0 <= x < width:
                        r2 = (x_off/2)**2 + y_off**2
                        if r2 <= radio_esfera**2:
                            # Z de la superficie de la esfera
                            z_surf = -math.sqrt(max(0, radio_esfera**2 - r2))
                            z_buffer[(y, x)] = z_surf
                            try:
                                stdscr.addch(y, x, ' ', curses.color_pair(1))
                            except:
                                pass
            
            # --- 3. RENDERIZAR PARTÍCULAS DEL DISCO (solo las visibles) ---
            for p in particulas_disco:
                x_screen = p['x']
                y_screen = p['y']
                z_rot = p['z']
                intensidad = p['intensidad']
                r_factor = p['r_factor']
                z_disk = p['z_disk']
                
                # Verificar si está tapado por la esfera negra
                current_z = z_buffer.get((y_screen, x_screen), float('inf'))
                
                # Solo renderizar si está DELANTE de la esfera
                if z_rot < current_z:
                    # Oclusión adicional: verificar si está dentro del círculo de la esfera
                    dx = x_screen - center_x
                    dy = y_screen - center_y
                    dist_2d = math.sqrt((dx/2)**2 + dy**2)
                    
                    # Si está dentro del radio de la esfera Y la parte del disco está detrás, ocultar
                    if dist_2d < radio_esfera * 0.95:
                        # Verificar si esta parte del disco está en la parte trasera (z_disk > 0)
                        if z_disk > 0:
                            continue
                    
                    # Color y carácter basado en intensidad y radio
                    # Gradiente de temperatura: Azul (caliente/centro) -> Amarillo -> Rojo (frío/borde)
                    # Color y carácter basado en intensidad y radio
                    # Gradiente de temperatura: Azul (caliente/centro) -> Amarillo -> Rojo (frío/borde)
                    # AJUSTE 4: Extender MÁS el anillo amarillo (petición usuario)
                    if r_factor < 1.08:
                        color = 3 # Cyan/Azul (Borde interior, 1-2 chars)
                    elif r_factor < 1.5: # Antes 1.25, ahora 1.5 para llenar más el centro
                        color = 7 # Amarillo (Bastante más extendido)
                    else:
                        color = 6 # Rojo (Disco exterior frío)
                    
                    # Sobreescribir para mantener el estilo "Todo Azul" si se prefiere, 
                    # pero el usuario pidió mejoras visuales. Vamos a probar el gradiente.
                    # Si se ve mal, volvemos al azul.
                    # color = 3
                    
                    # --- MEJORAS FÍSICAS REVERTIDAS ---
                    # Volvemos a la intensidad base sin doppler ni turbulencia extra
                    
                    # Caracteres simples (Estilo original)
                    if intensidad > 0.7:
                        # SIN ANILLO SÓLIDO - Solo textura suave
                        if r_factor < 1.2:
                            char = '▓'
                        else:
                            char = '▒'
                    elif intensidad > 0.4:
                        char = '▒'
                    else:
                        char = '░'
                    
                    try:
                        attr = curses.color_pair(color)
                        # Partes delanteras más brillantes
                        if z_disk < 0:
                            attr |= curses.A_BOLD
                        else:
                            attr |= curses.A_DIM
                        
                        stdscr.addch(y_screen, x_screen, char, attr)
                        z_buffer[(y_screen, x_screen)] = z_rot
                    except:
                        pass

            # --- 4. JETS RELATIVISTAS (DESACTIVADOS) ---
            # El usuario no quiere las líneas verticales
            # jet_length = int(radio_esfera * 8)
            # jet_width = max(1, int(radio_esfera * 0.3))
            # ... (código comentado)

            # --- HUD ---
            try:
                stdscr.addstr(0, 2, "AGUJERO NEGRO V4 - Flechas: Rotar | Q: Salir", curses.A_BOLD | curses.color_pair(4))
                # Debug info
                # stdscr.addstr(1, 2, f"Pitch: {pitch:.2f} Yaw: {yaw:.2f}", curses.A_DIM)
            except:
                pass

            stdscr.refresh()
            curses.napms(FRAME_DELAY)
            self.time += 0.05

def main():
    try:
        agujero = AgujeroNegro()
        curses.wrapper(agujero.run)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
