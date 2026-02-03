import os
from pathlib import Path
from typing import List, Optional, Any

from PySide6.QtMultimedia import QSoundEffect, QAudioOutput, QMediaPlayer
from PySide6.QtCore import QUrl, QObject, Signal, Slot

from app.utils.paths import get_resource_path, get_user_sounds_path, get_custom_sounds_path
from app.core.config_manager import ConfigManager
from app.core.state import AppState

# Implementa el motor de audio basado en QtMultimedia
# Gestiona la carga y reproducción de efectos de sonido con baja latencia
class SoundSignalBridge(QObject):
    play_sound = Signal(str)

# Instancia global para el puente de señales entre hilos
sound_bridge: SoundSignalBridge = SoundSignalBridge()

class SoundEngine(QObject):
    def __init__(self) -> None:
        super().__init__()
        self.config: ConfigManager = ConfigManager()
        self.effects: List[QSoundEffect] = [] 
        self.current_pack_path: Optional[Path] = None
        self.volume: float = self.config.get("volume", 50) / 100.0
        
        # Conecta la señal del puente para ejecución en el hilo principal
        sound_bridge.play_sound.connect(self._play_on_main_thread)
        
        # Asegura la existencia del directorio de sonidos personalizados
        Path(get_custom_sounds_path()).mkdir(parents=True, exist_ok=True)
        self.load_sound_pack(str(self.config.get("sound_pack", "Default")))

    def load_sound_pack(self, pack_name: str) -> None:
        # Carga el pack de sonidos especificado en memoria
        self.effects.clear()
        
        sound_file: Optional[Path] = None
        
        if pack_name == "Default":
            # Carga el sonido predeterminado de los recursos
            sound_file = Path(get_resource_path("sounds")) / "click.wav"
        else:
            # Busca archivos en ubicaciones personalizadas
            custom_path: Path = Path(get_custom_sounds_path())
            potential_file: Path = custom_path / f"{pack_name}.wav"
            
            if potential_file.exists():
                sound_file = potential_file
            else:
                user_path: Path = Path(get_user_sounds_path()) / pack_name / "click.wav"
                if user_path.exists():
                    sound_file = user_path

        # Fallback al sonido por defecto si no se encuentra el archivo
        if not sound_file or not sound_file.exists():
            print(f"No se encontró sonido para: {pack_name}")
            sound_file = Path(get_resource_path("sounds")) / "click.wav"

        self.current_pack_path = sound_file

        # Inicializa el objeto QSoundEffect
        effect: QSoundEffect = QSoundEffect()
        effect.setSource(QUrl.fromLocalFile(str(sound_file)))
        effect.setVolume(self.volume)
        self.effects.append(effect)
        print(f"Sonido cargado: {pack_name} -> {sound_file}")

    @Slot(str)
    def _play_on_main_thread(self, sound_name: str) -> None:
        # Ejecuta la reproducción del sonido en el hilo UI
        if not AppState.is_active():
            return
            
        if self.volume <= 0:
            return

        # Gestiona la polifonía rotando o creando nuevos efectos
        if self.effects:
            # Busca un efecto disponible (inactivo)
            available: Optional[QSoundEffect] = None
            for ef in self.effects:
                if not ef.isPlaying():
                    available = ef
                    break
            
            # Si todos están ocupados, crea uno nuevo hasta el límite
            if not available:
                if len(self.effects) < 10: # Límite de polifonía
                    new_ef: QSoundEffect = QSoundEffect()
                    new_ef.setSource(self.effects[0].source())
                    new_ef.setVolume(self.volume)
                    self.effects.append(new_ef)
                    available = new_ef
                else:
                    available = self.effects[0] # Reusa el primero si se excede el límite

            available.setVolume(self.volume)
            available.play()

    def set_volume(self, volume_percent: int) -> None:
        # Actualiza el volumen global
        self.volume = max(0, min(100, volume_percent)) / 100.0
        self.config.set("volume", volume_percent)
        
        # Aplica el nuevo volumen a todas las instancias activas
        for ef in self.effects:
            ef.setVolume(self.volume)

    @staticmethod
    def get_available_packs() -> List[str]:
        # Enumera los packs de sonido disponibles
        packs: List[str] = ["Default"]
        
        custom_path: Path = Path(get_custom_sounds_path())
        if custom_path.exists():
            for item in custom_path.glob("*.wav"):
                # Formatea el nombre para visualización
                clean_name: str = item.stem.capitalize()
                packs.append(clean_name)
                
        return packs

# Variable global para el Singleton
_engine_instance: Optional[SoundEngine] = None

def initialize_sound_engine() -> SoundEngine:
    # Inicializa y retorna la instancia única del motor de sonido
    global _engine_instance
    _engine_instance = SoundEngine()
    return _engine_instance

def get_engine() -> Optional[SoundEngine]:
    # Obtiene la instancia actual del motor
    return _engine_instance
