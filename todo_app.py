#!/usr/bin/env python3
# Indica que este script debe ejecutarse con Python 3

"""
To-Do List con SQLite y tkinter
Cumple con: agregar, listar, editar, eliminar, marcar como completada.
Con exportación a archivo de texto
"""
# Documentación del programa: describe su propósito y funcionalidades

import sqlite3  # Importa el módulo para trabajar con bases de datos SQLite
import datetime  # Importa el módulo para trabajar con fechas y horas
import tkinter as tk  # Importa el módulo principal de tkinter para la interfaz gráfica
from tkinter import ttk, messagebox, simpledialog, filedialog  
# Importa componentes específicos de tkinter:
# - ttk: widgets temáticos mejorados
# - messagebox: para mostrar mensajes emergentes
# - simpledialog: para diálogos simples de entrada
# - filedialog: para diálogos de selección de archivos

DB_FILE = "tasks.db"  # Define el nombre del archivo de base de datos

# ---------------------------
# Funciones de base de datos
# ---------------------------

def get_conn():
    # Establece y retorna una conexión a la base de datos
    conn = sqlite3.connect(DB_FILE)  # Conecta con el archivo de base de datos
    conn.row_factory = sqlite3.Row  # Configura para que las filas se comporten como diccionarios
    return conn  # Retorna la conexión

def init_db():
    # Inicializa la base de datos creando la tabla si no existe
    conn = get_conn()  # Obtiene una conexión a la base de datos
    cur = conn.cursor()  # Crea un cursor para ejecutar comandos SQL
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('pendiente','completada')) DEFAULT 'pendiente',
            created_at TEXT NOT NULL,
            updated_at TEXT
        );
    """)  # Ejecuta el comando SQL para crear la tabla 'tasks' con sus campos
    conn.commit()  # Guarda los cambios en la base de datos
    conn.close()  # Cierra la conexión

def add_task(title: str):
    # Agrega una nueva tarea a la base de datos
    now = datetime.datetime.utcnow().isoformat()  # Obtiene la fecha/hora actual en formato ISO
    conn = get_conn()  # Obtiene una conexión a la base de datos
    conn.execute(
        "INSERT INTO tasks (title, status, created_at) VALUES (?, 'pendiente', ?)",
        (title.strip(), now)  # Inserta una nueva tarea con estado 'pendiente'
    )
    conn.commit()  # Guarda los cambios
    conn.close()  # Cierra la conexión

def edit_task(task_id: int, new_title: str):
    # Edita el título de una tarea existente
    now = datetime.datetime.utcnow().isoformat()  # Obtiene la fecha/hora actual
    conn = get_conn()  # Obtiene una conexión
    conn.execute(
        "UPDATE tasks SET title = ?, updated_at = ? WHERE id = ?",
        (new_title.strip(), now, task_id)  # Actualiza el título y la fecha de modificación
    )
    conn.commit()  # Guarda los cambios
    conn.close()  # Cierra la conexión

def delete_task(task_id: int):
    # Elimina una tarea de la base de datos
    conn = get_conn()  # Obtiene una conexión
    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))  # Ejecuta el DELETE
    conn.commit()  # Guarda los cambios
    conn.close()  # Cierra la conexión

def mark_completed(task_id: int):
    # Marca una tarea como completada
    now = datetime.datetime.utcnow().isoformat()  # Obtiene la fecha/hora actual
    conn = get_conn()  # Obtiene una conexión
    conn.execute(
        "UPDATE tasks SET status = 'completada', updated_at = ? WHERE id = ?",
        (now, task_id)  # Cambia el estado a 'completada' y actualiza la fecha
    )
    conn.commit()  # Guarda los cambios
    conn.close()  # Cierra la conexión

def get_all_tasks():
    # Obtiene todas las tareas de la base de datos
    conn = get_conn()  # Obtiene una conexión
    rows = conn.execute(
        "SELECT id, title, status, created_at, updated_at FROM tasks ORDER BY id"
    ).fetchall()  # Ejecuta la consulta y obtiene todos los resultados
    conn.close()  # Cierra la conexión
    return rows  # Retorna las filas obtenidas

def export_to_text_file():
    # Exporta todas las tareas a un archivo de texto
    tasks = get_all_tasks()  # Obtiene todas las tareas
    
    # Pide al usuario dónde guardar el archivo
    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",  # Extensión por defecto
        filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")],  # Tipos de archivo
        title="Guardar lista de tareas"  # Título del diálogo
    )
    
    if not file_path:  # Si el usuario canceló la operación
        return  # Sale de la función
    
    try:
        # Abre el archivo para escritura
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("LISTA DE TAREAS\n")  # Escribe el encabezado
            f.write("=" * 50 + "\n")  # Línea separadora
            f.write(f"Fecha de exportación: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")  # Fecha de exportación
            f.write("=" * 50 + "\n\n")  # Línea separadora
            
            # Escribe cada tarea en el archivo
            for task in tasks:
                status_symbol = "✓" if task['status'] == 'completada' else "◯"  # Símbolo según estado
                f.write(f"{status_symbol} [{task['id']}] {task['title']}\n")  # ID y título
                f.write(f"   Creado: {task['created_at'][:19]}\n")  # Fecha de creación
                if task['updated_at']:  # Si hay fecha de actualización
                    f.write(f"   Actualizado: {task['updated_at'][:19]}\n")  # Fecha de actualización
                f.write("-" * 50 + "\n")  # Línea separadora entre tareas
        
        # Muestra mensaje de éxito
        messagebox.showinfo("Éxito", f"Lista de tareas exportada a:\n{file_path}")
    except Exception as e:
        # Muestra mensaje de error si ocurre alguno
        messagebox.showerror("Error", f"No se pudo exportar el archivo:\n{str(e)}")

# ---------------------------
# Clase principal de la aplicación
# ---------------------------
class TodoApp(tk.Tk):
    def __init__(self):
        super().__init__()  # Inicializa la clase padre (tk.Tk)
        self.title("To-Do List - SQLite")  # Establece el título de la ventana
        self.geometry("700x450")  # Establece el tamaño de la ventana
        self.resizable(False, False)  # Impide que la ventana sea redimensionable
        self.create_widgets()  # Crea los widgets de la interfaz
        self.refresh_tasks()  # Carga las tareas en la interfaz

    def create_widgets(self):
        # Marco superior para entrada de datos
        frame_top = ttk.Frame(self, padding=10)  # Crea un marco con relleno
        frame_top.pack(fill=tk.X)  # Empaca el marco para que ocupe todo el ancho
        
        # Campo de entrada para el título de la tarea
        self.entry_title = ttk.Entry(frame_top)  # Crea un campo de entrada
        self.entry_title.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))  # Empaca a la izquierda
        self.entry_title.bind("<Return>", lambda e: self.on_add())  # Asocia la tecla Enter a la función on_add
        
        # Botón para agregar tarea
        ttk.Button(frame_top, text="Agregar tarea", command=self.on_add).pack(side=tk.LEFT)  # Crea y empaca el botón

        # Tabla para mostrar las tareas
        columns = ("id", "title", "status", "created_at", "updated_at")  # Define las columnas
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=15)  # Crea la tabla
        
        # Configura las columnas de la tabla
        for col, text, w in [
            ("id", "ID", 40),
            ("title", "Título", 300),
            ("status", "Estado", 100),
            ("created_at", "Creado", 130),
            ("updated_at", "Actualizado", 130)
        ]:
            self.tree.heading(col, text=text)  # Establece el encabezado de columna
            self.tree.column(col, width=w, anchor=tk.CENTER if col in ("id", "status") else tk.W)  # Configura la columna
        
        self.tree.pack(padx=10, pady=(5, 0), fill=tk.BOTH, expand=True)  # Empaca la tabla

        # Barra de desplazamiento vertical
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)  # Crea la barra
        self.tree.configure(yscrollcommand=vsb.set)  # Configura la tabla para usar la barra
        vsb.place(in_=self.tree, relx=1.0, rely=0, relheight=1.0, x=-2)  # Posiciona la barra

        # Marco inferior para botones de acción
        frame_bot = ttk.Frame(self, padding=10)  # Crea el marco
        frame_bot.pack(fill=tk.X, side=tk.BOTTOM)  # Empaca en la parte inferior
        
        # Botones de acción
        ttk.Button(frame_bot, text="Editar", command=self.on_edit).pack(side=tk.LEFT, padx=5)  # Botón Editar
        ttk.Button(frame_bot, text="Eliminar", command=self.on_delete).pack(side=tk.LEFT, padx=5)  # Botón Eliminar
        ttk.Button(frame_bot, text="Marcar completada", command=self.on_complete).pack(side=tk.LEFT, padx=5)  # Botón Completar
        ttk.Button(frame_bot, text="Exportar a texto", command=export_to_text_file).pack(side=tk.LEFT, padx=5)  # Botón Exportar

        self.tree.bind("<Double-1>", lambda e: self.on_edit())  # Asocia doble clic a la función editar

    def _selected_task_id(self):
        # Obtiene el ID de la tarea seleccionada en la tabla
        sel = self.tree.selection()  # Obtiene la selección actual
        if not sel:  # Si no hay selección
            return None  # Retorna None
        return self.tree.item(sel[0])["values"][0]  # Retorna el ID de la tarea seleccionada

    def on_add(self):
        # Maneja el evento de agregar tarea
        title = self.entry_title.get().strip()  # Obtiene el texto del campo de entrada
        if not title:  # Si está vacío
            messagebox.showwarning("Atención", "Escribe el título de la tarea.")  # Muestra advertencia
            return  # Sale de la función
        add_task(title)  # Agrega la tarea a la base de datos
        self.entry_title.delete(0, tk.END)  # Limpia el campo de entrada
        self.refresh_tasks()  # Actualiza la tabla

    def on_edit(self):
        # Maneja el evento de editar tarea
        task_id = self._selected_task_id()  # Obtiene el ID de la tarea seleccionada
        if not task_id:  # Si no hay tarea seleccionada
            messagebox.showinfo("Editar", "Selecciona una tarea.")  # Muestra mensaje
            return  # Sale de la función
        
        # Obtiene el título actual de la tarea
        current_title = next(r["title"] for r in get_all_tasks() if r["id"] == task_id)
        
        # Muestra un diálogo para editar el título
        new_title = simpledialog.askstring("Editar tarea", "Nuevo título:", initialvalue=current_title)
        
        if new_title and new_title.strip():  # Si se ingresó un nuevo título
            edit_task(task_id, new_title)  # Actualiza la tarea en la base de datos
            self.refresh_tasks()  # Actualiza la tabla

    def on_delete(self):
        # Maneja el evento de eliminar tarea
        task_id = self._selected_task_id()  # Obtiene el ID de la tarea seleccionada
        if not task_id:  # Si no hay tarea seleccionada
            messagebox.showinfo("Eliminar", "Selecciona una tarea.")  # Muestra mensaje
            return  # Sale de la función
        
        # Pide confirmación antes de eliminar
        if messagebox.askyesno("Confirmar", "¿Eliminar la tarea seleccionada?"):
            delete_task(task_id)  # Elimina la tarea de la base de datos
            self.refresh_tasks()  # Actualiza la tabla

    def on_complete(self):
        # Maneja el evento de marcar tarea como completada
        task_id = self._selected_task_id()  # Obtiene el ID de la tarea seleccionada
        if not task_id:  # Si no hay tarea seleccionada
            messagebox.showinfo("Completar", "Selecciona una tarea.")  # Muestra mensaje
            return  # Sale de la función
        
        mark_completed(task_id)  # Marca la tarea como completada
        self.refresh_tasks()  # Actualiza la tabla

    def refresh_tasks(self):
        # Actualiza la tabla con las tareas de la base de datos
        for i in self.tree.get_children():  # Para cada elemento en la tabla
            self.tree.delete(i)  # Lo elimina
        
        for r in get_all_tasks():  # Para cada tarea en la base de datos
            # Inserta la tarea en la tabla
            self.tree.insert("", tk.END, values=(
                r["id"],  # ID
                r["title"],  # Título
                r["status"],  # Estado
                r["created_at"][:19],  # Fecha de creación (solo los primeros 19 caracteres)
                r["updated_at"][:19] if r["updated_at"] else ""  # Fecha de actualización o vacío
            ))

# ---------------------------
# Función principal
# ---------------------------
def main():
    init_db()  # Inicializa la base de datos
    app = TodoApp()  # Crea la aplicación
    app.mainloop()  # Inicia el bucle principal de la interfaz gráfica

if __name__ == "__main__":
    main()  # Ejecuta la función principal si el script se ejecuta directamente