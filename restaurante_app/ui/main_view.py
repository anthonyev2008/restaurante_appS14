"""
Módulo: ui/main_view.py

Contiene la clase MainView, un tk.Frame que presenta el panel
principal del restaurante después de un acceso correcto. Desde la
Semana 14, MainView organiza su contenido mediante un ttk.Notebook
(contenedor de pestañas) con tres secciones:

    - "Productos": un formulario (ttk.LabelFrame) para registrar,
      consultar/cargar, actualizar y eliminar productos, junto con una
      tabla (ttk.Treeview) que refleja siempre el estado actual.
    - "Usuarios": una tabla de solo consulta con los usuarios
      registrados.
    - "Ventas": sección identificada como funcionalidad pendiente.

MainView NO lee ni escribe archivos JSON, no valida datos y no
concentra reglas del restaurante: toda la información que muestra y
toda operación sobre productos se solicitan a RestauranteServicio a
través de sus métodos públicos. Los botones únicamente recogen lo
escrito en el formulario, llaman al servicio y actualizan lo que se
observa en pantalla según el resultado (éxito o ValueError).

Tampoco crea su propia ventana Tkinter ni un nuevo mainloop; vive
dentro de la única ventana principal creada por main.py, y avisa a
quien la creó (mediante al_cerrar_sesion) cuando la persona decide
cerrar sesión.
"""

import tkinter as tk
from tkinter import ttk, messagebox


class MainView(tk.Frame):
    """Panel principal del restaurante: gestión de productos y consulta de usuarios."""

    COLOR_EXITO = "#1a7a34"
    COLOR_ERROR = "#b3261e"

    def __init__(self, contenedor, restaurante_servicio, usuario, al_cerrar_sesion):
        super().__init__(contenedor)
        self.restaurante_servicio = restaurante_servicio
        self.usuario = usuario
        self.al_cerrar_sesion = al_cerrar_sesion

        self._construir_estilos()
        self._construir_encabezado()
        self._construir_pestanas()

        self._actualizar_tabla_productos()
        self._actualizar_tabla_usuarios()

    # ------------------------------------------------------------------
    # Construcción general de la interfaz
    # ------------------------------------------------------------------
    def _construir_estilos(self) -> None:
        """Define un estilo visual coherente para los contenedores ttk usados en el panel."""
        estilo = ttk.Style(self)
        try:
            estilo.theme_use("clam")
        except tk.TclError:
            pass  # Si "clam" no está disponible, se conserva el tema por defecto.
        estilo.configure("TNotebook.Tab", padding=(14, 6), font=("Arial", 10, "bold"))
        estilo.configure("Seccion.TLabelframe.Label", font=("Arial", 10, "bold"))
        estilo.configure("Total.TLabel", foreground="gray30")

    def _construir_encabezado(self) -> None:
        """Contenedor superior con el saludo al usuario y el botón de cerrar sesión."""
        encabezado = tk.Frame(self, bg="#2c3e50")
        encabezado.pack(fill="x")

        tk.Label(
            encabezado,
            text=f"Mi Restaurante — Bienvenido, {self.usuario.nombre}",
            font=("Arial", 13, "bold"),
            bg="#2c3e50",
            fg="white",
            padx=15,
            pady=10,
        ).pack(side="left")

        tk.Button(
            encabezado,
            text="Cerrar sesión",
            command=self._cerrar_sesion,
        ).pack(side="right", padx=15, pady=10)

    def _construir_pestanas(self) -> None:
        """Contenedor de pestañas (ttk.Notebook) que organiza las secciones del sistema."""
        self.pestanas = ttk.Notebook(self)
        self.pestanas.pack(fill="both", expand=True, padx=12, pady=12)

        self.pestana_productos = ttk.Frame(self.pestanas)
        self.pestana_usuarios = ttk.Frame(self.pestanas)
        self.pestana_ventas = ttk.Frame(self.pestanas)

        self.pestanas.add(self.pestana_productos, text="Productos")
        self.pestanas.add(self.pestana_usuarios, text="Usuarios")
        self.pestanas.add(self.pestana_ventas, text="Ventas (pendiente)")

        self._construir_pestana_productos()
        self._construir_pestana_usuarios()
        self._construir_pestana_ventas()

    # ------------------------------------------------------------------
    # Pestaña "Productos": formulario + acciones + tabla
    # ------------------------------------------------------------------
    def _construir_pestana_productos(self) -> None:
        contenedor = self.pestana_productos

        # --- Contenedor del formulario ---
        marco_formulario = ttk.LabelFrame(
            contenedor, text="Datos del producto", style="Seccion.TLabelframe"
        )
        marco_formulario.pack(fill="x", padx=12, pady=(12, 6))

        ttk.Label(marco_formulario, text="Código:").grid(
            row=0, column=0, sticky="e", padx=8, pady=6
        )
        self.entrada_codigo = ttk.Entry(marco_formulario, width=18)
        self.entrada_codigo.grid(row=0, column=1, sticky="w", padx=8, pady=6)

        ttk.Label(marco_formulario, text="Nombre:").grid(
            row=0, column=2, sticky="e", padx=8, pady=6
        )
        self.entrada_nombre = ttk.Entry(marco_formulario, width=28)
        self.entrada_nombre.grid(row=0, column=3, sticky="w", padx=8, pady=6)

        ttk.Label(marco_formulario, text="Categoría:").grid(
            row=1, column=0, sticky="e", padx=8, pady=6
        )
        self.combo_categoria = ttk.Combobox(
            marco_formulario,
            width=16,
            values=self.restaurante_servicio.listar_categorias(),
        )
        self.combo_categoria.grid(row=1, column=1, sticky="w", padx=8, pady=6)

        ttk.Label(marco_formulario, text="Precio:").grid(
            row=1, column=2, sticky="e", padx=8, pady=6
        )
        self.entrada_precio = ttk.Entry(marco_formulario, width=28)
        self.entrada_precio.grid(row=1, column=3, sticky="w", padx=8, pady=6)

        ttk.Label(marco_formulario, text="Stock:").grid(
            row=2, column=0, sticky="e", padx=8, pady=6
        )
        self.entrada_stock = ttk.Entry(marco_formulario, width=18)
        self.entrada_stock.grid(row=2, column=1, sticky="w", padx=8, pady=6)

        # --- Contenedor de acciones (botones con command=) ---
        marco_acciones = ttk.Frame(contenedor)
        marco_acciones.pack(fill="x", padx=12, pady=(0, 4))

        ttk.Button(
            marco_acciones, text="Registrar", command=self._registrar_producto
        ).pack(side="left", padx=(0, 6))
        ttk.Button(
            marco_acciones, text="Consultar / Cargar", command=self._consultar_producto
        ).pack(side="left", padx=6)
        ttk.Button(
            marco_acciones, text="Actualizar", command=self._actualizar_producto
        ).pack(side="left", padx=6)
        ttk.Button(
            marco_acciones, text="Eliminar", command=self._eliminar_producto
        ).pack(side="left", padx=6)
        ttk.Button(
            marco_acciones, text="Limpiar campos", command=self._manejar_limpiar_formulario
        ).pack(side="left", padx=6)

        # --- Mensaje de retroalimentación de la última operación ---
        self.etiqueta_mensaje_producto = tk.Label(
            contenedor, text="", font=("Arial", 9, "bold"), anchor="w"
        )
        self.etiqueta_mensaje_producto.pack(fill="x", padx=14, pady=(0, 6))

        # --- Contenedor de la tabla de productos ---
        marco_lista = ttk.LabelFrame(
            contenedor, text="Productos registrados", style="Seccion.TLabelframe"
        )
        marco_lista.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        marco_tabla = ttk.Frame(marco_lista)
        marco_tabla.pack(fill="both", expand=True, padx=8, pady=8)

        columnas = ("codigo", "nombre", "categoria", "precio", "stock")
        self.tabla_productos = ttk.Treeview(marco_tabla, columns=columnas, show="headings")
        encabezados = {
            "codigo": "Código",
            "nombre": "Nombre",
            "categoria": "Categoría",
            "precio": "Precio",
            "stock": "Stock",
        }
        anchos = {"codigo": 90, "nombre": 220, "categoria": 130, "precio": 90, "stock": 70}
        for columna in columnas:
            self.tabla_productos.heading(columna, text=encabezados[columna])
            self.tabla_productos.column(
                columna, width=anchos[columna], anchor="center" if columna != "nombre" else "w"
            )

        scroll_productos = ttk.Scrollbar(
            marco_tabla, orient="vertical", command=self.tabla_productos.yview
        )
        self.tabla_productos.configure(yscrollcommand=scroll_productos.set)
        self.tabla_productos.pack(side="left", fill="both", expand=True)
        scroll_productos.pack(side="right", fill="y")

        self.etiqueta_total_productos = ttk.Label(marco_lista, text="", style="Total.TLabel")
        self.etiqueta_total_productos.pack(anchor="w", padx=8, pady=(0, 6))

    # ------------------------------------------------------------------
    # Pestaña "Usuarios": solo consulta
    # ------------------------------------------------------------------
    def _construir_pestana_usuarios(self) -> None:
        contenedor = self.pestana_usuarios

        marco_lista = ttk.LabelFrame(
            contenedor, text="Usuarios registrados", style="Seccion.TLabelframe"
        )
        marco_lista.pack(fill="both", expand=True, padx=12, pady=12)

        marco_tabla = ttk.Frame(marco_lista)
        marco_tabla.pack(fill="both", expand=True, padx=8, pady=8)

        columnas = ("identificacion", "nombre", "correo")
        self.tabla_usuarios = ttk.Treeview(marco_tabla, columns=columnas, show="headings")
        encabezados = {"identificacion": "Identificación", "nombre": "Nombre", "correo": "Correo"}
        for columna in columnas:
            self.tabla_usuarios.heading(columna, text=encabezados[columna])
            self.tabla_usuarios.column(
                columna, width=160, anchor="w" if columna != "identificacion" else "center"
            )

        scroll_usuarios = ttk.Scrollbar(
            marco_tabla, orient="vertical", command=self.tabla_usuarios.yview
        )
        self.tabla_usuarios.configure(yscrollcommand=scroll_usuarios.set)
        self.tabla_usuarios.pack(side="left", fill="both", expand=True)
        scroll_usuarios.pack(side="right", fill="y")

        self.etiqueta_total_usuarios = ttk.Label(marco_lista, text="", style="Total.TLabel")
        self.etiqueta_total_usuarios.pack(anchor="w", padx=8, pady=(0, 6))

    # ------------------------------------------------------------------
    # Pestaña "Ventas": pendiente
    # ------------------------------------------------------------------
    def _construir_pestana_ventas(self) -> None:
        contenedor = self.pestana_ventas

        marco_aviso = ttk.Frame(contenedor)
        marco_aviso.pack(expand=True)

        ttk.Label(
            marco_aviso,
            text="La gestión de Ventas todavía no ha sido incorporada a la interfaz gráfica.",
            font=("Arial", 11),
        ).pack(pady=(60, 6))
        ttk.Label(
            marco_aviso,
            text="Quedará disponible en una etapa posterior del proyecto.",
            style="Total.TLabel",
        ).pack()

    # ------------------------------------------------------------------
    # Operaciones sobre productos (delegadas a RestauranteServicio)
    # ------------------------------------------------------------------
    def _registrar_producto(self) -> None:
        """Recoge el formulario y solicita a RestauranteServicio registrar un producto nuevo."""
        codigo = self.entrada_codigo.get()
        nombre = self.entrada_nombre.get()
        categoria = self.combo_categoria.get()
        precio = self.entrada_precio.get()
        stock = self.entrada_stock.get()

        try:
            producto = self.restaurante_servicio.registrar_producto(
                codigo, nombre, categoria, precio, stock
            )
        except ValueError as error:
            self._mostrar_mensaje_producto(str(error), es_error=True)
            return

        self._mostrar_mensaje_producto(
            f"Producto '{producto.codigo}' registrado y guardado correctamente.", es_error=False
        )
        self._limpiar_formulario_producto()
        self._actualizar_tabla_productos()
        self._actualizar_categorias_disponibles()

    def _consultar_producto(self) -> None:
        """Busca el producto por código y, si existe, carga sus datos en el formulario."""
        codigo = self.entrada_codigo.get().strip()
        if not codigo:
            self._mostrar_mensaje_producto("Ingrese un código para consultar.", es_error=True)
            return

        producto = self.restaurante_servicio.buscar_producto(codigo)
        if producto is None:
            self._mostrar_mensaje_producto(
                f"No existe ningún producto con el código '{codigo}'.", es_error=True
            )
            return

        self.entrada_nombre.delete(0, tk.END)
        self.entrada_nombre.insert(0, producto.nombre)
        self.combo_categoria.set(producto.categoria)
        self.entrada_precio.delete(0, tk.END)
        self.entrada_precio.insert(0, str(producto.precio))
        self.entrada_stock.delete(0, tk.END)
        self.entrada_stock.insert(0, str(producto.stock))

        self._mostrar_mensaje_producto(
            f"Producto '{producto.codigo}' cargado. Puede actualizarlo o eliminarlo.", es_error=False
        )

    def _actualizar_producto(self) -> None:
        """Recoge el formulario y solicita a RestauranteServicio actualizar el producto indicado."""
        codigo = self.entrada_codigo.get()
        nombre = self.entrada_nombre.get()
        categoria = self.combo_categoria.get()
        precio = self.entrada_precio.get()
        stock = self.entrada_stock.get()

        try:
            producto = self.restaurante_servicio.actualizar_producto(
                codigo, nombre, categoria, precio, stock
            )
        except ValueError as error:
            self._mostrar_mensaje_producto(str(error), es_error=True)
            return

        self._mostrar_mensaje_producto(
            f"Producto '{producto.codigo}' actualizado y guardado correctamente.", es_error=False
        )
        self._actualizar_tabla_productos()
        self._actualizar_categorias_disponibles()

    def _eliminar_producto(self) -> None:
        """Solicita confirmación y, de aceptarse, pide a RestauranteServicio eliminar el producto."""
        codigo = self.entrada_codigo.get().strip()
        if not codigo:
            self._mostrar_mensaje_producto("Ingrese un código para eliminar.", es_error=True)
            return

        confirmar = messagebox.askyesno(
            "Confirmar eliminación", f"¿Desea eliminar el producto con código '{codigo}'?"
        )
        if not confirmar:
            return

        try:
            self.restaurante_servicio.eliminar_producto(codigo)
        except ValueError as error:
            self._mostrar_mensaje_producto(str(error), es_error=True)
            return

        self._mostrar_mensaje_producto(
            f"Producto '{codigo}' eliminado y guardado correctamente.", es_error=False
        )
        self._limpiar_formulario_producto()
        self._actualizar_tabla_productos()

    def _limpiar_formulario_producto(self) -> None:
        """
        Vacía todos los campos del formulario de productos. No toca el
        mensaje de retroalimentación: se usa también justo después de
        registrar o eliminar un producto, cuando ese mensaje de éxito
        todavía debe permanecer visible para el usuario.
        """
        self.entrada_codigo.delete(0, tk.END)
        self.entrada_nombre.delete(0, tk.END)
        self.combo_categoria.set("")
        self.entrada_precio.delete(0, tk.END)
        self.entrada_stock.delete(0, tk.END)

    def _manejar_limpiar_formulario(self) -> None:
        """Acción del botón 'Limpiar campos': vacía el formulario y también el mensaje anterior."""
        self._limpiar_formulario_producto()
        self.etiqueta_mensaje_producto.config(text="")

    def _mostrar_mensaje_producto(self, texto: str, es_error: bool) -> None:
        """Muestra en pantalla el resultado de la última operación sobre productos."""
        color = self.COLOR_ERROR if es_error else self.COLOR_EXITO
        self.etiqueta_mensaje_producto.config(text=texto, fg=color)

    def _actualizar_categorias_disponibles(self) -> None:
        """Refresca las categorías sugeridas en el combobox con las que existen actualmente."""
        self.combo_categoria["values"] = self.restaurante_servicio.listar_categorias()

    # ------------------------------------------------------------------
    # Actualización de las tablas (reflejan siempre el estado del servicio)
    # ------------------------------------------------------------------
    def _actualizar_tabla_productos(self) -> None:
        """Vuelve a solicitar los productos a RestauranteServicio y repuebla la tabla."""
        for fila in self.tabla_productos.get_children():
            self.tabla_productos.delete(fila)

        productos = self.restaurante_servicio.listar_productos()
        for producto in productos:
            self.tabla_productos.insert(
                "",
                "end",
                values=(
                    producto.codigo,
                    producto.nombre,
                    producto.categoria,
                    f"${producto.precio:.2f}",
                    producto.stock,
                ),
            )

        self.etiqueta_total_productos.config(text=f"Total de productos: {len(productos)}")

    def _actualizar_tabla_usuarios(self) -> None:
        """Solicita los usuarios a RestauranteServicio y los muestra en la tabla."""
        for fila in self.tabla_usuarios.get_children():
            self.tabla_usuarios.delete(fila)

        usuarios = self.restaurante_servicio.listar_usuarios()
        for usuario in usuarios:
            self.tabla_usuarios.insert(
                "",
                "end",
                values=(usuario.identificacion, usuario.nombre, usuario.correo),
            )

        self.etiqueta_total_usuarios.config(text=f"Total de usuarios: {len(usuarios)}")

    # ------------------------------------------------------------------
    # Cierre de sesión
    # ------------------------------------------------------------------
    def _cerrar_sesion(self) -> None:
        """Avisa al contenedor de la aplicación que debe volver a mostrar LoginView."""
        self.al_cerrar_sesion()
