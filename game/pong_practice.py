import pygame
import random
from game.config import *
from game.utils import *

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