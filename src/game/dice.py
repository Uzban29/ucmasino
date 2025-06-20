import pygame
import sys
import os
import random

# Conexión a la base de datos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.db.database import get_user, update_points

# --- Paleta de colores estilo Balatro ---
BG_COLOR = (15, 25, 35)
PANEL_COLOR = (25, 40, 55)
ACCENT_COLOR = (229, 48, 83)
SECONDARY_COLOR = (255, 215, 0)
TEXT_COLOR = (240, 240, 240)
GREEN = (80, 220, 120)
RED = (220, 80, 60)
BLUE = (80, 180, 255)
PURPLE = (170, 90, 220)
CHIP_COLORS = [(255,255,255), (80,180,255), (80,220,120), (255,215,0), (229,48,83)]
NEON_COLORS = [ACCENT_COLOR, SECONDARY_COLOR, BLUE, GREEN, PURPLE]

FONT_PATH = os.path.join("src", "assets", "BigBlue.ttf")

APUESTAS = [
    ("Pass Line", "Ganas si el primer tiro es 7 u 11, pierdes con 2, 3 o 12.", GREEN, 1),
    ("Don't Pass", "Ganas con 2 o 3, pierdes con 7 u 11, empate con 12.", RED, 1),
    ("Field", "Ganas con 2, 3, 4, 9, 10, 11 o 12.", BLUE, 1),
    ("Any Craps", "Ganas con 2, 3 o 12. Pago 7:1", PURPLE, 7),
    ("Seven", "Ganas con 7. Pago 4:1", SECONDARY_COLOR, 4),
]

CHIP_VALUES = [1, 10, 100, 1000]

def draw_text(surface, text, font, color, pos, centered=False, shadow=False, shadow_color=(0,0,0)):
    if shadow:
        txt = font.render(text, True, shadow_color)
        shadow_pos = (pos[0]+2, pos[1]+2) if not centered else (pos[0]-txt.get_width()//2+2, pos[1]-txt.get_height()//2+2)
        surface.blit(txt, shadow_pos)
    txt = font.render(text, True, color)
    if centered:
        pos = (pos[0] - txt.get_width() // 2, pos[1] - txt.get_height() // 2)
    surface.blit(txt, pos)

def neon_glow(surface, rect, color, intensity=6, radius=12):
    """Dibuja un resplandor neon alrededor de un rectángulo."""
    glow = pygame.Surface((rect.width+radius*2, rect.height+radius*2), pygame.SRCALPHA)
    for i in range(intensity, 0, -1):
        alpha = int(120 * (i/intensity) * 0.18)
        pygame.draw.rect(
            glow,
            (*color, alpha),
            (radius-i, radius-i, rect.width+2*i, rect.height+2*i),
            border_radius=rect.height//2
        )
    surface.blit(glow, (rect.x-radius, rect.y-radius), special_flags=pygame.BLEND_RGBA_ADD)

def neon_circle(surface, center, radius, color, intensity=6):
    """Dibuja un resplandor neon alrededor de un círculo."""
    for i in range(intensity, 0, -1):
        alpha = int(120 * (i/intensity) * 0.18)
        pygame.draw.circle(surface, (*color, alpha), center, radius+i)

def draw_arrow(surface, center, direction="left", color=(60,80,110)):
    x, y = center
    if direction == "left":
        points = [(x+10, y-14), (x-10, y), (x+10, y+14)]
    else:
        points = [(x-10, y-14), (x+10, y), (x-10, y+14)]
    pygame.draw.polygon(surface, color, points)

def draw_chip_with_arrows(surface, center, value, selected=False, idx=0):
    color = CHIP_COLORS[idx % len(CHIP_COLORS)]
    if selected:
        neon_circle(surface, center, 44, NEON_COLORS[idx % len(NEON_COLORS)], 8)
    pygame.draw.circle(surface, color, center, 38)
    pygame.draw.circle(surface, (40,40,60), center, 38, 4)
    if selected:
        pygame.draw.circle(surface, ACCENT_COLOR, center, 44, 4)
    font = pygame.font.Font(FONT_PATH, 22)
    draw_text(surface, str(value), font, (30,30,30), (center[0], center[1]-10), centered=True)
    draw_text(surface, "$", font, (30,30,30), (center[0], center[1]+14), centered=True)
    # Flechas
    draw_arrow(surface, (center[0]-55, center[1]), "left", ACCENT_COLOR if selected else (60,80,110))
    draw_arrow(surface, (center[0]+55, center[1]), "right", ACCENT_COLOR if selected else (60,80,110))

def draw_die(surface, x, y, size, value, angle=0, rolling=False):
    die_surf = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.rect(die_surf, TEXT_COLOR, (0, 0, size, size), border_radius=12)
    pygame.draw.rect(die_surf, (180, 180, 200), (0, 0, size, size), 3, border_radius=12)
    dot_color = (30, 30, 40)
    dot_radius = size // 10
    dots = {
        1: [(0.5,0.5)],
        2: [(0.25,0.25),(0.75,0.75)],
        3: [(0.25,0.25),(0.5,0.5),(0.75,0.75)],
        4: [(0.25,0.25),(0.75,0.25),(0.25,0.75),(0.75,0.75)],
        5: [(0.25,0.25),(0.75,0.25),(0.5,0.5),(0.25,0.75),(0.75,0.75)],
        6: [(0.25,0.25),(0.75,0.25),(0.25,0.5),(0.75,0.5),(0.25,0.75),(0.75,0.75)]
    }
    for dx,dy in dots[value]:
        pygame.draw.circle(die_surf, dot_color, (int(dx*size), int(dy*size)), dot_radius)
    if rolling:
        die_surf = pygame.transform.rotate(die_surf, angle)
    surface.blit(die_surf, (x, y))

def draw_button(surface, rect, text, font, bg_color, fg_color, hover=False):
    neon_glow(surface, rect, bg_color, 8, 16)
    color = tuple(min(255, c+30) for c in bg_color) if hover else bg_color
    pygame.draw.rect(surface, color, rect, border_radius=12)
    pygame.draw.rect(surface, (60, 80, 110), rect, 2, border_radius=12)
    txt = font.render(text, True, fg_color)
    txt_rect = txt.get_rect(center=rect.center)
    surface.blit(txt, txt_rect)

def main(usuario):
    pygame.init()
    WIDTH, HEIGHT = 1600, 950
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("UCMASINO - Dados Casino")
    clock = pygame.time.Clock()
    
    title_font = pygame.font.Font(FONT_PATH, 44)
    main_font = pygame.font.Font(FONT_PATH, 28)
    small_font = pygame.font.Font(FONT_PATH, 20)
    tiny_font = pygame.font.Font(FONT_PATH, 16)

    user_data = get_user(usuario)
    puntos = int(user_data["puntos"]) if user_data else 1000

    apuesta_idx = 0
    selected_chips = set([1])  # Por defecto la de 10 seleccionada
    apuesta_actual = [v for v in CHIP_VALUES]
    resultado = ""
    dados = [1, 1]
    animando = False
    anim_frames = 0
    die_angles = [0, 0]
    die_speeds = [0, 0]
    ganancia = 0
    mouse_pos = (0, 0)

    # Probabilidades y pagos para mostrar en el panel de apuesta
    PROBABILIDADES = {
        "Pass Line": ("Prob: 8/36 (22%)", "Pago: 1:1"),
        "Don't Pass": ("Prob: 3/36 (8%)", "Pago: 1:1"),
        "Field": ("Prob: 16/36 (44%)", "Pago: 1:1"),
        "Any Craps": ("Prob: 4/36 (11%)", "Pago: 7:1"),
        "Seven": ("Prob: 6/36 (17%)", "Pago: 4:1"),
    }

    # Combinaciones de dados para mostrar en la tabla
    DICE_COMBOS = {
        "Pass Line": "7, 11 (Gana) | 2, 3, 12 (Pierde)",
        "Don't Pass": "2, 3 (Gana) | 7, 11 (Pierde) | 12 (Empate)",
        "Field": "2, 3, 4, 9, 10, 11, 12 (Gana)",
        "Any Craps": "2, 3, 12 (Gana)",
        "Seven": "7 (Gana)",
    }

    def dibujar_ui():
        w, h = screen.get_size()
        center_x, center_y = w // 2, h // 2

        # Fondo degradado
        screen.fill(BG_COLOR)
        for i in range(200, 0, -20):
            alpha = max(0, 100 - i//2)
            highlight = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.circle(highlight, (50, 80, 120, alpha), (center_x, center_y), i)
            screen.blit(highlight, (0, 0))

        # Panel usuario
        pygame.draw.rect(screen, PANEL_COLOR, (20, 80, w-40, 70), border_radius=10)
        pygame.draw.rect(screen, (60, 80, 110), (20, 80, w-40, 70), 2, border_radius=10)
        draw_text(screen, f"Jugador: {usuario}", main_font, TEXT_COLOR, (40, 90))
        draw_text(screen, f"Saldo: ${puntos}", main_font, SECONDARY_COLOR, (40, 120))

        # Mensaje de resultado a la derecha del panel usuario
        mensaje_y = 90
        if resultado:
            color = GREEN if ganancia > 0 else RED if ganancia < 0 else TEXT_COLOR
            draw_text(
                screen, resultado, main_font, color,
                (w-420, mensaje_y), shadow=True
            )
            if ganancia != 0:
                signo = "+" if ganancia > 0 else ""
                ganancia_text = f"{signo}${abs(ganancia)}"
                draw_text(screen, ganancia_text, main_font, color, (w-420, mensaje_y+30), shadow=True)

        # --- FICHAS ARRIBA DEL BOX DE TIPOS DE APUESTA ---
        tabla_h = max(320, h//3)
        tabla_y = h - tabla_h - 20
        chip_space = 145
        chips_total_w = (len(CHIP_VALUES)-1) * chip_space
        chips_start_x = 60 + (w-120-chips_total_w)//2  # centrado respecto a la tabla, no a la pantalla
        chips_y = tabla_y - 60  # justo arriba del box de tipos de apuesta

        for i, val in enumerate(CHIP_VALUES):
            chip_x = chips_start_x + i * chip_space
            selected = (i in selected_chips)
            draw_chip_with_arrows(screen, (chip_x, chips_y), apuesta_actual[i], selected, i)

        # --- DADOS CENTRADOS Y MÁS ARRIBA ---
        die_size = 110
        die_y = 210  # Más arriba
        die1_x = center_x - die_size - 20
        die2_x = center_x + 20
        draw_die(screen, die1_x, die_y, die_size, dados[0], die_angles[0], animando)
        draw_die(screen, die2_x, die_y, die_size, dados[1], die_angles[1], animando)

        # --- BOTÓN DE APOSTAR DEBAJO DEL MENSAJE DE RESULTADO ---
        btn_lanzar_y = mensaje_y + 80  # Más separado del mensaje
        btn_lanzar = pygame.Rect(w-420, btn_lanzar_y, 180, 54)
        draw_button(screen, btn_lanzar, "APOSTAR", main_font, ACCENT_COLOR, TEXT_COLOR, btn_lanzar.collidepoint(mouse_pos))

        # --- SELECTOR DE APUESTA ---
        panel_w = 380
        panel_h = 260
        panel_x = 60
        panel_rect = pygame.Rect(panel_x, tabla_y - panel_h - 40, panel_w, panel_h)
        neon_glow(screen, panel_rect, ACCENT_COLOR, 8, 18)
        pygame.draw.rect(screen, PANEL_COLOR, panel_rect, border_radius=16)
        pygame.draw.rect(screen, (60, 80, 110), panel_rect, 2, border_radius=16)

        nombre, desc, color, mult = APUESTAS[apuesta_idx]
        btn_prev = pygame.Rect(panel_x+30, panel_rect.y+30, 40, 40)
        btn_next = pygame.Rect(panel_x+panel_w-70, panel_rect.y+30, 40, 40)
        draw_button(screen, btn_prev, "‹", main_font, BLUE, TEXT_COLOR, btn_prev.collidepoint(mouse_pos))
        draw_button(screen, btn_next, "›", main_font, BLUE, TEXT_COLOR, btn_next.collidepoint(mouse_pos))
        draw_text(screen, nombre, main_font, color, (panel_x+panel_w//2, panel_rect.y+50), centered=True, shadow=True)

        prob, pago = PROBABILIDADES[nombre]
        draw_text(screen, prob, small_font, SECONDARY_COLOR, (panel_x+30, panel_rect.y+90))
        draw_text(screen, pago, small_font, ACCENT_COLOR, (panel_x+30, panel_rect.y+120))
        monto_total = sum(apuesta_actual[i] for i in selected_chips)
        draw_text(screen, f"Monto: ${monto_total}", main_font, TEXT_COLOR, (panel_x+30, panel_rect.y+170))

        # --- TABLA DE APUESTAS EN UNA SOLA COLUMNA, INTERLINEADO MÁS JUNTO Y "Pago" MÁS A LA DERECHA ---
        tabla_rect = pygame.Rect(60, tabla_y, w-120, tabla_h)
        neon_glow(screen, tabla_rect, BLUE, 8, 18)
        pygame.draw.rect(screen, PANEL_COLOR, tabla_rect, border_radius=16)
        pygame.draw.rect(screen, (60, 80, 110), tabla_rect, 2, border_radius=16)
        draw_text(screen, "TIPOS DE APUESTAS:", main_font, SECONDARY_COLOR, (tabla_rect.x+20, tabla_y+20), shadow=True)
        y = tabla_y+70
        espacio_vertical = 38  # Más junto
        pago_x = tabla_rect.x + tabla_rect.width - 180  # Pago más a la derecha
        for nombre, desc, color, mult in APUESTAS:
            combos = DICE_COMBOS[nombre]
            draw_text(screen, f"• {nombre}", small_font, color, (tabla_rect.x+20, y), shadow=True)
            draw_text(screen, combos, small_font, BLUE, (tabla_rect.x+180, y))
            draw_text(screen, f"Pago: {mult}:1", small_font, ACCENT_COLOR, (pago_x, y))
            y += espacio_vertical

        # Título centrado arriba
        draw_text(screen, "UCMASINO - DADOS", title_font, SECONDARY_COLOR, (w//2, 40), centered=True, shadow=True)

    def evaluar_apuesta(apuesta_nombre, suma, monto):
        if apuesta_nombre == "Pass Line":
            if suma in (7, 11):
                return f"¡Ganaste! (Sacaste {suma})", monto
            elif suma in (2, 3, 12):
                return f"Perdiste. (Sacaste {suma})", -monto
            else:
                return f"Empate. (Sacaste {suma})", 0
        elif apuesta_nombre == "Don't Pass":
            if suma in (2, 3):
                return f"¡Ganaste! (Sacaste {suma})", monto
            elif suma in (7, 11):
                return f"Perdiste. (Sacaste {suma})", -monto
            elif suma == 12:
                return f"Empate. (Sacaste {suma})", 0
            else:
                return f"Empate. (Sacaste {suma})", 0
        elif apuesta_nombre == "Field":
            if suma in (2, 3, 4, 9, 10, 11, 12):
                return f"¡Ganaste! (Sacaste {suma})", monto
            else:
                return f"Perdiste. (Sacaste {suma})", -monto
        elif apuesta_nombre == "Any Craps":
            if suma in (2, 3, 12):
                return f"¡Ganaste! (Sacaste {suma})", monto * 7
            else:
                return f"Perdiste. (Sacaste {suma})", -monto
        elif apuesta_nombre == "Seven":
            if suma == 7:
                return f"¡Ganaste! (Sacaste 7)", monto * 4
            else:
                return f"Perdiste. (Sacaste {suma})", -monto
        else:
            return "Apuesta no válida.", 0

    while True:
        mouse_pos = pygame.mouse.get_pos()
        w, h = screen.get_size()
        center_x, center_y = w // 2, h // 2

        # --- PANEL SELECTOR DE APUESTA ---
        panel_w = 380
        panel_h = 260
        panel_x = 60
        tabla_h = max(320, h//3)
        tabla_y = h - tabla_h - 20
        panel_rect = pygame.Rect(panel_x, tabla_y - panel_h - 40, panel_w, panel_h)
        btn_prev = pygame.Rect(panel_x+30, panel_rect.y+30, 40, 40)
        btn_next = pygame.Rect(panel_x+panel_w-70, panel_rect.y+30, 40, 40)

        # Dados centrados y más arriba
        die_size = 110
        die_y = 210
        die1_x = center_x - die_size - 20
        die2_x = center_x + 20

        # Fichas arriba del box de tipos de apuesta
        chip_space = 145
        chips_total_w = (len(CHIP_VALUES)-1) * chip_space
        chips_start_x = 60 + (w-120-chips_total_w)//2
        chips_y = tabla_y - 60
        chip_centers = [(chips_start_x + i * chip_space, chips_y) for i in range(len(CHIP_VALUES))]
        chip_rects = [pygame.Rect(cx-38, cy-38, 76, 76) for cx, cy in chip_centers]
        arrow_left_rects = [pygame.Rect(cx-80, cy-20, 32, 40) for cx, cy in chip_centers]
        arrow_right_rects = [pygame.Rect(cx+48, cy-20, 32, 40) for cx, cy in chip_centers]

        # Botón apostar debajo del mensaje de resultado, bien separado
        mensaje_y = 90
        btn_lanzar_y = mensaje_y + 80
        btn_lanzar = pygame.Rect(w-420, btn_lanzar_y, 180, 54)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    puntos = 1500
                    update_points(usuario, puntos)
            if event.type == pygame.MOUSEBUTTONDOWN and not animando:
                if event.button == 1:
                    # Selección múltiple de fichas
                    for i, rect in enumerate(chip_rects):
                        if rect.collidepoint(mouse_pos):
                            if i in selected_chips:
                                selected_chips.remove(i)
                            else:
                                selected_chips.add(i)
                    # Flechas izquierda
                    for i, rect in enumerate(arrow_left_rects):
                        if rect.collidepoint(mouse_pos):
                            apuesta_actual[i] = max(CHIP_VALUES[i], apuesta_actual[i] - CHIP_VALUES[i])
                    # Flechas derecha
                    for i, rect in enumerate(arrow_right_rects):
                        if rect.collidepoint(mouse_pos):
                            apuesta_actual[i] += CHIP_VALUES[i]
                    # Botón apuesta anterior
                    if btn_prev.collidepoint(mouse_pos):
                        apuesta_idx = (apuesta_idx - 1) % len(APUESTAS)
                    # Botón apuesta siguiente
                    if btn_next.collidepoint(mouse_pos):
                        apuesta_idx = (apuesta_idx + 1) % len(APUESTAS)
                    # Botón lanzar (ahora aquí la función de apostar)
                    monto_total = sum(apuesta_actual[i] for i in selected_chips)
                    if btn_lanzar.collidepoint(mouse_pos) and monto_total <= puntos and selected_chips:
                        animando = True
                        anim_frames = 25
                        resultado = ""
                        ganancia = 0
                        die_speeds[0] = random.randint(18, 28)
                        die_speeds[1] = random.randint(18, 28)
                        die_angles[0] = 0
                        die_angles[1] = 0

        # Animación de dados
        if animando:
            for i in range(2):
                die_angles[i] += die_speeds[i]
                die_speeds[i] = max(2, die_speeds[i] - 2)
            dados = [random.randint(1, 6), random.randint(1, 6)]
            anim_frames -= 1
            if anim_frames == 0:
                animando = False
                suma = sum(dados)
                nombre_apuesta = APUESTAS[apuesta_idx][0]
                monto_total = sum(apuesta_actual[i] for i in selected_chips)
                res, gan = evaluar_apuesta(nombre_apuesta, suma, monto_total)
                resultado = res
                ganancia = gan
                if gan != 0:
                    nuevos_puntos = puntos + gan
                    update_points(usuario, nuevos_puntos)
                    puntos = nuevos_puntos

        dibujar_ui()
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main("jugador_demo")
