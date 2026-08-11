#!/usr/bin/env python3
import configparser
import os
import sys
import datetime
import subprocess
import gi

gi.require_version("Gtk", "3.0")

try:
    gi.require_version("GtkLayerShell", "0.1")
    from gi.repository import GtkLayerShell
    HAS_LAYER_SHELL = True
except (ValueError, ImportError, ModuleNotFoundError):
    HAS_LAYER_SHELL = False

from gi.repository import Gdk, GLib, Gtk, GdkPixbuf

def get_arch_logo_widget(size=14):
    """Procura explicitamente pelo arquivo de logo do Arch no sistema."""
    arch_paths = [
        "/usr/share/pixmaps/archlinux.png",
        "/usr/share/pixmaps/archlinux-logo-text.svg",
        "/usr/share/icons/hicolor/scalable/apps/archlinux-logo.svg"
    ]
    for path in arch_paths:
        if os.path.exists(path):
            try:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(path, size, size, True)
                return Gtk.Image.new_from_pixbuf(pixbuf)
            except Exception:
                pass
    
    theme = Gtk.IconTheme.get_default()
    for candidate in ["archlinux-logo", "archlinux", "distributor-logo-arch"]:
        if theme.has_icon(candidate):
            return Gtk.Image.new_from_icon_name(candidate, Gtk.IconSize.MENU)

    return Gtk.Image.new_from_icon_name("system-run-symbolic", Gtk.IconSize.MENU)


def get_current_workspace():
    """Detecta a workspace ativa usando wmctrl ou hyprctl."""
    try:
        res = subprocess.run(["wmctrl", "-d"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        if res.returncode == 0:
            for line in res.stdout.splitlines():
                if "*" in line:
                    return int(line.split()[0]) + 1
    except Exception:
        pass

    try:
        res = subprocess.run(["hyprctl", "activeworkspace"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        if res.returncode == 0:
            for line in res.stdout.splitlines():
                if "workspace ID" in line:
                    return int(line.split()[2])
    except Exception:
        pass

    return 1


# ==============================================================================
# BASE CUSTOM BUTTON
# ==============================================================================
class BaseButton(Gtk.Button):
    """Classe base para botões estilizados."""
    def __init__(self, label="", icon_widget=None, icon_name=None, onclick=None, onhover=None, onright=None, css_class="btn-flat"):
        super().__init__()
        self.onclick_callback = onclick
        self.onhover_callback = onhover
        self.onright_callback = onright

        # Impede que o GTK desenhe bordas de foco (quadrado branco/cinza) no botão ativo/inicial
        self.set_can_focus(False)

        if icon_widget:
            self.set_image(icon_widget)
            self.set_always_show_image(True)
            if label:
                self.set_label(label)
        elif icon_name:
            icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.MENU)
            self.set_image(icon)
            self.set_always_show_image(True)
            if label:
                self.set_label(label)
        elif label:
            self.set_label(label)

        self.get_style_context().add_class(css_class)
        self.add_events(Gdk.EventMask.POINTER_MOTION_MASK | Gdk.EventMask.BUTTON_PRESS_MASK)

        self.connect("button-press-event", self._on_button_press)
        self.connect("enter-notify-event", self._on_enter_notify)

    def _on_button_press(self, widget, event):
        if event.button == 1 and self.onclick_callback:
            self.onclick_callback(widget)
            return True
        elif event.button == 3 and self.onright_callback:
            self.onright_callback(widget)
            return True
        return False

    def _on_enter_notify(self, widget, event):
        if self.onhover_callback:
            self.onhover_callback(widget)
        return False


# ==============================================================================
# SUBCLASSES DE BOTÕES
# ==============================================================================
class ArchButton(BaseButton):
    def __init__(self, onclick=None):
        icon_w = get_arch_logo_widget(size=14)
        super().__init__(
            icon_widget=icon_w,
            onclick=onclick or (lambda w: subprocess.Popen(["rofi", "-show", "drun"])),
            css_class="btn-arch"
        )


class WorkspaceButton(BaseButton):
    def __init__(self, ws_num, is_active=False, onclick=None):
        css = "ws-dot active" if is_active else "ws-dot"
        super().__init__(css_class=css, onclick=onclick)
        self.ws_num = ws_num

        # Garante alinhamento centralizado para não esticar na altura do painel
        self.set_valign(Gtk.Align.CENTER)
        self.set_halign(Gtk.Align.CENTER)

    def set_active(self, active: bool):
        ctx = self.get_style_context()
        if active:
            if not ctx.has_class("active"):
                ctx.add_class("active")
        else:
            if ctx.has_class("active"):
                ctx.remove_class("active")


class ClockButton(BaseButton):
    def __init__(self, onclick=None):
        super().__init__(
            label="00:00 - 01/01/2026",
            onclick=onclick or (lambda w: print("Abrir Calendário")),
            css_class="btn-clock"
        )

    def update_time(self):
        now = datetime.datetime.now().strftime("%H:%M  •  %d/%m")
        self.set_label(now)


class SysTrayButton(BaseButton):
    def __init__(self, app_name, icon_name):
        super().__init__(
            icon_name=icon_name,
            onclick=lambda w: print(f"App ativo: {app_name}"),
            css_class="btn-tray"
        )


class VolumeButton(BaseButton):
    def __init__(self):
        super().__init__(
            icon_name="audio-volume-high-symbolic",
            onclick=lambda w: subprocess.Popen(["pavucontrol"]),
            css_class="btn-sound"
        )


class BluetoothButton(BaseButton):
    def __init__(self):
        super().__init__(
            icon_name="bluetooth-active-symbolic",
            onclick=lambda w: subprocess.Popen(["blueman-manager"]),
            css_class="btn-bluetooth"
        )


class WifiButton(BaseButton):
    def __init__(self):
        super().__init__(
            icon_name="network-wireless-symbolic",
            onclick=lambda w: subprocess.Popen(["nm-connection-editor"]),
            css_class="btn-wifi"
        )


# ==============================================================================
# PAINEL PRINCIPAL (SHELLBAR)
# ==============================================================================
class ShellBar(Gtk.Window):
    def __init__(self, config_path="Desktop.conf"):
        super().__init__(title="ShellBar")

        self.config_path = os.path.expanduser(config_path)
        self.current_theme = None
        self.current_color = None
        self.active_workspace_num = -1  # Força a atualização inicial

        if HAS_LAYER_SHELL:
            GtkLayerShell.init_for_window(self)
            GtkLayerShell.set_layer(self, GtkLayerShell.Layer.TOP)
            GtkLayerShell.auto_exclusive_zone_enable(self)

            GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.TOP, True)
            GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.LEFT, True)
            GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.RIGHT, True)

        self.set_default_size(-1, 20)
        self.connect("destroy", Gtk.main_quit)

        self.css_provider = Gtk.CssProvider()
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            self.css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        self.main_panel = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.main_panel.get_style_context().add_class("bar-panel")
        self.add(self.main_panel)

        self.left_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        self.center_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.right_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)

        self.main_panel.pack_start(self.left_box, False, False, 0)
        self.main_panel.set_center_widget(self.center_box)
        self.main_panel.pack_end(self.right_box, False, False, 0)

        self._build_left_section()
        self._build_center_section()
        self._build_right_section()

        self.update_theme_from_config()
        GLib.timeout_add(1000, self.update_theme_from_config)
        
        # Checa a workspace inicial e monitora continuamente
        self._check_active_workspace()
        GLib.timeout_add(250, self._check_active_workspace)

        self.show_all()

    def _build_left_section(self):
        self.arch_btn = ArchButton()
        self.left_box.pack_start(self.arch_btn, False, False, 0)

        ws_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
        ws_container.get_style_context().add_class("workspace-container")
        ws_container.set_valign(Gtk.Align.CENTER)

        self.ws_buttons = []
        for i in range(1, 5):
            dot_btn = WorkspaceButton(
                ws_num=i,
                is_active=False,
                onclick=lambda w, num=i: self._switch_workspace(num)
            )
            self.ws_buttons.append(dot_btn)
            ws_container.pack_start(dot_btn, False, False, 0)

        self.left_box.pack_start(ws_container, False, False, 2)

    def _build_center_section(self):
        self.clock_btn = ClockButton()
        self.center_box.pack_start(self.clock_btn, False, False, 0)
        
        GLib.timeout_add(1000, self._update_clock)
        self.clock_btn.update_time()

    def _build_right_section(self):
        self.tray_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
        self.right_box.pack_start(self.tray_box, False, False, 2)

        self.sound_btn = VolumeButton()
        self.right_box.pack_start(self.sound_btn, False, False, 0)

        self.bt_btn = BluetoothButton()
        self.right_box.pack_start(self.bt_btn, False, False, 0)

        self.net_btn = WifiButton()
        self.right_box.pack_start(self.net_btn, False, False, 0)

        GLib.timeout_add(2000, self._update_tray_apps)
        self._update_tray_apps()

    def _update_tray_apps(self):
        for child in self.tray_box.get_children():
            self.tray_box.remove(child)

        check_apps = [
            {"proc": "discord", "icon": "discord"},
            {"proc": "steam", "icon": "steam"},
            {"proc": "flameshot", "icon": "flameshot"}
        ]

        for app in check_apps:
            try:
                res = subprocess.run(["pgrep", "-x", app["proc"]], stdout=subprocess.PIPE)
                if res.returncode == 0:
                    icon_btn = SysTrayButton(app_name=app["proc"], icon_name=app["icon"])
                    self.tray_box.pack_start(icon_btn, False, False, 0)
            except Exception:
                pass

        self.tray_box.show_all()
        return True

    def _switch_workspace(self, ws_num):
        try:
            subprocess.Popen(["wmctrl", "-s", str(ws_num - 1)])
        except Exception:
            try:
                subprocess.Popen(["hyprctl", "dispatch", "workspace", str(ws_num)])
            except Exception:
                pass

        self._update_ws_ui(ws_num)

    def _check_active_workspace(self):
        current = get_current_workspace()
        if current != self.active_workspace_num:
            self._update_ws_ui(current)
        return True

    def _update_ws_ui(self, active_num):
        self.active_workspace_num = active_num
        for btn in self.ws_buttons:
            btn.set_active(btn.ws_num == active_num)

    def _update_clock(self):
        self.clock_btn.update_time()
        return True

    def update_theme_from_config(self):
        config = configparser.ConfigParser()
        if not os.path.exists(self.config_path):
            return True

        config.read(self.config_path)
        theme_mode = config.get("theme", "theme", fallback="Light").strip()
        theme_color = config.get("theme", "colortheme", fallback="#89b4fa").strip()

        if theme_mode == self.current_theme and theme_color == self.current_color:
            return True

        self.current_theme = theme_mode
        self.current_color = theme_color
        is_light = theme_mode.lower() == "light"
        
        bg_color = "#ffffff" if is_light else "#1e1e2e"
        fg_color = "#111111" if is_light else "#cdd6f4"

        css_data = f"""
        * {{
            font-size: 11px;
            font-weight: 500;
            outline: none;
            box-shadow: none;
        }}

        .bar-panel {{
            background-color: {bg_color};
            padding: 1px 4px;
            min-height: 2px;
        }}

        .btn-arch, .btn-sound, .btn-bluetooth, .btn-wifi, .btn-tray, .btn-clock {{
            background-color: transparent;
            background-image: none;
            color: {fg_color};
            border: none;
            outline: none;
            box-shadow: none;
            padding: 1px 4px;
            margin: 0;
        }}

        .btn-arch:hover {{
            opacity: 0.7;
        }}

        .btn-clock:hover {{
            color: {theme_color};
            font-weight: bold;
        }}

        .btn-sound:hover, .btn-bluetooth:hover, .btn-wifi:hover, .btn-tray:hover {{
            opacity: 0.5;
        }}

        .workspace-container {{
            padding: 0 2px;
        }}

        /* Remove o foco visual padrão do GTK e fixa dimensões */
        .ws-dot {{
            background-color: {fg_color};
            opacity: 0.3;
            border-radius: 50%;
            border: none;
            outline: none;
            margin: 0 3px;
            padding: 0;
            min-width: 8px;
            min-height: 8px;
            box-shadow: none;
            background-image: none;
        }}

        .ws-dot:hover {{
            opacity: 0.7;
        }}

        /* Pílula ativa arredondada */
        .ws-dot.active {{
            background-color: {theme_color};
            opacity: 1.0;
            min-width: 18px;
            min-height: 8px;
            border-radius: 10px;
        }}
        """

        self.css_provider.load_from_data(css_data.encode('utf-8'))
        return True

if __name__ == "__main__":
    app = ShellBar("~/.config/Desktop.conf")
    Gtk.main()