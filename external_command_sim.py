from multiprocessing import Pipe, Process
import time
import pygame_brain_pong

def external_proc(conn):
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
    
    # Start the Pong game in a separate process
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