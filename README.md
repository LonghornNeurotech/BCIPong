BCI Pong Game Documentation

Table of Contents

* [Introduction](#introduction)
* [Features](#features)
* [Prerequisites](#prerequisites)
* [Installation](#installation)
* [Running the Game](#running-the-game)
* [Game Modes](#game-modes)
* [Play Game (Human vs AI)](#play-game-human-vs-ai)
* [Fine-tune Model (Practice Mode)](#fine-tune-model-practice-mode)
* [Controls](#controls)
* [Fine-tuning the Model](#fine-tuning-the-model)
* [Overview](#overview)
* [Process](#process)
* [Project Structure](#project-structure)
* [License](#license)

### Introduction

BCI Pong Game is a Brain-Computer Interface (BCI) application that allows users to play the classic Pong game using neural signals. The game integrates real-time EEG data streaming, machine learning for prediction, and an interactive Pygame interface.

This application is designed to:
*	Provide a platform for BCI controlled pong.
*	Provide users ability to fine-tune their ML model for the Pong environment.
*	Provide a framework for data collection.

### Features

*   Real-time EEG Data Streaming: Uses BrainFlow to stream EEG data.
*   Machine Learning Predictions: Implements a neural network for classifying EEG signals into commands in the pong game.
*   Interactive Gameplay: Play Pong against another opponent using keyboard based controls.
*   Practice Mode: Fine-tune the machine learning model to be used in the Pong environment.

### Prerequisites

Before running the game, ensure you have the following installed:
*   Python 3.7 or higher
*   Pip (Python package manager)

### Python Packages

The game requires several Python packages:
*   pygame
*   brainflow
*   torch (PyTorch)
*   numpy
*   scipy

You can install these packages using the requirements.txt file provided.

Installation

1.	Clone the Repository

```bash 
git clone https://github.com/yourusername/BCI-Pong-Game.git
cd BCI-Pong-Game
```

2.	Create a Conda environment

```bash 
conda create -n BCIPong python=3.9
conda activate BCIPong
```

3.	Install Dependencies

```bash 
pip install -r requirements.txt
```

4. Running the Game

Start the game by running the run.py script:

```bash 
python run.py
```

Note: The game uses a synthetic board by default (bf.BoardIds.SYNTHETIC_BOARD.value). If you have a real EEG device, adjust the board_id and serial_port accordingly in run.py. CURRENTLY, THIS GAME IS ONLY SET UP FOR OPENBCI HARDWARE. Contributions are welcome for compatability with other devices.


## Game Modes

Upon launching the game, you’ll be presented with a main menu with three options:
	1.	Play Game
	2.	Fine-tune Model
	3.	Exit

You can navigate the menu using the UP/DOWN arrow keys or by hovering and clicking with the mouse.

### Play Game

*   Objective: Play Pong against another opponent using EEG-based controls.
*   Controls: Use your neural signals to move the paddle up or down.

### Fine-tune Model (Practice Mode)

*   Objective: Improve the machine learning model in the BCIPong environment.
*   Process: Imagine squeezing left or right hand (without moving) to move the paddle in the direction indicated by on-screen prompts.
*   It is recommended to fine tune the model each time before playing due to intra-subject variability. If you would like to learn more about Intra-Subject Variability we recommend reading this [paper](https://www.frontiersin.org/journals/computational-neuroscience/articles/10.3389/fncom.2019.00087/full).

### Controls

*   Toggle Fullscreen: Press F to toggle fullscreen mode.
*   Pause/Resume: Press P to pause or resume the game.
*   Exit to Main Menu: Press ESC during gameplay to return to the main menu.
*   Start Practice Mode: In the main menu, select Fine-tune Model.

## Fine-tuning the Model

### Overview

The fine-tuning process allows the machine learning model to adapt to your specific neural signals, improving the accuracy of in-game controls.

### Process
1.	Focus Period:
    *   A + sign appears on the screen. Maintain focus on the +.
2.	Direction Prompt:
    *   An arrow (up or down) appears, imagine squeezing left or right hand (without actually moving)
3.	Trial Phase:
    *   continue imagining squeezing left or right hand
    *   The paddle will start moving based on the model’s predictions.
4.	Rest Phase:
    *   Rest phase of random duration
5.	Feedback Loop:
    *   The model receives feedback on its predictions and adjusts accordingly.


## Project Structure

BCI-Pong-Game/
├── assets/
│   └── Picture2.png          # Background image
├── data_streaming/
│   ├── __init__.py
│   └── stream.py             # Data streaming logic
├── game/
│   ├── __init__.py
│   ├── config.py             # Game configuration constants
│   ├── entities.py           # Game entities (Paddle, Ball)
│   ├── input_handler.py      # Input handling logic
│   ├── main.py               # Main game script
│   ├── practice_mode.py      # Practice mode logic
│   ├── render.py             # Rendering functions
│   └── utils.py              # Utility functions
├── model/
│   ├── CapsNet.py            # EEGNet model definition
│   ├── generate_weights.py   # generate weights if not already downloaded
│   ├── load_model.py         # load model weights
│   └── utils.py              # include utilities for CapsNet
├── online_training/
│   ├── loss.py               # includes loss functions for training
│   ├── store_data.py         # store data
│   └── train.py              # train model
├── utils.py
├── streamer.py               # Streaming predictions and model updates
├── run.py                    # Script to start the game
└── requirements.txt          # Python dependencies


### License

This project is licensed under the MIT License.


### Machine Learning Model

The game uses an EEGNet-based neural network for processing EEG data and making predictions. The model is defined in models/CapsNet.py.

### Training and Prediction

*   Training: During the practice mode, the model is finetuned based on user performance in the Pong environment
*   Prediction: In the play mode, the model predicts the intended paddle movement based on incoming EEG data.

### Data Handling

*   Data Collection: EEG data is streamed and stored temporarily for processing.
*   Data Preprocessing: Data is filtered and transformed before being fed into the model.
*   Feedback Loop: The model uses the feedback from practice sessions to improve its accuracy.

### Contact

For questions or support, please contact:
*   Email: n.feldt@utexas.edu

### Contributions are welcome!

