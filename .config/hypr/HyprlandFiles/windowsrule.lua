local suppressMaximizeRule = hl.window_rule({
    -- Ignore maximize requests from all apps. You'll probably like this.
    name  = "suppress-maximize-events",
    match = { class = ".*" },

    suppress_event = "maximize",
})

hl.window_rule({
    -- Fix some dragging issues with XWayland
    name  = "fix-xwayland-drags",
    match = {
        class      = "^$",
        title      = "^$",
        xwayland   = true,
        float      = true,
        fullscreen = false,
        pin        = false,
    },

    no_focus = true, 
})

-- Hyprland-run windowrule
hl.window_rule({
    name  = "move-hyprland-run",
    match = { class = "hyprland-run" },

    move  = "20 monitor_h-120",
    float = true,
})

hl.window_rule({
    name = "DektopConfigMenu",
    match = { class = "idk" },

    move  = "20 monitor_h-120",
    float = true,
})

-- Regras para a janela do Menu PyQt6
hl.window_rule({
    name = "hypr-menu",
    match = { class = "^(hypr_menu)$" },

    float = true,
    center = true,
    pin = true,
    stay_focused = true,
    dim_around = true,
})

-- Regras para o Seletor de Wallpaper
hl.window_rule({
    name = "wallpaper-selector",
    match = { class = "^(wallpaper-selector)$" },

    float = true,
    --center = true,
    pin = true,
    stay_focused = true,
    dim_around = true,
    no_shadow = true,
    fullscreen = 1,
    border_size = 0,
    move = "{0, 0}"
})

-- Blur e Opacidade para o Foot
hl.window_rule({
    name = "foot-blur",
    match = { class = "^(foot)$" },
    opacity = "0.85 0.85",
})