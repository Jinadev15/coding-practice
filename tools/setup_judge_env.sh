#!/usr/bin/env bash
# Creates/updates the isolated Python environment the judge uses for Python submissions.
# PyTorch comes from the CPU-only wheel index (no CUDA download).
set -euo pipefail
cd "$(dirname "$0")/.."
UV=${UV:-$(command -v uv || echo /snap/bin/uv)}
"$UV" venv --python "$(command -v python3)" .venv-judge --allow-existing
"$UV" pip install --python .venv-judge/bin/python \
    --index-url https://pypi.org/simple \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    --index-strategy unsafe-best-match \
    -r requirements-judge.txt
.venv-judge/bin/python - <<'PY'
import numpy, pandas, scipy, sklearn, torch, cv2, matplotlib
print("judge env ready:", "numpy", numpy.__version__, "| sklearn", sklearn.__version__,
      "| torch", torch.__version__, "| cv2", cv2.__version__)
PY
