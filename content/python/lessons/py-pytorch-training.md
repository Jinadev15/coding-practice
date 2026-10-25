# PyTorch Models and Training Loops

With tensors and autograd understood, real models are built from `torch.nn` modules, fed by `Dataset`/`DataLoader`, optimised by `torch.optim`, and trained in a loop you write yourself. Owning that loop is PyTorch's philosophy. This lesson builds the canonical training and evaluation loop: model definition, loss functions, optimisers, learning-rate schedules, train/eval modes, checkpointing, reproducibility, and the debugging habits that separate working models from mysteriously broken ones.

## 1. Defining a model with `nn.Module`

```python
import torch
from torch import nn

class MLP(nn.Module):
    def __init__(self, d_in, d_hidden, d_out, p_drop=0.1):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(d_in, d_hidden), nn.ReLU(), nn.Dropout(p_drop),
            nn.Linear(d_hidden, d_hidden), nn.ReLU(),
            nn.Linear(d_hidden, d_out),            # raw scores (logits): NO softmax here
        )

    def forward(self, x):
        return self.net(x)

model = MLP(8, 64, 3)
sum(p.numel() for p in model.parameters())         # parameter count
```

Assigning `nn.Module`s or `nn.Parameter`s as attributes **registers** them, so `model.parameters()`, `.to(device)`, `state_dict()` and `train()/eval()` all see them. Plain tensors stored as attributes aren't registered: use `register_buffer` for non-trainable state such as running statistics.

## 2. Data: `Dataset` and `DataLoader`

```python
from torch.utils.data import Dataset, DataLoader, TensorDataset, random_split

class SensorDataset(Dataset):
    def __init__(self, X, y):
        self.X = torch.as_tensor(X, dtype=torch.float32)
        self.y = torch.as_tensor(y, dtype=torch.long)
    def __len__(self):
        return len(self.X)
    def __getitem__(self, i):
        return self.X[i], self.y[i]

g = torch.Generator().manual_seed(0)
X = torch.randn(1000, 8); y = (X[:, 0] + X[:, 1] > 0).long() + (X[:, 2] > 1).long()
full = SensorDataset(X, y)
train_ds, val_ds = random_split(full, [800, 200], generator=g)
train_dl = DataLoader(train_ds, batch_size=64, shuffle=True, generator=g)
val_dl = DataLoader(val_ds, batch_size=256)
```

`num_workers > 0` loads batches in parallel worker processes (images, augmentations), and `pin_memory=True` speeds up host-to-GPU copies.

## 3. Loss functions

| Task | Loss | Model output |
|---|---|---|
| multi-class classification | `nn.CrossEntropyLoss` | **logits** (B, C); targets are class indices (B,) |
| binary / multi-label | `nn.BCEWithLogitsLoss` | logits; targets in {0, 1} as float |
| regression | `nn.MSELoss`, `nn.L1Loss`, `nn.SmoothL1Loss` (Huber) | values |

> [!WARNING]
> `CrossEntropyLoss` applies log-softmax internally. Feeding it probabilities (softmax outputs) is a silent bug that slows or ruins training. Likewise, use `BCEWithLogitsLoss` rather than `Sigmoid` + `BCELoss`, which is numerically more stable.

## 4. The training loop

```python
def train_one_epoch(model, loader, loss_fn, opt, device):
    model.train()                                    # enables dropout and batch-norm updates
    total, correct, loss_sum = 0, 0, 0.0
    for xb, yb in loader:
        xb, yb = xb.to(device), yb.to(device)
        opt.zero_grad(set_to_none=True)              # 1. reset gradients
        logits = model(xb)                           # 2. forward
        loss = loss_fn(logits, yb)                   # 3. loss
        loss.backward()                              # 4. backward
        nn.utils.clip_grad_norm_(model.parameters(), 1.0)   # optional: stabilise
        opt.step()                                   # 5. update
        loss_sum += loss.item() * len(xb)
        correct += (logits.argmax(1) == yb).sum().item()
        total += len(xb)
    return loss_sum / total, correct / total

@torch.no_grad()
def evaluate(model, loader, loss_fn, device):
    model.eval()                                     # disables dropout, uses running BN statistics
    total, correct, loss_sum = 0, 0, 0.0
    for xb, yb in loader:
        xb, yb = xb.to(device), yb.to(device)
        logits = model(xb)
        loss_sum += loss_fn(logits, yb).item() * len(xb)
        correct += (logits.argmax(1) == yb).sum().item()
        total += len(xb)
    return loss_sum / total, correct / total

torch.manual_seed(0)
device = "cpu"
model = MLP(8, 64, 3).to(device)
opt = torch.optim.AdamW(model.parameters(), lr=3e-3, weight_decay=1e-4)
sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=20)
loss_fn = nn.CrossEntropyLoss()
for epoch in range(20):
    tr_loss, tr_acc = train_one_epoch(model, train_dl, loss_fn, opt, device)
    va_loss, va_acc = evaluate(model, val_dl, loss_fn, device)
    sched.step()
```

> [!KEY]
> The five-step heartbeat is **zero_grad → forward → loss → backward → step**. Call `model.train()` before training and `model.eval()` + `torch.no_grad()` for validation. Forgetting `eval()` leaves dropout active and batch norm updating, which makes validation noisy and wrong.

## 5. Optimisers and schedules

| Optimiser | Notes |
|---|---|
| `SGD(momentum=0.9, nesterov=True)` | strong for vision with a good schedule; needs tuning |
| `Adam` | adaptive per-parameter rates; a robust default |
| `AdamW` | Adam with *decoupled* weight decay; the standard for transformers |

Learning-rate schedules: warm-up followed by cosine decay is the modern default. `OneCycleLR` is good for fast training, and `ReduceLROnPlateau` reacts to the validation loss.

## 6. Checkpointing and reproducibility

```python
torch.save({"model": model.state_dict(), "opt": opt.state_dict(), "epoch": epoch}, "ckpt.pt")
ckpt = torch.load("ckpt.pt", weights_only=True)      # weights_only: safe loading (no arbitrary pickle code)
model.load_state_dict(ckpt["model"]); opt.load_state_dict(ckpt["opt"])
```

For reproducibility:
- seed Python, NumPy and torch (`torch.manual_seed`), and seed the DataLoader generators
- use `torch.use_deterministic_algorithms(True)` where it's supported
- record versions and configs

Bit-exact results across hardware aren't guaranteed.

For deployment, export with `torch.export` / ONNX for C++ or TensorRT inference on a robot, or use TorchScript in legacy code.

## 7. Debugging a model that won't learn

1. **Overfit a single batch first.** If the loss can't reach about 0 on 32 samples, there's a bug (wrong labels, wrong loss, data not matching targets, the learning rate).
2. Check shapes and dtypes at each stage (`CrossEntropyLoss` wants `long` targets of shape (B,)).
3. Check the initial loss: for C balanced classes it should be about ln(C) (≈ 1.0986 for 3).
4. Plot training versus validation loss: overfitting, underfitting, or divergence (lower the learning rate, clip gradients).
5. Normalise the inputs, and verify the augmentations are correct.
6. Watch for NaNs with `torch.autograd.set_detect_anomaly(True)` (slow; debug only).

## 8. Exam-ready answers

> [!EXAM]
> **The PyTorch training loop.** A model is defined as a subclass of `nn.Module` whose submodules and parameters are registered automatically; data is served in mini-batches by a `DataLoader` over a `Dataset`. Each training iteration clears accumulated gradients (`optimizer.zero_grad()`), computes the forward pass and a loss, back-propagates with `loss.backward()` to populate parameter gradients, and updates parameters with `optimizer.step()`, optionally adjusting the learning rate with a scheduler. `model.train()` and `model.eval()` switch the behaviour of layers such as dropout and batch normalisation, and evaluation runs under `torch.no_grad()` to avoid building computational graphs. Model and optimiser state dictionaries are saved for checkpointing and resumption.

## 9. Cheat sheet

| Need | Code |
|---|---|
| model | subclass `nn.Module`, define `forward` |
| batches | `DataLoader(ds, batch_size, shuffle=True)` |
| classification loss | `nn.CrossEntropyLoss()` on logits |
| optimiser | `torch.optim.AdamW(model.parameters(), lr, weight_decay)` |
| heartbeat | `zero_grad`, forward, loss, `backward`, `step` |
| modes | `model.train()` / `model.eval()` + `torch.no_grad()` |
| save/load | `torch.save(model.state_dict())`, `load_state_dict`, `weights_only=True` |
| sanity check | overfit one batch; initial loss ≈ ln(C) |

> [!INTERVIEW]
> **"Training loss decreases but validation accuracy is stuck at chance. What do you check?"** In order:
> - Is `model.eval()` called during validation?
> - Are the validation data preprocessed exactly like the training data (normalisation statistics, channel order)?
> - Do the label mappings match between splits?
> - Is there data leakage, or a split that puts all of one class on one side?
> - Is the model memorising (too little data, no regularisation)? Look at the gap between training and validation loss.
>
> Then overfit a single batch, and evaluate the model on a few *training* samples in eval mode, which isolates mode-related bugs.
