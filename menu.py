import pygame
from button import Button
import os
import sys
import json
import subprocess

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Variables globales
game_paused = False
menu_state = "main"
game_running = False

# Configuraciones por defecto
default_settings = {
    "resolution": "800x600",
    "fullscreen": False,
    "vsync": True,
    "master_volume": 70,
    "sfx_volume": 80,
    "music_volume": 60,
    "pause_key": "ESCAPE"
}

game_settings = default_settings.copy()

# Resoluciones disponibles
RESOLUTIONS = [
    ("800x600", 800, 600),
    ("1024x768", 1024, 768),
    ("1280x720", 1280, 720),
    ("1200x650", 1200, 650),
    ("1920x1080", 1920, 1080)
]

# Inicialización de pygame
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Main Menu")
clock = pygame.time.Clock()

# Fuentes
try:
    font = pygame.font.Font(None, 60)
    medium_font = pygame.font.Font(None, 40)
    small_font = pygame.font.Font(None, 30)
    tiny_font = pygame.font.Font(None, 24)
except:
    font = pygame.font.SysFont("arial", 60)
    medium_font = pygame.font.SysFont("arial", 40)
    small_font = pygame.font.SysFont("arial", 30)
    tiny_font = pygame.font.SysFont("arial", 24)

# Colores
TEXT_COL = (255, 255, 255)
BACKGROUND_COL = (3, 186, 252)
BUTTON_HOVER_COL = (100, 200, 255)
SELECTED_COL = (255, 255, 0)
ERROR_COL = (255, 100, 100)
SUCCESS_COL = (100, 255, 100)

def crear_ruta_img(nombre_imagen):
    """Crea la ruta completa para una imagen"""
    return os.path.join(os.path.dirname(__file__), 'image', nombre_imagen)

def load_image(filename, default_size=(100, 50)):
    """Carga una imagen con manejo de errores mejorado"""
    try:
        img = pygame.image.load(crear_ruta_img(filename)).convert_alpha()
        return img
    except (pygame.error, FileNotFoundError) as e:
        print(f"No se pudo cargar la imagen {filename}: {e}")
        placeholder = pygame.Surface(default_size, pygame.SRCALPHA)
        pygame.draw.rect(placeholder, (100, 100, 100, 180), placeholder.get_rect(), border_radius=10)
        pygame.draw.rect(placeholder, (200, 200, 200), placeholder.get_rect(), 2, border_radius=10)
        
        text_surface = tiny_font.render(filename.split('.')[0], True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=placeholder.get_rect().center)
        placeholder.blit(text_surface, text_rect)
        
        return placeholder

# Cargar imágenes con tamaños apropiados
play_img = load_image("play.png", (150, 60))
options_img = load_image("options.png", (150, 60))
exit_img = load_image("exit.png", (150, 60))
video_img = load_image("video.png", (120, 50))
audio_img = load_image("audio.png", (120, 50))
credit_img = load_image("credistos.png", (120, 50))
back_img = load_image("back.png", (120, 50))
huergo_img = load_image("huergo.png", (300, 300))

# Cargar fondos
fondo_menu = load_image("fondo_menu.png", (SCREEN_WIDTH, SCREEN_HEIGHT))
fondo_menu_option = load_image("fondo_menu_option.png", (SCREEN_WIDTH, SCREEN_HEIGHT))

# Sistema mejorado de control de clics
last_click_time = 0
CLICK_DELAY = 200
last_button_clicked = None

def can_click():
    """Verifica si se puede hacer clic (cooldown global)"""
    global last_click_time
    current_time = pygame.time.get_ticks()
    
    if current_time - last_click_time > CLICK_DELAY:
        last_click_time = current_time
        return True
    return False

# Variables para mensajes
message_timer = 0
current_message = ""
message_color = TEXT_COL

def show_message(text, color=TEXT_COL, duration=2000):
    """Muestra un mensaje temporal"""
    global current_message, message_color, message_timer
    current_message = text
    message_color = color
    message_timer = pygame.time.get_ticks() + duration

def draw_text(text, font, text_col, x, y):
    """Dibuja texto en posición específica"""
    img = font.render(str(text), True, text_col)
    screen.blit(img, (x, y))
    return img.get_rect(topleft=(x, y))

def draw_centered_text(text, font, text_col, y):
    """Dibuja texto centrado horizontalmente"""
    img = font.render(str(text), True, text_col)
    x = (SCREEN_WIDTH - img.get_width()) // 2
    screen.blit(img, (x, y))
    return img.get_rect(topleft=(x, y))

def draw_clickable_option(text, font, text_col, x, y, selected=False, hover=False):
    """Dibuja una opción clickeable con estados visuales"""
    color = SELECTED_COL if selected else (BUTTON_HOVER_COL if hover else text_col)
    rect = draw_text(text, font, color, x, y)
    
    if selected:
        pygame.draw.rect(screen, SELECTED_COL, rect, 2, border_radius=5)
    elif hover:
        pygame.draw.rect(screen, BUTTON_HOVER_COL, rect, 1, border_radius=5)
    
    return rect

def draw_pause_overlay():
    """Dibuja overlay semitransparente para el menú de pausa"""
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(128)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

def draw_message():
    """Dibuja mensajes temporales"""
    global current_message, message_timer
    
    if current_message and pygame.time.get_ticks() < message_timer:
        draw_centered_text(current_message, small_font, message_color, SCREEN_HEIGHT - 50)
    elif pygame.time.get_ticks() >= message_timer:
        current_message = ""

def apply_resolution():
    """Aplica la resolución seleccionada"""
    global screen, SCREEN_WIDTH, SCREEN_HEIGHT, fondo_menu, fondo_menu_option
    
    try:
        res_str = game_settings["resolution"]
        width, height = map(int, res_str.split('x'))
        
        if game_settings["fullscreen"]:
            screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
        else:
            screen = pygame.display.set_mode((width, height))
        
        SCREEN_WIDTH, SCREEN_HEIGHT = width, height
        
        # Recargar fondos con nueva resolución
        fondo_menu = load_image("fondo_menu.png", (SCREEN_WIDTH, SCREEN_HEIGHT))
        fondo_menu_option = load_image("fondo_menu_option.png", (SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Escalar fondos si es necesario
        fondo_menu = pygame.transform.scale(fondo_menu, (SCREEN_WIDTH, SCREEN_HEIGHT))
        fondo_menu_option = pygame.transform.scale(fondo_menu_option, (SCREEN_WIDTH, SCREEN_HEIGHT))
        
        show_message(f"Resolución aplicada: {res_str}", SUCCESS_COL)
        
    except Exception as e:
        show_message(f"Error al aplicar resolución: {str(e)}", ERROR_COL)
        print(f"Error aplicando resolución: {e}")

def handle_main_menu():
    """Maneja la lógica del menú principal"""
    global game_paused, menu_state, game_running, last_button_clicked
    
    # Dibujar fondo del menú principal (Minigames)
    screen.blit(pygame.transform.scale(fondo_menu, (SCREEN_WIDTH, SCREEN_HEIGHT)), (0, 0))
    
    play_button = Button(130, 125, play_img, 7)
    options_button = Button(450, 125, options_img, 7)
    exit_button = Button(300, 375, exit_img, 7)
    
    play_pressed = play_button.draw(screen)
    options_pressed = options_button.draw(screen)
    exit_pressed = exit_button.draw(screen)
    
    if can_click():
        if play_pressed:
            last_button_clicked = "play"
            try:
                save_settings()
                print("Iniciando pantalla_de_inicio.py...")
                
                if not os.path.exists("pantalla_de_inicio.py"):
                    show_message("Error: pantalla_de_inicio.py no encontrado", ERROR_COL)
                    print("Error: Asegúrate de que pantalla_de_inicio.py existe")
                    return True
                
                pygame.quit()
                subprocess.call([sys.executable, "pantalla_de_inicio.py"])
                return False
                
            except Exception as e:
                show_message(f"Error: {str(e)}", ERROR_COL)
                print(f"Error al abrir el juego: {e}")
                try:
                    pygame.init()
                    globals()['screen'] = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                except:
                    pass
            return True
        
        if options_pressed:
            last_button_clicked = "options"
            menu_state = "options"
            return True
        
        if exit_pressed:
            last_button_clicked = "exit"
            return False
    
    return True

def handle_options_menu():
    """Maneja el menú de opciones"""
    global menu_state
    
    # Dibujar fondo del menú de opciones (OPTIONS)
    screen.blit(pygame.transform.scale(fondo_menu_option, (SCREEN_WIDTH, SCREEN_HEIGHT)), (0, 0))
    
    video_button = Button(100, 120, video_img, 7)
    audio_button = Button(400, 120, audio_img, 7)
    credit_button = Button(100, 300, credit_img, 7)
    back_button = Button(400, 300, back_img, 7)
    
    video_pressed = video_button.draw(screen)
    audio_pressed = audio_button.draw(screen)
    credit_pressed = credit_button.draw(screen)
    back_pressed = back_button.draw(screen)
    
    if can_click():
        if video_pressed:
            menu_state = "video"
        elif audio_pressed:
            menu_state = "audio"
        elif credit_pressed:
            menu_state = "credits"
        elif back_pressed:
            menu_state = "main"

def handle_credits():
    """Maneja la pantalla de créditos"""
    global menu_state
    
    screen.fill(BACKGROUND_COL)
    
    draw_centered_text("CRÉDITOS", font, TEXT_COL, 30)
    
    y_pos = 120
    draw_centered_text("Producido por:", medium_font, TEXT_COL, y_pos)
    draw_centered_text("PAPU GAMES INC.", font, (255, 200, 0), y_pos + 50)
    
    y_pos += 120
    draw_centered_text("Desarrolladores:", medium_font, TEXT_COL, y_pos)
    developers = [
        "Valentin Martinez",
        "Manuel Mañe Mazzieri",
        "Juanjo Shlamovitz Alfonso",
    ]
    
    for i, dev in enumerate(developers):
        draw_centered_text(dev, small_font, (200, 200, 255), y_pos + 40 + (i * 30))
    
    y_pos += 160
    logo_x = (SCREEN_WIDTH - huergo_img.get_width()) // 2
    screen.blit(huergo_img, (logo_x, y_pos))
    
    draw_centered_text("Ins. Ind. Luis A. Huergo", medium_font, TEXT_COL, y_pos + huergo_img.get_height() + 20)
    draw_centered_text("2025", small_font, TEXT_COL, SCREEN_HEIGHT - 80)
    
    back_x = SCREEN_WIDTH // 2 - back_img.get_width() // 2
    back_y = SCREEN_HEIGHT - 70
    back_button = Button(back_x, back_y, back_img, 1)
    
    # Dibujar el botón SIEMPRE primero
    back_button.draw(screen)
    
    # Luego verificar si fue clickeado
    if back_button.clicked and can_click():
        menu_state = "options"

def handle_video_settings():
    """Maneja las configuraciones de video"""
    global menu_state, game_settings
    
    screen.fill(BACKGROUND_COL)
    draw_centered_text("CONFIGURACIÓN DE VIDEO", font, TEXT_COL, 50)
    
    mouse_pos = pygame.mouse.get_pos()
    mouse_clicked = pygame.mouse.get_pressed()[0]
    
    y_start = 150
    spacing = 80
    
    # Resolución
    draw_text("Resolución:", medium_font, TEXT_COL, 100, y_start)
    current_res = game_settings["resolution"]
    
    # Dibujar todas las opciones de resolución
    for i, (res_str, width, height) in enumerate(RESOLUTIONS):
        x = 300 + (i % 3) * 180
        y = y_start + (i // 3) * 40
        selected = (res_str == current_res)
        hover = pygame.Rect(x, y, 150, 30).collidepoint(mouse_pos)
        
        rect = draw_clickable_option(res_str, small_font, TEXT_COL, x, y, selected, hover)
        
        # Detectar clic en la resolución
        if rect.collidepoint(mouse_pos) and mouse_clicked and can_click():
            game_settings["resolution"] = res_str
            show_message(f"Resolución seleccionada: {res_str}", SUCCESS_COL)
    
    # Botón aplicar resolución
    apply_rect = pygame.Rect(100, y_start + 100, 120, 35)
    apply_hover = apply_rect.collidepoint(mouse_pos)
    apply_color = (150, 200, 150) if apply_hover else (100, 150, 100)
    pygame.draw.rect(screen, apply_color, apply_rect, border_radius=5)
    draw_text("Aplicar", medium_font, TEXT_COL, 110, y_start + 105)
    
    if apply_rect.collidepoint(mouse_pos) and mouse_clicked and can_click():
        apply_resolution()
    
    # Pantalla completa
    y_pos = y_start + spacing * 2
    draw_text("Pantalla completa:", medium_font, TEXT_COL, 100, y_pos)
    fullscreen_text = "ACTIVADA" if game_settings["fullscreen"] else "DESACTIVADA"
    hover = pygame.Rect(350, y_pos, 200, 30).collidepoint(mouse_pos)
    
    rect = draw_clickable_option(fullscreen_text, small_font, TEXT_COL, 350, y_pos, 
                                game_settings["fullscreen"], hover)
    
    if rect.collidepoint(mouse_pos) and mouse_clicked and can_click():
        game_settings["fullscreen"] = not game_settings["fullscreen"]
        status = "activada" if game_settings["fullscreen"] else "desactivada"
        show_message(f"Pantalla completa {status}", SUCCESS_COL)
    
    # V-Sync
    y_pos = y_start + spacing * 3
    draw_text("V-Sync:", medium_font, TEXT_COL, 100, y_pos)
    vsync_text = "ACTIVADO" if game_settings["vsync"] else "DESACTIVADO"
    hover = pygame.Rect(250, y_pos, 200, 30).collidepoint(mouse_pos)
    
    rect = draw_clickable_option(vsync_text, small_font, TEXT_COL, 250, y_pos, 
                                game_settings["vsync"], hover)
    
    if rect.collidepoint(mouse_pos) and mouse_clicked and can_click():
        game_settings["vsync"] = not game_settings["vsync"]
        status = "activado" if game_settings["vsync"] else "desactivado"
        show_message(f"V-Sync {status}", SUCCESS_COL)
    
    # Botón back usando Button
    back_x = SCREEN_WIDTH // 2 - back_img.get_width() // 2
    back_y = SCREEN_HEIGHT - 80
    back_button = Button(back_x, back_y, back_img, 1)
    
    # Dibujar el botón SIEMPRE primero
    back_button.draw(screen)
    
    # Luego verificar si fue clickeado
    if back_button.clicked and can_click():
        menu_state = "options"

def handle_audio_settings():
    """Maneja las configuraciones de audio"""
    global menu_state, game_settings
    
    screen.fill(BACKGROUND_COL)
    draw_centered_text("CONFIGURACIÓN DE AUDIO", font, TEXT_COL, 50)
    
    mouse_pos = pygame.mouse.get_pos()
    mouse_pressed = pygame.mouse.get_pressed()[0]
    
    y_start = 150
    spacing = 100
    
    def draw_volume_slider(label, key, y_pos):
        """Dibuja un slider de volumen"""
        draw_text(f"{label}:", medium_font, TEXT_COL, 100, y_pos)
        current_volume = game_settings[key]
        
        bar_x, bar_y = 350, y_pos + 15
        bar_width, bar_height = 300, 25
        
        pygame.draw.rect(screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height), border_radius=12)
        pygame.draw.rect(screen, (40, 40, 40), (bar_x, bar_y, bar_width, bar_height), 2, border_radius=12)
        
        fill_width = int((current_volume / 100) * bar_width)
        if fill_width > 0:
            color = (100, 255, 100) if current_volume > 70 else (255, 255, 100) if current_volume > 30 else (255, 150, 150)
            pygame.draw.rect(screen, color, (bar_x, bar_y, fill_width, bar_height), border_radius=12)
        
        handle_x = bar_x + fill_width - 10
        handle_rect = pygame.Rect(handle_x, bar_y - 5, 20, bar_height + 10)
        pygame.draw.rect(screen, (200, 200, 200), handle_rect, border_radius=10)
        pygame.draw.rect(screen, (100, 100, 100), handle_rect, 2, border_radius=10)
        
        draw_text(f"{current_volume}%", small_font, TEXT_COL, bar_x + bar_width + 20, y_pos + 5)
        
        slider_rect = pygame.Rect(bar_x - 10, bar_y - 10, bar_width + 20, bar_height + 20)
        if slider_rect.collidepoint(mouse_pos) and mouse_pressed:
            relative_x = max(0, min(bar_width, mouse_pos[0] - bar_x))
            new_volume = int((relative_x / bar_width) * 100)
            if new_volume != current_volume:
                game_settings[key] = new_volume
    
    draw_volume_slider("Volumen Maestro", "master_volume", y_start)
    draw_volume_slider("Efectos de Sonido", "sfx_volume", y_start + spacing)
    draw_volume_slider("Música", "music_volume", y_start + spacing * 2)
    
    test_y = y_start + spacing * 3
    draw_text("Prueba de audio:", medium_font, TEXT_COL, 100, test_y)
    
    test_sfx_rect = pygame.Rect(300, test_y, 100, 30)
    test_music_rect = pygame.Rect(420, test_y, 100, 30)
    
    pygame.draw.rect(screen, (100, 100, 150), test_sfx_rect, border_radius=5)
    pygame.draw.rect(screen, (150, 100, 100), test_music_rect, border_radius=5)
    
    draw_text("SFX", small_font, TEXT_COL, 320, test_y + 5)
    draw_text("Música", small_font, TEXT_COL, 430, test_y + 5)
    
    if mouse_pressed and can_click():
        if test_sfx_rect.collidepoint(mouse_pos):
            show_message("Reproduciendo efecto de sonido", SUCCESS_COL)
        elif test_music_rect.collidepoint(mouse_pos):
            show_message("Reproduciendo música", SUCCESS_COL)
    
    # Botón back usando Button
    back_x = SCREEN_WIDTH // 2 - back_img.get_width() // 2
    back_y = SCREEN_HEIGHT - 80
    back_button = Button(back_x, back_y, back_img, 1)
    
    # Dibujar el botón SIEMPRE primero
    back_button.draw(screen)
    
    # Luego verificar si fue clickeado
    if back_button.clicked and can_click():
        menu_state = "options"

def handle_events():
    """Maneja todos los eventos de pygame"""
    global game_paused, game_running, menu_state
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Navegación jerárquica con ESC
                if menu_state in ["video", "audio", "credits"]:
                    menu_state = "options"
                elif menu_state == "options":
                    menu_state = "main"
                else:  # menu_state == "main"
                    return False
            
            elif event.key == pygame.K_c:
                menu_state = "credits"
    
    return True

def save_settings():
    """Guarda las configuraciones en formato JSON"""
    try:
        with open('game_settings.json', 'w', encoding='utf-8') as f:
            json.dump(game_settings, f, indent=4, ensure_ascii=False)
        print(" Configuraciones guardadas exitosamente")
    except Exception as e:
        print(f" Error al guardar configuraciones: {e}")

def load_settings():
    """Carga las configuraciones desde JSON"""
    global game_settings
    
    try:
        with open('game_settings.json', 'r', encoding='utf-8') as f:
            loaded_settings = json.load(f)
        
        for key in default_settings:
            if key in loaded_settings:
                game_settings[key] = loaded_settings[key]
        
        print(" Configuraciones cargadas exitosamente")
        
    except FileNotFoundError:
        print(" No se encontró archivo de configuraciones, usando valores por defecto")
        game_settings = default_settings.copy()
        save_settings()
    except Exception as e:
        print(f" Error al cargar configuraciones: {e}")
        game_settings = default_settings.copy()

def main():
    """Función principal del juego"""
    global menu_state, screen, fondo_menu, fondo_menu_option

    load_settings()

    # Asegurarse de que fullscreen esté en False al inicio
    if game_settings.get("fullscreen", False):
        game_settings["fullscreen"] = False
        save_settings()

    try:
        # Escalar fondos a la resolución actual
        fondo_menu = pygame.transform.scale(fondo_menu, (SCREEN_WIDTH, SCREEN_HEIGHT))
        fondo_menu_option = pygame.transform.scale(fondo_menu_option, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except:
        print("⚠️ Error escalando fondos")

    run = True

    print("=" * 50)
    print("🎮 MENÚ DE JUEGO - PAPU GAMES INC.")
    print("=" * 50)
    print("📋 CONTROLES:")
    print("   • ESC: Volver / Salir")
    print("   • C: Ver créditos")
    print("   • Click: Interactuar con elementos")
    print("=" * 50)

    while run:
        clock.tick(FPS)

        # ✅ Verificar si la ventana fue cerrada (evita "display Surface quit")
        if not pygame.display.get_init():
            break

        run = handle_events()
        if not run:
            break

        if menu_state == "main":
            run = handle_main_menu()

        elif menu_state == "options":
            handle_options_menu()

        elif menu_state == "video":
            handle_video_settings()

        elif menu_state == "audio":
            handle_audio_settings()

        elif menu_state == "credits":
            handle_credits()

        # ✅ Verificar otra vez antes de dibujar o actualizar
        if not pygame.display.get_init():
            break

        draw_message()
        pygame.display.update()


    if pygame.display.get_init():
        save_settings()
        pygame.quit()
    sys.exit()
if __name__ == "__main__":
    main()