from PySide6.QtMultimedia import QSoundEffect, QAudioOutput, QMediaPlayer
from PySide6.QtCore import QUrl, QObject, Signal, Slot
import os
from pathlib import Path
from app.utils.paths import get_resource_path, get_user_sounds_path, get_custom_sounds_path
from app.core.config_manager import ConfigManager
from app.core.state import AppState

# Motor de sonido usando QtMultimedia.
# Permite reproducir multiples sonidos a la vez y controlar volumen.

class SoundSignalBridge(QObject):
    play_sound = Signal(str)

# Instancia global del puente
sound_bridge = SoundSignalBridge()

class SoundEngine(QObject):
    def __init__(self):
        super().__init__()
        self.config = ConfigManager()
        self.effects = [] 
        self.current_pack_path = ""
        self.volume = self.config.get("volume", 50) / 100.0
        
        # Conectamos la señal del puente a nuestra funcion de reproduccion
        sound_bridge.play_sound.connect(self._play_on_main_thread)
        
        Path(get_custom_sounds_path()).mkdir(parents=True, exist_ok=True)
        self.load_sound_pack(self.config.get("sound_pack", "Default"))

    def load_sound_pack(self, pack_name):
        self.effects.clear()
        
        sound_file = None
        
        if pack_name == "Default":
            # Usar sonido interno
            sound_file = Path(get_resource_path("sounds")) / "click.wav"
        else:
            # Buscar en Custom/<nombre>.wav
            custom_path = Path(get_custom_sounds_path())
            potential_file = custom_path / f"{pack_name}.wav"
            
            if potential_file.exists():
                sound_file = potential_file
            else:
                user_path = Path(get_user_sounds_path()) / pack_name / "click.wav"
                if user_path.exists():
                    sound_file = user_path

        if not sound_file or not sound_file.exists():
            print(f"No se encontro sonido para: {pack_name}")
            sound_file = Path(get_resource_path("sounds")) / "click.wav"

        self.current_pack_path = sound_file

        # Cargar efecto
        effect = QSoundEffect()
        effect.setSource(QUrl.fromLocalFile(str(sound_file)))
        effect.setVolume(self.volume)
        self.effects.append(effect)
        print(f"Sonido cargado: {pack_name} -> {sound_file}")

    @Slot(str)
    def _play_on_main_thread(self, sound_name):
        if not AppState.is_active():
            return
            
        if self.volume <= 0:
            return

        # Reproducir cualquiera de los efectos cargados o rotar si hubiera varios
        if self.effects:
            # Buscamos uno que no este sonando o el mas antiguo
            available = None
            for ef in self.effects:
                if not ef.isPlaying():
                    available = ef
                    break
            
            if not available:
                if len(self.effects) < 10: # Limite de 10 voces
                    new_ef = QSoundEffect()
                    new_ef.setSource(self.effects[0].source())
                    new_ef.setVolume(self.volume)
                    self.effects.append(new_ef)
                    available = new_ef
                else:
                    available = self.effects[0] # Reusar el primero

            available.setVolume(self.volume) # Actualizar volumen por si hay un cambio
            available.play()

    def set_volume(self, volume_percent):
        self.volume = max(0, min(100, volume_percent)) / 100.0
        self.config.set("volume", volume_percent)
        # Actualizamos volumen de instancias
        for ef in self.effects:
            ef.setVolume(self.volume)

    @staticmethod
    def get_available_packs():
        packs = ["Default"]
        
        custom_path = Path(get_custom_sounds_path())
        if custom_path.exists():
            # Listar archivos .wav
            for item in custom_path.glob("*.wav"):
                # Mostrar "Nombre" en lugar de "nombre" o "NOMBRE"
                clean_name = item.stem.capitalize()
                packs.append(clean_name)
                
        return packs

# Instancia global singleton
_engine_instance = None

def initialize_sound_engine():
    global _engine_instance
    _engine_instance = SoundEngine()
    return _engine_instance

def get_engine():
    return _engine_instance
