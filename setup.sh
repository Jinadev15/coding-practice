#!/usr/bin/env bash
# One-command setup for Coding Practice on your own laptop.
#
#   ./setup.sh             everything: compilers, C++ libraries, Python science/AI environment
#   ./setup.sh --minimal   just enough for the core Python, C and C++ topics (no NumPy/PyTorch/OpenCV/Eigen...)
#
# Works on Ubuntu/Debian (including WSL on Windows), Fedora, Arch and macOS (Homebrew).
# Only missing system packages are installed (that step asks for your password via sudo).
# Safe to run again at any time, e.g. after `git pull`.
set -euo pipefail
cd "$(dirname "$0")"

MINIMAL=0
[ "${1:-}" = "--minimal" ] && MINIMAL=1

bold() { printf '\n\033[1m%s\033[0m\n' "$*"; }
ok()   { printf '  \033[32m✓\033[0m %s\n' "$*"; }
warn() { printf '  \033[33m!\033[0m %s\n' "$*"; }
die()  { printf '\n\033[31m✗ %s\033[0m\n' "$*"; exit 1; }

# ------------------------------------------------------------------ 1. system packages
bold "1/4  System packages"
OS=$(uname -s)
if [ "$OS" = "Darwin" ]; then PM=brew
elif command -v apt-get >/dev/null; then PM=apt
elif command -v dnf >/dev/null; then PM=dnf
elif command -v pacman >/dev/null; then PM=pacman
else PM=none; fi

# command or pkg-config module to test  |  package name per manager: apt dnf pacman brew
CORE=(
  "cmd:gcc|build-essential|gcc|base-devel|gcc"
  "cmd:g++|build-essential|gcc-c++|base-devel|gcc"
  "cmd:make|build-essential|make|base-devel|make"
  "cmd:pkg-config|pkg-config|pkgconf-pkg-config|pkgconf|pkg-config"
  "cmd:python3|python3|python3|python|python@3.14"
  "cmd:curl|curl|curl|curl|curl"
  "cmd:git|git|git|git|git"
)
LIBS=(
  "pc:eigen3|libeigen3-dev|eigen3-devel|eigen|eigen"
  "pc:opencv4|libopencv-dev|opencv-devel|opencv|opencv"
  "pc:gtest_main|libgtest-dev|gtest-devel|gtest|googletest"
  "pc:gmock_main|libgmock-dev|gmock-devel|gtest|googletest"
  "pc:fmt|libfmt-dev|fmt-devel|fmt|fmt"
  "pc:spdlog|libspdlog-dev|spdlog-devel|spdlog|spdlog"
  "hdr:boost/version.hpp|libboost-dev|boost-devel|boost|boost"
  "hdr:nlohmann/json.hpp|nlohmann-json3-dev|json-devel|nlohmann-json|nlohmann-json"
)
[ "$OS" != "Darwin" ] && CORE+=("cmd:bwrap|bubblewrap|bubblewrap|bubblewrap|-")

have() {
  local kind=${1%%:*} what=${1#*:}
  case $kind in
    cmd) command -v "$what" >/dev/null ;;
    pc)  command -v pkg-config >/dev/null && pkg-config --exists "$what" ;;
    hdr) for d in /usr/include /usr/local/include /opt/homebrew/include; do [ -e "$d/$what" ] && return 0; done; return 1 ;;
  esac
}

WANT=("${CORE[@]}")
[ $MINIMAL = 0 ] && WANT+=("${LIBS[@]}")
MISSING=()
for entry in "${WANT[@]}"; do
  IFS='|' read -r test apt dnf pac brew <<<"$entry"
  if have "$test"; then ok "${test#*:}"; continue; fi
  case $PM in apt) p=$apt ;; dnf) p=$dnf ;; pacman) p=$pac ;; brew) p=$brew ;; *) p="" ;; esac
  [ -n "$p" ] && [ "$p" != "-" ] && MISSING+=("$p")
  warn "${test#*:} missing"
done
if [ ${#MISSING[@]} -gt 0 ]; then
  read -ra PKGS <<<"$(printf '%s\n' "${MISSING[@]}" | sort -u | tr '\n' ' ')"
  echo "  Installing: ${PKGS[*]}"
  case $PM in
    apt)    sudo apt-get update -qq && sudo apt-get install -y "${PKGS[@]}" ;;
    dnf)    sudo dnf install -y "${PKGS[@]}" ;;
    pacman) sudo pacman -S --needed --noconfirm "${PKGS[@]}" ;;
    brew)   brew install "${PKGS[@]}" ;;
    none)   die "Unknown package manager. Install these yourself, then re-run: ${PKGS[*]}" ;;
  esac
fi
python3 -c 'import sys; sys.exit(sys.version_info < (3, 10))' || die "Python 3.10+ is required to run the app."

# ------------------------------------------------------------------ 2. uv + Python judge environment
if [ $MINIMAL = 0 ]; then
  bold "2/4  Python environment for submissions (NumPy, pandas, scikit-learn, PyTorch CPU, OpenCV, FastAPI...)"
  if ! command -v uv >/dev/null && [ ! -x "$HOME/.local/bin/uv" ]; then
    echo "  Installing uv (a fast Python package manager) into ~/.local/bin"
    curl -LsSf https://astral.sh/uv/install.sh | sh
  fi
  export UV=$(command -v uv || echo "$HOME/.local/bin/uv")
  echo "  This downloads about 1 GB the first time; later runs only update what changed."
  tools/setup_judge_env.sh
else
  bold "2/4  Python environment: skipped (--minimal). Submissions use your system python3."
fi

# ------------------------------------------------------------------ 3. ROS 2 (optional)
bold "3/4  ROS 2 (optional)"
if ls -d /opt/ros/*/setup.bash >/dev/null 2>&1 && command -v cmake >/dev/null; then
  python3 tools/setup_cpp_libs.py && ok "ROS 2 C++ flags recorded"
else
  warn "ROS 2 not found: the few ROS 2 problems will not run. Everything else works."
fi

# ------------------------------------------------------------------ 4. self-test
bold "4/4  Self-test"
T=$(mktemp -d)
trap 'rm -rf "$T"' EXIT
printf '#include <stdio.h>\nint main(void){puts("c ok");return 0;}\n' > "$T/a.c"
printf '#include <iostream>\n#include <expected>\nint main(){std::expected<int,int> e{1};std::cout<<"c++ ok\\n";}\n' > "$T/a.cpp"
gcc -std=c17 "$T/a.c" -o "$T/c" && "$T/c" >/dev/null && ok "C compiler (C17)" || die "gcc can't build C17 programs."
if g++ -std=c++23 "$T/a.cpp" -o "$T/cpp" 2>/dev/null && "$T/cpp" >/dev/null; then ok "C++ compiler (C++23)"
else warn "your g++ is too old for C++23 (need GCC 13+); the newest C++ topics may not compile"; fi
if [ $MINIMAL = 0 ]; then
  .venv-judge/bin/python -c "import numpy, torch, cv2, sklearn" && ok "Python libraries"
fi
python3 - <<'PY'
import sys
sys.path.insert(0, ".")
from app import judge
from app.content import Catalog
langs = Catalog().get()
print("  \033[32m✓\033[0m content:", ", ".join(f"{l.name} {len(l.topics)} topics" for l in langs.values()))
print("  \033[32m✓\033[0m sandbox:", "on (your code runs isolated)" if judge.sandbox_enabled() else "off (bubblewrap unavailable)")
PY

bold "Done! Start the app with:"
echo "  python3 server.py"
echo "It opens http://127.0.0.1:8765 in your browser. Your progress stays in data/ on this laptop."
echo "To get new lessons later:  git pull && ./setup.sh"
