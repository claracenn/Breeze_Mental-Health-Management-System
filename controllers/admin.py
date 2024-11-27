import pandas as pd
import json
import logging
import os
from datetime import datetime
from models.user import Admin, MHWP, Patient
from utils.display_manager import DisplayManager
from utils.data_handler import *

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
LIGHT_YELLOW = "\033[93m"
ITALIC = "\033[3m"
ORANGE = "\033[1;33m"  


"""
==================================
MHWP Controller Class
==================================
"""
# ----------------------------
# Homepage and Menus
# ----------------------------
class AdminController:
    def __init__(self, admin):
        self.admin = admin
        self.display_manager = DisplayManager()
        self.appointment_file = "./data/appointment.json"
        self.mhwp_info = "./data/mhwp_info.json"
        self.journal_file = "./data/patient_journal.json"
        self.mood_file = "./data/patient_mood.json"
        self.patient_info_file = "./data/patient_info.json"
        self.patient_record_file = "./data/patient_record.json"
        self.request_log_file = "./data/request_log.json"
        self.mhwp_info_file = "./data/mhwp_info.json"
        self.feedback_file = "./data/feedback.json"
        self.user_info_file = "./data/user.json"
    
    def display_admin_homepage(self):
        title = "🏠 Admin Homepage"
        main_menu_title = "🏠 Admin Homepage"
        options = ["Allocate Patient to MHWP",
                   "Edit User Info",
                   "Disable or Enable User",
                   "Delete User",
                   "Resolve Requests",
                   "Display Summary",
                   "Logout"]
        action_map = {
            "1": self.allocate_patient,
            "2": self.edit_user_info_menu,
            "3": self.disable_enable_user_menu,
            "4": self.delete_user_menu,
            "5": self.resolve_request,
            "6": self.display_summary,
            "7": lambda: None
        }
        self.display_manager.navigate_menu(title, options, action_map, main_menu_title)
    
    def edit_user_info_menu(self):
        title = "🖊️  Edit User"
        main_menu_title = "🏠 Admin Homepage"
        options = ["Edit MHWP",
                   "Edit Patient",
                   "Back to Homepage"]
        action_map = {
            "1": self.edit_mhwp,
            "2": self.edit_patient,
            "3": lambda: None
        }
        result = self.display_manager.navigate_menu(title, options, action_map, main_menu_title)
        if result == "main_menu":
            self.display_admin_homepage()

    def disable_enable_user_menu(self):
        title = "🙅 Disable User"
        main_menu_title = "🏠 Admin Homepage"
        options = ["Disable MHWP",
                   "Disable Patient",
                   "Enable MHWP",
                   "Enable Patient",
                   "Back to Homepage"]
        action_map = {
            "1": self.disable_mhwp,
            "2": self.disable_patient,
            "3": self.enable_mhwp,
            "4": self.enable_patient,
            "5": lambda: None
        }
        result = self.display_manager.navigate_menu(title, options, action_map, main_menu_title)
        if result == "main_menu":
            self.display_admin_homepage()
    
    def delete_user_menu(self):
        title = "🗑️ Delete User"
        main_menu_title = "🏠 Admin Homepage"
        options = ["Delete MHWP",
                   "Delete Patient",
                   "Back to Homepage"]
        action_map = {
            "1": self.delete_mhwp,
            "2": self.delete_patient,
            "3": lambda: None
        }
        result = self.display_manager.navigate_menu(title, options, action_map, main_menu_title)
        if result == "main_menu":
            self.display_admin_homepage()


# ----------------------------
# Common Functions
# ----------------------------
    def is_integer(self, value):
        '''
        Checks if the given value can be safely converted to an integer for user input sanitation.
        Args: value, The value to check.
            
        Returns: bool, True if the value is an integer, False otherwise.
        '''
        if isinstance(value,int): return True

        try:
            value = value.strip()
            int(value)  # Try converting to an integer
            return True
        except (ValueError, TypeError):
            return False

    def display_patient_info(self):
        '''
        Retrieves patient info from the data files.
        Returns data table if found, None otherwise.
        '''
        data_path = self.patient_info_file

        patient_info = read_json(data_path)
        if patient_info is None or not isinstance(patient_info, list):
            print(f"{RED}Error: Failed to read valid data from {data_path}")
            return None
        else:
            data = {
            "Patient ID": [p.get("patient_id", None) for p in patient_info],
            "Name": [p.get("name", None) for p in patient_info],
            "Email": [p.get("email", None) for p in patient_info],
            "Emergency Contact Email": [p.get("emergency_contact_email", None) for p in patient_info],
            "MHWP ID": [p.get("mhwp_id", None) for p in patient_info],
            }
            if data["Patient ID"]:
                create_table(data, "Patient Information", display_title=True, display_index=True)
                return data
    
    def display_mhwp_info(self):
        '''
        Retrieves MHWP info from the data files.
        Returns data table if found, None otherwise.
        '''
        data_path = self.mhwp_info_file

        mhwp_info = read_json(data_path)
        if mhwp_info is None or not isinstance(mhwp_info, list):
            print(f"{RED}Error: Failed to read valid data from {data_path}")
            return None
        else:
            data = {
            "MHWP ID": [m.get("mhwp_id", None) for m in mhwp_info],
            "Name": [m.get("name", None) for m in mhwp_info],
            "Email": [m.get("email", None) for m in mhwp_info],
            "Patient Count": [m.get("patient_count", None) for m in mhwp_info],
            }
            if data["MHWP ID"]:
                create_table(data, "MHWP Information", display_title=True, display_index=True)
                return data
            
    def display_request_info(self):
        '''
        Retrieves request info from the data files.
        Returns data table if found, None otherwise.
        '''

        data_path = self.request_log_file
        request_info = read_json(data_path)
        requests_sorted = sorted(request_info, key=lambda x: datetime.strptime(x["requested_at"], "%Y-%m-%d %H:%M:%S"), reverse=True)

        if requests_sorted is None or not isinstance(requests_sorted, list):
            print(f"{RED}Error: Failed to read valid data from {data_path}")
            return None
        else:
            # Step 3: Create the final data dictionary
            data = {
                "Patient ID": [r.get("user_id", None) for r in request_info],
                "Current MHWP ID": [r.get("current_mhwp_id") for r in request_info],
                "Target MHWP ID": [r.get("target_mhwp_id") for r in request_info],
                "Reason": [r.get("reason") for r in request_info],
                "Status": [r.get("status") for r in request_info],
                "Requested At": [r.get("requested_at") for r in request_info]
            }
            if data["Patient ID"]:
                create_table(data, "Request Log Information", display_title=True, display_index=True)
                return data
            
    def check_request_is_not_pending(self, index):

        data_path = self.request_log_file
        request_info = read_json(data_path)

        specific_request = request_info[index]
        status = specific_request["status"]

        if status.lower() != "pending":
            return True
        
        return False

    @staticmethod
    def calculate_patient_counts(patient_file, mhwp_file):
        """
        Calculate the number of patients assigned to each MHWP and update the patient_count field in mhwp_file.
        :param patient_file: The file path to the JSON file containing patient information.
        :param mhwp_file: The file path to the JSON file containing MHWP information.
        """
        patients = read_json(patient_file)
        mhwp_data = read_json(mhwp_file)

        mhwp_patient_counts = {}
        
        # Count the number of patients assigned to each MHWP
        for patient in patients:
            mhwp_id = patient.get("mhwp_id")
            if mhwp_id not in mhwp_patient_counts:
                mhwp_patient_counts[mhwp_id] = 0
            else:
                mhwp_patient_counts[mhwp_id] += 1

        # Update mhwp_data with patient counts
        for mhwp in mhwp_data:
            mhwp_id = mhwp.get("mhwp_id")
            mhwp["patient_count"] = mhwp_patient_counts.get(mhwp_id, 0)

        save_json(mhwp_file, mhwp_data)
        return mhwp_data

# ----------------------------
# Section 1: Allocate Patient
# ----------------------------
    def allocate_patient(self):
        # Display patient data
        patient_data = self.display_patient_info()
        
        # Ask for Patient ID to allocate
        retry_attempts = 0
        while retry_attempts < 3:
            input_patient_id = input(f"{CYAN}{BOLD}Enter Patient ID to allocate ⏳: {RESET}").strip()
            if input_patient_id == "back":
                self.display_manager.back_operation()
                self.display_admin_homepage()
                return
            
            # Validate if input is an integer
            if not self.is_integer(input_patient_id):
                retry_attempts += 1
                print(f"{RED}Invalid input. Please enter an interger.{RESET}")
                continue
            
            # Check if the input patient ID exists and proceed to allocate
            input_patient_id = int(input_patient_id)
            if input_patient_id in patient_data.get("Patient ID", []):
                print(f"{GREEN}Patient ID {input_patient_id} found. Proceeding to assign an MHWP...{RESET}")
                break
            else:
                retry_attempts += 1
                print(f"{RED}Patient ID '{input_patient_id}' not found. Please try again.{RESET}")
            
        if retry_attempts == 3:
            print(f"{RED}You have exceeded the maximum number of attempts. Returning to the Admin Menu...{RESET}")
            self.display_manager.back_operation()
            self.display_admin_homepage()
            return

        # Display MHWP data
        mhwp_data = self.display_mhwp_info()

        # Ask for MHWP ID to allocate
        retry_attempts = 0
        while retry_attempts < 3:
            input_mhwp_id = input(f"{CYAN}{BOLD}Enter MHWP ID to allocate ⏳: {RESET}").strip()
            if input_mhwp_id == "back":
                self.display_manager.back_operation()
                self.display_admin_homepage()
                return
            
            # Validate if input is an integer
            if not self.is_integer(input_mhwp_id):
                retry_attempts += 1
                print(f"{RED}Invalid input. Please enter an interger.{RESET}")
                continue

            # Check if the input MHWP ID exists and proceed to allocate
            input_mhwp_id = int(input_mhwp_id)
            if input_mhwp_id in mhwp_data.get("MHWP ID", []):
                # Check if the MHWP is already assigned to the patient
                patient_entry = next((p for p in patient_data if p["Patient ID"] == input_patient_id), None)
                if patient_entry.get("mhwp_id") == input_mhwp_id:
                    retry_attempts += 1
                    print(f"{RED}Patient ID {input_patient_id} is already assigned to MHWP ID {input_mhwp_id}.{RESET}")
                # If not assigned to the same MHWP, proceed to update               
                update_entry(self.patient_info_file, input_patient_id, {"mhwp_id": input_mhwp_id})
                print(f"{GREEN}MHWP ID {input_mhwp_id} found. Successfully assigned Patient {input_patient_id} to MHWP {input_mhwp_id}! {RESET}")
                self.calculate_patient_counts(self.patient_info_file, self.mhwp_info_file)
                break

            else:
                retry_attempts += 1
                print(f"{RED}MHWP ID '{input_mhwp_id}' not found. Please try again.{RESET}")
            
        if retry_attempts == 3:
            print(f"{RED}You have exceeded the maximum number of attempts. Returning to the Admin Menu...{RESET}")
            self.display_manager.back_operation()
            self.display_admin_homepage()
            return

# ----------------------------
# Section 2: Edit User Info
# ----------------------------
    def edit_mhwp(self):
        # Display MHWP info
        self.display_mhwp_info()
        data = read_json(self.mhwp_info_file)

        while True:
            input_mhwp_id = input(f"{CYAN}{BOLD}Enter MHWP ID to edit ⏳: {RESET}").strip()
            if input_mhwp_id == "back":
                self.display_manager.back_operation()
                self.edit_user_info_menu()
                return
        
            # Validate if input is an integer
            if not self.is_integer(input_mhwp_id):
                print(f"{RED}Invalid input. Please enter an interger.{RESET}")
                continue
            
            input_mhwp_id = int(input_mhwp_id)
            for mhwp in data:
                # Check if the input MHWP ID exists and proceed to edit
                if mhwp["mhwp_id"] == input_mhwp_id:
                    print(f"\n{BOLD}📃 Edit MHWP {input_mhwp_id} information:")
                    while True:
                        # Display a simple menu for editing mhwp data
                        print(f"{BOLD}{MAGENTA}\nSelect the field you want to edit:{RESET}")
                        print(f"1. Name (current: {mhwp['name']})")
                        print(f"2. Email (current: {mhwp['email']})")
                        print(f"3. Edit All")
                        print(f"4. Back to Edit User Info Menu")

                        # Get user input and handle it
                        choice = input(f"{CYAN}{BOLD}Choose an option ⏳: {RESET}").strip()
                        if choice == "back":
                            self.edit_mhwp()
                            return
                        if choice == "1":
                            new_name = input(f"{CYAN}{BOLD}Enter new name: {RESET}").strip()
                            if new_name == "back":
                                self.display_manager.back_operation()
                                self.edit_user_info_menu()
                                return
                            if new_name:
                                mhwp["name"] = new_name
                                print(f"{GREEN}Name updated successfully!{RESET}")
                        elif choice == "2":
                            new_email = input(f"{CYAN}{BOLD}Enter new email: {RESET}").strip()
                            if new_email == "back":
                                self.display_manager.back_operation()
                                self.edit_user_info_menu()
                                return
                            if new_email:
                                mhwp["email"] = new_email
                                print(f"{GREEN}Email updated successfully!{RESET}")
                        elif choice == "3":
                            new_name = input(f"{CYAN}{BOLD}Enter new name: {RESET}").strip()
                            if new_name == "back":
                                self.display_manager.back_operation()
                                self.edit_user_info_menu()
                                return
                            if new_name:
                                mhwp["name"] = new_name
                            new_email = input(f"{CYAN}{BOLD}Enter new email: {RESET}").strip()
                            if new_email == "back":
                                self.display_manager.back_operation()
                                self.edit_user_info_menu()
                                return
                            if new_email:
                                mhwp["email"] = new_email
                            print(f"{GREEN}All fields updated successfully!{RESET}")
                        elif choice == "4":
                            self.display_manager.back_operation()
                            self.edit_user_info_menu()
                            break
                        else:
                            print(f"{RED}Invalid choice. Please try again.")

                    # Save the updated data
                    save_json(self.mhwp_info_file, data)

            # If MHWP ID not found
            else:
                print(f"{RED}MHWP ID '{input_mhwp_id}' not found. Please try again.{RESET}")


    def edit_patient(self):
        # Display patient info
        self.display_patient_info()
        data = read_json(self.patient_info_file)
        
        while True:
            input_patient_id = input(f"{CYAN}{BOLD}Enter Patient ID to edit ⏳: {RESET}").strip()
            if input_patient_id == "back":
                self.display_manager.back_operation()
                self.edit_user_info_menu()
                return
        
            # Validate if input is an integer
            if not self.is_integer(input_patient_id):
                print(f"{RED}Invalid input. Please enter an interger.{RESET}")
                continue
                    
            input_patient_id = int(input_patient_id)
            for patient in data:
                # Check if the input MHWP ID exists and proceed to edit
                if patient["patient_id"] == input_patient_id:
                    print(f"\n{BOLD}📃 Edit Patient {input_patient_id} information:")
                    while True:
                        # Display a simple menu for editing mhwp data
                        print(f"{BOLD}{MAGENTA}\nSelect the field you want to edit:{RESET}")
                        print(f"1. Name (current: {patient['name']})")
                        print(f"2. Email (current: {patient['email']})")
                        print(f"3. Emergency Contact Email (current: {patient['emergency_contact_email']})")
                        print(f"4. Edit All")
                        print(f"5. Back to Edit User Info Menu")

                        # Get user input and handle it
                        choice = input(f"{CYAN}{BOLD}Choose an option ⏳: {RESET}").strip()
                        if choice == "back":
                            self.edit_patient()
                            return
                        # Edit Name
                        if choice == "1":
                            new_name = input(f"{CYAN}{BOLD}Enter new name: {RESET}").strip()
                            if new_name == "back":
                                self.display_manager.back_operation()
                                self.edit_user_info_menu()
                                return
                            if new_name:
                                patient["name"] = new_name
                                print(f"{GREEN}Name updated successfully!{RESET}")
                        # Edit Email
                        elif choice == "2":
                            new_email = input(f"{CYAN}{BOLD}Enter new email: {RESET}").strip()
                            if new_email == "back":
                                self.display_manager.back_operation()
                                self.edit_user_info_menu()
                                return
                            if new_email:
                                patient["email"] = new_email
                                print(f"{GREEN}Email updated successfully!{RESET}")
                        # Edit Emergency Contact Email
                        elif choice == "3":
                            new_emergency_contact_email = input(f"{CYAN}{BOLD}Enter new emergency contact email: {RESET}").strip()
                            if new_emergency_contact_email == "back":
                                self.display_manager.back_operation()
                                self.edit_user_info_menu()
                                return
                            if new_emergency_contact_email:
                                patient["emergency_contact_email"] = new_emergency_contact_email
                                print(f"{GREEN}Emergency contact email updated successfully!{RESET}")
                        # Edit All
                        elif choice == "4":
                            new_name = input(f"{CYAN}{BOLD}Enter new name: {RESET}").strip()
                            if new_name == "back":
                                self.display_manager.back_operation()
                                self.edit_user_info_menu()
                                return
                            if new_name:
                                patient["name"] = new_name
                            new_email = input(f"{CYAN}{BOLD}Enter new email: {RESET}").strip()
                            if new_email == "back":
                                self.display_manager.back_operation()
                                self.edit_user_info_menu()
                                return
                            if new_email:
                                patient["email"] = new_email
                            new_emergency_contact_email = input(f"{CYAN}{BOLD}Enter new emergency contact email: {RESET}").strip()
                            if new_emergency_contact_email == "back":
                                self.display_manager.back_operation()
                                self.edit_user_info_menu()
                                return
                            if new_emergency_contact_email:
                                patient["emergency_contact_email"] = new_emergency_contact_email
                            print(f"{GREEN}All fields updated successfully!{RESET}")
                        # Back to Edit User Info Menu
                        elif choice == "5":
                            print(f"{GREY}Returning to Profile Menu.")
                            self.display_manager.back_operation()
                            self.edit_user_info_menu()
                            break
                        else:
                            print(f"{RED}Invalid choice. Please try again.")

                    # Save the updated data
                    save_json(self.patient_info_file, data)
                    update_entry(self.patient_record_file, input_patient_id, {"name": new_name})
                    break

            # If MHWP ID not found
            else:
                print(f"{RED}Patient ID '{input_patient_id}' not found. Please try again.{RESET}")


# ----------------------------
# Section 3: Disable/Enable User
# ----------------------------
    def disable_mhwp(self):
        print("Developing...")

    def disable_patient(self):
        print("Developing...")

    def enable_mhwp(self):
        print("Developing...")

    def enable_patient(self):
        print("Developing...")

# ----------------------------
# Section 4: Delete User
# ----------------------------
    def delete_mhwp(self):
        print("Developing...")

    def delete_patient(self):
        print("Developing...")

# ----------------------------
# Section 5: Resolve Requests
# ----------------------------
    def resolve_request(self):

        self.display_request_info()
        request_data = read_json(self.request_log_file)

        # Ask for Patient ID to allocate
        retry_attempts = 0
        while retry_attempts < 3:
            row = input(f"{CYAN}{BOLD}Enter the row of the request you would like to resolve ✅: {RESET}").strip()
            if row == "back":
                self.display_manager.back_operation()
                self.display_admin_homepage()
                return
            
            # Validate if input is an integer
            if not self.is_integer(row):
                retry_attempts += 1
                print(f"{RED}Invalid input. Please enter an integer.{RESET}")
                continue
            
            row = int(row)
            # Check if the input patient ID exists and proceed to allocate
            if not (row < len(request_data) and row > 0):
                retry_attempts += 1
                print(f"{RED}Row not found. Please try again.{RESET}")
                continue
            
            # Check if the input patient ID exists and proceed to allocate
            index = int(row) - 1

            if self.check_request_is_not_pending(index):
                retry_attempts += 1
                print(f"{RED}Please select a request with a pending status.{RESET}")
                continue

            specific_record_info = request_data[index]

            while True:
                # Display a simple menu for editing mhwp data
                print(f"{BOLD}{MAGENTA}\nResolve patient {specific_record_info['user_id']}'s request:{RESET}")
                print(f"1. Approve request")
                print(f"2. Reject request")
                print(f"3. Back to Homepage")
        
                # Get user input and handle it
                choice = input(f"{CYAN}{BOLD}Choose an option ⏳: {RESET}").strip()
                if choice == "back" or choice == "3":
                    self.display_admin_homepage()
                    return
                
                # Approve request
                if choice == "1":
                    request_data[index]['status'] = "Approved"
                    save_json(self.request_log_file, request_data)
                    patient_id = request_data[index]['user_id']
                    target_MHWP_id = request_data[index]['target_mhwp_id']
                    current_MHWP_id = request_data[index]['current_mhwp_id']

                    #update patient file to new MHWP           
                    update_entry(self.patient_info_file, patient_id, {"mhwp_id": target_MHWP_id})
                    print(f"{GREEN}Request settled. MHWP ID {current_MHWP_id} found. Successfully assigned Patient {patient_id} to MHWP {target_MHWP_id}! {RESET}")
                    self.calculate_patient_counts(self.patient_info_file, self.mhwp_info_file)
                    self.display_admin_homepage()
                    return

                elif choice == "2":
                    request_data[index]['status'] = "Rejected"
                    save_json(self.request_log_file, request_data)
                    self.display_admin_homepage()
                    return
                
                else:
                    retry_attempts += 1
                    print(f"{RED}That is an invalid input. Please follow the instructions...{RESET}")

                    if retry_attempts == 3:
                        print(f"{RED}You have exceeded the maximum number of attempts. Returning to the Admin Menu...{RESET}")
                        self.display_manager.back_operation()
                        self.display_admin_homepage()
                        return
                
        if retry_attempts == 3:
            print(f"{RED}You have exceeded the maximum number of attempts. Returning to the Admin Menu...{RESET}")
            self.display_manager.back_operation()
            self.display_admin_homepage()
            return

# ----------------------------
# Section 6: Display Summary
# ----------------------------
    def display_summary(self):
        print("Developing...")


    
# give test of allocate patient to mhwp
if __name__ == "__main__":
    admin = Admin(1, "admin", "ACTIVE")
    admin_controller = AdminController(admin)
    admin_controller.display_admin_homepage()