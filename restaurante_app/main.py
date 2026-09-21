"""
Módulo: main.py

Punto de arranque de la aplicación gráfica del restaurante. Crea una
ÚNICA ventana principal de Tkinter, prepara los servicios
(ArchivoServicio y RestauranteServicio), les entrega esos servicios ya
listos a las vistas (LoginView y MainView) y controla el cambio entre
la pantalla de acceso y la interfaz principal dentro de esa misma
ventana.

main.py no lee archivos JSON, no valida credenciales ni contiene
reglas del restaurante: solo coordina qué vista se muestra en cada
momento, dentro de un único ciclo de ejecución (root.mainloop()).

Flujo general:
    main.py prepara Tkinter y los servicios
        -> LoginView (ingreso de usuario y contraseña)
        -> RestauranteServicio valida el acceso
        -> MainView (productos registrados | usuarios registrados |
           ventas, pendiente)
        -> cerrar sesión
        -> LoginView
"""

import tkinter as tk

from servicios.archivo_servicio import ArchivoServicio
from servicios.restaurante_servicio import RestauranteServicio
from ui.login_view import LoginView
from ui.main_view import MainView


class Aplicacion:
    """Coordina la ventana principal, los servicios y el cambio entre vistas."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Restaurante App")
        self.root.geometry("880x580")
        self.root.minsize(780, 520)

        # Preparación de los servicios: se crean una sola vez y se
        # comparten con las vistas que los necesiten.
        self.archivo_servicio = ArchivoServicio()
        self.restaurante_servicio = RestauranteServicio(self.archivo_servicio)
        self.restaurante_servicio.cargar_datos()

        print(
            f"Se cargaron {self.restaurante_servicio.contar_productos()} producto(s) "
            f"y {self.restaurante_servicio.contar_usuarios()} usuario(s) desde la carpeta datos/."
        )

        # Contenedor único donde se van a montar y desmontar las
        # vistas; la ventana principal (root) nunca se destruye.
        self.contenedor = tk.Frame(self.root)
        self.contenedor.pack(fill="both", expand=True)

        self.vista_actual: tk.Frame | None = None
        self.mostrar_login()

    def mostrar_login(self) -> None:
        """Destruye la vista actual (si existe) y muestra la pantalla de acceso."""
        self._limpiar_contenedor()
        self.vista_actual = LoginView(
            self.contenedor,
            self.restaurante_servicio,
            self.mostrar_principal,
        )
        self.vista_actual.pack(fill="both", expand=True)

    def mostrar_principal(self, usuario) -> None:
        """Destruye la vista actual y muestra el panel principal para 'usuario'."""
        self._limpiar_contenedor()
        self.vista_actual = MainView(
            self.contenedor,
            self.restaurante_servicio,
            usuario,
            self.mostrar_login,
        )
        self.vista_actual.pack(fill="both", expand=True)

    def _limpiar_contenedor(self) -> None:
        """Elimina la vista montada actualmente, si la hay, antes de montar la siguiente."""
        if self.vista_actual is not None:
            self.vista_actual.destroy()
            self.vista_actual = None


def main() -> None:
    """Crea la única ventana Tkinter de la aplicación y arranca el ciclo principal."""
    root = tk.Tk()
    Aplicacion(root)
    root.mainloop()


if __name__ == "__main__":
    main()
