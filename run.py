import brainflow as bf
from data_streaming.stream import Stream

if __name__ == '__main__':
    board_id = bf.BoardIds.CYTON_DAISY_BOARD.value
    serial_port = 'COM3'
    stream = Stream(board_id, serial_port)