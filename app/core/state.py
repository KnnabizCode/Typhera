# Gestiona el estado global de la aplicación
# Permite un acceso centralizado para verificar si la aplicación está activa o en pausa
class AppState:
    # Mantiene el estado activo compartir entre componentes
    _is_active: bool = True
    
    @classmethod
    def is_active(cls) -> bool:
        # Retorna el estado actual
        return cls._is_active
    
    @classmethod
    def set_active(cls, active: bool) -> None:
        # Actualiza el estado global de la aplicación
        cls._is_active = active
        print(f"Estado cambiado a: {'Activo' if active else 'Pausa'}")

    @classmethod
    def toggle(cls) -> None:
        # Alterna entre activo y pausa
        cls.set_active(not cls.is_active())
