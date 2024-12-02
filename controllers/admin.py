import pandas as pd
import json
import logging
import os
from datetime import datetime, timedelta
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
Admin Controller Class
==================================
"""
class AdminController:
    def __init__(self, admin):
        self.admin = admin
        self.display_manager = DisplayManager()


# ----------------------------
# Homepage and Menus
# ----------------------------
    def display_admin_homepage(self):
        title = "🏠 Admin Homepage"
        main_menu_title = "🏠 Admin Homepage"
        options = ["Allocate Patient to MHWP",
                   "Resolve Patient Requests",
                   "Edit User Info",
                   "Disable or Enable User",
                   "Delete User",
                   "Display Summary",
                   "Logout"]
        action_map = {
            "1": self.allocate_patient,
            "2": self.resolve_request,
            "3": self.edit_user_info_menu,
            "4": self.disable_enable_user_menu,
            "5": self.delete_user_menu,
            "6": self.display_summary_menu,
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
        title = "🙋 Disable/Enable User"
        main_menu_title = "🏠 Admin Homepage"
        options = ["Disable MHWP",
                   "Disable Patient",
                   "Enable MHWP",
                   "Enable Patient",
                   "Back to Homepage"]
        action_map = {
            "1": lambda: self.disable_user("mhwp"),
            "2": lambda: self.disable_user("patient"),
            "3": lambda: self.enable_user("mhwp"),
            "4": lambda: self.enable_user("patient"),
            "5": lambda: None  # Left it as None for going back
        }
        result = self.display_manager.navigate_menu(title, options, action_map, main_menu_title)
        if result == "main_menu":
            self.display_admin_homepage()
    
    def delete_user_menu(self):
        title = "🗑️  Delete User"
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
    
    def display_summary_menu(self):
        title = "📊 Display Summary"
        main_menu_title = "🏠 Admin Homepage"
        options = [
            "View Patients Summary",
            "View MHWPs Summary",
            "View Allocations",
            "View Weekly Confirmed Bookings",
            "Back to Homepage"
        ]
        action_map = {
            "1": self.view_patients_summary,
            "2": self.view_mhwps_summary,
            "3": self.view_allocations_summary,
            "4": self.view_weekly_bookings_summary,
            "5": lambda: None  
        }
        self.display_manager.navigate_menu(title, options, action_map, main_menu_title)


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
        data_path = "./data/patient_info.json"

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
                create_table(data, "Patient Information", display_title=True, display_index=False)
                return data
    
    def display_mhwp_info(self):
        '''
        Retrieves MHWP info from the data files.
        Returns data table if found, None otherwise.
        '''
        data_path = "./data/mhwp_info.json"

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
                create_table(data, "MHWP Information", display_title=True, display_index=False)
                return data
     
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
            if mhwp_id is not None:
                mhwp_patient_counts[mhwp_id] = mhwp_patient_counts.get(mhwp_id, 0) + 1

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
                patient_index = next((i for i, id_ in enumerate(patient_data["Patient ID"]) if id_ == input_patient_id), None)
                if patient_index is not None:
                    patient_entry = {key: patient_data[key][patient_index] for key in patient_data}
                if patient_entry.get("mhwp_id") == input_mhwp_id:
                    retry_attempts += 1
                    print(f"{RED}Patient ID {input_patient_id} is already assigned to MHWP ID {input_mhwp_id}.{RESET}")
                    continue
                # If not assigned to the same MHWP, proceed to update               
                update_entry("./data/patient_info.json", input_patient_id, {"mhwp_id": input_mhwp_id})
                print(f"{GREEN}MHWP ID {input_mhwp_id} found. Successfully assigned Patient {input_patient_id} to MHWP {input_mhwp_id}! {RESET}")
                self.calculate_patient_counts("./data/patient_info.json", "./data/mhwp_info.json")
                break

            else:
                retry_attempts += 1
                print(f"{RED}MHWP ID '{input_mhwp_id}' not found. Please try again.{RESET}")
            
        if retry_attempts == 3:
            print(f"{RED}You have exceeded the maximum number of attempts. Returning to the Admin Menu...{RESET}")
            self.display_manager.back_operation()
            self.display_admin_homepage()
            return


# ----------------------------------
# Section 2: Resolve Patient Requests
# ----------------------------------
    def display_request_info(self):
        """Retrieve and display request information"""
        request_info = read_json("./data/request_log.json")
        requests_sorted = sorted(request_info, key=lambda x: datetime.strptime(x["requested_at"], "%Y-%m-%d %H:%M:%S"), reverse=True)

        if requests_sorted is None or not isinstance(requests_sorted, list):
            print(f"{RED}Error: Failed to read valid data.")
            return None
        else:
            data = {
                "Patient ID": [r.get("patient_id", None) for r in request_info],
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
        """ Check if the request is not pending"""
        request_info = read_json("./data/request_log.json")

        specific_request = request_info[index-1]
        status = specific_request["status"]

        if status != "pending":
            return True
        return False


    def resolve_request(self):
        """ Resolve patient requests of changing MHWP """
        self.display_request_info()
        request_data = read_json("./data/request_log.json")

        # Ask for Patient ID to allocate
        retry_attempts = 0
        while retry_attempts < 3:
            input_index = input(f"{CYAN}{BOLD}Enter the index of the request you would like to resolve ⏳: {RESET}").strip()
            if input_index == "back":
                self.display_manager.back_operation()
                self.display_admin_homepage()
                return
            
            # Validate if input is an integer
            if not self.is_integer(input_index):
                retry_attempts += 1
                print(f"{RED}Invalid input. Please enter an integer.{RESET}")
                continue
            
            input_index = int(input_index)
            # Check if the input patient ID exists and proceed to allocate
            if not (input_index <= len(request_data) and input_index > 0):
                retry_attempts += 1
                print(f"{RED}Index not found. Please try again.{RESET}")
                continue

            if self.check_request_is_not_pending(input_index):
                retry_attempts += 1
                print(f"{RED}Please select a request with a pending status.{RESET}")
                continue

            specific_record_info = request_data[input_index-1]

            while True:
                # Display a simple menu for editing mhwp data
                print(f"{BOLD}{MAGENTA}\nResolve Patient {specific_record_info['patient_id']}'s request:{RESET}")
                print(f"1. Approve request")
                print(f"2. Reject request")
                print(f"3. Back to Homepage")
        
                # Get user input and handle it
                choice = input(f"{CYAN}{BOLD}Choose an option ⏳: {RESET}").strip()

                # Back to Homepage
                if choice == "back" or choice == "3":
                    self.back_operation()
                    self.display_admin_homepage()
                    return
                
                # Approve request
                if choice == "1":
                    request_data[input_index-1]['status'] = "approved"
                    save_json("./data/request_log.json", request_data)
                    patient_id = request_data[input_index-1]['patient_id']
                    target_MHWP_id = request_data[input_index-1]['target_mhwp_id']

                    #update patient file to new MHWP           
                    update_entry("./data/patient_info.json", patient_id, {"mhwp_id": target_MHWP_id})
                    print(f"{GREEN}Request settled. Successfully assigned Patient {patient_id} to MHWP {target_MHWP_id}! {RESET}")
                    self.calculate_patient_counts("./data/patient_info.json", "./data/mhwp_info.json")
                    return

                # Reject request
                elif choice == "2":
                    request_data[input_index-1]['status'] = "rejected"
                    patient_id = request_data[input_index-1]['patient_id']
                    print(f"{RED}Request settled. Rejected Patient {patient_id}'s request. {RESET}")
                    save_json("./data/request_log.json", request_data)
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
# Section 3: Edit User Info
# ----------------------------
    def edit_mhwp(self):
        # Display MHWP info
        self.display_mhwp_info()
        data = read_json("./data/mhwp_info.json")

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
            mhwp_found = False
            for mhwp in data:
                # Check if the input MHWP ID exists and proceed to edit
                if mhwp["mhwp_id"] == input_mhwp_id:
                    mhwp_found = True
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
                    save_json("./data/mhwp_info.json", data)

            # If MHWP ID not found
            if mhwp_found == False:
                print(f"{RED}MHWP ID '{input_mhwp_id}' not found. Please try again.{RESET}")


    def edit_patient(self):
        # Display patient info
        self.display_patient_info()
        data = read_json("./data/patient_info.json")
        
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
            patient_found = False
            for patient in data:
                # Check if the input MHWP ID exists and proceed to edit
                if patient["patient_id"] == input_patient_id:
                    patient_found = True
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
                    save_json("./data/patient_info.json", data)
                    update_entry("./data/patient_record.json", input_patient_id, {"name": new_name})
                    break

            # If MHWP ID not found
            if patient_found == False:
                print(f"{RED}Patient ID '{input_patient_id}' not found. Please try again.{RESET}")


# ----------------------------
# Section 4: Disable/Enable User
# ----------------------------
    def disable_user(self, role):
        # Read data 
        data = read_json('./data/user.json')
        if data is None or not isinstance(data, list):
            print(f"{RED}Error: Failed to read valid data.")
            return None
        
        else:
            # Display active account
            if role == "mhwp":
                active_data = [
                    {"user_id": d.get("user_id"), "username": d.get("username"), "status": d.get("status")}
                    for d in data
                    if d.get("status") == "ACTIVE" and d.get("role") == "mhwp"
                ]
                title = "Active MHWP Accounts"
            elif role == "patient":
                active_data = [
                    {"user_id": d.get("user_id"), "username": d.get("username"), "status": d.get("status")}
                    for d in data
                    if d.get("status") == "ACTIVE" and d.get("role") == "patient"
                ]
                title = "Active Patient Accounts"
            else:
                print(f"{RED}Invalid role provided.{RESET}")
                return None
            
            if active_data:
                table_data = {
                    "User ID": [d["user_id"] for d in active_data],
                    "Username": [d["username"] for d in active_data],
                    "Status": [d["status"] for d in active_data],
                }
                create_table(table_data, title, display_title=True, display_index=False)
            else:
                print(f"{RED}No active accounts found for the selected role.{RESET}")
                return None
            
        # User input loop to disable account
        while True:
            selected_user_id = input(f"{CYAN}{BOLD}Enter the ID of the user to disable: {RESET}").strip()
            if selected_user_id == "back":
                self.display_manager.back_operation()
                self.disable_enable_user_menu()
                return
            
            # Validate if input user id is integer
            if not self.is_integer(selected_user_id):
                print(f"{RED}Invalid input. Please enter an interger.{RESET}")
                continue

            # Update status
            selected_user_id = int(selected_user_id)
            for user in active_data:
                if user["user_id"] == selected_user_id:
                    update_entry('./data/user.json', selected_user_id, {"status": "DISABLED"})
                    print(f"{GREEN}User with ID {selected_user_id} has been successfully disabled.{RESET}")
                    return
            else:
                print(f"{RED}Account with ID '{selected_user_id}' not found. Please try again.{RESET}")


    def enable_user(self, role):
        # Read data 
        data = read_json('./data/user.json')
        if data is None or not isinstance(data, list):
            print(f"{RED}Error: Failed to read valid data.")
            return None
        
        else:
            # Display disabled account
            if role == "mhwp":
                disabled_data = [
                    {"user_id": d.get("user_id"), "username": d.get("username"), "status": d.get("status")}
                    for d in data
                    if d.get("status") == "DISABLED" and d.get("role") == "mhwp"
                ]
                title = "Disabled MHWP Accounts"
            elif role == "patient":
                disabled_data = [
                    {"user_id": d.get("user_id"), "username": d.get("username"), "status": d.get("status")}
                    for d in data
                    if d.get("status") == "DISABLED" and d.get("role") == "patient"
                ]
                title = "Disabled Patient Accounts"
            else:
                print(f"{RED}Invalid role provided.{RESET}")
                return None
            
            if disabled_data:
                table_data = {
                    "User ID": [d["user_id"] for d in disabled_data],
                    "Username": [d["username"] for d in disabled_data],
                    "Status": [d["status"] for d in disabled_data],
                }
                create_table(table_data, title, display_title=True, display_index=False)
            else:
                print(f"{RED}No disabled accounts found for the selected role.{RESET}")
                return None
            
        # User input loop to enable account
        while True:
            selected_user_id = input(f"{CYAN}{BOLD}Enter the ID of the user to enable: {RESET}").strip()
            if selected_user_id == "back":
                self.display_manager.back_operation()
                self.disable_enable_user_menu()
                return
            
            # Validate if input user id is integer
            if not self.is_integer(selected_user_id):
                print(f"{RED}Invalid input. Please enter an interger.{RESET}")
                continue

            # Update status
            selected_user_id = int(selected_user_id)
            for user in disabled_data:
                if user["user_id"] == selected_user_id:
                    user_found = True
                    update_entry('./data/user.json', selected_user_id, {"status": "ACTIVE"})
                    print(f"{GREEN}User with ID {selected_user_id} has been successfully enabled.{RESET}")
                    return
            else:
                print(f"{RED}Account with ID '{selected_user_id}' not found. Please try again.{RESET}")


# ----------------------------
# Section 5: Delete User
# ----------------------------
    def delete_mhwp(self):
        """Delete an MHWP account"""
        # Display MHWP info
        mhwp_data = self.display_mhwp_info()
        if not mhwp_data:
            self.display_manager.back_operation()
            self.delete_user_menu()
            return

        retry_attempts = 0
        while retry_attempts < 3:
            input_mhwp_id = input(f"{CYAN}{BOLD}Enter MHWP ID to delete ⏳: {RESET}").strip()
            if input_mhwp_id == "back":
                self.display_manager.back_operation()
                self.delete_user_menu()
                return
            
            # Validate if input is an integer
            if not self.is_integer(input_mhwp_id):
                retry_attempts += 1
                print(f"{RED}Invalid input. Please enter an integer.{RESET}")
                continue

            input_mhwp_id = int(input_mhwp_id)
            if input_mhwp_id in mhwp_data.get("MHWP ID", []):
                # Check for existing relationships with patients
                patient_data = read_json("./data/patient_info.json")
                patients_assigned = [p for p in patient_data if p.get("mhwp_id") == input_mhwp_id]
                if patients_assigned:
                    print(f"{RED}Cannot delete MHWP with assigned patients. Please reassign patients first.{RESET}")
                    self.display_manager.back_operation()
                    self.delete_user_menu()
                    return

                # Check for future uncancelled appointments
                appointment_data = read_json("./data/appointment.json")
                current_datetime = datetime.now()
                appointments_assigned = [
                    appt for appt in appointment_data
                    if appt.get("mhwp_id") == input_mhwp_id
                    and datetime.strptime(f"{appt.get('date')} {appt.get('time_slot').split(' - ')[0]}", 
                                        "%Y-%m-%d %H:%M") > current_datetime
                    and appt.get("status") != "CANCELED"
                ]
                if appointments_assigned:
                    print(f"{RED}MHWP has upcoming appointments. Please handle these appointments first.{RESET}")
                    self.display_manager.back_operation()
                    self.delete_user_menu()
                    return

                # Check for pending requests
                request_data = read_json("./data/request_log.json")
                requests_assigned = [
                    req for req in request_data 
                    if (req.get("current_mhwp_id") == input_mhwp_id or 
                        req.get("target_mhwp_id") == input_mhwp_id) and 
                    req.get("status") == "pending"
                ]
                if requests_assigned:
                    print(f"{RED}MHWP has pending patient transfer requests. Please handle these requests first.{RESET}")
                    self.display_manager.back_operation()
                    self.delete_user_menu()
                    return

                # Confirm deletion
                confirm = input(f"{ORANGE}Are you sure you want to delete MHWP {input_mhwp_id}? (yes/no): {RESET}").strip().lower()
                if confirm == "yes":
                    try:
                        # Delete from all relevant files
                        mhwp_file_paths = [
                            "./data/mhwp_info.json",
                            "./data/user.json"
                        ]
                        for file_path in mhwp_file_paths:
                            data = read_json(file_path)
                            data = [m for m in data if m.get("mhwp_id", m.get("user_id")) != input_mhwp_id]
                            save_json(file_path, data)
                        
                        print(f"{GREEN}Successfully deleted MHWP {input_mhwp_id}!{RESET}")
                        break
                    except IOError as e:
                        print(f"{RED}An error occurred while deleting MHWP data: {e}{RESET}")
                else:
                    print(f"{GREY}Deletion cancelled.{RESET}")
                    break
            else:
                retry_attempts += 1
                print(f"{RED}MHWP ID '{input_mhwp_id}' not found. Please try again.{RESET}")

        if retry_attempts == 3:
            print(f"{RED}You have exceeded the maximum number of attempts. Returning to the Delete User Menu...{RESET}")
        
        self.display_manager.back_operation()
        self.delete_user_menu()


    def delete_patient(self):
        """Delete a patient account"""
        # Display patient info
        patient_data = self.display_patient_info()
        if not patient_data:
            self.display_manager.back_operation()
            self.delete_user_menu()
            return

        retry_attempts = 0
        while retry_attempts < 3:
            input_patient_id = input(f"{CYAN}{BOLD}Enter Patient ID to delete ⏳: {RESET}").strip()
            if input_patient_id == "back":
                self.display_manager.back_operation()
                self.delete_user_menu()
                return
            
            # Validate if input is an integer
            if not self.is_integer(input_patient_id):
                retry_attempts += 1
                print(f"{RED}Invalid input. Please enter an integer.{RESET}")
                continue

            input_patient_id = int(input_patient_id)
            if input_patient_id in patient_data.get("Patient ID", []):
                # Confirm deletion
                confirm = input(f"{ORANGE}Are you sure you want to delete Patient {input_patient_id}? (yes/no): {RESET}").strip().lower()
                if confirm == "yes":
                    try:
                        # Get MHWP ID before deletion for patient count update
                        patient_info = read_json("./data/patient_info.json")
                        patient_entry = next((p for p in patient_info if p["patient_id"] == input_patient_id), None)
                        mhwp_id = patient_entry.get("mhwp_id") if patient_entry else None

                        # Delete from all relevant files
                        patient_file_paths = [
                            "./data/appointment.json",
                            "./data/patient_info.json",
                            "./data/patient_journal.json",
                            "./data/patient_mood.json",
                            "./data/patient_record.json",
                            "./data/user.json"
                        ]
                        
                        for file_path in patient_file_paths:
                            data = read_json(file_path)
                            data = [p for p in data if p.get("patient_id", p.get("user_id")) != input_patient_id]
                            save_json(file_path, data)

                        # Update MHWP patient count if patient was assigned
                        if mhwp_id:
                            mhwp_data = read_json("./data/mhwp_info.json")
                            for mhwp in mhwp_data:
                                if mhwp["mhwp_id"] == mhwp_id:
                                    mhwp["patient_count"] = max(0, mhwp["patient_count"] - 1)
                            save_json("./data/mhwp_info.json", mhwp_data)

                        print(f"{GREEN}Successfully deleted Patient {input_patient_id}!{RESET}")
                        break
                    except IOError as e:
                        print(f"{RED}An error occurred while deleting patient data: {e}{RESET}")
                else:
                    print(f"{GREY}Deletion cancelled.{RESET}")
                    break
            else:
                retry_attempts += 1
                print(f"{RED}Patient ID '{input_patient_id}' not found. Please try again.{RESET}")

        if retry_attempts == 3:
            print(f"{RED}You have exceeded the maximum number of attempts. Returning to the Delete User Menu...{RESET}")
        
        self.display_manager.back_operation()
        self.delete_user_menu()


# ----------------------------
# Section 6: Display Summary
# ----------------------------
    def view_patients_summary(self):
        """Displays a summary of all patients"""
        patient_file = "./data/patient_info.json"
        patient_data = read_json(patient_file)
        if not patient_data:
            create_table({}, title="Patients Summary", no_data_message="No Patient Data Found", display_title=True, display_index=False)
        else:
            data = {
                "Patient ID": [p.get("patient_id", "N/A") for p in patient_data],
                "Name": [p.get("name", "N/A") for p in patient_data],
                "Email": [p.get("email", "N/A") for p in patient_data],
                "MHWP ID": [p.get("mhwp_id", "Unassigned") for p in patient_data],
            }
            create_table(data, title="Patients Summary", display_title=True, display_index=False)

    def view_mhwps_summary(self):
        """Displays a summary of all MHWPs"""
        mhwp_file = "./data/mhwp_info.json"
        mhwp_data = read_json(mhwp_file)
        if not mhwp_data:
            create_table({}, title="MHWPs Summary", no_data_message="No MHWP Data Found", display_title=True, display_index=False)
        else:
            data = {
                "MHWP ID": [m.get("mhwp_id", "N/A") for m in mhwp_data],
                "Name": [m.get("name", "N/A") for m in mhwp_data],
                "Email": [m.get("email", "N/A") for m in mhwp_data],
                "Patient Count": [m.get("patient_count", 0) for m in mhwp_data],
            }
            create_table(data, title="MHWPs Summary", display_title=True, display_index=False)

    def view_allocations_summary(self):
        """Displays patient-to-MHWP allocations"""
        patient_file = "./data/patient_info.json"
        patient_data = read_json(patient_file)
        if not patient_data:
            create_table({}, title="Patient Allocations", no_data_message="No Allocations Found", display_title=True, display_index=False)
        else:
            data = {
                "Patient ID": [p.get("patient_id", "N/A") for p in patient_data],
                "Patient Name": [p.get("name", "N/A") for p in patient_data],
                "MHWP ID": [p.get("mhwp_id", "Unassigned") for p in patient_data],
            }
            create_table(data, title="Patient Allocations", display_title=True, display_index=False)

    def view_weekly_bookings_summary(self):
        """Displays the count of weekly confirmed bookings per MHWP"""
        appointment_file = "./data/appointment.json"
        appointments = read_json(appointment_file)

        if not appointments:
            create_table({}, title="Weekly Confirmed Bookings", no_data_message="No Appointments Found", display_title=True, display_index=False)
            return

        today = datetime.now()
        start_of_week = today - timedelta(days=today.weekday()) 
        end_of_week = start_of_week + timedelta(days=6)  
       
        confirmed_appointments = []
        for appointment in appointments:
            if appointment.get("status") == "CONFIRMED":
                try:
                    appointment_date = datetime.strptime(appointment["date"], "%Y-%m-%d")
                    if start_of_week <= appointment_date <= end_of_week:
                        confirmed_appointments.append(appointment)
                except ValueError:
                    print(f"{RED}Invalid date format in appointment ID: {appointment.get('appointment_id')}{RESET}")
                    continue

        if not confirmed_appointments:
            create_table({}, title="Weekly Confirmed Bookings", no_data_message="No Confirmed Appointments for the Current Week", display_title=True, display_index=False)
            return

        mhwp_bookings = {}
        for appointment in confirmed_appointments:
            mhwp_id = appointment.get("mhwp_id", "N/A")
            mhwp_bookings[mhwp_id] = mhwp_bookings.get(mhwp_id, 0) + 1

        data = {
            "MHWP ID": list(mhwp_bookings.keys()),
            "Confirmed Bookings": list(mhwp_bookings.values()),
        }
        create_table(data, title="Weekly Confirmed Bookings", display_title=True, display_index=False)
        total_confirmed = len(confirmed_appointments)
        print(f"\n{GREEN}{BOLD}Total Confirmed Appointments for This Week: {total_confirmed}{RESET}\n")
    
    
# Give test of allocate patient to mhwp
if __name__ == "__main__":
    admin = Admin(1, "admin", "", "ACTIVE")
    admin_controller = AdminController(admin)
    admin_controller.display_admin_homepage()
