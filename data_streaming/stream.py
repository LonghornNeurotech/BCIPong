import brainflow as bf
import numpy as np
import time
from preprocessing.preprocess import PreProcess
from model.load_model import LoadModel
from model.generate_weights import GenerateWeights
import torch
import os


class Stream:
    def __init__(self, board_id, serial_port):
        self.model_path = os.path.join("add-model-path-here")
        print("STREAM RUNNING")
        print("MODEL PATH:", self.model_path)
        self.board_id = board_id
        self.serial_port = serial_port
        self.params = bf.BrainFlowInputParams()
        self.params.serial_port = serial_port
        self.board = bf.BoardShim(self.board_id, self.params)
        self.channels = self.board.get_eeg_channels(self.board_id)
        self.buffer = np.zeros((len(self.channels), 192))
        self.stop = False
        self.preprocess = PreProcess(125, 4, 40, 2)
        self.model_path = GenerateWeights()._get()
        self.model = LoadModel(self.model_path)._get()
        self.current_index = -192
    
    def one_hot(self, y):
        y = y[0]
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
                
    def begin_stream(self):
        print("starting stream")
        self.board.prepare_session()
        self.board.start_stream()
        time.sleep(2)
    
    def get_output(self):
        data = self.board.get_board_data()
        temp = data[self.channels]
        self.current_index += np.shape(temp)[1]
        data_save = self.preprocess.preprocess(data[self.channels])
        data = torch.tensor(data_save, dtype=torch.float32).unsqueeze(0).unsqueeze(0)
        out = self.model(data, mode='test')

        return self.one_hot(out), self.current_index, data_save
    
    def reload_model(self):
        self.model = LoadModel(self.model_path)._get()

    def save_preds(self, index, correct):
        print("Saving raw data...")
        current_time = time.strftime("%m%d-%H%M%S")
        raw = self.preprocess.buffer[:, -self.current_index-192:]
        np.save(f"{os.getcwd()}/data/raw_data_{correct}_{current_time}.npy", raw)
        self.current_index = -192
        print("Raw data saved.")
