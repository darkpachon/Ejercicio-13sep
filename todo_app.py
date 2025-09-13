import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Gestión de Tareas")
        self.root.geometry("600x400")
        
        # Conectar a la base de datos
        self.conn = sqlite3.connect('tasks.db')
        self.create_table()
        
        # Interfaz gráfica
        self.create_widgets()
        
        # Cargar tareas
        self.load_tasks()
        
    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pendiente'
            )
        ''')
        self.conn.commit()
    
    def create_widgets(self):
        # Frame para entrada de nueva tarea
        input_frame = ttk.Frame(self.root, padding="10")
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        ttk.Label(input_frame, text="Nueva tarea:").grid(row=0, column=0, sticky=tk.W)
        self.task_entry = ttk.Entry(input_frame, width=40)
        self.task_entry.grid(row=0, column=1, padx=5)
        
        add_button = ttk.Button(input_frame, text="Agregar", command=self.add_task)
        add_button.grid(row=0, column=2, padx=5)
        
        # Frame para la lista de tareas
        list_frame = ttk.Frame(self.root, padding="10")
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Treeview para mostrar las tareas
        columns = ('id', 'title', 'status')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        self.tree.heading('id', text='ID')
        self.tree.heading('title', text='Tarea')
        self.tree.heading('status', text='Estado')
        
        self.tree.column('id', width=50)
        self.tree.column('title', width=300)
        self.tree.column('status', width=100)
        
        self.tree.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=3, sticky=(tk.N, tk.S))
        
        # Botones de acción
        button_frame = ttk.Frame(self.root, padding="10")
        button_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        complete_button = ttk.Button(button_frame, text="Marcar como Completada", command=self.complete_task)
        complete_button.grid(row=0, column=0, padx=5)
        
        delete_button = ttk.Button(button_frame, text="Eliminar Tarea", command=self.delete_task)
        delete_button.grid(row=0, column=1, padx=5)
        
        refresh_button = ttk.Button(button_frame, text="Actualizar Lista", command=self.load_tasks)
        refresh_button.grid(row=0, column=2, padx=5)
        
        # Configurar expansión
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
    
    def add_task(self):
        title = self.task_entry.get().strip()
        if not title:
            messagebox.showwarning("Advertencia", "Por favor, ingresa el título de la tarea.")
            return
        
        try:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO tasks (title, status) VALUES (?, 'pendiente')", (title,))
            self.conn.commit()
            self.task_entry.delete(0, tk.END)
            self.load_tasks()
            messagebox.showinfo("Éxito", "Tarea agregada correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo agregar la tarea: {str(e)}")
    
    def load_tasks(self):
        # Limpiar treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, title, status FROM tasks ORDER BY id")
            for row in cursor.fetchall():
                self.tree.insert('', tk.END, values=row)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las tareas: {str(e)}")
    
    def complete_task(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Por favor, selecciona una tarea.")
            return
        
        item_id = self.tree.item(selected_item[0])['values'][0]
        
        try:
            cursor = self.conn.cursor()
            cursor.execute("UPDATE tasks SET status = 'completada' WHERE id = ?", (item_id,))
            self.conn.commit()
            self.load_tasks()
            messagebox.showinfo("Éxito", "Tarea marcada como completada.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar la tarea: {str(e)}")
    
    def delete_task(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Por favor, selecciona una tarea.")
            return
        
        if messagebox.askyesno("Confirmar", "¿Estás seguro de que quieres eliminar esta tarea?"):
            item_id = self.tree.item(selected_item[0])['values'][0]
            
            try:
                cursor = self.conn.cursor()
                cursor.execute("DELETE FROM tasks WHERE id = ?", (item_id,))
                self.conn.commit()
                self.load_tasks()
                messagebox.showinfo("Éxito", "Tarea eliminada correctamente.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar la tarea: {str(e)}")
    
    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()