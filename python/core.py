#!/usr/bin/env python3
"""Caelestia Keybinds — M3 keybind manager synced with Caelestia scheme."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

HOME = Path.home()


def project_root() -> Path:
    """Repo root (CaelestiaBinds/) — portable for clone/download installs."""
    env = os.environ.get("CAELESTIA_BINDS_ROOT")
    if env:
        return Path(env).expanduser().resolve()
    here = Path(__file__).resolve().parent  # .../python
    if (here.parent / "quickshell" / "shell.qml").exists():
        return here.parent
    # fallback: ~/CaelestiaBinds
    return (HOME / "CaelestiaBinds").resolve()


PROJECT_ROOT = project_root()
HYPR = HOME / ".config/hypr"
CAELESTIA = HOME / ".config/caelestia"
KEYBINDS_LUA = HYPR / "hyprland/keybinds.lua"
VARIABLES_LUA = HYPR / "variables.lua"
HYPR_VARS_LUA = CAELESTIA / "hypr-vars.lua"
HYPR_USER_LUA = CAELESTIA / "hypr-user.lua"
CUSTOM_JSON = CAELESTIA / "custom-keybinds.json"
SCHEME_JSON = HOME / ".local/state/caelestia/scheme.json"
SCHEME_LUA = HYPR / "scheme/current.lua"
APP_ID = "dev.caelestia.binds"
FONT = "Google Sans Flex"

def _resolve_app_bin() -> str:
    for cand in (
        PROJECT_ROOT / "bin" / "caelestia-binds",
        HOME / ".local" / "bin" / "caelestia-binds",
        HOME / ".local" / "bin" / "caelestia-keybinds",
    ):
        if cand.exists():
            return str(cand)
    return str(HOME / ".local" / "bin" / "caelestia-binds")


APP_BIN = _resolve_app_bin()

# ---------------------------------------------------------------------------
# Labels / action intelligence
# ---------------------------------------------------------------------------

GLOBAL_LABELS = {
    "caelestia:launcher": ("Open app launcher", "Opens the Caelestia application launcher overlay."),
    "caelestia:session": ("Session / power menu", "Shows lock, logout, reboot, shutdown actions."),
    "caelestia:sidebar": ("Toggle sidebar", "Opens/closes the notification sidebar."),
    "caelestia:clearNotifs": ("Clear notifications", "Dismisses all notifications in the sidebar."),
    "caelestia:showall": ("Show all panels", "Reveals every Caelestia panel at once."),
    "caelestia:lock": ("Lock screen", "Locks the session with the Caelestia lock screen."),
    "caelestia:brightnessUp": ("Brightness up", "Increases display brightness."),
    "caelestia:brightnessDown": ("Brightness down", "Decreases display brightness."),
    "caelestia:mediaToggle": ("Play / pause", "Toggles playback of the active media player."),
    "caelestia:mediaNext": ("Next track", "Skips to the next media track."),
    "caelestia:mediaPrev": ("Previous track", "Goes to the previous media track."),
    "caelestia:mediaStop": ("Stop media", "Stops the active media player."),
    "caelestia:screenshot": ("Screenshot region", "Interactive region screenshot via Caelestia."),
    "caelestia:screenshotFreeze": ("Screenshot freeze", "Freezes the screen, then pick a region."),
}

VAR_LABELS = {
    "kbSession": "Session / power menu",
    "kbShowSidebar": "Toggle sidebar",
    "kbClearNotifs": "Clear notifications",
    "kbShowPanels": "Show all panels",
    "kbLock": "Lock screen",
    "kbRestoreLock": "Restore shell + lock",
    "kbGoToWs": "Go to workspace",
    "kbMoveWinToWs": "Move window to workspace",
    "kbGoToWsGroup": "Go to workspace group",
    "kbMoveWinToWsGroup": "Move window to workspace group",
    "kbPrevWs": "Previous workspace",
    "kbNextWs": "Next workspace",
    "kbWindowGroupCycleNext": "Next window",
    "kbWindowGroupCyclePrev": "Previous window",
    "kbUngroup": "Ungroup window",
    "kbToggleGroup": "Toggle window group",
    "kbMoveWindow": "Move window (drag)",
    "kbResizeWindow": "Resize window (mouse)",
    "kbWindowPip": "Picture-in-picture",
    "kbPinWindow": "Pin window",
    "kbWindowFullscreen": "Fullscreen",
    "kbWindowBorderedFullscreen": "Maximize",
    "kbToggleWindowFloating": "Toggle floating",
    "kbCloseWindow": "Close window",
    "kbSpecialWs": "Toggle special workspace",
    "kbSystemMonitorWs": "System monitor workspace",
    "kbMusicWs": "Music workspace",
    "kbCommunicationWs": "Communication workspace",
    "kbTodoWs": "Todo workspace",
    "kbTerminal": "Open terminal",
    "kbBrowser": "Open browser",
    "kbEditor": "Open editor",
    "kbFileExplorer": "Open file manager",
}

ACTION_PRESETS = [
    ("exec", "Run command", "Shell command (e.g. foot, firefox)"),
    ("hypr", "Hyprland dispatcher", "e.g. killactive, workspace 2, togglefloating"),
    ("global", "Caelestia global", "e.g. caelestia:launcher, caelestia:lock"),
    ("caelestia", "Caelestia CLI", "Subcommand after caelestia (e.g. screenshot)"),
]

HYPR_PRESETS = [
    ("killactive", "Close active window"),
    ("togglefloating", "Toggle floating"),
    ("fullscreen", "Fullscreen"),
    ("fullscreen 1", "Maximize"),
    ("centerwindow", "Center window"),
    ("workspace e+1", "Next workspace"),
    ("workspace e-1", "Previous workspace"),
    ("movetoworkspace e+1", "Move window to next workspace"),
    ("movetoworkspace e-1", "Move window to previous workspace"),
    ("togglespecialworkspace", "Toggle special workspace"),
    ("cyclenext", "Focus next window"),
    ("cycleprev", "Focus previous window"),
    ("pin", "Pin window"),
    ("exit", "Exit Hyprland"),
]


@dataclass
class Bind:
    id: str
    keys: str
    title: str
    detail: str
    category: str
    source: str  # system | custom | override
    kind: str = "system"  # system | exec | hypr | global | caelestia
    payload: str = ""
    flags: list[str] = field(default_factory=list)
    raw: str = ""
    enabled: bool = True
    technical: str = ""
    # resolved real command when technical uses vars.* (e.g. exec thunar)
    technical_resolved: str = ""

    @property
    def has_var_cmd(self) -> bool:
        """True if technical still contains an unresolved vars. reference."""
        t = self.technical or ""
        r = self.technical_resolved or ""
        return bool(r) and r != t and ("vars." in t or "vars." in (self.raw or ""))

    @property
    def search_blob(self) -> str:
        return " ".join(
            [
                self.keys,
                self.title,
                self.detail,
                self.category,
                self.payload,
                self.technical,
                self.technical_resolved,
                self.source,
                *self.flags,
            ]
        ).lower()


# ---------------------------------------------------------------------------
# Scheme / helpers
# ---------------------------------------------------------------------------


def _run(cmd: list[str], timeout: float = 3.0) -> str:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.stdout
    except (OSError, subprocess.SubprocessError):
        return ""


def load_scheme() -> dict[str, str]:
    colours: dict[str, str] = {}
    if SCHEME_JSON.exists():
        try:
            data = json.loads(SCHEME_JSON.read_text())
            raw = data.get("colours") or data
            for k, v in raw.items():
                if isinstance(v, str) and re.fullmatch(r"[0-9a-fA-F]{6,8}", v):
                    colours[k] = f"#{v[:6]}"
            return colours
        except (OSError, json.JSONDecodeError):
            pass
    if SCHEME_LUA.exists():
        for m in re.finditer(r'(\w+)\s*=\s*"([0-9a-fA-F]{6})"', SCHEME_LUA.read_text()):
            colours[m.group(1)] = f"#{m.group(2)}"
    return colours


def scheme_meta() -> str:
    if SCHEME_JSON.exists():
        try:
            m = json.loads(SCHEME_JSON.read_text())
            return f"{m.get('name', 'scheme')} · {m.get('flavour', '')} · {m.get('mode', '')}".strip(" ·")
        except Exception:
            pass
    return "caelestia"


# display-only prettifiers (never write these into hypr lua)
_DISPLAY_KEYS = {
    "mouse:272": "LMB",
    "mouse:273": "RMB",
    "mouse_up": "Scroll↑",
    "mouse_down": "Scroll↓",
    "SUPER_L": "Super",
    "Return": "Enter",
    "slash": "/",
    "period": ".",
    "comma": ",",
    "equal": "=",
    "minus": "−",
    "backslash": "\\",
}

# map pretty symbols back to hypr key names when saving
_HYPR_KEY_ALIASES = {
    "/": "slash",
    ".": "period",
    ",": "comma",
    "=": "equal",
    "−": "minus",
    "-": "minus",
    "\\": "backslash",
    "enter": "Return",
    "esc": "Escape",
    "escape": "Escape",
    "space": "Space",
    "lmb": "mouse:272",
    "rmb": "mouse:273",
    "scrollup": "mouse_up",
    "scrolldown": "mouse_down",
    "super": "SUPER",
    "ctrl": "CTRL",
    "control": "CTRL",
    "alt": "ALT",
    "shift": "SHIFT",
}


def pretty_keys(keys: str) -> str:
    k = re.sub(r"\s*\+\s*", " + ", keys.strip())
    for a, b in _DISPLAY_KEYS.items():
        k = re.sub(rf"\b{re.escape(a)}\b", lambda _m, v=b: v, k, flags=re.I)
    return k


def hypr_keys(keys: str) -> str:
    """Normalize keys into Hyprland/lua form (slash, Return, SUPER, …)."""
    k = re.sub(r"\s*\+\s*", " + ", keys.strip())
    parts = []
    for raw in k.split("+"):
        p = raw.strip()
        if not p:
            continue
        pl = p.lower()
        if pl in _HYPR_KEY_ALIASES:
            parts.append(_HYPR_KEY_ALIASES[pl])
            continue
        if p in _HYPR_KEY_ALIASES:
            parts.append(_HYPR_KEY_ALIASES[p])
            continue
        # single symbol
        if p in _HYPR_KEY_ALIASES:
            parts.append(_HYPR_KEY_ALIASES[p])
        elif pl in ("super", "ctrl", "control", "alt", "shift"):
            parts.append(_HYPR_KEY_ALIASES[pl])
        elif len(p) == 1 and p.isalpha():
            parts.append(p.upper())
        else:
            parts.append(p)
    return " + ".join(parts)


def norm_keys(keys: str) -> str:
    """Canonical key string for storage / compare (hypr form)."""
    return hypr_keys(keys)


def load_var_keys() -> dict[str, str]:
    """kb* keybind chords only."""
    out: dict[str, str] = {}
    for path in (VARIABLES_LUA, HYPR_VARS_LUA):
        if not path.exists():
            continue
        for m in re.finditer(r'(kb\w+)\s*=\s*"([^"]+)"', path.read_text(errors="replace")):
            out[m.group(1)] = m.group(2)
    return out


def load_var_values() -> dict[str, str]:
    """All string variables from variables.lua (+ hypr-vars overrides).

    e.g. fileExplorer → "thunar", terminal → "foot"
    """
    out: dict[str, str] = {}
    for path in (VARIABLES_LUA, HYPR_VARS_LUA):
        if not path.exists():
            continue
        text = path.read_text(errors="replace")
        for m in re.finditer(r'(\w+)\s*=\s*"((?:\\.|[^"\\])*)"', text):
            name, val = m.group(1), m.group(2).replace('\\"', '"')
            # skip non-command noise if needed; keep all strings
            out[name] = val
        for m in re.finditer(r"(\w+)\s*=\s*'((?:\\.|[^'\\])*)'", text):
            name, val = m.group(1), m.group(2).replace("\\'", "'")
            out[name] = val
    return out


def resolve_var_cmd(var_name: str, var_values: dict[str, str] | None = None) -> str:
    vals = var_values if var_values is not None else load_var_values()
    return vals.get(var_name, "")


# ---------------------------------------------------------------------------
# Custom store (JSON) → hypr-user.lua
# ---------------------------------------------------------------------------


def default_store() -> dict[str, Any]:
    return {
        "version": 2,
        "binds": [
            {
                "id": "open-keybinds-viewer",
                "keys": "SUPER + slash",
                "kind": "exec",
                "payload": APP_BIN,
                "title": "Open keybinds manager",
                "detail": "Opens this Caelestia Keybinds window.",
                "category": "Custom",
                "flags": [],
                "enabled": True,
            },
            {
                "id": "open-keybinds-viewer-shift",
                "keys": "SUPER + SHIFT + slash",
                "kind": "exec",
                "payload": APP_BIN,
                "title": "Open keybinds manager",
                "detail": "Opens this Caelestia Keybinds window.",
                "category": "Custom",
                "flags": [],
                "enabled": True,
            },
        ],
        # temporary off — still listed, can re-enable
        "disabled": [],
        # permanent removal — hidden forever, unbound, source line cut when possible
        "deleted": [],
        "overrides": {},
    }


def load_store() -> dict[str, Any]:
    if not CUSTOM_JSON.exists():
        store = default_store()
        save_store(store)
        return store
    try:
        data = json.loads(CUSTOM_JSON.read_text())
        if "binds" not in data:
            data = default_store()
        data.setdefault("disabled", [])
        data.setdefault("deleted", [])
        data.setdefault("overrides", {})
        data.setdefault("version", 2)
        return data
    except (OSError, json.JSONDecodeError):
        return default_store()


def save_store(store: dict[str, Any]) -> None:
    CAELESTIA.mkdir(parents=True, exist_ok=True)
    CUSTOM_JSON.write_text(json.dumps(store, indent=2, ensure_ascii=False) + "\n")
    write_hypr_user_lua(store)
    _run(["hyprctl", "reload"])


def _lua_escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def _flags_lua(flags: list[str]) -> str:
    if not flags:
        return ""
    parts = [f"{f} = true" for f in flags if f]
    return ", { " + ", ".join(parts) + " }" if parts else ""


def bind_to_lua(keys: str, kind: str, payload: str, flags: list[str]) -> str:
    keys_s = _lua_escape(hypr_keys(keys))
    fl = _flags_lua(flags)
    p = payload.strip()
    if kind == "exec":
        return f'hl.bind("{keys_s}", hl.dsp.exec_cmd("{_lua_escape(p)}"){fl})'
    if kind == "hypr":
        # dispatcher string via exec of hyprctl dispatch is safer & universal
        return f'hl.bind("{keys_s}", hl.dsp.exec_cmd("hyprctl dispatch {_lua_escape(p)}"){fl})'
    if kind == "global":
        g = p if p.startswith("caelestia:") else f"caelestia:{p}"
        return f'hl.bind("{keys_s}", hl.dsp.global("{_lua_escape(g)}"){fl})'
    if kind == "caelestia":
        cmd = p if p.startswith("caelestia ") else f"caelestia {p}"
        return f'hl.bind("{keys_s}", hl.dsp.exec_cmd("{_lua_escape(cmd)}"){fl})'
    return f'hl.bind("{keys_s}", hl.dsp.exec_cmd("{_lua_escape(p)}"){fl})'


def write_hypr_user_lua(store: dict[str, Any]) -> None:
    lines = [
        "-- AUTO-GENERATED by Caelestia Keybinds",
        "-- Source of truth: ~/.config/caelestia/custom-keybinds.json",
        "-- Do not edit this file by hand — use the Keybinds app.",
        "",
    ]

    # Permanent deletes + temporary disables → unbind at runtime
    unbound: list[str] = []
    for keys in list(store.get("deleted") or []) + list(store.get("disabled") or []):
        nk = norm_keys(keys)
        if nk and nk not in unbound:
            unbound.append(nk)
    if unbound:
        lines.append("-- Unbound (deleted permanently or disabled temporarily)")
        for keys in unbound:
            lines.append(f'hl.unbind("{_lua_escape(keys)}")')
        lines.append("")

    overrides = store.get("overrides") or {}
    if overrides:
        lines.append("-- Overrides of system binds")
        for keys, ov in overrides.items():
            lines.append(f'hl.unbind("{_lua_escape(norm_keys(keys))}")')
            lines.append(
                bind_to_lua(
                    ov.get("keys") or keys,
                    ov.get("kind", "exec"),
                    ov.get("payload", ""),
                    ov.get("flags") or [],
                )
            )
        lines.append("")

    lines.append("-- Custom binds")
    for b in store.get("binds") or []:
        if not b.get("enabled", True):
            continue
        # skip if permanently deleted by keys
        if norm_keys(b.get("keys", "")).lower() in {
            norm_keys(x).lower() for x in (store.get("deleted") or [])
        }:
            continue
        lines.append(
            bind_to_lua(
                b.get("keys", ""),
                b.get("kind", "exec"),
                b.get("payload", ""),
                b.get("flags") or [],
            )
        )
    lines.append("")
    HYPR_USER_LUA.write_text("\n".join(lines))


def _backup_keybinds_lua() -> None:
    bak = KEYBINDS_LUA.with_suffix(".lua.bak")
    if KEYBINDS_LUA.exists() and not bak.exists():
        bak.write_text(KEYBINDS_LUA.read_text(errors="replace"))


def remove_bind_from_system_lua(bind_raw: str, keys: str) -> bool:
    """Physically cut the bind out of hyprland/keybinds.lua. Returns True if file changed."""
    if not KEYBINDS_LUA.exists():
        return False
    text = KEYBINDS_LUA.read_text(errors="replace")
    original = text
    raw = (bind_raw or "").strip()

    if raw and raw in text:
        # exact chunk (single or multi-line as stored by parser)
        text = text.replace(raw, "", 1)
        # clean leftover blank clutter from multi-line removal
        text = re.sub(r"\n{3,}", "\n\n", text)
    else:
        # fall back: drop hl.bind lines whose first arg resolves to same keys
        var_keys = load_var_keys()
        target = norm_keys(keys).lower()
        lines = text.splitlines(keepends=True)
        out: list[str] = []
        i = 0
        changed = False
        while i < len(lines):
            line = lines[i]
            if "hl.bind(" not in line:
                out.append(line)
                i += 1
                continue
            chunk = line.rstrip("\n")
            j = i
            while chunk.count("(") > chunk.count(")") and j + 1 < len(lines):
                j += 1
                chunk += " " + lines[j].strip()
            m = re.search(r"hl\.bind\((.*)\)\s*$", chunk.strip())
            if m:
                keys_raw, _, _ = split_bind_args(m.group(1))
                resolved = norm_keys(resolve_key_expr(keys_raw, var_keys)).lower()
                # template key 0-9: match if target is SUPER + N style under same prefix
                if resolved == target or (
                    "0-9" in resolved
                    and re.sub(r"\b\d\b", "0-9", target) == resolved
                ):
                    # skip lines i..j
                    i = j + 1
                    changed = True
                    continue
            for k in range(i, j + 1):
                out.append(lines[k])
            i = j + 1
        if changed:
            text = "".join(out)

    if text == original:
        return False
    _backup_keybinds_lua()
    KEYBINDS_LUA.write_text(text)
    return True


# ---------------------------------------------------------------------------
# System bind parser
# ---------------------------------------------------------------------------


def resolve_key_expr(expr: str, var_keys: dict[str, str]) -> str:
    expr = expr.strip().strip('"').strip("'")

    def repl(m: re.Match) -> str:
        return var_keys.get(m.group(1), m.group(1))

    expr = re.sub(r"vars\.(\w+)", repl, expr)
    expr = expr.replace(" .. ", "")
    expr = re.sub(r'"\s*\+\s*"', " + ", expr).replace('"', "")
    expr = re.sub(r"\s*\+\s*", " + ", expr)
    return pretty_keys(re.sub(r"\s+", " ", expr).strip())


def describe_action(
    raw: str, var_values: dict[str, str] | None = None
) -> tuple[str, str, str, str]:
    """Return (title, detail, technical, technical_resolved).

    technical keeps vars.* form; technical_resolved expands to real command.
    """
    vals = var_values if var_values is not None else load_var_values()
    s = raw.strip()
    tech = re.sub(r"\s+", " ", s)

    m = re.search(r'global\(\s*"([^"]+)"\s*\)', s)
    if m:
        g = m.group(1)
        title, detail = GLOBAL_LABELS.get(g, (f"Global · {g}", f"Sends Caelestia global signal «{g}»."))
        t = f"global {g}"
        return title, detail, t, t

    m = re.search(r'exec_cmd\(\s*"((?:\\.|[^"\\])*)"', s)
    if m:
        cmd = m.group(1).replace('\\"', '"')
        t, d, tech_s = describe_cmd(cmd)
        return t, d, tech_s, tech_s

    # exec_cmd(vars.xxx) without quotes — resolve real binary/command
    m = re.search(r"exec_cmd\(\s*vars\.(\w+)\s*\)", s)
    if m:
        v = m.group(1)
        real = vals.get(v, "")
        app_map = {
            "terminal": "Open terminal",
            "browser": "Open browser",
            "editor": "Open editor",
            "fileExplorer": "Open file manager",
            "audioSettings": "Audio settings",
            "sleepGestureCmd": "Sleep",
        }
        title = app_map.get(v) or VAR_LABELS.get(v) or f"Run · {v}"
        tech_var = f"exec vars.{v}"
        tech_real = f"exec {real}" if real else tech_var
        if real:
            detail = f"Runs «{real}»  (from vars.{v} in variables.lua)"
        else:
            detail = f"Runs vars.{v} (value not found in variables.lua)"
        return title, detail, tech_var, tech_real

    if "wsaction" in s:
        if "focus" in s and "group" in s:
            return ("Focus workspace group N", "Switches to workspace group N (1–10) on the current monitor.", tech, tech)
        if "move" in s and "group" in s:
            return ("Move window → workspace group N", "Moves the active window into workspace group N (1–10).", tech, tech)
        if "focus" in s:
            return ("Focus workspace N", "Switches to workspace number N (1–10).", tech, tech)
        if "move" in s:
            return ("Move window → workspace N", "Moves the active window to workspace N (1–10).", tech, tech)
    if "focus({" in s:
        if "workspace" in s:
            m = re.search(r'workspace\s*=\s*"?([^",}]+)"?', s)
            ws = m.group(1).strip() if m else "?"
            return (f"Focus workspace {ws}", f"Changes focus to workspace «{ws}».", tech, tech)
        if "direction" in s:
            m = re.search(r'direction\s*=\s*"(\w+)"', s)
            d = m.group(1) if m else "?"
            return (f"Focus {d}", f"Moves keyboard focus to the window on the {d}.", tech, tech)
        return ("Focus", "Changes window/monitor focus.", tech, tech)
    if "window.move" in s:
        if "special" in s:
            return ("Move → special workspace", "Sends the active window to the special (scratch) workspace.", tech, tech)
        if "out_of_group" in s:
            return ("Leave window group", "Pulls the active window out of its group.", tech, tech)
        if "workspace" in s:
            m = re.search(r'workspace\s*=\s*"?([^",}]+)"?', s)
            return (f"Move → workspace {m.group(1).strip() if m else '?'}", "Moves the active window to another workspace.", tech, tech)
        if "direction" in s:
            m = re.search(r'direction\s*=\s*"(\w+)"', s)
            return (f"Move window {m.group(1) if m else ''}".strip(), "Swaps/moves the window in a direction.", tech, tech)
        return ("Move window", "Moves the active window.", tech, tech)
    if "window.resize" in s:
        return ("Resize window", "Resizes the active window (keyboard or mouse).", tech, tech)
    if "window.drag" in s:
        return ("Drag window", "Click-drag to reposition a floating/tiled window.", tech, tech)
    if "window.close" in s:
        return ("Close window", "Closes the currently focused window.", tech, tech)
    if "window.float" in s:
        return ("Toggle floating", "Toggles floating mode for the active window.", tech, tech)
    if "window.fullscreen" in s:
        if "maximized" in s:
            return ("Maximize", "Maximizes the window while keeping decorations where applicable.", tech, tech)
        return ("Fullscreen", "Makes the active window fullscreen.", tech, tech)
    if "window.center" in s:
        return ("Center window", "Centers the floating window on the monitor.", tech, tech)
    if "window.pin" in s:
        return ("Pin window", "Pins the window so it stays visible across workspaces.", tech, tech)
    if "window.cycle_next" in s:
        if "next = false" in s:
            return ("Previous window", "Cycles focus to the previous window.", tech, tech)
        return ("Next window", "Cycles focus to the next window.", tech, tech)
    if "group." in s:
        if "next" in s:
            return ("Next in group", "Focuses the next window inside the group tab.", tech, tech)
        if "prev" in s:
            return ("Previous in group", "Focuses the previous window inside the group tab.", tech, tech)
        if "toggle" in s:
            return ("Toggle group", "Groups the active window with others / toggles group mode.", tech, tech)
        if "lock" in s:
            return ("Lock group", "Locks the active window group.", tech, tech)
    if "layout(" in s:
        return ("Toggle split", "Toggles the dwindle split direction.", tech, tech)
    if "function" in s:
        if "move_actions" in s or "pip" in s.lower():
            return ("Picture-in-picture", "Floats, resizes and pins the window as PiP.", tech, tech)
        if "caelestia shell" in s:
            return ("Restore shell + lock", "Restarts Caelestia shell and locks the session.", tech, tech)
        return ("Custom Lua action", "Runs a custom Lua function defined in the Hypr config.", tech, tech)
    return (compact(s), "System Hyprland / Caelestia action.", tech, tech)
def describe_cmd(cmd: str) -> tuple[str, str, str]:
    c = cmd.strip()
    known = {
        "caelestia toggle specialws": ("Toggle special workspace", "Shows/hides the special scratch workspace."),
        "caelestia toggle sysmon": ("System monitor workspace", "Toggles the system monitor special workspace."),
        "caelestia toggle music": ("Music workspace", "Toggles the music special workspace."),
        "caelestia toggle communication": ("Communication workspace", "Toggles chat/comms special workspace."),
        "caelestia toggle todo": ("Todo workspace", "Toggles the todo special workspace."),
        "caelestia screenshot": ("Screenshot", "Takes a screenshot via Caelestia."),
        "caelestia record -s": ("Record selection", "Starts recording a selected region."),
        "caelestia record": ("Record screen", "Starts a full-screen recording."),
        "caelestia record -r": ("Record region", "Records a chosen region."),
        "hyprpicker -a": ("Color picker", "Picks a screen color and copies it to the clipboard."),
        "pkill fuzzel || caelestia clipboard": ("Clipboard history", "Opens Caelestia clipboard history."),
        "pkill fuzzel || caelestia clipboard -d": ("Clipboard (delete mode)", "Clipboard history with delete mode."),
        "pkill fuzzel || caelestia emoji -p": ("Emoji picker", "Opens the emoji/glyph picker."),
        "qs -c caelestia kill": ("Kill Caelestia shell", "Stops the Caelestia Quickshell instance."),
        "systemctl suspend-then-hibernate": ("Sleep", "Suspends then hibernates the system."),
    }
    if c in known:
        t, d = known[c]
        return t, d, c
    if c == APP_BIN or c.endswith("caelestia-keybinds") or c.endswith("caelestia-binds"):
        return ("Open keybinds manager", "Opens the CaelestiaBinds window.", c)
    if "qs -c caelestia kill" in c and "shell -d" in c:
        return ("Restart Caelestia shell", "Kills and relaunches the Caelestia shell.", c)
    if c.startswith("wpctl set-mute @DEFAULT_AUDIO_SOURCE@"):
        return ("Mic mute", "Toggles mute on the default microphone.", c)
    if c.startswith("wpctl set-mute @DEFAULT_AUDIO_SINK@"):
        return ("Speaker mute", "Toggles mute on the default audio output.", c)
    if "wpctl set-volume" in c and "%+" in c:
        return ("Volume up", "Raises the default sink volume.", c)
    if "wpctl set-volume" in c and "%-" in c:
        return ("Volume down", "Lowers the default sink volume.", c)
    if c.startswith("notify-send"):
        return ("Test notification", "Sends a test notification through the shell.", c)
    if "ydotool type" in c:
        return ("Type clipboard", "Types the latest clipboard entry with ydotool.", c)
    if c.startswith("caelestia "):
        return (f"Caelestia · {c[10:]}", f"Runs: {c}", c)
    if c.startswith("hyprctl dispatch "):
        d = c[len("hyprctl dispatch ") :]
        return (f"Hypr · {d}", f"Dispatches Hyprland action «{d}».", c)
    return (f"Run · {c[:48]}{'…' if len(c) > 48 else ''}", f"Executes shell command:\n{c}", c)


def compact(s: str) -> str:
    s = re.sub(r"\s+", " ", s).strip()
    return s[:72] + ("…" if len(s) > 72 else "")


def split_first_arg(s: str) -> tuple[str, str]:
    depth = 0
    in_str = False
    quote = ""
    escape = False
    for i, ch in enumerate(s):
        if in_str:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == quote:
                in_str = False
            continue
        if ch in "\"'":
            in_str = True
            quote = ch
            continue
        if ch in "({[":
            depth += 1
        elif ch in ")}]":
            depth = max(0, depth - 1)
        elif ch == "," and depth == 0:
            return s[:i].strip(), s[i + 1 :].strip()
    return s.strip(), ""


def split_bind_args(inner: str) -> tuple[str, str, list[str]]:
    flags: list[str] = []
    flag_m = re.search(r",\s*(\{[^}]*\})\s*$", inner)
    if flag_m:
        for fm in re.finditer(r"(\w+)\s*=\s*true", flag_m.group(1)):
            flags.append(fm.group(1))
        inner = inner[: flag_m.start()].rstrip()
    keys, rest = split_first_arg(inner)
    return keys, rest.lstrip(",").strip(), flags


def parse_system_binds() -> list[Bind]:
    if not KEYBINDS_LUA.exists():
        return []
    text = KEYBINDS_LUA.read_text(errors="replace")
    var_keys = load_var_keys()
    var_values = load_var_values()
    binds: list[Bind] = []
    category = "General"
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith("---"):
            m = re.search(r"-+\s*(.+?)\s*-*$", stripped)
            if m:
                category = m.group(1).strip(" -")
            i += 1
            continue
        if stripped.startswith("--"):
            comment = stripped.lstrip("- ").strip()
            if comment and len(comment) < 60 and not comment.startswith("10 maps"):
                category = comment
            i += 1
            continue

        if re.match(r"for\s+i\s*=\s*1,\s*10\s+do", stripped):
            block: list[str] = []
            i += 1
            depth = 1
            while i < len(lines) and depth:
                l2 = lines[i]
                if re.search(r"\bdo\b", l2) and not l2.strip().startswith("--"):
                    depth += l2.count(" do")
                if re.match(r"\s*end\b", l2):
                    depth -= 1
                    if depth == 0:
                        break
                block.append(l2)
                i += 1
            for bl in block:
                bm = re.search(r"hl\.bind\((.+)\)\s*$", bl.strip())
                if not bm:
                    continue
                keys_raw, action_raw, flags = split_bind_args(bm.group(1))
                keys = resolve_key_expr(keys_raw.replace("key", "0-9"), var_keys)
                keys = re.sub(r"\bkey\b", "0-9", keys)
                title, detail, tech, tech_r = describe_action(action_raw, var_values)
                binds.append(
                    Bind(
                        id=f"sys-{len(binds)}",
                        keys=keys,
                        title=title + " (1–10)",
                        detail=detail,
                        category=category,
                        source="system",
                        flags=flags,
                        raw=bl.strip(),
                        technical=tech,
                        technical_resolved=tech_r,
                    )
                )
            i += 1
            continue

        if "hl.bind(" in stripped:
            chunk = stripped
            while chunk.count("(") > chunk.count(")") and i + 1 < len(lines):
                i += 1
                chunk += " " + lines[i].strip()
            m = re.search(r"hl\.bind\((.*)\)\s*$", chunk)
            if m:
                keys_raw, action_raw, flags = split_bind_args(m.group(1))
                keys = resolve_key_expr(keys_raw, var_keys)
                kvm = re.match(r"vars\.(\w+)", keys_raw.strip())
                title, detail, tech, tech_r = describe_action(action_raw, var_values)
                if kvm and kvm.group(1) in VAR_LABELS:
                    title = VAR_LABELS[kvm.group(1)]
                    if detail.startswith("System Hyprland") or len(detail) < 12:
                        detail = f"{title}. Bound via vars.{kvm.group(1)}."
                binds.append(
                    Bind(
                        id=f"sys-{len(binds)}-{keys}",
                        keys=keys,
                        title=title,
                        detail=detail,
                        category=category,
                        source="system",
                        flags=flags,
                        raw=chunk,
                        technical=tech,
                        technical_resolved=tech_r,
                    )
                )
        i += 1
    return binds


def custom_to_bind(b: dict[str, Any]) -> Bind:
    kind = b.get("kind", "exec")
    payload = b.get("payload", "")
    title = b.get("title") or ""
    detail = b.get("detail") or ""
    if not title or not detail:
        t2, d2, tech = describe_custom(kind, payload)
        title = title or t2
        detail = detail or d2
    else:
        tech = technical_for(kind, payload)
    # resolve vars.X in payload if present
    tech_r = tech
    m = re.match(r"(?:exec\s+)?vars\.(\w+)$", payload.strip())
    if m:
        real = resolve_var_cmd(m.group(1))
        if real:
            tech = f"exec vars.{m.group(1)}"
            tech_r = f"exec {real}"
            if not detail or "vars." in detail:
                detail = f"Runs «{real}»  (from vars.{m.group(1)})"
    return Bind(
        id=b.get("id") or str(uuid.uuid4()),
        keys=pretty_keys(b.get("keys", "")),
        title=title,
        detail=detail,
        category=b.get("category") or "Custom",
        source="custom",
        kind=kind,
        payload=payload,
        flags=list(b.get("flags") or []),
        raw=json.dumps(b, ensure_ascii=False),
        enabled=b.get("enabled", True),
        technical=tech,
        technical_resolved=tech_r,
    )


def describe_custom(kind: str, payload: str) -> tuple[str, str, str]:
    p = payload.strip()
    tech = technical_for(kind, p)
    if kind == "exec":
        if p == APP_BIN or p.endswith("caelestia-keybinds") or p.endswith("caelestia-binds"):
            return ("Open keybinds manager", "Opens the CaelestiaBinds window.", tech)
        return (f"Run · {Path(p.split()[0]).name if p else '?'}", f"Runs shell command:\n{p}", tech)
    if kind == "hypr":
        for d, label in HYPR_PRESETS:
            if d == p:
                return (label, f"Hyprland dispatcher: {p}", tech)
        return (f"Hypr · {p}", f"Dispatches Hyprland action «{p}».", tech)
    if kind == "global":
        g = p if p.startswith("caelestia:") else f"caelestia:{p}"
        t, d = GLOBAL_LABELS.get(g, (f"Global · {g}", f"Caelestia global signal «{g}»."))
        return t, d, tech
    if kind == "caelestia":
        return (f"Caelestia · {p}", f"Runs: caelestia {p}", tech)
    return ("Custom bind", p, tech)


def technical_for(kind: str, payload: str) -> str:
    p = payload.strip()
    if kind == "exec":
        return f"exec {p}"
    if kind == "hypr":
        return f"hyprctl dispatch {p}"
    if kind == "global":
        g = p if p.startswith("caelestia:") else f"caelestia:{p}"
        return f"global {g}"
    if kind == "caelestia":
        return f"caelestia {p}"
    return p


def load_all_binds(store: dict[str, Any]) -> list[Bind]:
    disabled = {norm_keys(k).lower() for k in store.get("disabled") or []}
    deleted = {norm_keys(k).lower() for k in store.get("deleted") or []}
    overrides = {norm_keys(k).lower(): v for k, v in (store.get("overrides") or {}).items()}

    out: list[Bind] = []
    for b in parse_system_binds():
        nk = norm_keys(b.keys).lower()
        # permanently deleted → gone from UI
        if nk in deleted:
            continue
        # template SUPER + 0-9: hide if every digit deleted? keep simple: exact key match only
        if nk in overrides:
            ov = overrides[nk]
            merged = custom_to_bind(
                {**ov, "id": f"override-{nk}", "category": ov.get("category") or b.category}
            )
            merged.source = "override"
            merged.detail = f"Overrides system bind.\n{merged.detail}"
            out.append(merged)
            continue
        if nk in disabled:
            b.enabled = False
            b.title = f"[disabled] {b.title}"
            b.detail = "Temporarily disabled. Use Re-enable to turn it back on. Delete removes it for real."
        out.append(b)

    for cb in store.get("binds") or []:
        nk = norm_keys(cb.get("keys", "")).lower()
        if nk in deleted:
            continue
        bind = custom_to_bind(cb)
        if not cb.get("enabled", True) or nk in disabled:
            bind.enabled = False
            if not bind.title.startswith("[disabled]"):
                bind.title = f"[disabled] {bind.title}"
        out.append(bind)

    def sort_key(b: Bind):
        prio = 0 if b.source == "custom" else 1 if b.source == "override" else 2
        return (prio, b.category.lower(), b.title.lower(), b.keys.lower())

    return sorted(out, key=sort_key)


# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------


def build_css(c: dict[str, str]) -> str:
    g = lambda n, f: c.get(n, f)
    bg = g("background", "#131317")
    surface = g("surfaceContainer", "#201f23")
    surface_lo = g("surfaceContainerLow", "#1c1b1f")
    surface_hi = g("surfaceContainerHigh", "#2a292e")
    surface_highest = g("surfaceContainerHighest", "#353438")
    on = g("onSurface", "#e5e1e7")
    on_var = g("onSurfaceVariant", "#c8c5d1")
    outline = g("outlineVariant", "#47464f")
    primary = g("primary", "#c2c1ff")
    on_primary = g("onPrimary", "#2a2a60")
    primary_c = g("primaryContainer", "#7171ac")
    secondary = g("secondary", "#c6c4e0")
    sec_c = g("secondaryContainer", "#45455c")
    tertiary = g("tertiary", "#f5b2e0")
    error = g("error", "#ffb4ab")
    success = g("success", "#B5CCBA")

    return f"""
    * {{
        font-family: "{FONT}", "Inter", "Noto Sans", sans-serif;
    }}
    window, .root {{
        background-color: {bg};
        color: {on};
    }}
    .sidebar {{
        background-color: {surface_lo};
        border-right: 1px solid alpha({outline}, 0.5);
    }}
    .brand {{
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.12em;
        color: {primary};
    }}
    .title {{
        font-size: 22px;
        font-weight: 700;
        color: {on};
    }}
    .subtitle {{
        font-size: 12px;
        color: {on_var};
    }}
    .search {{
        background-color: {surface};
        color: {on};
        border-radius: 16px;
        padding: 12px 16px;
        border: 1px solid alpha({outline}, 0.6);
        font-size: 14px;
    }}
    .search:focus {{
        border-color: {primary};
        box-shadow: 0 0 0 1px {primary};
    }}
    .nav-btn {{
        background: transparent;
        color: {on_var};
        border-radius: 12px;
        padding: 10px 14px;
        font-weight: 600;
        font-size: 13px;
        border: none;
    }}
    .nav-btn:hover {{
        background-color: alpha({primary}, 0.08);
        color: {on};
    }}
    .nav-btn.active {{
        background-color: alpha({primary}, 0.16);
        color: {primary};
    }}
    .accent {{
        background-color: {primary};
        color: {on_primary};
        border-radius: 14px;
        padding: 10px 16px;
        font-weight: 700;
        border: none;
    }}
    .accent:hover {{
        filter: brightness(1.08);
    }}
    .ghost {{
        background-color: {surface_hi};
        color: {on};
        border-radius: 12px;
        padding: 8px 12px;
        border: 1px solid alpha({outline}, 0.5);
        font-weight: 600;
    }}
    .ghost:hover {{
        border-color: {primary};
        color: {primary};
    }}
    .danger {{
        background-color: alpha({error}, 0.14);
        color: {error};
        border-radius: 12px;
        padding: 8px 12px;
        border: 1px solid alpha({error}, 0.3);
        font-weight: 600;
    }}
    .danger:hover {{
        background-color: alpha({error}, 0.22);
    }}
    .icon-danger {{
        background-color: alpha({error}, 0.12);
        color: {error};
        border-radius: 10px;
        padding: 4px 10px;
        border: 1px solid alpha({error}, 0.28);
        font-weight: 700;
        font-size: 13px;
        min-width: 28px;
    }}
    .icon-danger:hover {{
        background-color: alpha({error}, 0.28);
    }}
    .confirm-box {{
        background-color: {surface};
        border-radius: 18px;
        padding: 18px;
        border: 1px solid alpha({outline}, 0.5);
    }}
    .category {{
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.1em;
        color: {secondary};
        padding: 16px 4px 8px 4px;
    }}
    .bind-card {{
        background-color: {surface};
        border-radius: 16px;
        padding: 0;
        margin: 4px 0;
        border: 1px solid alpha({outline}, 0.4);
    }}
    .bind-card:hover {{
        background-color: {surface_hi};
        border-color: alpha({primary}, 0.35);
    }}
    .bind-card.selected {{
        background-color: {surface_highest};
        border-color: alpha({primary}, 0.65);
        box-shadow: 0 0 0 1px alpha({primary}, 0.25);
    }}
    .bind-card.disabled {{
        opacity: 0.55;
    }}
    .key-chip {{
        background-color: {sec_c};
        color: {secondary};
        border-radius: 10px;
        padding: 6px 12px;
        font-family: "JetBrains Mono", "Noto Sans Mono", monospace;
        font-weight: 700;
        font-size: 12px;
    }}
    .key-chip-custom {{
        background-color: {primary_c};
        color: white;
    }}
    .bind-title {{
        font-size: 14px;
        font-weight: 600;
        color: {on};
    }}
    .bind-detail {{
        font-size: 12px;
        color: {on_var};
    }}
    .badge {{
        border-radius: 999px;
        padding: 2px 8px;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 0.04em;
    }}
    .badge-custom {{
        background-color: alpha({primary}, 0.18);
        color: {primary};
    }}
    .badge-system {{
        background-color: alpha({secondary}, 0.14);
        color: {secondary};
    }}
    .badge-override {{
        background-color: alpha({tertiary}, 0.18);
        color: {tertiary};
    }}
    .badge-flag {{
        background-color: alpha({success}, 0.14);
        color: {success};
    }}
    .detail-panel {{
        background-color: {surface_lo};
        border-left: 1px solid alpha({outline}, 0.5);
    }}
    .detail-title {{
        font-size: 18px;
        font-weight: 700;
        color: {on};
    }}
    .detail-section {{
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.1em;
        color: {secondary};
        margin-top: 8px;
    }}
    .detail-body {{
        font-size: 13px;
        color: {on_var};
        line-height: 1.45;
    }}
    .mono-box {{
        background-color: {surface};
        border-radius: 12px;
        padding: 10px 12px;
        border: 1px solid alpha({outline}, 0.45);
        font-family: "JetBrains Mono", "Noto Sans Mono", monospace;
        font-size: 12px;
        color: {primary};
    }}
    .stat {{
        background-color: {surface};
        color: {on_var};
        border-radius: 999px;
        padding: 4px 12px;
        font-size: 12px;
        font-weight: 600;
    }}
    .toast {{
        background-color: {primary_c};
        color: white;
        border-radius: 12px;
        padding: 10px 16px;
        font-weight: 700;
    }}
    .dialog-frame {{
        background-color: {bg};
        border-radius: 20px;
        border: 1px solid alpha({outline}, 0.5);
        padding: 8px;
    }}
    entry, textview, .form-entry {{
        background-color: {surface};
        color: {on};
        border-radius: 12px;
        padding: 10px 12px;
        border: 1px solid alpha({outline}, 0.55);
    }}
    entry:focus, .form-entry:focus {{
        border-color: {primary};
    }}
    dropdown {{
        background-color: {surface};
        border-radius: 12px;
    }}
    checkbutton {{
        color: {on_var};
    }}
    scrolledwindow {{ background: transparent; }}
    scrollbar slider {{
        background-color: alpha({outline}, 0.7);
        border-radius: 99px;
        min-width: 8px;
    }}
    """


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------


