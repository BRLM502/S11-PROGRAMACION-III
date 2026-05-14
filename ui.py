"""
ui.py — Interfaz gráfica del sistema de edición con undo/redo.
Usa Tkinter (incluido en la stdlib de Python).
La UI solo consume EditorHistory; no contiene lógica de negocio.
"""

import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont

from editor_history import EditorHistory


# ═══════════════════════════════════════════════════════════════════════════ #
#  Paleta y constantes de estilo                                              #
# ═══════════════════════════════════════════════════════════════════════════ #

COLORS = {
    "bg":           "#0f0f13",
    "surface":      "#1a1a24",
    "surface2":     "#22222f",
    "border":       "#2e2e42",
    "accent":       "#7c6af7",
    "accent_dim":   "#4e44a8",
    "undo_color":   "#f7916a",
    "redo_color":   "#6af7c2",
    "text":         "#e8e6ff",
    "text_dim":     "#7a7899",
    "text_muted":   "#4a4866",
    "tag_undo":     "#f7916a",
    "tag_redo":     "#6af7c2",
    "entry_bg":     "#13131c",
    "scrollbar":    "#2e2e42",
    "ok":           "#6af7aa",
    "warn":         "#f7c46a",
    "err":          "#f76a6a",
}

PAD = 12
CORNER = 6


# ═══════════════════════════════════════════════════════════════════════════ #
#  Helpers de UI                                                              #
# ═══════════════════════════════════════════════════════════════════════════ #

def _styled_button(parent, text, command, color, width=14, **kw):
    btn = tk.Button(
        parent,
        text=text,
        command=command,
        bg=color,
        fg=COLORS["bg"],
        activebackground=color,
        activeforeground=COLORS["bg"],
        relief="flat",
        bd=0,
        cursor="hand2",
        font=("Courier New", 10, "bold"),
        padx=10,
        pady=6,
        width=width,
        **kw,
    )
    # Hover effect
    btn.bind("<Enter>", lambda e: btn.config(bg=_lighten(color)))
    btn.bind("<Leave>", lambda e: btn.config(bg=color))
    return btn


def _lighten(hex_color: str) -> str:
    """Aclara un color hex en un 15 %."""
    h = hex_color.lstrip("#")
    rgb = tuple(min(255, int(h[i:i+2], 16) + 38) for i in (0, 2, 4))
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def _separator(parent, pady=6):
    tk.Frame(parent, bg=COLORS["border"], height=1).pack(fill="x", pady=pady)


# ═══════════════════════════════════════════════════════════════════════════ #
#  Ventana principal                                                          #
# ═══════════════════════════════════════════════════════════════════════════ #

class EditorApp(tk.Tk):
    """Aplicación principal. Instancia EditorHistory y construye la UI."""

    def __init__(self):
        super().__init__()
        self.history = EditorHistory(initial_content="")

        self.title("✦ Editor — Sistema Undo / Redo")
        self.configure(bg=COLORS["bg"])
        self.resizable(True, True)
        self.minsize(820, 600)

        self._setup_fonts()
        self._build_layout()
        self._refresh_all()

    # ------------------------------------------------------------------ #
    #  Fuentes                                                              #
    # ------------------------------------------------------------------ #

    def _setup_fonts(self):
        self.font_mono = tkfont.Font(family="Courier New", size=11)
        self.font_mono_sm = tkfont.Font(family="Courier New", size=9)
        self.font_title = tkfont.Font(family="Courier New", size=13, weight="bold")
        self.font_label = tkfont.Font(family="Courier New", size=9)
        self.font_status = tkfont.Font(family="Courier New", size=9, slant="italic")

    # ------------------------------------------------------------------ #
    #  Layout principal                                                     #
    # ------------------------------------------------------------------ #

    def _build_layout(self):
        # ── Header ──────────────────────────────────────────────────────
        header = tk.Frame(self, bg=COLORS["surface"], pady=10)
        header.pack(fill="x")
        tk.Label(
            header,
            text="✦  EDITOR  ·  UNDO / REDO  SYSTEM",
            bg=COLORS["surface"],
            fg=COLORS["accent"],
            font=self.font_title,
        ).pack()

        # ── Cuerpo: columna izquierda (editor) + derecha (historial) ────
        body = tk.Frame(self, bg=COLORS["bg"])
        body.pack(fill="both", expand=True, padx=PAD, pady=PAD)

        left = tk.Frame(body, bg=COLORS["bg"])
        left.pack(side="left", fill="both", expand=True)

        right = tk.Frame(body, bg=COLORS["bg"], width=280)
        right.pack(side="right", fill="y", padx=(PAD, 0))
        right.pack_propagate(False)

        self._build_editor_panel(left)
        self._build_history_panel(right)

        # ── Status bar ──────────────────────────────────────────────────
        self._build_status_bar()

    # ------------------------------------------------------------------ #
    #  Panel editor (izquierda)                                            #
    # ------------------------------------------------------------------ #

    def _build_editor_panel(self, parent):
        # Título sección
        self._section_label(parent, "▸  DOCUMENTO ACTUAL")

        # Área de texto editable
        text_frame = tk.Frame(parent, bg=COLORS["border"], pady=1, padx=1)
        text_frame.pack(fill="both", expand=True)

        self.text_area = tk.Text(
            text_frame,
            bg=COLORS["entry_bg"],
            fg=COLORS["text"],
            insertbackground=COLORS["accent"],
            selectbackground=COLORS["accent_dim"],
            relief="flat",
            font=self.font_mono,
            padx=10,
            pady=10,
            wrap="word",
            undo=False,   # usamos nuestro propio sistema
        )
        scrollbar = tk.Scrollbar(text_frame, command=self.text_area.yview,
                                 bg=COLORS["scrollbar"], troughcolor=COLORS["surface"])
        self.text_area.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.text_area.pack(fill="both", expand=True)

        # ── Sección: registrar nueva acción ─────────────────────────────
        _separator(parent)
        self._section_label(parent, "▸  REGISTRAR ACCIÓN")

        entry_frame = tk.Frame(parent, bg=COLORS["bg"])
        entry_frame.pack(fill="x")

        tk.Label(
            entry_frame, text="Descripción:", bg=COLORS["bg"],
            fg=COLORS["text_dim"], font=self.font_label
        ).pack(anchor="w")

        desc_row = tk.Frame(entry_frame, bg=COLORS["bg"])
        desc_row.pack(fill="x", pady=(2, 6))

        self.desc_var = tk.StringVar()
        self.desc_entry = tk.Entry(
            desc_row,
            textvariable=self.desc_var,
            bg=COLORS["entry_bg"],
            fg=COLORS["text"],
            insertbackground=COLORS["accent"],
            relief="flat",
            font=self.font_mono,
        )
        self.desc_entry.pack(side="left", fill="x", expand=True, ipady=5, padx=(0, 6))
        self.desc_entry.bind("<Return>", lambda e: self._do_add_action())

        btn_add = _styled_button(desc_row, "＋ Agregar", self._do_add_action,
                                 COLORS["accent"], width=12)
        btn_add.pack(side="left")

        # ── Botones Undo / Redo / Reset ─────────────────────────────────
        _separator(parent)
        btn_row = tk.Frame(parent, bg=COLORS["bg"])
        btn_row.pack(fill="x")

        self.btn_undo = _styled_button(btn_row, "↩  Undo", self._do_undo,
                                       COLORS["undo_color"], width=12)
        self.btn_undo.pack(side="left", padx=(0, 6))

        self.btn_redo = _styled_button(btn_row, "↪  Redo", self._do_redo,
                                       COLORS["redo_color"], width=12)
        self.btn_redo.pack(side="left", padx=(0, 6))

        _styled_button(btn_row, "⟳  Reset", self._do_reset,
                       COLORS["text_muted"], width=10).pack(side="right")

    # ------------------------------------------------------------------ #
    #  Panel historial (derecha)                                           #
    # ------------------------------------------------------------------ #

    def _build_history_panel(self, parent):
        self._section_label(parent, "▸  HISTORIAL")

        # Undo stack
        tk.Label(parent, text="Pila UNDO  (más reciente abajo)",
                 bg=COLORS["bg"], fg=COLORS["text_muted"],
                 font=self.font_label).pack(anchor="w", pady=(4, 2))

        undo_frame = tk.Frame(parent, bg=COLORS["border"], pady=1, padx=1)
        undo_frame.pack(fill="both", expand=True)

        self.undo_list = tk.Listbox(
            undo_frame,
            bg=COLORS["surface"],
            fg=COLORS["tag_undo"],
            selectbackground=COLORS["accent_dim"],
            relief="flat",
            font=self.font_mono_sm,
            activestyle="none",
            borderwidth=0,
        )
        sb1 = tk.Scrollbar(undo_frame, command=self.undo_list.yview,
                           bg=COLORS["scrollbar"], troughcolor=COLORS["surface"])
        self.undo_list.config(yscrollcommand=sb1.set)
        sb1.pack(side="right", fill="y")
        self.undo_list.pack(fill="both", expand=True)

        # Redo stack
        tk.Label(parent, text="Pila REDO  (más reciente abajo)",
                 bg=COLORS["bg"], fg=COLORS["text_muted"],
                 font=self.font_label).pack(anchor="w", pady=(10, 2))

        redo_frame = tk.Frame(parent, bg=COLORS["border"], pady=1, padx=1)
        redo_frame.pack(fill="both", expand=True)

        self.redo_list = tk.Listbox(
            redo_frame,
            bg=COLORS["surface"],
            fg=COLORS["tag_redo"],
            selectbackground=COLORS["accent_dim"],
            relief="flat",
            font=self.font_mono_sm,
            activestyle="none",
            borderwidth=0,
        )
        sb2 = tk.Scrollbar(redo_frame, command=self.redo_list.yview,
                           bg=COLORS["scrollbar"], troughcolor=COLORS["surface"])
        self.redo_list.config(yscrollcommand=sb2.set)
        sb2.pack(side="right", fill="y")
        self.redo_list.pack(fill="both", expand=True)

    # ------------------------------------------------------------------ #
    #  Status bar                                                           #
    # ------------------------------------------------------------------ #

    def _build_status_bar(self):
        bar = tk.Frame(self, bg=COLORS["surface"], pady=5)
        bar.pack(fill="x", side="bottom")

        self.status_var = tk.StringVar(value="Listo.")
        self.status_color = tk.StringVar(value=COLORS["text_dim"])

        self.status_label = tk.Label(
            bar,
            textvariable=self.status_var,
            bg=COLORS["surface"],
            fg=COLORS["text_dim"],
            font=self.font_status,
            anchor="w",
            padx=PAD,
        )
        self.status_label.pack(side="left")

        self.counter_label = tk.Label(
            bar,
            text="",
            bg=COLORS["surface"],
            fg=COLORS["text_muted"],
            font=self.font_status,
            anchor="e",
            padx=PAD,
        )
        self.counter_label.pack(side="right")

    # ------------------------------------------------------------------ #
    #  Acciones de usuario                                                  #
    # ------------------------------------------------------------------ #

    def _do_add_action(self):
        desc = self.desc_var.get().strip()
        if not desc:
            self._set_status("⚠  La descripción no puede estar vacía.", "warn")
            self.desc_entry.focus()
            return

        content = self.text_area.get("1.0", "end-1c")

        try:
            action = self.history.add_action(desc, content)
            self.desc_var.set("")
            self._set_status(f"✔  Acción registrada: «{action.description}»", "ok")
            self._refresh_all()
        except ValueError as exc:
            self._set_status(f"✖  {exc}", "err")

    def _do_undo(self):
        if not self.history.can_undo():
            self._set_status("⚠  No hay acciones para deshacer.", "warn")
            return
        action = self.history.undo()
        # Actualizar el área de texto con el estado anterior
        self._load_content(self.history.current_content)
        self._set_status(f"↩  Deshecho: «{action.description}»", "ok")
        self._refresh_all()

    def _do_redo(self):
        if not self.history.can_redo():
            self._set_status("⚠  No hay acciones para rehacer.", "warn")
            return
        action = self.history.redo()
        self._load_content(self.history.current_content)
        self._set_status(f"↪  Rehecho: «{action.description}»", "ok")
        self._refresh_all()

    def _do_reset(self):
        if not messagebox.askyesno(
            "Confirmar reset",
            "¿Reiniciar el sistema?\nSe borrará todo el historial.",
            icon="warning",
        ):
            return
        self.history.reset()
        self._load_content("")
        self._set_status("⟳  Sistema reiniciado.", "warn")
        self._refresh_all()

    # ------------------------------------------------------------------ #
    #  Helpers internos                                                     #
    # ------------------------------------------------------------------ #

    def _load_content(self, content: str):
        """Reemplaza el contenido del área de texto."""
        self.text_area.delete("1.0", "end")
        self.text_area.insert("1.0", content)

    def _refresh_all(self):
        """Actualiza listas de historial, botones y contador."""
        # Undo list
        self.undo_list.delete(0, "end")
        for action in self.history.get_undo_history():
            self.undo_list.insert("end", f" {action}")
        if not self.undo_list.size() == 0:
            self.undo_list.see("end")

        # Redo list
        self.redo_list.delete(0, "end")
        for action in self.history.get_redo_history():
            self.redo_list.insert("end", f" {action}")
        if not self.redo_list.size() == 0:
            self.redo_list.see("end")

        # Botones habilitados/deshabilitados
        self.btn_undo.config(
            state="normal" if self.history.can_undo() else "disabled",
            bg=COLORS["undo_color"] if self.history.can_undo() else COLORS["text_muted"],
        )
        self.btn_redo.config(
            state="normal" if self.history.can_redo() else "disabled",
            bg=COLORS["redo_color"] if self.history.can_redo() else COLORS["text_muted"],
        )

        # Contador
        self.counter_label.config(
            text=f"Undo: {self.history.undo_size()}  |  Redo: {self.history.redo_size()}"
        )

    def _set_status(self, msg: str, level: str = "info"):
        color_map = {
            "ok":   COLORS["ok"],
            "warn": COLORS["warn"],
            "err":  COLORS["err"],
            "info": COLORS["text_dim"],
        }
        self.status_var.set(msg)
        self.status_label.config(fg=color_map.get(level, COLORS["text_dim"]))

    def _section_label(self, parent, text: str):
        tk.Label(
            parent,
            text=text,
            bg=COLORS["bg"],
            fg=COLORS["accent"],
            font=self.font_label,
            anchor="w",
        ).pack(fill="x", pady=(0, 4))


# ═══════════════════════════════════════════════════════════════════════════ #
#  Entry point                                                                #
# ═══════════════════════════════════════════════════════════════════════════ #

def main():
    app = EditorApp()
    app.mainloop()


if __name__ == "__main__":
    main()
