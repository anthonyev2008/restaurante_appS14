"""
Módulo: servicios/restaurante_servicio.py

Contiene la clase RestauranteServicio, capa de SERVICIO encargada de:
    - Recibir los registros crudos que entrega ArchivoServicio (listas
      de diccionarios) y convertirlos en objetos Producto y Usuario.
    - Concentrar las operaciones necesarias sobre esas dos colecciones:
      validar el acceso de un usuario, listar productos, listar
      usuarios y consultar cuántos hay registrados de cada uno.
    - (Semana 14) Concentrar las reglas de negocio sobre productos que
      la interfaz gráfica solicita: registrar, buscar, actualizar y
      eliminar, conservando siempre el archivo productos.json
      sincronizado con lo que hay en memoria mediante ArchivoServicio.

Ninguna vista (LoginView ni MainView) debe leer o escribir archivos
JSON de forma directa, ni recorrer o modificar listas de diccionarios
crudos, ni validar datos por su cuenta: siempre deben pedir la
información ya convertida en objetos, y solicitar cualquier operación
sobre productos, a través de este servicio. Los botones de la interfaz
solo recogen lo escrito en el formulario y llaman a estos métodos.

Nota sobre el acceso: validar_acceso() es una SIMULACIÓN pedagógica de
inicio de sesión (compara identificación y contraseña contra los
usuarios cargados desde usuarios.json). No implementa ningún mecanismo
real de seguridad -sin cifrado, sin tokens, sin control de intentos- y
no debe tratarse como tal.
"""

from modelos.producto import Producto
from modelos.usuario import Usuario


class RestauranteServicio:
    """Servicio que administra los productos y usuarios del restaurante."""

    def __init__(self, archivo_servicio) -> None:
        self.archivo_servicio = archivo_servicio
        self._productos: list[Producto] = []
        self._usuarios: list[Usuario] = []

    def cargar_datos(self) -> None:
        """
        Pide a ArchivoServicio los registros crudos de productos.json y
        usuarios.json, y los convierte en objetos Producto y Usuario
        respectivamente, dejándolos listos para ser consultados desde
        la interfaz gráfica.
        """
        self._productos = self._construir_productos(self.archivo_servicio.leer_productos())
        self._usuarios = self._construir_usuarios(self.archivo_servicio.leer_usuarios())

    # ------------------------------------------------------------------
    # Conversión de diccionarios crudos a objetos del dominio
    # ------------------------------------------------------------------
    def _construir_productos(self, registros: list) -> list:
        """Convierte los registros crudos en objetos Producto, omitiendo los inválidos."""
        productos: list[Producto] = []
        for registro in registros:
            try:
                if not isinstance(registro, dict):
                    raise ValueError("cada registro debe ser un objeto JSON (diccionario).")
                productos.append(Producto.from_dict(registro))
            except KeyError as error:
                print(f"Aviso: producto incompleto (falta la clave {error}); se omite: {registro}")
            except ValueError as error:
                print(f"Aviso: producto inválido ({error}); se omite: {registro}")
        return productos

    def _construir_usuarios(self, registros: list) -> list:
        """Convierte los registros crudos en objetos Usuario, omitiendo los inválidos."""
        usuarios: list[Usuario] = []
        for registro in registros:
            try:
                if not isinstance(registro, dict):
                    raise ValueError("cada registro debe ser un objeto JSON (diccionario).")
                usuarios.append(Usuario.from_dict(registro))
            except KeyError as error:
                print(f"Aviso: usuario incompleto (falta la clave {error}); se omite: {registro}")
            except ValueError as error:
                print(f"Aviso: usuario inválido ({error}); se omite: {registro}")
        return usuarios

    # ------------------------------------------------------------------
    # Consultas para la interfaz gráfica
    # ------------------------------------------------------------------
    def listar_productos(self) -> list:
        """Devuelve la lista completa de productos cargados."""
        return list(self._productos)

    def listar_usuarios(self) -> list:
        """Devuelve la lista completa de usuarios cargados."""
        return list(self._usuarios)

    def contar_productos(self) -> int:
        """Devuelve la cantidad de productos cargados."""
        return len(self._productos)

    def contar_usuarios(self) -> int:
        """Devuelve la cantidad de usuarios cargados."""
        return len(self._usuarios)

    def listar_categorias(self) -> list:
        """
        Devuelve, ordenadas alfabéticamente, las categorías distintas
        que existen entre los productos actualmente cargados. Se usa
        para sugerir valores en el formulario de productos de la
        interfaz, sin que la vista necesite conocer los productos.
        """
        categorias = {producto.categoria for producto in self._productos}
        return sorted(categorias)

    # ------------------------------------------------------------------
    # Gestión de productos (registro, consulta, actualización, baja)
    # ------------------------------------------------------------------
    def buscar_producto(self, codigo: str):
        """
        Devuelve el objeto Producto cuyo código coincide exactamente
        con 'codigo', o None si no existe ninguno. MainView usa este
        método para cargar un producto existente en el formulario
        antes de actualizarlo o eliminarlo.
        """
        return self._buscar_producto_por_codigo(self._normalizar_texto(codigo))

    def registrar_producto(self, codigo, nombre, categoria, precio, stock) -> "Producto":
        """
        Crea un nuevo producto a partir de los datos capturados en el
        formulario de la interfaz, verifica que el código no esté
        repetido, lo agrega a la colección en memoria y guarda de
        inmediato el cambio en productos.json.

        Lanza ValueError si el código ya existe, si el precio o el
        stock no tienen un formato numérico válido, o si algún dato no
        cumple las reglas propias de Producto (validadas por sus
        @setter). En cualquiera de esos casos no se modifica nada.
        """
        codigo_normalizado = self._normalizar_texto(codigo)
        if not codigo_normalizado:
            raise ValueError("El código del producto no puede estar vacío.")
        if self._buscar_producto_por_codigo(codigo_normalizado) is not None:
            raise ValueError(f"Ya existe un producto registrado con el código '{codigo_normalizado}'.")

        precio_numerico = self._convertir_precio(precio)
        stock_numerico = self._convertir_stock(stock)

        nuevo_producto = Producto(codigo_normalizado, nombre, categoria, precio_numerico, stock_numerico)
        self._productos.append(nuevo_producto)
        self._persistir_productos()
        return nuevo_producto

    def actualizar_producto(self, codigo, nombre, categoria, precio, stock) -> "Producto":
        """
        Busca el producto con el código recibido y actualiza su
        nombre, categoría, precio y stock (el código no cambia:
        identifica al producto). Guarda el cambio en productos.json.

        Lanza ValueError si no existe un producto con ese código, si
        el precio o el stock no son numéricos, o si algún dato no
        cumple las reglas de Producto.
        """
        producto = self._buscar_producto_por_codigo(self._normalizar_texto(codigo))
        if producto is None:
            raise ValueError(f"No existe un producto registrado con el código '{codigo}'.")

        precio_numerico = self._convertir_precio(precio)
        stock_numerico = self._convertir_stock(stock)

        # Las propias @setter de Producto validan nombre, categoría,
        # precio y stock antes de aceptarlos.
        producto.nombre = nombre
        producto.categoria = categoria
        producto.precio = precio_numerico
        producto.stock = stock_numerico

        self._persistir_productos()
        return producto

    def eliminar_producto(self, codigo: str) -> None:
        """
        Elimina, de la colección en memoria y de productos.json, el
        producto cuyo código coincide con 'codigo'. Lanza ValueError
        si no existe ningún producto con ese código.
        """
        producto = self._buscar_producto_por_codigo(self._normalizar_texto(codigo))
        if producto is None:
            raise ValueError(f"No existe un producto registrado con el código '{codigo}'.")

        self._productos.remove(producto)
        self._persistir_productos()

    # ------------------------------------------------------------------
    # Auxiliares internos de la gestión de productos
    # ------------------------------------------------------------------
    def _buscar_producto_por_codigo(self, codigo):
        """Recorre la colección en memoria y devuelve el Producto con ese código, o None."""
        for producto in self._productos:
            if producto.codigo == codigo:
                return producto
        return None

    def _persistir_productos(self) -> None:
        """
        Convierte todos los productos en memoria a diccionarios y le
        pide a ArchivoServicio que los escriba en productos.json. Si
        la escritura falla (por ejemplo, por permisos), se informa un
        aviso por consola sin interrumpir la operación ya realizada en
        memoria.
        """
        registros = [producto.to_dict() for producto in self._productos]
        guardado_exitoso = self.archivo_servicio.guardar_productos(registros)
        if not guardado_exitoso:
            print("Aviso: el cambio se aplicó en memoria, pero no pudo guardarse en productos.json.")

    @staticmethod
    def _normalizar_texto(valor) -> str:
        """Recorta espacios de un texto recibido desde la interfaz; tolera None."""
        return valor.strip() if isinstance(valor, str) else valor

    @staticmethod
    def _convertir_precio(valor) -> float:
        """Convierte el texto del formulario a float; lanza ValueError con un mensaje claro si no es numérico."""
        try:
            return float(valor)
        except (TypeError, ValueError):
            raise ValueError("El precio debe ser un número (use punto decimal, por ejemplo 8.50).")

    @staticmethod
    def _convertir_stock(valor) -> int:
        """Convierte el texto del formulario a int; lanza ValueError con un mensaje claro si no es numérico."""
        try:
            return int(valor)
        except (TypeError, ValueError):
            raise ValueError("El stock debe ser un número entero (por ejemplo 10).")

    # ------------------------------------------------------------------
    # Acceso simulado
    # ------------------------------------------------------------------
    def validar_acceso(self, identificacion: str, contrasena: str):
        """
        Busca, entre los usuarios cargados, uno cuya identificación y
        contraseña coincidan exactamente con las recibidas. Devuelve el
        objeto Usuario si el acceso es válido, o None si no hay
        coincidencia. LoginView solo debe llamar a este método: nunca
        debe comparar credenciales por su cuenta.
        """
        for usuario in self._usuarios:
            if usuario.identificacion == identificacion and usuario.contrasena == contrasena:
                return usuario
        return None
