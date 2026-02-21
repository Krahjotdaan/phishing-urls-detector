import os
import torch

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "best_model.pth")
SCALER_PATH = os.path.join(BASE_DIR, "models", "scaler.pkl")

MAX_LEN = 256
BATCH_SIZE = 1
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

CHARS = "".join(sorted(set(
    "abcdefghijklmnopqrstuvwxyz"
    "0123456789"
    "-._~"
    ":/?#[]@!$&'()*+,;="
    "`{}|\\^%\"<> "
)))
char_to_id = {ch: i + 1 for i, ch in enumerate(CHARS)}
