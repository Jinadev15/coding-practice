---
id: py-autograd-workbench
title: "Autograd Workbench: Gradients, Manipulator Jacobians, Fitting"
difficulty: Hard
order: 1
tags: pytorch, autograd, backward, torch.func, jacobian, gradient descent
time_limit: 12
---
## Statement
Use PyTorch's automatic differentiation (no hand-derived derivatives) for four tasks:

```python
def gradient_at(f, x):
    """f maps a 1-D float tensor to a scalar tensor. Return df/dx at x (a new tensor, x unchanged)
    using requires_grad + backward."""

def arm_fk(q, l1=1.0, l2=0.8):
    """Planar 2-link arm: end-effector (x, y) for joint angles q = [q1, q2] (radians), as a tensor of shape (2,):
    x = l1 cos q1 + l2 cos(q1+q2), y = l1 sin q1 + l2 sin(q1+q2). Must be differentiable."""

def arm_jacobian(q):
    """2x2 Jacobian d(x, y)/d(q1, q2) of arm_fk at q, computed with torch.func.jacrev (or autograd)."""

def fit_plane(points, steps=500, lr=0.1):
    """points (n, 3): fit z = a*x + b*y + c by gradient descent on mean squared error with torch.optim.SGD,
    parameters initialised to zeros. Return (a, b, c) as Python floats."""
```

The driver checks the results against analytic values, checks that `gradient_at` doesn't leave gradients behind on the caller's tensor, and runs the fit on noisy data.

## Starter
```python
import torch

def gradient_at(f, x):
    eps = 1e-3
    return torch.stack([(f(x + eps * e) - f(x - eps * e)) / (2 * eps) for e in torch.eye(len(x))])

def arm_fk(q, l1=1.0, l2=0.8):
    return torch.tensor([l1 * float(torch.cos(q[0])), l1 * float(torch.sin(q[0]))])

def arm_jacobian(q):
    return torch.zeros(2, 2)

def fit_plane(points, steps=500, lr=0.1):
    return 0.0, 0.0, 0.0
```

## Driver
```python
import math
import sys
import torch

torch.manual_seed(0)
torch.set_num_threads(1)

def r(t, d=4):
    return [round(float(v), d) + 0.0 for v in torch.as_tensor(t).flatten()]

for cmd in sys.stdin.read().split():
    if cmd == "grad":
        x = torch.tensor([1.0, -2.0, 0.5])
        g = gradient_at(lambda v: (v ** 3).sum() + v[0] * v[1], x)
        print("grad:", r(g), "| caller grad untouched:", x.grad is None and not x.requires_grad)
        g2 = gradient_at(lambda v: torch.log(1 + torch.exp(v)).sum(), torch.tensor([0.0, 2.0]))
        print("softplus grad:", r(g2))
    elif cmd == "arm":
        q = torch.tensor([math.pi / 4, math.pi / 3])
        p = arm_fk(q)
        print("fk:", r(p), "differentiable:", p.requires_grad or arm_fk(q.clone().requires_grad_()).requires_grad)
        J = arm_jacobian(q)
        q1, q2 = q.tolist()
        Ja = torch.tensor([[-math.sin(q1) - 0.8 * math.sin(q1 + q2), -0.8 * math.sin(q1 + q2)],
                           [math.cos(q1) + 0.8 * math.cos(q1 + q2), 0.8 * math.cos(q1 + q2)]])
        print("jacobian:", r(J), "matches analytic:", torch.allclose(J, Ja, atol=1e-5))
        print("singular at q2=0:", abs(float(torch.det(arm_jacobian(torch.tensor([0.3, 0.0])))) ) < 1e-6)
    elif cmd == "fit":
        g = torch.Generator().manual_seed(1)
        xy = torch.rand(400, 2, generator=g) * 2 - 1
        z = 1.5 * xy[:, 0] - 0.75 * xy[:, 1] + 0.3 + 0.01 * torch.randn(400, generator=g)
        a, b, c = fit_plane(torch.cat([xy, z[:, None]], 1), steps=600, lr=0.2)
        print("plane:", round(a, 2), round(b, 2), round(c, 2), "| floats:", all(isinstance(v, float) for v in (a, b, c)))
```

## Tests
=== sample
grad
arm
---
grad: [1.0, 13.0, 0.75] | caller grad untouched: True
softplus grad: [0.5, 0.8808]
fk: [0.5001, 1.4798] differentiable: True
jacobian: [-1.4798, -0.7727, 0.5001, -0.2071] matches analytic: True
singular at q2=0: True
=== hidden
fit
arm
grad
---
plane: 1.5 -0.75 0.3 | floats: True
fk: [0.5001, 1.4798] differentiable: True
jacobian: [-1.4798, -0.7727, 0.5001, -0.2071] matches analytic: True
singular at q2=0: True
grad: [1.0, 13.0, 0.75] | caller grad untouched: True
softplus grad: [0.5, 0.8808]

## Hints
- `gradient_at`: `xx = x.detach().clone().requires_grad_(True)`; `f(xx).backward()`; `return xx.grad`. Working on a detached clone keeps the caller's tensor clean.
- `arm_fk` must build the output from torch operations (`torch.cos`, `torch.stack`), not floats. Converting with `float()` breaks the graph.
- `torch.func.jacrev(arm_fk)(q)` gives the 2×2 Jacobian. The determinant is l1·l2·sin(q2), which is zero when the arm is straight (a kinematic singularity).
- `fit_plane`: `params = torch.zeros(3, requires_grad=True)`; `opt = torch.optim.SGD([params], lr=lr)`; loop zero_grad → loss → backward → step; return `params.tolist()`.

## Solution
```python
import torch
from torch.func import jacrev

def gradient_at(f, x):
    xx = x.detach().clone().requires_grad_(True)
    f(xx).backward()
    return xx.grad.detach()

def arm_fk(q, l1=1.0, l2=0.8):
    q1, q2 = q[0], q[1]
    x = l1 * torch.cos(q1) + l2 * torch.cos(q1 + q2)
    y = l1 * torch.sin(q1) + l2 * torch.sin(q1 + q2)
    return torch.stack([x, y])

def arm_jacobian(q):
    return jacrev(arm_fk)(q)

def fit_plane(points, steps=500, lr=0.1):
    X = torch.cat([points[:, :2], torch.ones(len(points), 1)], dim=1)
    z = points[:, 2]
    params = torch.zeros(3, requires_grad=True)
    opt = torch.optim.SGD([params], lr=lr)
    for _ in range(steps):
        opt.zero_grad()
        loss = ((X @ params - z) ** 2).mean()
        loss.backward()
        opt.step()
    a, b, c = params.detach().tolist()
    return float(a), float(b), float(c)
```

- **`backward` on a detached clone** computes exact gradients (no finite-difference error) without touching the caller's tensor or leaving gradients behind.
- **Differentiable forward kinematics** is just ordinary maths written with torch operations. `jacrev` then produces the manipulator Jacobian automatically, the same matrix used for velocity control (ẋ = J q̇), inverse kinematics and singularity analysis. det J = l1·l2·sin q2 vanishes when the arm is fully stretched.
- **Optimiser-driven fitting** follows the standard heartbeat (zero_grad → loss → backward → step). Replace the plane with any differentiable model, a camera calibration or a dynamics model, and the loop stays the same.
