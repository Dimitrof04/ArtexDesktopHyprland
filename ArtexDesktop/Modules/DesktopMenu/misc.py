from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QCheckBox, QSpinBox, QLineEdit
)

class MiscTab(QWidget):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # 1. Auto Save Checkbox
        autosave_layout = QHBoxLayout()
        autosave_label = QLabel("Ativar Auto Save:")
        self.main_app.autosave_checkbox = QCheckBox()
        self.main_app.autosave_checkbox.stateChanged.connect(self.main_app.toggle_autosave)
        autosave_layout.addWidget(autosave_label)
        autosave_layout.addWidget(self.main_app.autosave_checkbox)
        autosave_layout.addStretch()
        layout.addLayout(autosave_layout)

        # 2. Auto Save Delay (ms) - Mínimo 100ms
        delay_layout = QHBoxLayout()
        delay_label = QLabel("Delay do Auto Save (ms):")
        self.main_app.autosave_delay_spin = QSpinBox()
        self.main_app.autosave_delay_spin.setRange(100, 60000)
        self.main_app.autosave_delay_spin.setSingleStep(100)
        self.main_app.autosave_delay_spin.valueChanged.connect(self.main_app.update_autosave_delay)
        delay_layout.addWidget(delay_label)
        delay_layout.addWidget(self.main_app.autosave_delay_spin)
        delay_layout.addStretch()
        layout.addLayout(delay_layout)

        # 3. Icon Logo
        icon_layout = QHBoxLayout()
        icon_label = QLabel("Icon Logo:")
        self.main_app.icon_logo_input = QLineEdit()
        self.main_app.icon_logo_input.setPlaceholderText("nil")
        self.main_app.icon_logo_input.textChanged.connect(self.main_app.trigger_autosave)
        icon_layout.addWidget(icon_label)
        icon_layout.addWidget(self.main_app.icon_logo_input)
        layout.addLayout(icon_layout)

        layout.addStretch()