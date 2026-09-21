"""
Paquete modelos.

Agrupa las clases que representan las entidades base del restaurante
utilizadas en esta etapa: Producto y Usuario.
"""

from .producto import Producto
from .usuario import Usuario

__all__ = ["Producto", "Usuario"]
