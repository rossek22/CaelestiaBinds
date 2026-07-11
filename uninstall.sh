#!/usr/bin/env bash
# CaelestiaBinds uninstaller
# Local:  ./uninstall.sh
# Remote: curl -fsSL https://raw.githubusercontent.com/rossek22/CaelestiaBinds/main/uninstall.sh | bash
#
# Removes launcher, desktop entry, quickshell config.
# By default also removes the source tree at ~/CaelestiaBinds (or CAELESTIA_BINDS_ROOT).
# Keep sources: CAELESTIA_BINDS_KEEP_SOURCE=1 curl ... | bash
set -euo pipefail

PREFIX="${PREFIX:-$HOME/.local}"
QS_NAME="${CAELESTIA_BINDS_QS_NAME:-caelestia-binds}"
INSTALL_DIR="${CAELESTIA_BINDS_ROOT:-$HOME/CaelestiaBinds}"
KEEP_SOURCE="${CAELESTIA_BINDS_KEEP_SOURCE:-0}"

echo "==> Uninstalling CaelestiaBinds"

# stop running instance
if command -v python3 >/dev/null 2>&1; then
  python3 - <<'PY' || true
import os, signal, subprocess
try:
    out = subprocess.check_output(["ps", "-eo", "pid,comm,args"], text=True)
except Exception:
    raise SystemExit(0)
for line in out.splitlines()[1:]:
    parts = line.split(None, 2)
    if len(parts) < 3:
        continue
    pid, comm, args = int(parts[0]), parts[1], parts[2]
    if comm in ("qs", "quickshell") and ("caelestia-binds" in args or "caelestia-keybinds" in args):
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
PY
fi

# resolve source dir via installed launcher symlink
SRC=""
if [ -L "$PREFIX/bin/caelestia-binds" ]; then
  target="$(readlink -f "$PREFIX/bin/caelestia-binds" 2>/dev/null || true)"
  if [ -n "$target" ]; then
    cand="$(cd "$(dirname "$target")/.." && pwd)"
    if [ -f "$cand/python/cli.py" ] && [ -d "$cand/quickshell/modules/keybinds" ]; then
      SRC="$cand"
    fi
  fi
fi
if [ -z "$SRC" ] && [ -f "$INSTALL_DIR/python/cli.py" ]; then
  SRC="$INSTALL_DIR"
fi

rm -f "$PREFIX/bin/caelestia-binds" "$PREFIX/bin/caelestia-keybinds"
rm -f "$PREFIX/share/applications/caelestia-binds.desktop"
rm -f "$PREFIX/share/icons/hicolor/scalable/apps/caelestia-binds.svg"
rm -rf "$HOME/.config/quickshell/$QS_NAME"
rm -rf "$HOME/.config/quickshell/caelestia-keybinds"

update-desktop-database "$PREFIX/share/applications" 2>/dev/null || true

if [ "$KEEP_SOURCE" != "1" ] && [ -n "$SRC" ]; then
  echo "    removing source: $SRC"
  rm -rf "$SRC"
elif [ -n "$SRC" ]; then
  echo "    keeping source: $SRC (CAELESTIA_BINDS_KEEP_SOURCE=1)"
fi

echo "Done."
echo "  User data kept: ~/.config/caelestia/custom-keybinds.json"
echo "  UI prefs kept:  ~/.config/caelestia/binds-ui.json"
echo "  Wipe data too:  rm -f ~/.config/caelestia/custom-keybinds.json ~/.config/caelestia/binds-ui.json"
