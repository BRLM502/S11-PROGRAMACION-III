# S11-PROGRAMACION-III
PROGRA
# Sistema de Edición con Undo / Redo

Aplicación Python que simula un editor de texto con historial de acciones completo,
implementado sobre una clase `Deque` propia.

---

## Estructura del proyecto

```
undo_redo_system/
├── deque.py           # Estructura Deque (implementación propia)
├── editor_history.py  # Lógica del sistema (undo, redo, historial)
├── ui.py              # Interfaz gráfica (Tkinter) — solo consume las clases anteriores
├── tests.py           # Suite de pruebas (unittest)
└── README.md
```

---

## Requisitos

- Python 3.12+
- Tkinter (incluido en la instalación estándar de Python)
- No se requieren paquetes externos

---

## Ejecutar la aplicación

```bash
cd undo_redo_system
python ui.py
```

## Ejecutar las pruebas

```bash
python tests.py
# o con pytest:
pytest tests.py -v
```

---

## Decisiones de diseño

### Clase `Deque`
Implementada en `deque.py` usando una `list` interna.  
Toda la lógica de acceso doble está encapsulada; el exterior solo llama a
`add_front`, `add_rear`, `remove_front`, `remove_rear`, `is_empty`, `size`, etc.

### `EditorHistory`
Mantiene **dos pilas** (ambas implementadas como `Deque`):

| Pila | Rol | Tope |
|---|---|---|
| `_undo_stack` | Acciones realizadas | `rear` (último elemento) |
| `_redo_stack` | Acciones deshechas | `rear` (último elemento) |

**Invariante clave**: al registrar una nueva acción se limpia `_redo_stack`,
porque la rama de historia anterior queda inválida.

### Separación de responsabilidades
- `deque.py` — estructura de datos pura, sin lógica de negocio.
- `editor_history.py` — lógica de negocio, sin imports de UI.
- `ui.py` — solo crea widgets y llama métodos de `EditorHistory`.

### Validaciones
- Descripción vacía → `ValueError`.
- `undo` / `redo` sin elementos → retorna `None` sin lanzar excepción.
- Reset con confirmación en la UI para evitar pérdidas accidentales.

---

## Pruebas incluidas

| Clase testeada | Casos cubiertos |
|---|---|
| `Deque` | estado inicial, add/remove en ambos extremos, peek, errores en vacío, size, clear, to_list, tipos mixtos, iteración |
| `EditorHistory` | estado inicial, add_action, undo básico, undo hasta estado inicial, undo en vacío, redo básico, redo en vacío, ciclos undo-redo, limpieza de redo al agregar, reset, historial grande (100 pasos) |
