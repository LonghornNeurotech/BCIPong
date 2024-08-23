import torch
import torch.nn as nn
import numpy as np
import torch.nn.functional as F

class Squash(nn.Module):
    def __init__(self, eps=1e-20):
        super(Squash, self).__init__()
        self.eps = eps

    def forward(self, x):
        norm = torch.linalg.norm(x, ord=2, dim=-1, keepdim=True)
        coef = 1 - 1 / (torch.exp(norm) + self.eps)
        unit = x / (norm + self.eps)
        return coef * unit

class Routing(nn.Module):
    def __init__(self, groups, in_dims, out_dims):
        super(Routing, self).__init__()
        N0, D0 = in_dims
        N1, self.D1 = out_dims
        self.W = nn.Parameter(torch.Tensor(groups, N1, N0, D0, self.D1))
        nn.init.kaiming_normal_(self.W)
        self.b = nn.Parameter(torch.zeros(groups, N1, N0, 1))
        self.squash = Squash()

    def forward(self, x):

        u = torch.einsum('...gni,gknid->...gknd', x, self.W) # shape: (B, G, N1, N0, D1)

        c = torch.einsum("...ij,...kj->...i", u, u) # shape: (B, N1, N0)

        c = c[..., None]  # (B, N1, N0, 1) for bias broadcasting
        c = c / torch.sqrt(torch.tensor(self.D1).float())  # stabilize
        c = torch.softmax(c, axis=1) + self.b

        ## new capsules
        s = torch.sum(u * c, dim=-2)

        return self.squash(s)
    

class ReconstructionNet(nn.Module):
    def __init__(self, input_size=(1, 28, 28), num_classes=2, num_capsules=64):
        super(ReconstructionNet, self).__init__()
        self.input_size = input_size
        self.fc1 = nn.Linear(in_features=num_capsules * num_classes, out_features=512)
        self.fc2 = nn.Linear(512, 1024)
        self.fc3 = nn.Linear(1024, np.prod(input_size) * 2)
        self.relu = nn.ReLU()
        self.reset_parameters()

    def reset_parameters(self):
        gain = nn.init.calculate_gain('relu')
        nn.init.xavier_normal_(self.fc1.weight, gain=gain)
        nn.init.xavier_normal_(self.fc2.weight, gain=gain)
        nn.init.xavier_normal_(self.fc3.weight, gain=gain)

    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.fc3(x)
        x = x.view(x.size(0), 2, *self.input_size).squeeze(1)
        complex_x = torch.complex(x[:, 0], x[:, 1]) # create complex tensor to reflext fourier transform
        return complex_x
    

class CapsMask(nn.Module):
    def __init__(self):
        super(CapsMask, self).__init__()

    def forward(self, x, y_true=None):
        if y_true is not None:  # training mode
            mask = y_true
        else:  # testing mode
            # convert list of maximum value's indices to one-hot tensor
            temp = torch.sqrt(torch.sum(x**2, dim=-1))
            mask = F.one_hot(torch.argmax(temp, dim=1), num_classes=temp.shape[1])
        
        masked = x * mask.unsqueeze(-1)

        return masked.view(x.shape[0], -1)  # reshape
    

class CapsLen(nn.Module):
    def __init__(self, eps=1e-7):
        super(CapsLen, self).__init__()
        self.eps = eps

    def forward(self, x):
        return torch.sqrt(
            torch.sum(x**2, dim=-1) + self.eps
        )  # (batch_size, num_capsules)
