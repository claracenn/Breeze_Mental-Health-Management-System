from models.user import Admin, MHWP, Patient
from controllers.admin import AdminController
from controllers.patient import PatientController
from controllers.mhwp import MHWPController
import sys

# Sample data
users = {
    "admin1": {"password": "", "role": "admin"},
    "mhwp1": {"password": "", "role": "mhwp"},
    "patient1": {"password": "", "role": "patient"},
}

# Display the welcome page
def display_welcome_page():
    print()
    print("🍃\033[1m Welcome to Breeze Mental Health System\033[0m 🍃", end='\n\n')
    print("-----------------------------------------------", end='\n\n')
    print(" ⬇️  Please login to continue. ⬇️", end='\n\n')

# Handle user login
def login():
    username = input("Enter username: ")
    password = input("Enter password: ")

    # Check if the username exists
    if username in users and users[username]["password"] == password:
        role = users[username]["role"]
        print(f"\nLogin successful! Welcome, {username}!")
        print(f"Role: {role.capitalize()}\n")
        return role
    else:
        print("\nInvalid username or password. Please try again.\n")
        return None

# Show options after login
def show_options(role):
    if role == "admin":
        print("Welcome, Admin! Here are your options:")
        print("1. Manage Patients and MHWPs")
        print("2. View System Summary")
        print("3. Logout")
    elif role == "mhwp":
        print("Welcome, MHWP! Here are your options:")
        print("1. View Appointments")
        print("2. Manage Patient Records")
        print("3. Display Dashboard")
        print("4. Logout")
    elif role == "patient":
        print("Welcome, Patient! Here are your options:")
        print("1. Book/Cancel Appointment")
        print("2. Enter Mood Track or Journal")
        print("3. Logout")
    else:
        print("Unknown role.")

# Main function
def main():
    display_welcome_page()

    role = None
    while role is None:
        role = login()

    show_options(role)

    action = input("\nChoose an option (or 'logout' to exit): ").lower()
    if action == "logout":
        print("Logging out. Goodbye!")
        sys.exit(0)
    # Linked to Controllers to implement the functionality of each user role
    else:
        print("Functionality implementing...")
        

if __name__ == "__main__":
    main()


# Font and color codes (for reference)
    Red = "\033[31m"  # use for errors
    Green = "\033[32m"  # use for success messages
    Yellow = "\033[33m"  # use for warnings or prompts
    Cyan = "\033[36m"  # use for general information
    Reset = "\033[0m"  # to reset text to normal
    Bold = "\033[1m"  # to make text bold