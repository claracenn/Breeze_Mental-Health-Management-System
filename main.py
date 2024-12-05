import sys
import logging
import time
from controllers.admin import AdminController
from controllers.mhwp import MHWPController
from controllers.patient import PatientController
from models.user import Admin, MHWP, Patient
from utils.data_handler import *
from utils.display_manager import *


"""
==================================
Initialise ANSI color codes
==================================
"""
BOLD = "\033[1m"
UNDERLINE = "\033[4m"
RESET = "\033[0m"
RED = "\033[91m"
LIGHT_GREEN = "\033[92m"
GREEN = "\033[92m"
CYAN = "\033[96m"
GREY = "\033[90m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
YELLOW = "\033[93m"
ITALIC = "\033[3m"
ORANGE = "\033[1;33m"  
display_manager = DisplayManager()

# Set logging for auditing purposes
logging.basicConfig(filename='audit.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Set timeout duration (in seconds) for inactivity
timeout_duration = 180  # 3 minutes
last_activity_time = time.time()

def log_action(action, user):
    logging.info(f"Action: {action}, Performed by: {user}")

def display_welcome_page():
    display_manager.print_divider(line="=", length=70, style=f"{BOLD}")
    display_manager.print_centered_message(message="🍃 Breeze Mental Health Management System 🍃", style=f"{GREEN}{BOLD}")
    display_manager.print_centered_message(message="✨ Your journey to better mental health starts here! ✨", style=f"{MAGENTA}")
    display_manager.print_divider(line="=", length=70, style=f"{BOLD}")
    print(f"{CYAN}Please log in to continue.{CYAN}{RESET}")

def reset_inactivity_timer():
    global last_activity_time
    last_activity_time = time.time()

def check_inactivity():
    """Check for inactivity and log out if timeout duration is exceeded."""
    if time.time() - last_activity_time > timeout_duration:
        print(f"{RED}Session timed out due to inactivity. Logging out...{RESET}")
        log_action("Session timed out due to inactivity", "system")
        sys.exit()

def get_user_info_by_userid(user_id, filepath):
    """Retrieve basic user information by user_id from user.json."""
    user_data = read_json(filepath)
    
    for user in user_data:
        # Check if the user_id matches
        if 'user_id' in user and int(user['user_id']) == user_id:
            return user  # Return the user dictionary if found
    
    print(f"No user found with user id '{user_id}' in {filepath}.")
    return None

def get_role_specific_info(user_id, role, filepath):
    """Retrieve role-specific information by user_id from role-specific files."""
    user_data = read_json(filepath)
    
    # Determine the correct key for user_id based on the role
    user_id_key = 'patient_id' if role == 'patient' else 'mhwp_id' if role == 'mhwp' else 'user_id'
    
    for user in user_data:
        if user_id_key in user and int(user[user_id_key]) == user_id:
            return user  # Return the role-specific user dictionary if found
    
    print(f"No {role} data found for user id '{user_id}' in {filepath}.")
    return None

def login():
    """Prompt user for login credentials and validate them."""
    retry_attempts = 3  # Set retry attempts for login
    users_data = read_json('./data/user.json')
    
    if not users_data:
        print("No users loaded. Exiting program.")
        sys.exit()
    
    users_dict = {user["username"]: user for user in users_data if "username" in user and "password" in user}

    for attempt in range(retry_attempts):
        check_inactivity()
        try:
            # Prompt user for credentials
            username = input("Enter your username: ")
            reset_inactivity_timer()

            # Check if username is valid
            if username not in users_dict:
                print(f"{RED}Username not found. Please try again. Attempts left: {retry_attempts - attempt - 1}{RESET}")
                log_action(f"Failed login attempt: Username '{username}' not found", "system")
                continue

            user_data = users_dict[username]
            
            # Even if account is disabled, allow login
            if user_data.get('status') == 'DISABLED':
                print(f"{YELLOW}Your account has been disabled, but you can still log in.{RESET}")
                log_action(f"User '{username}' logged in despite being disabled", "system")
            
            # Prompt for password
            password = input(f"Enter your password:")
            reset_inactivity_timer()

            # Validate credentials directly from the user dictionary
            if user_data['password'] == password :
                user_role = user_data['role']
                log_action(f"Successful login: Username '{username}'", username)

                print("\n")
                display_manager.print_centered_message(message=f"🙋 Welcome, {username}!", style=f"{BOLD}")
                display_manager.print_divider(line="~", length=70, style=f"{BOLD}")
                return user_role, user_data['user_id']
            else:
                print(f"{RED}Invalid password or account not active. Please try again. Attempts left: {retry_attempts - attempt - 1}{RESET}")
                log_action(f"Failed login attempt: Incorrect password for Username '{username}'", "system")

        except ValueError as ve:
            print(f"{RED}Login Error: {ve}{RESET}")
        except Exception as e:
            print(f"{RED}An unexpected error occurred during login: {e}{RESET}")

    # After reaching retry attempts limit
    print(f"{RED}Exceeded the maximum number of login attempts. Exiting...{RESET}")
    log_action("Exceeded maximum login attempts", "system")
    sys.exit()


def role_navigation(user_role, user_id):
    """Navigate based on the user's role and initialize the appropriate controller."""
    check_inactivity()
    
    user_info = get_user_info_by_userid(user_id, './data/user.json')
    if not user_info:
        print("User information not found.")
        return

    if user_role == 'admin':
        admin_user = Admin(
            user_id=user_info['user_id'],
            username=user_info['username'],
            password=user_info['password'],
            status=user_info['status']
        )
        admin_controller = AdminController(admin_user)
        if hasattr(admin_controller, 'display_admin_homepage'):
            admin_controller.display_admin_homepage()
        else:
            print(f"{RED}Error: Admin controller does not have a display_menu method.{RESET}")

    elif user_role == 'patient':
        patient_info = get_role_specific_info(user_id, 'patient', './data/patient_info.json')
        if patient_info:
            patient_user = Patient(
                user_id=user_info['user_id'],
                username=user_info['username'],
                password=user_info['password'],
                name=patient_info['name'],
                email=patient_info['email'],
                emergency_contact_email=patient_info['emergency_contact_email'],
                mhwp_id=patient_info.get('mhwp_id', ""),
                status=user_info['status']
            )
            patient_controller = PatientController(patient_user)
            if hasattr(patient_controller, 'display_patient_homepage'):
                patient_controller.display_patient_homepage()
            else:
                print(f"{RED}Error: Patient controller does not have a display_patient_homepage method.{RESET}")
        else:
            print("Patient-specific information not found.")

    elif user_role == 'mhwp':
        mhwp_info = get_role_specific_info(user_id, 'mhwp', './data/mhwp_info.json')
        if mhwp_info:
            mhwp_user = MHWP(
                user_id=user_info['user_id'],
                username=user_info['username'],
                password=user_info['password'],
                name=mhwp_info['name'],
                email=mhwp_info['email'],
                patient_count=mhwp_info.get('patient_count', 0),
                status=user_info['status']
            )
            mhwp_controller = MHWPController(mhwp_user)
            if hasattr(mhwp_controller, 'display_mhwp_homepage'):
                mhwp_controller.display_mhwp_homepage()
            else:
                print(f"{RED}Error: MHWP controller does not have a display_menu method.{RESET}")
        else:
            print("MHWP-specific information not found.")

    else:
        print(f"{RED}User role is not recognized. Please contact the administrator.{RESET}")
        log_action(f"User role '{user_role}' not recognized for user '{user_id}'", "system")

def main():
    while True:
        display_welcome_page()
        user_role, user_id = login()
        if user_role and user_id:
            role_navigation(user_role, user_id)
        else:
            retry = input(f"{YELLOW}Would you like to try again? (y/n): {RESET}").lower()
            reset_inactivity_timer()
            if retry != 'y':
                print(f"{CYAN}Exiting... Goodbye!{RESET}")
                log_action("User chose to exit the system", "system")
                sys.exit()

if __name__ == "__main__":
    main()
