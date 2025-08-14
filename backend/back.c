// snake_backend.c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <stdbool.h>

#define WIDTH 20
#define HEIGHT 20
#define PORT 8080
#define MAX_CLIENTS 5

typedef enum {
    DIR_UP,
    DIR_RIGHT,
    DIR_DOWN,
    DIR_LEFT
} Direction;

typedef enum {
    STATE_MENU,
    STATE_PLAYING,
    STATE_GAME_OVER,
    STATE_HIGHSCORES
} GameState;

typedef struct {
    int x, y;
} Position;

typedef struct {
    Position *body;
    int length;
    Direction direction;
    Position food;
    int score;
    int highscore;
    int speed;
    int level;
    GameState state;
} SnakeGame;

typedef struct {
    char name[50];
    int score;
} Highscore;

// Forward declarations
void place_food(SnakeGame *game);
void update_highscores(SnakeGame *game);
void init_game(SnakeGame *game);
void update_game(SnakeGame *game);
void reset_game(SnakeGame *game);
void change_direction(SnakeGame *game, Direction new_dir);
void serialize_game(SnakeGame *game, char *buffer);
void handle_client(int client_socket, SnakeGame *game);

Highscore highscores[10] = {0};

void place_food(SnakeGame *game) {
    int valid;
    do {
        valid = 1;
        game->food.x = rand() % WIDTH;
        game->food.y = rand() % HEIGHT;
        
        for (int i = 0; i < game->length; i++) {
            if (game->food.x == game->body[i].x && game->food.y == game->body[i].y) {
                valid = 0;
                break;
            }
        }
    } while (!valid);
}

void update_highscores(SnakeGame *game) {
    if (game->score <= highscores[9].score) return;
    
    Highscore new_hs = { .score = game->score, .name = "Player" };
    
    for (int i = 0; i < 10; i++) {
        if (game->score > highscores[i].score) {
            for (int j = 9; j > i; j--) {
                highscores[j] = highscores[j-1];
            }
            highscores[i] = new_hs;
            break;
        }
    }
    
    game->highscore = highscores[0].score;
}

void init_game(SnakeGame *game) {
    game->body = malloc(sizeof(Position) * WIDTH * HEIGHT);
    if (game->body == NULL) {
        perror("Failed to allocate memory for snake body");
        exit(EXIT_FAILURE);
    }
    
    game->body[0].x = WIDTH / 2;
    game->body[0].y = HEIGHT / 2;
    game->length = 1;
    game->direction = DIR_RIGHT;
    game->score = 0;
    game->speed = 100000;
    game->level = 1;
    game->state = STATE_MENU;
    
    srand(time(NULL));
    place_food(game);
    
    // Initialize highscores
    for (int i = 0; i < 10; i++) {
        highscores[i].score = 0;
        strcpy(highscores[i].name, "Player");
    }
}

void update_game(SnakeGame *game) {
    if (game->state != STATE_PLAYING) return;
    
    // Move snake body
    for (int i = game->length - 1; i > 0; i--) {
        game->body[i] = game->body[i-1];
    }
    
    // Move head based on direction
    switch (game->direction) {
        case DIR_UP:    game->body[0].y--; break;
        case DIR_RIGHT: game->body[0].x++; break;
        case DIR_DOWN:  game->body[0].y++; break;
        case DIR_LEFT: game->body[0].x--; break;
    }
    
    // Check wall collision
    if (game->body[0].x < 0 || game->body[0].x >= WIDTH || 
        game->body[0].y < 0 || game->body[0].y >= HEIGHT) {
        game->state = STATE_GAME_OVER;
        update_highscores(game);
        return;
    }
    
    // Check self collision
    for (int i = 1; i < game->length; i++) {
        if (game->body[0].x == game->body[i].x && game->body[0].y == game->body[i].y) {
            game->state = STATE_GAME_OVER;
            update_highscores(game);
            return;
        }
    }
    
    // Check food collision
    if (game->body[0].x == game->food.x && game->body[0].y == game->food.y) {
        game->length++;
        game->score += 10 * game->level;
        
        // Increase difficulty every 5 foods
        if (game->score % (50 * game->level) == 0) {
            game->level++;
            game->speed = game->speed * 0.8; // Increase speed by 20%
        }
        
        place_food(game);
    }
}

void reset_game(SnakeGame *game) {
    free(game->body);
    init_game(game);
    game->state = STATE_PLAYING;
}

void change_direction(SnakeGame *game, Direction new_dir) {
    if ((game->direction == DIR_UP && new_dir != DIR_DOWN) || 
        (game->direction == DIR_DOWN && new_dir != DIR_UP) || 
        (game->direction == DIR_LEFT && new_dir != DIR_RIGHT) || 
        (game->direction == DIR_RIGHT && new_dir != DIR_LEFT)) {
        game->direction = new_dir;
    }
}

void serialize_game(SnakeGame *game, char *buffer) {
    int offset = 0;
    
    // Game state (1 byte)
    buffer[offset++] = '0' + game->state;
    
    // Game data based on state
    if (game->state == STATE_PLAYING || game->state == STATE_GAME_OVER) {
        // Snake length (4 bytes)
        sprintf(buffer + offset, "%04d", game->length);
        offset += 4;
        
        // Snake body (x,y pairs)
        for (int i = 0; i < game->length; i++) {
            sprintf(buffer + offset, "%02d%02d", game->body[i].x, game->body[i].y);
            offset += 4;
        }
        
        // Food position (4 bytes)
        sprintf(buffer + offset, "%02d%02d", game->food.x, game->food.y);
        offset += 4;
        
        // Score and level (8 bytes)
        sprintf(buffer + offset, "%04d%02d", game->score, game->level);
        offset += 6;
    }
    else if (game->state == STATE_HIGHSCORES) {
        // Highscores
        for (int i = 0; i < 10; i++) {
            sprintf(buffer + offset, "%04d%-50s", highscores[i].score, highscores[i].name);
            offset += 54;
        }
    }
    
    buffer[offset] = '\0';
}

void handle_client(int client_socket, SnakeGame *game) {
    char buffer[2048] = {0};
    char response[2048];
    
    while (1) {
        int valread = read(client_socket, buffer, sizeof(buffer));
        
        if (valread > 0) {
            // Process command
            switch (buffer[0]) {
                case 'U': change_direction(game, DIR_UP); break;
                case 'R': change_direction(game, DIR_RIGHT); break;
                case 'D': change_direction(game, DIR_DOWN); break;
                case 'L': change_direction(game, DIR_LEFT); break;
                case 'S': game->state = STATE_PLAYING; break; // Start game
                case 'N': reset_game(game); break; // New game
                case 'H': game->state = STATE_HIGHSCORES; break; // Show highscores
                case 'M': game->state = STATE_MENU; break; // Return to menu
                case 'Q': close(client_socket); return; // Quit

                    if (buffer[1] == '1') game->speed = 150000;
                    else if (buffer[1] == '2') game->speed = 100000;
                    else if (buffer[1] == '3') game->speed = 50000;
                    break;
            }
            
            // Update game if playing
            if (game->state == STATE_PLAYING) {
                update_game(game);
            }
            
            // Serialize game state
            serialize_game(game, response);
            
            // Send game state to client
            send(client_socket, response, strlen(response), 0);
        }
        
        usleep(game->speed);
    }
}

int main() {
    int server_fd, client_socket;
    struct sockaddr_in address;
    int opt = 1;
    int addrlen = sizeof(address);
    
    SnakeGame game;
    init_game(&game);
    
    // Create socket
    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0) {
        perror("socket failed");
        exit(EXIT_FAILURE);
    }
    
    // Set socket options
    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt))) {
        perror("setsockopt");
        exit(EXIT_FAILURE);
    }
    
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(PORT);
    
    // Bind socket
    if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0) {
        perror("bind failed");
        exit(EXIT_FAILURE);
    }
    
    // Listen for connections
    if (listen(server_fd, MAX_CLIENTS) < 0) {
        perror("listen");
        exit(EXIT_FAILURE);
    }
    
    printf("Server listening on port %d...\n", PORT);
    
    // Accept incoming connections
    while ((client_socket = accept(server_fd, (struct sockaddr *)&address, (socklen_t*)&addrlen)) > 0) {
        printf("New client connected\n");
        handle_client(client_socket, &game);
    }
    
    if (client_socket < 0) {
        perror("accept failed");
        exit(EXIT_FAILURE);
    }
    
    close(server_fd);
    free(game.body);
    return 0;
}