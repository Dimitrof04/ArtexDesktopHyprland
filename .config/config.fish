if status is-interactive
    # Desativa a mensagem de boas-vindas padrão do Fish (opcional)
    set -g fish_greeting

    # Aliases
    alias ls='ls --color=auto'
    alias grep='grep --color=auto'

    # Executa o fastfetch ao abrir
    fastfetch
end

# Prompt personalizado equivalente ao seu PS1: ╭─ \w\n╰─ \u ~$ 
function fish_prompt
    echo -e "╭─ "(prompt_pwd)"\n╰─ "$USER" ~\$ "
end
