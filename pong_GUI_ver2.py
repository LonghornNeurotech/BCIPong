# imports
import tkinter
import time
import random
import sys
from copy import copy
from PIL import Image,ImageTk

# create game window
window = tkinter.Tk()

# create window size and set no-resize option
window_dimensions = [1200, 625]
window.geometry(str(window_dimensions[0]) + "x" + str(window_dimensions[1]))
window.resizable(0, 0)

# set window title
window.title("BCI Pong Game")

# close window when OS close button is clicked
window.protocol("WM_DELETE_WINDOW", sys.exit)

# choose fps for game
frames_per_second = 60

# create game canvas
game_canvas = tkinter.Canvas(window, width=window_dimensions[0], height=window_dimensions[1], bd=0, highlightthickness=0)
game_canvas.pack()

# create game variables

# paddle sizes
paddle_size = [15, 125]

# initial centered Y position for both paddles
initial_y_position = (window_dimensions[1] - paddle_size[1]) / 2

# player variables
player_y_position = initial_y_position
player_y_velocity = 0

# player2 variables
player2_y_position = initial_y_position
player2_y_velocity = 0

# ball variables
ball_diameter = 15

initial_ball_position = [(window_dimensions[0] - 35 - paddle_size[0]) - (int(window_dimensions[1] / 2)), ((window_dimensions[1] - ball_diameter) / 2) - (int(window_dimensions[1] / 2))]
initial_ball_velocity = [12, 12]

ball_position = copy(initial_ball_position)
ball_velocity = copy(initial_ball_velocity)

# score variable and widget
score = [0, 0]

# 승리 모드 변수
game_over = False
winning_score = 5

# delete useless global variables
del initial_y_position

# display instructions variable
display_instructions = True

# game restart function
def restart_game(e):
    global score, ball_position, ball_velocity, game_over
    score = [0, 0]
    ball_position = copy(initial_ball_position)
    ball_velocity = copy(initial_ball_velocity)
    game_over = False
    gameloop()

root='C:/Users/tonys/Desktop/UT Club/Longhorn_Neurotech/BCI Pong GUI/Picture2.png'

background_image = Image.open(root)  # image file path for longhorn
background_image = background_image.resize((window_dimensions[0], window_dimensions[1]))  # resize for window size
background_photo = ImageTk.PhotoImage(background_image)

# gameloop
def gameloop():
    global frames_per_second
    global game_canvas
    global window_dimensions
    global player_y_position
    global paddle_size
    global player2_y_position
    global ball_diameter
    global ball_position
    global ball_velocity
    global player_y_velocity
    global player2_y_velocity
    global display_instructions
    global score
    global game_over

    if game_over:
        return

    window.after(int(1000 / frames_per_second), gameloop)

    game_canvas.delete("all")
    game_canvas.create_image(0, 0, anchor="nw", image=background_photo)
    
    # game_canvas.create_rectangle(0, 0, window_dimensions[0], window_dimensions[1], fill="#BF5720", outline="#222222") 

    game_canvas.create_rectangle(35, player_y_position, 35 + paddle_size[0], player_y_position + paddle_size[1], fill="#ffffff", outline="#ffffff")

    game_canvas.create_rectangle(window_dimensions[0] - 35, player2_y_position, (window_dimensions[0] - 35) - paddle_size[0], player2_y_position + paddle_size[1], fill="#ffffff", outline="#ffffff")

    game_canvas.create_rectangle(ball_position[0], ball_position[1], ball_position[0] + ball_diameter, ball_position[1] + ball_diameter, fill="black", outline="black")

    game_canvas.create_text(window_dimensions[0] / 2, 35, anchor="center", font="Monaco 28 bold", fill="#ffffff", text=str(score[0]) + "   " + str(score[1]))

    game_canvas.create_line((window_dimensions[0] / 2) , 0, (window_dimensions[0] / 2), window_dimensions[1], fill="#ffffff", dash=(6, 10), width=3)

    if(display_instructions):
        game_canvas.create_text((window_dimensions[0] / 2) - 30, window_dimensions[1] - 40, anchor="ne", font="Monaco 16 bold", fill="#ffffff", text="Move w/WASD")
        game_canvas.create_text((window_dimensions[0] / 2) + 30, window_dimensions[1] - 40, anchor="nw", font="Monaco 16 bold", fill="#ffffff", text="Move w/Arrows")

    player_y_position += player_y_velocity
    player2_y_position += player2_y_velocity
    
    if(player_y_position + paddle_size[1] > window_dimensions[1]):
        player_y_position = window_dimensions[1] - paddle_size[1]
    elif(player_y_position < 0):
        player_y_position = 0

    if(player2_y_position + paddle_size[1] > window_dimensions[1]):
        player2_y_position = window_dimensions[1] - paddle_size[1]
    elif(player2_y_position < 0):
        player2_y_position = 0

    ball_position[0] += ball_velocity[0]
    ball_position[1] += ball_velocity[1]

    if(ball_position[1] >= window_dimensions[1] - ball_diameter or ball_position[1] <= 0):
        ball_velocity[1] = -ball_velocity[1]

    if(ball_position[0] <= 0):
        score[1] += 1
        ball_position = copy(initial_ball_position)
        ball_velocity = copy(initial_ball_velocity)

    if(ball_position[0] >= window_dimensions[0] - ball_diameter):
        score[0] += 1
        ball_position = copy(initial_ball_position)
        ball_velocity = copy(initial_ball_velocity)

    if(((ball_position[0] >= 35 and ball_position[0] <= 35 + paddle_size[0]) and (ball_position[1] + ball_diameter >= player_y_position and ball_position[1] <= player_y_position + paddle_size[1])) or ((ball_position[0] + ball_diameter <= window_dimensions[0] - 35 and ball_position[0] + ball_diameter >= (window_dimensions[0] - 35) - paddle_size[0]) and (ball_position[1] + ball_diameter >= player2_y_position and ball_position[1] <= player2_y_position + paddle_size[1]))):
        ball_velocity[0] = -ball_velocity[0]

        if(ball_velocity[0] >= 0):
            if((ball_position[1] + ball_diameter <= player_y_position + paddle_size[0] and ball_velocity[1] >= 0) or (ball_position[1] >= player_y_position + paddle_size[1] - paddle_size[0] and ball_velocity[1] <= 0)):
                ball_velocity[1] = -ball_velocity[1]

        if(ball_velocity[0] <= 0):
            if((ball_position[1] + ball_diameter <= player2_y_position + paddle_size[0] and ball_velocity[1] >= 0) or (ball_position[1] >= player2_y_position + paddle_size[1] - paddle_size[0] and ball_velocity[1] <= 0)):
                ball_velocity[1] = -ball_velocity[1]

    # check for who wins (final winner)
    if score[0] >= winning_score or score[1] >= winning_score:
        game_over = True
        winner = "Player 1" if score[0] >= winning_score else "Player 2"
        game_canvas.create_text(window_dimensions[0] / 2, window_dimensions[1] / 2, anchor="center", font="Monaco 36 bold", fill="#ffffff", text=winner + " Wins!")
        game_canvas.create_text(window_dimensions[0] / 2, window_dimensions[1] / 2 + 50, anchor="center", font="Monaco 20 bold", fill="#ffffff", text="Press Space to Restart")
        window.bind("<space>", restart_game)

# handle arrow keys keydown events
def onKeyDown(e):
    global player_y_velocity
    global player2_y_velocity
    global display_instructions

    player_y_velocity_current = player_y_velocity
    player2_y_velocity_current = player2_y_velocity

    if(e.keysym == "w"):
        player_y_velocity = -15
    elif(e.keysym == "s"):
        player_y_velocity = 15

    if(e.keysym == "Up"):
        player2_y_velocity = -15
    elif(e.keysym == "Down"):
        player2_y_velocity = 15
    
    if(player_y_velocity_current != player_y_velocity or player2_y_velocity_current != player2_y_velocity):
        display_instructions = False

# handle arrow keys keyup events
def onKeyUp(e):
    global player_y_velocity
    global player2_y_velocity

    if(e.keysym == "w" or e.keysym == "s"):
        player_y_velocity = 0

    if(e.keysym == "Up" or e.keysym == "Down"):
        player2_y_velocity = 0

window.bind("<KeyPress>", onKeyDown)
window.bind("<KeyRelease>", onKeyUp)

gameloop()

window.mainloop()
