from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QFrame, QSlider, QComboBox
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QAction
from app.core.config_manager import ConfigManager
from app.core.state import AppState
from app.core.sound_engine import get_engine, SoundEngine
from app.utils.paths import get_resource_path
import sys

# Esta es la ventana principal que ve el usuario.
# Debe ser moderna y bonita.

class TypheraWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = ConfigManager()
        self.sound_engine = get_engine() # Obtenemos la instancia del motor
        self.setWindowTitle("Typhera")
        self.setFixedSize(400, 450) # Aumentamos altura para nuevos controles
        
        # Configuramos el icono de la ventana
        # Asumimos que existe un icon.ico en resources, en caso contrario, no mostrara el icono
        self.setWindowIcon(QIcon(get_resource_path("icons/icon.ico")))

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(30, 30, 30, 30) # Mas margen
        self.main_layout.setSpacing(15)

        top_bar_layout = QHBoxLayout()
        top_bar_layout.addStretch() # Empujar a la derecha

        self.theme_btn = QPushButton("☀") # Icono o texto corto
        self.theme_btn.setFixedSize(30, 30)
        self.theme_btn.setCursor(Qt.PointingHandCursor)
        self.theme_btn.clicked.connect(self.toggle_theme)
        # Tooltip
        self.theme_btn.setToolTip("Cambiar Tema")
        top_bar_layout.addWidget(self.theme_btn)
        
        self.main_layout.addLayout(top_bar_layout)

        # Usamos un layout vertical interno para el contenido y lo centramos
        content_layout = QVBoxLayout()
        content_layout.setSpacing(20)

        self.main_layout.addStretch() # Espacio arriba
        self.main_layout.addLayout(content_layout)
        self.main_layout.addStretch() # Espacio abajo

        # Titulo
        self.title_label = QLabel("Typhera")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 32px; font-weight: bold;")
        content_layout.addWidget(self.title_label)

        # Estado (Activo / Pausa)
        self.status_label = QLabel("Estado: Activo")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 16px; margin-bottom: 5px;")
        content_layout.addWidget(self.status_label)

        # Boton Toggle (Activar / Desactivar)
        self.toggle_btn = QPushButton("Pausar")
        self.toggle_btn.setCursor(Qt.PointingHandCursor)
        self.toggle_btn.clicked.connect(self.toggle_active_state)
        self.toggle_btn.setMinimumHeight(45)
        content_layout.addWidget(self.toggle_btn)

        # Controles de Audio
        sep_label = QLabel("Configuración de Audio")
        sep_label.setAlignment(Qt.AlignCenter)
        sep_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 15px;")
        content_layout.addWidget(sep_label)

        # Selector de Pack
        self.pack_selector = QComboBox()
        self.pack_selector.addItems(SoundEngine.get_available_packs())
        # Seleccionar el actual
        current_pack = self.config.get("sound_pack", "Default")
        self.pack_selector.setCurrentText(current_pack)
        self.pack_selector.currentTextChanged.connect(self.change_sound_pack)
        content_layout.addWidget(self.pack_selector)

        # Slider de Volumen
        vol_layout = QHBoxLayout()
        vol_label = QLabel("Volumen:")
        self.vol_slider = QSlider(Qt.Horizontal)
        self.vol_slider.setRange(0, 100)
        self.vol_slider.setValue(self.config.get("volume", 50))
        self.vol_slider.valueChanged.connect(self.change_volume)
        
        vol_layout.addWidget(vol_label)
        vol_layout.addWidget(self.vol_slider)
        content_layout.addLayout(vol_layout)


        # Aplicamos el tema guardado
        self.apply_theme()

        # Actualizar UI inicial
        self.update_ui_state()

    def apply_theme(self):
        current_theme = self.config.get("theme", "dark")
        
        if current_theme == "dark":
            # Colores oscuros (#1e1e2e)
            bg_color = "#1e1e2e"
            text_color = "#ffffff"
            btn_bg = "#313244" # Surface0
            btn_text = "#cdd6f4" # Text
            btn_hover = "#45475a" # Surface1
            
            # Estilo especifico para el boton de tema
            theme_btn_style = f"""
                QPushButton {{
                    background-color: transparent;
                    color: {text_color};
                    border-radius: 15px; /* Redondo */
                    font-size: 18px;
                }}
                QPushButton:hover {{
                    background-color: {btn_hover};
                }}
            """
        else:
            # Colores claros
            bg_color = "#eff1f5" # Base
            text_color = "#4c4f69" # Text
            btn_bg = "#e6e9ef" # Surface0
            btn_text = "#4c4f69"
            btn_hover = "#bcc0cc" # Surface1
            
            theme_btn_style = f"""
                QPushButton {{
                    background-color: transparent;
                    color: {text_color};
                    border-radius: 15px;
                    font-size: 18px;
                }}
                QPushButton:hover {{
                    background-color: {btn_hover};
                }}
            """

        self.theme_btn.setText("🌙" if current_theme == "light" else "☀")
        self.theme_btn.setStyleSheet(theme_btn_style)

        # Aplicamos la hoja de estilo general
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {bg_color};
            }}
            QLabel {{
                color: {text_color};
            }}
            QPushButton {{
                background-color: {btn_bg};
                color: {btn_text};
                border: none;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton#toggle_btn:hover {{
                background-color: {btn_hover};
            }}
        """)
        
        # Asignamos ID al boton toggle para que tome el estilo especifico si es necesario
        self.toggle_btn.setObjectName("toggle_btn")

    def toggle_theme(self):
        current = self.config.get("theme", "dark")
        new_theme = "light" if current == "dark" else "dark"
        self.config.set("theme", new_theme)
        self.apply_theme()

    def update_ui_state(self):
        is_active = AppState.is_active()
        if is_active:
            self.status_label.setText("Estado: Activo 🔊")
            self.toggle_btn.setText("Pausar")
            # Podriamos cambiar color del texto a verde
            self.status_label.setStyleSheet("color: #a6e3a1; font-weight: bold;") # Verde pastel
        else:
            self.status_label.setText("Estado: Pausa 🔇")
            self.toggle_btn.setText("Reanudar")
            self.status_label.setStyleSheet("color: #f38ba8; font-weight: bold;") # Rojo pastel

    def toggle_active_state(self):
        AppState.toggle()
        self.update_ui_state()

    def change_volume(self, value):
        if self.sound_engine:
            self.sound_engine.set_volume(value)

    def change_sound_pack(self, pack_name):
        if self.sound_engine:
            self.sound_engine.load_sound_pack(pack_name)
            self.config.set("sound_pack", pack_name)

    def closeEvent(self, event):
        event.ignore()
        self.hide()
