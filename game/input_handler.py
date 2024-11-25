# /game/input_handler.py

import pygame
from game.config import PLAYER_1_VEL, PLAYER_2_VEL

def handle_input(event, game_state, paddles, game_actions):
    """
    Handles input events.

    Args:
        event: The pygame event.
        game_state: The current state of the game.
        paddles: A tuple of paddle objects (player1, player2).
        game_actions: A dictionary to communicate actions (e.g., restart, menu).
    """
    player1, player2 = paddles

    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            pygame.quit()
            exit()

        elif event.key == pygame.K_f:
            game_actions['toggle_fullscreen'] = True

        elif game_state == "MENU":
            if event.key == pygame.K_1:
                game_actions['start_game'] = "HUMAN_VS_HUMAN"
            elif event.key == pygame.K_2:
                game_actions['start_game'] = "HUMAN_VS_AI"

        elif game_state == "PLAYING":
            if event.key == pygame.K_w:
                player1.movement = -1
            elif event.key == pygame.K_s:
                player1.movement = 1
            elif event.key == pygame.K_UP:
                player2.movement = -1
            elif event.key == pygame.K_DOWN:
                player2.movement = 1
            elif event.key == pygame.K_q:
                player1.resize(10)
            elif event.key == pygame.K_a:
                player1.resize(-10)
            elif event.key == pygame.K_p:
                player2.resize(10)
            elif event.key == pygame.K_l:
                player2.resize(-10)

        elif game_state == "GAME_OVER":
            if event.key == pygame.K_SPACE:
                game_actions['restart'] = True
            elif event.key == pygame.K_m:
                game_actions['menu'] = True

    elif event.type == pygame.KEYUP:
        if event.key in (pygame.K_w, pygame.K_s):
            player1.movement = 0
        if event.key in (pygame.K_UP, pygame.K_DOWN):
            player2.movement = 0