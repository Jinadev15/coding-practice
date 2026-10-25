---
id: py-attention-from-scratch
title: Attention and Convolution Shapes from Scratch
difficulty: Hard
order: 1
tags: attention, multi-head attention, causal mask, convolution arithmetic, transformer
time_limit: 12
---
## Statement
Implement the core transformer and CNN mechanics yourself. The driver compares them against PyTorch's built-ins.

```python
def conv_out_size(n, k, stride=1, padding=0, dilation=1):
    """Output length of a convolution along one dimension."""

def scaled_dot_attention(q, k, v, causal=False):
    """q (..., Lq, d), k (..., Lk, d), v (..., Lk, dv). softmax(q k^T / sqrt(d)) v; with causal=True,
    position i may only attend to positions <= i (Lq == Lk). Return (output, weights).
    Don't call F.scaled_dot_product_attention or nn.MultiheadAttention."""

def multi_head_attention(x, Wq, Wk, Wv, Wo, n_heads, causal=False):
    """Self-attention on x (B, L, D) with projection matrices Wq, Wk, Wv, Wo of shape (D, D)
    (y = x @ W). Split D into n_heads heads of size D/n_heads, attend per head (your function above),
    concatenate the heads and project with Wo. Return (B, L, D)."""

def sinusoidal_positions(L, D):
    """PE[pos, 2i] = sin(pos / 10000^(2i/D)), PE[pos, 2i+1] = cos(pos / 10000^(2i/D)); shape (L, D), D even."""
```

## Starter
```python
import torch

def conv_out_size(n, k, stride=1, padding=0, dilation=1):
    return n - k + 1

def scaled_dot_attention(q, k, v, causal=False):
    w = torch.softmax(q @ k.transpose(-2, -1), dim=-1)
    return w @ v, w

def multi_head_attention(x, Wq, Wk, Wv, Wo, n_heads, causal=False):
    out, _ = scaled_dot_attention(x @ Wq, x @ Wk, x @ Wv, causal)
    return out @ Wo

def sinusoidal_positions(L, D):
    return torch.zeros(L, D)
```

## Driver
```python
import math
import sys
import torch
import torch.nn.functional as F

torch.manual_seed(0)
torch.set_num_threads(1)
for cmd in sys.stdin.read().split():
    if cmd == "conv":
        cases = [(64, 3, 1, 1, 1), (64, 3, 2, 1, 1), (32, 5, 1, 0, 1), (100, 3, 1, 2, 2), (7, 7, 1, 0, 1), (224, 7, 2, 3, 1)]
        mine = [conv_out_size(*c) for c in cases]
        ref = [torch.nn.Conv1d(1, 1, c[1], stride=c[2], padding=c[3], dilation=c[4])(torch.zeros(1, 1, c[0])).shape[-1] for c in cases]
        print("conv sizes:", mine, "match torch:", mine == ref)
    elif cmd == "attn":
        q, k, v = torch.randn(2, 3, 6, 8), torch.randn(2, 3, 6, 8), torch.randn(2, 3, 6, 5)
        for causal in (False, True):
            out, w = scaled_dot_attention(q, k, v, causal)
            ref = F.scaled_dot_product_attention(q, k, v, is_causal=causal)
            print(f"causal={causal}: shape={tuple(out.shape)} match={torch.allclose(out, ref, atol=1e-5)} "
                  f"rows_sum_to_1={torch.allclose(w.sum(-1), torch.ones(2, 3, 6))} "
                  f"future_weight={float(w[..., 0, 1:].abs().sum()):.1f}" if causal else
                  f"causal={causal}: shape={tuple(out.shape)} match={torch.allclose(out, ref, atol=1e-5)} "
                  f"rows_sum_to_1={torch.allclose(w.sum(-1), torch.ones(2, 3, 6))}")
        big = torch.randn(1, 1, 4, 512) * 30                        # large logits: softmax must stay finite
        o, w = scaled_dot_attention(big, big, big)
        print("large inputs finite:", bool(torch.isfinite(o).all()))
    elif cmd == "mha":
        B, L, D, H = 2, 7, 16, 4
        mha = torch.nn.MultiheadAttention(D, H, bias=False, batch_first=True)
        Wq, Wk, Wv = mha.in_proj_weight.detach().chunk(3)
        Wo = mha.out_proj.weight.detach()
        x = torch.randn(B, L, D)
        for causal in (False, True):
            mask = torch.triu(torch.ones(L, L, dtype=torch.bool), 1) if causal else None
            ref, _ = mha(x, x, x, attn_mask=mask, need_weights=False)
            mine = multi_head_attention(x, Wq.T, Wk.T, Wv.T, Wo.T, H, causal)
            print(f"mha causal={causal}: shape={tuple(mine.shape)} match={torch.allclose(mine, ref, atol=1e-5)}")
    elif cmd == "pos":
        pe = sinusoidal_positions(50, 16)
        print("pos shape:", tuple(pe.shape), "pe[0]:", [round(float(v), 4) for v in pe[0, :4]],
              "pe[1,0..1]:", [round(float(v), 4) for v in pe[1, :2]], "bounded:", bool((pe.abs() <= 1).all()))
```

## Tests
=== sample
conv
attn
---
conv sizes: [64, 32, 28, 100, 1, 112] match torch: True
causal=False: shape=(2, 3, 6, 5) match=True rows_sum_to_1=True
causal=True: shape=(2, 3, 6, 5) match=True rows_sum_to_1=True future_weight=0.0
large inputs finite: True
=== hidden
mha
pos
attn
---
mha causal=False: shape=(2, 7, 16) match=True
mha causal=True: shape=(2, 7, 16) match=True
pos shape: (50, 16) pe[0]: [0.0, 1.0, 0.0, 1.0] pe[1,0..1]: [0.8415, 0.5403] bounded: True
causal=False: shape=(2, 3, 6, 5) match=True rows_sum_to_1=True
causal=True: shape=(2, 3, 6, 5) match=True rows_sum_to_1=True future_weight=0.0
large inputs finite: True

## Hints
- Conv: `⌊(n + 2·padding − dilation·(k − 1) − 1) / stride⌋ + 1`.
- Attention: `scores = q @ k.transpose(-2, -1) / math.sqrt(d)`. For causal masking, `scores.masked_fill(torch.triu(torch.ones(L, L, dtype=torch.bool), 1), float("-inf"))`. `torch.softmax` subtracts the maximum internally, so large logits stay finite.
- Multi-head: `(B, L, D) → (B, L, H, D/H) → transpose → (B, H, L, D/H)`, attend, transpose back, `reshape(B, L, D)`, then `@ Wo`.
- Positions: `div = 10000 ** (torch.arange(0, D, 2) / D)`; `pe[:, 0::2] = sin(pos / div)`, `pe[:, 1::2] = cos(pos / div)`.

## Solution
```python
import math
import torch

def conv_out_size(n, k, stride=1, padding=0, dilation=1):
    return (n + 2 * padding - dilation * (k - 1) - 1) // stride + 1

def scaled_dot_attention(q, k, v, causal=False):
    d = q.shape[-1]
    scores = q @ k.transpose(-2, -1) / math.sqrt(d)
    if causal:
        L = scores.shape[-1]
        future = torch.triu(torch.ones(L, L, dtype=torch.bool, device=q.device), diagonal=1)
        scores = scores.masked_fill(future, float("-inf"))
    weights = torch.softmax(scores, dim=-1)
    return weights @ v, weights

def multi_head_attention(x, Wq, Wk, Wv, Wo, n_heads, causal=False):
    B, L, D = x.shape
    hd = D // n_heads
    def split(t):                                   # (B, L, D) -> (B, H, L, hd)
        return t.reshape(B, L, n_heads, hd).transpose(1, 2)
    out, _ = scaled_dot_attention(split(x @ Wq), split(x @ Wk), split(x @ Wv), causal)
    out = out.transpose(1, 2).reshape(B, L, D)      # concatenate the heads
    return out @ Wo

def sinusoidal_positions(L, D):
    pos = torch.arange(L, dtype=torch.float32)[:, None]
    div = 10000 ** (torch.arange(0, D, 2, dtype=torch.float32) / D)
    pe = torch.zeros(L, D)
    pe[:, 0::2] = torch.sin(pos / div)
    pe[:, 1::2] = torch.cos(pos / div)
    return pe
```

- **Scaling by √d** keeps the logits' variance near 1, so the softmax neither saturates nor kills the gradients. The starter's unscaled version gives different, sharper weights.
- **Causal masking** sets the scores of future positions to −∞ before the softmax, so they get exactly zero weight. That's what lets a decoder be trained on whole sequences in parallel while staying autoregressive.
- **Multi-head attention** is the same operation run on D/H-dimensional slices. Reshaping to (B, H, L, D/H) lets one batched matmul handle all heads, which is precisely what `nn.MultiheadAttention` does internally (here without biases).
- **Sinusoidal encodings** give each position a unique, bounded signature, with frequencies forming a geometric progression, so relative offsets correspond to rotations that the model can learn to read.
- **Convolution arithmetic** must match the framework exactly, or decoder skip connections and flatten sizes break.
