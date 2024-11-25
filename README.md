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
* [Troubleshooting](#troubleshooting)
* [Contributing](#contributing)
* [License](#license)

### Introduction

BCI Pong Game is a Brain-Computer Interface (BCI) application that allows users to play the classic Pong game using neural signals. The game integrates real-time EEG data streaming, machine learning for prediction, and an interactive Pygame interface.

This application is designed to:
    *	Provide an interactive platform for BCI experiments.
    *	Allow users to fine-tune the machine learning model for better accuracy.
    *	Demonstrate real-time data streaming and processing.

### Features

	•	Real-time EEG Data Streaming: Uses BrainFlow to stream synthetic or real EEG data.
	•	Machine Learning Predictions: Implements a neural network for classifying EEG signals into commands.
	•	Interactive Gameplay: Play Pong against an AI opponent using EEG-based controls.
	•	Practice Mode: Fine-tune the machine learning model by participating in guided training sessions.
	•	Customizable Settings: Adjust game settings and configurations as needed.

### Prerequisites

Before running the game, ensure you have the following installed:
	•	Python 3.7 or higher
	•	Pip (Python package manager)

### Python Packages

The game requires several Python packages:
	•	pygame
	•	brainflow
	•	torch (PyTorch)
	•	numpy
	•	scipy

You can install these packages using the requirements.txt file provided.

Installation

	1.	Clone the Repository

```bash git clone https://github.com/yourusername/BCI-Pong-Game.git
cd BCI-Pong-Game```


	2.	Create a Virtual Environment (Optional but Recommended)

```bash python -m venv venv
source venv/bin/activate  # On Windows, use venv\Scripts\activate```


	3.	Install Dependencies

```bash pip install -r requirements.txt```

Running the Game

Start the game by running the run.py script:

```bash python run.py```

Note: The game uses a synthetic board by default (bf.BoardIds.SYNTHETIC_BOARD.value). If you have a real EEG device, adjust the board_id and serial_port accordingly in run.py. CURRENTLY, THIS GAME IS ONLY SET UP FOR OPENBCI HARDWARE.


## Game Modes

Upon launching the game, you’ll be presented with a main menu with three options:
	1.	Play Game
	2.	Fine-tune Model
	3.	Exit

You can navigate the menu using the UP/DOWN arrow keys or by hovering and clicking with the mouse.

### Play Game

	•	Objective: Play Pong against another opponent using EEG-based controls.
	•	Controls: Use your neural signals to move the paddle up or down.

### Fine-tune Model (Practice Mode)

	•	Objective: Improve the machine learning model by participating in training sessions.
	•	Process:
	•	Focus on moving the paddle in the direction indicated by on-screen prompts.
	•	The model learns from your neural patterns to improve prediction accuracy.

### Controls

	•	Toggle Fullscreen: Press F to toggle fullscreen mode.
	•	Pause/Resume: Press P to pause or resume the game.
	•	Exit to Main Menu: Press ESC during gameplay to return to the main menu.
	•	Start Practice Mode: In the main menu, select Fine-tune Model.

## Fine-tuning the Model

### Overview

The fine-tuning process allows the machine learning model to adapt to your specific neural signals, improving the accuracy of in-game controls.

### Process

	1.	Focus Period:
	    •	A + sign appears on the screen. Maintain focus on the +.
	2.	Direction Prompt:
	    •	An arrow (up or down) appears, imagine squeezing left or right hand (without actually moving)
	3.	Trial Phase:
	    •	continue imagining squeezing left or right hand
	    •	The paddle will start moving based on the model’s predictions.
	4.	Rest Phase:
	    •	Rest phase of random duration
	5.	Feedback Loop:
	    •	The model receives feedback on its predictions and adjusts accordingly.


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

	•	Training: During the practice mode, the model is finetuned based on user performance in the Pong environment
	•	Prediction: In the play mode, the model predicts the intended paddle movement based on incoming EEG data.

### Data Handling

	•	Data Collection: EEG data is streamed and stored temporarily for processing.
	•	Data Preprocessing: Data is filtered and transformed before being fed into the model.
	•	Feedback Loop: The model uses the feedback from practice sessions to improve its accuracy.

### Contact

For questions or support, please contact:
	•	Email: n.feldt@utexas.edu

### Contributions are welcome

