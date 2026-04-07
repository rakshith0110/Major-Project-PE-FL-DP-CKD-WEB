import torch
import math

def clip_gradients(model, max_norm: float):
    total_sq = 0.0
    for p in model.parameters():
        if p.grad is None:
            continue
        total_sq += p.grad.data.norm(2).item()**2
    total_norm = math.sqrt(total_sq)
    if total_norm > max_norm and total_norm > 0:
        scale = max_norm / (total_norm + 1e-12)
        for p in model.parameters():
            if p.grad is None:
                continue
            p.grad.data.mul_(scale)
    return total_norm

def add_gaussian_noise(model, noise_multiplier: float, max_norm: float, device="cpu"):
    std = noise_multiplier * max_norm
    for p in model.parameters():
        if p.grad is None:
            continue
        noise = torch.randn_like(p.grad, device=device) * std
        p.grad.data.add_(noise)
