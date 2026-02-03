import sys
from typing import Optional

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, 
    QFrame, QSlider, QComboBox
)
from PySide6.QtCore import Qt, QSize, QUrl, QEvent
from PySide6.QtGui import QIcon, QAction, QDesktopServices, QMouseEvent, QEnterEvent

from app.core.config_manager import ConfigManager
from app.core.state import AppState
from app.core.sound_engine import get_engine, SoundEngine
from app.utils.paths import get_resource_path
from app.utils.updater import check_for_updates

# Etiqueta clickeable que actúa como un hipervínculo
class WebLinkLabel(QLabel):
    def __init__(self, text: str, url: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(text, parent)
        self.url: str = url
        self.setCursor(Qt.PointingHandCursor)
        self.setAlignment(Qt.AlignCenter)
        
    def mousePressEvent(self, event: QMouseEvent) -> None:
        # Abre la URL en el navegador predeterminado
        QDesktopServices.openUrl(QUrl(self.url))
        
    def enterEvent(self, event: QEnterEvent) -> None:
        # Resalta el texto al pasar el mouse por encima
        font = self.font()
        font.setBold(True)
        self.setFont(font)
        super().enterEvent(event)
        
    def leaveEvent(self, event: QEvent) -> None:
        # Restaura el estilo original al salir el mouse
        font = self.font()
        font.setBold(False)
        self.setFont(font)
        super().leaveEvent(event)

# Ventana principal de la aplicación Typhera
# Gestiona la interfaz de usuario, la configuración visual y la interacción con el usuario
class TypheraWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.config: ConfigManager = ConfigManager()
        # Obtenemos la instancia del motor de sonido
        self.sound_engine: Optional[SoundEngine] = get_engine() 
        
        self.setWindowTitle("Typhera")
        # Aumentamos altura para nuevos controles
        self.setFixedSize(400, 450) 
        
        # Carga el icono de la ventana si existe
        # Asumimos que existe un icon.ico en resources, en caso contrario, no mostrara el icono
        self.setWindowIcon(QIcon(get_resource_path("icons/icon.ico")))

        # Configura el contenedor principal
        central_widget: QWidget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout: QVBoxLayout = QVBoxLayout(central_widget)
        # Mas margen
        self.main_layout.setContentsMargins(30, 30, 30, 30) 
        self.main_layout.setSpacing(15)

        # Construye la barra superior (Top Bar)
        top_bar_layout: QHBoxLayout = QHBoxLayout()
        
        # Inicializa botón de actualizaciones
        self.update_btn: QPushButton = QPushButton("🔄")
        self.update_btn.setFixedSize(40, 40)
        self.update_btn.setCursor(Qt.PointingHandCursor)
        self.update_btn.setToolTip("Buscar Actualizaciones")
        self.update_btn.clicked.connect(self.manual_update_check)
        top_bar_layout.addWidget(self.update_btn)

        # Empujar a la derecha
        top_bar_layout.addStretch() 

        # Inicializa botón de tema
        self.theme_btn: QPushButton = QPushButton("☀️") # Icono o texto corto
        self.theme_btn.setFixedSize(40, 40)
        self.theme_btn.setCursor(Qt.PointingHandCursor)
        self.theme_btn.clicked.connect(self.toggle_theme)
        # Tooltip
        self.theme_btn.setToolTip("Cambiar Tema")
        top_bar_layout.addWidget(self.theme_btn)
        
        self.main_layout.addLayout(top_bar_layout)

        # Construye el área de contenido
        # Usamos un layout vertical interno para el contenido y lo centramos
        content_layout: QVBoxLayout = QVBoxLayout()
        content_layout.setSpacing(20)

        # Espacio arriba
        self.main_layout.addStretch() 
        self.main_layout.addLayout(content_layout)
        # Espacio abajo
        self.main_layout.addStretch() 

        # Título principal
        self.title_label: QLabel = QLabel("Typhera")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 32px; font-weight: bold;")
        content_layout.addWidget(self.title_label)

        # Etiqueta de estado (Activo / Pausa)
        self.status_label: QLabel = QLabel("Estado: Activo")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 16px; margin-bottom: 5px;")
        content_layout.addWidget(self.status_label)

        # Botón de alternancia de estado (Activar / Desactivar)
        self.toggle_btn: QPushButton = QPushButton("Pausar")
        self.toggle_btn.setCursor(Qt.PointingHandCursor)
        self.toggle_btn.clicked.connect(self.toggle_active_state)
        self.toggle_btn.setMinimumHeight(45)
        # Asigna ID para estilos específicos
        self.toggle_btn.setObjectName("toggle_btn")
        content_layout.addWidget(self.toggle_btn)

        # Separador visual para configuración de audio
        sep_label: QLabel = QLabel("Configuración de Audio")
        sep_label.setAlignment(Qt.AlignCenter)
        sep_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 15px;")
        content_layout.addWidget(sep_label)

        # Selector de Pack de Sonido
        self.pack_selector: QComboBox = QComboBox()
        self.pack_selector.addItems(SoundEngine.get_available_packs())
        # Seleccionar el pack actual guardado en la configuración
        current_pack: str = str(self.config.get("sound_pack", "Default"))
        self.pack_selector.setCurrentText(current_pack)
        self.pack_selector.currentTextChanged.connect(self.change_sound_pack)
        content_layout.addWidget(self.pack_selector)

        # Slider de Volumen
        vol_layout: QHBoxLayout = QHBoxLayout()
        vol_label: QLabel = QLabel("Volumen:")
        self.vol_slider: QSlider = QSlider(Qt.Horizontal)
        self.vol_slider.setRange(0, 100)
        self.vol_slider.setValue(int(self.config.get("volume", 50)))
        self.vol_slider.valueChanged.connect(self.change_volume)
        
        vol_layout.addWidget(vol_label)
        vol_layout.addWidget(self.vol_slider)
        content_layout.addLayout(vol_layout)

        content_layout.addStretch()
        
        # Enlace del pie de página
        self.footer_link: WebLinkLabel = WebLinkLabel("Web: knnabiz.vip", "https://knnabiz.vip")
        content_layout.addWidget(self.footer_link)

        # Aplica el tema inicial y actualiza la UI
        self.apply_theme()
        self.update_ui_state()

    def apply_theme(self) -> None:
        # Aplica los colores y estilos CSS basados en el tema seleccionado
        current_theme: str = str(self.config.get("theme", "dark"))
        
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
                    border: 1px solid {btn_hover};
                    border-radius: 20px; /* Redondo */
                    font-size: 14px;
                }}
                QPushButton:hover {{
                    background-color: {btn_hover};
                    border-color: {text_color};
                }}
            """
        else:
            # Modo Claro - Paleta Mejorada
            bg_color = "#FAFAFA" # Blanco Roto / Gris Muy Claro
            text_color = "#2C3E50" # Azul Oscuro / Gris Antracita
            btn_bg = "#FFFFFF" # Superficie Blanca
            btn_text = "#2C3E50"
            btn_hover = "#F0F0F0" # Gris Tenue
            
            theme_btn_style = f"""
                QPushButton {{
                    background-color: transparent;
                    color: {text_color};
                    border: 1px solid #E0E0E0;
                    border-radius: 20px;
                    font-size: 14px;
                }}
                QPushButton:hover {{
                    background-color: #F0F0F0;
                    border-color: {text_color};
                }}
            """

        # Actualiza el texto del botón de tema y aplica estilos a los botones de la barra superior
        self.theme_btn.setText("🌙" if current_theme == "light" else "☀️")
        self.theme_btn.setStyleSheet(theme_btn_style)
        self.update_btn.setStyleSheet(theme_btn_style)

        # Actualiza el estilo del footer
        self.footer_link.setStyleSheet(f"color: {text_color}; margin-top: 10px; font-size: 12px;")

        # Aplica la hoja de estilo global
        if current_theme == "dark":
            # Estilo Dark Mode (Mejorado)
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
                QPushButton:hover {{
                    background-color: {btn_hover};
                }}
                QPushButton:pressed {{
                    background-color: #585b70;
                }}
                QComboBox {{
                    padding: 5px;
                    border: 1px solid {btn_hover};
                    border-radius: 5px;
                    background-color: {btn_bg};
                    color: {text_color};
                }}
                QComboBox::drop-down {{
                    border: none;
                }}
                QComboBox QAbstractItemView {{
                    border: 1px solid {btn_hover};
                    selection-background-color: {btn_hover};
                    selection-color: {text_color};
                    background-color: {btn_bg};
                    color: {text_color};
                    outline: none;
                }}
                QSlider::groove:horizontal {{
                    border: 1px solid {btn_hover};
                    height: 6px;
                    background: {btn_bg};
                    margin: 2px 0;
                    border-radius: 3px;
                }}
                QSlider::sub-page:horizontal {{
                    background: #585b70;
                    border: 1px solid #585b70;
                    height: 6px;
                    border-radius: 3px;
                }}
                QSlider::handle:horizontal {{
                    background: {text_color};
                    border: 1px solid {text_color};
                    width: 16px;
                    height: 16px;
                    margin: -6px 0;
                    border-radius: 8px;
                }}
            """)
        else:
            # Estilo Light Mode (Nuevo y Mejorado)
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
                    border: 1px solid #E0E0E0; /* Borde sutil */
                    border-radius: 8px;
                    padding: 10px;
                    font-size: 14px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {btn_hover};
                    border: 1px solid #D0D0D0;
                }}
                QPushButton:pressed {{
                    background-color: #E6E6E6;
                    border: 1px solid #C0C0C0;
                }}
                QPushButton:disabled {{
                    background-color: #F5F5F5;
                    color: #A0A0A0;
                    border: 1px solid #EEEEEE;
                }}
                QComboBox {{
                    padding: 5px;
                    border: 1px solid #E0E0E0;
                    border-radius: 5px;
                    background-color: {btn_bg};
                    color: {text_color};
                }}
                QComboBox::drop-down {{
                    border: none;
                }}
                QComboBox QAbstractItemView {{
                     border: 1px solid #E0E0E0;
                     selection-background-color: #D6D6D6; /* Un poco mas oscuro para resaltar seleccion */
                     selection-color: {text_color};
                     background-color: {btn_bg};
                     color: {text_color}; /* Forzar color de texto oscuro */
                     outline: none;
                }}
                QSlider::groove:horizontal {{
                    border: 1px solid #E0E0E0;
                    height: 6px; /* ranura ligeramente más delgada */
                    background: #F0F0F0;
                    margin: 2px 0;
                    border-radius: 3px;
                }}
                QSlider::sub-page:horizontal {{
                    background: #A0A0A0; /* Color de la parte rellena */
                    border: 1px solid #A0A0A0;
                    height: 6px;
                    border-radius: 3px;
                }}
                QSlider::handle:horizontal {{
                    background: {text_color};
                    border: 1px solid {text_color};
                    width: 16px;
                    height: 16px;
                    margin: -6px 0;
                    border-radius: 8px;
                }}
            """)
        
    def toggle_theme(self) -> None:
        # Alterna entre temas claro y oscuro y persiste la elección
        current: str = str(self.config.get("theme", "dark"))
        new_theme: str = "light" if current == "dark" else "dark"
        self.config.set("theme", new_theme)
        self.apply_theme()

    def update_ui_state(self) -> None:
        # Actualiza visualmente los indicadores de estado de la aplicación
        is_active: bool = AppState.is_active()
        if is_active:
            self.status_label.setText("Estado: Activo 🔊")
            self.toggle_btn.setText("Pausar")
            # Podriamos cambiar color del texto a verde
            self.status_label.setStyleSheet("color: #a6e3a1; font-weight: bold;") # Verde pastel
        else:
            self.status_label.setText("Estado: Pausa 🔇")
            self.toggle_btn.setText("Reanudar")
            self.status_label.setStyleSheet("color: #f38ba8; font-weight: bold;") # Rojo pastel

    def toggle_active_state(self) -> None:
        # Maneja el evento de click en el botón de pausa/reanudar
        AppState.toggle()
        self.update_ui_state()

    def change_volume(self, value: int) -> None:
        # Ajusta el volumen del motor de sonido
        if self.sound_engine:
            self.sound_engine.set_volume(value)

    def change_sound_pack(self, pack_name: str) -> None:
        # Carga un nuevo pack de sonidos según la selección del usuario
        if self.sound_engine:
            self.sound_engine.load_sound_pack(pack_name)
            self.config.set("sound_pack", pack_name)

    def manual_update_check(self) -> None:
        # Inicia una búsqueda forzada de actualizaciones
        check_for_updates(self, force=True)

    def closeEvent(self, event: QEvent) -> None:
        # Minimiza a la bandeja en lugar de cerrar la aplicación
        event.ignore()
        self.hide()
