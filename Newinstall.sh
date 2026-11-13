sudo pacman -Syu --needed --noconfirm hyprland hyprlock awww 
sudo pacman -Syu --needed --noconfirm nodejs npm cargo-tauri
sudo pacman -Syu --needed --noconfirm base-devel curl wget file openssl appmenu-gtk-module libappindicator-gtk3 librsvg xdotool webkit2gtk-4.1 rustup
rustup default stable
fish_add_path /usr/bin