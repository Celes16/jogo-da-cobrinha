import os
import pygame
import socket
import threading
import sys
import time

# Configuração
os.environ['SDL_VIDEODRIVER'] = 'x11'
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

# Constantes
WIDTH, HEIGHT = 20, 20
CELL_SIZE = 30
SCREEN_WIDTH = WIDTH * CELL_SIZE
SCREEN_HEIGHT = HEIGHT * CELL_SIZE + 150  
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 8080

# Cores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 180, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (100, 100, 100)
BUTTON_COLOR = (50, 50, 50)
BUTTON_HOVER = (70, 70, 70)
SCORE_COLOR = (255, 215, 0)  

class Button:
    def __init__(self, x, y, w, h, text, action=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.action = action
        self.hover = False
        self.font = pygame.font.SysFont('Arial', 26, bold=True)

    def draw(self, surface):
        color = BUTTON_HOVER if self.hover else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=10)
        
        text = self.font.render(self.text, True, WHITE)
        text_rect = text.get_rect(center=self.rect.center)
        surface.blit(text, text_rect)

    def check_hover(self, pos):
        self.hover = self.rect.collidepoint(pos)
        return self.hover

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.hover:
            if self.action:
                self.action()

class SnakeClient:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Jogo da Cobrinha")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 24)
        self.big_font = pygame.font.SysFont('Arial', 48, bold=True)
        self.score_font = pygame.font.SysFont('Arial', 36, bold=True)
        
        # Conexão
        self.sock = self.connect_to_server()
        self.last_direction = None
        self.direction_changed = False
        
        self.reset_game_state()
        
        self.create_buttons()
        
        # Thread de comunicação
        self.running = True
        self.recv_thread = threading.Thread(target=self.receive_updates)
        self.recv_thread.daemon = True
        self.recv_thread.start()

    def reset_game_state(self):
        self.game_state = {
            'state': '0',  # 0=menu, 1=jogando, 2=game over
            'snake': [],
            'food': (0, 0),
            'score': 0,
            'level': 1
        }

    def create_buttons(self):
        btn_w, btn_h = 200, 50
        center_x = SCREEN_WIDTH // 2 - btn_w // 2
        
        self.start_button = Button(
            center_x, SCREEN_HEIGHT - 120, 
            btn_w, btn_h,
            "INICIAR JOGO",
            self.start_game
        )
        
        self.quit_button = Button(
            center_x, SCREEN_HEIGHT - 60, 
            btn_w, btn_h,
            "SAIR",
            self.quit_game
        )

    def connect_to_server(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((SERVER_HOST, SERVER_PORT))
            print(" Conectado ao servidor!")
            return sock
        except Exception as e:
            print(f" Erro de conexão: {str(e)}")
            pygame.quit()
            sys.exit(1)

    def start_game(self):
        self.reset_game_state()
        self.send_command('N')  # Novo jogo

    def quit_game(self):
        self.send_command('Q')
        self.running = False

    def send_command(self, cmd):
        try:

            if cmd in ['U', 'D', 'L', 'R'] and self.game_state['state'] == '1':
                if not self.direction_changed:
                    self.sock.sendall(cmd.encode())
                    self.last_direction = cmd
                    self.direction_changed = True
            else:
                self.sock.sendall(cmd.encode())
        except:
            self.running = False

    def receive_updates(self):
        while self.running:
            try:
                data = self.sock.recv(4096).decode()
                if not data:
                    break
                self.parse_game_state(data)
            except Exception as e:
                print(f"Erro na conexão: {str(e)}")
                break

    def parse_game_state(self, data):
        try:
            # Estado (1 byte)
            self.game_state['state'] = data[0]
            
            if self.game_state['state'] in ('1', '2'):
                # Comprimento (4 bytes)
                length = int(data[1:5])
                self.game_state['length'] = length
                
                # Cobra (x,y pairs)
                snake_data = data[5:5 + length*4]
                snake = []
                for i in range(0, len(snake_data), 4):
                    x = int(snake_data[i:i+2])
                    y = int(snake_data[i+2:i+4])
                    snake.append((x, y))
                self.game_state['snake'] = snake
                
                # Comida (4 bytes)
                food_data = data[5 + length*4:9 + length*4]
                fx = int(food_data[:2])
                fy = int(food_data[2:4])
                self.game_state['food'] = (fx, fy)
                
                # Pontuação e nível (6 bytes)
                score_data = data[9 + length*4:13 + length*4]
                level_data = data[13 + length*4:15 + length*4]
                self.game_state['score'] = int(score_data)
                self.game_state['level'] = int(level_data)
        except Exception as e:
            print(f"Erro ao analisar dados: {str(e)}")

    def draw_menu(self):
        self.screen.fill(BLACK)
        
        # Título
        title = self.big_font.render("SNAKE GAME PRO", True, GREEN)
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//4))
        self.screen.blit(title, title_rect)
        
        # Botões
        mouse_pos = pygame.mouse.get_pos()
        self.start_button.check_hover(mouse_pos)
        self.start_button.draw(self.screen)
        self.quit_button.check_hover(mouse_pos)
        self.quit_button.draw(self.screen)
        
        pygame.display.flip()

    def draw_game(self):
        self.screen.fill(BLACK)
        
        # grade
        for x in range(0, SCREEN_WIDTH, CELL_SIZE):
            pygame.draw.line(self.screen, GRAY, (x, 0), (x, HEIGHT*CELL_SIZE))
        for y in range(0, HEIGHT*CELL_SIZE, CELL_SIZE):
            pygame.draw.line(self.screen, GRAY, (0, y), (WIDTH*CELL_SIZE, y))
        
        # Comida
        fx, fy = self.game_state['food']
        pygame.draw.rect(self.screen, RED, 
                        (fx*CELL_SIZE, fy*CELL_SIZE, CELL_SIZE, CELL_SIZE))
        
        # Cobra
        for i, (x, y) in enumerate(self.game_state['snake']):
            color = DARK_GREEN if i == 0 else GREEN
            pygame.draw.rect(self.screen, color, 
                           (x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE))
        
        # UI
        score_text = self.score_font.render(f"Pontuação: {self.game_state['score']}", True, SCORE_COLOR)
        level_text = self.font.render(f"Nível: {self.game_state['level']}", True, WHITE)
        self.screen.blit(score_text, (20, HEIGHT*CELL_SIZE + 10))
        self.screen.blit(level_text, (SCREEN_WIDTH - 100, HEIGHT*CELL_SIZE + 20))
        
        pygame.display.flip()

    def draw_game_over(self):
        self.screen.fill(BLACK)
        
        # título
        game_over = self.big_font.render("FIM DE JOGO", True, RED)
        game_over_rect = game_over.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//4))
        self.screen.blit(game_over, game_over_rect)
        
        # pontuação Final 
        score_text = self.score_font.render(f"Pontuação Final: {self.game_state['score']}", True, SCORE_COLOR)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 40))
        self.screen.blit(score_text, score_rect)
        
        # Botões 
        mouse_pos = pygame.mouse.get_pos()
        self.start_button.check_hover(mouse_pos)
        self.start_button.draw(self.screen)
        self.quit_button.check_hover(mouse_pos)
        self.quit_button.draw(self.screen)
        
        pygame.display.flip()

    def handle_events(self):
        self.direction_changed = False  # Reseta a cada frame
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            # Controles do mouse
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.start_button.handle_event(event)
                self.quit_button.handle_event(event)
            
            # Controles do teclado (movimento contínuo)
            if event.type == pygame.KEYDOWN:
                if self.game_state['state'] == '1':  # Durante o jogo
                    if event.key == pygame.K_UP and self.last_direction != 'D':
                        self.send_command('U')
                    elif event.key == pygame.K_RIGHT and self.last_direction != 'L':
                        self.send_command('R')
                    elif event.key == pygame.K_DOWN and self.last_direction != 'U':
                        self.send_command('D')
                    elif event.key == pygame.K_LEFT and self.last_direction != 'R':
                        self.send_command('L')
                    elif event.key == pygame.K_ESCAPE:
                        self.send_command('M')
                
                elif self.game_state['state'] == '2':  # Game Over
                    if event.key == pygame.K_n:
                        self.start_game()
                    elif event.key == pygame.K_m:
                        self.send_command('M')
                    elif event.key == pygame.K_q:
                        return False
        
        # Envia a última direção continuamente
        if self.game_state['state'] == '1' and self.last_direction:
            self.send_command(self.last_direction)
        
        return True

    def run(self):
        while self.running:
            if not self.handle_events():
                self.running = False
            
            if self.game_state['state'] == '0':
                self.draw_menu()
            elif self.game_state['state'] == '1':
                self.draw_game()
            elif self.game_state['state'] == '2':
                self.draw_game_over()
            
            self.clock.tick(15)  # Controle de FPS para movimento suave
        
        self.cleanup()

    def cleanup(self):
        try:
            self.sock.close()
        except:
            pass
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = SnakeClient()
    game.run()
