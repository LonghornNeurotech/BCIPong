import pygame
import time
from multiprocessing import Pipe

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

def main(conn=None):
    pygame.init()

    # Constants
    WINDOW_WIDTH, WINDOW_HEIGHT = 1200, 625
    PADDLE_WIDTH, PADDLE_HEIGHT = 15, 125
    PADDLE_COLOR = (255, 255, 255)
    WHITE = (255, 255, 255)
    BG_COLOR = (0, 0, 0)
    FPS = 60
    MOVE_STEP = 5  # Paddle movement speed
    BORDER_MARGIN = 0  # Allow the paddle to go all the way to the top
    TASK_DELAY = 1  # Delay in seconds between tasks
    FOCUS_PERIOD = 2  # Focus period before the task starts
    ARROW_SIZE = 40  # Size of the arrow

    # Fullscreen-related variables
    fullscreen = False
    scale_factor = 1
    fullscreen_offset = (0, 0)

    # Create the display window
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Motor Imagery Practice")

    # Paddle initial position (middle of the screen)
    paddle_y = WINDOW_HEIGHT // 2 - PADDLE_HEIGHT // 2
    paddle_x = 35  # Paddle is placed on the left like in Pong

    # Task variables
    direction = 0  # 0: No movement, 1: Up, -1: Down
    task_counter = 0  # To alternate between up and down tasks
    received = False

    # Clock
    clock = pygame.time.Clock()

    # Background setup
    static_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    draw_dotted_line(static_surface, WHITE, (WINDOW_WIDTH // 2, 0), (WINDOW_WIDTH // 2, WINDOW_HEIGHT), width=3, dash_length=20)

    def toggle_fullscreen():
        nonlocal fullscreen, window, scale_factor, fullscreen_offset
        fullscreen = not fullscreen
        if fullscreen:
            screen_info = pygame.display.Info()
            DISPLAY_WIDTH, DISPLAY_HEIGHT = screen_info.current_w, screen_info.current_h
            
            # Set the display to fullscreen mode
            window = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT), pygame.FULLSCREEN)

            # Calculate the scale factor to maintain the aspect ratio
            scale_factor = min(DISPLAY_WIDTH / WINDOW_WIDTH, DISPLAY_HEIGHT / WINDOW_HEIGHT)
            scaled_width = int(WINDOW_WIDTH * scale_factor)
            scaled_height = int(WINDOW_HEIGHT * scale_factor)

            # Center the game surface on the screen
            fullscreen_offset = (
                (DISPLAY_WIDTH - scaled_width) // 2,
                (DISPLAY_HEIGHT - scaled_height) // 2
            )
        else:
            window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
            scale_factor = 1
            fullscreen_offset = (0, 0)

    running = True
    while running:
        df = clock.tick(FPS) / 1000  # Delta time in seconds
        window.fill(BG_COLOR)
        window.blit(static_surface, (0, 0))  # Display the dotted line

        # Event handling

        # Task alternation logic with focus period
        if task_counter % 2 == 0:
            correct_direction = 'up'
            pygame.draw.polygon(window, WHITE, [(WINDOW_WIDTH // 2, 50), (WINDOW_WIDTH // 2 - ARROW_SIZE // 2, 50 + ARROW_SIZE), (WINDOW_WIDTH // 2 + ARROW_SIZE // 2, 50 + ARROW_SIZE)])
        else:
            correct_direction = 'down'
            pygame.draw.polygon(window, WHITE, [(WINDOW_WIDTH // 2, 50 + ARROW_SIZE), (WINDOW_WIDTH // 2 - ARROW_SIZE // 2, 50), (WINDOW_WIDTH // 2 + ARROW_SIZE // 2, 50)])

        # Focus period
        pygame.display.flip()
        time.sleep(FOCUS_PERIOD)

        # Reset paddle position before starting the movement
        paddle_y = WINDOW_HEIGHT // 2 - PADDLE_HEIGHT // 2

        # Handle predictions through the connection
        while conn.poll():
            conn.recv()  # Clear any old predictions
        model_trained = False
        while not model_trained:
            if conn.poll():
                val = conn.recv()
                if val:
                    model_trained = True
                    break
            time.sleep(0.5)

        # Clear previous predictions
        while conn.poll():
            _ = conn.recv()

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_f:
                        toggle_fullscreen()
            window.fill(BG_COLOR)
            window.blit(static_surface, (0, 0))  # Reapply background and dotted line

            # Draw the paddle
            pygame.draw.rect(window, PADDLE_COLOR, (paddle_x, paddle_y, PADDLE_WIDTH, PADDLE_HEIGHT))

            while conn.poll():
                received = True
                predicted_direction, index = conn.recv()  # Receive predicted direction (1 for left, 0 for right)
                if predicted_direction == 1:
                    direction = -1  # Left means Down
                elif predicted_direction == 0:
                    direction = 1  # Right means Up

            # Move the paddle up or down based on the received direction
            if direction == 1:  # Move Up
                paddle_y -= MOVE_STEP
                if paddle_y <= BORDER_MARGIN:
                    conn.send((predicted_direction, correct_direction, index, True))  # Send completion signal
                    time.sleep(3)  # Delay before the next task
                    while conn.poll():
                        conn.recv()  # Clear remaining data
                    break  # Task ends when the paddle hits the top
            elif direction == -1:  # Move Down
                paddle_y += MOVE_STEP
                if paddle_y + PADDLE_HEIGHT >= WINDOW_HEIGHT:
                    conn.send((predicted_direction, correct_direction, index, True))  # Send completion signal
                    time.sleep(3)  # Delay before the next task
                    while conn.poll():
                        conn.recv()  # Clear remaining data
                    break  # Task ends when the paddle hits the bottom

            # Send the result back through the same connection
            if received:
                received = False
                conn.send((predicted_direction, correct_direction, index, False))

            # Handle fullscreen scaling
            if fullscreen:
                scaled_surface = pygame.transform.scale(window, 
                                                        (int(WINDOW_WIDTH * scale_factor),
                                                         int(WINDOW_HEIGHT * scale_factor)))
                pygame.display.get_surface().blit(scaled_surface, fullscreen_offset)
            else:
                pygame.display.flip()

            clock.tick(FPS)

        time.sleep(TASK_DELAY)  # Add delay between tasks
        task_counter += 1  # Alternate task after each completion

    pygame.quit()

if __name__ == "__main__":
    main()
