import pygame
import os
import sys
import subprocess
from datetime import datetime

pygame.init()


SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 800
FPS = 60

BACKGROUND_COLOR = (15, 15, 25)
CARD_COLOR = (40, 40, 60)
CARD_HOVER_COLOR = (60, 60, 90)
TEXT_COLOR = (255, 255, 255)
ACCENT_COLOR = (100, 200, 255)
GRADIENT_START = (25, 25, 45)
GRADIENT_END = (15, 15, 25)


screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(" Minigames - Selecciona tu Juego")
clock = pygame.time.Clock()


title_font = pygame.font.SysFont("Arial", 48, bold=True)
game_title_font = pygame.font.SysFont("Arial", 24, bold=True)
description_font = pygame.font.SysFont("Arial", 16)
small_font = pygame.font.SysFont("Arial", 14)
time_font = pygame.font.SysFont("Arial", 18)


games = [
    {
        "title": "Flappy bird",
        "description": "Controla a un pájaro que salta los obstáculos",
        "file": "flappy.py",
        "category": "arcade",
        "color": (100, 200, 100),
        "status": "Disponible"
    },
    {
        "title": "Pong",
        "description": "Un clásico juego de Ping Pong",
        "file": "pong.py",
        "category": "arcade",
        "color": (200, 100, 100),
        "status": "Disponible"
    },
    {
        "title": "4 lineas",
        "description": "juego de dos jugadores, intenta alinear 4 fichas antes de tu oponente",
        "file": "4_lineas.py",
        "category": "estrategia ",
        "color": (100, 100, 200),
        "status": "Disponible"
    },
    {
        "title": "Fall_out",
        "description": "Evita los bloques que caen del cielo",
        "file": "Fall_out.py",
        "category": "arcade",
        "color": (200, 200, 100),
        "status": "Disponible"
    },
    {
        "title": "Memotest",
        "description": "Intentar recordar la posición de las cartas",
        "file": "memotest.py",
        "category": "puzzle",
        "color": (200, 100, 200),
        "status": "Disponible"
    },
    {
        "title": "Snake",
        "description": "Controla la serpiente y come la comida",
        "file": "snake.py",
        "category": "arcade",
        "color": (100, 200, 200),
        "status": "Disponible"
    },{
        "title": "Grid fútbol",
        "description": "Un emocionante juego para probar tus conocimientos de fútbol en una cuadrícula",
        "file": "grid.py",
        "category": "conocimiento",
        "color": (100, 200, 200),
        "status": "Disponible"
    },{
        "title": "Crash run",
        "description": "Esquiva los autos y llega lo más lejos posible",
        "file": "crash_run.py",
        "category": "arcade",
        "color": (100, 200, 200),
        "status": "Disponible"
    },{
        "title": "Fruit ninja",
        "description": "Corta la fruta pero evita las bombas",
        "file": "fruit_cutter.py",
        "category": "arcade",
        "color": (100, 200, 200),
        "status": "Disponible"
    },{
        "title": "Sky hopper",
        "description": "Salta de plataforma en plataforma sin caer",
        "file": "sky_hopper.py",
        "category": "arcade",
        "color": (100, 200, 200),
        "status": "Disponible"
    },{
        "title": "Fast fingers",
        "description": "Corre lo más rápido que puedas tocando las teclas",
        "file": "fast_finger.py",
        "category": "arcade",
        "color": (100, 200, 200),
        "status": "Disponible"
    },
    {
        "title": "F11 Clubes",
        "description": "Crea tu propia formación con jugadores de distintos clubes",
        "file": "f11clubes.py",
        "category": "conocimiento",
        "color": (100, 200, 200),
        "status": "Disponible"
    }
]


selected_game = None
mouse_pos = (0, 0)
scroll_offset = 0
max_scroll = 0

def draw_gradient_background():
    """Dibuja un fondo con gradiente"""
    if not pygame.display.get_init():
        return

    for y in range(SCREEN_HEIGHT):
        ratio = y / SCREEN_HEIGHT
        r = int(GRADIENT_START[0] * (1 - ratio) + GRADIENT_END[0] * ratio)
        g = int(GRADIENT_START[1] * (1 - ratio) + GRADIENT_END[1] * ratio)
        b = int(GRADIENT_START[2] * (1 - ratio) + GRADIENT_END[2] * ratio)

        if screen:
            pygame.draw.line(screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        else:
            break

def draw_text(text, font, color, x, y, center=False):
    """Dibuja texto en pantalla"""
    text_surface = font.render(text, True, color)
    if center:
        text_rect = text_surface.get_rect(center=(x, y))
        screen.blit(text_surface, text_rect)
        return text_rect
    else:
        screen.blit(text_surface, (x, y))
        return text_surface.get_rect(topleft=(x, y))

def draw_game_card(game, x, y, width, height, hovered=False):
    """Dibuja una tarjeta de juego"""

    card_color = CARD_HOVER_COLOR if hovered else CARD_COLOR
    

    shadow_offset = 5
    pygame.draw.rect(screen, (0, 0, 0, 50), 
                     (x + shadow_offset, y + shadow_offset, width, height), 
                     border_radius=15)
    

    pygame.draw.rect(screen, card_color, (x, y, width, height), border_radius=15)
    

    pygame.draw.rect(screen, game["color"], (x, y, width, 8), border_top_left_radius=15, border_top_right_radius=15)
    
    border_color = game["color"] if hovered else (80, 80, 100)
    pygame.draw.rect(screen, border_color, (x, y, width, height), width=2, border_radius=15)
    

    title_y = y + 25
    draw_text(game["title"], game_title_font, TEXT_COLOR, x + 20, title_y)
    

    category_y = title_y + 35
    category_color = game["color"]
    draw_text(f" {game['category']}", description_font, category_color, x + 20, category_y)
    

    desc_y = category_y + 25
    draw_text(game["description"], description_font, (200, 200, 200), x + 20, desc_y)
    

    status_y = y + height - 35
    status_colors = {
        "Disponible": (100, 255, 100),
        "En desarrollo": (255, 200, 100),
        "Próximamente": (255, 100, 100)
    }
    status_color = status_colors.get(game["status"], TEXT_COLOR)
    

    if game["status"] == "Disponible":
        play_button_x = x + width - 100
        play_button_y = y + height - 50
        play_button_width = 80
        play_button_height = 30
        

        play_color = game["color"] if hovered else (60, 60, 80)
        pygame.draw.rect(screen, play_color, 
                        (play_button_x, play_button_y, play_button_width, play_button_height),
                        border_radius=15)
        
        draw_text(" JUGAR", small_font, TEXT_COLOR, 
                 play_button_x + play_button_width//2, play_button_y + play_button_height//2, center=True)
        
        return pygame.Rect(play_button_x, play_button_y, play_button_width, play_button_height)
    
    return None

def launch_game(game_file):
    """Lanza un juego específico"""
    try:
        if os.path.exists(game_file):
            print(f" Lanzando: {game_file}")

            subprocess.Popen([sys.executable, game_file])
            return True
        else:
            print(f" Archivo no encontrado: {game_file}")
            return False
    except Exception as e:
        print(f" Error al lanzar {game_file}: {e}")
        return False

def draw_header():
    """Dibuja el encabezado de la aplicación"""

    draw_text(" Minigames  ", title_font, ACCENT_COLOR, SCREEN_WIDTH//2, 50, center=True)
    

    draw_text("Selecciona tu aventura", description_font, (180, 180, 180), 
              SCREEN_WIDTH//2, 90, center=True)
    

    current_time = datetime.now().strftime("%H:%M:%S")
    draw_text(f" {current_time}", time_font, (150, 150, 150), SCREEN_WIDTH - 150, 30)
    

    pygame.draw.line(screen, ACCENT_COLOR, (100, 120), (SCREEN_WIDTH - 100, 120), 2)

def draw_footer():
    """Dibuja el pie de página"""
    footer_y = SCREEN_HEIGHT - 50
    

    pygame.draw.line(screen, ACCENT_COLOR, (100, footer_y - 20), (SCREEN_WIDTH - 100, footer_y - 20), 1)
    

    controls_text = " Click para jugar • ESC para salir • ↑↓ Scroll para navegar • Q para pausar"
    draw_text(controls_text, small_font, (150, 150, 150), SCREEN_WIDTH//2, footer_y, center=True)

def handle_scroll(event):
    """Maneja el scroll del mouse"""
    global scroll_offset, max_scroll
    
    if event.type == pygame.MOUSEWHEEL:
        scroll_speed = 30
        scroll_offset -= event.y * scroll_speed
        scroll_offset = max(0, min(scroll_offset, max_scroll))

def main():
    global mouse_pos, selected_game, scroll_offset, max_scroll
    
    running = True
    
    print("=== GAME LAUNCHER INICIADO ===")
    print(" Juegos disponibles:")
    for i, game in enumerate(games, 1):
        print(f"   {i}. {game['title']} ({game['status']})")
    print("\n Haz clic en 'JUGAR' para lanzar un juego")
    print(" Asegúrate de que los archivos .py existan en la misma carpeta")
    
    while running:
        clock.tick(FPS)
        mouse_pos = pygame.mouse.get_pos()
        

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_q:
                    print("Volviendo al menú principal...")
                    pygame.quit()  # Cierra la ventana actual
                    subprocess.Popen([sys.executable, "menu.py"])  # Ejecuta menu.py
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  

                    cards_per_row = 2
                    card_width = 500
                    card_height = 200
                    margin = 50
                    start_x = (SCREEN_WIDTH - (cards_per_row * card_width + (cards_per_row - 1) * margin)) // 2
                    start_y = 150
                    
                    for i, game in enumerate(games):
                        row = i // cards_per_row
                        col = i % cards_per_row
                        
                        card_x = start_x + col * (card_width + margin)
                        card_y = start_y + row * (card_height + margin) - scroll_offset
                        

                        if card_y + card_height >= 0 and card_y <= SCREEN_HEIGHT:
                            card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
                            
                            if card_rect.collidepoint(mouse_pos) and game["status"] == "Disponible":

                                play_button_x = card_x + card_width - 100
                                play_button_y = card_y + card_height - 50
                                play_button_rect = pygame.Rect(play_button_x, play_button_y, 80, 30)
                                
                                if play_button_rect.collidepoint(mouse_pos):
                                    print(f" Intentando lanzar: {game['title']}")
                                    if launch_game(game["file"]):
                                        print(f" {game['title']} lanzado exitosamente")
                                    else:
                                        print(f" No se pudo lanzar {game['title']}")
                                        print(f"   Verifica que {game['file']} existe")
            

            handle_scroll(event)
        

        draw_gradient_background()
        

        draw_header()
        

        cards_per_row = 2
        card_width = 500
        card_height = 200
        margin = 50
        start_x = (SCREEN_WIDTH - (cards_per_row * card_width + (cards_per_row - 1) * margin)) // 2
        start_y = 150
        

        total_rows = (len(games) + cards_per_row - 1) // cards_per_row
        total_height = total_rows * (card_height + margin)
        visible_height = SCREEN_HEIGHT - start_y - 100
        max_scroll = max(0, total_height - visible_height)
        

        for i, game in enumerate(games):
            row = i // cards_per_row
            col = i % cards_per_row
            
            card_x = start_x + col * (card_width + margin)
            card_y = start_y + row * (card_height + margin) - scroll_offset
            

            if card_y + card_height >= 0 and card_y <= SCREEN_HEIGHT:

                card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
                hovered = card_rect.collidepoint(mouse_pos)
                
                if hovered:
                    selected_game = game
                

                play_button_rect = draw_game_card(game, card_x, card_y, card_width, card_height, hovered)
        

        draw_footer()
        

        if max_scroll > 0:

            scroll_bar_x = SCREEN_WIDTH - 20
            scroll_bar_y = 150
            scroll_bar_height = SCREEN_HEIGHT - 250
            scroll_bar_width = 8
            

            pygame.draw.rect(screen, (50, 50, 50), 
                           (scroll_bar_x, scroll_bar_y, scroll_bar_width, scroll_bar_height))
            
            # Indicador de posición
            indicator_height = max(20, scroll_bar_height * (visible_height / total_height))
            indicator_y = scroll_bar_y + (scroll_offset / max_scroll) * (scroll_bar_height - indicator_height)
            
            pygame.draw.rect(screen, ACCENT_COLOR, 
                           (scroll_bar_x, indicator_y, scroll_bar_width, indicator_height))
        
        pygame.display.flip()
    
    print(" Cerrando Game Launcher...")
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
