import os
import subprocess
import random
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QComboBox, QPushButton, QFileDialog, QColorDialog
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

class PersonalizationTab(QWidget):
    def __init__(self, parent_app):
        super().__init__()
        self.app = parent_app
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        layout.addWidget(QLabel("<h1>Personalização</h1>"))

        layout.addWidget(QLabel("<h2>Tema do Sistema</h2>"))
        layout.addWidget(QLabel("Modo Escuro / Claro:"))
        self.app.theme_combo = QComboBox()
        self.app.theme_combo.addItems(["Dark", "Light"])
        layout.addWidget(self.app.theme_combo)

        layout.addWidget(QLabel("Cor de Destaque (HEX):"))
        color_layout = QHBoxLayout()
        self.app.color_input = QLineEdit()
        self.app.color_input.setPlaceholderText("#89b4fa")
        
        pick_color_btn = QPushButton("Escolher Cor")
        pick_color_btn.clicked.connect(self.select_theme_color)
        color_layout.addWidget(self.app.color_input)
        color_layout.addWidget(pick_color_btn)
        layout.addLayout(color_layout)

        layout.addWidget(QLabel("<h2>Hyprland</h2>"))
        layout.addWidget(QLabel("Arredondamento de Borda (Rounding):"))
        self.app.hypr_rounding_input = QLineEdit()
        self.app.hypr_rounding_input.setPlaceholderText("10")
        layout.addWidget(self.app.hypr_rounding_input)

        layout.addWidget(QLabel("Espessura da Borda (Border Size):"))
        self.app.hypr_border_size_input = QLineEdit()
        self.app.hypr_border_size_input.setPlaceholderText("2")
        layout.addWidget(self.app.hypr_border_size_input)

        layout.addWidget(QLabel("Cor da Borda Ativa:"))
        border_color_layout = QHBoxLayout()
        self.app.hypr_active_border_input = QLineEdit()
        self.app.hypr_active_border_input.setPlaceholderText("0xff89b4fa")

        pick_border_color_btn = QPushButton("Escolher Cor da Borda")
        pick_border_color_btn.clicked.connect(self.select_active_border_color)

        border_color_layout.addWidget(self.app.hypr_active_border_input)
        border_color_layout.addWidget(pick_border_color_btn)
        layout.addLayout(border_color_layout)

        layout.addWidget(QLabel("<h2>Wallpaper</h2>"))
        
        # --- PREVIEW DO WALLPAPER ---
        self.wallpaper_preview_label = QLabel("Nenhum wallpaper selecionado")
        self.wallpaper_preview_label.setFixedSize(280, 150)
        self.wallpaper_preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.wallpaper_preview_label.setStyleSheet("border: 1px solid #444; border-radius: 8px; background-color: #111;")
        layout.addWidget(self.wallpaper_preview_label)

        layout.addWidget(QLabel("Caminho do Wallpaper Atual:"))
        file_layout = QHBoxLayout()
        self.app.wallpaper_path_input = QLineEdit()
        self.app.wallpaper_path_input.textChanged.connect(self.update_wallpaper_preview)
        
        browse_file_btn = QPushButton("Procurar...")
        browse_file_btn.clicked.connect(self.select_wallpaper_file)
        file_layout.addWidget(self.app.wallpaper_path_input)
        file_layout.addWidget(browse_file_btn)
        layout.addLayout(file_layout)

        layout.addWidget(QLabel("Pasta de Wallpapers:"))
        folder_layout = QHBoxLayout()
        self.app.wallpaper_folder_input = QLineEdit()
        browse_folder_btn = QPushButton("Procurar...")
        browse_folder_btn.clicked.connect(self.select_wallpaper_folder)
        folder_layout.addWidget(self.app.wallpaper_folder_input)
        folder_layout.addWidget(browse_folder_btn)
        layout.addLayout(folder_layout)

        layout.addWidget(QLabel("Tipo de Transição (awww):"))
        self.app.awww_translate_options = QComboBox()
        self.app.awww_translate_options.addItems([
            "none", "fade", "wipe", "wave", 
            "grow", "center", "any", "outer", "random"
        ])
        layout.addWidget(self.app.awww_translate_options)

        save_btn = QPushButton("Salvar Configurações")
        save_btn.clicked.connect(self.app.save_settings)
        layout.addWidget(save_btn)

        save_btn = QPushButton("Escholer wallpaper")
        save_btn.clicked.connect(self.StartWallpaperSelectWallpaper)
        layout.addWidget(save_btn)

        random_wp_btn = QPushButton("Wallpaper Aleatório")
        random_wp_btn.clicked.connect(self.get_random_wallpaper)
        layout.addWidget(random_wp_btn)

        layout.addStretch()

    def update_wallpaper_preview(self, path: str):
        if path and os.path.exists(path):
            pixmap = QPixmap(path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    self.wallpaper_preview_label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.wallpaper_preview_label.setPixmap(scaled_pixmap)
                return
        self.wallpaper_preview_label.setText("Imagem não encontrada")

    def StartWallpaperSelectWallpaper(self):
        subprocess.run(["ArtexDesktop", "--Wallpaper", "-r"])

    def select_wallpaper_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Selecionar Wallpaper", str(Path.home()),
            "Imagens (*.png *.jpg *.jpeg *.webp *.bmp)"
        )
        if file_path:
            self.app.wallpaper_path_input.setText(file_path)

    def select_wallpaper_folder(self):
        folder_path = QFileDialog.getExistingDirectory(
            self, "Selecionar Pasta de Wallpapers", str(Path.home())
        )
        if folder_path:
            self.app.wallpaper_folder_input.setText(folder_path)

    def select_theme_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.app.color_input.setText(color.name())
    
    def select_active_border_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            hex_color = color.name().lstrip("#")
            hypr_color = f"0xff{hex_color}"
            self.app.hypr_active_border_input.setText(hypr_color)

    def get_random_wallpaper(self):
        folder_path = self.app.wallpaper_folder_input.text()
        if not os.path.exists(folder_path):
            return

        valid_extensions = ('.png', '.jpg', '.jpeg', '.webp', '.bmp')
        wallpapers = [f for f in os.listdir(folder_path) if f.lower().endswith(valid_extensions)]

        if wallpapers:
            wallpaper_escolhido = random.choice(wallpapers)
            location_wallpaper = os.path.join(folder_path, wallpaper_escolhido)
            self.app.wallpaper_path_input.setText(location_wallpaper)
            self.app.save_settings()