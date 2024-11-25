## Game Modes

Upon launching the game, you’ll be presented with a main menu with three options:
	1.	Play Game
	2.	Fine-tune Model
	3.	Exit

You can navigate the menu using the UP/DOWN arrow keys or by hovering and clicking with the mouse.

### Play Game

*   Objective: Play Pong against another opponent using EEG-based controls.
*   Controls: Use your neural signals to move the paddle up or down.

### Fine-tune Model (Online Training)

*   Objective: Improve the machine learning model in the BCIPong environment.
*   Process: Imagine squeezing left or right hand (without moving) to move the paddle in the direction indicated by on-screen prompts.
*   The goal of this process is to repeat the procedure completed during data collection but allow the user to have immediate feedback of their motor imagery performance.
*   This approach allows the model to learn from neural signals in the pong environment (as opposed to data collection environment).
*   This process also allows the user to get familiar to mapping the right hand imagery to up and left hand imagery to down.
*   It is recommended to fine tune the model each time before playing due to intra-subject variability. If you would like to learn more about Intra-Subject Variability we recommend reading this [paper](https://www.frontiersin.org/journals/computational-neuroscience/articles/10.3389/fncom.2019.00087/full).

### Controls

*   Toggle Fullscreen: Press F to toggle fullscreen mode.
*   Pause/Resume: Press P to pause or resume the game.
*   ↑/↓: Control opponent paddle (non-bci controlled)
*   Exit to Main Menu: Press ESC during gameplay to return to the main menu.
*   Start Practice Mode: In the main menu, select Fine-tune Model.

## Fine-tuning the Model

### Overview

The fine-tuning process allows the machine learning model to adapt to your specific neural signals, improving the accuracy of in-game controls. This process is similar to data collection but instead the user has to control up and down motion with right and left motor imagery.

### Process
1.	Focus Period:
    *   A + sign appears on the screen. Maintain focus on the +.
2.	Direction Prompt:
    *   An arrow (up or down) appears, imagine squeezing right or left hand (without actually moving)
    *   Imagining squeezing right hand makes the paddle go up
    *   Imagining squeezing left hand makes the paddle go down
3.	Trial Phase:
    *   continue imagining squeezing left or right hand
    *   The paddle will start moving based on the model’s predictions.
4.	Rest Phase:
    *   Rest phase of random duration
5.	Feedback Loop:
    *   The model receives feedback on its predictions and adjusts accordingly.

