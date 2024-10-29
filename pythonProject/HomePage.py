import tkinter as tk
from tkinter import messagebox, Frame, CENTER
from PIL import Image, ImageTk

class HomePage:
    def __init__(self, root):
        self.root = root
        self.root.title("Breeze Mental Health Management System (Home Page)")  # Window Title Name
        self.root.iconbitmap('icon.ico')  # Window Icon
        self.windowWidth = 800
        self.windowHeight = 500
        self.xposition = int(self.root.winfo_screenwidth() / 2 - self.windowWidth / 2)
        self.yposition = int(self.root.winfo_screenheight() / 2 - self.windowHeight / 2)
        self.root.geometry('%dx%d+%d+%d' % (self.windowWidth, self.windowHeight, self.xposition, self.yposition))
        self.root.resizable(width=False, height=False)

        # Title of the Home Page
        self.TitleFrame = Frame(self.root)
        self.TitleFrame.place(relx=0.5, rely=0.2, anchor=CENTER)
        self.TitleLabel = tk.Label(self.TitleFrame, font=('Times', 30, 'bold'), text="Welcome to Breeze Mental Health System", bd=2, relief=tk.FLAT, bg='ghostwhite', fg='Black')
        self.TitleLabel.grid(row=0, column=0)

        # Buttons for user roles
        tk.Button(self.root, text="Admin Login", command=self.admin_login).place(relx=0.3, rely=0.5, anchor=CENTER)
        tk.Button(self.root, text="MHWP Login", command=self.mhwp_login).place(relx=0.5, rely=0.5, anchor=CENTER)
        tk.Button(self.root, text="Patient Login", command=self.patient_login).place(relx=0.7, rely=0.5, anchor=CENTER)

    def admin_login(self):
        # Instantiate Admin Login or Admin Page
        self.root.destroy()  # Close current window
        admin_root = tk.Tk()
        AdminPage(admin_root)  # Or Admin menu (This needs to link to the AdminPage in the breeze_admin_module)

    def mhwp_login(self):
        # Instantiate MHWP Page/Login (Placeholder function)
        messagebox.showinfo("Info", "MHWP Login under development")

    def patient_login(self):
        # Instantiate Patient Page/Login (Placeholder function)
        messagebox.showinfo("Info", "Patient Login under development")

# Placeholder AdminPage class, replace this with the import statement from your Admin module
class AdminPage:
    def __init__(self, root):
        self.root = root
        self.root.title("Admin Menu")  # Set window title
        tk.Label(self.root, text="Admin Dashboard (Placeholder)").pack()  # Placeholder label
        tk.Button(self.root, text="Logout", command=self.root.quit).pack()  # Logout button
        self.root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    HomePage(root)
    root.mainloop()
