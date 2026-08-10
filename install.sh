#!/usr/bin/env bash
# One-shot setup: installs pixi if needed, builds the project's Python
# environment, and installs a `get-armor-heading` launcher on PATH.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$HOME/.local/bin"
LAUNCHER="$BIN_DIR/get-armor-heading"

if ! command -v pixi >/dev/null 2>&1; then
    echo "Installing pixi..."
    curl -fsSL https://pixi.sh/install.sh | sh
fi
export PATH="$HOME/.pixi/bin:$PATH"

echo "Setting up the project environment..."
pixi install --manifest-path "$REPO_DIR/pixi.toml"

mkdir -p "$BIN_DIR"
cat > "$LAUNCHER" <<EOF
#!/bin/bash
nohup "\$HOME/.pixi/bin/pixi" run --manifest-path "$REPO_DIR/pixi.toml" gui \\
  > "$REPO_DIR/gui.log" 2>&1 &
disown
echo "ARMOR/MAX GUI launched in background (PID \$!). Logs: $REPO_DIR/gui.log"
EOF
chmod +x "$LAUNCHER"

SHELL_RC="$HOME/.$(basename "$SHELL")rc"
if [[ ":$PATH:" != *":$BIN_DIR:"* ]] && ! grep -qs "$BIN_DIR" "$SHELL_RC" 2>/dev/null; then
    echo "export PATH=\"$BIN_DIR:\$PATH\"" >> "$SHELL_RC"
    echo "Added $BIN_DIR to PATH in $SHELL_RC"
fi

echo
echo "Done. Open a new terminal (or run 'source $SHELL_RC') and run:"
echo "  get-armor-heading"
