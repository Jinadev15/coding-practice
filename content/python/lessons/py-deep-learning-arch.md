# Deep Learning Architectures: CNN, RNN, Transformer

Architectures encode **assumptions about the data**:
- Convolutional networks assume locality and translation equivariance, which suits images, occupancy grids and spectrograms.
- Recurrent networks assume sequential state, which suits time series and control.
- Transformers assume little, using **attention** to let every element look at every other. Given enough data, they now dominate language, vision (ViT), robotics policies (RT-2, diffusion and transformer policies) and multimodal models.

This lesson explains each architecture's mechanism, implements the key pieces in PyTorch (including scaled dot-product attention from scratch), and shows how to choose among them.

## 1. Why architecture matters: inductive bias

A fully connected layer on a 224 × 224 × 3 image needs 150 528 weights *per neuron* and ignores the fact that nearby pixels are related. Building in the right structure (weight sharing, locality, recurrence, attention) reduces the parameter count, improves generalisation, and makes training feasible.

## 2. Convolutional neural networks

A 2-D convolution slides a small learned kernel over the input, computing a dot product at each position. The same weights are used everywhere (**weight sharing**), so the output shifts when the input shifts (**translation equivariance**).

Output size per spatial dimension: **out = ⌊(in + 2·padding − dilation·(k − 1) − 1) / stride⌋ + 1**

```python
import torch
from torch import nn

x = torch.randn(8, 3, 64, 64)                     # (batch, channels, height, width): NCHW
conv = nn.Conv2d(in_channels=3, out_channels=16, kernel_size=3, stride=1, padding=1)
conv(x).shape                                     # (8, 16, 64, 64): "same" padding keeps the size
nn.Conv2d(3, 16, 3, stride=2, padding=1)(x).shape # (8, 16, 32, 32): stride 2 halves it
sum(p.numel() for p in conv.parameters())         # 16*3*3*3 + 16 = 448 parameters

class SmallCNN(nn.Module):
    def __init__(self, n_classes=10):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, 3, padding=1), nn.BatchNorm2d(32), nn.ReLU(), nn.MaxPool2d(2),   # 64 → 32
            nn.Conv2d(32, 64, 3, padding=1), nn.BatchNorm2d(64), nn.ReLU(), nn.MaxPool2d(2),  # 32 → 16
            nn.Conv2d(64, 128, 3, padding=1), nn.BatchNorm2d(128), nn.ReLU(),
            nn.AdaptiveAvgPool2d(1),                                                          # → (B, 128, 1, 1)
        )
        self.head = nn.Linear(128, n_classes)
    def forward(self, x):
        return self.head(self.features(x).flatten(1))

SmallCNN()(x).shape                               # (8, 10)
```

Key ideas:
- The **receptive field** grows with depth: deep layers see large regions and detect objects, while early layers detect edges.
- **Pooling and strides** downsample, trading resolution for context.
- **Batch normalisation** stabilises training.
- **Residual connections** (ResNet: `y = x + F(x)`) let gradients flow through 100+ layers.
- Variants include depthwise-separable convolutions (MobileNet, fast on robots), dilated convolutions (large context without downsampling), U-Net encoder–decoders for segmentation, and 3-D/sparse convolutions for voxels and point clouds.

## 3. Recurrent networks

An RNN processes a sequence step by step, carrying a hidden state: hₜ = tanh(W_x xₜ + W_h hₜ₋₁ + b). Plain RNNs suffer from **vanishing/exploding gradients** over long sequences. **LSTM** and **GRU** add gates that control what to remember and forget, which preserves long-range information.

```python
lstm = nn.LSTM(input_size=6, hidden_size=32, num_layers=2, batch_first=True)
imu = torch.randn(4, 100, 6)                      # (batch, time, features): 100 IMU samples
out, (h, c) = lstm(imu)
out.shape, h.shape                                # (4, 100, 32) all steps; (2, 4, 32) final state per layer
pred = nn.Linear(32, 3)(out[:, -1])               # e.g. classify the motion from the last step
```

RNNs are natural for streaming data: they process one step at a time with constant memory, so they suit online state estimation and control loops. Their weakness is sequential computation (no parallelism over time) and difficulty with very long contexts, which is where transformers took over.

## 4. Attention and the transformer

**Scaled dot-product attention**: queries Q, keys K and values V (projections of the inputs):

**Attention(Q, K, V) = softmax(QKᵀ / √d_k) V**

Each output is a weighted average of the values, with weights given by query–key similarity. Dividing by √d_k keeps the dot products from growing with the dimension and saturating the softmax.

```python
import math

def attention(q, k, v, mask=None):
    """q: (..., Lq, d), k: (..., Lk, d), v: (..., Lk, dv). mask: True = keep."""
    scores = q @ k.transpose(-2, -1) / math.sqrt(q.shape[-1])     # (..., Lq, Lk)
    if mask is not None:
        scores = scores.masked_fill(~mask, float("-inf"))
    weights = scores.softmax(dim=-1)
    return weights @ v, weights

q = k = v = torch.randn(2, 5, 16)
out, w = attention(q, k, v)
causal = torch.tril(torch.ones(5, 5, dtype=torch.bool))          # step t sees only steps <= t
out_c, w_c = attention(q, k, v, causal)
torch.allclose(out_c, nn.functional.scaled_dot_product_attention(q, k, v, is_causal=True), atol=1e-5)   # True
```

### Multi-head attention and the transformer block

Several heads attend in parallel to different subspaces. Their outputs are concatenated and projected:

```python
class TransformerBlock(nn.Module):
    def __init__(self, d_model=64, n_heads=4, d_ff=256, p=0.1):
        super().__init__()
        self.attn = nn.MultiheadAttention(d_model, n_heads, dropout=p, batch_first=True)
        self.ff = nn.Sequential(nn.Linear(d_model, d_ff), nn.GELU(), nn.Linear(d_ff, d_model))
        self.n1, self.n2 = nn.LayerNorm(d_model), nn.LayerNorm(d_model)
        self.drop = nn.Dropout(p)
    def forward(self, x, attn_mask=None):
        h = self.n1(x)                                             # pre-norm (stable for deep stacks)
        a, _ = self.attn(h, h, h, attn_mask=attn_mask, need_weights=False)
        x = x + self.drop(a)                                       # residual
        x = x + self.drop(self.ff(self.n2(x)))                     # position-wise feed-forward + residual
        return x

tokens = torch.randn(2, 10, 64)
TransformerBlock()(tokens).shape                                   # (2, 10, 64)
```

Attention is **permutation-invariant**, so order must be injected with **positional encodings**: sinusoidal, learned, or rotary (RoPE).

| Architecture | Parallel over sequence | Cost in length L | Long-range |
|---|---|---|---|
| RNN/LSTM | no | O(L) | weak |
| CNN (1-D) | yes | O(L·k) | needs depth/dilation |
| Transformer | yes | **O(L²)** attention | direct, any distance |

The quadratic cost motivates efficient variants: FlashAttention (exact, memory-efficient kernels), sliding-window and sparse attention, linear attention, and state-space models (Mamba).

**Families**:
- encoder-only (BERT) for understanding
- decoder-only with causal masks (GPT) for generation
- encoder–decoder (T5, the original translation transformer)
- ViT: images split into 16 × 16 patches treated as tokens
- robotics transformers: tokenised observations and actions (RT-1/2, ACT, diffusion policies)

## 5. Choosing an architecture

| Data | First choice |
|---|---|
| images, grid maps, depth images | CNN (ResNet/EfficientNet/MobileNet); ViT with lots of data or pretraining |
| short time series, streaming control | GRU/LSTM, or a temporal CNN |
| long sequences, multimodal, plenty of data | transformer |
| point clouds | PointNet/PointNet++, sparse 3-D convolutions, point transformers |
| graphs (molecules, scene graphs) | graph neural networks |
| small tabular data | gradient boosting, not deep learning |

## 6. Exam-ready answers

> [!EXAM]
> **Self-attention.** Self-attention computes, for each element of a sequence, a weighted combination of all elements' value vectors, with weights obtained from the softmax of scaled dot products between that element's query vector and every element's key vector: Attention(Q, K, V) = softmax(QKᵀ/√dₖ)V, where Q, K and V are learned linear projections of the input. Scaling by √dₖ prevents large dot products from saturating the softmax. Multi-head attention runs several attention operations on different learned projections in parallel and concatenates them. Transformers stack self-attention and position-wise feed-forward layers with residual connections and layer normalisation, add positional encodings because attention is permutation-invariant, and use causal masks in decoders; they process all positions in parallel at O(L²) cost in sequence length.

> [!EXAM]
> **Convolutional layers.** A convolutional layer applies a set of learned kernels across the spatial extent of its input, computing local weighted sums at every position with the same weights. This weight sharing drastically reduces parameters compared with fully connected layers and makes the layer translation-equivariant, while locality matches the spatial correlation structure of images. Stacking convolutions with nonlinearities and downsampling (pooling or strides) builds hierarchical features with growing receptive fields; residual connections enable very deep networks by easing gradient flow.

## 7. Cheat sheet

| Need | PyTorch |
|---|---|
| conv output size | ⌊(n + 2p − d(k−1) − 1)/s⌋ + 1 |
| 2-D conv | `nn.Conv2d(cin, cout, k, stride, padding)` on NCHW |
| global pooling | `nn.AdaptiveAvgPool2d(1)` |
| sequence model | `nn.LSTM(..., batch_first=True)` / `nn.GRU` |
| attention | `F.scaled_dot_product_attention(q, k, v, is_causal=...)` |
| multi-head | `nn.MultiheadAttention(d, h, batch_first=True)` |
| transformer stack | `nn.TransformerEncoder(nn.TransformerEncoderLayer(...), n)` |
| causal mask | `torch.tril(torch.ones(L, L, dtype=torch.bool))` |

> [!INTERVIEW]
> **"Why divide by √dₖ in attention?"** If the components of q and k are independent with zero mean and unit variance, their dot product has variance dₖ. For large dₖ, the logits become large in magnitude, the softmax saturates towards one-hot, and its gradients vanish. Scaling by √dₖ restores unit variance, so training stays well conditioned. Follow-up: attention is O(L²) in memory and time, and FlashAttention computes the same result exactly by tiling to avoid materialising the L × L matrix.
