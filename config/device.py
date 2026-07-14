import torch

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

GPU_ENABLED = torch.cuda.is_available()