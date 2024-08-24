"""import brainflow as bf
from data_streaming.stream import Stream

dirname = os.path.dirname(__file__)
print("DIRNAME:", dirname)

if __name__ == '__main__':
    board_id = bf.BoardIds.SYNTHETIC_BOARD.value
    serial_port = 'COM3'
    stream = Stream(board_id, serial_port)
    stream.stream()"""


import os
import sys
import platform
import brainflow as bf
from data_streaming.stream import Stream
from multiprocessing import Pipe, Process, Event
import game.pygame_brain_pong as pygame_brain_pong
import time
import serial.tools.list_ports
import torch
import numpy as np

dirname = os.path.dirname(__file__)
print(f"DIRNAME: {dirname}")

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

def stream_predictions(conn, stream, stop_event):
    """
    Stream predictions from the AI model and send them to the game.

    Args:
        conn (Connection): The connection object to send predictions to the game.
        stream (Stream): The Stream object for getting AI predictions.
        stop_event (Event): Event to signal when to stop the stream.
    """
    print(f"Stream predictions process started. PID: {os.getpid()}")
    
    max_retries = 5
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            # Start the stream
            stream.stream()
            print("Stream started successfully.")
            break
        except Exception as e:
            print(f"Error starting stream (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("Max retries reached. Unable to start stream.")
                return

    with torch.no_grad():
        while not stop_event.is_set() and not stream.stop:
            try:
                time.sleep(0.08)
                
                # Get the latest data from the stream
                data = stream.board.get_current_board_data(1)
                
                # Preprocess the data
                preprocessed_data = stream.preprocess.preprocess(data[stream.channels])
                
                # Prepare data for the model
                model_input = torch.tensor(preprocessed_data, dtype=torch.float32).unsqueeze(0).unsqueeze(0)
                
                # Make prediction
                prediction = stream.model(model_input, mode='test')
                
                # Convert to one-hot encoding
                one_hot = stream.one_hot(prediction.cpu().numpy())
                
                # Send command to the game
                command = int(one_hot[1])  # 0 for up, 1 for down
                conn.send(command)
            except Exception as e:
                print(f"Error in stream_predictions: {e}")
                break
    
    print("Stream predictions process ending.")
    # Ensure the stream is stopped
    stream.stop = True

def main():
    board_id = bf.BoardIds.SYNTHETIC_BOARD.value
    
    # Automatically find the serial port
    serial_port = find_serial_port()
    if serial_port is None:
        print("Could not automatically detect the serial port.")
        if platform.system() == "Windows":
            default_port = "COM3"
        elif platform.system() == "Darwin":  # macOS
            default_port = "/dev/tty.usbserial-DM00CKM8"
        else:  # Linux
            default_port = "/dev/ttyUSB0"
        serial_port = default_port
        print(f"Default port selected: {serial_port}")
    else:
        print(f"Automatically detected serial port: {serial_port}")
    
    """# List all available ports for reference
    ports = list(serial.tools.list_ports.comports())
    print("\nAll available ports:")
    for p in ports:
        print(f"- {p.device}")"""
    
    stream = None
    parent_conn, child_conn = Pipe()
    stop_event = Event()

    try:
        stream = Stream(board_id, serial_port)
        print("Stream object created successfully.")

        # Start Pong in a separate process
        game_process = Process(target=pygame_brain_pong.main, args=(child_conn,))
        game_process.start()
        print(f"Game process started. PID: {game_process.pid}")

        # Start the streaming process
        stream_process = Process(target=stream_predictions, args=(parent_conn, stream, stop_event))
        stream_process.start()
        print(f"Stream process started. PID: {stream_process.pid}")

        # Wait for processes to complete
        game_process.join()
        stream_process.join()

    except KeyboardInterrupt:
        print("\nKeyboard interrupt received. Exiting...")
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        print("Cleaning up...")
        # Stop the stream
        stop_event.set()
        if stream:
            stream.stop = True

        # Terminate the processes
        if 'game_process' in locals():
            game_process.terminate()
            game_process.join()
            print("Game process terminated.")
        if 'stream_process' in locals():
            stream_process.terminate()
            stream_process.join()
            print("Stream process terminated.")

        print("All processes terminated.")

if __name__ == "__main__":
    main()