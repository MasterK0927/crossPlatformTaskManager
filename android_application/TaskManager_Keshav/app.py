import toga
from toga.style import Pack
from toga.style.pack import COLUMN
from firebase_admin import credentials, db, initialize_app
import os

class MyTextInput(toga.TextInput):
    def gtk_key_press_event(self, widget, event):
        try:
            super().gtk_key_press_event(widget, event)
        except KeyError:
            pass

class Taskmanager_Keshav(toga.App):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Initialize Firebase Admin SDK
        try:
            cred = credentials.Certificate('serviceAccountKey.json')  # Path to your service account key JSON file
            initialize_app(cred, {
                'databaseURL': 'https://crossplaformtaskmanager-default-rtdb.firebaseio.com/'
            })
        except FileNotFoundError:
            print("Error: serviceAccountKey.json not found. Please ensure it is in the correct location.")
            self.exit()

    def startup(self):
        self.tasks = []

        self.main_box = toga.Box(style=Pack(direction=COLUMN))

        self.list_label = toga.Label('Tasks:', style=Pack(padding=(0, 5)))
        self.task_list = toga.MultilineTextInput(readonly=True, style=Pack(flex=1))
        self.new_task_input = MyTextInput(placeholder='Enter new task', style=Pack(padding=(0, 5)))  # Use the customized TextInput widget
        self.add_button = toga.Button('Add Task', on_press=self.add_task, style=Pack(padding=(0, 5)))
        self.sync_button = toga.Button('Sync', on_press=self.sync_tasks, style=Pack(padding=(0, 5)))
        self.delete_button = toga.Button('Delete Task', on_press=self.delete_task, style=Pack(padding=(0, 5)))

        self.task_list.on_right_click = self.on_task_list_right_click  # Connect right-click event to the method

        self.main_box.add(self.list_label)
        self.main_box.add(self.task_list)
        self.main_box.add(self.new_task_input)
        self.main_box.add(self.add_button)
        self.main_box.add(self.delete_button)
        self.main_box.add(self.sync_button)

        self.load_tasks()

        self.main_window = toga.MainWindow(title=self.name)
        self.main_window.content = self.main_box
        self.main_window.show()

    def add_task(self, widget):
        task = self.new_task_input.value
        if task:
            self.tasks.append(task)
            self.task_list.value = '\n'.join(self.tasks)
            self.new_task_input.value = ''

    def delete_task(self, widget):
        selected_range = self.task_list.selected_range
        if selected_range:
            start, end = selected_range
            task_index = self.task_list.get_line_at_index(start)
            del self.tasks[task_index]
            self.task_list.value = '\n'.join(self.tasks)

            # Update tasks in the database
            tasks_str = '\n'.join(self.tasks)
            db.reference('/tasks/tasks_list').set(tasks_str)

    def edit_task(self, widget, task_index):
        # Implementation for editing a task
        pass

    def sync_tasks(self, widget):
        # Load tasks from the database
        database_tasks = db.reference('/tasks/tasks_list').get().split('\n') if db.reference('/tasks/tasks_list').get() else []
        # Get tasks from the app
        app_tasks = self.tasks

        # Add missing tasks from the database to the app
        added_tasks = []
        for task in database_tasks:
            if task not in app_tasks:
                app_tasks.append(task)
                added_tasks.append(task)

        # Save all tasks to the database
        tasks_str = '\n'.join(app_tasks)
        db.reference('/tasks/tasks_list').set(tasks_str)

        # Reload tasks in the app
        self.load_tasks()

        # Show self-destructing prompt
        if added_tasks:
            self.show_prompt('Sync Complete', f'The following tasks were added:\n\n{", ".join(added_tasks)}')

    def load_tasks(self):
        result = db.reference('/tasks/tasks_list').get()
        if result:
            self.tasks = result.split('\n')
            self.task_list.value = '\n'.join(self.tasks)

    def show_prompt(self, title, message):
        prompt_window = toga.Window(title=title)
        prompt_label = toga.Label(message)
        prompt_button = toga.Button('OK', on_press=self.close_prompt)
        prompt_window.content = toga.Box(children=[prompt_label, prompt_button])
        prompt_window.show()

    def close_prompt(self, widget):
        widget.window.close()

    def create_task_context_menu(self, task_index):
        context_menu = toga.Group('Task Actions')
        context_menu.add(toga.Command('Edit', action=self.edit_task, args=(task_index,)))
        context_menu.add(toga.Command('Delete', action=self.delete_task, args=(task_index,)))
        return context_menu

    def on_task_list_right_click(self, widget, event):
        print("Right-click event detected!")
        if event.button == 3:  # Right click
            task_index = self.task_list.get_line_at_point(event.x, event.y)
            print(f"Task index: {task_index}")
            if task_index is not None:
                context_menu = self.create_task_context_menu(task_index)
                context_menu.show(widget, event.x, event.y)

def main():
    return Taskmanager_Keshav('Task Scheduler', app_id='com.example.taskManager')

if __name__ == '__main__':
    main().main_loop()
