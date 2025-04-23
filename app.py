import customtkinter as ctk
from tkinter import filedialog
import os
import json
import csv
import hashlib
import random

ctk.set_appearance_mode("dark")

# Ensure 'data' folder exists
if not os.path.exists("User_data/"):
    os.makedirs("User_data")

USER_DB = os.path.join("User_data", "users.json")

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

class ToDoApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("To-do List")
        self.geometry("500x450")
        self.resizable(False, False)

        self.username = self.authenticate_user()
        tasks_dir = os.path.join("User_data", "tasks")
        if not os.path.exists(tasks_dir):
            os.makedirs(tasks_dir)

        self.save_file = os.path.join(tasks_dir, f"tasks_{self.username}.csv")
        self.tasks = []

        self.create_widgets()
        self.load_tasks()

    def authenticate_user(self):
        if not os.path.exists(USER_DB):
            with open(USER_DB, "w") as f:
                json.dump({}, f)

        with open(USER_DB, "r") as f:
            users = json.load(f)

        dialog = ctk.CTkInputDialog(text="Enter username:", title="Login / Register")
        username = dialog.get_input()
        if not username or not username.strip():
            self.destroy()
            raise SystemExit("Username required.")
        username = username.strip()

        if username in users:
            dialog = ctk.CTkInputDialog(text="Enter password:", title="Login")
            password = dialog.get_input()

            if users[username] != hash_password(password):
                dialog = ctk.CTkInputDialog(text="Incorrect password. Reset password? (yes/no)", title="Reset?")
                choice = dialog.get_input()

                if choice and choice.lower() == "yes":
                    verification_code = str(random.randint(100000, 999999))
                    print(f"[VERIFICATION CODE]: {verification_code}")

                    dialog = ctk.CTkInputDialog(text="Enter the 6-digit verification code shown in terminal:", title="Verify")
                    entered_code = dialog.get_input()

                    if entered_code != verification_code:
                        self.destroy()
                        raise SystemExit("Verification failed. Access denied.")

                    dialog = ctk.CTkInputDialog(text="Enter new password:", title="Reset Password")
                    new_password = dialog.get_input()

                    dialog = ctk.CTkInputDialog(text="Confirm new password:", title="Reset Password")
                    confirm_password = dialog.get_input()

                    if new_password != confirm_password:
                        self.destroy()
                        raise SystemExit("Passwords do not match.")

                    if not new_password:
                        self.destroy()
                        raise SystemExit("Password is required.")

                    users[username] = hash_password(new_password)
                    with open(USER_DB, "w") as f:
                        json.dump(users, f, indent=2)

                else:
                    self.destroy()
                    raise SystemExit("Incorrect password.")

        else:
            dialog = ctk.CTkInputDialog(text="New user. Create password:", title="Register")
            password = dialog.get_input()
            if not password:
                self.destroy()
                raise SystemExit("Password required.")

            users[username] = hash_password(password)
            with open(USER_DB, "w") as f:
                json.dump(users, f, indent=2)

        return username

    def create_widgets(self):
        self.title_label = ctk.CTkLabel(self, text=f"{self.username}'s Tasks", font=("Aptos", 25, "bold"))
        self.title_label.pack(pady=10)

        self.task_entry = ctk.CTkEntry(self, placeholder_text="Enter a task")
        self.task_entry.pack(pady=10, padx=20, fill="x")

        button_row = ctk.CTkFrame(self)
        button_row.pack(pady=5)

        self.add_button = ctk.CTkButton(button_row, text="Add Task", command=self.add_task)
        self.add_button.pack(side="left", padx=10)

        self.delete_button = ctk.CTkButton(button_row, text="Delete Selected", command=self.delete_selected)
        self.delete_button.pack(side="left", padx=10)

        self.toggle_button = ctk.CTkButton(self, text="Show Unfinished", command=self.toggle_completed)
        self.toggle_button.pack(pady=5)

        self.task_frame = ctk.CTkScrollableFrame(self)
        self.task_frame.pack(pady=10, padx=20, fill="both", expand=True)

        self.show_completed = True

    def add_task(self):
        task_text = self.task_entry.get().strip()
        if task_text:
            self.create_task(task_text, done=False)
            self.task_entry.delete(0, 'end')
            self.save_tasks()
        else:
            ctk.CTkMessageBox.show_error("Error", "Task cannot be empty.")
            return
        self.task_entry.delete(0, 'end')

    def create_task(self, text, done=False):
        checkbox = ctk.CTkCheckBox(self.task_frame, text=text)
        checkbox.pack(anchor="w", padx=10, pady=2)
        checkbox.select() if done else checkbox.deselect()

        self.tasks.append({"checkbox": checkbox, "text": text, "done": done})
        self.refresh_tasks()

    def delete_selected(self):
        for task in self.tasks[:]:
            if task["checkbox"].get() == 1:
                task["checkbox"].destroy()
                self.tasks.remove(task)
        self.save_tasks()

    def toggle_completed(self):
        self.show_completed = not self.show_completed
        self.toggle_button.configure(text="Show All" if not self.show_completed else "Show Unfinished")
        self.refresh_tasks()

    def refresh_tasks(self):
        for task in self.tasks:
            checked = task["checkbox"].get() == 1
            task["done"] = checked
            if not self.show_completed and checked:
                task["checkbox"].pack_forget()
            else:
                task["checkbox"].pack(anchor="w", padx=10, pady=2)
        self.save_tasks()

    def save_tasks(self):
        with open(self.save_file, "w", newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for task in self.tasks:
                writer.writerow([task["text"], task["checkbox"].get()])

    def load_tasks(self):
        if os.path.exists(self.save_file):
            with open(self.save_file, "r", newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) == 2:
                        text, done = row
                        self.create_task(text, done == "1")

if __name__ == "__main__":
    app = ToDoApp()
    app.mainloop()
