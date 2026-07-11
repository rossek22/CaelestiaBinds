# CaelestiaBinds

Visual **keybind manager** for [Hyprland](https://hyprland.org/) + [Caelestia shell](https://github.com/caelestia-dots/shell).

Built with **real Caelestia Quickshell components** (same stack as Nexus):  
`StyledRect`, `IconButton`, `MaterialIcon`, `Colours`, `Tokens`, blobs, …

> Editing binds from raw lua/json files was annoying. This app is a GUI for that.

**Author:** [Rossek2](https://github.com/rossek22) · [rossek2.ru](https://rossek2.ru) · [Telegram](https://t.me/rossekdev2)

## Install

### Install (one-liner)

```bash
curl -fsSL https://raw.githubusercontent.com/rossek22/CaelestiaBinds/main/install.sh | bash
```

### Run

```bash
caelestia-binds
```

### Uninstall (one-liner)

```bash
curl -fsSL https://raw.githubusercontent.com/rossek22/CaelestiaBinds/main/uninstall.sh | bash
```

What the install does:

1. Clones (or updates) the repo into `~/CaelestiaBinds`
2. Links `~/.local/bin/caelestia-binds`
3. Wires Quickshell config + Caelestia UI components
4. Installs a desktop entry

Notes:

- Uninstall keeps bind data: `~/.config/caelestia/custom-keybinds.json`
- Keep the source tree on uninstall:

```bash
CAELESTIA_BINDS_KEEP_SOURCE=1 curl -fsSL https://raw.githubusercontent.com/rossek22/CaelestiaBinds/main/uninstall.sh | bash
```

- If `caelestia-binds` is not found, add `~/.local/bin` to `PATH`:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

### Dependencies

| Dep | Notes |
|-----|--------|
| Hyprland | lua / caelestia hypr layout |
| Quickshell (`qs`) | UI runtime |
| Caelestia shell | QML under `/etc/xdg/quickshell/caelestia` |
| Python 3.11+ | CLI / data layer |
| `wl-copy` | optional, copy buttons |

**Arch / CachyOS:**

```bash
sudo pacman -S quickshell python
# + caelestia-shell (AUR / your repo)
```

### Manual install (local clone)

```bash
git clone https://github.com/rossek22/CaelestiaBinds.git ~/CaelestiaBinds
cd ~/CaelestiaBinds
./install.sh
caelestia-binds
```

```bash
./uninstall.sh
```

### Optional Hypr bind

```lua
hl.bind("SUPER + slash", hl.dsp.exec_cmd(os.getenv("HOME") .. "/.local/bin/caelestia-binds"))
```

## Features

- Browse all Hyprland / Caelestia binds
- Search and filter (custom / system / overrides / disabled)
- Resolve `vars.*` → real command
- Create / edit / delete custom binds
- Disable (temporary) vs delete (permanent)
- Override system binds
- Key capture in the editor
- EN / RU UI (toggle bottom-left)
- About (project) + Author (me / setup / links)
- Live theme from Caelestia `scheme.json`

## Project layout

```
CaelestiaBinds/
├── bin/caelestia-binds
├── python/                 # core + CLI
├── quickshell/             # Caelestia qs UI
│   └── modules/keybinds/
├── assets/
├── share/applications/
├── packaging/PKGBUILD
├── install.sh / uninstall.sh
├── CONTRIBUTING.md
└── README.md
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for architecture, i18n, and PR tips.

## CLI

```bash
export CAELESTIA_BINDS_ROOT=~/CaelestiaBinds
python3 python/cli.py list
python3 python/cli.py delete <id>
python3 python/cli.py disable <id>
python3 python/cli.py enable <id>
python3 python/cli.py save-json '{"keys":"SUPER + B","kind":"exec","payload":"foot","title":"Term"}'
```

## Config files

| Path | Purpose |
|------|---------|
| `~/.config/caelestia/custom-keybinds.json` | Custom binds, overrides, disabled/deleted |
| `~/.config/caelestia/hypr-user.lua` | Generated Hypr binds (do not edit by hand) |
| `~/.config/caelestia/binds-ui.json` | UI prefs (language) |
| `~/.config/hypr/hyprland/keybinds.lua` | System Caelestia binds (touched on permanent delete) |

## Contributing

PRs and issues welcome.

1. Fork → feature branch
2. `./install.sh` and test UI + CLI paths
3. Add **both EN and RU** strings in `KeybindsI18n.qml` for new UI text
4. Open a PR with a short description (and screenshots for UI)

Details: **[CONTRIBUTING.md](CONTRIBUTING.md)**

## License

**[GPL-3.0-or-later](LICENSE)**

You can use, study, share and change this project freely (including in your own setups and forks).  
If you **distribute** modified or combined versions, the corresponding source **must stay open** under GPL-3.0 (or later).

In short: free to use, keep the code open source.
