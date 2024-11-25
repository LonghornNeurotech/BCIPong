# render.py

import pygame
from game.utils import draw_dotted_line
from game.config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, WHITE, FONT, COUNTDOWN_FONT,
    WINNING_SCORE, INSTRUCTIONS_FONT, PHYSICS_FPS
)

def draw_static_elements(bg_image):
    """
    Draws static elements like the center dotted line.

    Returns:
        Surface with static elements drawn.
    """
    static_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    draw_dotted_line(static_surface, WHITE, (WINDOW_WIDTH // 2, 0), (WINDOW_WIDTH // 2, WINDOW_HEIGHT), width=3, dash_length=20)
    bg_with_static = bg_image.copy()
    bg_with_static.blit(static_surface, (0, 0))
    return bg_with_static

def draw_game(
    window, bg_with_static, paddles, ball, score, display_instructions,
    game_state, countdown_timer, ball_surface, interpolation
):
    """
    Draws the main game screen.

    Args:
        window: The game window surface.
        bg_with_static: Background surface with static elements.
        paddles: Tuple of paddle objects.
        ball: Ball object.
        score: Tuple containing player scores.
        display_instructions: Boolean to display instructions.
        game_state: Current game state.
        countdown_timer: Timer for the countdown.
        ball_surface: Surface of the ball.
        interpolation: Interpolation value for smooth movement.
    """
    window.blit(bg_with_static, (0, 0))

    # Draw paddles
    for paddle in paddles:
        paddle.draw(window, WHITE)

    # Draw ball with interpolation
    interpolated_x = ball.x + ball.vx * interpolation / PHYSICS_FPS
    interpolated_y = ball.y + ball.vy * interpolation / PHYSICS_FPS
    window.blit(ball_surface, (int(interpolated_x), int(interpolated_y)))

    # Draw score
    score_surface = FONT.render(f"{score[0]}   {score[1]}", True, WHITE)
    window.blit(score_surface, (WINDOW_WIDTH // 2 - score_surface.get_width() // 2, 35))

    # Draw instructions
    if display_instructions:
        instruction_left = INSTRUCTIONS_FONT.render("Move: W/S, Height: Q/A", True, WHITE)
        instruction_right = INSTRUCTIONS_FONT.render("Move: Up/Down, Height: P/L", True, WHITE)
        window.blit(instruction_left, ((WINDOW_WIDTH // 2) - 30 - instruction_left.get_width(), WINDOW_HEIGHT - 40))
        window.blit(instruction_right, ((WINDOW_WIDTH // 2) + 30, WINDOW_HEIGHT - 40))

    # Draw countdown
    if game_state == "COUNTDOWN":
        seconds_left = countdown_timer // 1000 + 1
        countdown_text = COUNTDOWN_FONT.render(str(int(seconds_left)), True, WHITE)
        window.blit(countdown_text, (WINDOW_WIDTH // 2 - countdown_text.get_width() // 2, WINDOW_HEIGHT // 4 - countdown_text.get_height() // 2))

def draw_menu(window, bg_with_static, menu_font, menu_options):
    """
    Draws the main menu screen.

    Args:
        window: The game window surface.
        bg_with_static: Background surface with static elements.
    """
    window.blit(bg_with_static, (0, 0))
    menu_option_rects = []
    for idx, option in enumerate(menu_options):
        color = WHITE
        option_text = menu_font.render(option, True, color)
        text_rect = option_text.get_rect()
        # Position the text
        text_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + idx * 50)
        window.blit(option_text, text_rect)
        menu_option_rects.append(text_rect)
    return menu_option_rects

def draw_game_over_screen(window, bg_with_static, score):
    """
    Draws the game over screen.

    Args:
        window: The game window surface.
        bg_with_static: Background surface with static elements.
        score: Tuple containing player scores.
    """
    window.blit(bg_with_static, (0, 0))
    winner = "Player 1" if score[0] >= WINNING_SCORE else "Player 2"
    winner_text = FONT.render(f"{winner} Wins!", True, WHITE)
    restart_text = FONT.render("Press Space to Restart", True, WHITE)
    menu_text = FONT.render("Press M for Menu", True, WHITE)
    window.blit(winner_text, (WINDOW_WIDTH // 2 - winner_text.get_width() // 2, WINDOW_HEIGHT // 3))
    window.blit(restart_text, (WINDOW_WIDTH // 2 - restart_text.get_width() // 2, WINDOW_HEIGHT // 2 + 50))
    window.blit(menu_text, (WINDOW_WIDTH // 2 - menu_text.get_width() // 2, WINDOW_HEIGHT // 2 + 100))