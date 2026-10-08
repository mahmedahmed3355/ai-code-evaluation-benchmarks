import torch
from torch import nn

class TinyNet(nn.Module):
    def __init__(self, input_dim=4, hidden_dim=7, output_dim=2):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(input_dim, hidden_dim), nn.Tanh(), nn.Linear(hidden_dim, output_dim))

    def forward(self, x):
        return self.net(x)
