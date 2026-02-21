import joblib
import torch
import torch.nn as nn
from detector.config import *
from detector.extraction import *

class HybridPhishNet(nn.Module):
    def __init__(self, vocab_size, embed_dim=128, kernel_sizes=[3, 4, 5, 6, 7, 8], num_filters=128, 
                 handcrafted_dim=13, hidden_cnn=128, hidden_hc=8, hidden_combined=16):
        super().__init__()
        
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.convs = nn.ModuleList([
            nn.Sequential(
                nn.Conv1d(embed_dim, num_filters, k),
                nn.ReLU(),
                nn.AdaptiveMaxPool1d(1)
            ) for k in kernel_sizes
        ])
        self.cnn_classifier = nn.Linear(num_filters * len(kernel_sizes), hidden_cnn)
        
        self.hc_net = nn.Sequential(
            nn.Linear(handcrafted_dim, 32),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(16, hidden_hc)
        )
        
        self.combined_net = nn.Sequential(
            nn.Linear(hidden_cnn + hidden_hc, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_combined, 1),
            nn.Sigmoid()
        )
    
    def forward(self, x_seq, x_hc):
        emb = self.embedding(x_seq).permute(0, 2, 1)
        cnn_features = torch.cat([conv(emb).squeeze(-1) for conv in self.convs], dim=1)
        cnn_out = self.cnn_classifier(cnn_features)
        hc_out = self.hc_net(x_hc)
        combined = torch.cat([cnn_out, hc_out], dim=1)
        return self.combined_net(combined).squeeze(-1)


class PhishDetector:
    def __init__(self, model_path=MODEL_PATH, scaler_path=SCALER_PATH, threshold=0.07):
        self.threshold = threshold
        self.scaler = joblib.load(scaler_path)
        self.model = HybridPhishNet(vocab_size=len(CHARS) + 1)

        self.model.load_state_dict(torch.load(model_path, map_location=DEVICE, weights_only=True))
        self.model.to(DEVICE)
        self.model.eval()
        
        print(f"Model was loaded on {DEVICE}")
    
    def predict(self, url: str) -> dict:
        if rule_based_phish(url):
            return {
                "is_phishing": True,
                "probability": 1.0,
                "rule_based": True
            }
        
        seq = url_to_seq(url)
        hc_features = extract_features(url)
        hc_scaled = self.scaler.transform([hc_features])
        
        with torch.no_grad():
            seq_tensor = torch.tensor([seq], dtype=torch.long).to(DEVICE)
            hc_tensor = torch.tensor(hc_scaled, dtype=torch.float32).to(DEVICE)
            
            probability = self.model(seq_tensor, hc_tensor).item()
            is_phishing = probability > self.threshold
        
        return {
            "is_phishing": bool(is_phishing),
            "probability": float(probability),
            "rule_based": False
        }
    