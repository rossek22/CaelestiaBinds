#!/usr/bin/env bash
# Install CaelestiaBinds for the current user
set -euo pipefail

REPO="$(cd "$(dirname "$0")" && pwd)"
PREFIX="${PREFIX:-$HOME/.local}"
QS_NAME="${CAELESTIA_BINDS_QS_NAME:-caelestia-binds}"

echo "==> CaelestiaBinds install"
echo "    repo:   $REPO"
echo "    prefix: $PREFIX"
echo "    qs:     $QS_NAME"

# --- deps check ---
need=()
command -v qs >/dev/null 2>&1 || need+=("quickshell (qs)")
command -v python3 >/dev/null 2>&1 || need+=("python3")
command -v hyprctl >/dev/null 2>&1 || true  # optional warn
if ((${#need[@]})); then
  echo "!! Missing dependencies: ${need[*]}" >&2
  echo "   On Arch/CachyOS: pacman -S quickshell caelestia-shell python" >&2
fi

# --- bin ---
mkdir -p "$PREFIX/bin"
chmod +x "$REPO/bin/caelestia-binds" "$REPO/python/cli.py"
ln -sfn "$REPO/bin/caelestia-binds" "$PREFIX/bin/caelestia-binds"
# compat alias
ln -sfn "$REPO/bin/caelestia-binds" "$PREFIX/bin/caelestia-keybinds"

# --- quickshell config (symlinks to real Caelestia components) ---
QS_DIR="$HOME/.config/quickshell/$QS_NAME"
mkdir -p "$HOME/.config/quickshell"
rm -rf "$QS_DIR"
mkdir -p "$QS_DIR/modules"

ln -sfn "$REPO/quickshell/shell.qml" "$QS_DIR/shell.qml"
ln -sfn "$REPO/quickshell/modules/keybinds" "$QS_DIR/modules/keybinds"

# real Caelestia UI components
CAE_QS="/etc/xdg/quickshell/caelestia"
if [ ! -d "$CAE_QS/components" ]; then
  # try user-local caelestia shell
  CAE_QS="$HOME/.config/quickshell/caelestia"
fi
if [ -d "$CAE_QS/components" ]; then
  ln -sfn "$CAE_QS/components" "$QS_DIR/components"
  ln -sfn "$CAE_QS/services" "$QS_DIR/services"
  ln -sfn "$CAE_QS/utils" "$QS_DIR/utils"
  ln -sfn "$CAE_QS/assets" "$QS_DIR/assets"
  echo "    linked Caelestia components from $CAE_QS"
else
  echo "!! Caelestia shell QML not found at /etc/xdg/quickshell/caelestia" >&2
  echo "   Install caelestia-shell so UI components are available." >&2
fi

# авы/локальные ассеты проги
ln -sfn "$REPO/assets" "$QS_DIR/project-assets" 2>/dev/null || true

# --- desktop entry ---
mkdir -p "$PREFIX/share/applications"
sed "s|@EXEC@|$PREFIX/bin/caelestia-binds|g" \
  "$REPO/share/applications/caelestia-binds.desktop.in" \
  > "$PREFIX/share/applications/caelestia-binds.desktop"
# icon
mkdir -p "$PREFIX/share/icons/hicolor/scalable/apps"
ln -sfn "$REPO/share/icons/hicolor/scalable/apps/caelestia-binds.svg" \
  "$PREFIX/share/icons/hicolor/scalable/apps/caelestia-binds.svg" 2>/dev/null || true

# --- env for launcher when installed ---
# bin already resolves CAELESTIA_BINDS_ROOT via symlink

# --- optional: register Super+/ bind if hypr-user managed by us ---
if [ -f "$HOME/.config/hypr/hyprland.lua" ] || [ -d "$HOME/.config/hypr/hyprland" ]; then
  python3 "$REPO/python/cli.py" reload >/dev/null 2>&1 || true
fi

update-desktop-database "$PREFIX/share/applications" 2>/dev/null || true

echo ""
echo "Installed."
echo "  Run:   caelestia-binds"
echo "  Or:    Super + /  (if custom-keybinds has the open bind)"
echo ""
echo "Uninstall: $REPO/uninstall.sh"
