import sys
import logging
import time
from controllers.admin import AdminController
from controllers.mhwp import MHWPController
from controllers.patient import PatientController
from models.user import Admin, MHWP, Patient
from utils.data_handler import read_json
# from utils.validation import validate_credentials

# Font and color codes (for reference)
Red = "\033[91m"  # use for errors (bright red for visibility)
Green = "\033[92m"  # use for success messages (bright green)
Yellow = "\033[93m"  # use for warnings or prompts (bright yellow)
Cyan = "\033[96m"  # use for general information (bright cyan)
Blue = "\033[94m"  # use for headings or important text (bright blue)
Magenta = "\033[95m"  # use for secondary emphasis (bright magenta)
Reset = "\033[0m"  # to reset text to normal
Bold = "\033[1m"  # to make text bold

# Setup logging for auditing purposes
logging.basicConfig(filename='audit.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Set timeout duration (in seconds) for inactivity
timeout_duration = 180  # 3 minutes
last_activity_time = time.time()

def log_action(action, user):
    logging.info(f"Action: {action}, Performed by: {user}")

def print_divider():
    print(f"{Blue}{Bold}=" * 55 + f"{Reset}")

def display_welcome_page():
    print_divider()
    print(f"{Green}{Bold}🍃 Welcome to Breeze Mental Health Management System 🍃{Reset}\n")
    print(f"{Magenta}✨ Your journey to better mental health starts here! ✨{Reset}\n")
    print(f"{Cyan}Please log in to continue.{Reset}\n")
    print_divider()

def reset_inactivity_timer():
    global last_activity_time
    last_activity_time = time.time()

def check_inactivity():
    """Check for inactivity and log out if timeout duration is exceeded."""
    if time.time() - last_activity_time > timeout_duration:
        print(f"{Red}Session timed out due to inactivity. Logging out...{Reset}")
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
            username = input(f"{Cyan}Enter your username: {Reset}")
            reset_inactivity_timer()

            # Check if username is valid
            if username not in users_dict:
                print(f"{Red}Username not found. Please try again. Attempts left: {retry_attempts - attempt - 1}{Reset}")
                log_action(f"Failed login attempt: Username '{username}' not found", "system")
                continue

            user_data = users_dict[username]
            
            # Even if account is disabled, allow login
            if user_data.get('status') == 'DISABLED':
                print(f"{Yellow}Your account has been disabled, but you can still log in.{Reset}")
                log_action(f"User '{username}' logged in despite being disabled", "system")
            
            # Prompt for password
            password = input(f"{Cyan}Enter your password: {Reset}")
            reset_inactivity_timer()

            # Validate credentials directly from the user dictionary
            if user_data['password'] == password :
                user_role = user_data['role']
                log_action(f"Successful login: Username '{username}'", username)

                print(f"{Green}{Bold}Welcome, {username}!{Reset}")
                return user_role, user_data['user_id']
            else:
                print(f"{Red}Invalid password or account not active. Please try again. Attempts left: {retry_attempts - attempt - 1}{Reset}")
                log_action(f"Failed login attempt: Incorrect password for Username '{username}'", "system")

        except ValueError as ve:
            print(f"{Red}Login Error: {ve}{Reset}")
        except Exception as e:
            print(f"{Red}An unexpected error occurred during login: {e}{Reset}")

    # After reaching retry attempts limit
    print(f"{Red}Exceeded the maximum number of login attempts. Exiting...{Reset}")
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
            password=user_info['password']
        )
        admin_controller = AdminController(admin_user)
        if hasattr(admin_controller, 'display_menu'):
            admin_controller.display_menu() # TODO: Implement display_menu method in AdminController
        else:
            print(f"{Red}Error: Admin controller does not have a display_menu method.{Reset}")

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
                status=user_info['status']  # 从 user_info 获取 status
            )
            patient_controller = PatientController(patient_user)  # 直接传递 patient_user
            if hasattr(patient_controller, 'display_patient_homepage'):
                patient_controller.display_patient_homepage()
            else:
                print(f"{Red}Error: Patient controller does not have a display_patient_homepage method.{Reset}")
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
                patient_count=mhwp_info.get('patient_count', 0)
            )
            mhwp_controller = MHWPController(mhwp_user)
            if hasattr(mhwp_controller, 'display_menu'):
                mhwp_controller.display_menu() # TODO: Implement display_menu method in MHWPController
            else:
                print(f"{Red}Error: MHWP controller does not have a display_menu method.{Reset}")
        else:
            print("MHWP-specific information not found.")

    else:
        print(f"{Red}User role is not recognized. Please contact the administrator.{Reset}")
        log_action(f"User role '{user_role}' not recognized for user '{user_id}'", "system")

def main():
    while True:
        display_welcome_page()
        user_role, user_id = login()
        if user_role and user_id:
            role_navigation(user_role, user_id)
        else:
            retry = input(f"{Yellow}Would you like to try again? (y/n): {Reset}").lower()
            reset_inactivity_timer()
            if retry != 'y':
                print(f"{Cyan}Exiting... Goodbye!{Reset}")
                log_action("User chose to exit the system", "system")
                sys.exit()

if __name__ == "__main__":
    main()
