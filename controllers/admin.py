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
    
    def display_admin_homepage(self):
        title = "🏠 Admin Homepage"
        main_menu_title = "🏠 Admin Homepage"
        options = ["Allocate Patient to MHWP",
                   "Edit User Info",
                   "Disable or Enable User",
                   "Delete User",
                   "Display Summary",
                   "Logout"]
        action_map = {
            "1": self.allocate_patient,
            "2": self.edit_user_info_menu,
            "3": self.disable_enable_user_menu,
            "4": self.delete_user_menu,
            "5": self.display_summary,
            "6": lambda: None
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
        title = "🙅 Diable User"
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
                create_table(data, "Patient Information", display_title=True, display_index=True)
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
                create_table(data, "MHWP Information", display_title=True, display_index=True)
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
                patient_entry = next((p for p in patient_data if p["Patient ID"] == input_patient_id), None)
                if patient_entry.get("mhwp_id") == input_mhwp_id:
                    retry_attempts += 1
                    print(f"{RED}Patient ID {input_patient_id} is already assigned to MHWP ID {input_mhwp_id}.{RESET}")
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

# ----------------------------
# Section 2: Edit User Info
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
                    save_json("./data/mhwp_info.json", data)

            # If MHWP ID not found
            else:
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
                    save_json("./data/patient_info.json", data)
                    update_entry("./data/patient_record.json", input_patient_id, {"name": new_name})
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
# Section 5: Display Summary
# ----------------------------
    def display_summary(self):
        """Display Summary Submenu"""
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

    def view_patients_summary(self):
        """Displays a summary of all patients"""
        patient_file = "./data/patient_info.json"
        patient_data = read_json(patient_file)
        if not patient_data:
            create_table({}, title="Patients Summary", no_data_message="No Patient Data Found", display_title=True)
        else:
            data = {
                "Patient ID": [p.get("patient_id", "N/A") for p in patient_data],
                "Name": [p.get("name", "N/A") for p in patient_data],
                "Email": [p.get("email", "N/A") for p in patient_data],
                "MHWP ID": [p.get("mhwp_id", "Unassigned") for p in patient_data],
            }
            create_table(data, title="Patients Summary", display_title=True)

    def view_mhwps_summary(self):
        """Displays a summary of all MHWPs"""
        mhwp_file = "./data/mhwp_info.json"
        mhwp_data = read_json(mhwp_file)
        if not mhwp_data:
            create_table({}, title="MHWPs Summary", no_data_message="No MHWP Data Found", display_title=True)
        else:
            data = {
                "MHWP ID": [m.get("mhwp_id", "N/A") for m in mhwp_data],
                "Name": [m.get("name", "N/A") for m in mhwp_data],
                "Email": [m.get("email", "N/A") for m in mhwp_data],
                "Patient Count": [m.get("patient_count", 0) for m in mhwp_data],
            }
            create_table(data, title="MHWPs Summary", display_title=True)

    def view_allocations_summary(self):
        """Displays patient-to-MHWP allocations"""
        patient_file = "./data/patient_info.json"
        patient_data = read_json(patient_file)
        if not patient_data:
            create_table({}, title="Patient Allocations", no_data_message="No Allocations Found", display_title=True)
        else:
            data = {
                "Patient ID": [p.get("patient_id", "N/A") for p in patient_data],
                "Patient Name": [p.get("name", "N/A") for p in patient_data],
                "MHWP ID": [p.get("mhwp_id", "Unassigned") for p in patient_data],
            }
            create_table(data, title="Patient Allocations", display_title=True)


    

    def view_weekly_bookings_summary(self):
        """Displays the count of weekly confirmed bookings per MHWP"""
        appointment_file = "./data/appointment.json"
        appointments = read_json(appointment_file)

        if not appointments:
            create_table({}, title="Weekly Confirmed Bookings", no_data_message="No Appointments Found", display_title=True)
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
            create_table({}, title="Weekly Confirmed Bookings", no_data_message="No Confirmed Appointments for the Current Week", display_title=True)
            return

       
        mhwp_bookings = {}
        for appointment in confirmed_appointments:
            mhwp_id = appointment.get("mhwp_id", "N/A")
            mhwp_bookings[mhwp_id] = mhwp_bookings.get(mhwp_id, 0) + 1

        
        data = {
            "MHWP ID": list(mhwp_bookings.keys()),
            "Confirmed Bookings": list(mhwp_bookings.values()),
        }
        create_table(data, title="Weekly Confirmed Bookings", display_title=True)
        total_confirmed = len(confirmed_appointments)
        print(f"\n{GREEN}{BOLD}Total Confirmed Appointments for This Week: {total_confirmed}{RESET}\n")
    
    
# give test of allocate patient to mhwp
if __name__ == "__main__":
    admin = Admin(1, "admin", "", "ACTIVE")
    admin_controller = AdminController(admin)
    admin_controller.display_admin_homepage()
