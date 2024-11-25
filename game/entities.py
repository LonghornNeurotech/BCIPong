# /game/entities.py

import pygame
from game.config import PADDLE_WIDTH, PADDLE_MIN_HEIGHT, PADDLE_MAX_HEIGHT, WINDOW_HEIGHT

class Paddle:
    """
    Represents a paddle in the game.
    """
    def __init__(self, x, initial_y, height, velocity):
        self.x = x
        self.y = initial_y
        self.height = height
        self.velocity = velocity
        self.movement = 0  # Current movement direction

    def move(self, dt):
        """
        Updates the paddle position based on its movement and velocity.
        """
        self.y += self.movement * self.velocity * dt
        self.y = max(self.height / 2, min(self.y, WINDOW_HEIGHT - self.height / 2))

    def resize(self, amount):
        """
        Adjusts the paddle height within min and max limits.
        """
        self.height = max(PADDLE_MIN_HEIGHT, min(self.height + amount, PADDLE_MAX_HEIGHT))

    def draw(self, surface, color):
        """
        Draws the paddle on the given surface.
        """
        rect = pygame.Rect(
            self.x,
            self.y - self.height / 2,
            PADDLE_WIDTH,
            self.height
        )
        pygame.draw.rect(surface, color, rect)

class Ball:
    """
    Represents the ball in the game.
    """
    def __init__(self, x, y, diameter, velocity):
        self.x = x
        self.y = y
        self.diameter = diameter
        self.velocity = velocity
        self.vx = velocity
        self.vy = velocity

    def move(self, dt):
        """
        Updates the ball position based on its velocity.
        """
        self.x += self.vx * dt
        self.y += self.vy * dt

    def draw(self, surface, ball_surface):
        """
        Draws the ball on the given surface.
        """
        surface.blit(ball_surface, (int(self.x), int(self.y)))