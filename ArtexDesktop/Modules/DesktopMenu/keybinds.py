# modules/keybinds.py

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton
)

class KeybindsTab(QWidget):
    def __init__(self, parent_app):
        super().__init__()
        self.app = parent_app
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        layout.addWidget(QLabel("<h1>Atalhos & Aplicativos</h1>"))

        layout.addWidget(QLabel("<h2>Aplicativos Padrão</h2>"))

        layout.addWidget(QLabel("Emulador de Terminal:"))
        self.app.app_terminal_input = QLineEdit()
        self.app.app_terminal_input.setPlaceholderText("foot")
        layout.addWidget(self.app.app_terminal_input)

        layout.addWidget(QLabel("Navegardor"))
        self.app.app_Browser_input = QLineEdit()
        self.app.app_Browser_input.setPlaceholderText("firefox")
        layout.addWidget(self.app.app_Browser_input)

        layout.addWidget(QLabel("Gerenciador de Arquivos:"))
        self.app.app_filemanager_input = QLineEdit()
        self.app.app_filemanager_input.setPlaceholderText("Thunar")
        layout.addWidget(self.app.app_filemanager_input)

        layout.addWidget(QLabel("Menu de Aplicativos / Launcher:"))
        self.app.app_menu_input = QLineEdit()
        self.app.app_menu_input.setPlaceholderText("ArtexDesktop --StartMenu")
        layout.addWidget(self.app.app_menu_input)

        layout.addWidget(QLabel("<h2>Combinações de Teclas</h2>"))

        layout.addWidget(QLabel("Tecla Modificadora Principal:"))
        self.app.key_mod_combo = QComboBox()
        self.app.key_mod_combo.addItems(["SUPER", "ALT", "CTRL"])
        layout.addWidget(self.app.key_mod_combo)

        layout.addWidget(QLabel("Atalho para Abrir Terminal:"))
        self.app.bind_terminal_input = QLineEdit()
        self.app.bind_terminal_input.setPlaceholderText("Q")
        layout.addWidget(self.app.bind_terminal_input)

        layout.addWidget(QLabel("Atalho para Abrir o Navegador"))
        self.app.bind_Browser_input = QLineEdit()
        self.app.bind_Browser_input.setPlaceholderText("W")
        layout.addWidget(self.app.bind_Browser_input)

        layout.addWidget(QLabel("Atalho para Fechar Janela:"))
        self.app.bind_close_input = QLineEdit()
        self.app.bind_close_input.setPlaceholderText("C")
        layout.addWidget(self.app.bind_close_input)

        layout.addWidget(QLabel("Atalho para Fixar / Soltar Janela:"))
        self.app.bind_ToggleFloting = QLineEdit()
        self.app.bind_ToggleFloting.setPlaceholderText("Space")
        layout.addWidget(self.app.bind_ToggleFloting)

        layout.addWidget(QLabel("Atalho para Abrir Menu:"))
        self.app.bind_menu_input = QLineEdit()
        self.app.bind_menu_input.setPlaceholderText("R")
        layout.addWidget(self.app.bind_menu_input)

        layout.addWidget(QLabel("Atalho para Gerenciador de Arquivos:"))
        self.app.bind_filemanager_input = QLineEdit()
        self.app.bind_filemanager_input.setPlaceholderText("E")
        layout.addWidget(self.app.bind_filemanager_input)

        save_btn = QPushButton("Salvar Atalhos")
        save_btn.setObjectName("PrimaryButton")
        save_btn.clicked.connect(self.app.save_settings)
        layout.addWidget(save_btn)

        layout.addStretch()