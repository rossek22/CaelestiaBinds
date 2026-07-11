#!/usr/bin/env bash
# CaelestiaBinds installer
# Local:  ./install.sh
# Remote: curl -fsSL https://raw.githubusercontent.com/rossek22/CaelestiaBinds/main/install.sh | bash
set -euo pipefail

REPO_URL="${CAELESTIA_BINDS_REPO:-https://github.com/rossek22/CaelestiaBinds.git}"
BRANCH="${CAELESTIA_BINDS_BRANCH:-main}"
INSTALL_DIR="${CAELESTIA_BINDS_ROOT:-$HOME/CaelestiaBinds}"
PREFIX="${PREFIX:-$HOME/.local}"
QS_NAME="${CAELESTIA_BINDS_QS_NAME:-caelestia-binds}"

# --- detect local checkout vs curl|bash ---
_self=""
if [ -n "${BASH_SOURCE[0]:-}" ] && [ -f "${BASH_SOURCE[0]}" ]; then
  _self="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
elif [ -n "${0:-}" ] && [ -f "$0" ]; then
  case "$(basename "$0")" in
    sh|bash|dash|zsh) ;;
    *) _self="$(cd "$(dirname "$0")" && pwd)" ;;
  esac
fi

_is_repo() {
  [ -f "$1/python/cli.py" ] && [ -d "$1/quickshell/modules/keybinds" ] && [ -f "$1/bin/caelestia-binds" ]
}

REPO=""
if [ -n "$_self" ] && _is_repo "$_self"; then
  REPO="$_self"
  echo "==> CaelestiaBinds install (local checkout)"
else
  echo "==> CaelestiaBinds install (bootstrap from GitHub)"
  echo "    dest: $INSTALL_DIR"

  if command -v git >/dev/null 2>&1; then
    if [ -d "$INSTALL_DIR/.git" ] && _is_repo "$INSTALL_DIR"; then
      echo "    updating existing clone…"
      git -C "$INSTALL_DIR" fetch --depth 1 origin "$BRANCH"
      git -C "$INSTALL_DIR" checkout -q "$BRANCH" 2>/dev/null || git -C "$INSTALL_DIR" checkout -q -B "$BRANCH" "origin/$BRANCH"
      git -C "$INSTALL_DIR" reset --hard "origin/$BRANCH"
    else
      if [ -e "$INSTALL_DIR" ] && [ ! -d "$INSTALL_DIR/.git" ]; then
        echo "!! $INSTALL_DIR exists and is not a git clone." >&2
        echo "   Move it aside or set CAELESTIA_BINDS_ROOT to another path." >&2
        exit 1
      fi
      rm -rf "$INSTALL_DIR"
      git clone --depth 1 --branch "$BRANCH" "$REPO_URL" "$INSTALL_DIR"
    fi
  else
    echo "    git not found, using tarball…"
    command -v curl >/dev/null 2>&1 || { echo "!! need curl or git" >&2; exit 1; }
    command -v tar >/dev/null 2>&1 || { echo "!! need tar" >&2; exit 1; }
    tmp="$(mktemp -d)"
    trap 'rm -rf "$tmp"' EXIT
    curl -fsSL "https://github.com/rossek22/CaelestiaBinds/archive/refs/heads/${BRANCH}.tar.gz" \
      | tar -xz -C "$tmp"
    src="$(find "$tmp" -maxdepth 1 -type d -name 'CaelestiaBinds-*' | head -1)"
    [ -n "$src" ] || { echo "!! failed to unpack tarball" >&2; exit 1; }
    rm -rf "$INSTALL_DIR"
    mkdir -p "$(dirname "$INSTALL_DIR")"
    mv "$src" "$INSTALL_DIR"
    trap - EXIT
    rm -rf "$tmp"
  fi

  REPO="$INSTALL_DIR"
fi

export CAELESTIA_BINDS_ROOT="$REPO"

echo "    repo:   $REPO"
echo "    prefix: $PREFIX"
echo "    qs:     $QS_NAME"

# --- deps check ---
need=()
command -v qs >/dev/null 2>&1 || need+=("quickshell (qs)")
command -v python3 >/dev/null 2>&1 || need+=("python3")
if ((${#need[@]})); then
  echo "!! Missing dependencies: ${need[*]}" >&2
  echo "   On Arch/CachyOS: pacman -S quickshell caelestia-shell python" >&2
fi

# --- bin ---
mkdir -p "$PREFIX/bin"
chmod +x "$REPO/bin/caelestia-binds" "$REPO/python/cli.py" "$REPO/install.sh" "$REPO/uninstall.sh"
ln -sfn "$REPO/bin/caelestia-binds" "$PREFIX/bin/caelestia-binds"
ln -sfn "$REPO/bin/caelestia-binds" "$PREFIX/bin/caelestia-keybinds"

# --- quickshell config ---
QS_DIR="$HOME/.config/quickshell/$QS_NAME"
mkdir -p "$HOME/.config/quickshell"
rm -rf "$QS_DIR"
mkdir -p "$QS_DIR/modules"

ln -sfn "$REPO/quickshell/shell.qml" "$QS_DIR/shell.qml"
ln -sfn "$REPO/quickshell/modules/keybinds" "$QS_DIR/modules/keybinds"

CAE_QS="/etc/xdg/quickshell/caelestia"
if [ ! -d "$CAE_QS/components" ]; then
  CAE_QS="$HOME/.config/quickshell/caelestia"
fi
if [ -d "$CAE_QS/components" ]; then
  ln -sfn "$CAE_QS/components" "$QS_DIR/components"
  ln -sfn "$CAE_QS/services" "$QS_DIR/services"
  ln -sfn "$CAE_QS/utils" "$QS_DIR/utils"
  ln -sfn "$CAE_QS/assets" "$QS_DIR/assets"
  echo "    linked Caelestia components from $CAE_QS"
else
  echo "!! Caelestia shell QML not found" >&2
  echo "   Install caelestia-shell so UI components are available." >&2
fi

ln -sfn "$REPO/assets" "$QS_DIR/project-assets" 2>/dev/null || true

# --- desktop entry ---
mkdir -p "$PREFIX/share/applications"
sed "s|@EXEC@|$PREFIX/bin/caelestia-binds|g" \
  "$REPO/share/applications/caelestia-binds.desktop.in" \
  > "$PREFIX/share/applications/caelestia-binds.desktop"
mkdir -p "$PREFIX/share/icons/hicolor/scalable/apps"
ln -sfn "$REPO/share/icons/hicolor/scalable/apps/caelestia-binds.svg" \
  "$PREFIX/share/icons/hicolor/scalable/apps/caelestia-binds.svg" 2>/dev/null || true

if [ -f "$HOME/.config/hypr/hyprland.lua" ] || [ -d "$HOME/.config/hypr/hyprland" ]; then
  python3 "$REPO/python/cli.py" reload >/dev/null 2>&1 || true
fi

update-desktop-database "$PREFIX/share/applications" 2>/dev/null || true

# ensure ~/.local/bin on PATH hint
case ":$PATH:" in
  *":$PREFIX/bin:"*) ;;
  *)
    echo ""
    echo "!! $PREFIX/bin is not on PATH. Add to your shell rc:"
    echo "   export PATH=\"$PREFIX/bin:\$PATH\""
    ;;
esac

echo ""
echo "Installed."
echo "  Source: $REPO"
echo "  Run:    caelestia-binds"
echo ""
echo "Uninstall:"
echo "  curl -fsSL https://raw.githubusercontent.com/rossek22/CaelestiaBinds/main/uninstall.sh | bash"
echo "  # or:  $REPO/uninstall.sh"
