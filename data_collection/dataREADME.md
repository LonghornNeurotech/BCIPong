# EEG Motor Imagery Data Collection

This README provides a comprehensive guide to our implemenation of EEG Motor Imagery Data Collection. It includes detailed explanations of the code and detailed procedure description of the data collection procedure. The application is designed to collect EEG data while subjects perform motor imagery tasks, specifically imagining squeezing their left or right hand based on arrow directions displayed on the screen.

## Table of Contents

* [Introduction](#introduction)
* [Prerequisites](#prerequisites)
* [Usage](#usage)
* [Code Overview](#code-overview)
* [Data Collection Procedure](#data-collection-procedure)
* [Best Practices for Data Collection](#best-practices-for-data-collection)
* [Contact Information](#contact-information)

### Introduction

The EEG Motor Imagery Data Collection Tool is a Python-based application that allows the collection of EEG data for motor imagery tasks. The application guides the subject through a series of trials where they are instructed to imagine squeezing their left or right hand, prompted by arrow directions on the screen. The collected data can be used for training machine learning models for EEG signal classification.

### Prerequisites

Before running the application, ensure you have the following:
*   Operating System: Compatible with Windows, macOS, or Linux.
*   Python Version: Python 3.6 or higher.
*   Hardware: An EEG headset compatible with the BrainFlow library (e.g., OpenBCI Cyton with Daisy module).


### Usage

1. Connect the EEG Headset:
	*   Ensure your EEG headset is properly connected to your computer.
	*   Check electrode impedance using the headset’s software before starting the data collection. Lower impedance levels are preferable.
2. Run the Application:

```bash
python eeg_motor_imagery.py
```

3.	Follow On-Screen Instructions:
*   Enter Session Number: You’ll be prompted to input a session number.
*   Enter Your Name: Provide your name when prompted.
*   Main Menu:
	*   Press S to start the trials.
	*   Press N to set the number of recordings (trials). The default is 20 trials per run.
	*   Press Q to quit the application.
*   During Trials:
	*   Follow the instructions displayed on the screen.
	*   Press M during trials to access the trial menu, where you can resume or quit.

### Code Overview

#### Main Components

*   Imports: The necessary libraries for EEG data acquisition, signal processing, and the graphical user interface are imported.
*   Utility Functions:
    *   find_serial_port(): Automatically detects the serial port for the EEG device.
    *   draw_plus_sign(screen, center_pos, plus_length, thickness, color): Draws a plus sign on the screen.
*   EEGProcessor Class:
	*   Handles EEG data acquisition and processing.
	*   Initializes the EEG board using BrainFlow.
	*   Implements methods to filter and buffer the EEG data.
*   Data Saving Function:
	*   save_data(eeg_processor, metadata, direction, trial_num, directory): Saves the processed EEG data and metadata for each trial.
*   Main Function:
	*   Handles the application flow, including the GUI and data collection logic.
	*   Manages different states like the main menu, input screens, trial runs, and menus during trials.

## Data Collection Procedure

### Overview

The data collection procedure involves guiding a subject through a series of motor imagery tasks while collecting EEG data. The subject is instructed to imagine squeezing their left or right hand based on arrow cues displayed on the screen. Consistency in the imagined movements and maintaining a still posture are crucial for obtaining high-quality data.

### Detailed Steps

1. Preparation:
    *   Electrode Impedance Check:
        *   Before starting, use the EEG headset software to check and minimize electrode impedance. Low impedance ensures better signal quality.
	*   Subject Instructions:
	    *   Instruct the subject to remain perfectly still during the data collection.
	    *   Emphasize the importance of consistent imagined movements throughout all trials.
	    *   Explain that they should imagine squeezing their left or right hand based on the arrow direction.
	    *   The imagined squeezing should involve a constant squeezing force, not repetitive opening and closing, to avoid introducing unwanted frequency components into the EEG signal.
	    *   Advise the subject to keep their hands still and in the same position for all trials.
2. Starting the Application:
	*   Run the application and enter the session number when prompted.
	*   Enter the subject’s name when requested.
3. Main Menu:
    *   Set the number of trials if different from the default (20 trials per run). It’s recommended to perform 20 trials per run.
    *   Press S to start the data collection.
4.	Data Collection Cycle:
	*   Random Rest Period (2-4 seconds):
        *   A blank screen is displayed.
        *   The rest period duration is randomized between 2 to 4 seconds to prevent the subject from anticipating the next focus period.
	*   Focus Period (2 seconds):
        *   A plus sign (+) appears at the center of the screen.
        *   The subject should focus intently on the plus sign, minimizing any movement or thought unrelated to the task.
	*   Priming Period (1.2 seconds):
        *   An arrow pointing left or right appears on the screen.
        *   The arrow indicates which hand the subject should imagine squeezing.
        *   This period prepares the subject for the motor imagery task without including reaction-related signals in the data.
	*   Data Collection Period (7 seconds):
	    *   The arrow remains on the screen.
        *   A progress bar starts moving from the center towards the corresponding green bar (located at 1/4 or 3/4 of the screen width).
        *   The subject should continuously imagine squeezing the indicated hand with a constant force until the progress bar reaches the green bar.
        *   The hands must remain still and in the same position.
	*   Rest Period (2-4 seconds):
	    *   A rest period allows the subject to relax before the next trial.
	    *   The duration is randomized between 2 to 4 seconds.
	*   Cycle Repeats:
	    *   The procedure repeats until the set number of trials is completed.
	    *   The direction of the arrow alternates between left and right in each trial.
5.	During Trials:
	*   The subject should avoid any physical movement.
	*   If necessary, the operator can press M to access the trial menu to pause or quit.
6.	Post-Run Recommendations:
	*   It’s recommended to complete 4 runs per session.
	*   Complete at least 2 sessions before starting to train a model.
	*   Allow a rest period between runs to prevent fatigue.

### Visual Cues and Interface

*   Green Bars:
	*   Positioned at the 1/4 and 3/4 marks of the screen width.
	*   Serve as endpoints for the progress bar during data collection.
*   Plus Sign:
	*   Appears during the focus period to center the subject’s attention.
*   Arrows:
	*   Indicate the hand the subject should imagine squeezing.
	*   Left arrow for the left hand, right arrow for the right hand.
*   Progress Bar:
	*   Moves from the center towards the green bar over 7 seconds.
	*   Provides a visual indicator of the data collection duration.

### Best Practices for Data Collection

*   Consistency:
	*   Ensure that the subject’s imagined movements are consistent across all trials.
	*   The imagined squeezing should be of constant force and duration.
*   Stillness:
	*   The subject must remain perfectly still to avoid introducing artifacts into the EEG data.
	*   Hands should be in the same position throughout the session.
*   Environment:
	*   Conduct the session in a quiet environment with minimal distractions.
*   Session Management:
	*   Regularly monitor the subject’s state to ensure they are not fatigued.
	*   Offer breaks between runs if necessary.
*   Data Integrity:
	*   Check the EEG data periodically to ensure signal quality.
	8   Address any issues with electrode placement or impedance promptly.

### Contact Information

For any questions or support, please contact:
	•	Email: n.feldt@utexas.edu

Contrabution is encouraged and welcome!

