"""
deque.py — Implementación propia de la estructura de datos Deque (Double-Ended Queue).
No usa collections.deque ni ningún sustituto externo para la lógica principal.
"""


class Deque:
    """
    Deque (Double-Ended Queue) implementado desde cero usando una lista interna.
    Permite agregar y eliminar elementos tanto al frente como al final.
    """

    def __init__(self):
        self._data: list = []

    # ------------------------------------------------------------------ #
    #  Operaciones de inserción                                            #
    # ------------------------------------------------------------------ #

    def add_front(self, item) -> None:
        """Agrega un elemento al frente del deque."""
        self._data.insert(0, item)

    def add_rear(self, item) -> None:
        """Agrega un elemento al final del deque."""
        self._data.append(item)

    # ------------------------------------------------------------------ #
    #  Operaciones de eliminación                                          #
    # ------------------------------------------------------------------ #

    def remove_front(self):
        """
        Elimina y retorna el elemento del frente.
        Lanza IndexError si el deque está vacío.
        """
        if self.is_empty():
            raise IndexError("remove_front() en un Deque vacío")
        return self._data.pop(0)

    def remove_rear(self):
        """
        Elimina y retorna el elemento del final.
        Lanza IndexError si el deque está vacío.
        """
        if self.is_empty():
            raise IndexError("remove_rear() en un Deque vacío")
        return self._data.pop()

    # ------------------------------------------------------------------ #
    #  Operaciones de consulta                                             #
    # ------------------------------------------------------------------ #

    def peek_front(self):
        """Retorna (sin eliminar) el elemento del frente."""
        if self.is_empty():
            raise IndexError("peek_front() en un Deque vacío")
        return self._data[0]

    def peek_rear(self):
        """Retorna (sin eliminar) el elemento del final."""
        if self.is_empty():
            raise IndexError("peek_rear() en un Deque vacío")
        return self._data[-1]

    def is_empty(self) -> bool:
        """Retorna True si el deque no contiene elementos."""
        return len(self._data) == 0

    def size(self) -> int:
        """Retorna el número de elementos en el deque."""
        return len(self._data)

    def clear(self) -> None:
        """Elimina todos los elementos del deque."""
        self._data.clear()

    def to_list(self) -> list:
        """Retorna una copia de los elementos como lista (frente → final)."""
        return list(self._data)

    # ------------------------------------------------------------------ #
    #  Representación                                                       #
    # ------------------------------------------------------------------ #

    def __repr__(self) -> str:
        return f"Deque({self._data})"

    def __len__(self) -> int:
        return self.size()

    def __iter__(self):
        return iter(self._data)
