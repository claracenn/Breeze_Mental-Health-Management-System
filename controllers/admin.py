import pandas as pd
import json
import logging
from models.user import Admin, MHWP, Patient
from utils.data_handler import read_json

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
        print(f"{Blue}{Bold}=" * 55 + f"{Reset}")

    def print_centered_message(self, message, color_code):
        # Calculate the centered message without ANSI codes
        centered_message = message.center(55)
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

    def print_page_header(self, title):
        self.print_divider()
        self.print_centered_message(title, f"{Magenta}{Bold}")
        self.print_centered_message("Type 'back' at any time to return to the previous menu", f"{Grey}")
        self.print_divider()

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

    def disable_user(self, user):
        confirm = self.get_user_input(f"{Red}Are you sure you want to disable User ID {user.user_id}? (y/n): {Reset}", valid_options=["y", "n"])
        if confirm == 'y':
            user.is_disabled = True
            print(f"{Green}User {user.user_id} has been disabled successfully.{Reset}")
            self.log_action(f"Disabled User ID {user.user_id}", "info", self.admin.username)
        elif confirm == 'n':
            print(f"{Cyan}Action cancelled. Returning to Admin Menu...{Reset}")

    # deletes a specific patient based on their user id, writes json file
    # without the patient you want to delete
    def delete_patient(self, patient_del: Patient) -> None:
        confirm = self.get_user_input(f"{Red}Are you sure you want to delete Patient ID {patient_del.user_id}? (y/n): {Reset}", valid_options=["y", "n"])
        if confirm != 'y':
            print(f"{Cyan}Action cancelled. Returning to Admin Menu...{Reset}")
            return

        patient_data_path_name = "../data/patient_info.json"
        patient_info = read_json(patient_data_path_name)
        fin_json = []

        for i in range(len(patient_info)):
            patient = patient_info[i]

            # Creating a new lists of Patients
            # checks id and username/email
            if (patient['patient_id'] != patient_del.user_id and
                    patient['email'] != patient_del.username):
                fin_json.append(patient)

        # save it in the new patient info
        with open('../data/patient_info.json', 'w+') as file:
            json.dump(fin_json, file, indent=4)
        print(f"{Green}Patient {patient_del.user_id} deleted successfully.{Reset}")
        self.log_action(f"Deleted Patient ID {patient_del.user_id}", "info", self.admin.username)

    #deletes a specific MHWP based on their user id, writes json file
    #without the MHWP you want to delete
    def delete_mhwp(self, mhwp_del: MHWP):
        confirm = self.get_user_input(f"{Red}Are you sure you want to delete MHWP ID {mhwp_del.user_id}? (y/n): {Reset}", valid_options=["y", "n"])
        if confirm != 'y':
            print(f"{Cyan}Action cancelled. Returning to Admin Menu...{Reset}")
            return

        # Check for existing relationships with patients
        mhwp_data_path_name = "../data/mhwp_info.json"
        patient_data = read_json("../data/patient_info.json")
        patients_assigned = [patient for patient in patient_data if patient.get("mhwp_id") == mhwp_del.user_id]

        if patients_assigned:
            print(f"{Red}MHWP has assigned patients. Please reassign these patients before deleting.{Reset}")
            self.log_action(f"Attempted to delete MHWP ID {mhwp_del.user_id} with assigned patients", "warning", self.admin.username)
            return

        mhwp_info = read_json(mhwp_data_path_name)
        fin_json = []

        for i in range(len(mhwp_info)):
            mhwp = mhwp_info[i]

            #Creating a new list of MHWPs
            #checks id and username/email
            if (mhwp['mhwp_id'] != mhwp_del.user_id and
            mhwp['email'] != mhwp_del.username):
                fin_json.append(mhwp)

        #save it in the new MHWP info
        with open('../data/mhwp_info.json', 'w+') as file:
            json.dump(fin_json, file, indent=4)
        print(f"{Green}MHWP {mhwp_del.user_id} deleted successfully.{Reset}")
        self.log_action(f"Deleted MHWP ID {mhwp_del.user_id}", "info", self.admin.username)

    def delete_user(self, user):
        if isinstance(user, Patient):
            return self.delete_patient(user)
        if isinstance(user, MHWP):
            return self.delete_mhwp(user)

    def display_summary(self):
        try:
            self.update_breadcrumbs("Display Summary")
            self.show_breadcrumbs()
            patient_info = read_json('../data/patient_info.json')
            mhwp_info = read_json('../data/mhwp_info.json')
            print(f"{Cyan}Total Patients: {len(patient_info)}{Reset}")
            print(f"{Cyan}Total MHWPs: {len(mhwp_info)}{Reset}")

            df_patients = pd.DataFrame(patient_info)
            df_mhwps = pd.DataFrame(mhwp_info)
            print(f"{Blue}\nPatients Data:{Reset}")
            print(df_patients.head())
            print(f"{Blue}\nMHWPs Data:{Reset}")
            print(df_mhwps.head())
            self.breadcrumbs.pop()
        except Exception as e:
            print(f"{Red}An error occurred while displaying the summary. Please contact the administrator.{Reset}")
            self.log_action(f"Error in display_summary: {e}", "system")

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
            print(f"{Yellow}4. Delete User{Reset}")
            print(f"{Yellow}5. Display Summary{Reset}")
            print(f"{Yellow}6. Log Out{Reset}")
            choice = input(f"{Cyan}{Italic}Enter your choice: {Reset}")

            if choice == '1':
                self.allocate_patient_menu()
            elif choice == '2':
                self.edit_user_menu()
            elif choice == '3':
                self.disable_user_menu()
            elif choice == '4':
                self.delete_user_menu()
            elif choice == '5':
                self.display_summary()
            elif choice == '6':
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

            retry_attempts = 0
            while retry_attempts < 3:
                mhwp_id = self.get_user_input(f"{Cyan}{Italic}Enter MHWP ID to assign to Patient {patient_id}: {Reset}").strip()
                if mhwp_id in mhwp_ids:
                    print(f"{Green}MHWP ID {mhwp_id} found. Assigning Patient {patient_id} to MHWP {mhwp_id}.{Reset}")
                    patient = Patient(patient_id, f"patient{patient_id}", "")
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
            # Retry mechanism for user type input
            retry_attempts = 0
            while retry_attempts < 3:
                user_type = self.get_user_input(f"{Cyan}{Italic}Enter user type (patient/mhwp):{Reset} ").lower()
                if user_type in ["patient", "mhwp"]:
                    break
                else:
                    retry_attempts += 1
                    if retry_attempts < 3:
                        print(f"{Red}Invalid user type. Please enter 'patient' or 'mhwp'.{Reset}")
                    else:
                        print(f"{Red}You have exceeded the number of attempts. Returning to the Admin Menu...{Reset}")
                        self.breadcrumbs.pop()
                        return
                self.print_divider()

            # Prompt for User ID and validate if the user exists
            user_id = self.get_user_input(f"{Cyan}{Italic}Enter User ID: {Reset}").strip()
            if not user_id:
                print(f"{Red}User ID cannot be empty. Returning to the Admin Menu...{Reset}")
                self.breadcrumbs.pop()
                return

            # Load user data based on user type
            if user_type == "patient":
                user_data = read_json("../data/patient_info.json")
                user_info = next((u for u in user_data if str(u["patient_id"]) == user_id), None)
            elif user_type == "mhwp":
                user_data = read_json("../data/mhwp_info.json")
                user_info = next((u for u in user_data if str(u["mhwp_id"]) == user_id), None)

            if not user_info:
                print(f"{Red}User ID {user_id} not found. Returning to the Admin Menu...{Reset}")
                self.breadcrumbs.pop()
                return

            # Show current user information
            self.print_centered_message("Current User Information", f"{Blue}{Bold}")
            print(f"{Blue}-" * 55 + f"{Reset}")
            for key, value in user_info.items():
                print(f"{key}: {value}{Reset}")
            print(f"{Blue}-" * 55 + f"{Reset}")

            # Collect fields to edit for patients and MHWPs
            new_data = {}

            # Get first name and last name separately, combine them into 'name' field
            new_first_name = self.get_user_input(f"{Cyan}{Italic}Enter new first name (leave blank to keep current):{Reset} ").strip()
            new_last_name = self.get_user_input(f"{Cyan}{Italic}Enter new last name (leave blank to keep current):{Reset} ").strip()
            if new_first_name or new_last_name:
                current_name = user_info.get("name", "")
                first_name, last_name = current_name.split(' ', 1) if ' ' in current_name else (current_name, "")
                first_name = new_first_name.capitalize() if new_first_name else first_name
                last_name = new_last_name.capitalize() if new_last_name else last_name
                new_data["name"] = f"{first_name} {last_name}"

            # Get email
            new_email = self.get_user_input(f"{Cyan}{Italic}Enter new email (leave blank to keep current):{Reset} ").strip()
            if new_email:
                new_data["email"] = new_email

            # Get emergency contact email for patients
            if user_type == "patient":
                new_emergency_contact_email = self.get_user_input(
                    f"{Cyan}{Italic}Enter new emergency contact email (leave blank to keep current):{Reset} ").strip()
                if new_emergency_contact_email:
                    new_data["emergency_contact_email"] = new_emergency_contact_email

            # Confirmation step before making changes
            confirm = self.get_user_input(f"{Yellow}Are you sure you want to apply these changes? (y/n):{Reset} ").strip().lower()
            if confirm != 'y':
                print(f"{Cyan}Edit operation cancelled. Returning to Admin Menu...{Reset}")
                self.breadcrumbs.pop()
                return

            # Create user object and call edit_user
            if user_type == "patient":
                user = Patient(user_id, user_info.get("name"), user_info.get("email"))
            elif user_type == "mhwp":
                user = MHWP(user_id, user_info.get("name"), user_info.get("email"))

            # Perform the edit operation
            self.edit_user(user, new_data)
            print(f"{Green}User {user_id} edited successfully.{Reset}")

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

    def disable_user_menu(self):
        self.update_breadcrumbs("Disable User")
        self.show_breadcrumbs()
        try:
            user_type = self.get_user_input(f"{Cyan}{Italic}Enter user type (patient/mhwp): {Reset}")
            if user_type.lower() not in ["patient", "mhwp"]:
                raise ValueError("Invalid user type. Must be 'patient' or 'mhwp'.")
            user_id = self.get_user_input(f"{Cyan}{Italic}Enter User ID: {Reset}")
            if not user_id:
                raise ValueError("User ID cannot be empty.")
            if user_type.lower() == "patient":
                user = Patient(user_id, f"patient{user_id}", "")
            elif user_type.lower() == "mhwp":
                user = MHWP(user_id, f"mhwp{user_id}", "")
            self.disable_user(user)
            print(f"User {user_id} has been disabled.")
        except ValueError as ve:
            print(f"Input Error: {ve}")
        except Exception as e:
            print(f"Error occurred: {e}")
        finally:
            self.breadcrumbs.pop()

    def delete_user_menu(self):
        self.update_breadcrumbs("Delete User")
        self.show_breadcrumbs()
        try:
            user_type = self.get_user_input(f"{Cyan}{Italic}Enter user type (patient/mhwp): {Reset}")
            if user_type.lower() not in ["patient", "mhwp"]:
                raise ValueError("Invalid user type. Must be 'patient' or 'mhwp'.")
            user_id = self.get_user_input(f"{Cyan}{Italic}Enter User ID: {Reset}")
            if not user_id:
                raise ValueError("User ID cannot be empty.")
            if user_type.lower() == "patient":
                user = Patient(user_id, f"patient{user_id}", "")
            elif user_type.lower() == "mhwp":
                user = MHWP(user_id, f"mhwp{user_id}", "")
            self.delete_user(user)
            print(f"User {user_id} deleted successfully.")
        except ValueError as ve:
            print(f"Input Error: {ve}")
        except Exception as e:
            print(f"Error occurred: {e}")
        finally:
            self.breadcrumbs.pop()


if __name__ == "__main__":
    admin_user = Admin(1, "admin", "")
    admin_controller = AdminController(admin_user)
    admin_controller.display_menu()

# a = Admin(1,"tim","")
# p = Patient(1,"bob","")
# m = MHWP(1, "dr", "")

# ac = AdminController(a)
# ac.delete_user(m)
