import torch
import torch.nn as nn

class MLP(nn.Module):
    def __init__(self, in_dim: int, hidden=(256,128,64), dropout=0.2):
        super().__init__()
        layers = []
        last = in_dim
        for h in hidden:
            layers += [nn.Linear(last, h), nn.ReLU(), nn.Dropout(dropout)]
            last = h
        layers += [nn.Linear(last, 1)]
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        return self.net(x)

def build_model(input_dim: int):
    return MLP(input_dim)
