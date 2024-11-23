import pandas as pd
import json
import logging
from models.user import Admin, MHWP, Patient
from utils.data_handler import *
from datetime import datetime

# from controllers.mhwp import MHWPController
# from controllers.patient import PatientController

##python -m controllers.admin

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
        # Calculate the centered message without ANSI codes
        centered_message = message.center(79)
        # Add the color codes around the centered message
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
            # Load user data based on user type
            if user_type == "patient":
                user_data = read_json("../data/patient_info.json")
            elif user_type == "mhwp":
                user_data = read_json("../data/mhwp_info.json")
            else:
                raise ValueError("Invalid user type specified.")

            # Extract user IDs based on user type
            user_ids = [str(user["patient_id"]) for user in user_data] if user_type == "patient" else [
                str(user["mhwp_id"]) for user in user_data]

            # Prompt for User ID and validate if the user exists
            user_id = self.get_user_input(f"{Cyan}{Italic}Enter User ID: {Reset}", valid_options=user_ids).strip()

            # Retrieve and return the user info dictionary
            user_info = next((user for user in user_data if str(user["patient_id"]) == user_id),
                             None) if user_type == "patient" else next(
                (user for user in user_data if str(user["mhwp_id"]) == user_id), None)

            if not user_info:
                print(f"{Red}User ID {user_id} not found. Returning to the Admin Menu...{Reset}")
                raise BackException()

            return user_info

        except BackException:
            # Handle the back scenario
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
        """Displays users of the given type, with an optional filter on status."""
        user_data_path = "../data/patient_info.json" if user_type == "patient" else "../data/mhwp_info.json"
        user_data = read_json(user_data_path)

        if user_data is None:
            print(f"{Red}Failed to load user data. Please check the file and try again.{Reset}")
            return

        # Load corresponding status information from user.json
        user_status_data_path = "../data/user.json"
        user_status_data = read_json(user_status_data_path)

        if user_status_data is None:
            print(f"{Red}Failed to load user status data. Please check the file and try again.{Reset}")
            return

        # Filter users based on status if a filter is provided
        filtered_users = []
        for user in user_data:
            user_id = user["patient_id"] if user_type == "patient" else user["mhwp_id"]
            user_record = next((u for u in user_status_data if u["user_id"] == user_id), None)

            if user_record and (status_filter is None or user_record["status"] == status_filter):
                filtered_users.append(user)

        if not filtered_users:
            print(f"{Yellow}No users found with status '{status_filter}'.{Reset}")
            return

        # Display the filtered users
        user_ids = [str(user["patient_id"]) for user in filtered_users] if user_type == "patient" else [
            str(user["mhwp_id"]) for user in filtered_users]
        user_names = [str(user["name"]) for user in filtered_users]
        user_dict = {"User ID": user_ids, "User Names": user_names}
        create_table(user_dict)

    # Function to get the element by patient_id or mhwp_id
    def get_user_by_id(self, json_path, user_type_id: str, id_num):

        try:
            info = read_json(json_path)

            # Check if patient data loaded correctly
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

    # Creates a dictionary of a patient and their respective MHWP
    # If the patient doesn't have a MHWP, assign them to MHWP
    # used as input
    def allocate_patient(self, mhwp: MHWP, patient: Patient):

        patient_data_path_name = "../data/patient_info.json"
        patient_info = read_json(patient_data_path_name)

        # Check if patient data loaded correctly
        if patient_info is None or not isinstance(patient_info, list):
            self.log_action(f"Failed to read patient data from {patient_data_path_name}", "error", "system")
            return "data_error"

        # Iterate through patient data and assign the MHWP to the patient
        for patient_details in patient_info:
            if str(patient_details["patient_id"]) == str(patient.user_id):
                # Check if the patient is already assigned to the same MHWP
                if patient_details.get("mhwp_id") == mhwp.user_id:
                    self.log_action(
                        f"Attempted to reassign Patient ID {patient.user_id} to the same MHWP ID {mhwp.user_id}",
                        "info", self.admin.username)
                    return "already_assigned"

                # If not assigned to the same MHWP, proceed to update
                patient_details["mhwp_id"] = mhwp.user_id
                break

        try:
            # Save the updated patient data back to the JSON file
            with open(patient_data_path_name, 'w') as file:
                json.dump(patient_info, file, indent=4)

            self.log_action(f"Allocated Patient ID {patient.user_id} to MHWP ID {mhwp.user_id}", "info",
                            self.admin.username)
            return "success"

        except IOError as e:
            print(f"{Red}An error occurred while saving the updated patient data: {e}{Reset}")
            self.log_action(f"Failed to save updated patient data: {e}", "error", self.admin.username)
            return "save_error"

    # Updates user
    # Checks if they are patients and amends their attributes accordingly
    # Also checks if they are a MHWP and amends their attributes accordingly
    def edit_user(self, user, new_data: dict):
        if user.is_disabled:
            self.log_action(f"Attempted to edit disabled User ID {user.user_id}", "warning", self.admin.username)
            raise PermissionError("User is disabled, cannot edit")

        # Fields allowed for editing
        editable_fields = ['name', 'email', 'emergency_contact_email']
        if isinstance(user, Patient):
            editable_fields.append('emergency_contact_email')

        # Apply new values to the user object
        for field, value in new_data.items():
            if field in editable_fields:
                setattr(user, field, value)
            else:
                print(f"{Red}Warning: {field} is not editable for this user type.{Reset}")

        # Update data in the JSON file
        user_data_path = "../data/patient_info.json" if isinstance(user, Patient) else "../data/mhwp_info.json"
        user_data = read_json(user_data_path)
        user_found = False

        for i, user_details in enumerate(user_data):
            # Find the corresponding user to update in JSON data
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

    def disable_user(self, user_record, user_info):
        try:
            # Get the path of user data file
            user_data_path = "../data/user.json"
            user_data = read_json(user_data_path)

            if user_data is None:
                print(f"{Red}Failed to load user data. Please check the file and try again.{Reset}")
                return

            # Update the user's status to DISABLED
            user_found = False
            for user in user_data:
                if user["user_id"] == user_record["user_id"]:
                    if user.get("status") == "DISABLED":
                        print(
                            f"{Yellow}User {user_info['name']} (User ID: {user['user_id']}) is already disabled.{Reset}")
                        return
                    # Set user status to DISABLED
                    user["status"] = "DISABLED"
                    user_found = True
                    break

            # If for some reason the user isn't found in the data file, notify the admin
            if not user_found:
                print(f"{Red}User ID {user_record['user_id']} not found in the system.{Reset}")
                return

            # Save the updated data back to the JSON file
            with open(user_data_path, 'w') as file:
                json.dump(user_data, file, indent=4)

            # Log the action and inform the admin
            print(
                f"{Green}User {user_info['name']} (User ID: {user_record['user_id']}) has been disabled successfully.{Reset}")
            self.log_action(f"Disabled User ID {user_record['user_id']}", "info", self.admin.username)

        except IOError as e:
            print(f"{Red}An error occurred while saving the updated user data: {e}{Reset}")
            self.log_action(f"Failed to save updated user data: {e}", "error", self.admin.username)
        except Exception as e:
            print(f"{Red}An unexpected error occurred: {e}{Reset}")
            self.log_action(f"Unexpected error in disable_user: {e}", "error", self.admin.username)

    def activate_user(self, user_record, user_info):
        try:
            # Get the path of user data file
            user_data_path = "../data/user.json"
            user_data = read_json(user_data_path)

            if user_data is None:
                print(f"{Red}Failed to load user data. Please check the file and try again.{Reset}")
                return

            # Update the user's status to ACTIVE
            user_found = False
            for user in user_data:
                if user["user_id"] == user_record["user_id"]:
                    if user.get("status") == "ACTIVE":
                        print(
                            f"{Yellow}User {user_info['name']} (User ID: {user['user_id']}) is already active.{Reset}")
                        return
                    # Set user status to ACTIVE
                    user["status"] = "ACTIVE"
                    user_found = True
                    break

            # If for some reason the user isn't found in the data file, notify the admin
            if not user_found:
                print(f"{Red}User ID {user_record['user_id']} not found in the system.{Reset}")
                return

            # Save the updated data back to the JSON file
            with open(user_data_path, 'w') as file:
                json.dump(user_data, file, indent=4)

            # Log the action and inform the admin
            print(
                f"{Green}User {user_info['name']} (User ID: {user_record['user_id']}) has been activated successfully.{Reset}")
            self.log_action(f"Activated User ID {user_record['user_id']}", "info", self.admin.username)

        except IOError as e:
            print(f"{Red}An error occurred while saving the updated user data: {e}{Reset}")
            self.log_action(f"Failed to save updated user data: {e}", "error", self.admin.username)
        except Exception as e:
            print(f"{Red}An unexpected error occurred: {e}{Reset}")
            self.log_action(f"Unexpected error in activate_user: {e}", "error", self.admin.username)

    def delete_user_from_file(self, user_del, file_path):

        try:
            user_info = read_json(file_path)
            if isinstance(user_del, Patient):
                user_type = "patient"
            elif isinstance(user_del, MHWP):
                user_type = "mhwp"
            if file_path == "../data/user.json":
                user_type = "user"

            fin_json = []

            for i in range(len(user_info)):
                user = user_info[i]

                # Creating a new lists of Patients by checking id
                if user[f"{user_type}_id"] != user_del.user_id:
                    fin_json.append(user)

            # save it in the new patient info
            with open(file_path, 'w') as file:
                json.dump(fin_json, file, indent=4)
            print(f"{Green}{user_type.capitalize()} {user_del.user_id} deleted successfully from {file_path}.{Reset}")
            self.log_action(f"Deleted {user_type.capitalize()} ID {user_del.user_id}", "info", self.admin.username)

        except IOError as e:
                print(f"{Red}An error occurred while deleting user data: {e}{Reset}")
                self.log_action(f"Failed to deleted user data: {e}", "error", self.admin.username)

    
    # deletes a specific patient based on their user id, writes json file
    # without the patient you want to delete
    def delete_patient(self, patient_del: Patient):
        confirm = self.get_user_input(f"{Red}Are you sure you want to delete Patient ID {patient_del.user_id}? (y/n): {Reset}", valid_options=["y", "n"]).strip().lower()
        if confirm != 'y':
            print(f"{Cyan}Action cancelled. Returning to Admin Menu...{Reset}")
            return

        try:
            #get mhwp id from patient_del to update patient count
            mhwp_file_path = "../data/mhwp_info.json"
            mhwp_id = patient_del.mhwp_id
            mhwp_info = read_json(mhwp_file_path)
            fin_json = []

            #adjust patient count -= 1 for specific mhwp
            for i in range(len(mhwp_info)):
                mhwp = mhwp_info[i]

                if mhwp['mhwp_id'] == mhwp_id:
                    mhwp['patient_count'] -= 1

                fin_json.append(mhwp)

            #write to mhwp_info.json
            with open(mhwp_file_path, 'w') as file:
                json.dump(fin_json, file, indent=4)
            print(f"{Green}Patient {patient_del.user_id} deleted successfully.{Reset}")
            self.log_action(f"Deleted Patient ID {patient_del.user_id}", "info", self.admin.username)


            #edit patient related files
            patient_file_paths = [
                                "../data/appointment.json",
                                "../data/patient_info.json",
                                "../data/patient_journal.json",
                                "../data/patient_mood.json",
                                "../data/patient_record.json",
                                "../data/user.json"
                                 ]
            
            for path in patient_file_paths:
                self.delete_user_from_file(patient_del, path)
        
        except IOError as e:
                print(f"{Red}An error occurred while deleting user data: {e}{Reset}")
                self.log_action(f"Failed to deleted user data: {e}", "error", self.admin.username)

    #deletes a specific MHWP based on their user id, writes json file
    #without the MHWP you want to delete
    def delete_mhwp(self, mhwp_del: MHWP):
        confirm = self.get_user_input(f"{Red}Are you sure you want to delete MHWP ID {mhwp_del.user_id}? (y/n): {Reset}", valid_options=["y", "n"])
        if confirm != 'y':
            print(f"{Cyan}Action cancelled. Returning to Admin Menu...{Reset}")
            return
        
        try:
            # Check for existing relationships with patients
            patient_data = read_json("../data/patient_info.json")
            patients_assigned = [patient for patient in patient_data if patient.get("mhwp_id") == mhwp_del.user_id]

            if patients_assigned:
                print(f"{Red}MHWP has assigned patients. Please reassign these patients before deleting.{Reset}")
                self.log_action(f"Attempted to delete MHWP ID {mhwp_del.user_id} with assigned patients", "warning", self.admin.username)
                return
            
            # Check for any existing appointments with patients
            # Checks future uncancelled appointments
            appointment_data = read_json("../data/appointment.json")
            current_datetime = datetime.now()
            #checks mhwp id, if the appointment is in the future, and if the appointment is not cancelled
            appointments_assigned = [
                    appt for appt in appointment_data
                    if appt.get("mhwp_id") == mhwp_del.user_id
                    and datetime.strptime(
                        f"{appt.get('date')} {appt.get('time_slot').split(' - ')[0]}", "%Y-%m-%d %H:%M"
                    ) > current_datetime
                    and appt.get("status") != "CANCELED"
                ]

            if appointments_assigned:
                print(f"{Red}MHWP has upcoming appointment with patients. Please reassign these patients before deleting the MHWP.{Reset}")
                self.log_action(f"Attempted to delete MHWP ID {mhwp_del.user_id} with assigned appointments", "warning", self.admin.username)
                return
            
            #checks if mhwp is mentioned in request_log.json
            #they shouldn't be expecting any requests to change or be changed from
            request_data = read_json("../data/request_log.json")
            requests_assigned = [mhwp for mhwp in request_data 
                                 if (mhwp.get("current_mhwp_id") == mhwp_del.user_id
                                 or mhwp.get("target_mhwp_id") == mhwp_del.user_id)
                                 and mhwp.get("status") == "pending"]
            
            
            if requests_assigned:
                print(f"{Red}MHWP has pending requests for switching from or to another MHWP. Please reassign the MHWP before deleting the MHWP.{Reset}")
                self.log_action(f"Attempted to delete MHWP ID {mhwp_del.user_id} with pending requests", "warning", self.admin.username)
                return

            #edit patient related files
            mhwp_file_paths = [
                                "../data/mhwp_info.json",
                                "../data/user.json"
                              ]
            
            for path in mhwp_file_paths:
                    self.delete_user_from_file(mhwp_del, path)
        
        except IOError as e:
                print(f"{Red}An error occurred while deleting user data: {e}{Reset}")
                self.log_action(f"Failed to deleted user data: {e}", "error", self.admin.username)


    def delete_user(self, user):
        if isinstance(user, Patient):
            return self.delete_patient(user)
        if isinstance(user, MHWP):
            return self.delete_mhwp(user)

    def display_summary(self):
        try:
            self.update_breadcrumbs("Display Summary")

            # Outer loop to continuously return to Display Summary until the user chooses otherwise
            while True:
                self.show_breadcrumbs()
                self.print_page_header("Display Summary")

                # Load data and check for any issues
                patient_info, mhwp_info, user_info = self.load_summary_data()
                if not all([patient_info, mhwp_info, user_info]):
                    return

                # Add status information to data
                self.add_user_status_to_data(patient_info, mhwp_info, user_info)

                # Display data summary (total patients, MHWPs, and a preview of 5 rows each)
                self.display_summary_overview(patient_info, mhwp_info)

                # Ask the user if they want to see the full list
                user_choice = self.get_user_input(
                    f"{Cyan}{Italic}Select an option to view detailed data:{Reset}\n"
                    f"{Yellow}1. Patients Full Data\n"
                    f"{Yellow}2. MHWPs Full Data\n"
                    f"{Yellow}3. Patients and MHWPs Full Data\n"
                    f"{Yellow}4. No, return to main menu\n"
                    f"{Cyan}{Italic}Enter your choice (1/2/3/4):{Reset} ",
                    valid_options=["1", "2", "3", "4"]
                )

                if user_choice == "1":
                    self.view_full_data("Patients", patient_info)

                elif user_choice == "2":
                    self.view_full_data("MHWPs", mhwp_info)

                elif user_choice == "3":
                    self.view_full_data("Patients and MHWPs", patient_info, mhwp_info)

                elif user_choice == "4":
                    print(f"{Cyan}Returning to the main menu...{Reset}")
                    break

        except BackException:
            print(f"{Cyan}Returning to the previous menu...{Reset}")

        except Exception as e:
            print(f"{Red}An error occurred while displaying the summary. Please contact the administrator.{Reset}")
            self.log_action(f"Error in display_summary: {e}", "system")

        finally:
            if self.breadcrumbs:
                self.breadcrumbs.pop()

    # Helper Functions for Display Summary
    def load_summary_data(self):
        patient_info = read_json('../data/patient_info.json')
        mhwp_info = read_json('../data/mhwp_info.json')
        user_info = read_json('../data/user.json')

        # Check if files are loaded correctly
        if patient_info is None or mhwp_info is None or user_info is None:
            print(f"{Red}Failed to load user data. Please check the files and try again.{Reset}")
            return None, None, None

        return patient_info, mhwp_info, user_info

    def add_user_status_to_data(self, patient_info, mhwp_info, user_info):
        user_status_dict = {user["user_id"]: user["status"] for user in user_info}

        for patient in patient_info:
            patient_id = patient.get("patient_id")
            patient["status"] = user_status_dict.get(patient_id, "Unknown")

        for mhwp in mhwp_info:
            mhwp_id = mhwp.get("mhwp_id")
            mhwp["status"] = user_status_dict.get(mhwp_id, "Unknown")

    def display_summary_overview(self, patient_info, mhwp_info):
        df_patients = pd.DataFrame(patient_info)
        df_mhwps = pd.DataFrame(mhwp_info)

        print(f"{Cyan}Total Patients: {len(df_patients)}{Reset}")
        print(f"{Cyan}Total MHWPs: {len(df_mhwps)}{Reset}")

        print(f"{Blue}\nPatients Data (First 5 Records):{Reset}")
        print(df_patients.head())
        print(f"{Blue}\nMHWPs Data (First 5 Records):{Reset}")
        print(df_mhwps.head())

    def view_full_data(self, data_type, *data_frames):
        self.update_breadcrumbs(f"Full Data [{data_type}]")
        self.show_breadcrumbs()

        try:
            while True:
                # Print page header and divider
                self.print_page_header(f"Full Data [{data_type}]")

                for df, title in zip(data_frames, data_type.split(" and ")):
                    self.print_centered_message(f"Full {title} Data", f"{Blue}{Bold}")

                    # Check if df is a DataFrame and display it
                    if isinstance(df, pd.DataFrame):
                        print(df)
                    else:
                        df = pd.DataFrame(df)
                        print(df)

                    self.print_divider()

                # Provide an option to go back
                self.get_user_input(
                    f"{Cyan}{Italic}Press 'back' to return to the Display Summary menu...{Reset}",
                    allow_back=True
                )

        except BackException:
            # Back to the previous menu
            self.breadcrumbs.pop()

    def display_menu(self):
        while True:
            self.update_breadcrumbs("Admin Menu")
            self.show_breadcrumbs()
            self.print_divider()
            self.print_centered_message("🍃 Breeze Mental Health Management System 🍃", f"{Green}{Bold}")
            self.print_centered_message("[Admin Page]", f"{Magenta}")
            self.print_divider()

            print(f"{Cyan}Select one of the following options: {Reset}")
            print(f"{Yellow}1. Allocate a Patient to a MHWP{Reset}")
            print(f"{Yellow}2. Edit User{Reset}")
            print(f"{Yellow}3. Disable User{Reset}")
            print(f"{Yellow}4. Activate User{Reset}")
            print(f"{Yellow}5. Delete User{Reset}")
            print(f"{Yellow}6. Recover Deleted User{Reset}")
            print(f"{Yellow}7. Display Summary{Reset}")
            print(f"{Yellow}8. Log Out{Reset}")
            choice = input(f"{Cyan}{Italic}Enter your choice: {Reset}")

            if choice == '1':
                self.allocate_patient_menu()
            elif choice == '2':
                self.edit_user_menu()
            elif choice == '3':
                self.disable_user_menu()
            elif choice == '4':
                self.activate_user_menu()
            elif choice == '5':
                self.delete_user_menu()
            elif choice == '6':
                self.recover_user_menu()
            elif choice == '7':
                self.display_summary()
            elif choice == '8':
                self.print_centered_message("Logging out...", Cyan)
                break
            else:
                self.print_centered_message("Invalid choice, please try again.", Red)

    def allocate_patient_menu(self):
        self.update_breadcrumbs("Patient Allocation")
        self.show_breadcrumbs()
        try:
            # Load patient data
            patient_data = read_json("../data/patient_info.json")
            if patient_data is None:
                print(f"{Red}Failed to load patient data. Please check the file and try again.{Reset}")
                return

            patient_ids = [str(patient["patient_id"]) for patient in patient_data]
            patient_names = [str(patient["name"]) for patient in patient_data]
            patient_dict = {"Patient Id": patient_ids, "Patient Names": patient_names}
            create_table(patient_dict)

            # Print header and divider
            self.print_page_header("Allocation Page")

            # Ask for Patient ID
            retry_attempts = 0
            while retry_attempts < 3:
                patient_id = self.get_user_input(f"{Cyan}{Italic}Enter Patient ID to allocate: {Reset}").strip()
                if patient_id in patient_ids:
                    print(f"{Green}Patient ID {patient_id} found. Proceeding to assign an MHWP...{Reset}")
                    break
                else:
                    retry_attempts += 1
                    if retry_attempts < 3:
                        print(f"{Red}Patient ID '{patient_id}' not found. Please try again.{Reset}")
                    else:
                        print(
                            f"{Red}You have exceeded the maximum number of attempts. Returning to the Admin Menu...{Reset}")
                        self.breadcrumbs.pop()
                        return
                self.print_divider()  # Divider for retry attempts

            # Ask for MHWP ID
            mhwp_data = read_json("../data/mhwp_info.json")
            if mhwp_data is None:
                print(f"{Red}Failed to load MHWP data. Please check the file and try again.{Reset}")
                return

            mhwp_ids = [str(mhwp["mhwp_id"]) for mhwp in mhwp_data]
            mhwp_names = [str(mhwp["name"]) for mhwp in mhwp_data]
            mhwp_dict = {"MHWP Id": mhwp_ids, "MHWP Names": mhwp_names}
            create_table(mhwp_dict)

            retry_attempts = 0
            while retry_attempts < 3:
                mhwp_id = self.get_user_input(f"{Cyan}{Italic}Enter MHWP ID to assign to Patient {patient_id}: {Reset}").strip()
                if mhwp_id in mhwp_ids:
                    print(f"{Green}MHWP ID {mhwp_id} found. Assigning Patient {patient_id} to MHWP {mhwp_id}.{Reset}")

                    #temporarily create patient
                    #may need to fix this after merging
                    #update username & password
                    
                    patient_data = self.get_user_by_id("../data/patient_info.json", "patient_id", int(patient_id))
                    mhwp_data = self.get_user_by_id("../data/mhwp_info.json", "mhwp_id", int(mhwp_id))

                    patient = Patient(patient_id, f"patient{patient_id}", "", patient_data['email'], patient_data['emergency_contact_email'], patient_data['mhwp_id'])
                    mhwp = MHWP(mhwp_id, f"mhwp{mhwp_id}", "")

                    # Call allocate_patient and let it handle the final assignment
                    allocation_status = self.allocate_patient(mhwp, patient)

                    # Check allocation result and print appropriate messages
                    if allocation_status == "already_assigned":
                        print(f"{Yellow}Warning: Patient {patient_id} is already assigned to MHWP {mhwp_id}.{Reset}")
                    elif allocation_status == "success":
                        print(f"{Green}Patient {patient_id} successfully allocated to MHWP {mhwp_id}.{Reset}")
                    break
                else:
                    retry_attempts += 1
                    if retry_attempts < 3:
                        print(f"{Red}MHWP ID '{mhwp_id}' not found. Please try again.{Reset}")
                    else:
                        print(
                            f"{Red}You have exceeded the maximum number of attempts. Returning to the Admin Menu...{Reset}")
                        self.breadcrumbs.pop()
                        return
                self.print_divider()  # Divider for retry attempts

        except BackException:
            print(f"{Grey}Returning to the previous menu...{Reset}")
        except ValueError as ve:
            print(f"{Red}Input Error. Please make sure the provided input is valid and try again.{Reset}")
            self.log_action(f"Input Error in allocate_patient_menu: {ve}", "system")
        except Exception as e:
            print(f"{Red}An unexpected error occurred. Please contact the administrator for assistance.{Reset}")
            self.log_action(f"Unexpected error in allocate_patient_menu: {e}", "system")

        finally:
            if self.breadcrumbs:
                self.breadcrumbs.pop()

    def edit_user_menu(self):
        self.update_breadcrumbs("Edit User")
        self.show_breadcrumbs()

        # Print header and divider
        self.print_page_header("Edit User Page")

        try:
            # Get user type (patient or mhwp)
            user_type = self.get_user_type()

            # Display users based on the selected type
            self.display_users(user_type)

            # Retrieve user information based on the provided user type and ID
            user_info = self.get_user_info_by_id(user_type)
            if not user_info:
                return  # If the user chooses 'back' or the user does not exist, return to the previous menu

            # Show current user information
            self.display_user_info(user_info)

            # Collect fields to edit for patients and MHWPs
            new_data = {}

            # Get first name and last name separately, combine them into 'name' field
            new_first_name = self.get_user_input(
                f"{Cyan}{Italic}Enter new first name (leave blank to keep current):{Reset} "
            ).strip()
            new_last_name = self.get_user_input(
                f"{Cyan}{Italic}Enter new last name (leave blank to keep current):{Reset} "
            ).strip()
            if new_first_name or new_last_name:
                current_name = user_info.get("name", "")
                first_name, last_name = current_name.split(' ', 1) if ' ' in current_name else (current_name, "")
                first_name = new_first_name.capitalize() if new_first_name else first_name
                last_name = new_last_name.capitalize() if new_last_name else last_name
                new_data["name"] = f"{first_name} {last_name}"

            # Get email
            new_email = self.get_user_input(
                f"{Cyan}{Italic}Enter new email (leave blank to keep current):{Reset} "
            ).strip()
            if new_email:
                new_data["email"] = new_email

            # Get emergency contact email for patients
            if user_type == "patient":
                new_emergency_contact_email = self.get_user_input(
                    f"{Cyan}{Italic}Enter new emergency contact email (leave blank to keep current):{Reset} "
                ).strip()
                if new_emergency_contact_email:
                    new_data["emergency_contact_email"] = new_emergency_contact_email

            # Confirmation step before making changes
            confirm = self.get_user_input(
                f"{Yellow}Are you sure you want to apply these changes? (y/n):{Reset} "
            ).strip().lower()
            if confirm != 'y':
                print(f"{Cyan}Edit operation cancelled. Returning to Admin Menu...{Reset}")
                return

            # Create user object with updated details
            if user_type == "patient":
                user = Patient(
                    int(user_info["patient_id"]),
                    user_info["name"],
                    "",
                    user_info.get("email"),
                    user_info.get("emergency_contact_email"),
                    user_info.get("mhwp_id")
                )
            elif user_type == "mhwp":
                user = MHWP(int(user_info["mhwp_id"]), user_info["name"], "")

            # Perform the edit operation
            self.edit_user(user, new_data)
            print(f"{Green}User ID {user.user_id} edited successfully.{Reset}")

        except BackException:
            print(f"{Grey}Returning to the previous menu...{Reset}")
        except ValueError as ve:
            print(f"{Red}Input Error: {ve}{Reset}")
        except PermissionError as e:
            print(f"{Red}Error: {e}{Reset}")
        except Exception as e:
            print(f"{Red}Error occurred: {e}{Reset}")
            self.log_action(f"Error in edit_user_menu: {e}", "error", self.admin.username)
        finally:
            if self.breadcrumbs:
                self.breadcrumbs.pop()

    def disable_user_menu(self):
        self.update_breadcrumbs("Disable User")
        self.show_breadcrumbs()

        # Print header and divider
        self.print_page_header("Disable User Page")

        try:
            # Get the user type (patient or mhwp) - this will handle retries internally
            user_type = self.get_user_type()

            # Display users of the selected type that are currently ACTIVE
            self.display_users(user_type, status_filter="ACTIVE")

            # Get the user ID (includes retry and validation)
            user_info = self.get_user_info_by_id(user_type)

            # Display selected user information
            self.display_user_info(user_info)

            # Retrieve the corresponding user record from user.json for status checking
            user_data_path = "../data/user.json"
            user_data = read_json(user_data_path)

            if user_data is None:
                print(f"{Red}Failed to load user data. Please check the file and try again.{Reset}")
                return

            # Find the user in user.json to check their status
            user_id = user_info.get("patient_id") if user_type == "patient" else user_info.get("mhwp_id")
            user_record = next((u for u in user_data if u["user_id"] == user_id), None)

            if not user_record:
                print(f"{Red}User ID {user_id} not found in the user records. Returning to the Admin Menu...{Reset}")
                return

            # Check if the user is already disabled
            if user_record.get("status") == "DISABLED":
                # Inform admin that the user is already disabled
                print(
                    f"{Yellow}Warning: {user_info.get('name')} (User ID: {user_id}) is already disabled.{Reset}")

                # Ask if the admin wants to disable another user or return
                proceed = self.get_user_input(
                    f"{Cyan}{Italic}Would you like to disable another user instead? (y/n): {Reset}",
                    valid_options=["y", "n"]
                ).strip().lower()

                if proceed == 'y':
                    # Restart the disable user menu to disable a different user
                    self.disable_user_menu()
                    return
                elif proceed == 'n':
                    print(f"{Cyan}Returning to the Admin Menu...{Reset}")
                    return

            # Confirmation to disable the user
            confirm = self.get_user_input(
                f"{Red}Are you sure you want to disable {user_info.get('name')} (User ID: {user_id})? (y/n): {Reset}",
                valid_options=["y", "n"])

            if confirm.lower() == 'n':
                print(f"{Cyan}Action cancelled. Returning to Admin Menu...{Reset}")
                return

            # Proceed to disable the user if they are not already disabled
            self.disable_user(user_record, user_info)

        except BackException:
            print(f"{Grey}Returning to the previous menu...{Reset}")
        except ValueError as ve:
            print(f"{Red}Input Error: {ve}{Reset}")
        except PermissionError as e:
            print(f"{Red}Error: {e}{Reset}")
        except Exception as e:
            print(f"{Red}Error occurred: {e}{Reset}")
        finally:
            if self.breadcrumbs:
                self.breadcrumbs.pop()

    def activate_user_menu(self):
        self.update_breadcrumbs("Activate User")
        self.show_breadcrumbs()

        # Print header and divider
        self.print_page_header("Activate User Page")

        try:
            # Get the user type (patient or mhwp) - this will handle retries internally
            user_type = self.get_user_type()

            # Display users of the selected type that are currently DISABLED
            self.display_users(user_type, status_filter="DISABLED")

            # Get the user ID (includes retry and validation)
            user_info = self.get_user_info_by_id(user_type)

            # Display selected user information
            self.display_user_info(user_info)

            # Retrieve the corresponding user record from user.json for status checking
            user_data_path = "../data/user.json"
            user_data = read_json(user_data_path)

            if user_data is None:
                print(f"{Red}Failed to load user data. Please check the file and try again.{Reset}")
                return

            # Find the user in user.json to check their status
            user_id = user_info.get("patient_id") if user_type == "patient" else user_info.get("mhwp_id")
            user_record = next((u for u in user_data if u["user_id"] == user_id), None)

            if not user_record:
                print(f"{Red}User ID {user_id} not found in the user records. Returning to the Admin Menu...{Reset}")
                return

            # Check if the user is already active
            if user_record.get("status") == "ACTIVE":
                # Inform admin that the user is already active
                print(
                    f"{Yellow}Warning: {user_info.get('name')} (User ID: {user_id}) is already active.{Reset}")

                # Ask if the admin wants to activate another user or return
                proceed = self.get_user_input(
                    f"{Cyan}{Italic}Would you like to activate another user instead? (y/n): {Reset}",
                    valid_options=["y", "n"]
                ).strip().lower()

                if proceed == 'y':
                    # Restart the activate user menu to activate a different user
                    self.activate_user_menu()
                    return
                elif proceed == 'n':
                    print(f"{Cyan}Returning to the Admin Menu...{Reset}")
                    return

            # Confirmation to activate the user
            confirm = self.get_user_input(
                f"{Green}Are you sure you want to activate {user_info.get('name')} (User ID: {user_id})? (y/n): {Reset}",
                valid_options=["y", "n"])

            if confirm.lower() == 'n':
                print(f"{Cyan}Action cancelled. Returning to Admin Menu...{Reset}")
                return

            # Proceed to activate the user if they are not already active
            self.activate_user(user_record, user_info)

        except BackException:
            print(f"{Grey}Returning to the previous menu...{Reset}")
        except ValueError as ve:
            print(f"{Red}Input Error: {ve}{Reset}")
        except PermissionError as e:
            print(f"{Red}Error: {e}{Reset}")
        except Exception as e:
            print(f"{Red}Error occurred: {e}{Reset}")
        finally:
            if self.breadcrumbs:
                self.breadcrumbs.pop()

    def delete_user_menu(self):
        self.update_breadcrumbs("Delete User")
        self.show_breadcrumbs()

        # Print header and divider
        self.print_page_header("Delete User Page")

        try:
            # Get user type ('patient' or 'mhwp') using a helper function
            user_type = self.get_user_type()

            # Display existing users of the selected type
            self.display_users(user_type)

            # Load user data and get user IDs
            user_data_path = "../data/patient_info.json" if user_type == "patient" else "../data/mhwp_info.json"
            user_data = read_json(user_data_path)
            user_ids = [str(user.get(f"{user_type}_id")) for user in user_data]

            # Get valid user ID
            user_id = self.get_user_id(user_type, user_ids)

            # Retrieve the specific user information
            user_info = self.get_user_by_id(user_data_path, f"{user_type}_id", int(user_id))

            # Display user information in a table
            create_table([user_info])

            # Instantiate the corresponding user object
            if user_type == "patient":
                user = Patient(
                    int(user_id), f"patient{user_id}", "",
                    user_info.get("email"), user_info.get("emergency_contact_email"),
                    user_info.get("mhwp_id")
                )
            elif user_type == "mhwp":
                user = MHWP(int(user_id), f"mhwp{user_id}", "")

            # Step 8: Call delete user
            self.delete_user(user)

        except BackException:
            print(f"{Grey}Returning to the previous menu...{Reset}")
        except ValueError as ve:
            print(f"{Red}Input Error: {ve}{Reset}")
        except PermissionError as e:
            print(f"{Red}Error: {e}{Reset}")
        except Exception as e:
            print(f"{Red}Error occurred: {e}{Reset}")
        finally:
            if self.breadcrumbs:
                self.breadcrumbs.pop()

if __name__ == "__main__":
    admin_user = Admin(1, "admin", "")
    admin_controller = AdminController(admin_user)
    admin_controller.display_menu()
