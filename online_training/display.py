import pygame
import os
import time
from multiprocessing import Pipe

def draw_arrow(surface, direction, position, color, size):
    x, y = position
    if direction == 'right':
        points = [(x, y), (x - size, y - size // 2), (x - size, y + size // 2)]
    elif direction == 'left':
        points = [(x, y), (x + size, y - size // 2), (x + size, y + size // 2)]
    pygame.draw.polygon(surface, color, points)

def main(conn=None):
    pygame.init()

    # Constants
    WINDOW_WIDTH, WINDOW_HEIGHT = 800, 400
    BAR_HEIGHT = 50
    BAR_COLOR = (0, 128, 255)
    RED_COLOR = (255, 0, 0)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    FPS = 60
    MOVE_STEP = 1  # Reduced speed for slower bar movement
    BORDER_MARGIN = 20  # Space between red bars and screen border
    TASK_DELAY = 1  # Delay in seconds between tasks
    FOCUS_PERIOD = 2  # Focus period before the task starts
    ARROW_SIZE = 40  # Size of the arrow
    PASS_THROUGH = 10  # How far the bar should pass through the red bar

    # Create the display window
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("EEG Motor Imagery")

    # Initial positions
    bar_width = 0
    direction = 0  # 0: No movement, 1: Right, -1: Left

    # Define the red boundaries
    red_bar_width = 50
    left_red_bar_x = BORDER_MARGIN
    right_red_bar_x = WINDOW_WIDTH - red_bar_width - BORDER_MARGIN

    # Clock
    clock = pygame.time.Clock()
    task_counter = 0  # Counter to alternate tasks
    received = False
    bar_position = WINDOW_WIDTH // 2

    running = True
    while running:
        window.fill(WHITE)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Task alternation logic with focus period
        if task_counter % 2 == 0:
            correct_direction = 'right'
            bar_position = WINDOW_WIDTH // 2  # Start from the middle
            draw_arrow(window, 'right', (WINDOW_WIDTH // 2, 50), BLACK, ARROW_SIZE)
        else:
            correct_direction = 'left'
            bar_position = WINDOW_WIDTH // 2  # Start from the middle
            draw_arrow(window, 'left', (WINDOW_WIDTH // 2, 50), BLACK, ARROW_SIZE)

        # Focus period
        pygame.display.flip()
        time.sleep(FOCUS_PERIOD)

        bar_width = 0  # Reset the bar width before moving

        # Handle predictions through the connection
        while conn.poll():
            conn.recv()
        model_trained = False
        while not model_trained:
            if conn.poll():
                val = conn.recv()
                if val:
                    model_trained = True
                    break
            time.sleep(0.5)
        time.sleep(0.2) # small time to allow a new prediction to be sent
        while conn.poll():
            print("cleared pred")
            _ = conn.recv()

        print("cleared conn")
        while running:
            window.fill(WHITE)

            # Draw the red boundaries (always visible)
            pygame.draw.rect(window, RED_COLOR, (left_red_bar_x, (WINDOW_HEIGHT - BAR_HEIGHT) // 2, red_bar_width, BAR_HEIGHT))
            pygame.draw.rect(window, RED_COLOR, (right_red_bar_x, (WINDOW_HEIGHT - BAR_HEIGHT) // 2, red_bar_width, BAR_HEIGHT))

            while conn.poll():
                received = True
                predicted_direction, index = conn.recv()  # Receive predicted direction (1 for left, 0 for right)
                if predicted_direction == 1:
                    direction = -1
                elif predicted_direction == 0:
                    direction = 1

            # Continuously move the bar in the current direction
            if direction == 1:
                bar_position += MOVE_STEP
                if bar_position >= right_red_bar_x + PASS_THROUGH:
                    conn.send((predicted_direction, correct_direction, index, True))
                    time.sleep(3)
                    while conn.poll():
                        conn.recv()
                    break  # Stop when reaching the right boundary
            elif direction == -1:
                bar_position -= MOVE_STEP
                if bar_position <= left_red_bar_x - PASS_THROUGH:
                    conn.send((predicted_direction, correct_direction, index, True))
                    time.sleep(3)
                    while conn.poll():
                        conn.recv()
                    break  # Stop when reaching the left boundary

            pygame.draw.rect(window, BAR_COLOR, (bar_position, (WINDOW_HEIGHT - BAR_HEIGHT) // 2, 10, BAR_HEIGHT))

            # Check if the prediction is correct
            if (direction == 1 and correct_direction == 'right') or (direction == -1 and correct_direction == 'left'):
                result = "Correct"
            else:
                result = "Incorrect"
            # Send the result back through the same connection
            if received:
                received = False
                conn.send((predicted_direction, correct_direction, index, False))


            pygame.display.flip()
            clock.tick(24)

        time.sleep(TASK_DELAY)  # Add delay between tasks
        task_counter += 1  # Alternate task after each boundary hit
    print("Ending")
    pygame.quit()

if __name__ == "__main__":
    main()
