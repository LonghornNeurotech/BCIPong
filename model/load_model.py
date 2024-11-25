from model.CapsNet import EEGCapsNet
import torch

class LoadModel:
    def __init__(self, model_path):
        self.model = EEGCapsNet()
        if type(model_path) == str:
            self.model.load_state_dict(torch.load(model_path, weights_only=True))
        else:
            self.model.load_state_dict(model_path)
            
    def _get(self):
        return self.model.eval()
