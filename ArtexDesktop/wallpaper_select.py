import sys
import os
import re
import subprocess
from pathlib import Path
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtGui import QPainter, QPainterPath, QPixmap, QColor, QTransform, QWheelEvent, QKeyEvent, QGuiApplication

# FIX 1: Extensão alterada de Desktop.config para Desktop.conf
CONFIG_PATH = Path.home() / ".config" / "Desktop.conf"

class WallpaperCard:
    def __init__(self, path):
        self.path = path
        self.pixmap = QPixmap(path)

class WallpaperSelectorApp(QWidget):
    def __init__(self):
        super().__init__()
        
        # Define o nome da classe para o Window Manager (Hyprland) reconhecer como "wallpaper-selector"
        self.setObjectName("wallpaper-selector")
        self.setProperty("class", "wallpaper-selector")
        
        # 1. LER CONFIGURAÇÃO
        self.wallpapers_folder = str(Path.home() / "Pictures/Wallpapers")
        self.awww_transition = "wave"
        self.load_config()

        # 2. CARREGAR WALLPAPERS
        self.wallpapers = []
        self.load_wallpapers()

        self.current_index = 0

        # 3. CONFIGURAR JANELA TRANSPARENTE E SOBREPOSTA
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        # 4. MONITOR M1
        self.setup_target_monitor("M1")

    def setup_target_monitor(self, target_monitor_name="M1"):
        screens = QGuiApplication.screens()
        target_screen = None

        for screen in screens:
            if target_monitor_name.lower() in screen.name().lower():
                target_screen = screen
                break

        if not target_screen and screens:
            target_screen = screens[0]

        if target_screen:
            geo = target_screen.geometry()
            self.setGeometry(geo)

    def load_config(self):
        if CONFIG_PATH.exists():
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    content = f.read()

                # Busca a pasta de wallpapers
                folder_match = re.search(r"WallpapersFolder\s*=\s*(.+)", content)
                if folder_match:
                    self.wallpapers_folder = folder_match.group(1).strip()

                # Busca o tipo de transição do awww
                trans_match = re.search(r"awww_transition\s*=\s*(.+)", content)
                if trans_match:
                    self.awww_transition = trans_match.group(1).strip()
            except Exception as e:
                print(f"Erro ao ler config: {e}")
        else:
            print(f"⚠️ Configuração não encontrada em: {CONFIG_PATH}")

    def save_wallpaper_to_config(self, selected_path):
        """Atualiza a chave Wallpaper= preservando 100% da estrutura, comentários e formatação do arquivo."""
        if not CONFIG_PATH.exists():
            print(f"⚠️ Não foi possível salvar: {CONFIG_PATH} não existe.")
            return

        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                lines = f.readlines()

            new_lines = []
            in_wallpapers_section = False
            wallpaper_updated = False

            for line in lines:
                stripped = line.strip()

                # Identifica se estamos na seção [Wallpapers] ou [General]
                if stripped.startswith("[") and stripped.endswith("]"):
                    in_wallpapers_section = (stripped.lower() == "[wallpapers]" or stripped.lower() == "[general]")

                # Se estivermos em uma seção válida e achar a linha Wallpaper=...
                if in_wallpapers_section and stripped.startswith("Wallpaper="):
                    # Mantém o comentário se houver
                    if "#" in line and not line.strip().startswith("#"):
                        comment = " #" + line.split("#", 1)[1].rstrip()
                        new_lines.append(f"Wallpaper={selected_path}{comment}\n")
                    else:
                        new_lines.append(f"Wallpaper={selected_path}\n")
                    wallpaper_updated = True
                else:
                    new_lines.append(line)

            # Se não encontrou nenhuma linha Wallpaper= para atualizar, insere na seção [Wallpapers]
            if not wallpaper_updated:
                final_lines = []
                for line in new_lines:
                    final_lines.append(line)
                    if line.strip().lower() == "[wallpapers]":
                        final_lines.append(f"Wallpaper={selected_path}\n")
                        wallpaper_updated = True
                new_lines = final_lines

            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
                
            print(f"✅ Wallpaper salvo em {CONFIG_PATH}: {selected_path}")

        except Exception as e:
            print(f"Erro ao salvar config: {e}")

    def load_wallpapers(self):
        # FIX 2: Expande ~/ para o caminho completo do usuário (/home/usuario)
        folder_path = os.path.expanduser(self.wallpapers_folder)
        folder = Path(folder_path)
        
        if folder.exists():
            exts = ('.png', '.jpg', '.jpeg', '.webp', '.bmp')
            files = [str(f) for f in folder.iterdir() if f.suffix.lower() in exts]
            # Ordena por nome de arquivo
            files.sort()
            self.wallpapers = [WallpaperCard(f) for f in files]
            print(f"🖼️ Carregados {len(self.wallpapers)} wallpapers de {folder_path}")
        else:
            print(f"⚠️ Pasta de wallpapers não encontrada: {folder_path}")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        # Fundo 100% transparente
        painter.fillRect(self.rect(), QColor(0, 0, 0, 0))

        if not self.wallpapers:
            return

        screen_w = self.width()
        screen_h = self.height()
        center_y = screen_h / 2

        visible_offsets = [-2, -1, 0, 1, 2]
        total_items = len(self.wallpapers)

        card_w, card_h = 280, 420
        spacing = 220

        for offset in visible_offsets:
            idx = (self.current_index + offset) % total_items
            card = self.wallpapers[idx]

            cx = (screen_w / 2) + (offset * spacing)
            cy = center_y

            is_selected = (offset == 0)
            scale = 1.15 if is_selected else 0.85
            opacity = 1.0 if is_selected else 0.6

            painter.save()
            painter.setOpacity(opacity)

            painter.translate(cx, cy)
            painter.scale(scale, scale)
            
            # Recorte estilo trapézio/paralelogramo inclinadinho
            transform = QTransform()
            transform.shear(-0.15, 0.05)
            painter.setTransform(transform, combine=True)

            rect = QRectF(-card_w / 2, -card_h / 2, card_w, card_h)
            path = QPainterPath()
            path.addRoundedRect(rect, 15, 15)

            border_color = QColor("#89b4fa") if is_selected else QColor(255, 255, 255, 100)
            border_width = 4 if is_selected else 2

            painter.save()
            painter.setClipPath(path)
            if not card.pixmap.isNull():
                scaled_pixmap = card.pixmap.scaled(
                    int(card_w), int(card_h), 
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding, 
                    Qt.TransformationMode.SmoothTransformation
                )
                painter.drawPixmap(rect.toRect(), scaled_pixmap)
            painter.restore()

            painter.setPen(Qt.PenStyle.SolidLine)
            pen = painter.pen()
            pen.setColor(border_color)
            pen.setWidth(border_width)
            painter.setPen(pen)
            painter.drawPath(path)

            painter.restore()

    def wheelEvent(self, event: QWheelEvent):
        if not self.wallpapers:
            return
        delta = event.angleDelta().y()
        if delta < 0:
            self.current_index = (self.current_index + 1) % len(self.wallpapers)
        elif delta > 0:
            self.current_index = (self.current_index - 1) % len(self.wallpapers)
        self.update()

    def keyPressEvent(self, event: QKeyEvent):
        if not self.wallpapers and event.key() not in (Qt.Key.Key_Escape, Qt.Key.Key_Backspace):
            return

        key = event.key()

        if key in (Qt.Key.Key_Right, Qt.Key.Key_Down):
            self.current_index = (self.current_index + 1) % len(self.wallpapers)
            self.update()
        elif key in (Qt.Key.Key_Left, Qt.Key.Key_Up):
            self.current_index = (self.current_index - 1) % len(self.wallpapers)
            self.update()

        elif key in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space):
            self.apply_wallpaper()
            self.close()

        # ESC ou BACKSPACE fecha o programa
        elif key in (Qt.Key.Key_Escape, Qt.Key.Key_Backspace):
            self.close()

    def apply_wallpaper(self):
        if not self.wallpapers:
            return
        
        selected_path = self.wallpapers[self.current_index].path
        
        # 1. Aplica o wallpaper via awww
        cmd = [
            "awww", "img", selected_path,
            "--transition-type", self.awww_transition
        ]
        subprocess.Popen(cmd)

        # 2. Salva apenas a linha do Wallpaper no Desktop.conf sem apagar nada
        self.save_wallpaper_to_config(selected_path)

if __name__ == "__main__":
    sys.argv.extend(["-name", "wallpaper-selector"])
    
    app = QApplication(sys.argv)
    app.setApplicationName("wallpaper-selector")
    app.setDesktopFileName("wallpaper-selector")
    
    QGuiApplication.setDesktopFileName("wallpaper-selector")
    
    selector = WallpaperSelectorApp()
    selector.show()

    sys.exit(app.exec())