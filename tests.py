"""
tests.py — Pruebas unitarias del sistema de undo/redo.
Cubre: Deque, EditorHistory (undo, redo, casos límite).
Ejecutar: python tests.py  o  python -m pytest tests.py -v
"""

import sys
import os
import unittest

# Permite importar desde el mismo directorio
sys.path.insert(0, os.path.dirname(__file__))

from deque import Deque
from editor_history import EditorHistory, Action


# ═══════════════════════════════════════════════════════════════════════════ #
#  Tests de Deque                                                             #
# ═══════════════════════════════════════════════════════════════════════════ #

class TestDeque(unittest.TestCase):

    def setUp(self):
        self.d = Deque()

    # ── Estado inicial ───────────────────────────────────────────────────

    def test_empty_on_creation(self):
        self.assertTrue(self.d.is_empty())
        self.assertEqual(self.d.size(), 0)

    def test_len_builtin(self):
        self.assertEqual(len(self.d), 0)
        self.d.add_rear(1)
        self.assertEqual(len(self.d), 1)

    # ── add_rear / remove_rear ────────────────────────────────────────────

    def test_add_rear_and_remove_rear(self):
        self.d.add_rear("a")
        self.d.add_rear("b")
        self.d.add_rear("c")
        self.assertEqual(self.d.remove_rear(), "c")
        self.assertEqual(self.d.remove_rear(), "b")
        self.assertEqual(self.d.remove_rear(), "a")
        self.assertTrue(self.d.is_empty())

    # ── add_front / remove_front ──────────────────────────────────────────

    def test_add_front_and_remove_front(self):
        self.d.add_front(1)
        self.d.add_front(2)
        self.d.add_front(3)
        # frente = 3, final = 1
        self.assertEqual(self.d.remove_front(), 3)
        self.assertEqual(self.d.remove_front(), 2)
        self.assertEqual(self.d.remove_front(), 1)
        self.assertTrue(self.d.is_empty())

    def test_add_front_remove_rear(self):
        self.d.add_front("x")
        self.d.add_front("y")
        # orden: y x
        self.assertEqual(self.d.remove_rear(), "x")
        self.assertEqual(self.d.remove_rear(), "y")

    # ── Peek ─────────────────────────────────────────────────────────────

    def test_peek_front(self):
        self.d.add_rear(10)
        self.d.add_rear(20)
        self.assertEqual(self.d.peek_front(), 10)
        self.assertEqual(self.d.size(), 2)  # no se eliminó

    def test_peek_rear(self):
        self.d.add_rear(10)
        self.d.add_rear(20)
        self.assertEqual(self.d.peek_rear(), 20)
        self.assertEqual(self.d.size(), 2)

    # ── Errores en deque vacío ────────────────────────────────────────────

    def test_remove_front_empty_raises(self):
        with self.assertRaises(IndexError):
            self.d.remove_front()

    def test_remove_rear_empty_raises(self):
        with self.assertRaises(IndexError):
            self.d.remove_rear()

    def test_peek_front_empty_raises(self):
        with self.assertRaises(IndexError):
            self.d.peek_front()

    def test_peek_rear_empty_raises(self):
        with self.assertRaises(IndexError):
            self.d.peek_rear()

    # ── Size y clear ──────────────────────────────────────────────────────

    def test_size_updates_correctly(self):
        for i in range(5):
            self.d.add_rear(i)
        self.assertEqual(self.d.size(), 5)
        self.d.remove_rear()
        self.assertEqual(self.d.size(), 4)

    def test_clear(self):
        self.d.add_rear(1)
        self.d.add_rear(2)
        self.d.clear()
        self.assertTrue(self.d.is_empty())
        self.assertEqual(self.d.size(), 0)

    # ── to_list ───────────────────────────────────────────────────────────

    def test_to_list_order(self):
        self.d.add_rear("a")
        self.d.add_rear("b")
        self.d.add_front("z")
        # orden: z a b
        self.assertEqual(self.d.to_list(), ["z", "a", "b"])

    def test_to_list_is_copy(self):
        self.d.add_rear(1)
        lst = self.d.to_list()
        lst.append(99)
        self.assertEqual(self.d.size(), 1)  # no afectó al deque

    # ── Tipos mixtos ──────────────────────────────────────────────────────

    def test_mixed_types(self):
        self.d.add_rear(42)
        self.d.add_rear("hello")
        self.d.add_rear([1, 2, 3])
        self.assertEqual(self.d.size(), 3)
        self.assertEqual(self.d.remove_front(), 42)

    # ── Iteración ─────────────────────────────────────────────────────────

    def test_iteration(self):
        items = [1, 2, 3]
        for i in items:
            self.d.add_rear(i)
        self.assertEqual(list(self.d), items)


# ═══════════════════════════════════════════════════════════════════════════ #
#  Tests de EditorHistory                                                     #
# ═══════════════════════════════════════════════════════════════════════════ #

class TestEditorHistory(unittest.TestCase):

    def setUp(self):
        self.eh = EditorHistory()

    # ── Estado inicial ────────────────────────────────────────────────────

    def test_initial_state(self):
        self.assertEqual(self.eh.current_content, "")
        self.assertIsNone(self.eh.current_action)
        self.assertFalse(self.eh.can_undo())
        self.assertFalse(self.eh.can_redo())

    def test_initial_content_custom(self):
        eh = EditorHistory(initial_content="hola")
        self.assertEqual(eh.current_content, "hola")

    # ── add_action ────────────────────────────────────────────────────────

    def test_add_action_basic(self):
        action = self.eh.add_action("Escribir hola", "hola")
        self.assertIsInstance(action, Action)
        self.assertEqual(action.description, "Escribir hola")
        self.assertEqual(self.eh.current_content, "hola")
        self.assertTrue(self.eh.can_undo())
        self.assertFalse(self.eh.can_redo())

    def test_add_action_strips_description(self):
        action = self.eh.add_action("  Prueba  ", "abc")
        self.assertEqual(action.description, "Prueba")

    def test_add_action_empty_description_raises(self):
        with self.assertRaises(ValueError):
            self.eh.add_action("", "contenido")

    def test_add_action_whitespace_only_raises(self):
        with self.assertRaises(ValueError):
            self.eh.add_action("   ", "contenido")

    def test_add_action_none_content_raises(self):
        with self.assertRaises(ValueError):
            self.eh.add_action("Acción", None)

    def test_add_action_clears_redo(self):
        self.eh.add_action("A1", "texto1")
        self.eh.add_action("A2", "texto2")
        self.eh.undo()
        self.assertTrue(self.eh.can_redo())
        # Nueva acción debe limpiar redo
        self.eh.add_action("A3", "texto3")
        self.assertFalse(self.eh.can_redo())

    # ── undo ─────────────────────────────────────────────────────────────

    def test_undo_basic(self):
        self.eh.add_action("A1", "v1")
        self.eh.add_action("A2", "v2")
        result = self.eh.undo()
        self.assertEqual(result.description, "A2")
        self.assertEqual(self.eh.current_content, "v1")
        self.assertTrue(self.eh.can_redo())

    def test_undo_all_returns_initial(self):
        self.eh.add_action("A1", "v1")
        self.eh.undo()
        self.assertEqual(self.eh.current_content, "")

    def test_undo_when_empty_returns_none(self):
        result = self.eh.undo()
        self.assertIsNone(result)

    def test_undo_does_not_raise_when_empty(self):
        # No debe lanzar excepción
        for _ in range(5):
            self.assertIsNone(self.eh.undo())

    def test_undo_multiple(self):
        for i in range(4):
            self.eh.add_action(f"A{i}", f"v{i}")
        for i in range(3, -1, -1):
            action = self.eh.undo()
            self.assertEqual(action.description, f"A{i}")

    # ── redo ─────────────────────────────────────────────────────────────

    def test_redo_basic(self):
        self.eh.add_action("A1", "v1")
        self.eh.undo()
        result = self.eh.redo()
        self.assertEqual(result.description, "A1")
        self.assertEqual(self.eh.current_content, "v1")
        self.assertFalse(self.eh.can_redo())

    def test_redo_when_empty_returns_none(self):
        result = self.eh.redo()
        self.assertIsNone(result)

    def test_redo_does_not_raise_when_empty(self):
        for _ in range(5):
            self.assertIsNone(self.eh.redo())

    def test_redo_multiple(self):
        self.eh.add_action("A1", "v1")
        self.eh.add_action("A2", "v2")
        self.eh.add_action("A3", "v3")
        self.eh.undo()
        self.eh.undo()
        self.eh.undo()
        r1 = self.eh.redo()
        r2 = self.eh.redo()
        r3 = self.eh.redo()
        self.assertEqual(r1.description, "A1")
        self.assertEqual(r2.description, "A2")
        self.assertEqual(r3.description, "A3")
        self.assertFalse(self.eh.can_redo())

    # ── Historial ────────────────────────────────────────────────────────

    def test_get_undo_history(self):
        self.eh.add_action("A1", "v1")
        self.eh.add_action("A2", "v2")
        hist = self.eh.get_undo_history()
        self.assertEqual(len(hist), 2)
        self.assertEqual(hist[0].description, "A1")
        self.assertEqual(hist[1].description, "A2")

    def test_get_redo_history(self):
        self.eh.add_action("A1", "v1")
        self.eh.add_action("A2", "v2")
        self.eh.undo()
        redo_hist = self.eh.get_redo_history()
        self.assertEqual(len(redo_hist), 1)
        self.assertEqual(redo_hist[0].description, "A2")

    # ── Casos límite ─────────────────────────────────────────────────────

    def test_undo_redo_undo_cycle(self):
        self.eh.add_action("A", "va")
        self.eh.undo()
        self.eh.redo()
        action = self.eh.undo()
        self.assertEqual(action.description, "A")
        self.assertEqual(self.eh.current_content, "")

    def test_redo_cleared_after_new_action(self):
        self.eh.add_action("A", "va")
        self.eh.undo()
        self.eh.add_action("B", "vb")
        self.assertEqual(self.eh.redo_size(), 0)

    def test_empty_string_content_allowed(self):
        action = self.eh.add_action("Borrar todo", "")
        self.assertEqual(action.content, "")
        self.assertEqual(self.eh.current_content, "")

    def test_sizes(self):
        self.eh.add_action("A1", "v1")
        self.eh.add_action("A2", "v2")
        self.assertEqual(self.eh.undo_size(), 2)
        self.assertEqual(self.eh.redo_size(), 0)
        self.eh.undo()
        self.assertEqual(self.eh.undo_size(), 1)
        self.assertEqual(self.eh.redo_size(), 1)

    def test_reset(self):
        self.eh.add_action("A1", "v1")
        self.eh.add_action("A2", "v2")
        self.eh.undo()
        self.eh.reset()
        self.assertFalse(self.eh.can_undo())
        self.assertFalse(self.eh.can_redo())
        self.assertEqual(self.eh.current_content, "")

    def test_large_history(self):
        n = 100
        for i in range(n):
            self.eh.add_action(f"Acción {i}", f"contenido {i}")
        self.assertEqual(self.eh.undo_size(), n)
        for _ in range(n):
            self.eh.undo()
        self.assertEqual(self.eh.redo_size(), n)
        self.assertEqual(self.eh.current_content, "")


# ═══════════════════════════════════════════════════════════════════════════ #
#  Entry point                                                                #
# ═══════════════════════════════════════════════════════════════════════════ #

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestDeque))
    suite.addTests(loader.loadTestsFromTestCase(TestEditorHistory))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
