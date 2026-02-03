from typing import Set, Optional, Any
from pynput import keyboard
from app.core.sound_engine import sound_bridge
from app.core.state import AppState

# Monitoriza los eventos globales del teclado utilizando pynput
class KeyboardMonitor:
    def __init__(self) -> None:
        self.listener: Optional[keyboard.Listener] = None
        self.pressed_keys: Set[Any] = set()

    def start(self) -> None:
        # Inicia el listener de teclado en un hilo separado si no está activo
        if self.listener is None:
            self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
            self.listener.start()
            print("Monitor de teclado iniciado.")

    def stop(self) -> None:
        # Detiene el listener y limpia el estado
        if self.listener:
            self.listener.stop()
            self.listener = None
            self.pressed_keys.clear()

    def on_release(self, key: Any) -> None:
        # Gestiona el evento de liberación de tecla
        try:
            if key in self.pressed_keys:
                self.pressed_keys.remove(key)
        except Exception:
            pass

    def on_press(self, key: Any) -> None:
        # Gestiona el evento de presión de tecla
        
        # Evita repeticiones si la tecla se mantiene presionada
        if key in self.pressed_keys:
            return
            
        self.pressed_keys.add(key)

        # Ignora el evento si la aplicación está pausada globalmente
        if not AppState.is_active():
            return

        try:
            # Emite la señal al hilo principal para reproducir el efecto de sonido
            sound_bridge.play_sound.emit("click")
        except Exception:
            # Previene que un error de audio detenga el listener
            pass

