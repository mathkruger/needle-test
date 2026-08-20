#!/bin/bash
set -e

pip install -q cactus-needle --no-deps 2>/dev/null || true
pip install -q -r requirements.txt 2>/dev/null || true

python3 src/main.py