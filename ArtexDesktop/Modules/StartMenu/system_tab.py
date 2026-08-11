import subprocess
import sys
from pathlib import Path
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QApplication
from PyQt6.QtGui import QFont
from PyQt6.QtCore import QSettings

CONFIG_MENU_PATH = str(Path.home() / ".config" / "DesktopDimitrof04Apps" / "DektopConfigMenu.py")

class SystemTab(QWidget):
    def __init__(self, config_path, refresh_theme_callback):
        super().__init__()
        self.config_path = config_path
        self.refresh_theme_callback = refresh_theme_callback
        
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(15, 15, 15, 15)

        self.buttons = []
        self.build_ui()

    def build_ui(self):
        actions = [
            ("⚡ Desligar", "hyprshutdown -t 'Shutdown...' --post-cmd 'shutdown -P 0'", "#f38ba8"),
            ("🔄 Reiniciar", "hyprshutdown -t 'Reboot / Restart...' --post-cmd 'reboot'", "#fab387"),
            ("🌙 Sleep (Suspender)", "hyprshutdown -t 'Slepping. . . ...' --post-cmd 'systemctl suspend'", "#89dceb"),
            ("🚪 Logout (Hyprland)", "hyprshutdown", "#f9e2af"),
            ("⚙️ Configurações do Desktop", f"python3 {CONFIG_MENU_PATH}", "#89b4fa"),
        ]

        for label, cmd, color in actions:
            btn = QPushButton(label)
            btn.setFixedHeight(40)
            btn.setFont(QFont("Sans-Serif", 10, QFont.Weight.Bold))
            btn.clicked.connect(lambda _, c=cmd: self.run_cmd(c))
            self.layout.addWidget(btn)
            self.buttons.append((btn, color))

        # Botão de alternar tema
        self.theme_btn = QPushButton("🌓 Alternar Tema (Dark/Light)")
        self.theme_btn.setFixedHeight(40)
        self.theme_btn.setFont(QFont("Sans-Serif", 10, QFont.Weight.Bold))
        self.theme_btn.clicked.connect(self.toggle_theme)
        self.layout.addWidget(self.theme_btn)

        self.layout.addStretch()

    def update_styles(self, btn_bg, text_color):
        """Atualiza a cor de fundo dos botões conforme o tema Claro/Escuro."""
        for btn, color in self.buttons:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {btn_bg}; color: {color};
                    border: 1px solid {color}; border-radius: 8px; text-align: left; padding-left: 15px;
                }}
                QPushButton:hover {{
                    background-color: {color}; color: #11111b;
                }}
            """)
        
        self.theme_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {btn_bg}; color: {text_color};
                border: 1px solid #45475a; border-radius: 8px; text-align: left; padding-left: 15px;
            }}
            QPushButton:hover {{ background-color: #45475a; color: #ffffff; }}
        """)

    def run_cmd(self, cmd):
        subprocess.Popen(cmd, shell=True)
        QApplication.quit()

    def toggle_theme(self):
        settings = QSettings(self.config_path, QSettings.Format.IniFormat)
        settings.beginGroup("theme")
        current_theme = str(settings.value("theme", "Dark")).strip().capitalize()
        accent_color = str(settings.value("colortheme", "#0cb6ff")).strip()
        settings.endGroup()

        new_theme = "Light" if current_theme == "Dark" else "Dark"
        subprocess.run(["ArtexDesktop", "--theme", new_theme])
        self.refresh_theme_callback()