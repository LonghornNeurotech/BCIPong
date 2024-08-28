from model.CapsNet import EEGCapsNet
import torch

class LoadModel:
    def __init__(self, model_path):
        self.model = EEGCapsNet()
        self.model.load_state_dict(torch.load(model_path, weights_only=True))
        self.model.eval()

    def _get(self):
        return self.model
