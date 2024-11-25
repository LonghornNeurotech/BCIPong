# /game/utils.py

import pygame
import math

def draw_dotted_line(surface, color, start_pos, end_pos, width=1, dash_length=10):
    """
    Draws a dotted line between start_pos and end_pos on the given surface.
    """
    x1, y1 = start_pos
    x2, y2 = end_pos
    dl = dash_length

    if x1 == x2:
        y_coords = list(range(y1, y2, dl if y1 < y2 else -dl))
        if len(y_coords) % 2:
            y_coords.append(y2)
        for i in range(0, len(y_coords), 2):
            pygame.draw.line(surface, color, (x1, y_coords[i]), (x1, y_coords[i+1]), width)
    else:
        x_coords = list(range(x1, x2, dl if x1 < x2 else -dl))
        if len(x_coords) % 2:
            x_coords.append(x2)
        for i in range(0, len(x_coords), 2):
            pygame.draw.line(surface, color, (x_coords[i], y1), (x_coords[i+1], y1), width)

def create_gradient_ball(diameter, inner_color, outer_color):
    """
    Creates a ball surface with a radial gradient.
    """
    surface = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
    center = diameter // 2
    for x in range(diameter):
        for y in range(diameter):
            distance = math.hypot(x - center, y - center)
            if distance <= center:
                ratio = distance / center
                color = [
                    inner_color[i] * (1 - ratio) + outer_color[i] * ratio
                    for i in range(3)
                ]
                surface.set_at((x, y), (*color, 255))
    return surface

def print_distance_from_ball(ball_pos, ball_size, paddle_pos, extra_message=""):
    """
    Prints the distance between the ball and paddle center.
    """
    ball_center_y = ball_pos[1] + ball_size / 2
    distance = ball_center_y - paddle_pos
    print(f"{extra_message}Ball was {abs(distance):.2f} pixels away from the paddle's center.\033[0m")