# Sistema de Restaurante — restaurante_app (Componentes y contenedores)

**Asignatura:** Programación Orientada a Objetos
**Tema:** Semana 14 — Componentes y contenedores en Tkinter

## 1. Propósito de esta entrega

Esta entrega evoluciona la base gráfica de `restaurante_app` construida en la
Semana 13. Se mantiene íntegra la arquitectura modular (`datos`, `modelos`,
`servicios`, `ui`, `main.py`) y el flujo de acceso ya desarrollado, y se
amplía principalmente la **capa de interfaz**: la ventana principal ahora
organiza su contenido mediante **componentes y contenedores** de Tkinter/ttk
(`ttk.Notebook`, `ttk.LabelFrame`, `ttk.Frame`, `ttk.Entry`, `ttk.Combobox`,
`ttk.Treeview`, `ttk.Scrollbar`, `ttk.Button`) y permite **gestionar
productos por completo** (registrar, consultar/cargar, actualizar y
eliminar) desde la interfaz gráfica, con persistencia real en
`productos.json`.

El propósito central de la semana es aplicar correctamente componentes y
contenedores; la gestión de productos se usa como contexto práctico para
demostrar esa integración, sin incorporar manejo avanzado de eventos
(`bind()`, doble clic, teclado o mouse): toda acción se dispara mediante
botones con `command=`.

## 2. Estructura del proyecto

```
restaurante_app/
├── datos/
│   ├── productos.json          # Información de productos (código, nombre, categoría, precio, stock)
│   └── usuarios.json           # Información de usuarios (identificación, nombre, correo, contraseña)
├── modelos/
│   ├── __init__.py             # Expone Producto y Usuario
│   ├── producto.py             # Clase Producto + to_dict()/from_dict()
│   └── usuario.py              # Clase Usuario + to_dict()/from_dict()
├── servicios/
│   ├── __init__.py             # Expone ArchivoServicio y RestauranteServicio
│   ├── archivo_servicio.py     # Lectura Y escritura de los archivos JSON locales
│   └── restaurante_servicio.py # Conversión a objetos, acceso, listados, conteos y CRUD de productos
├── ui/
│   ├── __init__.py             # Paquete de vistas gráficas
│   ├── login_view.py           # Pantalla de acceso simulada (sin cambios funcionales)
│   └── main_view.py            # Panel principal: Notebook con Productos, Usuarios y Ventas
├── main.py                     # Punto de entrada: crea la ventana y controla las vistas
└── README.md
```

La carpeta `datos/` solo almacena los archivos JSON; no representa una capa
adicional de la arquitectura. La estructura se conservó igual a la de la
Semana 13: no se crearon módulos nuevos, solo se ampliaron las
responsabilidades de `archivo_servicio.py`, `restaurante_servicio.py` y
`main_view.py`.

## 3. Componentes y contenedores utilizados en la interfaz

`MainView` (`ui/main_view.py`) organiza toda la pantalla principal con los
siguientes contenedores y componentes de Tkinter/ttk:

- **`tk.Frame`** (encabezado): agrupa el saludo al usuario y el botón
  "Cerrar sesión".
- **`ttk.Notebook`** (contenedor de pestañas): separa la aplicación en tres
  secciones — **Productos**, **Usuarios** y **Ventas (pendiente)** — sin
  necesidad de botones manuales para alternar entre ellas.
- **`ttk.LabelFrame` "Datos del producto"**: agrupa visualmente el
  formulario de productos (Código, Nombre, Categoría, Precio, Stock)
  distribuido con `grid()`.
- **`ttk.Entry`**: captura Código, Nombre, Precio y Stock.
- **`ttk.Combobox`**: captura/selecciona la Categoría, sugiriendo las
  categorías ya existentes entre los productos cargados.
- **`ttk.Frame`** (barra de acciones): agrupa los botones **Registrar**,
  **Consultar / Cargar**, **Actualizar**, **Eliminar** y **Limpiar
  campos**, todos activados mediante `command=`.
- **`tk.Label`** de retroalimentación: muestra en verde el resultado
  exitoso o en rojo el motivo del error de la última operación.
- **`ttk.LabelFrame` "Productos registrados"** y **"Usuarios registrados"**:
  agrupan cada tabla junto con su total de registros.
- **`ttk.Treeview` + `ttk.Scrollbar`**: presentan los productos y los
  usuarios en forma de tabla, con barra de desplazamiento vertical.

No se utilizó `bind()`, doble clic ni eventos de teclado/mouse: toda
interacción proviene de botones (`command=`) o de los propios controles de
`ttk.Notebook`/`ttk.Combobox`.

## 4. Responsabilidades de cada capa

- **Producto** y **Usuario** (`modelos/`): representan las entidades del
  restaurante. Validan sus propios datos mediante `@property`/`@setter` y
  saben convertirse a/desde un diccionario (`to_dict()`/`from_dict()`). No
  saben nada de archivos ni de la interfaz gráfica. Sin cambios respecto a
  la Semana 13.
- **ArchivoServicio** (`servicios/archivo_servicio.py`): responsable
  ÚNICAMENTE de leer y (desde esta semana) **escribir**
  `datos/productos.json` y `datos/usuarios.json`, controlando cada
  excepción de acceso (archivo inexistente, JSON inválido, permisos) sin
  detener el programa. Se agregó `guardar_productos()` para persistir los
  cambios que se hagan sobre productos desde la interfaz. No conoce las
  clases `Producto` ni `Usuario`.
- **RestauranteServicio** (`servicios/restaurante_servicio.py`): recibe los
  registros que entrega `ArchivoServicio`, los convierte en objetos
  `Producto`/`Usuario`, y concentra **todas** las reglas de negocio,
  incluidas las nuevas de esta semana:
  - `buscar_producto(codigo)`
  - `registrar_producto(codigo, nombre, categoria, precio, stock)`
  - `actualizar_producto(codigo, nombre, categoria, precio, stock)`
  - `eliminar_producto(codigo)`
  - `listar_categorias()`

  Cada operación valida sus datos (incluida la conversión numérica de
  precio/stock) y lanza `ValueError` con un mensaje claro cuando algo no es
  válido; después de registrar, actualizar o eliminar, guarda de inmediato
  el cambio en `productos.json` mediante `ArchivoServicio`. Ninguna vista
  accede a los archivos JSON directamente ni valida datos por su cuenta.
- **LoginView** (`ui/login_view.py`): pantalla de acceso simulada,
  **sin cambios** respecto a la Semana 13, tal como pedía la actividad.
- **MainView** (`ui/main_view.py`): panel principal mostrado tras un acceso
  correcto. Coordina la interacción del usuario (recoge el formulario,
  llama al servicio correspondiente y actualiza la tabla y el mensaje de
  resultado), pero **no** valida datos ni contiene reglas del restaurante:
  esa lógica permanece en `RestauranteServicio`.
- **main.py**: crea la **única ventana principal** de Tkinter, prepara
  `ArchivoServicio` y `RestauranteServicio`, se los entrega a las vistas, y
  controla el cambio entre `LoginView` y `MainView` dentro de esa misma
  ventana y de un único `mainloop()`. Sin cambios de responsabilidad.

## 5. Operaciones implementadas sobre productos

| Acción                 | Botón                | Qué hace |
|-------------------------|-----------------------|----------|
| Registrar                | **Registrar**         | Crea un producto nuevo con los datos del formulario, valida que el código no esté repetido y guarda en `productos.json`. |
| Consultar / cargar       | **Consultar / Cargar**| Busca el producto por código y, si existe, llena el resto del formulario con sus datos actuales para poder editarlo o eliminarlo. |
| Actualizar                | **Actualizar**        | Busca el producto por código y reemplaza nombre, categoría, precio y stock con lo que haya en el formulario; guarda el cambio. |
| Eliminar                  | **Eliminar**          | Pide confirmación y, de aceptarse, elimina el producto por código y guarda el cambio. |
| Limpiar campos            | **Limpiar campos**    | Vacía el formulario sin afectar los datos guardados. |

Después de cada operación, la tabla de "Productos registrados" y el total
mostrado se actualizan automáticamente, y el mensaje de retroalimentación
indica con claridad si la operación tuvo éxito (verde) o falló (rojo),
junto con el motivo.

## 6. Persistencia utilizada

La persistencia se mantiene en archivos JSON dentro de `datos/`, tal como
en la Semana 13:

- `productos.json`: ahora se lee **y se escribe**. Cada registro, actualización
  o eliminación de un producto desde la interfaz se refleja de inmediato en
  este archivo a través de `RestauranteServicio._persistir_productos()` y
  `ArchivoServicio.guardar_productos()`.
- `usuarios.json`: se sigue leyendo únicamente para la consulta de usuarios
  y la validación de acceso; esta semana no se agregó gestión (alta, edición
  o baja) de usuarios desde la interfaz.

## 7. Flujo de la aplicación

```
Inicio de la aplicación
        ↓
main.py prepara Tkinter y los servicios
        ↓
LoginView
        ↓
RestauranteServicio valida el acceso
        ↓
MainView (ttk.Notebook)
        ↓
   ┌───────────┬────────────┬────────────────────┐
   Productos     Usuarios     Ventas (pendiente)
   │ Registrar    │ Consulta
   │ Consultar/Cargar
   │ Actualizar
   │ Eliminar
   ↓
RestauranteServicio procesa la operación
   ↓
Persistencia en productos.json
   ↓
Actualización de la tabla y del mensaje en la interfaz
        ↓
Cerrar sesión
        ↓
LoginView
```

El cambio entre `LoginView` y `MainView` se realiza dentro de la misma
ventana: `main.py` destruye la vista actual y monta la siguiente sobre el
mismo contenedor, sin abrir nunca una segunda instancia de `Tk()`.

> **Nota sobre el acceso:** el inicio de sesión sigue siendo una
> **simulación con fines académicos**; no implementa un mecanismo real de
> autenticación segura.

## 8. Cómo ejecutar el programa

```bash
cd restaurante_app
python main.py
```

Al iniciar, la consola muestra cuántos productos y usuarios se recuperaron
desde la carpeta `datos/`, y luego se abre la ventana con la pantalla de
acceso.

### Usuarios de prueba incluidos

| Identificación | Contraseña | Nombre |
|---|---|---|
| U001 | 1234 | Maria Fernanda Lopez |
| U002 | 5678 | Carlos Andres Vega |
| U003 | clave3 | Ana Sofia Torres |

## 9. Qué se implementó y qué queda pendiente

**Implementado en esta etapa:**
- Interfaz principal reorganizada con `ttk.Notebook`, `ttk.LabelFrame` y
  demás componentes/contenedores descritos en la sección 3.
- Gestión completa de productos desde la interfaz: registrar, consultar/
  cargar, actualizar y eliminar, con validaciones y persistencia reales.
- Persistencia de escritura en `productos.json` (`ArchivoServicio.guardar_productos()`).
- Retroalimentación visual clara (verde/rojo) tras cada operación.
- Consulta de usuarios registrados, conservada desde la Semana 13.
- Conservación íntegra de la arquitectura modular y del flujo de acceso.

**Pendiente para próximas etapas:**
- Gestión completa de ventas (identificada en el Notebook como pestaña
  "Ventas (pendiente)").
- Registro, edición o baja de usuarios desde la interfaz.
- Cualquier mecanismo real de autenticación.
