"""
editor_history.py — Lógica principal del sistema de edición con undo/redo.
Toda la lógica está encapsulada aquí; la UI solo consume esta clase.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from deque import Deque


@dataclass
class Action:
    """Representa una acción registrada en el sistema."""
    description: str
    content: str                        # estado del documento tras esta acción
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%H:%M:%S"))

    def __repr__(self) -> str:
        return f"[{self.timestamp}] {self.description}"


class EditorHistory:
    """
    Sistema de historial de edición con soporte de undo/redo.

    Diseño:
    - `_undo_stack` (Deque): pila de acciones realizadas.
      El tope es el final (rear) del deque → add_rear / remove_rear.
    - `_redo_stack` (Deque): pila de acciones deshechas, disponibles para redo.
      Mismo convenio: tope = rear.
    - `_initial_content`: texto vacío que representa el estado inicial ("documento en blanco").

    Invariante: al hacer una nueva acción se limpia el redo_stack, porque la
    rama de historia anterior queda invalidada.
    """

    _INITIAL_DESCRIPTION = "Estado inicial"

    def __init__(self, initial_content: str = ""):
        self._initial_content: str = initial_content
        self._undo_stack: Deque = Deque()   # historial de acciones hechas
        self._redo_stack: Deque = Deque()   # acciones disponibles para redo

    # ------------------------------------------------------------------ #
    #  Estado actual                                                        #
    # ------------------------------------------------------------------ #

    @property
    def current_content(self) -> str:
        """Retorna el contenido actual del documento."""
        if self._undo_stack.is_empty():
            return self._initial_content
        return self._undo_stack.peek_rear().content

    @property
    def current_action(self) -> Optional[Action]:
        """Retorna la acción más reciente, o None si no hay ninguna."""
        if self._undo_stack.is_empty():
            return None
        return self._undo_stack.peek_rear()

    # ------------------------------------------------------------------ #
    #  Operaciones principales                                              #
    # ------------------------------------------------------------------ #

    def add_action(self, description: str, content: str) -> Action:
        """
        Registra una nueva acción.
        - Valida que la descripción y el contenido no estén vacíos.
        - Limpia el redo_stack (nueva rama de historial).
        Retorna la Action creada.
        """
        description = description.strip()
        if not description:
            raise ValueError("La descripción de la acción no puede estar vacía.")
        if content is None:
            raise ValueError("El contenido no puede ser None.")

        action = Action(description=description, content=content)
        self._undo_stack.add_rear(action)
        self._redo_stack.clear()          # nueva acción invalida el redo
        return action

    def undo(self) -> Optional[Action]:
        """
        Deshace la última acción.
        - Mueve la acción del tope de undo_stack → redo_stack.
        - Retorna la acción deshecha, o None si no hay nada que deshacer.
        """
        if self._undo_stack.is_empty():
            return None
        action = self._undo_stack.remove_rear()
        self._redo_stack.add_rear(action)
        return action

    def redo(self) -> Optional[Action]:
        """
        Rehace la última acción deshecha.
        - Mueve la acción del tope de redo_stack → undo_stack.
        - Retorna la acción rehecha, o None si no hay nada que rehacer.
        """
        if self._redo_stack.is_empty():
            return None
        action = self._redo_stack.remove_rear()
        self._undo_stack.add_rear(action)
        return action

    # ------------------------------------------------------------------ #
    #  Consultas de historial                                               #
    # ------------------------------------------------------------------ #

    def can_undo(self) -> bool:
        return not self._undo_stack.is_empty()

    def can_redo(self) -> bool:
        return not self._redo_stack.is_empty()

    def get_undo_history(self) -> list[Action]:
        """Lista de acciones hechas, del más antiguo al más reciente."""
        return self._undo_stack.to_list()

    def get_redo_history(self) -> list[Action]:
        """Lista de acciones deshechas disponibles para redo, del más antiguo al más reciente."""
        return self._redo_stack.to_list()

    def undo_size(self) -> int:
        return self._undo_stack.size()

    def redo_size(self) -> int:
        return self._redo_stack.size()

    def reset(self) -> None:
        """Reinicia completamente el sistema al estado inicial."""
        self._undo_stack.clear()
        self._redo_stack.clear()
