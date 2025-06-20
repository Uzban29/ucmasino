import pygame
import sys
import os
import random

# Conexión a la base de datos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.db.database import get_user, add_user, update_points, verify_user

# --- Paleta de colores pixel art ---
BG_COLOR = (24, 24, 32)
PANEL_COLOR = (40, 40, 60)
ACCENT_COLOR = (255, 85, 85)
PIXEL_GREEN = (80, 255, 80)
PIXEL_YELLOW = (255, 255, 120)
PIXEL_BLUE = (80, 180, 255)
PIXEL_WHITE = (240, 240, 240)
PIXEL_RED = (255, 80, 80)

# --- Fuente BigBlue ---
FONT_PATH = os.path.join("src", "assets", "BigBlue.ttf")

# --- Tabla de apuestas ---
APUESTAS = [
    ("Pass Line", "Ganas si el primer tiro es 7 u 11, pierdes con 2, 3 o 12."),
    ("Don't Pass", "Ganas con 2 o 3, pierdes con 7 u 11, empate con 12."),
    ("Field", "Ganas con 2, 3, 4, 9, 10, 11 o 12."),
    ("Any Craps", "Ganas con 2, 3 o 12."),
    ("Seven", "Ganas con 7."),
]

def pixel_rect(surface, color, rect, border=0):
    pygame.draw.rect(surface, color, rect, border)
    # Pixel corners
    for dx in [0, rect[2]-1]:
        for dy in [0, rect[3]-1]:
            surface.set_at((rect[0]+dx, rect[1]+dy), color)

def draw_pixel_text(surface, text, font, color, pos):
    txt = font.render(text, True, color)
    surface.blit(txt, pos)

def main(usuario):
    pygame.init()
    WIDTH, HEIGHT = 900, 650
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("UCMASINO - Dados Pixel Art")
    clock = pygame.time.Clock()

    # Fuente pixel art
    font = pygame.font.Font(FONT_PATH, 32)
    small_font = pygame.font.Font(FONT_PATH, 20)
    tiny_font = pygame.font.Font(FONT_PATH, 14)

    # Cargar puntos del usuario
    user_data = get_user(usuario)
    puntos = int(user_data["puntos"]) if user_data else 1000

    apuesta_idx = 0
    apuesta = 10
    resultado = ""
    dados = [1, 1]
    animando = False
    anim_frames = 0

    def dibujar_ui():
        screen.fill(BG_COLOR)
        # Título pixel art
        draw_pixel_text(screen, "UCMASINO - Dados", font, PIXEL_YELLOW, (WIDTH//2-220, 20))
        # Saldo
        draw_pixel_text(screen, f"Saldo de {usuario}: ${puntos}", small_font, PIXEL_GREEN, (40, 70))
        # Apuesta seleccionada
        draw_pixel_text(screen, f"Apuesta: {APUESTAS[apuesta_idx][0]}", small_font, PIXEL_WHITE, (40, 110))
        # Selector de apuesta
        pixel_rect(screen, PANEL_COLOR, (40, 150, 300, 50), 0)
        draw_pixel_text(screen, f"Monto: ${apuesta}", small_font, PIXEL_WHITE, (60, 165))
        # Botón menos
        pixel_rect(screen, PIXEL_RED, (200, 155, 40, 40), 0)
        draw_pixel_text(screen, "-", font, BG_COLOR, (210, 155))
        # Botón más
        pixel_rect(screen, PIXEL_GREEN, (260, 155, 40, 40), 0)
        draw_pixel_text(screen, "+", font, BG_COLOR, (270, 155))
        # Botón lanzar
        pixel_rect(screen, ACCENT_COLOR, (350, 155, 120, 40), 0)
        draw_pixel_text(screen, "LANZAR", tiny_font, BG_COLOR, (360, 165))
        # Resultado
        if resultado:
            color = PIXEL_GREEN if "Ganaste" in resultado else PIXEL_RED
            draw_pixel_text(screen, resultado, font, color, (WIDTH//2-120, 220))
        # Dados pixel art
        for i, val in enumerate(dados):
            x = 500 + i*100
            y = 150
            pixel_rect(screen, PIXEL_WHITE, (x, y, 80, 80), 0)
            draw_pixel_text(screen, str(val), font, BG_COLOR, (x+25, y+15))
        # Tabla de apuestas pixel art
        pixel_rect(screen, PANEL_COLOR, (40, 320, 820, 250), 0)
        y = 340
        for nombre, desc in APUESTAS:
            draw_pixel_text(screen, nombre, small_font, PIXEL_YELLOW, (60, y))
            draw_pixel_text(screen, desc, tiny_font, PIXEL_WHITE, (220, y+5))
            y += 40

    def evaluar_apuesta(apuesta, suma, monto):
        if apuesta == "Pass Line":
            if suma in (7, 11):
                return f"¡Ganaste! (Sacaste {suma})", monto
            elif suma in (2, 3, 12):
                return f"Perdiste. (Sacaste {suma})", -monto
            else:
                return f"Empate. (Sacaste {suma})", 0
        elif apuesta == "Don't Pass":
            if suma in (2, 3):
                return f"¡Ganaste! (Sacaste {suma})", monto
            elif suma in (7, 11):
                return f"Perdiste. (Sacaste {suma})", -monto
            elif suma == 12:
                return f"Empate. (Sacaste {suma})", 0
            else:
                return f"Empate. (Sacaste {suma})", 0
        elif apuesta == "Field":
            if suma in (2, 3, 4, 9, 10, 11, 12):
                return f"¡Ganaste! (Sacaste {suma})", monto
            else:
                return f"Perdiste. (Sacaste {suma})", -monto
        elif apuesta == "Any Craps":
            if suma in (2, 3, 12):
                return f"¡Ganaste! (Sacaste {suma})", monto * 7
            else:
                return f"Perdiste. (Sacaste {suma})", -monto
        elif apuesta == "Seven":
            if suma == 7:
                return f"¡Ganaste! (Sacaste 7)", monto * 4
            else:
                return f"Perdiste. (Sacaste {suma})", -monto
        else:
            return "Apuesta no válida.", 0

    # Loop principal
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if not animando:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        apuesta_idx = (apuesta_idx + 1) % len(APUESTAS)
                    if event.key == pygame.K_LEFT:
                        apuesta_idx = (apuesta_idx - 1) % len(APUESTAS)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    # Botón menos
                    if 200 <= mx <= 240 and 155 <= my <= 195 and apuesta > 1:
                        apuesta -= 1
                    # Botón más
                    if 260 <= mx <= 300 and 155 <= my <= 195 and apuesta < puntos:
                        apuesta += 1
                    # Botón lanzar
                    if 350 <= mx <= 470 and 155 <= my <= 195 and apuesta <= puntos:
                        animando = True
                        anim_frames = 20
                        resultado = ""

        if animando:
            dados = [random.randint(1, 6), random.randint(1, 6)]
            anim_frames -= 1
            if anim_frames == 0:
                animando = False
                suma = sum(dados)
                nombre_apuesta = APUESTAS[apuesta_idx][0]
                res, ganancia = evaluar_apuesta(nombre_apuesta, suma, apuesta)
                resultado = res
                # Actualiza puntos en la base de datos
                if ganancia > 0:
                    update_points(usuario, puntos + ganancia)
                elif ganancia < 0:
                    update_points(usuario, puntos + ganancia)
                # Refresca puntos
                user_data = get_user(usuario)
                puntos = int(user_data["puntos"]) if user_data else puntos

        dibujar_ui()
        pygame.display.flip()
        clock.tick(30)
