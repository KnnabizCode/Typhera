# Guarda el estado global de la aplicacion
# Puede ser accedido desde cualquier parte para saber si la app esta activa o en pausa.

class AppState:
    # Variable estatica compartida
    _is_active = True
    
    @classmethod
    def is_active(cls):
        return cls._is_active
    
    @classmethod
    def set_active(cls, active: bool):
        cls._is_active = active
        # Aqui podriamos avisar a otras partes si cambiamos el estado
        print(f"Estado cambiado a: {'Activo' if active else 'Pausa'}")

    @classmethod
    def toggle(cls):
        cls.set_active(not cls.is_active())
