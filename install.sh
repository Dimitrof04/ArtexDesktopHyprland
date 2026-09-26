#!/bin/bash

# Cores para mensagens
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Definindo variáveis de repositório e diretórios locais
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_CONFIG="$HOME/.config"
TARGET_HOME="$HOME"
TARGET_LOCAL_SHARE="$HOME/.local/share"
PICTURES_DIR="$HOME/Pictures"

echo -e "${BLUE}=======================================${NC}"
echo -e "${BLUE}     Welcome to ArtexDesktop!          ${NC}"
echo -e "${BLUE}=======================================${NC}"

# Check/Install yay
if ! command -v yay &> /dev/null; then
    echo -e "${YELLOW}[!] 'yay' is not installed. Installing yay...${NC}"
    sudo pacman -S --needed base-devel git -y
    git clone https://aur.archlinux.org/yay.git /tmp/yay
    cd /tmp/yay && makepkg -si --noconfirm
    cd "$SCRIPT_DIR"
fi

# Seleção do modo de instalação
echo -e "\nChoose installation mode:"
echo "1) [AutoInstallation] (Automatic copy and full setup)"
echo "2) [ManualInstallation] (Asks permission [Y/n] before overwriting files)"
read -p "Select mode (1 or 2): " MODE_CHOICE

case $MODE_CHOICE in
    2) IS_AUTO=false ;;
    *) IS_AUTO=true ;;
esac

# Função utilitária para copiar arquivos com permissão se em modo Manual
copy_file() {
    local src="$1"
    local dest="$2"
    
    if $IS_AUTO; then
        cp "$src" "$dest"
        echo -e "${BLUE}[+] Copied ${src} -> ${dest}${NC}"
    else
        read -p "Overwrite/Copy ${src} to ${dest}? [Y/n]: " confirm
        confirm=${confirm:-Y}
        if [[ $confirm =~ ^[Yy]$ ]]; then

            cp -rf "$src" "$dest"
            echo -e "${BLUE}[+] Copied!${NC}"
        else
            echo -e "${RED}[-] Skipped ${src}${NC}"
        fi
    fi
}

# 1. Copiar pacotes essenciais
echo -e "\n${BLUE}--- Installing the necessary packages ---${NC}"
yay -Syu --noconfirm
yay -S --needed --noconfirm hyprland foot fish awww

read -p "\n$Do you want recommended apps? (It is not required, but it is recommended.) [Y/n] ---${NC}" extrapps

extrapps=true

case $extrapps in
    2) $extrapps=true ;;
    *) $extrapps=false
esac

#if [$extrapps] then
#    yay -S --needed --noconfirm hyprlock pavucontrol ttf-nerd-fonts-symbols thunar dolphin
#fi

# Atualizar repositórios e instalar pacotes do sistema
yay -S --needed --noconfirm gtk3 python networkmanager bluez bluez-utils wireplumber pipewire-audio lsb-release ttf-font-awesome ttf-nerd-fonts-symbols-common noto-fonts-emoji gtk-layer-shell

# Habilitar serviços essenciais
sudo systemctl enable --now NetworkManager
sudo systemctl enable --now bluetooth

# 2. Perguntar sobre Tools adicionais
read -p "Install extra tools (unimatrix, cava, fastfetch, asciiquarium, pipes.sh, lavat, peaclock)? [Y/n]: " INSTALL_TOOLS
INSTALL_TOOLS=${INSTALL_TOOLS:-Y}

if [[ $INSTALL_TOOLS =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}[+] Installing tools...${NC}"
    yay -S --needed fastfetch asciiquarium pipes.sh lavat peaclock unimatrix cava Audacious lyrics-in-terminal cmatrix aafire --noconfirm
fi

# 3. Copiar configurações de .config
echo -e "\n${BLUE}--- Deploying Config Files ---${NC}"
if [ -d "$SCRIPT_DIR/.config" ]; then
    for item in "$SCRIPT_DIR/.config"/*; do
        if [ -e "$item" ]; then
            filename=$(basename "$item")
            copy_file "$item" "$TARGET_CONFIG/$filename"
        fi
    done
fi

# Copiar DefaultConfigs.conf para ~/.config/Desktop.conf (se não existir)
if [ -f "$SCRIPT_DIR/DefaultConfigs.conf" ]; then
    if [ ! -f "$TARGET_CONFIG/Desktop.conf" ]; then
        cp "$SCRIPT_DIR/DefaultConfigs.conf" "$TARGET_CONFIG/Desktop.conf"
        echo -e "${BLUE}[+] Copied DefaultConfigs.conf to ~/.config/Desktop.conf${NC}"
    else
        echo -e "${YELLOW}[!] ~/.config/Desktop.conf already exists. Skipping.${NC}"
    fi
fi

# 4. Copiar pasta ArtexDesktop para ~/.local/share/ (Subscreve direto sem pedir)
echo -e "\n${BLUE}--- Deploying ArtexDesktop App Data ---${NC}"
if [ -d "$SCRIPT_DIR/ArtexDesktop" ]; then
    mkdir -p "$TARGET_LOCAL_SHARE"
    cp -rf "$SCRIPT_DIR/ArtexDesktop" "$TARGET_LOCAL_SHARE/"
    echo -e "${BLUE}[+] Overwritten ArtexDesktop in ~/.local/share/${NC}"
fi

# 5. Copiar Shells (.bashrc, .zshrc)
echo -e "\n${BLUE}--- Deploying Shell Configurations ---${NC}"
if [ -d "$SCRIPT_DIR/Shells" ]; then
    for shell_file in "$SCRIPT_DIR/Shells"/.*; do
        if [ -f "$shell_file" ]; then
            filename=$(basename "$shell_file")
            # Ignora '.' e '..'
            if [ "$filename" != "." ] && [ "$filename" != ".." ]; then
                copy_file "$shell_file" "$TARGET_HOME/$filename"
            fi
        fi
    done
fi

# 6. Gerenciamento de Wallpapers
echo -e "\n${BLUE}--- Setting up Wallpapers ---${NC}"
mkdir -p "$PICTURES_DIR"

if [ -d "$PICTURES_DIR/Wallpapers" ]; then
    echo -e "${YELLOW}The 'Wallpapers' folder already exists in ~/Pictures.${NC}"
    echo "1) [Add Wallpapers] (Add repository wallpapers without deleting existing ones)"
    echo "2) [Dont add wallpapers]"
    echo "3) [CreateIsolatedFolder] (Create a new separate wallpapers folder)"
    read -p "Choose option (1-3): " WP_EXISTING_CHOICE

    case $WP_EXISTING_CHOICE in
        1)
            cp -rn "$SCRIPT_DIR/Wallpapers"/* "$PICTURES_DIR/Wallpapers/"
            echo -e "${BLUE}[+] Added wallpapers into ~/Pictures/Wallpapers/${NC}"
            ;;
        3)
            NEW_DIR="$PICTURES_DIR/Wallpapers_ArtexDesktop"
            mkdir -p "$NEW_DIR"
            cp -r "$SCRIPT_DIR/Wallpapers"/* "$NEW_DIR/"
            echo -e "${BLUE}[+] Copied wallpapers into ${NEW_DIR}${NC}"
            ;;
        *)
            echo -e "${RED}[-] Skipping wallpapers.${NC}"
            ;;
    esac
else
    echo -e "${YELLOW}The 'Wallpapers' folder does NOT exist in ~/Pictures.${NC}"
    echo "1) [Create Wallpapers Folder] (Copy wallpapers to ~/Pictures/Wallpapers)"
    echo "2) [Do nothing]"
    read -p "Choose option (1-2): " WP_NEW_CHOICE

    case $WP_NEW_CHOICE in
        1)
            mkdir -p "$PICTURES_DIR/Wallpapers"
            cp -r "$SCRIPT_DIR/Wallpapers"/* "$PICTURES_DIR/Wallpapers/"
            echo -e "${BLUE}[+] Created folder and added wallpapers!${NC}"
            ;;
        *)
            echo -e "${RED}[-] Doing nothing for wallpapers.${NC}"
            ;;
    esac
fi

cd ~

git https://github.com/Dimitrof04/ArtexDesktopApps.git
.~/ArtexDesktopApps/install.sh
source .venv/bin/activate
pip install wxPython requests psutil pywinctl bs4 plyer pip pillow requests psutil pyqt6
deactivate

echo -e "\n${BLUE}=======================================${NC}"
echo -e "${BLUE}    Installation Complete! Enjoy! :3   ${NC}"
echo -e "${BLUE}=======================================${NC}"