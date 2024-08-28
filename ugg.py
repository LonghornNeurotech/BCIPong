from online_training import train
import torch

model_weights = torch.load("C:/Users/Nathan/Git/capsnet_49.pth")["state_dict"]
#save
torch.save(model_weights, "C:/Users/Nathan/Git/capsnet_49.pth")