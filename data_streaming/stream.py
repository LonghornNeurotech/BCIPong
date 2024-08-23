import brainflow as bf
import numpy as np
import time
from preprocessing.preprocess import PreProcess
from model.load_model import LoadModel
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
        self.buffer = np.zeros((len(self.channels), 192))
        self.stop = False
        self.preprocess = PreProcess(125, 4, 40, 2)
        self.model = LoadModel('C:/Users/Nathan/Git/capsnet_15.pth')._get()
        
    def stream(self):
        self.board.start_stream()
        time.sleep(2)
        with torch.no_grad():
            while not self.stop:
                data = self.board.get_board_data()
                data = self.preprocess.preprocess(data[self.channels])
                data = torch.tensor(data, dtype=torch.float32).unsqueeze(0).unsqueeze(0)
                out = self.model(data)            




            


        