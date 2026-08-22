import os
import time
import subprocess
from pathlib import Path
from PyQt6.QtCore import QSettings

CONFIG_PATH = str(Path.home() / ".config" / "Desktop.conf")
SIGNAL_FILE = "/tmp/desktop_theme.signal"

# Path definitions for terminal/file manager configs
KITTY_CONF = Path.home() / ".config" / "kitty" / "kitty.conf"
FOOT_CONF = Path.home() / ".config" / "foot" / "foot.ini"
DOLPHIN_CONF = Path.home() / ".config" / "dolphinrc"
XFCE_CHANNEL = "xsettings"

def update_kitty(is_dark: bool):
    """Updates Kitty terminal theme dynamically."""
    if not KITTY_CONF.exists():
        return
    
    # Define themes (adjust names according to your installed kitty themes)
    theme_name = "Catppuccin-Mocha" if is_dark else "Catppuccin-Latte"
    
    # Send remote command to running kitty instances if remote control is enabled
    subprocess.Popen(["kitty", "@", "set-colors", "-a", f"~/.config/kitty/themes/{theme_name}.conf"], 
                     stderr=subprocess.DEVNULL)


def update_foot(is_dark: bool):
    """Updates Foot terminal theme by swapping included config or parameters."""
    if not FOOT_CONF.exists():
        return
    
    # Example using foot-client / OSC 10 & 11 commands or modifying the include file
    theme_file = "dark-theme.ini" if is_dark else "light-theme.ini"
    
    # You can link the active theme file dynamically
    foot_theme_link = Path.home() / ".config" / "foot" / "current_theme.ini"
    target_theme = Path.home() / ".config" / "foot" / theme_file
    
    if target_theme.exists():
        if foot_theme_link.is_symlink() or foot_theme_link.exists():
            foot_theme_link.unlink()
        foot_theme_link.symlink_to(target_theme)


def update_thunar(is_dark: bool):
    """Updates Thunar (XFCE File Manager) theme via xfconf-query."""
    theme_name = "Adwaita" if is_dark else "Adwaita-dark"
    subprocess.Popen([
        "xfconf-query", "-c", XFCE_CHANNEL, 
        "-p", "/Net/ThemeName", 
        "-s", theme_name
    ], stderr=subprocess.DEVNULL)


def update_dolphin(is_dark: bool):
    """Updates Dolphin (KDE File Manager) color scheme using kwriteconfig6/5."""
    color_scheme = "BreezeDark" if is_dark else "BreezeLight"
    
    # Try kwriteconfig6 (Plasma 6) or fallback to kwriteconfig5
    kwrite_bin = "kwriteconfig6" if subprocess.run(["which", "kwriteconfig6"], capture_output=True).returncode == 0 else "kwriteconfig5"
    
    subprocess.Popen([
        kwrite_bin, "--file", "kdeglobals", 
        "--group", "General", 
        "--key", "ColorScheme", color_scheme
    ], stderr=subprocess.DEVNULL)


def set_system_theme(theme_mode: str, colortheme: str = None):
    """Atualiza o Desktop.conf, notifica o GTK/Firefox/Discord e envia sinal pros menus."""
    is_dark = theme_mode.capitalize() == "Dark"
    
    # 1. Atualiza o arquivo Desktop.conf
    settings = QSettings(CONFIG_PATH, QSettings.Format.IniFormat)
    settings.beginGroup("theme")
    settings.setValue("theme", "Dark" if is_dark else "Light")
    if colortheme:
        settings.setValue("colortheme", colortheme)
    settings.endGroup()
    settings.sync()

    # 2. Muda o tema Global do Sistema (Firefox, Discord, GTK Apps)
    scheme = "prefer-dark" if is_dark else "prefer-light"
    subprocess.Popen(["gsettings", "set", "org.gnome.desktop.interface", "color-scheme", scheme], stderr=subprocess.DEVNULL)
    subprocess.Popen(["gsettings", "set", "org.gnome.desktop.interface", "gtk-theme", "Adwaita-dark" if is_dark else "Adwaita"], stderr=subprocess.DEVNULL)

    try:
        # 3. Atualiza Terminais (Kitty / Foot)
        update_kitty(is_dark)
        update_foot(is_dark)

        # 4. Atualiza Gerenciadores de Arquivos (Thunar / Dolphin)
        update_thunar(is_dark)
        update_dolphin(is_dark)
    except:
        print("Error in update themes")

    # 5. Notifica o outro app atualizando o timestamp do arquivo de sinal
    with open(SIGNAL_FILE, "w") as f:
        f.write(str(time.time()))