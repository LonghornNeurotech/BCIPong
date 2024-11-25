from model.CapsNet import EEGCapsNet
import torch
import os

class GenerateWeights:
    def __init__(self):
        self.model = EEGCapsNet()

    def _get(self):
        fake_weights = {}
        for name, param in self.model.state_dict().items():
            if param.dtype.is_floating_point:
                fake_weights[name] = torch.randn_like(param)
            else:
                fake_weights[name] = torch.randn(param.shape, dtype=torch.float32)
        # if weights do not already exist in cwd/weights, save the fake weights
        if not os.path.exists("weights/pong_weights.pth"):
            torch.save(fake_weights, "weights/pong_weights.pth")
        return fake_weights