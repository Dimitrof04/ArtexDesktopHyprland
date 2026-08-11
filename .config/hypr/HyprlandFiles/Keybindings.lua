local function read_ini_value(filepath, section, key, default)
    local file = io.open(filepath, "r")
    if not file then return default end
    
    local current_section = ""
    for line in file:lines() do
        local trimmed = line:match("^%s*(.-)%s*$")
        local sec = trimmed:match("^%[(.-)%]$")
        if sec then
            current_section = sec
        else
            local k, v = trimmed:match("^([^=]+)=(.*)$")
            if k and v and current_section == section and k:match("^%s*(.-)%s*$") == key then
                file:close()
                return v:match("^%s*(.-)%s*$")
            end
        end
    end
    file:close()
    return default
end

local conf_path = os.getenv("HOME") .. "/.config/Desktop.conf"

-- Carrega atalhos e programas dinamicamente
local mainMod     = read_ini_value(conf_path, "Keybinds", "main_mod", "SUPER")
local terminal    = read_ini_value(conf_path, "Apps", "terminal", "kitty")
local fileManager = read_ini_value(conf_path, "Apps", "filemanager", "Thunar")
local menu        = read_ini_value(conf_path, "Apps", "menu", "ArtexDesktop --StartMenu -r")
local Browser     = read_ini_value(conf_path, "Keybinds", "Browser", "firefox")

local key_term    = read_ini_value(conf_path, "Keybinds", "bind_terminal", "Q")
local key_close   = read_ini_value(conf_path, "Keybinds", "bind_close", "C")
local key_menu    = read_ini_value(conf_path, "Keybinds", "bind_menu", "R")
local key_file    = read_ini_value(conf_path, "Keybinds", "bind_filemanager", "E")
local key_Browser = read_ini_value(conf_path, "Keybinds", "bind_browser", "W")
local key_float = read_ini_value(conf_path, "Keybinds", "bind_ToggleFloting", "Space")

-- Binds
hl.bind(mainMod .. " + " .. key_term, hl.dsp.exec_cmd(terminal))
hl.bind(mainMod .. " + " .. key_close, hl.dsp.window.close())
hl.bind(mainMod .. " + " .. key_menu, hl.dsp.exec_cmd(menu))
hl.bind(mainMod .. " + " .. key_file, hl.dsp.exec_cmd(fileManager))
hl.bind(mainMod .. " + " .. key_Browser, hl.dsp.exec_cmd(Browser))
hl.bind(mainMod .. " + " .. key_float, hl.dsp.window.float({ action = "toggle" }))
hl.bind(mainMod .. " + M", hl.dsp.exec_cmd("ArtexDesktop --Desktop -r"))
hl.bind(mainMod .. " + H", hl.dsp.exec_cmd("ArtexDesktop --Wallpaper -r"))

hl.bind(mainMod .. " + P", hl.dsp.window.pseudo())
hl.bind(mainMod .. " + J", hl.dsp.layout("togglesplit"))    

-- [GNOME] Mover o foco entre janelas (Super + Setas)
hl.bind(mainMod .. " + left",  hl.dsp.focus({ direction = "left" }))
hl.bind(mainMod .. " + right", hl.dsp.focus({ direction = "right" }))
hl.bind(mainMod .. " + up",    hl.dsp.focus({ direction = "up" }))
hl.bind(mainMod .. " + down",  hl.dsp.focus({ direction = "down" }))

-- [GNOME] Mudar de Workspace (Super + Page_Up/Page_Down)
hl.bind(mainMod .. " + Page_Up",   hl.dsp.focus({ workspace = "e-1" }))
hl.bind(mainMod .. " + Page_Down", hl.dsp.focus({ workspace = "e+1" }))

-- [GNOME] Mover janela para outra Workspace (Super + Shift + Page_Up/Page_Down)
hl.bind(mainMod .. " + SHIFT + Page_Up",   hl.dsp.window.move({ workspace = "e-1" }))
hl.bind(mainMod .. " + SHIFT + Page_Down", hl.dsp.window.move({ workspace = "e+1" }))

hl.bind(mainMod .. " + SHIFT + R", hl.dsp.exec_cmd("ArtexDesktop --ShellBar -r")) -- restart waybar

-- Mantido suporte a mudar via números [1-10]
for i = 1, 10 do
    local key = i % 10
    hl.bind(mainMod .. " + " .. key,             hl.dsp.focus({ workspace = i}))
    hl.bind(mainMod .. " + SHIFT + " .. key,     hl.dsp.window.move({ workspace = i }))
end

-- Sair/Desligar
hl.bind(mainMod .. " + SHIFT + Delete", hl.dsp.exec_cmd("command -v hyprshutdown >/dev/null 2>&1 && hyprshutdown || hyprctl dispatch 'hl.dsp.exit()'"))

-- Scratchpad (Janela mágica/oculta)
hl.bind(mainMod .. " + S",         hl.dsp.workspace.toggle_special("magic"))
hl.bind(mainMod .. " + SHIFT + S", hl.dsp.window.move({ workspace = "special:magic" }))

-- Scroll do mouse para mudar de workspace (Super + Scroll)
hl.bind(mainMod .. " + mouse_down", hl.dsp.focus({ workspace = "e+1" }))
hl.bind(mainMod .. " + mouse_up",   hl.dsp.focus({ workspace = "e-1" }))

-- Mover/Redimensionar arrastando
hl.bind(mainMod .. "+ mouse:272", hl.dsp.window.drag(),   { mouse = true })
hl.bind(mainMod .. "+ mouse:273", hl.dsp.window.resize(), { mouse = true })

-- Teclas de mídia do Laptop
hl.bind("XF86AudioRaiseVolume", hl.dsp.exec_cmd("wpctl set-volume -l 1 @DEFAULT_AUDIO_SINK@ 5%+"), { locked = true, repeating = true })
hl.bind("XF86AudioLowerVolume", hl.dsp.exec_cmd("wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%-"),      { locked = true, repeating = true })
hl.bind("XF86AudioMute",        hl.dsp.exec_cmd("wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle"),     { locked = true, repeating = true })
hl.bind("XF86AudioMicMute",     hl.dsp.exec_cmd("wpctl set-mute @DEFAULT_AUDIO_SOURCE@ toggle"),   { locked = true, repeating = true })
hl.bind("XF86MonBrightnessUp",  hl.dsp.exec_cmd("brightnessctl -e4 -n2 set 5%+"),                  { locked = true, repeating = true })
hl.bind("XF86MonBrightnessDown",hl.dsp.exec_cmd("brightnessctl -e4 -n2 set 5%-"),                  { locked = true, repeating = true })

-- Controle de mídia (Playerctl)
hl.bind("XF86AudioNext",  hl.dsp.exec_cmd("playerctl next"),       { locked = true })
hl.bind("XF86AudioPause", hl.dsp.exec_cmd("playerctl play-pause"), { locked = true })
hl.bind("XF86AudioPlay",  hl.dsp.exec_cmd("playerctl play-pause"), { locked = true })
hl.bind("XF86AudioPrev",  hl.dsp.exec_cmd("playerctl previous"),   { locked = true })

return true