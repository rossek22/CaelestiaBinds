# CaelestiaBinds

Visual **keybind manager** for [Hyprland](https://hyprland.org/) + [Caelestia shell](https://github.com/caelestia-dots/shell).

Built with **real Caelestia Quickshell components** (same stack as Nexus):  
`StyledRect`, `IconButton`, `MaterialIcon`, `Colours`, `Tokens`, blobs, …

> Editing binds from raw lua/json files was annoying. This app is a GUI for that.

**Author:** [Rossek2](https://github.com/rossek22) · [rossek2.ru](https://rossek2.ru) · [Telegram](https://t.me/rossekdev2)

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

## Requirements

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

## Install

```bash
git clone https://github.com/rossek22/CaelestiaBinds.git ~/CaelestiaBinds
cd ~/CaelestiaBinds
./install.sh
caelestia-binds
```

`install.sh` will:

1. Link `~/.local/bin/caelestia-binds`
2. Link Quickshell config → `~/.config/quickshell/caelestia-binds`
3. Wire Caelestia UI components from the system package
4. Install a desktop entry

Optional Hypr bind:

```lua
hl.bind("SUPER + slash", hl.dsp.exec_cmd(os.getenv("HOME") .. "/.local/bin/caelestia-binds"))
```

## Uninstall

```bash
./uninstall.sh
```

User data is kept: `~/.config/caelestia/custom-keybinds.json`

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

MIT · see [LICENSE](LICENSE)
