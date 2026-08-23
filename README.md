# 🌌 Artex Desktop Hyprland

A sleek, minimalist, and highly optimized Hyprland configuration.

---

## 🛠️ Components & Features

This Hyprland environment is built using the following core software:

* **Window Manager:** [Hyprland](https://hyprland.org/) *(Dynamic tiling Wayland compositor)*
* **Status Bar:** [Waybar](https://github.com/Alexays/Waybar) *(Highly customizable Wayland bar)*
* **App Launcher:** [HyprLaucher](https://wiki.hypr.land/Hypr-Ecosystem/hyprlauncher/)
* **Terminal Emulator:** [Kitty](https://sw.kovidgoyal.net/kitty/) *(Fast, feature-rich, GPU-based terminal)*
* **Wallpaper Manager:** `awww`
* **Screen Locker:** [Hyprlock](https://wiki.hyprland.org/Hypr-ecosystem/hyprlock/) *(Fast, secure screen locker)*

---

## 🚀 Installation

Run the interactive installer script to set up everything automatically:

```bash
# Arch Linux
sudo pacman -Syu --needed git
git clone https://github.com/Dimitrof04/ArtexDesktopHyprland.git
cd ArtexDesktopHyprland
chmod +x install.sh
./install.sh
# debian/ubuntu
sudo apt update && sudo apt install git
git clone https://github.com/Dimitrof04/ArtexDesktopHyprland.git
cd ArtexDesktopHyprland
chmod +x install.sh
./install.sh
```

Keybinds (credits casestial for the list)

| Keybind                                       | Action                                                      |
| ------------------------------                | ----------------------------------------------------------- |
| `Super` + `1-10 or s`                         | Switch to workspace (S = special worskpace)                 |
| `Super` + `Shift` + `1-10 or s`               | Move window to workspace (S = special worskpace)            |
| `Super` + `Q`                                 | Open terminal                                               |
| `Super` + `W`                                 | Open browser                                                |
| `Super` + `E`                                 | Open File manager                                           |
| `Super` + `C`                                 | Close Window                                                |
| `Super` + `R`                                 | Open menu (ArtexMenu = default)                             |
| `Super` + `M`                                 | Open Senttigs                                               |
| `Super` + `H`                                 | Open WallpaperSelector                                      |
| `Super` + `Space`                             | Toggle special workspace or close current special workspace |
| `Super` + `Shift` + `Delete`                  | Logout or restart hyprland                                  |
| `Super` + `Shift` + `R`                       | Restart the ShellBar                                        |


> [!Tip]
> You can use ArtexDesktop in terminal

```bash
ArtexDesktop --help # or -h
```
