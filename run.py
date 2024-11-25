# run.py

import platform
import brainflow as bf
from multiprocessing import Pipe, Process, Event
from data_streaming.stream import Stream
from utils import find_serial_port
from streamer import stream_predictions

def main():
    """
    Main function to start the BCI Pong game.
    """
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

    stream = None
    parent_conn, child_conn = Pipe()
    stop_event = Event()

    try:
        stream = Stream(board_id, serial_port)
        print("Stream object created successfully.")

        # Start the game process
        from game.main import main as game_main
        game_process = Process(target=game_main, args=(child_conn,))
        print("Starting the game...")
        game_process.start()
        print(f"Game process started. PID: {game_process.pid}")

        # Start the streaming process
        stream_process = Process(target=stream_predictions, args=(parent_conn, stream, stop_event))
        stream_process.start()
        print(f"Stream process started. PID: {stream_process.pid}")

        # Wait for the game process to complete
        game_process.join()
        print("Game process completed.")

        # Signal the streaming process to stop
        stop_event.set()
        stream_process.join()
        print("Stream process terminated.")

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

        # Terminate the processes if they're still running
        if 'game_process' in locals() and game_process.is_alive():
            game_process.terminate()
            game_process.join()
            print("Game process terminated.")
        if 'stream_process' in locals() and stream_process.is_alive():
            stream_process.terminate()
            stream_process.join()
            print("Stream process terminated.")

        print("All processes terminated.")

if __name__ == "__main__":
    main()