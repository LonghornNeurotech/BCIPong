import pygame
import sys
import time
import pickle
import numpy as np
from scipy.signal import butter, lfilter, iirnotch
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
import platform
import serial
import serial.tools.list_ports
import datetime
from datetime import timedelta
import pandas as pd
import zipfile
import os

def find_serial_port():
    """
    Automatically find the correct serial port for the device across different operating systems.
    
    Returns:
        str: The path of the detected serial port, or None if not found.
    """
    system = platform.system()
    ports = list(serial.tools.list_ports.comports())
    
    for port in ports:
        if system == "Darwin":  # macOS
            if any(identifier in port.device.lower() for identifier in ["usbserial", "cu.usbmodem", "tty.usbserial"]):
                return port.device
        elif system == "Windows":
            if "com" in port.device.lower():
                return port.device
        elif system == "Linux":
            if "ttyUSB" in port.device or "ttyACM" in port.device:
                return port.device
    
    return None

def draw_plus_sign(screen, center_pos, plus_length, thickness, color):
    # Draw horizontal line
    pygame.draw.line(screen, color,
                     (center_pos[0] - plus_length // 2, center_pos[1]),
                     (center_pos[0] + plus_length // 2, center_pos[1]),
                     thickness)
    # Draw vertical line
    pygame.draw.line(screen, color,
                     (center_pos[0], center_pos[1] - plus_length // 2),
                     (center_pos[0], center_pos[1] + plus_length // 2),
                     thickness)


def create_user_directory(name, session_num):
    dir_name = name + '_Session' + str(session_num)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    new_dir_path = os.path.join(script_dir, dir_name)
    os.mkdir(new_dir_path)
    return dir_name

class EEGProcessor:
    def __init__(self):
        # Initialize BrainFlow
        BoardShim.enable_dev_board_logger()
        params = BrainFlowInputParams()
        # serial_port = find_serial_port()
        # params.serial_port = serial_port
        # self.board_id = BoardIds.CYTON_DAISY_BOARD.value
        self.board_id = BoardIds.SYNTHETIC_BOARD.value
        self.board = BoardShim(self.board_id, params)
        self.board.prepare_session()
        self.board.start_stream()
        print("BrainFlow streaming started...")

        # Sampling rate and window size
        self.sampling_rate = BoardShim.get_sampling_rate(self.board_id)
        self.window_size_sec = 7  # seconds
        self.window_size_samples = int(self.window_size_sec * self.sampling_rate)

        # we set raw window size to 10 seconds
        self.window_size_raw = int(10 * self.sampling_rate)
        self.lowcut = 1.0
        self.highcut = 50.0
        self.notch = 60.0

        # Get EEG channels
        self.eeg_channels = BoardShim.get_eeg_channels(self.board_id)

        # Initialize buffers
        self.raw_data_buffer = np.empty((len(self.eeg_channels), 0))
        self.processed_data_buffer = np.empty((len(self.eeg_channels), 0))

    def stop(self):
        # Stop the data stream and release the session
        self.board.stop_stream()
        self.board.release_session()
        print("BrainFlow streaming stopped.")

    def get_recent_data(self):
        """
        Returns the most recent 7 seconds of processed EEG data.

        The data is bandpass filtered, notch filtered, and z-scored.
        Each data point is filtered only once.
        """
        data = self.board.get_board_data() 
        if data.shape[1] == 0:
            # No new data
            pass
        else:
        
            # Append new raw data to the raw_data_buffer
            eeg_data = data[self.eeg_channels, :]
            self.raw_data_buffer = np.hstack((self.raw_data_buffer, eeg_data))

            # Process new data
            new_processed_data = np.empty(self.raw_data_buffer.shape)
            # It is important to process each channel separately
            for i in range(len(self.eeg_channels)):

                # Get the channel data
                channel_data = self.raw_data_buffer[i, :].copy()

                # Bandpass filter
                b, a = butter(2, [self.lowcut, self.highcut], btype='band', fs=self.sampling_rate)
                channel_data = lfilter(b, a, channel_data)
                
                # Notch filter
                b, a = iirnotch(self.notch, 30, fs=self.sampling_rate)
                channel_data = lfilter(b, a, channel_data)

                new_processed_data[i, :] =  channel_data

            self.processed_data_buffer = np.hstack((self.processed_data_buffer, new_processed_data))

            max_buffer_size = self.window_size_samples * 2
            if self.raw_data_buffer.shape[1] > self.window_size_raw:
                self.raw_data_buffer = self.raw_data_buffer[:, -self.window_size_raw:]
            if self.processed_data_buffer.shape[1] > max_buffer_size:
                self.processed_data_buffer = self.processed_data_buffer[:, -max_buffer_size:]

        if self.processed_data_buffer.shape[1] >= self.window_size_samples:
            recent_data = self.processed_data_buffer[:, -self.window_size_samples:]
        else:
            recent_data = self.processed_data_buffer

        return recent_data
    
# Save last 7 seconds of signal and metadata to its own .pkl file in the session directory
def save_data(eeg_processor, metadata, direction, trial_num, directory):
    sig = eeg_processor.get_recent_data()
    # Establish a filename [direction]_[trial number].pkl
    filename = direction + '_' + str(trial_num) + '.npy'

    script_dir = os.path.dirname(os.path.abspath(__file__))
    intermediate = os.path.join(script_dir, directory)
    filepath = os.path.join(intermediate, filename)

    # Dump signal and metadata into pickle file - this saves into the folder that we created earlier
    np.save(filepath, sig)
    

def main():
    session_num = input("Enter the session number: ")
    eeg_processor = EEGProcessor()

    # Initialize Pygame
    pygame.init()
    infoObject = pygame.display.Info()
    screen = pygame.display.set_mode((infoObject.current_w, infoObject.current_h), pygame.FULLSCREEN)
    pygame.display.set_caption("Motor Imagery Task")

    # Colors
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)


    # Control Variables
    running = True
    in_menu = True
    in_input = False
    in_trial_menu = False
    in_questionaire_subject = False
    in_buffer_screen = False
    in_after_session_menu = False
    trial_number = 1
    total_trials = 20  # Default number of trials
    time_between_sessions = 180  # number of seconds to wait between sessions of data collection
    start_enable_time = time.time()  # the time at/after which the start button is enabled
    saved_questionnaire_data = False
    
    # Calculate font sizes based on screen height
    font_size_large = infoObject.current_h // 10
    font_size_medium = infoObject.current_h // 15
    font_size_small = infoObject.current_h // 20

    # Initialize fonts with the calculated sizes
    large_font = pygame.font.SysFont(None, font_size_large)
    medium_font = pygame.font.SysFont(None, font_size_medium)
    small_font = pygame.font.SysFont(None, font_size_small)

    green_bar_width = infoObject.current_w // 60
    green_bar_height = infoObject.current_h // 3
    loading_bar_thickness = infoObject.current_h // 30
    arrow_y_offset = infoObject.current_h // 10

    # Positions for Green Bars at 1/4 and 3/4 of the screen width
    left_green_bar_pos = (infoObject.current_w // 4 - green_bar_width // 2, infoObject.current_h // 2 - green_bar_height // 2)
    right_green_bar_pos = (3 * infoObject.current_w // 4 - green_bar_width // 2, infoObject.current_h // 2 - green_bar_height // 2)

    # Center Position
    center_pos = (infoObject.current_w // 2, infoObject.current_h // 2)

    # Plus sign settings
    plus_length = infoObject.current_h // 15  # Adjust as needed

    # Clock
    clock = pygame.time.Clock()

    # Input Variables
    input_text = ""
    input_error = False

    # Name Input
    name_input = ""
    input_error = False

    direction = 'left'  # Start with 'left' and alternate

    while running:

        if in_menu:
            screen.fill(BLACK)
            title_text = large_font.render("EEG Motor Imagery", True, WHITE)
            start_text = medium_font.render("Press S to Start", True, GREEN)
            set_text = medium_font.render("Press N to Set Number", True, WHITE)
            quit_text = medium_font.render("Press Q to Quit", True, RED)
            trials_text = small_font.render(f"Total Trials: {total_trials}", True, WHITE)

            # Positioning Text
            title_rect = title_text.get_rect(center=(infoObject.current_w // 2, infoObject.current_h // 5))
            start_rect = start_text.get_rect(center=(infoObject.current_w // 2, infoObject.current_h // 2 - font_size_medium))
            set_rect = set_text.get_rect(center=(infoObject.current_w // 2, infoObject.current_h // 2))
            quit_rect = quit_text.get_rect(center=(infoObject.current_w // 2, infoObject.current_h // 2 + font_size_medium))
            trials_rect = trials_text.get_rect(center=(infoObject.current_w // 2, infoObject.current_h // 2 -  1.1 * font_size_large))

            # Blit Text to Screen
            screen.blit(title_text, title_rect)
            screen.blit(start_text, start_rect)
            screen.blit(set_text, set_rect)
            screen.blit(quit_text, quit_rect)
            screen.blit(trials_text, trials_rect)
            pygame.display.flip()

            # Processing Input at the Main Menu
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s: 
                        if time.time() >= start_enable_time:
                            in_menu = False
                            in_questionaire_subject = True
                    elif event.key == pygame.K_n:
                        in_input = True
                        in_menu = False
                        input_text = ""
                        input_error = False
                    elif event.key == pygame.K_q:
                        running = False

        elif in_questionaire_subject:
            screen.fill(BLACK)
            # Positions based on scaled heights
            height_delta = infoObject.current_h // 8

            # Render and position text
            name_text = medium_font.render("Enter your name:", True, WHITE)
            name_rect = name_text.get_rect(center=(infoObject.current_w // 2, height_delta))

            # Render and position response
            name_response = medium_font.render(name_input, True, WHITE)
            name_response_rect = name_response.get_rect(center=(infoObject.current_w // 2, height_delta * 2))

            # Blit texts to the screen
            screen.blit(name_text, name_rect)
            screen.blit(name_response, name_response_rect)

            # Error message if needed
            if input_error:
                error_text = small_font.render("Please enter your name.", True, RED)
                error_rect = error_text.get_rect(center=(infoObject.current_w // 2, infoObject.current_h - font_size_small))
                screen.blit(error_text, error_rect)

            pygame.display.flip()

            # Event handling for name input
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        break
                    elif event.key == pygame.K_BACKSPACE:
                        name_input = name_input[:-1]
                        input_error = False  # Reset error flag when user modifies input
                    elif event.key == pygame.K_RETURN:
                        # Check if field is filled
                        if name_input.strip() != "":
                            in_questionaire_subject = False
                            in_buffer_screen = True
                            input_error = False  # Reset the error flag
                        else:
                            input_error = True  # Set the error flag to display an error message
                    else:
                        name_input += event.unicode
                        input_error = False  # Reset error flag when user modifies input

        elif in_buffer_screen:
            if not saved_questionnaire_data:
                # Save results of name input locally
                name = name_input

                # Use name to update metadata and create session directory
                directory = create_user_directory(name, session_num)
                metadata = {"Name": name}
                saved_questionnaire_data = True
        
            # Display buffer screen that appears before the trials
            screen.fill(BLACK)
            buffer_screen_title = large_font.render("Ready?", True, WHITE)
            start_trial_text = medium_font.render("Press S to Start Trial", True, GREEN)

            # Positioning Text
            buffer_screen_title_rect = buffer_screen_title.get_rect(center=(infoObject.current_w // 2, infoObject.current_h // 4))
            start_trial_text_rect = start_trial_text.get_rect(center=(infoObject.current_w // 2, infoObject.current_h // 2 + 50))

            # Blit Text to Screen
            screen.blit(buffer_screen_title, buffer_screen_title_rect)
            screen.blit(start_trial_text, start_trial_text_rect)
            pygame.display.flip()

            # Processing Inputs at the Buffer Screen
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        break
                    if event.key == pygame.K_s:
                        in_buffer_screen = False

        elif in_input:
            # Display Input Menu for Setting Number of Trials
            screen.fill(BLACK)
            prompt_text = medium_font.render("Enter Number of Recordings (Even):", True, WHITE)
            input_display = medium_font.render(input_text, True, GREEN if not input_error else RED)
            instructions_text = small_font.render("Press Enter to Confirm", True, WHITE)

            # Positioning Text
            prompt_rect = prompt_text.get_rect(center=(infoObject.current_w // 2, infoObject.current_h // 3))
            input_rect = input_display.get_rect(center=(infoObject.current_w // 2, infoObject.current_h // 2))
            instructions_rect = instructions_text.get_rect(center=(infoObject.current_w // 2, infoObject.current_h // 2 + 100))

            # Blit Text to Screen
            screen.blit(prompt_text, prompt_rect)
            screen.blit(input_display, input_rect)
            screen.blit(instructions_text, instructions_rect)
            pygame.display.flip()

            # Processing Inputs at the Input Menu
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        break
                    elif event.key == pygame.K_RETURN:
                        if input_text.isdigit():
                            entered_number = int(input_text)
                            if entered_number > 0:
                                if entered_number % 2 != 0:
                                    entered_number += 1  # Make it even
                                    input_error = True
                                total_trials = entered_number
                                in_input = False
                                in_menu = True
                            else:
                                input_error = True
                        else:
                            input_error = True
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    elif event.unicode.isdigit():
                        input_text += event.unicode

        elif in_trial_menu: 
            # Display Trial Menu (Accessible via 'M' during trials)
            screen.fill(BLACK)
            menu_title = medium_font.render("Trial Menu", True, WHITE)
            quit_text = medium_font.render("Press Q to Quit", True, RED)
            resume_text = medium_font.render("Press R to Resume", True, GREEN)

            # Positioning Text
            menu_title_rect = menu_title.get_rect(center=(infoObject.current_w // 2, infoObject.current_h // 3))
            quit_rect = quit_text.get_rect(center=(infoObject.current_w // 2, infoObject.current_h // 2))
            resume_rect = resume_text.get_rect(center=(infoObject.current_w // 2, infoObject.current_h // 2 + 100))

            # Blit Text to Screen
            screen.blit(menu_title, menu_title_rect)
            screen.blit(quit_text, quit_rect)
            screen.blit(resume_text, resume_rect)
            pygame.display.flip()

            # Processing Inputs at the Trial Menu 
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        running = False
                    elif event.key == pygame.K_r:
                        in_trial_menu = False

        elif in_after_session_menu:
            # Display After Session Menu
            screen.fill(BLACK)
            question_text = large_font.render("Do you want to continue?", True, WHITE)
            continue_text = medium_font.render("Press Y to continue", True, GREEN)
            quit_text = medium_font.render("Press N to exit", True, RED)

            # Positioning Text
            question_rect = question_text.get_rect(center=(infoObject.current_w // 2, infoObject.current_h // 4))
            continue_rect = continue_text.get_rect(center=(infoObject.current_w // 2, infoObject.current_h // 2 - 50))
            quit_rect = quit_text.get_rect(center=(infoObject.current_w // 2, infoObject.current_h // 2 + 50))

            # Blit Text to Screen
            screen.blit(question_text, question_rect)
            screen.blit(continue_text, continue_rect)
            screen.blit(quit_text, quit_rect)
            pygame.display.flip()

            # Processing Inputs at the After Session Menu
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_y:
                        in_after_session_menu = False
                        in_menu = True
                        start_enable_time = time.time() + time_between_sessions  # Enable the start button after the current time
                    elif event.key == pygame.K_n: 
                        in_after_session_menu = False
                        running = False
                        eeg_processor.board.stop_stream()
                        eeg_processor.board.release_session()
                        pygame.quit()
                        sys.exit()

        else:
            # Display Current Trial Number
            screen.fill(BLACK)
            # Redraw green bars
            pygame.draw.rect(screen, GREEN, (*left_green_bar_pos, green_bar_width, green_bar_height))
            pygame.draw.rect(screen, GREEN, (*right_green_bar_pos, green_bar_width, green_bar_height))

            # Draw Current Trial Info
            trial_info = small_font.render(f"Trial {trial_number}/{total_trials}", True, WHITE)
            trial_info_rect = trial_info.get_rect(topright=(infoObject.current_w - 50, 50))
            screen.blit(trial_info, trial_info_rect)

            # Draw Focus Period '+' sign
            draw_plus_sign(screen, center_pos, plus_length, loading_bar_thickness, WHITE)
            pygame.display.flip()

            # Collect data during focus period
            focus_duration = 3  # seconds
            focus_start_time = time.time()
            while time.time() - focus_start_time < focus_duration:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        break
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            running = False
                            break
                clock.tick(60)

            if not running:
                break

            # Show Arrow (Moved Up)
            arrow_color = WHITE
            arrow_length = infoObject.current_w // 10  
            arrow_width = infoObject.current_h // 40
            arrow_y_offset = infoObject.current_h // 10

            # Clear screen but keep green bars and trial info
            screen.fill(BLACK)
            # Redraw green bars
            pygame.draw.rect(screen, GREEN, (*left_green_bar_pos, green_bar_width, green_bar_height))
            pygame.draw.rect(screen, GREEN, (*right_green_bar_pos, green_bar_width, green_bar_height))
            # Redraw trial info
            screen.blit(trial_info, trial_info_rect)

            # Draw Arrow
            if direction == 'left':
                pygame.draw.polygon(screen, arrow_color, [
                    (center_pos[0] - arrow_length, center_pos[1] - arrow_y_offset),
                    (center_pos[0], center_pos[1] - arrow_y_offset - arrow_width),
                    (center_pos[0], center_pos[1] - arrow_y_offset + arrow_width)
                ])
            else:
                pygame.draw.polygon(screen, arrow_color, [
                    (center_pos[0] + arrow_length, center_pos[1] - arrow_y_offset),
                    (center_pos[0], center_pos[1] - arrow_y_offset - arrow_width),
                    (center_pos[0], center_pos[1] - arrow_y_offset + arrow_width)
                ])

            draw_plus_sign(screen, center_pos, plus_length, loading_bar_thickness, WHITE)

            pygame.display.flip()

            # Wait before starting the loading bar
            pre_loading_duration = 1.2  # second
            pre_loading_start = time.time()
            while time.time() - pre_loading_start < pre_loading_duration:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        break
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            running = False
                            break
                clock.tick(60)

            if not running:
                break

            # grab data before the loading bar starts to discard
            eeg_processor.get_recent_data()

            # Loading Bar
            loading_duration = 7  # seconds
            loading_start_time = time.time()

            while time.time() - loading_start_time < loading_duration:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        break
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            running = False
                            break
                        elif event.key == pygame.K_m:
                            in_trial_menu = True
                            break

                # Calculate loading bar progress
                elapsed_time = time.time() - loading_start_time
                loading_progress = elapsed_time / loading_duration

                screen.fill(BLACK)
                # Redraw green bars
                pygame.draw.rect(screen, GREEN, (*left_green_bar_pos, green_bar_width, green_bar_height))
                pygame.draw.rect(screen, GREEN, (*right_green_bar_pos, green_bar_width, green_bar_height))
                # Redraw trial info
                screen.blit(trial_info, trial_info_rect)

                # Redraw Arrow
                if direction == 'left':
                    pygame.draw.polygon(screen, arrow_color, [
                        (center_pos[0] - arrow_length, center_pos[1] - arrow_y_offset),
                        (center_pos[0], center_pos[1] - arrow_y_offset - arrow_width),
                        (center_pos[0], center_pos[1] - arrow_y_offset + arrow_width)
                    ])
                    # Calculate current length of the loading bar
                    # From center to left green bar
                    max_length = center_pos[0] - (left_green_bar_pos[0] + green_bar_width)
                    current_length = loading_progress * max_length

                    # Draw loading bar moving left from center
                    pygame.draw.rect(screen, WHITE, (
                        center_pos[0] - current_length,  # Start at center and move left
                        center_pos[1] - loading_bar_thickness // 2,
                        current_length,
                        loading_bar_thickness
                    ))
                else:
                    pygame.draw.polygon(screen, arrow_color, [
                        (center_pos[0] + arrow_length, center_pos[1] - arrow_y_offset),
                        (center_pos[0], center_pos[1] - arrow_y_offset - arrow_width),
                        (center_pos[0], center_pos[1] - arrow_y_offset + arrow_width)
                    ])
                    # Calculate current length of the loading bar
                    # From center to right green bar
                    max_length = (right_green_bar_pos[0]) - center_pos[0]
                    current_length = loading_progress * max_length

                    # Draw loading bar moving right from center
                    pygame.draw.rect(screen, WHITE, (
                        center_pos[0],  # Start at center and move right
                        center_pos[1] - loading_bar_thickness // 2,
                        current_length,
                        loading_bar_thickness
                    ))

                draw_plus_sign(screen, center_pos, plus_length, loading_bar_thickness, WHITE)

                pygame.display.flip()
                save_data(eeg_processor, metadata, direction, trial_number, directory)
                clock.tick(60)

            if not running:
                break

            # Optional rest period with accessible menu
            # random rest between 3, 5 seconds
            rest_duration = np.random.uniform(3, 5)
            rest_start_time = time.time()
            while time.time() - rest_start_time < rest_duration:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        break
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            running = False
                            break
                        elif event.key == pygame.K_m:
                            in_trial_menu = True
                            break

                # Display Rest Text with Menu Instruction
                screen.fill(BLACK)
                # Redraw green bars
                pygame.draw.rect(screen, GREEN, (*left_green_bar_pos, green_bar_width, green_bar_height))
                pygame.draw.rect(screen, GREEN, (*right_green_bar_pos, green_bar_width, green_bar_height))
                # Redraw trial info
                screen.blit(trial_info, trial_info_rect)

                rest_text = small_font.render("Rest (Press M for Menu)", True, WHITE)
                rest_rect = rest_text.get_rect(center=center_pos)
                screen.blit(rest_text, rest_rect)
                pygame.display.flip()
                clock.tick(60)

            if not running:
                break

            # Alternate Direction
            if direction == 'left':
                direction = 'right'
            else:
                direction = 'left'

            trial_number += 1

            # Check if all trials are completed
            if trial_number > total_trials:
                # Display a completion message
                screen.fill(BLACK)
                completion_text = medium_font.render("All Trials Completed!", True, GREEN)
                completion_rect = completion_text.get_rect(center=center_pos)
                screen.blit(completion_text, completion_rect)
                pygame.display.flip()
                # Wait for 3 seconds before returning to menu
                time.sleep(3)
                trial_number = 1  # Reset trial number
                in_after_session_menu = True

        # Handle Trial Menu outside the main loop to avoid missing quit events
        while in_trial_menu and running:
            # Display Trial Menu (Accessible via 'M' during trials)
            screen.fill(BLACK)
            menu_title = medium_font.render("Trial Menu", True, WHITE)
            quit_text = medium_font.render("Press Q to Quit", True, RED)
            resume_text = medium_font.render("Press R to Resume", True, GREEN)

            # Positioning Text
            menu_title_rect = menu_title.get_rect(center=(infoObject.current_w // 2, infoObject.current_h // 3))
            quit_rect = quit_text.get_rect(center=(infoObject.current_w // 2, infoObject.current_h // 2))
            resume_rect = resume_text.get_rect(center=(infoObject.current_w // 2, infoObject.current_h // 2 + 100))

            # Blit Text to Screen
            screen.blit(menu_title, menu_title_rect)
            screen.blit(quit_text, quit_rect)
            screen.blit(resume_text, resume_rect)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    in_trial_menu = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        running = False
                        in_trial_menu = False
                    elif event.key == pygame.K_r:
                        in_trial_menu = False


if __name__ == "__main__":
    main()