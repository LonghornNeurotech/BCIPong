import pygame
import sys
from copy import copy
import math
import os
import random

def create_fifo():
    fifo_path = 'ai_commands'
    if not os.path.exists(fifo_path):
        os.mkfifo(fifo_path)
    return fifo_path

def draw_dotted_line(surface, color, start_pos, end_pos, width=1, dash_length=10):
    x1, y1 = start_pos
    x2, y2 = end_pos
    dl = dash_length

    if (x1 == x2):
        ycoords = [y for y in range(y1, y2, dl if y1 < y2 else -dl)]
        if len(ycoords) % 2:
            ycoords.append(y2)
        for i in range(0, len(ycoords), 2):
            pygame.draw.line(surface, color, (x1, ycoords[i]), (x1, ycoords[i+1]), width)
    else:
        xcoords = [x for x in range(x1, x2, dl if x1 < x2 else -dl)]
        if len(xcoords) % 2:
            xcoords.append(x2)
        for i in range(0, len(xcoords), 2):
            pygame.draw.line(surface, color, (xcoords[i], y1), (xcoords[i+1], y1), width)

def create_gradient_ball(diameter, inner_color, outer_color):
    surface = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
    center = diameter // 2
    for x in range(diameter):
        for y in range(diameter):
            distance = math.sqrt((x - center) ** 2 + (y - center) ** 2)
            if distance <= center:
                ratio = distance / center
                color = [
                    inner_color[i] * (1 - ratio) + outer_color[i] * ratio
                    for i in range(3)
                ]
                surface.set_at((x, y), color + [255])
    return surface

def print_distance_from_ball(ball_pos, ball_size, paddle_pos, extra_message = ""):
    ball_center_y = ball_pos[1] + ball_size / 2
    distance = ball_center_y - paddle_pos
    print(extra_message + f"Ball was {abs(distance):.2f} pixels away from the paddle's center.\033[0m")

def main(conn=None):
    print("BRAIN PONG RUNNING")
    pygame.init()

    # Game constants
    WINDOW_WIDTH, WINDOW_HEIGHT = 1200, 625
    FPS = 60
    PHYSICS_FPS = 240
    PADDLE_WIDTH = 15
    PADDLE_MIN_HEIGHT = 50
    PADDLE_MAX_HEIGHT = 250
    BALL_DIAMETER = 25
    WINNING_SCORE = 5
    PLAYER_1_VEL = 500
    PLAYER_2_VEL = 500
    COUNTDOWN_SECONDS = 5
    BALL_VEL = 250

    # Colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    BG_COLOR = (191, 87, 32)

    # Get display information
    disp_info = pygame.display.Info()
    DISPLAY_WIDTH = disp_info.current_w
    DISPLAY_HEIGHT = disp_info.current_h

    # Game variables
    player_y = player2_y = WINDOW_HEIGHT / 2
    player_velocity = player2_velocity = 0
    player_height = player2_height = 125
    has_just_missed = False

    # Initial ball position and velocity
    initial_ball_pos = [(WINDOW_WIDTH - BALL_DIAMETER) / 2, (WINDOW_HEIGHT - BALL_DIAMETER) / 2]
    initial_ball_vel = [BALL_VEL, BALL_VEL]
    ball_pos = list(copy(initial_ball_pos))
    ball_vel = list(copy(initial_ball_vel))

    # Game state variables
    score = [0, 0]
    game_state = "MENU"
    countdown_timer = COUNTDOWN_SECONDS * 1000
    display_instructions = True

    # Fullscreen variables
    fullscreen = False
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    scale_factor = 1
    fullscreen_offset = (0, 0)

    # Create game window
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Pygame Brain Pong Game")

    # Load and scale background image
    bg_image = pygame.image.load('Picture2.png').convert()
    bg_image = pygame.transform.scale(bg_image, (WINDOW_WIDTH, WINDOW_HEIGHT))

    # Create a surface for static elements
    static_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)

    # Fonts
    font = pygame.font.SysFont("Monaco", 28, bold=True)
    countdown_font = pygame.font.SysFont("Monaco", 72, bold=True)
    instructions_font = pygame.font.SysFont("Monaco", 16, bold=True)

    # Game mode and external command
    game_mode = "HUMAN_VS_HUMAN"
    external_command = 0

    # Create the gradient ball surface
    BALL_INNER_COLOR = (255, 255, 255)
    BALL_OUTER_COLOR = (150, 150, 150)
    ball_surface = create_gradient_ball(BALL_DIAMETER, BALL_INNER_COLOR, BALL_OUTER_COLOR)

    # Global variables for optimized rendering
    bg_with_static = None
    instruction_surfaces = {}
    score_surface = None
    score_changed = True

    # Draw the dotted center line
    draw_dotted_line(static_surface, WHITE, (WINDOW_WIDTH // 2, 0), (WINDOW_WIDTH // 2, WINDOW_HEIGHT), width=3, dash_length=20)

    def initialize_game():
        nonlocal bg_with_static, instruction_surfaces, score_surface
        
        bg_with_static = bg_image.copy()
        bg_with_static.blit(static_surface, (0, 0))
        
        instruction_surfaces = {
            "left": instructions_font.render("Move: W/S, Height: Q/A", True, WHITE),
            "right": instructions_font.render("Move: Up/Down, Height: P/L", True, WHITE)
        }
        
        score_surface = font.render("0   0", True, WHITE)

    def reset_game():
        nonlocal score, ball_pos, ball_vel, game_state, countdown_timer, player_y
        nonlocal player2_y, player_height, player2_height, score_changed
        nonlocal player_velocity, player2_velocity
        score = [0, 0]
        ball_pos = list(copy(initial_ball_pos))
        ball_vel = list(copy(initial_ball_vel))
        game_state = "COUNTDOWN"
        countdown_timer = COUNTDOWN_SECONDS * 1000
        player_y = player2_y = WINDOW_HEIGHT / 2
        player_height = player2_height = 125
        score_changed = True
        player_velocity = player2_velocity = 0

    def draw_game(interpolation):
        nonlocal score_surface, score_changed
        
        window.blit(bg_with_static, (0, 0))
        
        # Draw paddles
        pygame.draw.rect(window, WHITE, (35, player_y - player_height/2, PADDLE_WIDTH, player_height))
        pygame.draw.rect(window, WHITE, (WINDOW_WIDTH - 35 - PADDLE_WIDTH, player2_y - player2_height/2, PADDLE_WIDTH, player2_height))
        
        # Draw ball
        ball_draw_pos = [
            ball_pos[0] + ball_vel[0] * interpolation / PHYSICS_FPS,
            ball_pos[1] + ball_vel[1] * interpolation / PHYSICS_FPS
        ]
        ball_int_pos = (int(ball_draw_pos[0]), int(ball_draw_pos[1]))
        window.blit(ball_surface, ball_int_pos)
        
        # Draw score
        if score_changed:
            score_surface = font.render(f"{score[0]}   {score[1]}", True, WHITE)
            score_changed = False
        window.blit(score_surface, (WINDOW_WIDTH // 2 - score_surface.get_width() // 2, 35))

        # Draw instructions
        if display_instructions:
            window.blit(instruction_surfaces["left"], ((WINDOW_WIDTH // 2) - 30 - instruction_surfaces["left"].get_width(), WINDOW_HEIGHT - 40))
            window.blit(instruction_surfaces["right"], ((WINDOW_WIDTH // 2) + 30, WINDOW_HEIGHT - 40))

        # Draw countdown
        if game_state == "COUNTDOWN":
            seconds_left = countdown_timer // 1000 + 1
            countdown_text = countdown_font.render(str(int(seconds_left)), True, WHITE)
            window.blit(countdown_text, (WINDOW_WIDTH // 2 - countdown_text.get_width() // 2, WINDOW_HEIGHT // 4 - countdown_text.get_height() // 2))

    def update_game(dt):
        nonlocal player_y, player2_y, ball_pos, ball_vel, score, game_state
        nonlocal display_instructions, countdown_timer, score_changed
        nonlocal player_velocity, has_just_missed

        if game_state == "COUNTDOWN":
            countdown_timer -= dt * 1000
            if countdown_timer <= 0:
                game_state = "PLAYING"
            return

        if game_mode == "HUMAN_VS_AI":
            if external_command == 0:
                player_velocity = -PLAYER_1_VEL
            else:
                player_velocity = PLAYER_1_VEL

        # Update paddle positions
        player_y += player_velocity * dt
        player2_y += player2_velocity * dt

        # Keep paddles within screen bounds
        player_y = max(player_height/2, min(player_y, WINDOW_HEIGHT - player_height/2))
        player2_y = max(player2_height/2, min(player2_y, WINDOW_HEIGHT - player2_height/2))

        # Update ball position
        ball_pos[0] += ball_vel[0] * dt
        ball_pos[1] += ball_vel[1] * dt

        # Ball collision with top and bottom walls
        if ball_pos[1] <= 0 or ball_pos[1] >= WINDOW_HEIGHT - BALL_DIAMETER:
            ball_vel[1] = -ball_vel[1]
            ball_pos[1] = max(0, min(ball_pos[1], WINDOW_HEIGHT - BALL_DIAMETER))

        # Ball collision with paddles
        if (35 <= ball_pos[0] <= 35 + PADDLE_WIDTH and 
            player_y - player_height/2 - BALL_DIAMETER <= ball_pos[1] <= 
            player_y + player_height/2):
            ball_vel[0] = abs(ball_vel[0])
            ball_pos[0] = 35 + PADDLE_WIDTH
            print_distance_from_ball(ball_pos, BALL_DIAMETER, player_y, 
                                     extra_message = "\033[92mPlayer 1 hit the ball! ")
            
        elif (WINDOW_WIDTH - 35 - PADDLE_WIDTH <= 
              ball_pos[0] + BALL_DIAMETER <= WINDOW_WIDTH - 35 and 
              player2_y - player2_height/2 - BALL_DIAMETER <= 
              ball_pos[1] <= player2_y + player2_height/2):
            ball_vel[0] = -abs(ball_vel[0])
            ball_pos[0] = WINDOW_WIDTH - 35 - PADDLE_WIDTH - BALL_DIAMETER
            print_distance_from_ball(ball_pos, BALL_DIAMETER, player2_y, 
                                     extra_message = "\033[92mPlayer 2 hit the ball! ")

        # Check for misses to print, unless a miss has just happened and we're
        # waiting for a reset.
        if not has_just_missed:
            if ball_pos[0] < BALL_DIAMETER:
                print_distance_from_ball(ball_pos, BALL_DIAMETER, player_y, extra_message = "\033[91mPlayer 1 missed! ")
                has_just_missed = True
            elif ball_pos[0] > WINDOW_WIDTH - 35:
                print_distance_from_ball(ball_pos, BALL_DIAMETER, player2_y, extra_message = "\033[91mPlayer 2 missed! ")
                has_just_missed = True

        # Ball out of bounds (scoring)
        if ball_pos[0] < -BALL_DIAMETER:
            score[1] += 1
            score_changed = True
            ball_pos = list(copy(initial_ball_pos))
            vel_coeff = 1 if random.uniform(-1, 1) > 0 else -1
            ball_vel = [BALL_VEL, vel_coeff * BALL_VEL]
            has_just_missed = False
        elif ball_pos[0] > WINDOW_WIDTH:
            score[0] += 1
            score_changed = True
            ball_pos = list(copy(initial_ball_pos))
            vel_coeff = 1 if random.uniform(-1, 1) > 0 else -1
            ball_vel = [-BALL_VEL, vel_coeff * BALL_VEL]
            has_just_missed = False

        # Check for game over
        if score[0] >= WINNING_SCORE or score[1] >= WINNING_SCORE:
            game_state = "GAME_OVER"

    def draw_menu():
        window.blit(bg_with_static, (0, 0))
        title_text = font.render("Pong Game", True, WHITE)
        option1_text = font.render("1. Human vs Human", True, WHITE)
        option2_text = font.render("2. Human vs AI", True, WHITE)
        window.blit(title_text, (WINDOW_WIDTH // 2 - title_text.get_width() // 2, WINDOW_HEIGHT // 4))
        window.blit(option1_text, (WINDOW_WIDTH // 2 - option1_text.get_width() // 2, WINDOW_HEIGHT // 2))
        window.blit(option2_text, (WINDOW_WIDTH // 2 - option2_text.get_width() // 2, WINDOW_HEIGHT // 2 + 50))

    def draw_game_over_screen():
        window.blit(bg_with_static, (0, 0))
        winner = "Player 1" if score[0] >= WINNING_SCORE else "Player 2"
        winner_text = font.render(f"{winner} Wins!", True, WHITE)
        restart_text = font.render("Press Space to Restart", True, WHITE)
        menu_text = font.render("Press M for Menu", True, WHITE)
        window.blit(winner_text, (WINDOW_WIDTH // 2 - winner_text.get_width() // 2, WINDOW_HEIGHT // 3))
        window.blit(restart_text, (WINDOW_WIDTH // 2 - restart_text.get_width() // 2, WINDOW_HEIGHT // 2 + 50))
        window.blit(menu_text, (WINDOW_WIDTH // 2 - menu_text.get_width() // 2, WINDOW_HEIGHT // 2 + 100))

    def toggle_fullscreen():
        nonlocal fullscreen, screen, scale_factor, window, fullscreen_offset
        fullscreen = not fullscreen
        if fullscreen:
            screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            screen_info = pygame.display.Info()
            DISPLAY_WIDTH, DISPLAY_HEIGHT = screen_info.current_w, screen_info.current_h
            
            # Calculate the scale factor to fill the screen while maintaining aspect ratio
            scale_factor = min(DISPLAY_WIDTH / WINDOW_WIDTH, DISPLAY_HEIGHT / WINDOW_HEIGHT)
            
            # Calculate the size of the scaled game surface
            scaled_width = int(WINDOW_WIDTH * scale_factor)
            scaled_height = int(WINDOW_HEIGHT * scale_factor)
            
            # Calculate the offset to center the game on the screen
            fullscreen_offset = (
                (DISPLAY_WIDTH - scaled_width) // 2,
                (DISPLAY_HEIGHT - scaled_height) // 2
            )
        else:
            screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
            fullscreen_offset = (0, 0)
            scale_factor = 1
        window = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))

    def scale_surface(surface):
        if fullscreen:
            return pygame.transform.scale(surface, 
                                          (int(surface.get_width() * scale_factor),
                                           int(surface.get_height() * scale_factor)))
        return surface

    initialize_game()
    clock = pygame.time.Clock()
    
    physics_time = 0
    physics_step = 1 / PHYSICS_FPS

    while True:
        dt = clock.tick(FPS) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return
                if event.key == pygame.K_f:
                    toggle_fullscreen()
                elif game_state == "MENU":
                    if event.key == pygame.K_1:
                        game_mode = "HUMAN_VS_HUMAN"
                        game_state = "COUNTDOWN"
                        reset_game()
                    elif event.key == pygame.K_2:
                        game_mode = "HUMAN_VS_AI"
                        game_state = "COUNTDOWN"
                        reset_game()
                elif game_state == "PLAYING":
                    if game_mode == "HUMAN_VS_HUMAN":
                        if event.key == pygame.K_w:
                            player_velocity = -PLAYER_1_VEL
                            display_instructions = False
                        elif event.key == pygame.K_s:
                            player_velocity = PLAYER_1_VEL
                            display_instructions = False
                    if event.key == pygame.K_UP:
                        player2_velocity = -PLAYER_2_VEL
                        display_instructions = False
                    elif event.key == pygame.K_DOWN:
                        player2_velocity = PLAYER_2_VEL
                        display_instructions = False
                    elif event.key == pygame.K_q:
                        player_height = min(player_height + 10, PADDLE_MAX_HEIGHT)
                    elif event.key == pygame.K_a:
                        player_height = max(player_height - 10, PADDLE_MIN_HEIGHT)
                    elif event.key == pygame.K_p:
                        player2_height = min(player2_height + 10, PADDLE_MAX_HEIGHT)
                    elif event.key == pygame.K_l:
                        player2_height = max(player2_height - 10, PADDLE_MIN_HEIGHT)
                elif game_state == "GAME_OVER":
                    if event.key == pygame.K_SPACE:
                        reset_game()
                    elif event.key == pygame.K_m:
                        game_state = "MENU"
            elif event.type == pygame.KEYUP:
                if game_mode == "HUMAN_VS_HUMAN":
                    if event.key in (pygame.K_w, pygame.K_s):
                        player_velocity = 0
                if event.key in (pygame.K_UP, pygame.K_DOWN):
                    player2_velocity = 0

        # Handle external commands in HUMAN_VS_AI (brain) mode
        if game_mode == "HUMAN_VS_AI" and conn:
            if conn.poll():
                external_command = conn.recv()
                player_velocity = -PLAYER_1_VEL if external_command == 0 else PLAYER_1_VEL

        # Update and draw game based on current state
        if game_state == "MENU":
            draw_menu()
        elif game_state != "GAME_OVER":
            physics_time += dt
            while physics_time >= physics_step:
                update_game(physics_step)
                physics_time -= physics_step
            
            interpolation = physics_time / physics_step
            draw_game(interpolation)
        else:
            draw_game_over_screen()

        # Handle fullscreen scaling
        if fullscreen:
            scaled_surface = pygame.transform.scale(window, 
                                                    (int(WINDOW_WIDTH * scale_factor),
                                                     int(WINDOW_HEIGHT * scale_factor)))
            screen.fill((0, 0, 0))  # Fill the screen with black
            screen.blit(scaled_surface, fullscreen_offset)
        else:
            screen.blit(window, (0, 0))
        
        pygame.display.flip()

if __name__ == "__main__":
    main()