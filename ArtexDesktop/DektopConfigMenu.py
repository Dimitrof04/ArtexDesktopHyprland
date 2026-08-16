import sys
import psutil
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QApplication, QWidget, QListWidget, QStackedWidget,
    QHBoxLayout, QVBoxLayout, QLabel, QProgressBar, QFrame
)

class DiskCard(QFrame):
    """Widget individual para cada disco com barra de progresso e informações."""
    def __init__(self, device, mountpoint):
        super().__init__()
        self.mountpoint = mountpoint
        self.device = device
        
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            DiskCard {
                background-color: #2b2b2b;
                border-radius: 10px;
                padding: 15px;
            }
            QLabel {
                color: #ffffff;
            }
        """)

        layout = QVBoxLayout(self)

        # Nome do Disco e Ponto de Montagem
        self.title_label = QLabel(f"<b>{device}</b> ({mountpoint})")
        self.title_label.setStyleSheet("font-size: 15px;")
        layout.addWidget(self.title_label)

        # Rótulo de uso de espaço
        self.info_label = QLabel("Calculando...")
        self.info_label.setStyleSheet("font-size: 13px; color: #b0b0b0;")
        layout.addWidget(self.info_label)

        # Barra de Progresso
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(18)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: #404040;
                border-radius: 9px;
            }
            QProgressBar::chunk {
                background-color: #3b82f6;
                border-radius: 9px;
            }
        """)
        layout.addWidget(self.progress_bar)

        self.update_usage()

    def update_usage(self):
        try:
            usage = psutil.disk_usage(self.mountpoint)
            total_gb = usage.total / (1024**3)
            used_gb = usage.used / (1024**3)
            percent = usage.percent

            self.info_label.setText(f"{used_gb:.1f} GB de {total_gb:.1f} GB usados ({percent}%)")
            self.progress_bar.setValue(int(percent))

            # Altera a cor se o armazenamento estiver quase cheio
            if percent > 90:
                chunk_color = "#ef4444"  # Vermelho
            elif percent > 75:
                chunk_color = "#f97316"  # Laranja
            else:
                chunk_color = "#3b82f6"  # Azul

            self.progress_bar.setStyleSheet(f"""
                QProgressBar {{
                    border: none;
                    background-color: #404040;
                    border-radius: 9px;
                }}
                QProgressBar::chunk {{
                    background-color: {chunk_color};
                    border-radius: 9px;
                }}
            """)
        except PermissionError:
            self.info_label.setText("Sem permissão de acesso.")

class DiskMonitorApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Monitor de Discos")
        self.resize(520, 260)
        
        # Tema escuro para integrar com o Hyprland
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e2e;
                color: #cdd6f4;
                font-family: sans-serif;
            }
            QListWidget {
                background-color: #181825;
                border: 1px solid #313244;
                border-radius: 8px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 10px;
                border-radius: 5px;
            }
            QListWidget::item:selected {
                background-color: #45475a;
                color: #cdd6f4;
            }
        """)

        main_layout = QHBoxLayout(self)

        # Lista de Discos na Esquerda (QListWidget)
        self.list_widget = QListWidget()
        self.list_widget.setFixedWidth(160)
        main_layout.addWidget(self.list_widget)

        # Painel Empilhado na Direita (QStackedWidget)
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)

        # Guarda os cards de discos para o QTimer atualizar
        self.disk_cards = []

        # Carrega os discos
        self.load_disks()

        # Conecta a seleção da lista com o painel correto
        self.list_widget.currentRowChanged.connect(self.stacked_widget.setCurrentIndex)

        # QTimer para atualizar a leitura a cada 3 segundos
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_all_disks)
        self.timer.start(3000)

    def load_disks(self):
        for part in psutil.disk_partitions(all=False):
            # Filtra partições reais no Linux
            if part.fstype in ("ext4", "btrfs", "xfs", "vfat", "ntfs", "zfs"):
                display_name = f"{part.device}\n({part.mountpoint})"
                
                # Adiciona na lista
                self.list_widget.addItem(display_name)

                # Cria o card e adiciona no StackedWidget
                card = DiskCard(part.device, part.mountpoint)
                self.disk_cards.append(card)
                self.stacked_widget.addWidget(card)

        if self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)

    def refresh_all_disks(self):
        """Atualiza a porcentagem de todos os discos automaticamente."""
        for card in self.disk_cards:
            card.update_usage()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DiskMonitorApp()
    window.show()
    sys.exit(app.exec())