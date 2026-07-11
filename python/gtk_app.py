#!/usr/bin/env python3
"""Caelestia Keybinds — pixel-close Nexus (settings) layout & components."""

from __future__ import annotations

import sys
import uuid
from pathlib import Path

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("Gio", "2.0")
gi.require_version("Gdk", "4.0")
from gi.repository import Adw, Gdk, Gio, GLib, Gtk, Pango

sys.path.insert(0, str(Path(__file__).resolve().parent))
from core import (  # noqa: E402
    ACTION_PRESETS,
    APP_ID,
    FONT,
    HYPR_PRESETS,
    KEYBINDS_LUA,
    Bind,
    describe_custom,
    load_all_binds,
    load_scheme,
    load_store,
    norm_keys,
    pretty_keys,
    remove_bind_from_system_lua,
    save_store,
    write_hypr_user_lua,
)

MS_FONT = "Material Symbols Rounded"
MS_TTF = "/usr/share/fonts/TTF/MaterialSymbolsRounded[FILL,GRAD,opsz,wght].ttf"

# Nexus-ish tokens (from Caelestia Tokens usage)
PAD_SM, PAD_MD, PAD_LG, PAD_XL = 8, 12, 16, 24
R_SM, R_MD, R_LG, R_XL, R_FULL = 8, 12, 16, 24, 9999


def build_css(c: dict[str, str]) -> str:
    g = lambda n, f: c.get(n, f)
    # Nexus window uses m3surface / surfaceContainerLow for blobs
    surface = g("surface", g("background", "#131317"))
    surface_lo = g("surfaceContainerLow", "#1c1b1f")
    surface_c = g("surfaceContainer", "#201f23")
    surface_hi = g("surfaceContainerHigh", "#2a292e")
    surface_lowest = g("surfaceContainerLowest", "#0e0e12")
    on = g("onSurface", "#e5e1e7")
    on_var = g("onSurfaceVariant", "#c8c5d1")
    outline = g("outlineVariant", "#47464f")
    primary = g("primary", "#c2c1ff")
    on_primary = g("onPrimary", "#2a2a60")
    primary_c = g("primaryContainer", "#7171ac")
    secondary = g("secondary", "#c6c4e0")
    sec_c = g("secondaryContainer", "#45455c")
    on_sec_c = g("onSecondaryContainer", "#b4b2ce")
    error = g("error", "#ffb4ab")

    return f"""
    * {{
        font-family: "{FONT}", "Inter", "Noto Sans", sans-serif;
    }}

    window {{
        background-color: {surface};
        color: {on};
    }}

    .root {{
        background-color: {surface};
        transition: opacity 320ms cubic-bezier(0.2, 0, 0, 1);
    }}

    /* —— Material icons —— */
    .ms {{
        font-family: "Material Symbols Rounded", sans-serif;
        font-weight: 400;
        font-size: 22px;
        letter-spacing: 0;
        color: {on_var};
    }}
    .ms-on-primary {{ color: {on_primary}; }}
    .ms-on-sec {{ color: {on_sec_c}; }}
    .ms-primary {{ color: {primary}; }}
    .ms-error {{ color: {error}; }}
    .ms-sm {{ font-size: 18px; }}
    .ms-md {{ font-size: 20px; }}

    /* —— Search (SearchBar.qml) —— */
    .search-shell {{
        background-color: {surface_lowest};
        border-radius: {R_FULL}px;
        border: 1px solid {outline};
        min-height: 48px;
        padding: 0 4px 0 4px;
    }}
    .search-entry {{
        background: transparent;
        color: {on_var};
        border: none;
        box-shadow: none;
        font-size: 15px;
        padding: 10px 8px;
        outline: none;
    }}
    .search-entry:focus {{
        border: none;
        box-shadow: none;
        outline: none;
    }}
    .search-entry placeholder {{
        color: {on_var};
        opacity: 0.75;
    }}

    /* —— Nav items (NavLocations ConnectedRect) —— */
    .nav-item {{
        background-color: alpha({surface_hi}, 0.92);
        border-radius: {R_XL}px;
        border: none;
        transition: all 180ms cubic-bezier(0.2, 0, 0, 1);
        min-height: 64px;
    }}
    .nav-item:hover {{
        background-color: {surface_hi};
        filter: brightness(1.06);
    }}
    .nav-item.active {{
        background-color: {sec_c};
        border-radius: 28px;
    }}
    .nav-icon-circle {{
        background-color: {sec_c};
        border-radius: {R_FULL}px;
        min-width: 40px;
        min-height: 40px;
    }}
    .nav-item.active .nav-icon-circle {{
        background-color: {primary};
    }}
    .nav-item.active .ms-on-sec {{
        color: {on_primary};
    }}
    .nav-title {{
        font-size: 14px;
        font-weight: 500;
        color: {on};
    }}
    .nav-sub {{
        font-size: 12px;
        color: {on_var};
    }}

    /* —— Page title (PageBase) —— */
    .page-title {{
        font-size: 28px;
        font-weight: 500;
        color: {on};
        letter-spacing: -0.02em;
    }}
    .page-sub {{
        font-size: 13px;
        color: {on_var};
    }}
    .section-label {{
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.08em;
        color: {on_var};
        opacity: 0.7;
    }}

    /* —— Close pip (Nexus windowBtn) —— */
    .close-pip {{
        background-color: alpha({surface_hi}, 0.9);
        border-radius: {R_FULL}px;
        min-width: 40px;
        min-height: 40px;
        border: none;
        padding: 0;
        transition: all 150ms cubic-bezier(0.2, 0, 0, 1);
    }}
    .close-pip:hover {{
        background-color: alpha({error}, 0.2);
    }}
    .close-pip:hover .ms {{
        color: {error};
    }}

    /* —— Tonal / filled pills (Wallpapers / Colours buttons) —— */
    .pill-tonal {{
        background-color: {sec_c};
        color: {on_sec_c};
        border-radius: {R_FULL}px;
        padding: 10px 18px;
        font-weight: 500;
        border: none;
        transition: all 150ms cubic-bezier(0.2, 0, 0, 1);
    }}
    .pill-tonal:hover {{ filter: brightness(1.1); }}

    .pill-filled {{
        background-color: {primary};
        color: {on_primary};
        border-radius: {R_FULL}px;
        padding: 10px 18px;
        font-weight: 600;
        border: none;
    }}
    .pill-filled:hover {{ filter: brightness(1.08); }}

    .pill-text {{
        background: transparent;
        color: {primary};
        border-radius: {R_FULL}px;
        padding: 8px 14px;
        font-weight: 600;
        border: none;
    }}
    .pill-text:hover {{ background-color: alpha({primary}, 0.12); }}

    .pill-danger {{
        background-color: alpha({error}, 0.14);
        color: {error};
        border-radius: {R_FULL}px;
        padding: 10px 18px;
        font-weight: 600;
        border: none;
    }}
    .pill-danger:hover {{ background-color: alpha({error}, 0.22); }}

    /* —— Connected rows (ToggleRow / ConnectedRect) —— */
    .row {{
        background-color: {surface_c};
        border: none;
        transition: background 150ms cubic-bezier(0.2, 0, 0, 1);
        min-height: 56px;
    }}
    .row.first {{
        border-top-left-radius: {R_XL}px;
        border-top-right-radius: {R_XL}px;
    }}
    .row.last {{
        border-bottom-left-radius: {R_XL}px;
        border-bottom-right-radius: {R_XL}px;
    }}
    .row.only {{
        border-radius: {R_XL}px;
    }}
    .row.mid {{
        border-radius: {R_SM}px;
    }}
    .row:hover {{
        background-color: {surface_hi};
    }}
    .row.selected {{
        background-color: {sec_c};
    }}
    .row.disabled {{
        opacity: 0.5;
    }}

    .key-chip {{
        background-color: alpha({sec_c}, 1);
        color: {secondary};
        border-radius: 10px;
        padding: 4px 10px;
        font-family: "JetBrains Mono", "Noto Sans Mono", monospace;
        font-weight: 700;
        font-size: 11px;
    }}
    .key-chip-accent {{
        background-color: {primary_c};
        color: white;
    }}
    .row-title {{
        font-size: 14px;
        font-weight: 500;
        color: {on};
    }}
    .row-sub {{
        font-size: 12px;
        color: {on_var};
    }}
    .badge {{
        border-radius: {R_FULL}px;
        padding: 2px 8px;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 0.03em;
        background-color: alpha({on_var}, 0.12);
        color: {on_var};
    }}
    .badge-custom {{ background-color: alpha({primary}, 0.16); color: {primary}; }}
    .badge-override {{ background-color: alpha({secondary}, 0.2); color: {secondary}; }}

    .mono {{
        background-color: {surface_c};
        border-radius: {R_LG}px;
        padding: 12px 14px;
        font-family: "JetBrains Mono", "Noto Sans Mono", monospace;
        font-size: 12px;
        color: {primary};
    }}
    .hero {{
        background-color: {surface_c};
        border-radius: {R_XL}px;
        padding: 20px;
    }}
    .stat {{
        background-color: {surface_c};
        color: {on_var};
        border-radius: {R_FULL}px;
        padding: 4px 12px;
        font-size: 12px;
        font-weight: 500;
    }}
    .toast {{
        background-color: {primary_c};
        color: white;
        border-radius: 14px;
        padding: 10px 16px;
        font-weight: 600;
    }}
    .form-entry {{
        background-color: {surface_hi};
        color: {on};
        border-radius: {R_LG}px;
        padding: 12px 14px;
        border: none;
    }}
    .form-entry:focus {{
        box-shadow: 0 0 0 2px alpha({primary}, 0.35);
    }}
    .confirm {{
        background-color: {surface_c};
        border-radius: {R_XL}px;
        padding: 20px;
    }}

    scrolledwindow, viewport {{ background: transparent; }}
    scrollbar {{ opacity: 0.35; }}
    scrollbar slider {{
        background-color: {outline};
        border-radius: 99px;
        min-width: 5px;
    }}
    checkbutton {{ color: {on_var}; }}

    /* —— appearance animations —— */
    .fade-in {{
        opacity: 0;
        transition: opacity 280ms cubic-bezier(0.2, 0, 0, 1);
    }}
    .fade-in.visible {{
        opacity: 1;
    }}
    .row.appear {{
        opacity: 0;
        transition: opacity 220ms cubic-bezier(0.2, 0, 0, 1),
                    margin-top 220ms cubic-bezier(0.2, 0, 0, 1);
        margin-top: 10px;
    }}
    .row.appear.visible {{
        opacity: 1;
        margin-top: 0;
    }}
    .nav-item.appear {{
        opacity: 0;
        transition: opacity 200ms cubic-bezier(0.2, 0, 0, 1);
    }}
    .nav-item.appear.visible {{
        opacity: 1;
    }}
    .hero.appear, .detail-actions.appear {{
        opacity: 0;
        transition: opacity 260ms cubic-bezier(0.2, 0, 0, 1);
    }}
    .hero.appear.visible, .detail-actions.appear.visible {{
        opacity: 1;
    }}

    /* —— adaptive —— */
    .nav-pane.compact {{
        min-width: 220px;
    }}
    .nav-pane.hidden {{
        opacity: 0;
    }}
    .menu-btn {{
        background-color: {sec_c};
        color: {on_sec_c};
        border-radius: {R_FULL}px;
        min-width: 40px;
        min-height: 40px;
        border: none;
        padding: 0;
    }}
    .menu-btn:hover {{ filter: brightness(1.1); }}
    .page-title.compact {{
        font-size: 22px;
    }}

    /* —— scroll edge fades (VerticalFadeFlickable) —— */
    .fade-edge-top, .fade-edge-bottom {{
        background-size: 100% 100%;
        min-height: 28px;
        opacity: 0;
        transition: opacity 280ms cubic-bezier(0.2, 0, 0, 1);
    }}
    .fade-edge-top {{
        background-image: linear-gradient(
            to bottom,
            {surface} 0%,
            alpha({surface}, 0.0) 100%
        );
    }}
    .fade-edge-bottom {{
        background-image: linear-gradient(
            to top,
            {surface} 0%,
            alpha({surface}, 0.0) 100%
        );
    }}
    .fade-edge-top.active, .fade-edge-bottom.active {{
        opacity: 1;
    }}

    /* page content slide host (Pages.qml) */
    .page-host {{
        transition: opacity 180ms cubic-bezier(0.2, 0, 0, 1);
    }}
    """


# icon, label, description — mirror settings nav density
NAV = [
    ("all", "keyboard", "All binds", "Everything currently active"),
    ("custom", "tune", "Custom", "Your own shortcuts"),
    ("system", "memory", "System", "Caelestia / Hyprland defaults"),
    ("override", "swap_horiz", "Overrides", "System binds you replaced"),
    ("disabled", "block", "Disabled", "Temporarily turned off"),
]


def icon(name: str, *classes: str) -> Gtk.Label:
    lab = Gtk.Label(label=name)
    lab.add_css_class("ms")
    for c in classes:
        lab.add_css_class(c)
    return lab


def pill_button(label: str, icon_name: str | None, css: str, cb) -> Gtk.Button:
    btn = Gtk.Button()
    btn.add_css_class(css)
    box = Gtk.Box(spacing=8)
    box.set_halign(Gtk.Align.CENTER)
    if icon_name:
        box.append(icon(icon_name, "ms-sm"))
    box.append(Gtk.Label(label=label))
    btn.set_child(box)

    def _on_click(*_args):
        try:
            cb()
        except TypeError:
            # if cb expects event args, ignore
            cb()

    btn.connect("clicked", _on_click)
    return btn


def animate_in(widget: Gtk.Widget, delay_ms: int = 0):
    """Fade/slide-in via CSS class toggle."""
    widget.add_css_class("appear")
    widget.set_opacity(0)

    def show():
        widget.add_css_class("visible")
        widget.set_opacity(1)
        return False

    if delay_ms <= 0:
        # next frame so transition can start from 0
        GLib.idle_add(show)
    else:
        GLib.timeout_add(delay_ms, show)


class SmoothRubberScroll:
    """Smooth scrolling + rubber-band overshoot (Qt Flickable style).

    GTK ScrolledWindow has no real elastic overscroll — we fake it by
    translating the content holder with margin when past edges, then spring back.
    """

    MAX_OVER = 140.0
    # how much of wheel delta becomes overscroll (with resistance)
    OVER_GAIN = 10.0
    # smooth lerp for in-bounds scrolling
    SMOOTH = 0.28
    # spring back when released / idle
    SPRING = 0.22
    # in-bounds wheel gain (pixels per unit dy)
    WHEEL_GAIN = 48.0

    def __init__(self, scroll: Gtk.ScrolledWindow, holder: Gtk.Widget):
        self.scroll = scroll
        self.holder = holder
        self.over = 0.0  # <0 past top, >0 past bottom
        self.target: float | None = None
        self._smooth_src = 0
        self._spring_src = 0
        self._active = False

        # capture vertical scroll (trackpad + wheel). no DISCRETE → smooth deltas
        flags = (
            Gtk.EventControllerScrollFlags.VERTICAL
            | Gtk.EventControllerScrollFlags.KINETIC
        )
        ctl = Gtk.EventControllerScroll.new(flags)
        ctl.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        ctl.connect("scroll", self._on_scroll)
        try:
            ctl.connect("scroll-end", self._on_scroll_end)
        except TypeError:
            pass
        try:
            ctl.connect("decelerate", self._on_decelerate)
        except TypeError:
            pass
        # put on scroll window so we get events over the whole area
        scroll.add_controller(ctl)

    def reset(self):
        self.over = 0.0
        self.target = None
        self._apply_over()
        self._stop_smooth()
        self._stop_spring()

    def _adj(self):
        return self.scroll.get_vadjustment()

    def _limits(self):
        adj = self._adj()
        if adj is None:
            return 0.0, 0.0, 0.0
        lower = adj.get_lower()
        page = adj.get_page_size()
        upper = adj.get_upper()
        max_v = max(lower, upper - page)
        return lower, max_v, adj.get_value()

    def _apply_over(self):
        # resistance curve → visual displacement
        o = self.over
        # soft clamp
        if o > self.MAX_OVER:
            o = self.MAX_OVER + (o - self.MAX_OVER) * 0.15
        elif o < -self.MAX_OVER:
            o = -self.MAX_OVER + (o + self.MAX_OVER) * 0.15
        # display with extra damp
        vis = o * 0.55
        # past top (over<0): positive margin → content down
        # past bottom (over>0): negative margin → content up
        self.holder.set_margin_top(int(round(-vis)))

    def _on_scroll(self, _ctl, _dx, dy: float) -> bool:
        # dy > 0 → user scrolls content down (finger/wheel "down")
        adj = self._adj()
        if adj is None:
            return False

        lower, max_v, value = self._limits()
        delta = dy * self.WHEEL_GAIN

        # already in rubber zone
        if abs(self.over) > 0.01:
            resistance = 1.0 / (1.0 + abs(self.over) / 50.0)
            self.over += dy * self.OVER_GAIN * resistance
            # pull back into bounds if user scrolls reverse hard
            if self.over < 0 and dy > 0:
                # scrolling down while past top — reduce over then enter content
                self.over += dy * self.OVER_GAIN * resistance
                if self.over >= 0:
                    self.over = 0
                    self._apply_over()
                    self.target = min(max_v, lower + delta * 0.3)
                    self._start_smooth()
                    return True
            elif self.over > 0 and dy < 0:
                self.over += dy * self.OVER_GAIN * resistance
                if self.over <= 0:
                    self.over = 0
                    self._apply_over()
                    self.target = max(lower, max_v + delta * 0.3)
                    self._start_smooth()
                    return True
            self._apply_over()
            self._start_spring_delayed()
            return True

        # proposed new scroll position
        base = self.target if self.target is not None else value
        proposed = base + delta

        if proposed < lower:
            # hit top edge → rubber
            adj.set_value(lower)
            self.target = lower
            overflow = lower - proposed
            resistance = 1.0 / (1.0 + abs(self.over) / 50.0)
            self.over = -overflow * 0.45 * resistance
            self._apply_over()
            self._stop_smooth()
            self._start_spring_delayed()
            return True

        if proposed > max_v:
            adj.set_value(max_v)
            self.target = max_v
            overflow = proposed - max_v
            resistance = 1.0 / (1.0 + abs(self.over) / 50.0)
            self.over = overflow * 0.45 * resistance
            self._apply_over()
            self._stop_smooth()
            self._start_spring_delayed()
            return True

        # in bounds — smooth scroll
        self.over = 0.0
        self._apply_over()
        self.target = proposed
        self._start_smooth()
        return True  # consume so GTK doesn't double-scroll

    def _on_scroll_end(self, *_a):
        self._start_spring()
        return False

    def _on_decelerate(self, _ctl, vel_x, vel_y):
        # kinetic fling — convert residual velocity into smooth target or overscroll
        adj = self._adj()
        if adj is None:
            return
        lower, max_v, value = self._limits()
        # vel_y units are rough; scale down
        fling = vel_y * 0.08
        proposed = value + fling
        if proposed < lower:
            self.over = min(0.0, (proposed - lower) * 0.2)
            adj.set_value(lower)
            self._apply_over()
            self._start_spring()
        elif proposed > max_v:
            self.over = max(0.0, (proposed - max_v) * 0.2)
            adj.set_value(max_v)
            self._apply_over()
            self._start_spring()
        else:
            self.target = proposed
            self._start_smooth()

    def _start_smooth(self):
        self._stop_spring()
        if self._smooth_src:
            return
        self._smooth_src = GLib.timeout_add(12, self._tick_smooth)

    def _stop_smooth(self):
        if self._smooth_src:
            GLib.source_remove(self._smooth_src)
            self._smooth_src = 0

    def _tick_smooth(self):
        adj = self._adj()
        if adj is None or self.target is None:
            self._smooth_src = 0
            return False
        lower, max_v, value = self._limits()
        target = max(lower, min(max_v, self.target))
        self.target = target
        diff = target - value
        if abs(diff) < 0.4:
            adj.set_value(target)
            self.target = None
            self._smooth_src = 0
            return False
        adj.set_value(value + diff * self.SMOOTH)
        return True

    def _start_spring_delayed(self):
        # short delay so continuous wheel still builds rubber, then settle
        self._stop_spring()
        self._spring_src = GLib.timeout_add(90, self._begin_spring)

    def _begin_spring(self):
        self._spring_src = 0
        self._start_spring()
        return False

    def _start_spring(self):
        if self._spring_src:
            return
        self._spring_src = GLib.timeout_add(12, self._tick_spring)

    def _stop_spring(self):
        if self._spring_src:
            GLib.source_remove(self._spring_src)
            self._spring_src = 0

    def _tick_spring(self):
        if abs(self.over) < 0.4:
            self.over = 0.0
            self._apply_over()
            self._spring_src = 0
            return False
        # critically-damped-ish spring toward 0
        self.over *= 1.0 - self.SPRING
        self.over -= self.over * 0.08
        self._apply_over()
        return True


class KeybindsApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id=APP_ID, flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.window: Gtk.ApplicationWindow | None = None
        self.store = load_store()
        self.binds: list[Bind] = []
        self.filtered: list[Bind] = []
        self.scheme = load_scheme()
        self.css = Gtk.CssProvider()
        self.selected: Bind | None = None
        self.nav_filter = "all"
        self.nav_btns: dict[str, Gtk.Widget] = {}
        self._monitors: list = []
        self._toast_src = 0
        self._reload_src = 0
        self._layout_mode = "wide"  # wide | medium | narrow
        self._nav_revealed = True

        self.search: Gtk.Entry | None = None
        self.list_box: Gtk.Box | None = None
        self.stat: Gtk.Label | None = None
        self.toast_lab: Gtk.Label | None = None
        self.stack: Gtk.Stack | None = None
        self.detail_box: Gtk.Box | None = None
        self.detail_scroll: Gtk.ScrolledWindow | None = None
        self.page_title: Gtk.Label | None = None
        self.page_sub: Gtk.Label | None = None
        self.header_actions: Gtk.Box | None = None
        self.nav_pane: Gtk.Box | None = None
        self.content_pane: Gtk.Box | None = None
        self.root_box: Gtk.Box | None = None
        self.menu_btn: Gtk.Button | None = None
        self.nav_revealer: Gtk.Revealer | None = None
        self.list_scroll: Gtk.ScrolledWindow | None = None
        self.list_host: Gtk.Box | None = None
        self.list_overlay: Gtk.Overlay | None = None
        self.list_fade_top: Gtk.Box | None = None
        self.list_fade_bot: Gtk.Box | None = None
        self.detail_fade_top: Gtk.Box | None = None
        self.detail_fade_bot: Gtk.Box | None = None
        self.nav_scroll: Gtk.ScrolledWindow | None = None
        self.nav_fade_top: Gtk.Box | None = None
        self.nav_fade_bot: Gtk.Box | None = None
        self._nav_idx = 0
        self._page_anim_src = 0
        self._page_animating = False
        self._rubber: list[SmoothRubberScroll] = []

    def do_activate(self):
        if self.window:
            self.window.present()
            return
        self.scheme = load_scheme()
        self.apply_css()
        self.build()
        self.reload()
        self.watch()
        # entrance fade
        if self.root_box:
            self.root_box.set_opacity(0)
            self.window.present()

            def fade_root():
                if self.root_box:
                    self.root_box.set_opacity(1)
                return False

            GLib.timeout_add(30, fade_root)
        else:
            self.window.present()

    def apply_css(self):
        self.css.load_from_data(build_css(self.scheme).encode())
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(), self.css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    # ─────────────────────────────────────────────────────────────
    # Layout: exact Nexus chrome
    #   [ search + nav ]  |  [ title · actions · close ]
    #                     |  [ content stack ]
    # ─────────────────────────────────────────────────────────────

    def build(self):
        win = Gtk.ApplicationWindow(application=self, title="Nexus — Keybinds")
        win.set_default_size(1040, 680)
        win.set_size_request(420, 420)
        self.window = win

        root = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        root.add_css_class("root")
        win.set_child(root)
        self.root_box = root

        # ── LEFT NAV (in Revealer for narrow mode) ──
        self.nav_revealer = Gtk.Revealer()
        self.nav_revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_RIGHT)
        self.nav_revealer.set_transition_duration(240)
        self.nav_revealer.set_reveal_child(True)
        root.append(self.nav_revealer)

        nav = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=PAD_LG)
        nav.add_css_class("nav-pane")
        nav.set_size_request(300, -1)
        nav.set_margin_top(PAD_XL)
        nav.set_margin_bottom(PAD_XL)
        nav.set_margin_start(PAD_XL)
        nav.set_margin_end(PAD_MD)
        self.nav_pane = nav
        self.nav_revealer.set_child(nav)

        # SearchBar clone
        search_shell = Gtk.Box(spacing=6)
        search_shell.add_css_class("search-shell")
        search_shell.set_margin_bottom(4)
        nav.append(search_shell)

        search_icon = icon("search", "ms-md")
        search_icon.set_margin_start(14)
        search_icon.set_valign(Gtk.Align.CENTER)
        search_shell.append(search_icon)

        self.search = Gtk.Entry(placeholder_text="Search binds")
        self.search.add_css_class("search-entry")
        self.search.set_hexpand(True)
        self.search.set_has_frame(False)
        search_shell.append(self.search)

        clear = Gtk.Button()
        clear.add_css_class("close-pip")
        clear.set_child(icon("close", "ms-sm"))
        clear.set_margin_end(6)
        clear.set_valign(Gtk.Align.CENTER)
        clear.set_opacity(0)
        clear.set_sensitive(False)

        def on_search_changed(*_):
            has = bool(self.search.get_text())
            clear.set_opacity(1 if has else 0)
            clear.set_sensitive(has)
            self.apply_filter()

        self.search.connect("changed", on_search_changed)
        clear.connect("clicked", lambda *_: self.search.set_text(""))
        search_shell.append(clear)

        # Nav list with edge fades + rubber scroll
        nav_overlay, nav_scroll, nav_holder, nav_ft, nav_fb = self._make_fade_scroll()
        nav_overlay.set_vexpand(True)
        nav.append(nav_overlay)
        self.nav_scroll = nav_scroll
        self.nav_fade_top = nav_ft
        self.nav_fade_bot = nav_fb

        nav_list = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        nav_holder.append(nav_list)

        for i, (key, ic, title, sub) in enumerate(NAV):
            btn = self.make_nav(key, ic, title, sub)
            self.nav_btns[key] = btn
            nav_list.append(btn)
            animate_in(btn, 40 + i * 35)

        self._bind_scroll_fades(nav_scroll, nav_ft, nav_fb)

        # ── RIGHT CONTENT ──
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        content.set_hexpand(True)
        content.set_margin_top(PAD_XL)
        content.set_margin_bottom(PAD_XL)
        content.set_margin_end(PAD_XL)
        content.set_margin_start(PAD_MD)
        root.append(content)
        self.content_pane = content

        # Header: menu (narrow) · title · actions · close
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=PAD_MD)
        header.set_margin_bottom(PAD_LG)
        content.append(header)

        self.menu_btn = Gtk.Button()
        self.menu_btn.add_css_class("menu-btn")
        self.menu_btn.set_child(icon("menu", "ms-md", "ms-on-sec"))
        self.menu_btn.set_valign(Gtk.Align.CENTER)
        self.menu_btn.set_visible(False)
        self.menu_btn.set_tooltip_text("Toggle navigation")
        self.menu_btn.connect("clicked", lambda *_: self.toggle_nav())
        header.append(self.menu_btn)

        titles = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        titles.set_hexpand(True)
        header.append(titles)

        self.page_title = Gtk.Label(label="All binds", xalign=0)
        self.page_title.add_css_class("page-title")
        self.page_title.set_ellipsize(Pango.EllipsizeMode.END)
        titles.append(self.page_title)

        self.page_sub = Gtk.Label(label="Everything currently active", xalign=0)
        self.page_sub.add_css_class("page-sub")
        self.page_sub.set_ellipsize(Pango.EllipsizeMode.END)
        titles.append(self.page_sub)

        self.header_actions = Gtk.Box(spacing=8)
        self.header_actions.set_valign(Gtk.Align.CENTER)
        header.append(self.header_actions)

        self.header_actions.append(
            pill_button("New bind", "add", "pill-tonal", lambda: self.open_editor())
        )
        self.header_actions.append(
            pill_button("Refresh", "refresh", "pill-tonal", lambda: self.reload(flash=True))
        )

        close = Gtk.Button()
        close.add_css_class("close-pip")
        close.set_child(icon("close", "ms-md"))
        close.set_valign(Gtk.Align.START)
        close.connect("clicked", lambda *_: win.close())
        header.append(close)

        self.stat = Gtk.Label(label="", xalign=0)
        self.stat.add_css_class("stat")
        self.stat.set_halign(Gtk.Align.START)
        self.stat.set_margin_bottom(PAD_MD)
        content.append(self.stat)

        # Stack list ↔ detail — Nexus-style transitions
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(280)
        self.stack.set_vexpand(True)
        content.append(self.stack)

        # list page: host animates on nav switch (Pages.qml pattern)
        list_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.stack.add_named(list_page, "list")

        self.list_host = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.list_host.add_css_class("page-host")
        self.list_host.set_vexpand(True)
        list_page.append(self.list_host)

        list_overlay, list_scroll, list_holder, list_ft, list_fb = self._make_fade_scroll()
        list_overlay.set_vexpand(True)
        self.list_host.append(list_overlay)
        self.list_overlay = list_overlay
        self.list_scroll = list_scroll
        self.list_fade_top = list_ft
        self.list_fade_bot = list_fb

        self.list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        self.list_box.set_margin_bottom(8)
        self.list_box.set_margin_top(4)
        list_holder.append(self.list_box)
        self._bind_scroll_fades(list_scroll, list_ft, list_fb)

        # detail with edge fades + rubber
        detail_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.stack.add_named(detail_page, "detail")

        det_overlay, det_scroll, det_holder, det_ft, det_fb = self._make_fade_scroll()
        det_overlay.set_vexpand(True)
        detail_page.append(det_overlay)
        self.detail_scroll = det_scroll
        self.detail_fade_top = det_ft
        self.detail_fade_bot = det_fb

        self.detail_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=PAD_LG)
        self.detail_box.set_margin_bottom(12)
        self.detail_box.set_margin_top(4)
        det_holder.append(self.detail_box)
        self._bind_scroll_fades(det_scroll, det_ft, det_fb)

        toast_row = Gtk.Box()
        toast_row.set_margin_top(8)
        content.append(toast_row)
        self.toast_lab = Gtk.Label(label="")
        self.toast_lab.add_css_class("toast")
        self.toast_lab.set_visible(False)
        toast_row.append(self.toast_lab)

        self.stack.set_visible_child_name("list")
        self.set_nav("all", rebuild=False)

        kc = Gtk.EventControllerKey()
        kc.connect("key-pressed", self.on_key)
        win.add_controller(kc)

        # adaptive: recompute layout on resize
        win.connect("notify::default-width", self._on_size_hint)
        win.connect("notify::default-height", self._on_size_hint)
        win.connect("map", lambda *_: GLib.timeout_add(80, self._apply_layout_from_window))

        def on_realize(w):
            surface = w.get_surface()
            if surface is not None:
                try:
                    surface.connect("layout", lambda *_a: self._apply_layout_from_window())
                except Exception:
                    pass

        win.connect("realize", on_realize)
        GLib.timeout_add(120, self._apply_layout_from_window)

    # ── adaptive layout ──

    def _window_width(self) -> int:
        if not self.window:
            return 1040
        w = self.window.get_width()
        if w and w > 1:
            return w
        try:
            return int(self.window.get_default_size()[0] or 1040)
        except Exception:
            return 1040

    def _apply_layout_from_window(self):
        width = self._window_width()
        if width < 700:
            mode = "narrow"
        elif width < 920:
            mode = "medium"
        else:
            mode = "wide"
        if mode != self._layout_mode:
            self._layout_mode = mode
            self._apply_layout_mode(mode)
        return False

    def _apply_layout_mode(self, mode: str):
        if not self.nav_pane or not self.nav_revealer or not self.menu_btn:
            return
        if mode == "wide":
            self.nav_pane.set_size_request(300, -1)
            self.nav_pane.remove_css_class("compact")
            self.nav_revealer.set_reveal_child(True)
            self.menu_btn.set_visible(False)
            self._nav_revealed = True
            if self.page_title:
                self.page_title.remove_css_class("compact")
            if self.content_pane:
                self.content_pane.set_margin_start(PAD_MD)
            if self.header_actions:
                for child in self._iter_children(self.header_actions):
                    # keep both pills
                    pass
        elif mode == "medium":
            self.nav_pane.set_size_request(240, -1)
            self.nav_pane.add_css_class("compact")
            self.nav_revealer.set_reveal_child(True)
            self.menu_btn.set_visible(False)
            self._nav_revealed = True
            if self.page_title:
                self.page_title.add_css_class("compact")
            if self.content_pane:
                self.content_pane.set_margin_start(PAD_SM)
        else:  # narrow
            self.nav_pane.set_size_request(280, -1)
            self.nav_pane.remove_css_class("compact")
            self.menu_btn.set_visible(True)
            # collapse nav by default on narrow
            self.nav_revealer.set_reveal_child(False)
            self._nav_revealed = False
            if self.page_title:
                self.page_title.add_css_class("compact")
            if self.content_pane:
                self.content_pane.set_margin_start(PAD_XL)
                self.content_pane.set_margin_end(PAD_MD)

    def toggle_nav(self):
        if not self.nav_revealer:
            return
        self._nav_revealed = not self.nav_revealer.get_reveal_child()
        self.nav_revealer.set_reveal_child(self._nav_revealed)

    @staticmethod
    def _iter_children(box: Gtk.Widget):
        child = box.get_first_child()
        while child:
            yield child
            child = child.get_next_sibling()

    def _on_size_hint(self, *_):
        self._apply_layout_from_window()

    def _on_root_resize(self, *_):
        self._apply_layout_from_window()

    def make_nav(self, key: str, ic: str, title: str, sub: str) -> Gtk.Button:
        btn = Gtk.Button()
        btn.add_css_class("nav-item")
        btn.set_has_frame(False)

        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=14)
        row.set_margin_top(12)
        row.set_margin_bottom(12)
        row.set_margin_start(14)
        row.set_margin_end(14)
        btn.set_child(row)

        circle = Gtk.CenterBox()
        circle.add_css_class("nav-icon-circle")
        circle.set_center_widget(icon(ic, "ms-md", "ms-on-sec"))
        row.append(circle)

        texts = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        texts.set_hexpand(True)
        texts.set_valign(Gtk.Align.CENTER)
        row.append(texts)

        t = Gtk.Label(label=title, xalign=0)
        t.add_css_class("nav-title")
        texts.append(t)
        s = Gtk.Label(label=sub, xalign=0)
        s.add_css_class("nav-sub")
        texts.append(s)

        btn.connect("clicked", lambda *_: self.set_nav(key))
        return btn

    def _make_fade_scroll(self):
        """ScrolledWindow + rubber holder + edge fades (VerticalFadeFlickable + overshoot)."""
        overlay = Gtk.Overlay()
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.set_hexpand(True)
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        # we drive smooth/kinetic ourselves via SmoothRubberScroll
        scroll.set_kinetic_scrolling(False)
        scroll.set_overlay_scrolling(True)
        overlay.set_child(scroll)

        # holder gets margin_top for rubber-band stretch
        holder = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        holder.set_hexpand(True)
        scroll.set_child(holder)

        fade_top = Gtk.Box()
        fade_top.add_css_class("fade-edge-top")
        fade_top.set_valign(Gtk.Align.START)
        fade_top.set_hexpand(True)
        fade_top.set_can_target(False)
        overlay.add_overlay(fade_top)

        fade_bot = Gtk.Box()
        fade_bot.add_css_class("fade-edge-bottom")
        fade_bot.set_valign(Gtk.Align.END)
        fade_bot.set_hexpand(True)
        fade_bot.set_can_target(False)
        overlay.add_overlay(fade_bot)

        # enable smooth + rubber
        self._rubber.append(SmoothRubberScroll(scroll, holder))

        return overlay, scroll, holder, fade_top, fade_bot

    def _bind_scroll_fades(self, scroll: Gtk.ScrolledWindow, fade_top: Gtk.Widget, fade_bot: Gtk.Widget):
        """Toggle edge fades from adjustment (like VerticalFadeFlickable.fadeShouldBeActive)."""

        def update(*_a):
            adj = scroll.get_vadjustment()
            if adj is None:
                return
            upper = adj.get_upper()
            page = adj.get_page_size()
            value = adj.get_value()
            # content shorter than viewport → no fades
            if upper <= page + 1:
                fade_top.remove_css_class("active")
                fade_bot.remove_css_class("active")
                return
            if value > 1.0:
                fade_top.add_css_class("active")
            else:
                fade_top.remove_css_class("active")
            if value + page < upper - 1.0:
                fade_bot.add_css_class("active")
            else:
                fade_bot.remove_css_class("active")

        def on_map(*_):
            adj = scroll.get_vadjustment()
            if adj is not None:
                adj.connect("value-changed", update)
                adj.connect("changed", update)
            GLib.idle_add(update)
            return False

        scroll.connect("map", on_map)
        # also bind now if already has adjustment
        GLib.timeout_add(50, lambda: (update() or False))

    def _scroll_to_top(self, scroll: Gtk.ScrolledWindow | None):
        if not scroll:
            return
        # reset rubber on any attached SmoothRubberScroll
        for r in self._rubber:
            if r.scroll is scroll:
                r.reset()
                break
        adj = scroll.get_vadjustment()
        if adj:
            adj.set_value(0)

    def _nav_index(self, key: str) -> int:
        for i, (k, *_r) in enumerate(NAV):
            if k == key:
                return i
        return 0

    def _run_page_switch(self, direction: int, after):
        """Pages.qml style: fade out → swap content → slide+fade in.

        direction: +1 going down the nav list, -1 going up.
        """
        host = self.list_host
        if not host or self._page_animating:
            after()
            return

        self._page_animating = True
        if self._page_anim_src:
            GLib.source_remove(self._page_anim_src)
            self._page_anim_src = 0

        offset = 28 * (1 if direction >= 0 else -1)

        # phase 1: fade out
        host.set_opacity(0.0)

        def phase2():
            after()
            self._scroll_to_top(self.list_scroll)
            # start below/above
            host.set_margin_top(offset)
            host.set_margin_bottom(-offset)
            host.set_opacity(0.0)

            # phase 3: animate margin + opacity in steps
            steps = 8
            step_i = {"i": 0}

            def tick():
                step_i["i"] += 1
                t = step_i["i"] / steps
                # ease-out cubic
                e = 1 - (1 - t) ** 3
                host.set_opacity(e)
                host.set_margin_top(int(offset * (1 - e)))
                host.set_margin_bottom(int(-offset * (1 - e)))
                if step_i["i"] >= steps:
                    host.set_opacity(1.0)
                    host.set_margin_top(0)
                    host.set_margin_bottom(0)
                    self._page_animating = False
                    self._page_anim_src = 0
                    return False
                return True

            self._page_anim_src = GLib.timeout_add(22, tick)
            return False

        GLib.timeout_add(140, phase2)

    def set_nav(self, key: str, rebuild: bool = True):
        old_idx = self._nav_idx
        new_idx = self._nav_index(key)
        direction = 1 if new_idx >= old_idx else -1
        changed = key != self.nav_filter

        self.nav_filter = key
        self._nav_idx = new_idx

        for k, w in self.nav_btns.items():
            if k == key:
                w.add_css_class("active")
            else:
                w.remove_css_class("active")
        meta = {n[0]: (n[2], n[3]) for n in NAV}
        title, sub = meta.get(key, ("Keybinds", ""))
        if self.page_title:
            self.page_title.set_text(title)
        if self.page_sub:
            self.page_sub.set_text(sub)
        if self.header_actions:
            self.header_actions.set_visible(True)
        if self.stack:
            self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
            self.stack.set_visible_child_name("list")
        self.selected = None
        # auto-collapse nav on narrow after pick
        if self._layout_mode == "narrow" and self.nav_revealer:
            self.nav_revealer.set_reveal_child(False)
            self._nav_revealed = False

        def do_rebuild():
            if rebuild:
                self.apply_filter()
            else:
                self.rebuild_list()

        if rebuild and changed and self.list_host is not None:
            self._run_page_switch(direction, do_rebuild)
        else:
            do_rebuild()

    def on_key(self, _c, keyval, _code, state):
        ctrl = bool(state & Gdk.ModifierType.CONTROL_MASK)
        if keyval == Gdk.KEY_Escape:
            if self.stack and self.stack.get_visible_child_name() == "detail":
                self.show_list()
                return True
            if self._layout_mode == "narrow" and self.nav_revealer and self.nav_revealer.get_reveal_child():
                self.nav_revealer.set_reveal_child(False)
                self._nav_revealed = False
                return True
            self.window.close()
            return True
        if ctrl and keyval in (Gdk.KEY_f, Gdk.KEY_F):
            self.search.grab_focus()
            return True
        if ctrl and keyval in (Gdk.KEY_n, Gdk.KEY_N):
            self.open_editor()
            return True
        if ctrl and keyval in (Gdk.KEY_r, Gdk.KEY_R):
            self.reload(flash=True)
            return True
        if ctrl and keyval in (Gdk.KEY_b, Gdk.KEY_B):
            self.toggle_nav()
            return True
        if keyval in (Gdk.KEY_Delete, Gdk.KEY_KP_Delete):
            if self.selected and not (self.search and self.search.has_focus()):
                self.request_delete(self.selected)
                return True
        return False

    def watch(self):
        from core import CUSTOM_JSON, SCHEME_JSON, VARIABLES_LUA

        for path in (KEYBINDS_LUA, VARIABLES_LUA, CUSTOM_JSON, SCHEME_JSON):
            p = Path(path)
            t = p if p.exists() else p.parent
            if not t.exists():
                continue
            mon = Gio.File.new_for_path(str(t)).monitor(Gio.FileMonitorFlags.NONE, None)
            mon.connect("changed", self.on_file)
            self._monitors.append(mon)

    def on_file(self, *_):
        if self._reload_src:
            GLib.source_remove(self._reload_src)
        self._reload_src = GLib.timeout_add(280, self._debounced)

    def _debounced(self):
        self._reload_src = 0
        self.scheme = load_scheme()
        self.apply_css()
        self.store = load_store()
        self.reload()
        return False

    def reload(self, flash: bool = False):
        self.store = load_store()
        self.binds = load_all_binds(self.store)
        self.apply_filter()
        if flash:
            self.toast(f"Synced · {len(self.binds)} binds")

    def apply_filter(self):
        q = (self.search.get_text() if self.search else "").strip().lower()
        items = list(self.binds)
        if self.nav_filter == "custom":
            items = [b for b in items if b.source == "custom"]
        elif self.nav_filter == "system":
            items = [b for b in items if b.source == "system"]
        elif self.nav_filter == "override":
            items = [b for b in items if b.source == "override"]
        elif self.nav_filter == "disabled":
            items = [b for b in items if not b.enabled]
        if q:
            items = [b for b in items if q in b.search_blob]
        self.filtered = items
        self.rebuild_list()
        if self.stat:
            customs = sum(1 for b in self.binds if b.source == "custom")
            self.stat.set_text(
                f"{len(self.filtered)} shown  ·  {len(self.binds)} total  ·  {customs} custom"
            )

    def rebuild_list(self):
        assert self.list_box
        child = self.list_box.get_first_child()
        while child:
            nxt = child.get_next_sibling()
            self.list_box.remove(child)
            child = nxt

        groups: dict[str, list[Bind]] = {}
        for b in self.filtered:
            groups.setdefault(b.category, []).append(b)

        if not groups:
            empty = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
            empty.set_halign(Gtk.Align.CENTER)
            empty.set_margin_top(64)
            empty.append(icon("search_off", "ms-md"))
            lab = Gtk.Label(label="Nothing here")
            lab.add_css_class("page-sub")
            empty.append(lab)
            self.list_box.append(empty)
            animate_in(empty, 0)
            self._scroll_to_top(self.list_scroll)
            return

        anim_i = 0
        for cat, binds in groups.items():
            sec = Gtk.Label(label=cat.upper(), xalign=0)
            sec.add_css_class("section-label")
            sec.set_margin_top(18)
            sec.set_margin_bottom(6)
            self.list_box.append(sec)
            for i, b in enumerate(binds):
                row = self.make_row(b, i, len(binds))
                self.list_box.append(row)
                # staggered appear (cap delay so big lists don't feel laggy)
                delay = min(anim_i * 18, 280)
                animate_in(row, delay)
                anim_i += 1

        # keep scroll top when filter/search rebuilds without page anim
        if not self._page_animating:
            self._scroll_to_top(self.list_scroll)
        # refresh fade state after content changes
        GLib.timeout_add(80, lambda: False)

    def _row_radius_class(self, index: int, total: int) -> str:
        if total == 1:
            return "only"
        if index == 0:
            return "first"
        if index == total - 1:
            return "last"
        return "mid"

    def make_row(self, b: Bind, index: int, total: int) -> Gtk.Widget:
        """ConnectedRect-style settings row (like ToggleRow without switch)."""
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        row.add_css_class("row")
        row.add_css_class(self._row_radius_class(index, total))
        if self.selected and self.selected.id == b.id:
            row.add_css_class("selected")
        if not b.enabled:
            row.add_css_class("disabled")

        inner = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        inner.set_margin_top(12)
        inner.set_margin_bottom(12)
        inner.set_margin_start(18)
        inner.set_margin_end(14)
        inner.set_hexpand(True)
        row.append(inner)

        chip = Gtk.Label(label=pretty_keys(b.keys))
        chip.add_css_class("key-chip")
        if b.source in ("custom", "override"):
            chip.add_css_class("key-chip-accent")
        chip.set_valign(Gtk.Align.CENTER)
        inner.append(chip)

        texts = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        texts.set_hexpand(True)
        texts.set_valign(Gtk.Align.CENTER)
        inner.append(texts)

        title = Gtk.Label(label=b.title, xalign=0)
        title.add_css_class("row-title")
        title.set_ellipsize(Pango.EllipsizeMode.END)
        texts.append(title)

        sub = Gtk.Label(label=b.detail.split("\n")[0], xalign=0)
        sub.add_css_class("row-sub")
        sub.set_ellipsize(Pango.EllipsizeMode.END)
        texts.append(sub)

        badge = Gtk.Label(label=b.source.upper())
        badge.add_css_class("badge")
        if b.source == "custom":
            badge.add_css_class("badge-custom")
        elif b.source == "override":
            badge.add_css_class("badge-override")
        badge.set_valign(Gtk.Align.CENTER)
        inner.append(badge)

        # show resolved real cmd chip when vars.* expanded
        if b.technical_resolved and b.technical_resolved != (b.technical or ""):
            real_cmd = b.technical_resolved
            if real_cmd.startswith("exec "):
                real_cmd = real_cmd[5:]
            rc = Gtk.Label(label=real_cmd)
            rc.add_css_class("badge")
            rc.add_css_class("badge-custom")
            rc.set_valign(Gtk.Align.CENTER)
            rc.set_tooltip_text(f"Real command (from {b.technical})")
            rc.set_ellipsize(Pango.EllipsizeMode.END)
            rc.set_max_width_chars(18)
            inner.append(rc)

        # chevron like settings drill-in rows
        chev = icon("chevron_right", "ms-sm")
        chev.set_opacity(0.4)
        chev.set_valign(Gtk.Align.CENTER)
        inner.append(chev)

        click = Gtk.GestureClick()
        click.set_button(1)
        click.connect("pressed", lambda *_a, bind=b: self.open_detail(bind))
        row.add_controller(click)
        row.set_cursor_from_name("pointer")
        return row

    # ── detail sub-page ──

    def open_detail(self, b: Bind):
        self.selected = b
        self.render_detail(b)
        self._scroll_to_top(self.detail_scroll)
        if self.header_actions:
            self.header_actions.set_visible(False)
        if self.page_title:
            self.page_title.set_text(b.title.replace("[disabled] ", ""))
        if self.page_sub:
            self.page_sub.set_text(pretty_keys(b.keys))
        if self.stack:
            # valid GTK enum — slide content left to show detail
            self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
            self.stack.set_transition_duration(280)
            self.stack.set_visible_child_name("detail")
        # collapse nav on narrow so detail has room
        if self._layout_mode == "narrow" and self.nav_revealer:
            self.nav_revealer.set_reveal_child(False)
            self._nav_revealed = False

    def show_list(self, *_args):
        """Return from detail → list. Fixed: no invalid SLIDE_RIGHT_LEFT."""
        try:
            self.selected = None
            if self.header_actions:
                self.header_actions.set_visible(True)
            meta = {n[0]: (n[2], n[3]) for n in NAV}
            title, sub = meta.get(self.nav_filter, ("Keybinds", ""))
            if self.page_title:
                self.page_title.set_text(title)
            if self.page_sub:
                self.page_sub.set_text(sub)
            if self.stack:
                # valid GTK enum — slide content right to go back
                self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_RIGHT)
                self.stack.set_transition_duration(280)
                self.stack.set_visible_child_name("list")
            self.rebuild_list()
            self._scroll_to_top(self.list_scroll)
        except Exception as e:
            # never leave user stuck on detail
            if self.stack:
                self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
                self.stack.set_visible_child_name("list")
            self.toast(f"Back error: {e}")

    def render_detail(self, b: Bind):
        assert self.detail_box
        child = self.detail_box.get_first_child()
        while child:
            nxt = child.get_next_sibling()
            self.detail_box.remove(child)
            child = nxt

        # explicit handler — don't rely on broken transition enums
        back = Gtk.Button()
        back.add_css_class("pill-tonal")
        back.set_halign(Gtk.Align.START)
        bb = Gtk.Box(spacing=8)
        bb.set_halign(Gtk.Align.CENTER)
        bb.append(icon("arrow_back", "ms-sm"))
        bb.append(Gtk.Label(label="Back"))
        back.set_child(bb)
        back.connect("clicked", self.show_list)
        self.detail_box.append(back)
        animate_in(back, 0)

        hero = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        hero.add_css_class("hero")
        self.detail_box.append(hero)

        chip = Gtk.Label(label=pretty_keys(b.keys), xalign=0)
        chip.add_css_class("key-chip")
        if b.source in ("custom", "override"):
            chip.add_css_class("key-chip-accent")
        hero.append(chip)

        t = Gtk.Label(label=b.title, xalign=0, wrap=True)
        t.add_css_class("page-title")
        t.set_margin_top(4)
        t.set_wrap(True)
        hero.append(t)

        lab = Gtk.Label(label="WHAT IT DOES", xalign=0)
        lab.add_css_class("section-label")
        lab.set_margin_top(8)
        hero.append(lab)

        body = Gtk.Label(label=b.detail, xalign=0, wrap=True)
        body.add_css_class("row-sub")
        body.set_wrap(True)
        body.set_max_width_chars(48 if self._layout_mode == "narrow" else 58)
        hero.append(body)

        lab2 = Gtk.Label(label="TECHNICAL", xalign=0)
        lab2.add_css_class("section-label")
        lab2.set_margin_top(8)
        hero.append(lab2)

        tech_var = b.technical or b.raw or "—"
        tech_real = b.technical_resolved or tech_var
        # default show real command when we have a vars. expand
        show_resolved = bool(b.technical_resolved and b.technical_resolved != b.technical)

        tech_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        hero.append(tech_row)

        mono = Gtk.Label(
            label=tech_real if show_resolved else tech_var,
            xalign=0,
            wrap=True,
            selectable=True,
        )
        mono.add_css_class("mono")
        mono.set_wrap(True)
        mono.set_hexpand(True)
        tech_row.append(mono)

        # toggle vars.X  ↔  real command (only if they differ)
        if b.technical_resolved and b.technical_resolved != (b.technical or ""):
            state = {"resolved": show_resolved}

            def toggle_tech(*_):
                state["resolved"] = not state["resolved"]
                if state["resolved"]:
                    mono.set_text(tech_real)
                    toggle_btn.set_tooltip_text("Show vars.* form")
                    # update icon/label
                    toggle_btn.set_child(None)
                    tb = Gtk.Box(spacing=6)
                    tb.set_halign(Gtk.Align.CENTER)
                    tb.append(icon("data_object", "ms-sm"))
                    tb.append(Gtk.Label(label="vars"))
                    toggle_btn.set_child(tb)
                    mode_hint.set_text("showing real command")
                else:
                    mono.set_text(tech_var)
                    toggle_btn.set_tooltip_text("Show real command")
                    toggle_btn.set_child(None)
                    tb = Gtk.Box(spacing=6)
                    tb.set_halign(Gtk.Align.CENTER)
                    tb.append(icon("terminal", "ms-sm"))
                    tb.append(Gtk.Label(label="real"))
                    toggle_btn.set_child(tb)
                    mode_hint.set_text("showing vars.* reference")

            toggle_btn = Gtk.Button()
            toggle_btn.add_css_class("pill-tonal")
            toggle_btn.set_valign(Gtk.Align.START)
            tb0 = Gtk.Box(spacing=6)
            tb0.set_halign(Gtk.Align.CENTER)
            # currently showing real → button offers switch to vars
            tb0.append(icon("data_object", "ms-sm"))
            tb0.append(Gtk.Label(label="vars"))
            toggle_btn.set_child(tb0)
            toggle_btn.set_tooltip_text("Show vars.* form")
            toggle_btn.connect("clicked", toggle_tech)
            tech_row.append(toggle_btn)

            mode_hint = Gtk.Label(label="showing real command", xalign=0)
            mode_hint.add_css_class("row-sub")
            hero.append(mode_hint)
        elif "vars." in tech_var:
            # unresolved
            hint = Gtk.Label(label="vars.* value not found in variables.lua", xalign=0)
            hint.add_css_class("row-sub")
            hero.append(hint)

        meta = Gtk.Label(
            label=f"Category · {b.category}    Source · {b.source}"
            + (f"    Kind · {b.kind}" if b.source != "system" else ""),
            xalign=0,
            wrap=True,
        )
        meta.add_css_class("row-sub")
        hero.append(meta)
        animate_in(hero, 40)

        actions: list[tuple[str, str, str, callable]] = [
            ("Copy shortcut", "content_copy", "pill-tonal", lambda: self.copy_text(f"{pretty_keys(b.keys)}  →  {b.title}")),
        ]
        if b.source == "custom":
            actions.append(("Edit", "edit", "pill-filled", lambda: self.open_editor(b)))
            if b.enabled:
                actions.append(("Disable", "block", "pill-tonal", lambda: self.disable_bind(b)))
            else:
                actions.append(("Enable", "check_circle", "pill-tonal", lambda: self.enable_bind(b)))
            actions.append(("Delete forever", "delete", "pill-danger", lambda: self.request_delete(b)))
        elif b.source == "system":
            if b.enabled:
                actions.append(("Disable (temporary)", "block", "pill-tonal", lambda: self.disable_bind(b)))
            else:
                actions.append(("Enable", "check_circle", "pill-filled", lambda: self.enable_bind(b)))
            actions.append(("Override…", "swap_horiz", "pill-tonal", lambda: self.open_editor(b, True)))
            actions.append(("Delete forever", "delete", "pill-danger", lambda: self.request_delete(b)))
        else:
            actions.append(("Edit override", "edit", "pill-filled", lambda: self.open_editor(b, True)))
            actions.append(("Delete forever", "delete", "pill-danger", lambda: self.request_delete(b)))

        act_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        act_box.add_css_class("detail-actions")
        self.detail_box.append(act_box)
        for i, (label, ic, css, cb) in enumerate(actions):
            btn = pill_button(label, ic, css, cb)
            act_box.append(btn)
            animate_in(btn, 80 + i * 35)
        animate_in(act_box, 60)

    # ── store mutations ──

    def _confirm(self, heading: str, body: str, ok: str, on_ok):
        d = Gtk.Window(transient_for=self.window, modal=True, title=heading)
        d.set_default_size(420, 260)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        box.set_margin_top(20)
        box.set_margin_bottom(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        box.add_css_class("confirm")
        d.set_child(box)
        h = Gtk.Label(label=heading, xalign=0)
        h.add_css_class("page-title")
        box.append(h)
        m = Gtk.Label(label=body, xalign=0, wrap=True)
        m.add_css_class("row-sub")
        m.set_wrap(True)
        box.append(m)
        row = Gtk.Box(spacing=8)
        row.set_halign(Gtk.Align.END)
        box.append(row)
        cancel = Gtk.Button(label="Cancel")
        cancel.add_css_class("pill-tonal")
        cancel.connect("clicked", lambda *_: d.close())
        row.append(cancel)
        okb = Gtk.Button(label=ok)
        okb.add_css_class("pill-danger")

        def go(*_):
            d.close()
            on_ok()

        okb.connect("clicked", go)
        row.append(okb)
        d.present()

    def request_delete(self, b: Bind):
        if b.source == "system":
            body = (
                f"{pretty_keys(b.keys)}\n→ {b.title}\n\n"
                "Cuts from keybinds.lua, unbinds, hides forever.\n"
                "Not the same as Disable.\n"
                f"Backup: {KEYBINDS_LUA.with_suffix('.lua.bak')}"
            )
        elif b.source == "override":
            body = f"{pretty_keys(b.keys)}\n→ {b.title}\n\nOverride removed."
        else:
            body = f"{pretty_keys(b.keys)}\n→ {b.title}\n\nRemoved from config."
        self._confirm("Delete forever?", body, "Delete forever", lambda: self._do_delete(b))

    def _do_delete(self, b: Bind):
        if b.source == "custom":
            self.delete_custom(b)
        elif b.source == "override":
            self.remove_override(b)
        else:
            self.delete_system(b)

    def delete_custom(self, b: Bind):
        nk = norm_keys(b.keys).lower()
        self.store["binds"] = [
            x
            for x in self.store.get("binds", [])
            if x.get("id") != b.id and norm_keys(x.get("keys", "")).lower() != nk
        ]
        self.store["disabled"] = [d for d in self.store.get("disabled", []) if norm_keys(d).lower() != nk]
        save_store(self.store)
        self.toast(f"Deleted {pretty_keys(b.keys)}")
        self.show_list()
        self.reload()

    def delete_system(self, b: Bind):
        keys = norm_keys(b.keys.replace("[disabled] ", ""))
        nk = keys.lower()
        cut = remove_bind_from_system_lua(b.raw, keys)
        deleted = self.store.setdefault("deleted", [])
        if keys not in deleted and nk not in {norm_keys(d).lower() for d in deleted}:
            deleted.append(keys)
        self.store["disabled"] = [d for d in self.store.get("disabled", []) if norm_keys(d).lower() != nk]
        ov = self.store.get("overrides") or {}
        for k in list(ov.keys()):
            if norm_keys(k).lower() == nk:
                ov.pop(k, None)
        self.store["overrides"] = ov
        save_store(self.store)
        self.toast(f"Deleted {pretty_keys(keys)}" + (" · lua cut" if cut else ""))
        self.show_list()
        self.reload()

    def disable_bind(self, b: Bind):
        keys = norm_keys(b.keys.replace("[disabled] ", ""))
        nk = keys.lower()
        if b.source == "custom":
            for x in self.store.get("binds", []):
                if x.get("id") == b.id or norm_keys(x.get("keys", "")).lower() == nk:
                    x["enabled"] = False
        disabled = self.store.setdefault("disabled", [])
        if keys not in disabled and nk not in {norm_keys(d).lower() for d in disabled}:
            disabled.append(keys)
        save_store(self.store)
        self.toast(f"Disabled {pretty_keys(keys)}")
        self.reload()
        match = next((x for x in self.binds if norm_keys(x.keys).lower() == nk), None)
        if match and self.stack and self.stack.get_visible_child_name() == "detail":
            self.open_detail(match)

    def enable_bind(self, b: Bind):
        keys = norm_keys(b.keys.replace("[disabled] ", "")).lower()
        self.store["disabled"] = [d for d in self.store.get("disabled", []) if norm_keys(d).lower() != keys]
        if b.source == "custom":
            for x in self.store.get("binds", []):
                if x.get("id") == b.id or norm_keys(x.get("keys", "")).lower() == keys:
                    x["enabled"] = True
        save_store(self.store)
        self.toast("Enabled")
        self.reload()
        match = next((x for x in self.binds if norm_keys(x.keys).lower() == keys), None)
        if match and self.stack and self.stack.get_visible_child_name() == "detail":
            self.open_detail(match)

    def remove_override(self, b: Bind):
        ov = self.store.get("overrides") or {}
        for k, v in list(ov.items()):
            if (
                v.get("id") == b.id
                or norm_keys(k).lower() == norm_keys(b.keys).lower()
                or norm_keys(v.get("keys", "")).lower() == norm_keys(b.keys).lower()
            ):
                ov.pop(k, None)
        self.store["overrides"] = ov
        save_store(self.store)
        self.toast("Override deleted")
        self.show_list()
        self.reload()

    def open_editor(self, bind: Bind | None = None, as_override: bool = False, *_extra):
        if not isinstance(bind, Bind):
            bind = None
        EditorDialog(self, bind, as_override=bool(as_override)).present()

    def upsert_custom(self, data: dict, original: Bind | None, as_override: bool):
        if as_override and original and original.source in ("system", "override"):
            base_keys = original.keys
            if original.source == "override":
                for k, v in (self.store.get("overrides") or {}).items():
                    if v.get("id") == original.id:
                        base_keys = k
                        break
            self.store.setdefault("overrides", {})[norm_keys(base_keys)] = data
            save_store(self.store)
            self.toast(f"Override · {pretty_keys(data['keys'])}")
        else:
            binds = self.store.setdefault("binds", [])
            if original and original.source == "custom":
                for i, x in enumerate(binds):
                    if x.get("id") == original.id:
                        binds[i] = data
                        break
                else:
                    binds.append(data)
            else:
                binds.append(data)
            save_store(self.store)
            self.toast(f"Saved · {pretty_keys(data['keys'])}")
        self.reload()
        if self.stack and self.stack.get_visible_child_name() == "detail":
            self.show_list()

    def copy_text(self, text: str):
        Gdk.Display.get_default().get_clipboard().set(text)
        self.toast("Copied")

    def toast(self, msg: str):
        if not self.toast_lab:
            return
        self.toast_lab.set_text(msg)
        self.toast_lab.set_visible(True)
        if self._toast_src:
            GLib.source_remove(self._toast_src)
        self._toast_src = GLib.timeout_add(2000, self._hide_toast)

    def _hide_toast(self):
        self._toast_src = 0
        if self.toast_lab:
            self.toast_lab.set_visible(False)
        return False


class EditorDialog(Gtk.Window):
    def __init__(self, app: KeybindsApp, bind: Bind | None, as_override: bool = False):
        super().__init__(transient_for=app.window, modal=True, title="Edit bind" if bind else "New bind")
        self.app = app
        self.bind = bind
        self.as_override = as_override
        self.set_default_size(460, 580)

        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        outer.set_margin_top(22)
        outer.set_margin_bottom(22)
        outer.set_margin_start(22)
        outer.set_margin_end(22)
        self.set_child(outer)

        hdr = Gtk.Label(
            label="Override system bind"
            if as_override
            else ("Edit bind" if bind and bind.source == "custom" else "New custom bind"),
            xalign=0,
        )
        hdr.add_css_class("page-title")
        outer.append(hdr)

        self.keys = self._field(outer, "Keys", "SUPER + B")
        cap = pill_button("Capture keys…", "keyboard", "pill-tonal", self.start_capture)
        outer.append(cap)
        self.cap_lab = Gtk.Label(label="", xalign=0)
        self.cap_lab.add_css_class("page-sub")
        outer.append(self.cap_lab)

        kind_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        outer.append(kind_box)
        kl = Gtk.Label(label="ACTION TYPE", xalign=0)
        kl.add_css_class("section-label")
        kind_box.append(kl)
        self.kind_model = Gtk.StringList.new([f"{k} — {label}" for k, label, _ in ACTION_PRESETS])
        self.kind_drop = Gtk.DropDown(model=self.kind_model)
        kind_box.append(self.kind_drop)

        self.payload = self._field(outer, "Action payload", "command / dispatcher / global")
        self.title_e = self._field(outer, "Title", "What it does")
        self.detail_e = self._field(outer, "Description", "Longer explanation")
        self.cat_e = self._field(outer, "Category", "Custom")

        flags = Gtk.Box(spacing=16)
        outer.append(flags)
        self.fl_locked = Gtk.CheckButton(label="locked")
        self.fl_repeat = Gtk.CheckButton(label="repeating")
        self.fl_release = Gtk.CheckButton(label="release")
        for c in (self.fl_locked, self.fl_repeat, self.fl_release):
            flags.append(c)

        outer.append(pill_button("Fill from Hypr preset…", "list", "pill-text", self.pick_preset))

        btns = Gtk.Box(spacing=8)
        btns.set_halign(Gtk.Align.END)
        outer.append(btns)
        cancel = Gtk.Button(label="Cancel")
        cancel.add_css_class("pill-tonal")
        cancel.connect("clicked", lambda *_: self.close())
        btns.append(cancel)
        save = Gtk.Button(label="Save")
        save.add_css_class("pill-filled")
        save.connect("clicked", lambda *_: self.save())
        btns.append(save)

        if bind:
            self.keys.set_text(pretty_keys(bind.keys))
            kind_idx = next((i for i, (k, *_r) in enumerate(ACTION_PRESETS) if k == bind.kind), 0)
            if bind.source == "system":
                if bind.technical.startswith("global "):
                    kind_idx = 2
                    self.payload.set_text(bind.technical[7:])
                elif bind.technical.startswith("exec "):
                    self.payload.set_text(bind.technical[5:])
                else:
                    self.payload.set_text(bind.technical)
            else:
                self.payload.set_text(bind.payload)
            self.kind_drop.set_selected(kind_idx)
            self.title_e.set_text(bind.title.replace("[disabled] ", ""))
            self.detail_e.set_text(bind.detail)
            self.cat_e.set_text(bind.category if bind.category != "General" else "Custom")
            self.fl_locked.set_active("locked" in bind.flags)
            self.fl_repeat.set_active("repeating" in bind.flags)
            self.fl_release.set_active("release" in bind.flags)
        else:
            self.cat_e.set_text("Custom")

        self._capturing = False
        kc = Gtk.EventControllerKey()
        kc.connect("key-pressed", self.on_cap)
        self.add_controller(kc)

    def _field(self, parent, label, ph) -> Gtk.Entry:
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        parent.append(box)
        l = Gtk.Label(label=label.upper(), xalign=0)
        l.add_css_class("section-label")
        box.append(l)
        e = Gtk.Entry(placeholder_text=ph)
        e.add_css_class("form-entry")
        box.append(e)
        return e

    def start_capture(self):
        self._capturing = True
        self.cap_lab.set_text("Press a combination… (Esc cancels)")
        self.grab_focus()

    def on_cap(self, _c, keyval, keycode, state):
        if not self._capturing:
            return False
        if keyval == Gdk.KEY_Escape:
            self._capturing = False
            self.cap_lab.set_text("Cancelled")
            return True
        if keyval in (
            Gdk.KEY_Shift_L, Gdk.KEY_Shift_R, Gdk.KEY_Control_L, Gdk.KEY_Control_R,
            Gdk.KEY_Alt_L, Gdk.KEY_Alt_R, Gdk.KEY_Super_L, Gdk.KEY_Super_R,
            Gdk.KEY_Meta_L, Gdk.KEY_Meta_R, Gdk.KEY_ISO_Level3_Shift,
        ):
            return True
        parts = []
        if state & Gdk.ModifierType.SUPER_MASK:
            parts.append("SUPER")
        if state & Gdk.ModifierType.CONTROL_MASK:
            parts.append("CTRL")
        if state & Gdk.ModifierType.ALT_MASK:
            parts.append("ALT")
        if state & Gdk.ModifierType.SHIFT_MASK:
            parts.append("SHIFT")
        name = Gdk.keyval_name(keyval) or f"code{keycode}"
        name = {"Return": "Return", "space": "Space", "slash": "slash"}.get(name, name)
        if len(name) == 1:
            name = name.upper()
        parts.append(name)
        combo = " + ".join(parts)
        self.keys.set_text(combo)
        self._capturing = False
        self.cap_lab.set_text(f"Captured: {combo}")
        return True

    def pick_preset(self):
        pop = Gtk.Popover()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        box.set_margin_top(8)
        box.set_margin_bottom(8)
        box.set_margin_start(8)
        box.set_margin_end(8)
        pop.set_child(box)
        for disp, label in HYPR_PRESETS:
            b = Gtk.Button(label=f"{label}  ({disp})")
            b.add_css_class("pill-tonal")

            def apply(_w, d=disp, lab=label):
                self.kind_drop.set_selected(1)
                self.payload.set_text(d)
                if not self.title_e.get_text().strip():
                    self.title_e.set_text(lab)
                if not self.detail_e.get_text().strip():
                    self.detail_e.set_text(f"Hyprland dispatcher: {d}")
                pop.popdown()

            b.connect("clicked", apply)
            box.append(b)
        pop.set_parent(self)
        pop.popup()

    def save(self):
        keys = norm_keys(self.keys.get_text())
        if not keys:
            self.app.toast("Keys required")
            return
        kind = ACTION_PRESETS[self.kind_drop.get_selected()][0]
        payload = self.payload.get_text().strip()
        if not payload:
            self.app.toast("Action payload required")
            return
        title = self.title_e.get_text().strip()
        detail = self.detail_e.get_text().strip()
        if not title or not detail:
            t, d, _ = describe_custom(kind, payload)
            title = title or t
            detail = detail or d
        flags = []
        if self.fl_locked.get_active():
            flags.append("locked")
        if self.fl_repeat.get_active():
            flags.append("repeating")
        if self.fl_release.get_active():
            flags.append("release")
        data = {
            "id": (
                self.bind.id
                if self.bind and self.bind.source in ("custom", "override")
                else str(uuid.uuid4())
            ),
            "keys": keys,
            "kind": kind,
            "payload": payload,
            "title": title,
            "detail": detail,
            "category": self.cat_e.get_text().strip() or "Custom",
            "flags": flags,
            "enabled": True,
        }
        self.app.upsert_custom(data, self.bind, self.as_override)
        self.close()


def main():
    store = load_store()
    write_hypr_user_lua(store)
    return KeybindsApp().run(sys.argv)


if __name__ == "__main__":
    raise SystemExit(main())
