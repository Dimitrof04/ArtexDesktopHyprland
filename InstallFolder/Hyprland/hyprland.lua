-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
-- Dimitrof04 ~ Config, thanks for use :3
-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
hl.monitor({
    output   = "",
    mode     = "preferred",
    position = "auto",
    scale    = "auto",
})

local Keybinds = require("HyprlandFiles/Keybindings")
local animations = require("HyprlandFiles/animationcurve") 
local AutoStart = require("HyprlandFiles/Autostart")
local config = require("HyprlandFiles/config")
local WindowRules = require("HyprlandFiles/windowsrule")

hl.env("XCURSOR_SIZE", "24")
hl.env("HYPRCURSOR_SIZE", "24")

hl.gesture({
    fingers = 3,
    direction = "horizontal",
    action = "workspace"
})

-- Example per-device config
-- See https://wiki.hypr.land/Configuring/Advanced-and-Cool/Devices/ for more
hl.device({
    name        = "epic-mouse-v1",
    sensitivity = -0.5,
})