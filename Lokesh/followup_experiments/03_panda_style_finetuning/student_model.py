"""Compact fully-convolutional student for teacher pseudo-disparity distillation."""
from __future__ import annotations
import torch
from torch import nn
import torch.nn.functional as F


class Block(nn.Module):
    def __init__(self, cin: int, cout: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(cin, cout, 3, padding=1, bias=False),
            nn.GroupNorm(8, cout), nn.GELU(),
            nn.Conv2d(cout, cout, 3, padding=1, bias=False),
            nn.GroupNorm(8, cout), nn.GELU(),
        )
    def forward(self, x):
        return self.net(x)


class StudentDepthNet(nn.Module):
    """Small U-Net producing a single-channel relative disparity field."""
    def __init__(self, width: int = 32):
        super().__init__()
        self.e1 = Block(3, width)
        self.e2 = Block(width, width * 2)
        self.e3 = Block(width * 2, width * 4)
        self.mid = Block(width * 4, width * 6)
        self.d3 = Block(width * 10, width * 4)
        self.d2 = Block(width * 6, width * 2)
        self.d1 = Block(width * 3, width)
        self.out = nn.Conv2d(width, 1, 1)
        self.pool = nn.AvgPool2d(2)
    def forward(self, x):
        a = self.e1(x)
        b = self.e2(self.pool(a))
        c = self.e3(self.pool(b))
        m = self.mid(self.pool(c))
        z = F.interpolate(m, size=c.shape[-2:], mode="bilinear", align_corners=False)
        z = self.d3(torch.cat([z, c], 1))
        z = F.interpolate(z, size=b.shape[-2:], mode="bilinear", align_corners=False)
        z = self.d2(torch.cat([z, b], 1))
        z = F.interpolate(z, size=a.shape[-2:], mode="bilinear", align_corners=False)
        z = self.d1(torch.cat([z, a], 1))
        return self.out(z)
