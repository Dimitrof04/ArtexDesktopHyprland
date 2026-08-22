#!/usr/bin/env python3

import sys
import subprocess
import os
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QWidget, QListWidget, QStackedWidget,
    QHBoxLayout, QScrollArea
)

from PyQt6.QtCore import QSettings, QTimer

from Modules.DesktopMenu.Style import get_stylesheet
from Modules.DesktopMenu.personalization import PersonalizationTab
from Modules.DesktopMenu.keybinds import KeybindsTab
from Modules.DesktopMenu.system_config import SystemConfigTab
from Modules.DesktopMenu.info import InfoTab
from Modules.DesktopMenu.misc import MiscTab

config_path = str(Path.home() / ".config" / "Desktop.conf")

class SettingsApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Configurações do Desktop")
        self.resize(720, 420)
        self.last_config_mtime = 0
        self.setProperty("class", "hypr_menu")

        self.settings = QSettings(config_path, QSettings.Format.IniFormat)

        # TIMER DE AUTOSAVE
        self.autosave_timer = QTimer()
        self.autosave_timer.setSingleShot(True)
        self.autosave_timer.timeout.connect(self.save_settings)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # Menu Lateral
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(190)
        self.sidebar.addItem("Personalização")
        self.sidebar.addItem("Atalhos & Apps")
        self.sidebar.addItem("Configurações do Sistema")
        self.sidebar.addItem("Misc")
        self.sidebar.addItem("Info")

        # Área de Conteúdo Modularizada
        self.content_area = QStackedWidget()

        # Inicializa as abas
        self.personalization_tab = PersonalizationTab(self)
        self.keybinds_tab = KeybindsTab(self)
        self.system_config_tab = SystemConfigTab(self)
        self.misc_tab = MiscTab(self)
        self.info_tab = InfoTab()

        self.content_area.addWidget(self.make_scrollable(self.personalization_tab))
        self.content_area.addWidget(self.make_scrollable(self.keybinds_tab))
        self.content_area.addWidget(self.make_scrollable(self.system_config_tab))
        self.content_area.addWidget(self.make_scrollable(self.misc_tab))
        self.content_area.addWidget(self.make_scrollable(self.info_tab))

        self.sidebar.currentRowChanged.connect(self.content_area.setCurrentIndex)

        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.content_area)

        self.sidebar.setCurrentRow(0)
        self.load_settings()

        # TIMER DE SINCRONIZAÇÃO EM TEMPO REAL
        self.sync_timer = QTimer()
        self.sync_timer.setInterval(300)
        self.sync_timer.timeout.connect(self.check_external_theme_change)
        self.sync_timer.start()

        self.reload_theme()

    def trigger_autosave(self):
        """Reinicia o timer de autosave quando alguma alteração é detectada."""
        if hasattr(self, 'autosave_checkbox') and self.autosave_checkbox.isChecked():
            self.autosave_timer.start()

    def toggle_autosave(self):
        if not self.autosave_checkbox.isChecked():
            self.autosave_timer.stop()
        self.trigger_autosave()

    def update_autosave_delay(self, value):
        self.autosave_timer.setInterval(max(100, value))
        self.trigger_autosave()

    def check_external_theme_change(self):
        """Verifica se o Desktop.conf mudou externamente e atualiza a UI."""
        if os.path.exists(config_path):
            mtime = os.path.getmtime(config_path)
            if mtime != self.last_config_mtime:
                self.last_config_mtime = mtime
                self.reload_theme()
                self.load_settings()

    def reload_theme(self):
        """Lê o Desktop.conf e re-aplica o tema na UI do próprio menu."""
        settings = QSettings(config_path, QSettings.Format.IniFormat)
        settings.beginGroup("theme")
        theme_mode = str(settings.value("theme", "Dark")).strip().capitalize()
        settings.endGroup()

        if hasattr(self, 'theme_combo'):
            self.theme_combo.blockSignals(True)
            self.theme_combo.setCurrentText(theme_mode)
            self.theme_combo.blockSignals(False)

        self.apply_styles()

    def make_scrollable(self, widget: QWidget) -> QScrollArea:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget)
        return scroll

    def apply_styles(self):
        is_light = self.theme_combo.currentText() == "Light" if hasattr(self, 'theme_combo') else False
        accent_color = self.color_input.text().strip() if hasattr(self, 'color_input') else "#89b4fa"
        if not accent_color:
            accent_color = "#89b4fa"
            
        self.setStyleSheet(get_stylesheet(is_light, accent_color))

    def load_settings(self):
        # Desativa temporariamente os sinais para evitar autossave durante o carregamento
        self.block_all_signals(True)

        # 1. Tema
        self.settings.beginGroup("theme")
        if hasattr(self, 'theme_combo'):
            self.theme_combo.setCurrentText(str(self.settings.value("theme", "Dark")))
        if hasattr(self, 'color_input'):
            self.color_input.setText(str(self.settings.value("colortheme", "#89b4fa")))
        self.settings.endGroup()

        # 2. Hyprland
        self.settings.beginGroup("Hyprland")
        if hasattr(self, 'hypr_rounding_input'):
            self.hypr_rounding_input.setText(str(self.settings.value("rounding", "10")))
        if hasattr(self, 'hypr_border_size_input'):
            self.hypr_border_size_input.setText(str(self.settings.value("border_size", "2")))
        if hasattr(self, 'hypr_active_border_input'):
            self.hypr_active_border_input.setText(str(self.settings.value("active_border", "0xff89b4fa")))
        self.settings.endGroup()

        # 3. Wallpapers
        self.settings.beginGroup("Wallpapers")
        if hasattr(self, 'wallpaper_path_input'):
            wp_path = str(self.settings.value("Wallpaper", ""))
            self.wallpaper_path_input.setText(wp_path)
            if hasattr(self.personalization_tab, 'update_wallpaper_preview'):
                self.personalization_tab.update_wallpaper_preview(wp_path)
                
        if hasattr(self, 'wallpaper_folder_input'):
            self.wallpaper_folder_input.setText(
                str(self.settings.value("WallpapersFolder", str(Path.home() / "Pictures/Wallpapers")))
            )
        if hasattr(self, 'awww_translate_options'):
            self.awww_translate_options.setCurrentText(str(self.settings.value("awww_transition", "random")))
        self.settings.endGroup()

        # 4. Apps & Keybinds
        self.settings.beginGroup("Apps")
        if hasattr(self, 'app_terminal_input'):
            self.app_terminal_input.setText(str(self.settings.value("terminal", "kitty")))
        if hasattr(self, 'app_filemanager_input'):
            self.app_filemanager_input.setText(str(self.settings.value("filemanager", "dolphin")))
        if hasattr(self, 'app_menu_input'):
            self.app_menu_input.setText(str(self.settings.value("menu", "hyprlauncher")))
        if hasattr(self, 'app_Browser_input'):
            self.app_Browser_input.setText(str(self.settings.value("Browser", "firefox")))
        self.settings.endGroup()

        self.settings.beginGroup("Keybinds")
        if hasattr(self, 'key_mod_combo'):
            self.key_mod_combo.setCurrentText(str(self.settings.value("main_mod", "SUPER")))
        if hasattr(self, 'bind_terminal_input'):
            self.bind_terminal_input.setText(str(self.settings.value("bind_terminal", "Q")))
        if hasattr(self, 'bind_close_input'):
            self.bind_close_input.setText(str(self.settings.value("bind_close", "C")))
        if hasattr(self, 'bind_menu_input'):
            self.bind_menu_input.setText(str(self.settings.value("bind_menu", "R")))
        if hasattr(self, 'bind_filemanager_input'):
            self.bind_filemanager_input.setText(str(self.settings.value("bind_filemanager", "E")))
        if hasattr(self, 'bind_Browser_input'):
            self.bind_Browser_input.setText(str(self.settings.value("bind_browser", "W")))
        if hasattr(self, 'bind_ToggleFloting'):
            self.bind_ToggleFloting.setText(str(self.settings.value("bind_ToggleFloting", "Space")))
        self.settings.endGroup()

        # 5. Misc
        self.settings.beginGroup("Misc")
        if hasattr(self, 'autosave_checkbox'):
            is_autosave = str(self.settings.value("AutoSave", "False")).lower() == "true"
            self.autosave_checkbox.setChecked(is_autosave)

        if hasattr(self, 'autosave_delay_spin'):
            delay = int(self.settings.value("AutoSaveDelay", 1000))
            self.autosave_delay_spin.setValue(max(100, delay))
            self.autosave_timer.setInterval(max(100, delay))

        if hasattr(self, 'icon_logo_input'):
            icon_val = str(self.settings.value("iconlogo", "nil"))
            self.icon_logo_input.setText(icon_val)
        self.settings.endGroup()

        self.block_all_signals(False)
        self.apply_styles()

    def block_all_signals(self, block: bool):
        """Bloqueia sinais durante carregamentos para evitar chamadas acidentais de salvamento."""
        if hasattr(self, 'autosave_checkbox'): self.autosave_checkbox.blockSignals(block)
        if hasattr(self, 'autosave_delay_spin'): self.autosave_delay_spin.blockSignals(block)
        if hasattr(self, 'icon_logo_input'): self.icon_logo_input.blockSignals(block)

    def save_settings(self):
        """Salva as configurações no Desktop.conf e aplica as alterações nos apps / Hyprland."""
        selected_theme = self.theme_combo.currentText() if hasattr(self, 'theme_combo') else "Dark"
        accent_color = self.color_input.text().strip() if hasattr(self, 'color_input') else "#89b4fa"
        if not accent_color:
            accent_color = "#89b4fa"

        # Tema
        self.settings.beginGroup("theme")
        self.settings.setValue("theme", selected_theme)
        self.settings.setValue("colortheme", accent_color)
        self.settings.endGroup()

        subprocess.run(["ArtexDesktop", "--theme", selected_theme])

        # Hyprland
        self.settings.beginGroup("Hyprland")
        rounding = self.hypr_rounding_input.text().strip() if hasattr(self, 'hypr_rounding_input') else "10"
        border_size = self.hypr_border_size_input.text().strip() if hasattr(self, 'hypr_border_size_input') else "2"
        active_border = self.hypr_active_border_input.text().strip() if hasattr(self, 'hypr_active_border_input') else "0xff89b4fa"

        if active_border.startswith("#"):
            active_border = "0xff" + active_border.lstrip("#")

        if rounding: self.settings.setValue("rounding", rounding)
        if border_size: self.settings.setValue("border_size", border_size)
        if active_border: self.settings.setValue("active_border", active_border)
        self.settings.endGroup()

        # Wallpapers
        self.settings.beginGroup("Wallpapers")
        if hasattr(self, 'wallpaper_path_input'):
            self.settings.setValue("Wallpaper", self.wallpaper_path_input.text())
        if hasattr(self, 'wallpaper_folder_input'):
            self.settings.setValue("WallpapersFolder", self.wallpaper_folder_input.text())
        if hasattr(self, 'awww_translate_options'):
            self.settings.setValue("awww_transition", self.awww_translate_options.currentText())
        self.settings.endGroup()

        # Apps & Keybinds
        self.settings.beginGroup("Apps")
        if hasattr(self, 'app_terminal_input'):
            self.settings.setValue("terminal", self.app_terminal_input.text().strip() or "foot")
        if hasattr(self, 'app_filemanager_input'):
            self.settings.setValue("filemanager", self.app_filemanager_input.text().strip() or "Thunar")
        if hasattr(self, 'app_menu_input'):
            self.settings.setValue("menu", self.app_menu_input.text().strip() or "ArtexDesktop --StartMenu -r")
        if hasattr(self, 'app_Browser_input'):
            self.settings.setValue("Browser", self.app_Browser_input.text().strip() or "firefox")
        self.settings.endGroup()

        self.settings.beginGroup("Keybinds")
        if hasattr(self, 'key_mod_combo'):
            self.settings.setValue("main_mod", self.key_mod_combo.currentText())
        if hasattr(self, 'bind_terminal_input'):
            self.settings.setValue("bind_terminal", self.bind_terminal_input.text().strip() or "Q")
        if hasattr(self, 'bind_close_input'):
            self.settings.setValue("bind_close", self.bind_close_input.text().strip() or "C")
        if hasattr(self, 'bind_menu_input'):
            self.settings.setValue("bind_menu", self.bind_menu_input.text().strip() or "R")
        if hasattr(self, 'bind_filemanager_input'):
            self.settings.setValue("bind_filemanager", self.bind_filemanager_input.text().strip() or "E")
        if hasattr(self, 'bind_Browser_input'):
            self.settings.setValue("bind_browser", self.bind_Browser_input.text().strip() or "W")
        if hasattr(self, 'bind_ToggleFloting'):
            self.settings.setValue("bind_ToggleFloting", self.bind_ToggleFloting.text().strip() or "Space")
        self.settings.endGroup()

        # 5. Save Misc
        self.settings.beginGroup("Misc")
        if hasattr(self, 'autosave_checkbox'):
            self.settings.setValue("AutoSave", "True" if self.autosave_checkbox.isChecked() else "False")
        if hasattr(self, 'autosave_delay_spin'):
            self.settings.setValue("AutoSaveDelay", max(100, self.autosave_delay_spin.value()))
        if hasattr(self, 'icon_logo_input'):
            val = self.icon_logo_input.text().strip()
            self.settings.setValue("iconlogo", val if val else "nil")
        self.settings.endGroup()

        self.settings.sync()
        self.apply_styles()

        # Aplicar alterações do Hyprland via hyprctl
        try:
            subprocess.run(["hyprctl", "reload"])
            if rounding:
                subprocess.run(["hyprctl", "keyword", "decoration:rounding", rounding], stderr=subprocess.DEVNULL)
            if border_size:
                subprocess.run(["hyprctl", "keyword", "general:border_size", border_size], stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"Erro hyprctl: {e}")

        # Atualizar wallpaper via awww
        if hasattr(self, 'wallpaper_path_input'):
            wp = self.wallpaper_path_input.text().strip()
            if wp and os.path.exists(wp):
                trans = self.awww_translate_options.currentText() if hasattr(self, 'awww_translate_options') else "random"
                cmd = ["awww", "img", "--transition-type", trans, "--transition-duration", "3", "--transition-fps", "60", wp]
                try:
                    subprocess.run(cmd, stderr=subprocess.DEVNULL)
                except Exception as e:
                    print(f"Erro awww: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SettingsApp()
    window.show()
    sys.exit(app.exec())