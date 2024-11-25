# BCI Pong Game Documentation

### Table of Contents

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
*	Provide a framework for data collection. (Please see [Data Collection Documentation](data_collection/dataREADME.md))

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

### Installation

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

### General Instructions

1. Acquire an EEG Headset

*   This project was tested with the OpenBCI Cyton-Daisy 16 channel EEG headset.
*   Other headsets from g.tec, Emotiv, etc, can be adapted to be used in this project

2. Data Collection

*   In order to train the machine learning data must be collected. 
*   We provide a comprehensive description on this process in [Data Collection Documentation](data_collection/dataREADME.md)

3. Model training

*   Train the machine learning model with the data collected.
*   We provide documentation in [Machine Learning Model Documentation](model/modelREADME.md)

4. Fine-Tune

*   Due to intra-subject variability we recommend fine-tuning each time before playing
*   We provide documentation in [Pong Game Documentation](game/gameREADME.md)

5. Play

*   We provide documentation in [Pong Game Documentation](game/gameREADME.md)

Note: The game uses a synthetic board by default (bf.BoardIds.SYNTHETIC_BOARD.value). If you have a real EEG device, adjust the board_id and serial_port accordingly in run.py. CURRENTLY, THIS GAME IS ONLY SET UP FOR OPENBCI HARDWARE. Contributions are welcome for compatability with other devices.


## Project Structure
```
├── README.md
├── __init__.py
├── assets
│   └── Picture2.png
├── data
├── data_collection
│   ├── __init__.py
│   └── dataREADME.md
├── data_streaming
│   ├── __init__.py
│   └── stream.py
├── game
│   ├── __init__.py
│   ├── bci_input.py
│   ├── config.py
│   ├── entities.py
│   ├── gameREADME.md
│   ├── input_handler.py
│   ├── main.py
│   ├── pong_practice.py
│   ├── render.py
│   └── utils.py
├── model
│   ├── CapsNet.py
│   ├── __init__.py
│   ├── generate_weights.py
│   ├── load_model.py
│   ├── modelREADME.md
│   └── utils.py
├── online_training
│   ├── loss.py
│   ├── store_data.py
│   └── train.py
├── preprocessing
│   ├── __init__.py
│   ├── preprocess.py
│   └── preprocessingREADME.md
├── run.py
├── streamer.py
├── tree.md
├── utils.py
└── weights
```

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

