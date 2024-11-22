import pandas as pd
import json
import logging
import os
from models.user import Admin, MHWP, Patient
from utils.data_handler import *
from datetime import datetime

# Font and color codes (for reference)
Grey = "\033[0;37m"
Red = "\033[91m"
Green = "\033[92m"
Yellow = "\033[93m"
Cyan = "\033[96m"
Blue = "\033[94m"
Magenta = "\033[95m"
Reset = "\033[0m"  # to reset text to normal
Bold = "\033[1m"  # to make text bold
Italic = "\033[3m"

# Base directory for files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PATIENT_FILE_PATH = os.path.join(BASE_DIR, "data", "patient_info.json")
MHWP_FILE_PATH = os.path.join(BASE_DIR, "data", "mhwp_info.json")
USER_FILE_PATH = os.path.join(BASE_DIR, "data", "user.json")
REQUEST_LOG_FILE_PATH = os.path.join(BASE_DIR, "data", "mhwp_change_request.json")


class BackException(Exception):
    """Custom exception used to signal a request to return to the previous menu."""
    pass


class AdminController:
    def __init__(self, admin: Admin):
        self.admin = admin

    # Breadcrumb Navigation Tracker
    breadcrumbs = []

    def update_breadcrumbs(self, location):
        if len(self.breadcrumbs) == 0 or self.breadcrumbs[-1] != location:
            self.breadcrumbs.append(location)

    def show_breadcrumbs(self):
        print(f"{Grey}Navigation: {' > '.join(self.breadcrumbs)}{Reset}")

    # Log function integrated into the class to ensure consistency
    def log_action(self, action, level='info', user="system"):
        if level == 'info':
            logging.info(f"Action: {action}, Performed by: {user}")
        elif level == 'warning':
            logging.warning(f"Action: {action}, Performed by: {user}")
        elif level == 'error':
            logging.error(f"Action: {action}, Performed by: {user}")
        elif level == 'debug':
            logging.debug(f"Action: {action}, Performed by: {user}")

    def print_divider(self):
        print(f"{Blue}{Bold}=" * 79 + f"{Reset}")

    def print_centered_message(self, message, color_code):
        centered_message = message.center(79)
        print(f"{color_code}{centered_message}{Reset}")

    def get_user_input(self, prompt, valid_options=None, retries=3, allow_back=True):
        attempt = 0
        while attempt < retries:
            user_input = input(f"{prompt}").strip().lower()

            # Handle 'back' input
            if allow_back and user_input == 'back':
                raise BackException()

            # Validate against valid options if provided
            if valid_options is None or user_input in valid_options:
                return user_input
            else:
                print(f"{Red}Invalid input. Please try again.{Reset}")
                attempt += 1

        # If retries exceeded, also treat it as going back
        print(f"{Red}Maximum number of attempts reached. Returning to previous menu...{Reset}")
        raise BackException()

    def get_user_type(self):
        return self.get_user_input(
            f"{Cyan}{Italic}Enter user type (patient/mhwp): {Reset}",
            valid_options=["patient", "mhwp"]
        )

    def get_user_id(self, user_type, user_ids):
        return self.get_user_input(
            f"{Cyan}{Italic}Enter {user_type.capitalize()} ID: {Reset}",
            valid_options=user_ids
        )

    def get_user_info_by_id(self, user_type):
        try:
            if user_type == "patient":
                user_data = read_json(PATIENT_FILE_PATH)
            elif user_type == "mhwp":
                user_data = read_json(MHWP_FILE_PATH)
            else:
                raise ValueError("Invalid user type specified.")

            user_ids = [str(user["patient_id"]) for user in user_data] if user_type == "patient" else [
                str(user["mhwp_id"]) for user in user_data]

            user_id = self.get_user_input(f"{Cyan}{Italic}Enter User ID: {Reset}", valid_options=user_ids).strip()

            user_info = next((user for user in user_data if str(user["patient_id"]) == user_id),
                             None) if user_type == "patient" else next(
                (user for user in user_data if str(user["mhwp_id"]) == user_id), None)

            if not user_info:
                print(f"{Red}User ID {user_id} not found. Returning to the Admin Menu...{Reset}")
                raise BackException()

            return user_info

        except BackException:
            raise BackException()
        except Exception as e:
            print(f"{Red}An error occurred while retrieving user information: {e}{Reset}")
            self.log_action(f"Error in get_user_info_by_id: {e}", "error", self.admin.username)
            return None

    def print_page_header(self, title):
        self.print_divider()
        self.print_centered_message(title, f"{Magenta}{Bold}")
        self.print_centered_message("Type 'back' at any time to return to the previous menu", f"{Grey}")
        self.print_divider()

    def display_users(self, user_type, status_filter=None):
        user_data_path = PATIENT_FILE_PATH if user_type == "patient" else MHWP_FILE_PATH
        user_data = read_json(user_data_path)

        if user_data is None:
            print(f"{Red}Failed to load user data. Please check the file and try again.{Reset}")
            return

        user_status_data = read_json(USER_FILE_PATH)

        if user_status_data is None:
            print(f"{Red}Failed to load user status data. Please check the file and try again.{Reset}")
            return

        filtered_users = []
        for user in user_data:
            user_id = user["patient_id"] if user_type == "patient" else user["mhwp_id"]
            user_record = next((u for u in user_status_data if u["user_id"] == user_id), None)

            if user_record and (status_filter is None or user_record["status"] == status_filter):
                filtered_users.append(user)

        if not filtered_users:
            print(f"{Yellow}No users found with status '{status_filter}'.{Reset}")
            return

        user_ids = [str(user["patient_id"]) for user in filtered_users] if user_type == "patient" else [
            str(user["mhwp_id"]) for user in filtered_users]
        user_names = [str(user["name"]) for user in filtered_users]
        user_dict = {"User ID": user_ids, "User Names": user_names}
        create_table(user_dict)

    def get_user_by_id(self, json_path, user_type_id: str, id_num):
        try:
            info = read_json(json_path)

            if info is None or not isinstance(info, list):
                self.log_action(f"Failed to read patient data from {json_path}", "error", "system")
                return "data_error"
            
            if user_type_id.strip().lower() not in ["patient_id", "mhwp_id"]:
                raise IOError("The user type id must be typed either as patient_id or mhwp_id.")

            user = next((item for item in info if item[user_type_id] == id_num), None)

            if type(user) != dict:
                raise ValueError("This user doesn't exist.")
            else:
                return user
        
        except IOError as ioe:
            print(f"{Red}An error occurred while searching for the specified user: {ioe}{Reset}")
            self.log_action(f"Failed to key in user type id: {ioe}", "error", self.admin.username)
            return "save_error"
        
        except ValueError as ve:
            print(f"{Red}An error occurred while searching for the specified user: {ve}{Reset}")
            self.log_action(f"Failed to find user: {ve}", "error", self.admin.username)
            return "save_error"

    def display_user_info(self, user_info):
        self.print_centered_message("Current User Information", f"{Blue}{Bold}")
        print(f"{Blue}-" * 79 + f"{Reset}")
        for key, value in user_info.items():
            print(f"{key}: {value}{Reset}")
        print(f"{Blue}-" * 79 + f"{Reset}")

    def allocate_patient(self, mhwp: MHWP, patient: Patient):
        patient_data_path_name = "../data/patient_info.json"
        patient_info = read_json(patient_data_path_name)

        if patient_info is None or not isinstance(patient_info, list):
            self.log_action(f"Failed to read patient data from {patient_data_path_name}", "error", "system")
            return "data_error"

        for patient_details in patient_info:
            if str(patient_details["patient_id"]) == str(patient.user_id):
                if patient_details.get("mhwp_id") == mhwp.user_id:
                    self.log_action(
                        f"Attempted to reassign Patient ID {patient.user_id} to the same MHWP ID {mhwp.user_id}",
                        "info", self.admin.username)
                    return "already_assigned"

                patient_details["mhwp_id"] = mhwp.user_id
                break

        try:
            with open(patient_data_path_name, 'w') as file:
                json.dump(patient_info, file, indent=4)

            self.log_action(f"Allocated Patient ID {patient.user_id} to MHWP ID {mhwp.user_id}", "info",
                            self.admin.username)
            return "success"

        except IOError as e:
            print(f"{Red}An error occurred while saving the updated patient data: {e}{Reset}")
            self.log_action(f"Failed to save updated patient data: {e}", "error", self.admin.username)
            return "save_error"

    def edit_user(self, user, new_data: dict):
        if user.is_disabled:
            self.log_action(f"Attempted to edit disabled User ID {user.user_id}", "warning", self.admin.username)
            raise PermissionError("User is disabled, cannot edit")

        editable_fields = ['name', 'email', 'emergency_contact_email']
        if isinstance(user, Patient):
            editable_fields.append('emergency_contact_email')

        for field, value in new_data.items():
            if field in editable_fields:
                setattr(user, field, value)
            else:
                print(f"{Red}Warning: {field} is not editable for this user type.{Reset}")

        user_data_path = "../data/patient_info.json" if isinstance(user, Patient) else "../data/mhwp_info.json"
        user_data = read_json(user_data_path)
        user_found = False

        for i, user_details in enumerate(user_data):
            if (str(user_details.get("patient_id") if isinstance(user, Patient) else user_details.get(
                    "mhwp_id")) == str(user.user_id)):
                for key in editable_fields:
                    if key in new_data:
                        user_details[key] = new_data[key]
                user_found = True
                break

        if user_found:
            try:
                with open(user_data_path, 'w') as file:
                    json.dump(user_data, file, indent=4)
                self.log_action(f"Edited User ID {user.user_id}", "info", self.admin.username)
            except IOError as e:
                print(f"{Red}An error occurred while saving the updated user data: {e}{Reset}")
                self.log_action(f"Failed to save updated user data: {e}", "error", self.admin.username)
        else:
            print(f"{Red}User not found in the data file.{Reset}")
            self.log_action(f"Failed to locate User ID {user.user_id} for editing", "error", self.admin.username)

        
