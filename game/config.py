# /game/config.py

import pygame

# Screen settings
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 625
FPS = 60
PHYSICS_FPS = 240

# Paddle settings
PADDLE_WIDTH = 15
PADDLE_MIN_HEIGHT = 30
PADDLE_MAX_HEIGHT = 250
PADDLE_INITIAL_HEIGHT = 125
PLAYER_1_VEL = 200
PLAYER_2_VEL = 1500

# Ball settings
BALL_DIAMETER = 25
BALL_VEL = 250

# Game settings
WINNING_SCORE = 5
COUNTDOWN_SECONDS = 5

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BG_COLOR = (191, 87, 32)
BALL_INNER_COLOR = (255, 255, 255)
BALL_OUTER_COLOR = (150, 150, 150)

# Fonts
pygame.font.init()
FONT = pygame.font.SysFont("Monaco", 28, bold=True)
COUNTDOWN_FONT = pygame.font.SysFont("Monaco", 72, bold=True)
INSTRUCTIONS_FONT = pygame.font.SysFont("Monaco", 16, bold=True)