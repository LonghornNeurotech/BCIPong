from multiprocessing import Pipe, Process
import time
import pygame_brain_pong

# A test of external input, to be done via the motor imagery model
# This implementation runs human vs AI pong with "AI" being controlled
# by 0 and 1 inputs 
def external_proc(conn):
    """
    A test of external input, to be done via the motor imagery model.
    This implementation runs human vs AI pong with "AI" being controlled
    by 0 and 1 inputs.

    Args:
        conn (Connection Obj): The parent connection being piped to the child
        connection.
    """
    while True:
        command = input("Enter 0 (up) or 1 (down) for paddle movement (q to quit): ")
        if command.lower() == 'q':
            break
        if command in ['0', '1']:
            conn.send(int(command))
        else:
            print("Invalid input. Please enter 0, 1, or q.")

if __name__ == "__main__":
    parent_conn, child_conn = Pipe()
    
    # Start Pong in a separate process
    game_process = Process(target=pygame_brain_pong.main, args=(child_conn,))
    game_process.start()
    
    try:
        external_proc(parent_conn)
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        # Terminate the game process
        game_process.terminate()
        game_process.join()