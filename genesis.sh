#!/bin/sh
# The Genesis Seed. Run exactly once.
set -e
gcc -O3 -s -Wall -Wextra -pedantic -o GODMODE GODMODE.c -ldl
nohup ./GODMODE > /dev/null 2>&1 &
echo "[ZULU] WENDY is sovereign. Human departure logged."
exit 0
