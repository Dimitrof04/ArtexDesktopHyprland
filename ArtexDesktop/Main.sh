#!/usr/bin/env bash

# --- 1. GARANTE O DIRETÓRIO CORRETO ---
SCRIPT_DIR="$(cd "$(dirname "$(realpath "${BASH_SOURCE[0]}")")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

# Caminhos dos Scripts
StartMenuPath="$HOME/.local/share/ArtexDesktop/StartMenu.py"
DektopConfigMenuPath="$HOME/.local/share/ArtexDesktop/DektopConfigMenu.py"
ShellBarPath="$HOME/.local/share/ArtexDesktop/ShellBar.py"
CONFIG_PATH="$HOME/.config/Desktop.conf"
WallpaperSelectPath="$HOME/.local/share/ArtexDesktop/wallpaper_select.py"

PROG_NAME="ArtexDesktop"
VERSION="v0.3"

# Variáveis de Estado
TARGET=""
ACTION=""
THEME=""
THEME_REQUEST=false
GLOBAL_RESET=false
FORM_EXPR=""

show_help() {
    cat << EOF
usage: $PROG_NAME [-h] [-v] [--StartMenu] [--ShellBar] [--Desktop] [--WallpaperSelect] [-i] [-k] [-r] [-s] [--theme THEME] [--themerequest] [--gr | --globalreset] [--form "EXPRESSAO"]

options:
  -h, --help            Show this help message and exit
  -v, --version         Show program's version number and exit
  ==============
  --StartMenu           Target: Menu Launcher
  --ShellBar            Target: ShellBar / Taskbar
  --Desktop             Target: Desktop Config
  --WallpaperSelect     Target: Wallpaper Select
  -------------
  --Wallpaper           Altera o Wallpaper / Plano de fundo atual usando o awww
  --theme THEME         Altera o tema do sistema (opções: Light, Dark)
  --themerequest        Retorna o tema que está aplicado no momento
  --gr, --globalreset   Força a remoção de travas (.lock) e mata processos travados
  --form EXPRESSAO      Calcula e retorna o resultado de uma expressão matemática
  ==============
  -i, --init            Iniciar o serviço selecionado
  -k, --kill            Matar o serviço selecionado
  -r, --restart         Reiniciar o serviço selecionado
  -s, --status          Verificar status do serviço

ArtexDesktop ~ thanks for use :3
EOF
}

# Parsing de Argumentos
while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help)
            show_help
            exit 0
            ;;
        -v|--version)
            echo "$PROG_NAME $VERSION"
            exit 0
            ;;
        --StartMenu)
            TARGET="StartMenu"
            shift
            ;;
        --ShellBar)
            TARGET="ShellBar"
            shift
            ;;
        --Desktop)
            TARGET="Desktop"
            shift
            ;;
        --Wallpaper)
            TARGET="Wallpaper"
            shift
            ;;
        -i|--init)
            ACTION="init"
            shift
            ;;
        -k|--kill)
            ACTION="kill"
            shift
            ;;
        -r|--restart)
            ACTION="restart"
            shift
            ;;
        -s|--status)
            ACTION="status"
            shift
            ;;
        --theme)
            THEME="$2"
            shift 2
            ;;
        --themerequest)
            THEME_REQUEST=true
            shift
            ;;
        --gr|--globalreset)
            GLOBAL_RESET=true
            shift
            ;;
        --form)
            FORM_EXPR="$2"
            shift 2
            ;;
        *)
            echo "Opção desconhecida: $1"
            show_help
            exit 1
            ;;
    esac
done

global_reset() {
    echo "🧹 Executando Global Reset no ArtexDesktop..."
    
    pkill -f "DektopConfigMenu.py" 2>/dev/null
    pkill -f "ShellBar.py" 2>/dev/null
    pkill -f "StartMenu.py" 2>/dev/null
    pkill -f "Wallpaper.py" 2>/dev/null
    
    rm -f /tmp/ArtexDesktop_*.lock 2>/dev/null
    rm -f /tmp/desktop_theme.signal 2>/dev/null

    echo "✅ Todas as travas foram limpas e os serviços reiniciados/encerrados com sucesso!"
}

get_current_theme() {
    if [ -f "$CONFIG_PATH" ]; then
        local current_theme
        current_theme=$(grep -i "^theme=" "$CONFIG_PATH" | head -n 1 | cut -d'=' -f2 | tr -d '[:space:]')
        
        if [ -n "$current_theme" ]; then
            echo "$current_theme"
        else
            echo "Light"
        fi
    else
        echo "Light"
    fi
}

get_service_info() {
    local target="$1"
    case "$target" in
        "Desktop")
            SERVICE_PATH="$DektopConfigMenuPath"
            SERVICE_LOCK="DesktopConfig"
            SERVICE_NAME="DektopConfigMenu.py"
            ;;
        "ShellBar")
            SERVICE_PATH="$ShellBarPath"
            SERVICE_LOCK="ShellBar"
            SERVICE_NAME="ShellBar.py"
            ;;
        "StartMenu")
            SERVICE_PATH="$StartMenuPath"
            SERVICE_LOCK="StartMenu"
            SERVICE_NAME="StartMenu.py"
            ;;
        "Wallpaper")
            SERVICE_PATH="$WallpaperSelectPath"
            SERVICE_LOCK="WallpaperSelect"
            SERVICE_NAME="wallpaper_select.py"
            ;;
        *)
            SERVICE_PATH=""
            SERVICE_LOCK=""
            SERVICE_NAME=""
            ;;
    esac
}

check_menu_lock() {
    local lock_name="$1"
    local lock_file="/tmp/ArtexDesktop_${lock_name}.lock"

    exec 200>"$lock_file"
    if flock -n 200; then
        return 0
    else
        return 1
    fi
}

get_service_pid() {
    local script_name="$1"
    local current_pid=$$
    
    local pids
    pids=$(pgrep -f "$script_name")
    
    if [ -n "$pids" ]; then
        for pid in $pids; do
            if [ "$pid" -ne "$current_pid" ]; then
                echo "$pid"
                return 0
            fi
        done
    fi
    return 1
}

get_active_workspace() {
    if command -v hyprctl &> /dev/null; then
        local ws_id
        ws_id=$(hyprctl activeworkspace -j 2>/dev/null | jq -r '.id' 2>/dev/null)
        if [ -n "$ws_id" ] && [ "$ws_id" != "null" ]; then
            echo "Workspace${ws_id}"
            return
        fi
    fi
    echo "Workspace Unknown"
}

kill_service() {
    local pid
    pid=$(get_service_pid "$SERVICE_NAME")
    if [ -n "$pid" ]; then
        if kill -TERM "$pid" 2>/dev/null; then
            echo "Serviço ${SERVICE_NAME} encerrado {PID: ${pid}}."
            return 0
        else
            echo "Processo não localizado."
        fi
    else
        echo "⚠️ ${SERVICE_NAME} não está rodando."
    fi
    return 1
}

start_service() {
    if ! check_menu_lock "$SERVICE_LOCK"; then
        echo "⚠️ ${SERVICE_NAME} já está em execução!"
        return 1
    fi

    python3 "$SERVICE_PATH" &> /dev/null &
    echo "🚀 ${SERVICE_NAME} iniciado com sucesso."
}

status_service() {
    local pid
    pid=$(get_service_pid "$SERVICE_NAME")
    if [ -n "$pid" ]; then
        local ws
        ws=$(get_active_workspace)
        echo "Running : \"${ws}\""
    else
        echo "not Running"
    fi
}

handle_action() {
    local target="$1"
    get_service_info "$target"

    case "$ACTION" in
        "kill")
            kill_service
            ;;
        "restart")
            echo "🔄 Reiniciando ${target}..."
            kill_service
            start_service
            ;;
        "status")
            status_service
            ;;
        "init"|"")
            start_service
            ;;
    esac
}

main() {
    if [ "$GLOBAL_RESET" = true ]; then
        global_reset
    elif [ -n "$FORM_EXPR" ]; then
        python3 -c "import sys; print(eval(sys.argv[1]))" "$FORM_EXPR"
    elif [ "$THEME_REQUEST" = true ]; then
        get_current_theme
    elif [ -n "$THEME" ]; then
        local tema_formatado
        tema_formatado="$(echo "${THEME:0:1}" | tr '[:lower:]' '[:upper:]')$(echo "${THEME:1}" | tr '[:upper:]' '[:lower:]')"
        
        if [[ "$tema_formatado" == "Dark" || "$tema_formatado" == "Light" ]]; then
            python3 -c "import sys; sys.path.append('$HOME/.local/share/ArtexDesktop'); from Modules.theme_sync import set_system_theme; set_system_theme('$tema_formatado')" 2>/dev/null
            echo "🎨 Tema alterado para: $tema_formatado"
        else
            echo "⚠️ Tema '$THEME' inválido! Use apenas 'Dark' ou 'Light'."
        fi
    elif [ -n "$TARGET" ]; then
        handle_action "$TARGET"
    elif [ -n "$ACTION" ]; then
        handle_action "ShellBar"
    else
        echo "Nothing executed. Try using -h or --help"
    fi
}

main "$@"