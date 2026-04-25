#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="${1:-/home/ying/epsilon-reproduction}"

source /opt/ros/noetic/setup.bash
catkin_make -C "$WORKSPACE" -j"$(nproc)"

echo "[INFO] Build success: $WORKSPACE"
