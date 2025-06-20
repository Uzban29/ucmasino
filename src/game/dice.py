import pygame
import sys
import os
import random
import math

# Conexión a la base de datos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.db.database import get_user, update_points

# --- Paleta de colores estilo Balatro ---
BG_COLOR = (15, 25, 35)
PANEL_COLOR = (25, 40, 55)
ACCENT_COLOR = (229, 48, 83)  # Rojo Balatro
SECONDARY_COLOR = (255, 215, 0)  # Oro Balatro
TEXT_COLOR = (240, 240, 240)
GREEN = (80, 220, 120)
RED = (220, 80, 60)
BLUE = (80, 180, 255)
PURPLE = (170, 90, 220)

# --- Fuentes estilo Balatro ---
FONT_PATH = os.path.join("src", "assets", "BigBlue.ttf")

# --- Tabla de apuestas ---
APUESTAS = [
    ("Pass Line", "Ganas si el primer tiro es 7 u 11, pierdes con 2, 3 o 12.", GREEN, 1),
    ("Don't Pass", "Ganas con 2 o 3, pierdes con 7 u 11, empate con 12.", RED, 1),
    ("Field", "Ganas con 2, 3, 4, 9, 10, 11 o 12.", BLUE, 1),
    ("Any Craps", "Ganas con 2, 3 o 12. Pago 7:1", PURPLE, 7),
    ("Seven", "Ganas con 7. Pago 4:1", SECONDARY_COLOR, 4),
]

def draw_text(surface, text, font, color, pos, centered=False):
    txt = font.render(text, True, color)
    if centered:
        pos = (pos[0] - txt.get_width() // 2, pos[1] - txt.get_height() // 2)
    surface.blit(txt, pos)

def draw_button(surface, rect, text, font, bg_color, text_color, hover=False):
    # Fondo del botón
    pygame.draw.rect(surface, bg_color, rect, border_radius=8)
    
    # Efecto hover
    if hover:
        highlight = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(highlight, (255, 255, 255, 30), (0, 0, rect.width, rect.height), border_radius=8)
        surface.blit(highlight, rect.topleft)
    
    # Borde
    pygame.draw.rect(surface, (100, 100, 120), rect, 2, border_radius=8)
    
    # Texto centrado
    text_surf = font.render(text, True, text_color)
    text_rect = text_surf.get_rect(center=rect.center)
    surface.blit(text_surf, text_rect)

def draw_die(surface, x, y, size, value, rolling=False):
    # Fondo del dado
    pygame.draw.rect(surface, TEXT_COLOR, (x, y, size, size), border_radius=10)
    pygame.draw.rect(surface, (180, 180, 200), (x, y, size, size), 3, border_radius=10)
    
    # Si está rodando, dibujar un efecto de animación
    if rolling:
        pygame.draw.circle(surface, ACCENT_COLOR, (x + size//2, y + size//2), size//4)
        return
    
    # Dibujar puntos según el valor
    dot_color = (30, 30, 40)
    dot_radius = size // 10
    
    if value == 1:
        pygame.draw.circle(surface, dot_color, (x + size//2, y + size//2), dot_radius)
    elif value == 2:
        pygame.draw.circle(surface, dot_color, (x + size//4, y + size//4), dot_radius)
        pygame.draw.circle(surface, dot_color, (x + 3*size//4, y + 3*size//4), dot_radius)
    elif value == 3:
        pygame.draw.circle(surface, dot_color, (x + size//4, y + size//4), dot_radius)
        pygame.draw.circle(surface, dot_color, (x + size//2, y + size//2), dot_radius)
        pygame.draw.circle(surface, dot_color, (x + 3*size//4, y + 3*size//4), dot_radius)
    elif value == 4:
        pygame.draw.circle(surface, dot_color, (x + size//4, y + size//4), dot_radius)
        pygame.draw.circle(surface, dot_color, (x + 3*size//4, y + size//4), dot_radius)
        pygame.draw.circle(surface, dot_color, (x + size//4, y + 3*size//4), dot_radius)
        pygame.draw.circle(surface, dot_color, (x + 3*size//4, y + 3*size//4), dot_radius)
    elif value == 5:
        pygame.draw.circle(surface, dot_color, (x + size//4, y + size//4), dot_radius)
        pygame.draw.circle(surface, dot_color, (x + 3*size//4, y + size//4), dot_radius)
        pygame.draw.circle(surface, dot_color, (x + size//2, y + size//2), dot_radius)
        pygame.draw.circle(surface, dot_color, (x + size//4, y + 3*size//4), dot_radius)
        pygame.draw.circle(surface, dot_color, (x + 3*size//4, y + 3*size//4), dot_radius)
    elif value == 6:
        pygame.draw.circle(surface, dot_color, (x + size//4, y + size//4), dot_radius)
        pygame.draw.circle(surface, dot_color, (x + 3*size//4, y + size//4), dot_radius)
        pygame.draw.circle(surface, dot_color, (x + size//4, y + size//2), dot_radius)
        pygame.draw.circle(surface, dot_color, (x + 3*size//4, y + size//2), dot_radius)
        pygame.draw.circle(surface, dot_color, (x + size//4, y + 3*size//4), dot_radius)
        pygame.draw.circle(surface, dot_color, (x + 3*size//4, y + 3*size//4), dot_radius)

def main(usuario):
    pygame.init()
    WIDTH, HEIGHT = 900, 650
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("UCMASINO - Dados")
    clock = pygame.time.Clock()
    
    # Fuentes estilo Balatro
    title_font = pygame.font.Font(FONT_PATH, 42)
    main_font = pygame.font.Font(FONT_PATH, 28)
    small_font = pygame.font.Font(FONT_PATH, 20)
    tiny_font = pygame.font.Font(FONT_PATH, 16)

    # Cargar puntos del usuario
    user_data = get_user(usuario)
    puntos = int(user_data["puntos"]) if user_data else 1000

    apuesta_idx = 0
    apuesta = 10
    resultado = ""
    dados = [1, 1]
    animando = False
    anim_frames = 0
    total = 0
    ganancia = 0
    mouse_pos = (0, 0)

    # Botones
    botones = [
        {"rect": pygame.Rect(650, 150, 200, 50), "text": "LANZAR", "color": ACCENT_COLOR},
        {"rect": pygame.Rect(300, 150, 40, 40), "text": "-", "color": RED},
        {"rect": pygame.Rect(250, 150, 40, 40), "text": "+", "color": GREEN},
        {"rect": pygame.Rect(100, 150, 40, 40), "text": "<", "color": BLUE},
        {"rect": pygame.Rect(150, 150, 40, 40), "text": ">", "color": BLUE}
    ]

    def dibujar_ui():
        # Fondo con efecto de luz
        screen.fill(BG_COLOR)
        
        # Efecto de luz central
        center_x, center_y = WIDTH // 2, HEIGHT // 2
        for i in range(200, 0, -20):
            alpha = max(0, 100 - i//2)
            highlight = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(highlight, (50, 80, 120, alpha), (center_x, center_y), i)
            screen.blit(highlight, (0, 0))
        
        # Título
        draw_text(screen, "UCMASINO - DADOS", title_font, SECONDARY_COLOR, (WIDTH//2, 30), centered=True)
        
        # Panel de usuario
        pygame.draw.rect(screen, PANEL_COLOR, (20, 80, WIDTH-40, 80), border_radius=10)
        pygame.draw.rect(screen, (60, 80, 110), (20, 80, WIDTH-40, 80), 2, border_radius=10)
        draw_text(screen, f"Jugador: {usuario}", main_font, TEXT_COLOR, (40, 90))
        draw_text(screen, f"Saldo: ${puntos}", main_font, SECONDARY_COLOR, (40, 120))
        
        # Panel de apuesta
        pygame.draw.rect(screen, PANEL_COLOR, (20, 180, WIDTH-40, 100), border_radius=10)
        pygame.draw.rect(screen, (60, 80, 110), (20, 180, WIDTH-40, 100), 2, border_radius=10)
        
        # Información de apuesta
        nombre, desc, color, _ = APUESTAS[apuesta_idx]
        draw_text(screen, f"Apuesta: {nombre}", main_font, color, (40, 190))
        draw_text(screen, f"Monto: ${apuesta}", main_font, TEXT_COLOR, (40, 220))
        draw_text(screen, desc, small_font, TEXT_COLOR, (40, 250))
        
        # Botones
        for i, btn in enumerate(botones):
            hover = btn["rect"].collidepoint(mouse_pos)
            draw_button(screen, btn["rect"], btn["text"], main_font, btn["color"], TEXT_COLOR, hover)
        
        # Dados
        for i, val in enumerate(dados):
            x = 400 + i*120
            y = 300
            draw_die(screen, x, y, 80, val, animando)
        
        # Resultado
        if resultado:
            color = GREEN if ganancia > 0 else RED if ganancia < 0 else TEXT_COLOR
            pygame.draw.rect(screen, PANEL_COLOR, (WIDTH//2-200, 400, 400, 60), border_radius=10)
            pygame.draw.rect(screen, (60, 80, 110), (WIDTH//2-200, 400, 400, 60), 2, border_radius=10)
            draw_text(screen, resultado, main_font, color, (WIDTH//2, 430), centered=True)
            
            if ganancia != 0:
                signo = "+" if ganancia > 0 else ""
                ganancia_text = f"{signo}${abs(ganancia)}"
                draw_text(screen, ganancia_text, main_font, color, (WIDTH//2, 470), centered=True)
        
        # Tabla de apuestas
        pygame.draw.rect(screen, PANEL_COLOR, (20, 490, WIDTH-40, 140), border_radius=10)
        pygame.draw.rect(screen, (60, 80, 110), (20, 490, WIDTH-40, 140), 2, border_radius=10)
        draw_text(screen, "TIPOS DE APUESTAS:", small_font, SECONDARY_COLOR, (40, 500))
        
        y = 530
        for nombre, desc, color, mult in APUESTAS:
            draw_text(screen, f"• {nombre}", tiny_font, color, (40, y))
            draw_text(screen, desc, tiny_font, TEXT_COLOR, (250, y))
            if mult > 1:
                draw_text(screen, f"Pago: {mult}:1", tiny_font, SECONDARY_COLOR, (700, y))
            y += 25

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

    # Loop principal
    while True:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN and not animando:
                # Botón izquierdo
                if event.button == 1:
                    # Botón menos
                    if botones[1]["rect"].collidepoint(mouse_pos) and apuesta > 1:
                        apuesta -= 1
                    # Botón más
                    if botones[2]["rect"].collidepoint(mouse_pos) and apuesta < puntos:
                        apuesta += 1
                    # Botón apuesta anterior
                    if botones[3]["rect"].collidepoint(mouse_pos):
                        apuesta_idx = (apuesta_idx - 1) % len(APUESTAS)
                    # Botón apuesta siguiente
                    if botones[4]["rect"].collidepoint(mouse_pos):
                        apuesta_idx = (apuesta_idx + 1) % len(APUESTAS)
                    # Botón lanzar
                    if botones[0]["rect"].collidepoint(mouse_pos) and apuesta <= puntos:
                        animando = True
                        anim_frames = 20
                        resultado = ""
                        ganancia = 0

        # Animación de dados
        if animando:
            dados = [random.randint(1, 6), random.randint(1, 6)]
            anim_frames -= 1
            
            # Finalizar animación
            if anim_frames == 0:
                animando = False
                suma = sum(dados)
                nombre_apuesta = APUESTAS[apuesta_idx][0]
                res, gan = evaluar_apuesta(nombre_apuesta, suma, apuesta)
                resultado = res
                ganancia = gan
                
                # Actualizar puntos
                if gan != 0:
                    nuevos_puntos = puntos + gan
                    update_points(usuario, nuevos_puntos)
                    puntos = nuevos_puntos

        dibujar_ui()
        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    # Para pruebas, si no se llama desde otro módulo
    main("jugador_demo")
