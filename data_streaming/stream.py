import brainflow as bf
import numpy as np
import time
from BCIPong.preprocessing.preprocess import PreProcess
from BCIPong.model.load_model import LoadModel
import torch

class Stream:
    def __init__(self, board_id, serial_port):
        self.board_id = board_id
        self.serial_port = serial_port
        self.params = bf.BrainFlowInputParams()
        self.params.serial_port = serial_port
        self.board = bf.BoardShim(board_id, self.params)
        self.channels = self.board.get_eeg_channels(board_id)
        self.board.prepare_session()
        self.buffer = np.zeros((self.channels.size, 192))
        self.stop = False
        self.preprocess = PreProcess(125, 4, 40, 2)
        self.model = LoadModel('/home/nathan/Desktop/BCIMOUSE/capsnet_15.pth')._get()
        
    def stream(self):
        self.board.start_stream()
        time.sleep(2)
        with torch.no_grad():
            while not self.stop:
                time.sleep(0.1)
                data = self.board.get_data()
                self.buffer = np.concatenate((self.buffer[:, data.shape[1]:], data[self.channels]), axis=1)
                data = self.preprocess.preprocess(self.buffer)
                start = time.time()
                data = torch.tensor(data, dtype=torch.float32).unsqueeze(0)
                out = self.model(data)
                end = time.time()
                print(f"Time taken: {end - start}")




if __name__ == '__main__':
    board_id = bf.BoardIDs.CYTON_DAISY_BOARD.value
    serial_port = 'COM3'
    stream = Stream(board_id, serial_port)



            




            


        