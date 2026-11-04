"""Stand-in for DAP's networks.models.make, mimicking its output contract (for wrapper tests only)."""
import torch
import torch.nn as nn


class _FakeDAP(nn.Module):
    def __init__(self):
        super().__init__()
        self.scale = nn.Parameter(torch.tensor(0.05))

    def forward(self, x):
        d = (x.mean(1, keepdim=True) * 0 + 1) * self.scale  # constant 0.05 -> 5 m
        mask = torch.zeros_like(d)
        mask[..., :4, :] = 10.0  # top rows flagged as sky / invalid
        return {"pred_depth": d, "pred_mask": torch.sigmoid(mask) * (mask > 0)}


def make(spec):
    return _FakeDAP()
