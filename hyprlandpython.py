class HyprlandConfig:
    def __init__(self, config_path: Path = LUA_CONFIG_PATH):
        self.config_path = config_path

    def _update_lua_variable(self, var_name: str, new_value: str | int) -> None:
        """Substitui o valor atribuído a uma variável local no arquivo Lua."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {self.config_path}")

        content = self.config_path.read_text(encoding="utf-8")
        
        # Procura por padrões como: local conf_rounding = ... 
        # e substitui pelo novo valor garantindo sintaxe válida em Lua
        pattern = rf"(local\s+{var_name}\s*=).*$"
        replacement = f"local {var_name} = {new_value}"
        
        updated_content, count = re.subn(pattern, replacement, content, flags=re.MULTILINE)

        if count > 0:
            self.config_path.write_text(updated_content, encoding="utf-8")
        else:
            print(f"Aviso: Variável '{var_name}' não encontrada no arquivo Lua.")

    def set_border_radius(self, radius: int) -> None:
        """Altera o arredondamento das bordas (rounding)."""
        self._update_lua_variable("conf_rounding", radius)

    def set_border_size(self, size: int) -> None:
        """Altera a largura da borda (border_size)."""
        self._update_lua_variable("conf_border_size", size)

    def set_border_color(self, hex_color: str) -> None:
        """
        Altera a cor da borda ativa. 
        Exemplo de hex_color: '0xff89b4fa' ou '"0xffffffff"'
        """
        if not hex_color.startswith('"'):
            hex_color = f'"{hex_color}"'
        self._update_lua_variable("conf_active_col", hex_color)


class Wallpaper:
    """Gerenciamento de papel de parede usando awww."""
    
    @staticmethod
    def init_awww() -> None:
        """Inicializa o daemon do awww caso não esteja rodando."""
        try:
            subprocess.run(["awww-daemon"], check=False)
        except FileNotFoundError:
            print("Erro: 'awww-daemon' não está instalado no sistema.")

    @staticmethod
    def set_wallpaper(image_path: str | Path) -> None:
        """Define um novo papel de parede."""
        path_str = str(image_path)
        try:
            subprocess.run(["awww", "img", path_str], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Erro ao aplicar wallpaper com awww: {e}")
        except FileNotFoundError:
            print("Erro: O executável 'awww' não foi encontrado.")