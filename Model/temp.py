# train_midas.py (updated & stable)
import numpy as np, pandas as pd, torch, torch.nn as nn
from torch.utils.data import DataLoader, Dataset
from sklearn.preprocessing import RobustScaler
from sklearn.metrics import classification_report, confusion_matrix, balanced_accuracy_score
from collections import Counter

# ---- Config ----
L, STRIDE = 60, 10                 # window length & stride
BATCH, EPOCHS = 256, 12
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
AD_THRESHOLD = 0.5                  # stage-1 threshold

# ---- Load merged CSV ----
df = pd.read_csv(r"G:\Projects\honeywell\Anomalyze\DataProcessing\exported_data.csv")
drop_cols = ['number','Timestamp','Parameter for Anomaly','Actual value','Run id']
X = df.drop(columns=drop_cols + ['Anomaly']).values.astype('float32')
y_ac = df['Anomaly'].astype(int).values   # 0,1,2,3   (Normal, Freeze, Step, Ramp)
y_ad = (y_ac != 0).astype(int)            # 0/1

# ---- Split by run to avoid leakage ----
runs = df['Run id'].values
run_ids = np.unique(runs)
rng = np.random.RandomState(42)
rng.shuffle(run_ids)
test_runs = set(run_ids[:int(0.2*len(run_ids))])
mask_test = np.isin(runs, list(test_runs))
mask_train = ~mask_test

# ---- Scale per run (robust) using train only ----
scaler = RobustScaler().fit(X[mask_train])
X = scaler.transform(X)

# ---- Build sliding windows ----
def make_windows(X, y_ad, y_ac, runs, mask):
    Xw, yad, yac = [], [], []
    for r in np.unique(runs[mask]):
        idx = np.where((runs==r) & mask)[0]
        for s in range(0, len(idx)-L+1, STRIDE):
            sl = idx[s:s+L]
            Xw.append(X[sl])
            yad.append(int(np.any(y_ad[sl]==1)))
            # majority label inside window for AC
            vals, cnts = np.unique(y_ac[sl], return_counts=True)
            yac.append(int(vals[np.argmax(cnts)]))
    return np.stack(Xw), np.array(yad), np.array(yac)

Xt, yad_t, yac_t = make_windows(X, y_ad, y_ac, runs, mask_train)
Xv, yad_v, yac_v = make_windows(X, y_ad, y_ac, runs, mask_test)

class WinSet(Dataset):
    def __init__(self, X, y): self.X, self.y = X, y
    def __len__(self): return len(self.y)
    def __getitem__(self, i): return torch.from_numpy(self.X[i]), torch.tensor(self.y[i])

# ---- Stage-1: AD model (GRU) ----
class GRU_AD(nn.Module):
    def __init__(self, nfeats): 
        super().__init__()
        self.gru = nn.GRU(nfeats, 64, batch_first=True)
        self.fc  = nn.Linear(64, 1)
    def forward(self, x):
        h,_ = self.gru(x)
        return self.fc(h[:,-1])   # raw logits

ad_train, ad_val = WinSet(Xt, yad_t), WinSet(Xv, yad_v)

# class weights
pos = max(1, yad_t.sum())
neg = max(1, len(yad_t) - pos)
pos_weight = torch.tensor(neg/pos, device=DEVICE, dtype=torch.float32)
criterion_ad = nn.BCEWithLogitsLoss(pos_weight=pos_weight)

def train_ad():
    model = GRU_AD(X.shape[1]).to(DEVICE)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    for ep in range(EPOCHS):
        model.train(); total_loss=0.0
        for xb, yb in DataLoader(ad_train, batch_size=BATCH, shuffle=True):
            xb, yb = xb.to(DEVICE), yb.float().to(DEVICE)
            logits = model(xb).squeeze(1)
            loss = criterion_ad(logits, yb)
            opt.zero_grad(); loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)  # grad clipping
            opt.step()
            total_loss += loss.item()
        # Validation
        model.eval()
        with torch.no_grad():
            val_preds, val_labels = [], []
            for xb, yb in DataLoader(ad_val, batch_size=BATCH):
                xb, yb = xb.to(DEVICE), yb.float().to(DEVICE)
                logits = model(xb).squeeze(1)
                val_preds.extend(torch.sigmoid(logits).cpu().numpy())
                val_labels.extend(yb.cpu().numpy())
        val_acc = balanced_accuracy_score(val_labels, (np.array(val_preds) >= AD_THRESHOLD))
        print(f"[AD] Epoch {ep+1}/{EPOCHS} - Loss: {total_loss:.4f} - Val BalAcc: {val_acc:.4f}")
    return model

ad_model = train_ad()

# ---- Stage-2: AC model (GRU) trained on anomalous windows only ----
anom_train_idx = np.where(yad_t==1)[0]
anom_val_idx   = np.where(yad_v==1)[0]

class GRU_AC(nn.Module):
    def __init__(self, nfeats, nclass=4):
        super().__init__()
        self.gru = nn.GRU(nfeats, 96, batch_first=True)
        self.fc  = nn.Linear(96, nclass)
    def forward(self, x):
        h,_ = self.gru(x)
        return self.fc(h[:,-1])

ac_train = WinSet(Xt[anom_train_idx], yac_t[anom_train_idx])
ac_val   = WinSet(Xv[anom_val_idx], yac_v[anom_val_idx])

# class weights for AC
cnt = Counter(ac_train.y.tolist())
weights = torch.tensor([max(cnt.values())/max(1,cnt.get(c,1)) for c in range(4)], 
                       dtype=torch.float32, device=DEVICE)
criterion_ac = nn.CrossEntropyLoss(weight=weights)

def train_ac():
    model = GRU_AC(X.shape[1]).to(DEVICE)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    for ep in range(EPOCHS):
        model.train(); total_loss = 0.0
        for xb, yb in DataLoader(ac_train, batch_size=BATCH, shuffle=True):
            xb, yb = xb.to(DEVICE), yb.long().to(DEVICE)
            logits = model(xb)
            loss = criterion_ac(logits, yb)
            opt.zero_grad(); loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)  # grad clipping
            opt.step()
            total_loss += loss.item()
        # Validation
        model.eval()
        with torch.no_grad():
            val_preds, val_labels = [], []
            for xb, yb in DataLoader(ac_val, batch_size=BATCH):
                xb, yb = xb.to(DEVICE), yb.long().to(DEVICE)
                logits = model(xb)
                val_preds.extend(logits.argmax(1).cpu().numpy())
                val_labels.extend(yb.cpu().numpy())
        val_acc = balanced_accuracy_score(val_labels, val_preds)
        print(f"[AC] Epoch {ep+1}/{EPOCHS} - Loss: {total_loss:.4f} - Val BalAcc: {val_acc:.4f}")
    return model

ac_model = train_ac()

# ---- Inference (two-stage) ----
def infer_two_stage(Xw):
    with torch.no_grad():
        pa = torch.sigmoid(ad_model(torch.from_numpy(Xw).to(DEVICE))).cpu().numpy().ravel()
    yhat_ad = (pa >= AD_THRESHOLD)
    yhat_ac = np.zeros(len(Xw), dtype=int)
    if yhat_ad.any():
        idx = np.where(yhat_ad)[0]
        with torch.no_grad():
            logits = ac_model(torch.from_numpy(Xw[idx]).to(DEVICE)).cpu().numpy()
        yhat_ac[idx] = logits.argmax(1)
    return yhat_ad.astype(int), yhat_ac

yhat_ad, yhat_ac = infer_two_stage(Xv)

# ---- Metrics ----
print("AD balanced acc:", balanced_accuracy_score(yad_v, yhat_ad))
print("AD report:\n", classification_report(yad_v, yhat_ad, digits=4))
print("AC (on anomalous) report:\n", classification_report(yac_v[yad_v==1], yhat_ac[yad_v==1], digits=4))
print("AC confusion:\n", confusion_matrix(yac_v[yad_v==1], yhat_ac[yad_v==1]))
