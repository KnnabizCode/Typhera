from pynput import keyboard
from app.core.sound_engine import sound_bridge
from app.core.state import AppState

# Este modulo escucha cuando presionamos teclas.
# Usa la libreria 'pynput'.

class KeyboardMonitor:
    def __init__(self):
        self.listener = None
        self.pressed_keys = set()

    def start(self):
        if self.listener is None:
            self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
            self.listener.start()
            print("Monitor de teclado iniciado.")

    def stop(self):
        if self.listener:
            self.listener.stop()
            self.listener = None
            self.pressed_keys.clear()

    def on_release(self, key):
        try:
            if key in self.pressed_keys:
                self.pressed_keys.remove(key)
        except:
            pass

    def on_press(self, key):
        # Evitar reproducir el sonido si se deja presionada la tecla
        if key in self.pressed_keys:
            return
            
        self.pressed_keys.add(key)

        # Si la app esta en modo 'Pausa' en state.py, ignoramos la tecla
        if not AppState.is_active():
            return

        try:
            # Enviamos la señal para reproducir sonido en el hilo principal
            sound_bridge.play_sound.emit("click")
        except Exception as e:
            pass # Evitar romper el listener si algo falla

