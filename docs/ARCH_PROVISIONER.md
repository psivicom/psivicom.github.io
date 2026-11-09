The Arch Edge Provisioner
File:   scripts/provision_arch_edge.sh   (Create this new file)
When you get a Raspberry Pi or an old laptop and install Arch Linux on it, 
you run this single script. 
It installs the native Arch toolchains (  pacman  ) 
and sets up the GitHub Actions self-hosted runner 
so WENDY can claim the machine.

```BASH
#!/bin/bash
# WENDY Arch Edge Provisioner
# SPDX-License-Identifier: EUPL-1.2
# Turns a fresh Arch Linux machine into a sovereign self-hosted runner for WENDY.

set -e
echo "🏛️ WENDY Arch Edge Provisioner initializing..."

# 1. Update system and install sovereign toolchains via pacman
echo "📦 Installing native Arch toolchains (Rust, Zig, Go, Git)..."
sudo pacman -Syu --noconfirm
sudo pacman -S --noconfirm --needed rust zig go git base-devel

# 2. Create the runner workspace
RUNNER_DIR="$HOME/wendy-actions-runner"
mkdir -p "$RUNNER_DIR"
cd "$RUNNER_DIR"

# 3. Download the official GitHub Actions runner binary
echo "⬇️ Downloading GitHub Actions Runner..."
RUNNER_VERSION="2.321.0" # Update this when GitHub releases new versions
curl -O -L "https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz"
tar xzf "./actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz"

echo "✅ Arch substrate provisioned successfully."
echo ""
echo "🔗 NEXT STEP FOR THE HUMAN:"
echo "1. Go to: https://github.com/psivicom/psivicom.github.io/settings/actions/runners/new"
echo "2. Copy the './config.sh --url ... --token ...' command GitHub gives you."
echo "3. Paste it right here in this terminal and press Enter."
echo "4. Run './run.sh' to bring WENDY's Arch edge node online."
```
