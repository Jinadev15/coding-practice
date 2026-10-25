---
id: py-train-imu-classifier
title: Train an IMU Activity Classifier in PyTorch
difficulty: Hard
order: 1
tags: pytorch, nn.Module, DataLoader, training loop, evaluation, state_dict
time_limit: 20
---
## Statement
Each sample is a 6-axis IMU window flattened to 48 features, labelled `idle`, `drive` or `turn` (0/1/2). Build the full training pipeline in PyTorch:

```python
class IMUNet(nn.Module):
    """Linear(48 -> 64) -> ReLU -> Dropout(0.1) -> Linear(64 -> 32) -> ReLU -> Linear(32 -> 3). Outputs logits."""

def make_loaders(X, y, batch_size, seed):
    """Split the tensors 80/20 with torch.utils.data.random_split (generator seeded with `seed`),
    return (train_loader shuffled with a seeded generator, val_loader not shuffled)."""

def train(model, train_loader, epochs, lr):
    """AdamW(lr), CrossEntropyLoss, standard loop; return the list of mean training losses per epoch."""

def evaluate(model, loader):
    """model.eval() + torch.no_grad(); return accuracy as a float."""

def save_and_reload(model, path):
    """Save the state_dict to path, load it into a NEW IMUNet with torch.load(weights_only=True); return it."""
```

The driver checks the architecture (parameter count and layer types), that training reduces the loss, that validation accuracy is high, that `evaluate` leaves the model in eval mode and creates no graph, and that a reloaded model gives identical predictions.

## Starter
```python
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

class IMUNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = nn.Linear(48, 3)
    def forward(self, x):
        return torch.softmax(self.fc(x), dim=1)

def make_loaders(X, y, batch_size, seed):
    ds = TensorDataset(X, y)
    return DataLoader(ds, batch_size=batch_size), DataLoader(ds, batch_size=batch_size)

def train(model, train_loader, epochs, lr):
    return [0.0] * epochs

def evaluate(model, loader):
    return 0.0

def save_and_reload(model, path):
    return model
```

## Driver
```python
import sys
import torch

torch.manual_seed(0)
torch.set_num_threads(1)

def make_data(n, seed):
    g = torch.Generator().manual_seed(seed)
    y = torch.randint(0, 3, (n,), generator=g)
    t = torch.linspace(0, 1, 8)
    X = torch.randn(n, 6, 8, generator=g) * 0.3
    X[y == 1, 0] += 1.0                                     # driving: forward acceleration
    X[y == 2, 5] += torch.sin(6.28 * t)                     # turning: yaw-rate oscillation
    return X.reshape(n, 48), y

X, y = make_data(3000, 42)
for cmd in sys.stdin.read().split():
    if cmd == "arch":
        m = IMUNet()
        layers = [type(l).__name__ for l in m.modules() if not isinstance(l, (torch.nn.Sequential, IMUNet))]
        print("params:", sum(p.numel() for p in m.parameters()), "layers:", layers)
        out = m(torch.randn(5, 48))
        print("output shape:", tuple(out.shape), "logits (not probabilities):", not torch.allclose(out.sum(1), torch.ones(5)))
    elif cmd == "loaders":
        tr, va = make_loaders(X, y, 64, 0)
        print("sizes:", len(tr.dataset), len(va.dataset), "batch:", tr.batch_size)
        xb, yb = next(iter(tr))
        print("batch shapes:", tuple(xb.shape), tuple(yb.shape), yb.dtype)
    elif cmd == "train":
        torch.manual_seed(0)
        tr, va = make_loaders(X, y, 64, 0)
        m = IMUNet()
        m.eval()
        with torch.no_grad():
            init_loss = torch.nn.functional.cross_entropy(m(X[:500]), y[:500]).item()
        losses = train(m, tr, 8, 3e-3)
        acc = evaluate(m, va)
        print("epochs:", len(losses), "loss decreased:", losses[-1] < losses[0] * 0.5, "untrained loss ~ ln3:", abs(init_loss - 1.0986) < 0.35)
        print("val acc > 0.95:", acc > 0.95, "| eval mode after evaluate:", not m.training)
        m2 = save_and_reload(m, "imu.pt")
        m2.eval()
        with torch.no_grad():
            same = torch.equal(m(X[:100]), m2(X[:100]))
        print("reloaded identical:", same, "| distinct object:", m2 is not m)
```

## Tests
=== sample
arch
loaders
---
params: 5315 layers: ['Linear', 'ReLU', 'Dropout', 'Linear', 'ReLU', 'Linear']
output shape: (5, 3) logits (not probabilities): True
sizes: 2400 600 batch: 64
batch shapes: (64, 48) (64,) torch.int64
=== hidden
train
---
epochs: 8 loss decreased: True untrained loss ~ ln3: True
val acc > 0.95: True | eval mode after evaluate: True
reloaded identical: True | distinct object: True

## Hints
- Use `nn.Sequential(...)` inside `IMUNet`. Return **logits**, because `CrossEntropyLoss` applies log-softmax itself. Parameters: 48·64+64 + 64·32+32 + 32·3+3 = 5315.
- `ds = TensorDataset(X, y)`; `n_tr = int(0.8 * len(ds))`; `random_split(ds, [n_tr, len(ds) - n_tr], generator=torch.Generator().manual_seed(seed))`.
- Training loop per batch: `opt.zero_grad()`, `loss = loss_fn(model(xb), yb)`, `loss.backward()`, `opt.step()`. Call `model.train()` at the start of training.
- `evaluate`: `model.eval()`, then `with torch.no_grad():` count `argmax(1) == yb`.

## Solution
```python
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset, random_split

class IMUNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(48, 64), nn.ReLU(), nn.Dropout(0.1),
            nn.Linear(64, 32), nn.ReLU(),
            nn.Linear(32, 3),
        )
    def forward(self, x):
        return self.net(x)

def make_loaders(X, y, batch_size, seed):
    ds = TensorDataset(X, y)
    n_tr = int(0.8 * len(ds))
    tr, va = random_split(ds, [n_tr, len(ds) - n_tr], generator=torch.Generator().manual_seed(seed))
    train_loader = DataLoader(tr, batch_size=batch_size, shuffle=True,
                              generator=torch.Generator().manual_seed(seed))
    return train_loader, DataLoader(va, batch_size=batch_size)

def train(model, train_loader, epochs, lr):
    opt = torch.optim.AdamW(model.parameters(), lr=lr)
    loss_fn = nn.CrossEntropyLoss()
    history = []
    for _ in range(epochs):
        model.train()
        total, count = 0.0, 0
        for xb, yb in train_loader:
            opt.zero_grad()
            loss = loss_fn(model(xb), yb)
            loss.backward()
            opt.step()
            total += loss.item() * len(xb)
            count += len(xb)
        history.append(total / count)
    return history

@torch.no_grad()
def evaluate(model, loader):
    model.eval()
    correct = total = 0
    for xb, yb in loader:
        correct += (model(xb).argmax(1) == yb).sum().item()
        total += len(yb)
    return correct / total

def save_and_reload(model, path):
    torch.save(model.state_dict(), path)
    fresh = IMUNet()
    fresh.load_state_dict(torch.load(path, weights_only=True))
    return fresh
```

- **Logits out, loss handles the softmax.** The starter's softmax output fed to `CrossEntropyLoss` would double-apply the normalisation and badly weaken the gradients.
- **The five-step loop** (zero_grad → forward → loss → backward → step) is the core of every PyTorch training script. `model.train()` and `model.eval()` toggle dropout correctly, and `no_grad` keeps evaluation from building graphs.
- **Seeded generators** for both the split and the shuffling make runs reproducible.
- **`state_dict` checkpoints** contain only tensors, and loading with `weights_only=True` avoids executing arbitrary pickled code, which is the safe default for model files.
- An untrained loss near ln 3 ≈ 1.10 is the sanity check that the logits start out uninformative, as they should.
