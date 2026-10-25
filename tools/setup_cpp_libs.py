#!/usr/bin/env python3
"""Resolve compile/link flags for C/C++ libraries that problems may request (front matter `libs:`).

pkg-config libraries are resolved by the judge at run time. Libraries that only ship CMake config
packages (ROS 2's rclcpp and message packages) are resolved here once: a throw-away CMake project is
configured and built, and the exact compiler and linker flags it used are written to .cache/cpp_libs.json.

Usage: python3 tools/setup_cpp_libs.py
"""
from __future__ import annotations

import glob
import json
import os
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / ".cache" / "cpp_libs.json"

ROS_PACKAGES = ["rclcpp", "std_msgs", "geometry_msgs", "sensor_msgs", "std_srvs", "nav_msgs"]


def ros_flags(setup: str) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        finds = "\n".join(f"find_package({p} REQUIRED)" for p in ROS_PACKAGES)
        targets = " ".join(["rclcpp::rclcpp"] + [f"${{{p}_TARGETS}}" for p in ROS_PACKAGES[1:]])
        (t / "CMakeLists.txt").write_text(
            "cmake_minimum_required(VERSION 3.16)\nproject(flags CXX)\n" + finds +
            f"\nadd_executable(probe main.cpp)\ntarget_link_libraries(probe {targets})\n")
        (t / "main.cpp").write_text("#include <rclcpp/rclcpp.hpp>\nint main(){return 0;}\n")
        script = (f"source {shlex.quote(setup)} >/dev/null 2>&1 && "
                  f"cmake -S {tmp} -B {tmp}/b -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -DCMAKE_BUILD_TYPE=Release >/dev/null && "
                  f"cmake --build {tmp}/b >/dev/null && env")
        out = subprocess.run(["bash", "-c", script], capture_output=True, text=True, check=True).stdout
        env_all = dict(line.split("=", 1) for line in out.splitlines() if "=" in line)
        cmd = json.loads((t / "b" / "compile_commands.json").read_text())[0]["command"]
        cflags = [a for a in shlex.split(cmd)[1:] if a.startswith(("-I", "-D", "-isystem")) or a.startswith("/opt")]
        # keep "-isystem <dir>" pairs together
        parts, toks = [], shlex.split(cmd)[1:]
        i = 0
        while i < len(toks):
            if toks[i] == "-isystem":
                parts += [toks[i], toks[i + 1]]; i += 2; continue
            if toks[i].startswith(("-I", "-D")):
                parts.append(toks[i])
            i += 1
        link = (t / "b" / "CMakeFiles" / "probe.dir" / "link.txt").read_text().split()
        ldflags = [a for a in link if a.endswith(".so") or a.startswith(("-Wl,-rpath", "-l", "-L"))]
        keep = ["AMENT_PREFIX_PATH", "LD_LIBRARY_PATH", "ROS_DISTRO", "ROS_VERSION", "RMW_IMPLEMENTATION"]
        env = {k: env_all[k] for k in keep if k in env_all}
        env["ROS_AUTOMATIC_DISCOVERY_RANGE"] = "LOCALHOST"
        return {"cflags": parts, "ldflags": ldflags, "env": env}


def main() -> int:
    libs: dict[str, dict] = {}
    setups = sorted(glob.glob("/opt/ros/*/setup.bash"))
    if setups:
        libs["rclcpp"] = ros_flags(setups[-1])
        print(f"rclcpp: {len(libs['rclcpp']['cflags'])} compile flags, {len(libs['rclcpp']['ldflags'])} link flags")
    CACHE.parent.mkdir(exist_ok=True)
    CACHE.write_text(json.dumps(libs, indent=1))
    print("wrote", CACHE.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
