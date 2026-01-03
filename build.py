import os
import subprocess
import sys

# Este script facilita la creacion del .exe usando Nuitka.
def build():
    # Definimos el comando
    # --onefile: Crea un solo archivo .exe
    # La salida será en 'build/nuitka/'.
    
    cmd = [
        sys.executable, "-m", "nuitka",
        "--onefile", 
        "--enable-plugin=pyside6",
        "--disable-console",
        "--output-dir=build/nuitka",
        "--windows-icon-from-ico=app/resources/icons/icon.ico",
        "--include-data-dir=app/resources=app/resources", # Incluir todo resources (iconos y sonidos)
        "main.py"
    ]
    
    print("Iniciando compilacion con Nuitka...")
    print(" ".join(cmd))
    
    try:
        subprocess.check_call(cmd)
        print("\nCompilacion exitosa. Revisa la carpeta build/nuitka/")
    except subprocess.CalledProcessError as e:
        print(f"\nError durante la compilacion: {e}")

if __name__ == "__main__":
    build()
