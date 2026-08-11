local Autoboot = {
    "nm-applet", -- Substituído 'NetwokManager' pelo comando gráfico comum ou o binário correto
    "awww-daemon",
    "ArtexDesktop --ShellBar -i"
}

hl.on("hyprland.start", function()
    for _, Comand in ipairs(Autoboot) do
        os.execute(Comand .. " &") -- Executa o comando em segundo plano
    end
end)
