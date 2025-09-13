#!/usr/bin/env python3
"""
To-Do List con SQLite y tkinter
Cumple con: agregar, listar, editar, eliminar, marcar como completada.
"""

import sqlite3
import datetime
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

DB_FILE = "tasks.db"

# ---------------------------
# Base de datos
# ---------------------------
def get_conn():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('pendiente','completada')) DEFAULT 'pendiente',
            created_at TEXT NOT NULL,
            updated_at TEXT
        );
    """)
    conn.commit()
    conn.close()

def add_task(title: str):
    now = datetime.datetime.utcnow().isoformat()
    conn = get_conn()
    conn.execute(
        "INSERT INTO tasks (title, status, created_at) VALUES (?, 'pendiente', ?)",
        (title.strip(), now)
    )
    conn.commit()
    conn.close()

def edit_task(task_id: int, new_title: str):
    now = datetime.datetime.utcnow().isoformat()
    conn = get_conn()
    conn.execute(
        "UPDATE tasks SET title = ?, updated_at = ? WHERE id = ?",
        (new_title.strip(), now, task_id)
    )
    conn.commit()
    conn.close()

def delete_task(task_id: int):
    conn = get_conn()
    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

def mark_completed(task_id: int):
    now = datetime.datetime.utcnow().isoformat()
    conn = get_conn()
    conn.execute(
        "UPDATE tasks SET status = 'completada', updated_at = ? WHERE id = ?",
        (now, task_id)
    )
    conn.commit()
    conn.close()

def get_all_tasks():
    conn = get_conn()
    rows = conn.execute(
        "SELECT id, title, status, created_at, updated_at FROM tasks ORDER BY id"
    ).fetchall()
    conn.close()
    return rows

# ---------------------------
# Interfaz gráfica
# ---------------------------
class TodoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("To-Do List - SQLite")
        self.geometry("700x420")
        self.resizable(False, False)
        self.create_widgets()
        self.refresh_tasks()

    def create_widgets(self):
        # Entrada y botón agregar
        frame_top = ttk.Frame(self, padding=10)
        frame_top.pack(fill=tk.X)
        self.entry_title = ttk.Entry(frame_top)
        self.entry_title.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        self.entry_title.bind("<Return>", lambda e: self.on_add())
        ttk.Button(frame_top, text="Agregar tarea", command=self.on_add).pack(side=tk.LEFT)

        # Tabla de tareas
        columns = ("id", "title", "status", "created_at", "updated_at")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=15)
        for col, text, w in [
            ("id", "ID", 40),
            ("title", "Título", 300),
            ("status", "Estado", 100),
            ("created_at", "Creado", 130),
            ("updated_at", "Actualizado", 130)
        ]:
            self.tree.heading(col, text=text)
            self.tree.column(col, width=w, anchor=tk.CENTER if col in ("id", "status") else tk.W)
        self.tree.pack(padx=10, pady=(5, 0))

        # Scrollbar
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.place(in_=self.tree, relx=1.0, rely=0, relheight=1.0, x=-2)

        # Botones de acción
        frame_bot = ttk.Frame(self, padding=10)
        frame_bot.pack(fill=tk.X, side=tk.BOTTOM)
        ttk.Button(frame_bot, text="Editar", command=self.on_edit).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_bot, text="Eliminar", command=self.on_delete).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_bot, text="Marcar completada", command=self.on_complete).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_bot, text="Refrescar", command=self.refresh_tasks).pack(side=tk.RIGHT)

        self.tree.bind("<Double-1>", lambda e: self.on_edit())

    def _selected_task_id(self):
        sel = self.tree.selection()
        if not sel:
            return None
        return self.tree.item(sel[0])["values"][0]

    def on_add(self):
        title = self.entry_title.get().strip()
        if not title:
            messagebox.showwarning("Atención", "Escribe el título de la tarea.")
            return
        add_task(title)
        self.entry_title.delete(0, tk.END)
        self.refresh_tasks()

    def on_edit(self):
        task_id = self._selected_task_id()
        if not task_id:
            messagebox.showinfo("Editar", "Selecciona una tarea.")
            return
        current_title = next(r["title"] for r in get_all_tasks() if r["id"] == task_id)
        new_title = simpledialog.askstring("Editar tarea", "Nuevo título:", initialvalue=current_title)
        if new_title and new_title.strip():
            edit_task(task_id, new_title)
            self.refresh_tasks()

    def on_delete(self):
        task_id = self._selected_task_id()
        if not task_id:
            messagebox.showinfo("Eliminar", "Selecciona una tarea.")
            return
        if messagebox.askyesno("Confirmar", "¿Eliminar la tarea seleccionada?"):
            delete_task(task_id)
            self.refresh_tasks()

    def on_complete(self):
        task_id = self._selected_task_id()
        if not task_id:
            messagebox.showinfo("Completar", "Selecciona una tarea.")
            return
        mark_completed(task_id)
        self.refresh_tasks()

    def refresh_tasks(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for r in get_all_tasks():
            self.tree.insert("", tk.END, values=(
                r["id"], r["title"], r["status"],
                r["created_at"][:19],
                r["updated_at"][:19] if r["updated_at"] else ""
            ))

# ---------------------------
# Arranque
# ---------------------------
def main():
    init_db()
    app = TodoApp()
    app.mainloop()

if __name__ == "__main__":
    main()
