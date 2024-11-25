# /game/main.py

import pygame
import random
import time
import sys
from multiprocessing import Pipe

from game.config import *
from game.utils import create_gradient_ball, print_distance_from_ball
from game.entities import Paddle, Ball
from game.input_handler import handle_input
from game.render import draw_game, draw_menu, draw_game_over_screen, draw_static_elements
from game.pong_practice import practice_mode

def practice_mode(conn, window, screen, clock, fullscreen, scale_factor, fullscreen_offset, bg_with_static):
    """
    Function to handle the practice mode.

    Args:
        conn: Connection object for inter-process communication.
        window: Pygame window surface.
        screen: Pygame display surface (may be same as window or scaled).
        clock: Pygame clock object.
        fullscreen: Boolean indicating if fullscreen mode is active.
        scale_factor: Scale factor for fullscreen mode.
        fullscreen_offset: Offset for centering the game in fullscreen mode.
        bg_with_static: Pre-rendered background with static elements.
    """
    # Set up variables specific to practice mode
    # Game constants
    PADDLE_WIDTH = 15
    PLAYER_1_VEL = 200
    WHITE = (255, 255, 255)
    COUNTDOWN_SECONDS = 2  # Duration of the focus period (plus sign)
    TRIAL_DURATION = 5     # Duration of each trial in seconds
    REST_DURATION = 3      # Duration of rest period in seconds

    # Fonts
    font = pygame.font.SysFont("Monaco", 28, bold=True)
    countdown_font = pygame.font.SysFont("Monaco", 72, bold=True)
    plus_font = pygame.font.SysFont("Monaco", 150, bold=True)  # Bigger font for plus sign

    # Game variables
    player_y = WINDOW_HEIGHT / 2
    player_velocity = 0
    player_height = PADDLE_INITIAL_HEIGHT

    # Timing variables
    trial_start_time = None
    period_start_time = None
    period = 'waiting'  # Start with waiting period
    period_duration = {
        'waiting': 3,     # Wait for 3 seconds before starting
        'focus': COUNTDOWN_SECONDS,
        'prompt': 1.5,  # Duration to show the arrow
        'pre_trial': 0,  # No additional time needed
        'trial': TRIAL_DURATION,
        'rest': REST_DURATION
    }

    # Control variables
    external_command = 0
    direction = None  # 'up' or 'down'

    # Flags
    running = True
    display_instructions = True

    # Instruction surfaces
    instruction_text1 = "Press SPACE to start"
    instruction_text2 = "Focus on moving the paddle as indicated"
    instruction_surface1 = font.render(instruction_text1, True, WHITE)
    instruction_surface2 = font.render(instruction_text2, True, WHITE)

    index = None  # Initialize index

    predicted_direction = None  # Initialize predicted_direction

    while running:
        dt = clock.tick(FPS) / 1000.0  # Delta time in seconds

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                # Return to main menu
                return 'MAIN_MENU', fullscreen, scale_factor, fullscreen_offset
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    # Return to main menu
                    return 'MAIN_MENU', fullscreen, scale_factor, fullscreen_offset
                elif event.key == pygame.K_f:
                    # Handle fullscreen toggle
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                        screen_info = pygame.display.Info()
                        display_width, display_height = screen_info.current_w, screen_info.current_h
                        scale_factor = min(display_width / WINDOW_WIDTH, display_height / WINDOW_HEIGHT)
                        scaled_width = int(WINDOW_WIDTH * scale_factor)
                        scaled_height = int(WINDOW_HEIGHT * scale_factor)
                        fullscreen_offset = (
                            (display_width - scaled_width) // 2,
                            (display_height - scaled_height) // 2
                        )
                    else:
                        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
                        fullscreen_offset = (0, 0)
                        scale_factor = 1
                elif event.key == pygame.K_SPACE:
                    display_instructions = False

        # Game logic
        if display_instructions:
            # Display instructions until the user presses space
            window.blit(bg_with_static, (0, 0))
            # Draw instruction texts
            window.blit(instruction_surface1, (WINDOW_WIDTH // 2 - instruction_surface1.get_width() // 2,
                                               WINDOW_HEIGHT // 2 - instruction_surface1.get_height()))
            window.blit(instruction_surface2, (WINDOW_WIDTH // 2 - instruction_surface2.get_width() // 2,
                                               WINDOW_HEIGHT // 2 + instruction_surface1.get_height()))
            pygame.display.flip()
            continue

        if period_start_time is None:
            # Initialize the period
            period_start_time = pygame.time.get_ticks()
            if period == 'waiting':
                pass  # No additional initialization needed
            elif period == 'focus':
                # Reset variables for a new trial
                player_y = WINDOW_HEIGHT / 2
                player_velocity = 0
                direction = random.choice(['up', 'down'])
                index = None
                # Clear any remaining messages
                if conn:
                    while conn.poll():
                        conn.recv()
            elif period == 'prompt':
                pass  # No additional initialization needed
            elif period == 'pre_trial':
                pass  # No additional initialization needed
            elif period == 'trial':
                trial_start_time = pygame.time.get_ticks()
            elif period == 'rest':
                pass  # No additional initialization needed

        elapsed_time = (pygame.time.get_ticks() - period_start_time) / 1000.0
        if elapsed_time >= period_duration[period]:
            # Transition to the next period
            period_start_time = None
            if period == 'waiting':
                period = 'focus'
            elif period == 'focus':
                period = 'prompt'
            elif period == 'prompt':
                period = 'pre_trial'
            elif period == 'pre_trial':
                period = 'trial'
            elif period == 'trial':
                period = 'rest'
            elif period == 'rest':
                # Loop back to 'focus'
                period = 'focus'
            continue

        # Always draw the game environment
        window.blit(bg_with_static, (0, 0))
        # Draw paddles
        pygame.draw.rect(window, WHITE, (35, player_y - player_height / 2, PADDLE_WIDTH, player_height))
        # Draw opponent paddle in its default position (static)
        pygame.draw.rect(window, WHITE, (WINDOW_WIDTH - 35 - PADDLE_WIDTH, WINDOW_HEIGHT / 2 - player_height / 2, PADDLE_WIDTH, player_height))

        # Handle current period logic
        if period == 'waiting':
            # Display waiting message
            waiting_font = font
            waiting_text = waiting_font.render("Preparing...", True, WHITE)
            window.blit(waiting_text, (WINDOW_WIDTH // 2 - waiting_text.get_width() // 2,
                                       WINDOW_HEIGHT // 2 - waiting_text.get_height() // 2))
        elif period == 'focus':
            # Display focus period (plus sign '+')
            plus_text = plus_font.render("+", True, WHITE)
            window.blit(plus_text, (WINDOW_WIDTH // 2 - plus_text.get_width() // 2,
                                    WINDOW_HEIGHT // 2 - plus_text.get_height() // 2))
        elif period == 'prompt' or period == 'pre_trial' or period == 'trial':
            # Display the direction arrow in the center
            arrow_length = 50
            arrow_width = 20
            arrow_color = WHITE
            if direction == 'up':
                arrow_points = [
                    (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - arrow_length),
                    (WINDOW_WIDTH // 2 - arrow_width, WINDOW_HEIGHT // 2),
                    (WINDOW_WIDTH // 2 + arrow_width, WINDOW_HEIGHT // 2)
                ]
            else:
                arrow_points = [
                    (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + arrow_length),
                    (WINDOW_WIDTH // 2 - arrow_width, WINDOW_HEIGHT // 2),
                    (WINDOW_WIDTH // 2 + arrow_width, WINDOW_HEIGHT // 2)
                ]
            pygame.draw.polygon(window, arrow_color, arrow_points)

            if period == 'trial':
                # Trial is active
                # Receive predictions from the model
                if conn and conn.poll():
                    try:
                        message = conn.recv()
                        if isinstance(message, dict) and message.get('type') == 'DATA':
                            predicted_direction = message['command']
                            index = message['index']
                            if predicted_direction == 1:
                                player_velocity = -PLAYER_1_VEL
                            elif predicted_direction == 0:
                                player_velocity = PLAYER_1_VEL
                            else:
                                player_velocity = 0
                    except Exception as e:
                        print(f"Error receiving from conn: {e}")
                        index = None  # Reset index on error

                # Update paddle position
                player_y += player_velocity * dt
                player_y = max(player_height / 2, min(player_y, WINDOW_HEIGHT - player_height / 2))

                # Check if the paddle has hit the edge
                if player_y <= player_height / 2 or player_y >= WINDOW_HEIGHT - player_height / 2:
                    # Paddle has hit the edge; end the trial immediately
                    period = 'rest'
                    period_start_time = None
                    # Send done signal to model
                    if index is not None and conn:
                        predicted_int = predicted_direction
                        correct_int = 1 if direction == 'up' else 0
                        done = True
                        conn.send({
                            'type': 'FEEDBACK',
                            'pred': predicted_int,
                            'correct': correct_int,
                            'index': index,
                            'done': done
                        })
                        index = None  # Reset index after sending done signal

                # Send feedback to the model
                elif index is not None and conn:
                    predicted_int = predicted_direction
                    correct_int = 1 if direction == 'up' else 0
                    done = False
                    conn.send({
                        'type': 'FEEDBACK',
                        'pred': predicted_int,
                        'correct': correct_int,
                        'index': index,
                        'done': done
                    })

        elif period == 'rest':
            # Display rest message
            rest_font = font
            rest_text = rest_font.render("Rest", True, WHITE)
            window.blit(rest_text, (WINDOW_WIDTH // 2 - rest_text.get_width() // 2, WINDOW_HEIGHT // 2 - rest_text.get_height() // 2))
            # Optionally send done signal to model at the start of rest period
            if index is not None and conn:
                predicted_int = predicted_direction
                correct_int = 1 if direction == 'up' else 0
                done = True  # Indicate trial is done
                conn.send({
                    'type': 'FEEDBACK',
                    'pred': predicted_int,
                    'correct': correct_int,
                    'index': index,
                    'done': done
                })
                index = None  # Reset index after sending done signal

        # Handle fullscreen scaling
        if fullscreen:
            scaled_surface = pygame.transform.scale(
                window,
                (int(WINDOW_WIDTH * scale_factor), int(WINDOW_HEIGHT * scale_factor))
            )
            screen.fill(BLACK)
            screen.blit(scaled_surface, fullscreen_offset)
        else:
            screen.blit(window, (0, 0))

        pygame.display.flip()

    # Practice mode completed or exited
    # Return to main menu
    return 'MAIN_MENU', fullscreen, scale_factor, fullscreen_offset

def main(conn=None):
    """
    Main function to run the Pong game.

    Args:
        conn: Optional multiprocessing connection for external commands.
    """
    print("Starting Pygame Brain Pong Game...")
    pygame.init()
    clock = pygame.time.Clock()

    # Create game window
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Pygame Brain Pong Game")

    # Load and scale background image
    bg_image = pygame.image.load('assets/Picture2.png').convert()
    bg_image = pygame.transform.scale(bg_image, (WINDOW_WIDTH, WINDOW_HEIGHT))

    # Pre-rendered static elements
    bg_with_static = draw_static_elements(bg_image)

    # Game variables
    game_state = "MAIN_MENU"
    display_instructions = True
    external_command = 0
    game_mode = None
    score = [0, 0]
    countdown_timer = COUNTDOWN_SECONDS * 1000
    has_just_missed = False
    fullscreen = False
    scale_factor = 1
    fullscreen_offset = (0, 0)
    screen = window

    # Initialize paddles and ball
    player1 = Paddle(35, WINDOW_HEIGHT / 2, PADDLE_INITIAL_HEIGHT, PLAYER_1_VEL)
    player2 = Paddle(WINDOW_WIDTH - 35 - PADDLE_WIDTH, WINDOW_HEIGHT / 2, PADDLE_INITIAL_HEIGHT, PLAYER_2_VEL)
    ball = Ball(
        (WINDOW_WIDTH - BALL_DIAMETER) / 2,
        (WINDOW_HEIGHT - BALL_DIAMETER) / 2,
        BALL_DIAMETER,
        BALL_VEL
    )

    ball_surface = create_gradient_ball(BALL_DIAMETER, BALL_INNER_COLOR, BALL_OUTER_COLOR)

    # Physics timing
    physics_time = 0
    physics_step = 1 / PHYSICS_FPS

    # Game actions
    game_actions = {
        'toggle_fullscreen': False,
        'start_game': None,
        'restart': False,
        'menu': False,
        'selected_option': None
    }

    # Fonts for menu
    menu_font = pygame.font.SysFont("Monaco", 40, bold=True)
    menu_options = ["Play Game", "Fine-tune Model", "Exit"]
    selected_option_index = 0
    menu_option_rects = []

    while True:
        dt = clock.tick(FPS) / 1000.0

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            handle_input(event, game_state, (player1, player2), game_actions)
            # Handle menu navigation
            if game_state == "MAIN_MENU":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_option_index = (selected_option_index - 1) % len(menu_options)
                    elif event.key == pygame.K_DOWN:
                        selected_option_index = (selected_option_index + 1) % len(menu_options)
                    elif event.key == pygame.K_RETURN:
                        game_actions['selected_option'] = menu_options[selected_option_index]
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos  # Get the mouse position
                    # Check if the mouse click is within any of the option rects
                    for idx, rect in enumerate(menu_option_rects):
                        if rect.collidepoint(mouse_pos):
                            selected_option_index = idx
                            game_actions['selected_option'] = menu_options[selected_option_index]
                            break  # Exit the loop after finding the clicked option

        # Handle game actions
        if game_actions['toggle_fullscreen']:
            fullscreen = not fullscreen
            if fullscreen:
                screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                screen_info = pygame.display.Info()
                display_width, display_height = screen_info.current_w, screen_info.current_h
                scale_factor = min(display_width / WINDOW_WIDTH, display_height / WINDOW_HEIGHT)
                scaled_width = int(WINDOW_WIDTH * scale_factor)
                scaled_height = int(WINDOW_HEIGHT * scale_factor)
                fullscreen_offset = (
                    (display_width - scaled_width) // 2,
                    (display_height - scaled_height) // 2
                )
            else:
                screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
                fullscreen_offset = (0, 0)
                scale_factor = 1
            game_actions['toggle_fullscreen'] = False

        if game_actions['selected_option']:
            selected_option = game_actions['selected_option']
            if selected_option == "Play Game":
                game_mode = "HUMAN_VS_AI"  # Or "HUMAN_VS_AI"
                game_state = "COUNTDOWN"
                score = [0, 0]
                countdown_timer = COUNTDOWN_SECONDS * 1000
                player1.y = player2.y = WINDOW_HEIGHT / 2
                player1.height = player2.height = PADDLE_INITIAL_HEIGHT
                ball.x = (WINDOW_WIDTH - BALL_DIAMETER) / 2
                ball.y = (WINDOW_HEIGHT - BALL_DIAMETER) / 2
                ball.vx = BALL_VEL * (1 if random.choice([True, False]) else -1)
                ball.vy = BALL_VEL * (1 if random.choice([True, False]) else -1)
                game_actions['selected_option'] = None
                if conn:
                    conn.send({'type': 'SET_MODE', 'mode': 'PLAY'})
            elif selected_option == "Fine-tune Model":
                game_state = "PRACTICE_MODE"
                game_actions['selected_option'] = None
                if conn:
                    conn.send({'type': 'SET_MODE', 'mode': 'TRAIN'})
            elif selected_option == "Exit":
                pygame.quit()
                return

        if game_actions['restart']:
            game_state = "COUNTDOWN"
            score = [0, 0]
            countdown_timer = COUNTDOWN_SECONDS * 1000
            player1.y = player2.y = WINDOW_HEIGHT / 2
            player1.height = player2.height = PADDLE_INITIAL_HEIGHT
            ball.x = (WINDOW_WIDTH - BALL_DIAMETER) / 2
            ball.y = (WINDOW_HEIGHT - BALL_DIAMETER) / 2
            ball.vx = BALL_VEL * (1 if random.choice([True, False]) else -1)
            ball.vy = BALL_VEL * (1 if random.choice([True, False]) else -1)
            game_actions['restart'] = False

        if game_actions['menu']:
            game_state = "MAIN_MENU"
            game_actions['menu'] = False

        # Handle external commands
        if game_mode == "HUMAN_VS_AI" and conn:
            if conn.poll():
                message = conn.recv()
                if isinstance(message, dict) and message.get('type') == 'DATA':
                    external_command = message['command']
                    # Update player movement based on external_command
                    if external_command == 0:
                        player1.movement = -1
                    else:
                        player1.movement = 1

        # Game logic updates
        if game_state == "COUNTDOWN":
            countdown_timer -= dt * 1000
            if countdown_timer <= 0:
                game_state = "PLAYING"

        elif game_state == "PLAYING":
            physics_time += dt
            while physics_time >= physics_step:
                # Update paddles
                player1.move(physics_step)
                player2.move(physics_step)

                # Update ball
                ball.move(physics_step)

                # Ball collision with walls
                if ball.y <= 0 or ball.y >= WINDOW_HEIGHT - BALL_DIAMETER:
                    ball.vy = -ball.vy
                    ball.y = max(0, min(ball.y, WINDOW_HEIGHT - BALL_DIAMETER))

                if (
                    35 <= ball.x <= 35 + PADDLE_WIDTH and
                    player1.y - player1.height / 2 - BALL_DIAMETER <= ball.y <= player1.y + player1.height / 2
                ):
                    ball.vx = abs(ball.vx)
                    ball.x = 35 + PADDLE_WIDTH
                    print_distance_from_ball(
                        (ball.x, ball.y), BALL_DIAMETER, player1.y,
                        extra_message="\033[92mPlayer 1 hit the ball! "
                    )

                elif (
                    WINDOW_WIDTH - 35 - PADDLE_WIDTH <= ball.x + BALL_DIAMETER <= WINDOW_WIDTH - 35 and
                    player2.y - player2.height / 2 - BALL_DIAMETER <= ball.y <= player2.y + player2.height / 2
                ):
                    ball.vx = -abs(ball.vx)
                    ball.x = WINDOW_WIDTH - 35 - PADDLE_WIDTH - BALL_DIAMETER
                    print_distance_from_ball(
                        (ball.x, ball.y), BALL_DIAMETER, player2.y,
                        extra_message="\033[92mPlayer 2 hit the ball! "
                    )

                # Check for misses
                if not has_just_missed:
                    if ball.x < BALL_DIAMETER:
                        print_distance_from_ball(
                            (ball.x, ball.y), BALL_DIAMETER, player1.y,
                            extra_message="\033[91mPlayer 1 missed! "
                        )
                        has_just_missed = True
                    elif ball.x > WINDOW_WIDTH - 35:
                        print_distance_from_ball(
                            (ball.x, ball.y), BALL_DIAMETER, player2.y,
                            extra_message="\033[91mPlayer 2 missed! "
                        )
                        has_just_missed = True

                # Ball out of bounds (scoring)
                if ball.x < -BALL_DIAMETER:
                    score[1] += 1
                    ball.x = (WINDOW_WIDTH - BALL_DIAMETER) / 2
                    ball.y = (WINDOW_HEIGHT - BALL_DIAMETER) / 2
                    ball.vx = BALL_VEL
                    ball.vy = BALL_VEL * (1 if random.choice([True, False]) else -1)
                    has_just_missed = False
                elif ball.x > WINDOW_WIDTH:
                    score[0] += 1
                    ball.x = (WINDOW_WIDTH - BALL_DIAMETER) / 2
                    ball.y = (WINDOW_HEIGHT - BALL_DIAMETER) / 2
                    ball.vx = -BALL_VEL
                    ball.vy = BALL_VEL * (1 if random.choice([True, False]) else -1)
                    has_just_missed = False

                # Check for game over
                if score[0] >= WINNING_SCORE or score[1] >= WINNING_SCORE:
                    game_state = "GAME_OVER"

                physics_time -= physics_step

                physics_time -= physics_step

        elif game_state == "PRACTICE_MODE":
            # Call the practice_mode function
            result = practice_mode(conn, window, screen, clock, fullscreen, scale_factor, fullscreen_offset, bg_with_static)
            # Unpack the result
            game_state, fullscreen, scale_factor, fullscreen_offset = result
            # Continue the main loop with the updated game_state and variables
            continue

        # Drawing
        if game_state == "MAIN_MENU":
            menu_option_rects = draw_menu(window, bg_with_static, menu_font, menu_options)
        elif game_state != "GAME_OVER" and game_state != "PRACTICE_MODE":
            interpolation = physics_time / physics_step
            draw_game(
                window, bg_with_static, (player1, player2), ball, score,
                display_instructions, game_state, countdown_timer, ball_surface, interpolation
            )
        elif game_state == "GAME_OVER":
            draw_game_over_screen(window, bg_with_static, score)

        # Handle fullscreen scaling
        if fullscreen:
            scaled_surface = pygame.transform.scale(
                window,
                (int(WINDOW_WIDTH * scale_factor), int(WINDOW_HEIGHT * scale_factor))
            )
            screen.fill(BLACK)
            screen.blit(scaled_surface, fullscreen_offset)
        else:
            screen.blit(window, (0, 0))

        pygame.display.flip()

if __name__ == "__main__":
    main()