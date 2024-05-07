import tkinter as tk
from tkinter import ttk
import firebase_admin
from firebase_admin import credentials, db

def add_task():
    task = entry_task.get().strip()
    if task:
        listbox_tasks.insert(tk.END, task)
        entry_task.delete(0, tk.END)
        save_tasks()

def delete_task():
    try:
        task_index = listbox_tasks.curselection()[0]
        listbox_tasks.delete(task_index)
        save_tasks()
    except IndexError:
        pass

def save_tasks():
    tasks = listbox_tasks.get(0, tk.END)
    tasks_ref.set('\n'.join(tasks))

def load_tasks():
    tasks_snapshot = tasks_ref.get()
    if tasks_snapshot:
        listbox_tasks.delete(0, tk.END)
        for task in tasks_snapshot.split('\n'):
            listbox_tasks.insert(tk.END, task)

def sync_tasks():
    # Load tasks from the database
    database_tasks = tasks_ref.get().split('\n') if tasks_ref.get() else []
    # Get tasks from the desktop app
    desktop_tasks = listbox_tasks.get(0, tk.END)
    
    # Add tasks from the database not present in the desktop app
    for task in database_tasks:
        if task not in desktop_tasks:
            listbox_tasks.insert(tk.END, task)
    
    # Save all tasks to the database
    save_tasks()

root = tk.Tk()
root.title("Task Scheduler")

# Colors
background_color = "#f5f5f5"
accent_color = "#4CAF50"
text_color = "#333333"

# Set background color
root.configure(bg=background_color)

# Initialize Firebase Admin SDK
cred = credentials.Certificate('serviceAccountKey.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://crossplaformtaskmanager-default-rtdb.firebaseio.com/'
})

# Initialize tasks reference
tasks_ref = db.reference('/tasks/tasks_list')

# Fonts
task_font = ("Arial", 12)

# Main Frame
main_frame = ttk.Frame(root, padding=20)
main_frame.grid(row=0, column=0, sticky="nsew")

# Listbox for tasks
listbox_tasks = tk.Listbox(main_frame, height=10, width=50, bg=background_color, fg=text_color, font=task_font)
listbox_tasks.grid(row=1, column=0, padx=10, pady=10, sticky="nsew", columnspan=2)

# Scrollbar
scrollbar_tasks = tk.Scrollbar(main_frame, orient=tk.VERTICAL, command=listbox_tasks.yview)
scrollbar_tasks.grid(row=1, column=2, sticky="ns")
listbox_tasks.config(yscrollcommand=scrollbar_tasks.set)

# Entry for adding tasks
entry_task = ttk.Entry(main_frame, width=50, font=task_font)
entry_task.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

# Add Task Button
button_add_task = ttk.Button(main_frame, text="Add Task", command=add_task, style='Accent.TButton')
button_add_task.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

# Delete Task Button
button_delete_task = ttk.Button(main_frame, text="Delete Task", command=delete_task, style='Accent.TButton')
button_delete_task.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

# Sync Task Button
button_sync_task = ttk.Button(main_frame, text="Sync Tasks", command=sync_tasks, style='Accent.TButton')
button_sync_task.grid(row=4, column=1, padx=10, pady=5, sticky="ew")

# Load tasks
load_tasks()

root.mainloop()
