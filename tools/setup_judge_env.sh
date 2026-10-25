#!/usr/bin/env bash
# Creates/updates the isolated Python environment the judge uses for Python submissions.
# PyTorch comes from the CPU-only wheel index (no CUDA download).
set -euo pipefail
cd "$(dirname "$0")/.."
UV=${UV:-$(command -v uv || echo /snap/bin/uv)}
# --system-site-packages: ROS 2 (apt) relies on Debian python modules (empy, yaml, lark, ...).
# Packages installed in the venv still take precedence over the system ones.
# Problems target Python 3.14 (e.g. deferred annotations). Use the system python3 if it is new enough,
# otherwise let uv download a private 3.14 (no admin rights needed).
PY=$(command -v python3 || true)
if [ -z "$PY" ] || ! "$PY" -c 'import sys; sys.exit(sys.version_info < (3, 14))'; then
    "$UV" python install 3.14
    PY=$("$UV" python find 3.14)
fi
"$UV" venv --python "$PY" --system-site-packages .venv-judge --allow-existing
"$UV" pip install --python .venv-judge/bin/python \
    --index-url https://pypi.org/simple \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    --index-strategy unsafe-best-match \
    -r requirements-judge.txt
# ROS 2 (if installed under /opt/ros): expose rclpy & messages to the venv and record the runtime env.
ROS_SETUP=$(ls -d /opt/ros/*/setup.bash 2>/dev/null | tail -n 1 || true)
if [ -n "$ROS_SETUP" ]; then
    SITE=$(.venv-judge/bin/python -c "import sysconfig; print(sysconfig.get_paths()['purelib'])")
    bash -c "source '$ROS_SETUP' >/dev/null 2>&1 && echo \"\$PYTHONPATH\" | tr ':' '\n'" > "$SITE/ros2.pth"
    bash -c "source '$ROS_SETUP' >/dev/null 2>&1 && .venv-judge/bin/python -c '
import json, os
keys = [\"LD_LIBRARY_PATH\", \"AMENT_PREFIX_PATH\", \"ROS_DISTRO\", \"ROS_VERSION\", \"ROS_PYTHON_VERSION\", \"RMW_IMPLEMENTATION\"]
env = {k: os.environ[k] for k in keys if k in os.environ}
env[\"ROS_AUTOMATIC_DISCOVERY_RANGE\"] = \"LOCALHOST\"
json.dump(env, open(\".venv-judge/judge_env.json\", \"w\"), indent=2)
'"
    echo "ROS 2 wired in from $ROS_SETUP"
fi
.venv-judge/bin/python - <<'PY'
import numpy, pandas, scipy, sklearn, torch, cv2, matplotlib
print("judge env ready:", "numpy", numpy.__version__, "| sklearn", sklearn.__version__,
      "| torch", torch.__version__, "| cv2", cv2.__version__)
PY
