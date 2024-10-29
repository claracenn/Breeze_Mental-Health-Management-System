import sqlite3
import tkinter as tk
from tkinter import messagebox, simpledialog, Frame, CENTER
from PIL import Image, ImageTk
import pandas as pd

# Initialize SQLite database connection
# Establish a connection to the SQLite database and create a cursor for executing SQL commands.
conn = sqlite3.connect('breeze_data.db')
cursor = conn.cursor()

# Create tables if they do not exist
# The following commands create necessary tables in the database if they do not already exist.
cursor.execute('''CREATE TABLE IF NOT EXISTS patients (id TEXT PRIMARY KEY, name TEXT, email TEXT, disabled INTEGER)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS mhwp (id TEXT PRIMARY KEY, name TEXT, email TEXT, disabled INTEGER)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS allocations (patient_id TEXT, mhwp_id TEXT, PRIMARY KEY (patient_id, mhwp_id))''')
conn.commit()  # Commit changes to the database.

# Define a generic User class
class User:
    def __init__(self, user_id, name, email, disabled=False):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.disabled = disabled

# Define Patient and MHWP classes that inherit from User
class Patient(User):
    def __init__(self, user_id, name, email, disabled=False):
        super().__init__(user_id, name, email, disabled)

class MHWP(User):
    def __init__(self, user_id, name, email, disabled=False):
        super().__init__(user_id, name, email, disabled)

# Define Admin class that handles various admin operations
class Admin:
    @staticmethod
    def allocate_patient_to_mhwp(root):
        # Function to allocate a patient to an MHWP
        patient_id = simpledialog.askstring("Input", "Enter Patient ID to allocate:", parent=root)
        mhwp_id = simpledialog.askstring("Input", "Enter MHWP ID to assign:", parent=root)

        cursor.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
        patient = cursor.fetchone()
        cursor.execute("SELECT * FROM mhwp WHERE id = ?", (mhwp_id,))
        mhwp = cursor.fetchone()

        if patient and mhwp:
            cursor.execute("INSERT OR REPLACE INTO allocations (patient_id, mhwp_id) VALUES (?, ?)", (patient_id, mhwp_id))
            conn.commit()  # Commit the changes to make them persistent.
            messagebox.showinfo("Success", f"Patient {patient_id} assigned to MHWP {mhwp_id}.")
        else:
            messagebox.showerror("Error", "Invalid Patient ID or MHWP ID.")

    @staticmethod
    def edit_user_info(root):
        # Function to edit user information
        user_type = simpledialog.askstring("Input", "Edit (1) Patient or (2) MHWP info? Enter 1 or 2:", parent=root)
        user_id = simpledialog.askstring("Input", "Enter User ID:", parent=root)

        if user_type == '1':
            cursor.execute("SELECT * FROM patients WHERE id = ?", (user_id,))
            user = cursor.fetchone()
        elif user_type == '2':
            cursor.execute("SELECT * FROM mhwp WHERE id = ?", (user_id,))
            user = cursor.fetchone()
        else:
            messagebox.showerror("Error", "Invalid User ID.")
            return

        if user:
            new_name = simpledialog.askstring("Input", f"Enter new name (Current: {user[1]}):", parent=root)
            new_email = simpledialog.askstring("Input", f"Enter new email (Current: {user[2]}):", parent=root)
            new_name = new_name if new_name else user[1]  # Use existing name if no new input is given.
            new_email = new_email if new_email else user[2]  # Use existing email if no new input is given.

            if user_type == '1':
                cursor.execute("UPDATE patients SET name = ?, email = ? WHERE id = ?", (new_name, new_email, user_id))
            elif user_type == '2':
                cursor.execute("UPDATE mhwp SET name = ?, email = ? WHERE id = ?", (new_name, new_email, user_id))
            conn.commit()  # Commit changes to the database.
            messagebox.showinfo("Success", "User info updated successfully.")
        else:
            messagebox.showerror("Error", "User not found.")

    @staticmethod
    def delete_user_record(root):
        # Function to delete a user record
        user_type = simpledialog.askstring("Input", "Delete (1) Patient or (2) MHWP? Enter 1 or 2:", parent=root)
        user_id = simpledialog.askstring("Input", "Enter User ID to delete:", parent=root)

        if user_type == '1':
            cursor.execute("DELETE FROM patients WHERE id = ?", (user_id,))
            messagebox.showinfo("Success", f"Patient {user_id} deleted.")
        elif user_type == '2':
            cursor.execute("DELETE FROM mhwp WHERE id = ?", (user_id,))
            messagebox.showinfo("Success", f"MHWP {user_id} deleted.")
        else:
            messagebox.showerror("Error", "Invalid User ID.")
        conn.commit()  # Commit the changes to remove the user from the database.

    @staticmethod
    def disable_user_record(root):
        # Function to disable a user record
        user_id = simpledialog.askstring("Input", "Enter User ID to disable:", parent=root)

        cursor.execute("SELECT * FROM patients WHERE id = ?", (user_id,))
        patient = cursor.fetchone()
        cursor.execute("SELECT * FROM mhwp WHERE id = ?", (user_id,))
        mhwp = cursor.fetchone()

        if patient:
            cursor.execute("UPDATE patients SET disabled = 1 WHERE id = ?", (user_id,))
            messagebox.showinfo("Success", f"Patient {user_id} has been disabled.")
        elif mhwp:
            cursor.execute("UPDATE mhwp SET disabled = 1 WHERE id = ?", (user_id,))
            messagebox.showinfo("Success", f"MHWP {user_id} has been disabled.")
        else:
            messagebox.showerror("Error", "Invalid User ID.")
        conn.commit()  # Commit changes to the database.

    @staticmethod
    def display_summary():
        # Function to display a summary of the system data
        summary_window = tk.Toplevel()  # Create a new window for the summary
        summary_window.title("System Summary")  # Set the title of the summary window

        # Load data from the database into DataFrames for easy viewing
        patients_df = pd.read_sql_query("SELECT * FROM patients", conn)
        mhwp_df = pd.read_sql_query("SELECT * FROM mhwp", conn)
        allocations_df = pd.read_sql_query("SELECT * FROM allocations", conn)

        # Display Patient DataFrame in the GUI
        patient_summary_label = tk.Label(summary_window, text="Patients:")
        patient_summary_label.pack()
        patient_text = tk.Text(summary_window, height=10, width=50)
        patient_text.insert(tk.END, patients_df.to_string())  # Insert patient data into the text widget
        patient_text.pack()

        # Display MHWP DataFrame in the GUI
        mhwp_summary_label = tk.Label(summary_window, text="MHWPs:")
        mhwp_summary_label.pack()
        mhwp_text = tk.Text(summary_window, height=10, width=50)
        mhwp_text.insert(tk.END, mhwp_df.to_string())  # Insert MHWP data into the text widget
        mhwp_text.pack()

        # Display Allocations DataFrame in the GUI
        allocation_summary_label = tk.Label(summary_window, text="Allocations:")
        allocation_summary_label.pack()
        allocation_text = tk.Text(summary_window, height=10, width=50)
        allocation_text.insert(tk.END, allocations_df.to_string())  # Insert allocation data into the text widget
        allocation_text.pack()

# Define a LoginPage class to create a well-structured login page window
class LoginPage:
    def __init__(self, root):
        self.root = root
        self.root.title("Breeze Mental Health Management System (Login Page)")  # Window Title Name
        self.root.iconbitmap('icon.ico')  # Window Icon
        self.img = ImageTk.PhotoImage(Image.open("LoginImage.png"))  # Window Background Image
        self.label = tk.Label(self.root, image=self.img)
        self.label.pack()

        # Window screen (Position & Size)
        self.windowWidth = 1000
        self.windowHeight = 600
        self.xposition = int(self.root.winfo_screenwidth() / 2 - self.windowWidth / 2)
        self.yposition = int(self.root.winfo_screenheight() / 2 - self.windowHeight / 2)
        self.root.geometry('%dx%d+%d+%d' % (self.windowWidth, self.windowHeight, self.xposition, self.yposition))
        self.root.resizable(width=False, height=False)

        # Title of the Login Page
        self.TitleFrame = Frame(self.root)
        self.TitleFrame.place(relx=0.5, rely=0.2, anchor=CENTER)
        self.TitleLabel = tk.Label(self.TitleFrame, font=('Times', 40, 'bold'), text="Breeze Mental Health Management System", bd=2, relief=tk.FLAT, bg='ghostwhite', fg='Black')
        self.TitleLabel.grid(row=0, column=0)

# Main Admin Menu using Tkinter
# This function creates the main menu with buttons to access different admin functionalities

def admin_menu():
    root = tk.Tk()  # Create the main window
    LoginPage(root)  # Instantiate the login page first

    # Creating admin menu buttons after login (simulated here for simplicity)
    root.title("Admin Menu")  # Update the window title for admin menu

    # Create buttons for each admin function and pack them into the window
    tk.Button(root, text="Allocate Patient to MHWP", command=lambda: Admin.allocate_patient_to_mhwp(root)).pack(pady=5)
    tk.Button(root, text="Edit User Information", command=lambda: Admin.edit_user_info(root)).pack(pady=5)
    tk.Button(root, text="Delete User Record", command=lambda: Admin.delete_user_record(root)).pack(pady=5)
    tk.Button(root, text="Disable User Record", command=lambda: Admin.disable_user_record(root)).pack(pady=5)
    tk.Button(root, text="Display Summary", command=Admin.display_summary).pack(pady=5)
    tk.Button(root, text="Logout", command=root.quit).pack(pady=5)

    root.mainloop()  # Run the Tkinter event loop to keep the window open

# Run the admin menu if the script is executed
if __name__ == "__main__":
    admin_menu()

# Close the SQLite connection when the script ends
conn.close()  # Close the database connection to free resources.
