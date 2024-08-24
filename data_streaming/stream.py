import brainflow as bf
import numpy as np
import time
from preprocessing.preprocess import PreProcess
from model.load_model import LoadModel
import torch
import os

class Stream:
    def __init__(self, board_id, serial_port):
        model_path = os.path.join(os.getcwd(), 'model/checkpoints/capsnet_15.pth')
        print("STREAM RUNNING")
        print("MODEL PATH:", model_path)
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
        self.model = LoadModel(model_path)._get()
    
    def one_hot(self, y):
        y = y[0]
        # get index of max value
        print(y)
        one_hot = np.zeros(2)
        one_hot[np.argmax(y)] = 1
        return one_hot
        
    def stream(self):
        self.board.start_stream()
        time.sleep(2)
        with torch.no_grad():
            while not self.stop:
                time.sleep(0.08)
                data = self.board.get_board_data()
                data = self.preprocess.preprocess(data[self.channels])
                data = torch.tensor(data, dtype=torch.float32).unsqueeze(0).unsqueeze(0)
                out = self.model(data, mode='test')
                one_hot = self.one_hot(out)
                
    def start_stream(self):
        print("starting stream")
        self.board.start_stream()
        time.sleep(2)
    
    def get_output(self):
        data = self.board.get_board_data()
        data = self.preprocess.preprocess(data[self.channels])
        data = torch.tensor(data, dtype=torch.float32).unsqueeze(0).unsqueeze(0)
        out = self.model(data, mode='test')
        one_hot = self.one_hot(out)