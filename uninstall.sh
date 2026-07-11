#!/usr/bin/env bash
set -euo pipefail
PREFIX="${PREFIX:-$HOME/.local}"
QS_NAME="${CAELESTIA_BINDS_QS_NAME:-caelestia-binds}"

echo "==> Uninstalling CaelestiaBinds from $PREFIX"

rm -f "$PREFIX/bin/caelestia-binds" "$PREFIX/bin/caelestia-keybinds"
rm -f "$PREFIX/share/applications/caelestia-binds.desktop"
rm -f "$PREFIX/share/icons/hicolor/scalable/apps/caelestia-binds.svg"
rm -rf "$HOME/.config/quickshell/$QS_NAME"
# legacy
rm -rf "$HOME/.config/quickshell/caelestia-keybinds"

# stop running instance
python3 - <<PY
import os, signal, subprocess
for line in subprocess.check_output(["ps","-eo","pid,comm,args"], text=True).splitlines()[1:]:
    parts = line.split(None, 2)
    if len(parts) < 3: continue
    pid, comm, args = int(parts[0]), parts[1], parts[2]
    if comm in ("qs","quickshell") and ("caelestia-binds" in args or "caelestia-keybinds" in args):
        try: os.kill(pid, signal.SIGTERM)
        except ProcessLookupError: pass
PY

update-desktop-database "$PREFIX/share/applications" 2>/dev/null || true
echo "Done. User data kept: ~/.config/caelestia/custom-keybinds.json"
