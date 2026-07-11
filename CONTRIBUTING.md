# Contributing to CaelestiaBinds

Thanks for wanting to help. This project is a small keybind manager for **Hyprland + Caelestia shell**.

## Quick start

```bash
git clone https://github.com/rossek22/CaelestiaBinds.git
cd CaelestiaBinds
./install.sh
caelestia-binds
```

Requirements: Hyprland, Quickshell (`qs`), Caelestia shell QML under `/etc/xdg/quickshell/caelestia` (or `~/.config/quickshell/caelestia`), Python 3.11+.

After QML changes, restart the app (close the window and run `caelestia-binds` again). `install.sh` only needs re-running if you change install paths or add new top-level modules that are not already symlinked.

## Repo layout

```
CaelestiaBinds/
├── bin/caelestia-binds       # launcher (sets CAELESTIA_BINDS_ROOT)
├── python/                  # data layer
│   ├── core.py              # parse / write binds, hypr-user.lua
│   └── cli.py               # list | save-json | delete | disable | enable
├── quickshell/
│   ├── shell.qml
│   └── modules/keybinds/    # UI (real Caelestia components)
│       ├── KeybindsI18n.qml # EN/RU strings
│       ├── KeybindsNexus.qml
│       ├── KeybindsEditor.qml
│       └── ...
├── assets/                  # app assets (avatar, …)
├── share/                   # desktop entry + icon
├── install.sh / uninstall.sh
└── packaging/PKGBUILD       # optional Arch package
```

### UI vs data

| Layer | Tech | Responsibility |
|-------|------|----------------|
| UI | Quickshell QML | Lists, editor modal, About / Author, i18n |
| CLI | Python | Read system binds, CRUD custom JSON, generate `hypr-user.lua` |

Do **not** hand-edit `~/.config/caelestia/hypr-user.lua` in features; write through `python/core.py`.

## Coding notes

### QML

- Reuse Caelestia components: `StyledRect`, `IconButton`, `IconTextButton`, `MaterialIcon`, `Colours`, `Tokens`, blobs.
- Comments in QML: **Russian** is fine (project convention).
- UI user-facing strings: go through **`KeybindsI18n.t("key")`** with both `en` and `ru` entries. Do not leave hard-coded English in labels.
- Avoid em dashes (`—`) and double hyphens (`--`) in UI/comments (project style).
- Prefer keeping heavy views **mounted** and switching with `opacity` / `enabled` (less microfreezes than destroy/create).
- Modal editor must cover the **full** window and block wheel/clicks on the background.

### Python

- Keep CLI stable: `list`, `save-json`, `delete`, `disable`, `enable`, `reload`.
- `save-json` takes one JSON argv payload (UI uses this).
- Permanent delete ≠ disable. Do not merge those code paths.

### i18n

1. Add key to both `en` and `ru` maps in `KeybindsI18n.qml`.
2. Bind with `KeybindsI18n.t("…")` or `KeybindsI18n.tf("…", a, b)`.
3. For list models built from strings, depend on `KeybindsI18n.rev` so language switch refreshes labels.

Language preference is stored in `~/.config/caelestia/binds-ui.json`.

## Pull requests

1. Fork + branch from `main` (`feature/…` or `fix/…`).
2. Keep PRs focused (one concern).
3. Describe **what** and **why**; screenshots for UI changes.
4. Test on Caelestia + Hyprland if you can:
   - open app
   - create / edit / disable / delete a custom bind
   - switch EN ↔ RU
   - open About + Author
5. Do not commit `__pycache__`, personal configs, or huge binaries.

### PR checklist

- [ ] Builds / launches (`./install.sh` + `caelestia-binds`)
- [ ] No hard-coded UI strings (i18n keys added for EN + RU)
- [ ] Disable vs delete still distinct
- [ ] No secrets or absolute machine-only paths in code (use `CAELESTIA_BINDS_ROOT` / `$HOME`)

## Issues

Use GitHub Issues with:

- OS / distro (e.g. CachyOS)
- Hyprland + Caelestia / Quickshell versions if known
- Steps to reproduce
- Expected vs actual
- Logs from the terminal that launched `caelestia-binds` if relevant

## License

By contributing you agree your changes are licensed under **GPL-3.0-or-later** (see [LICENSE](LICENSE)).
