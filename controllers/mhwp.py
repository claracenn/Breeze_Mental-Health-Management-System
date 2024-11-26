from models.user import MHWP
import pandas as pd
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
class MHWPController:

    def __init__(self, mhwp):
        self.mhwp = mhwp
        self.display_manager = DisplayManager()
        self.icons = {
            1: "\U0001F601",
            2: "\U0001F642",
            3: "\U0001F610",
            4: "\U0001F615", 
            5: "\U0001F61E",
            6: "\U0001F621"
        }


# ----------------------------
# Homepage and Menus
# ----------------------------
    def display_mhwp_homepage(self):
        title = "🏠 MHWP HomePage"
        main_menu_title = "🏠 MHWP HomePage"
        options = ["Appointments Calendar", "Patient Records", "Patient Dashboard", "Log Out"]
        action_map = {
        "1": self.appointment_menu,
        "2": self.patient_records_menu,
        "3": self.view_dashboard,
        "4": lambda: None  # Left it to be None to return to log out
        }

        # Modify options and actions for disabled mhwp
        if self.mhwp.status == "DISABLED":
            print(f"{RED}Your account is disabled. You can only log out.{RESET}")
            options = [f"{option} (Disabled)" for option in options[:-1]] + ["Log Out"]
            action_map = {"4": lambda: None}
            
        self.display_manager.navigate_menu(title, options, action_map, main_menu_title)

    def appointment_menu(self):
        title = "📅 Appointments Calendar"
        main_menu_title = "🏠 MHWP HomePage"
        options = ["View Appointments", "Handle Appointments", "Back to Homepage"]
        action_map = {
            "1": self.view_calendar,
            "2": self.choose_appointment,
            "3": lambda: None
        }
        result = self.display_manager.navigate_menu(title, options, action_map, main_menu_title)
        if result == "main_menu":
            self.display_mhwp_homepage()
    
    def patient_records_menu(self):
        title = "📋 Patient Records"
        main_menu_title = "🏠 MHWP HomePage"
        options = ["View Patient Records", "Update Patient Records", "Back to Homepage"]
        action_map = {
            "1": self.view_patient_records,
            "2": self.update_patient_record,
            "3": lambda: None
        }
        result = self.display_manager.navigate_menu(title, options, action_map, main_menu_title)
        if result == "main_menu":
            self.display_mhwp_homepage()


# -----------------------------------
# Common Functions for Data Retrieval
# -----------------------------------
    def get_patients_info(self):
        '''Returns a list of patient information for current MHWP'''
        patient_data_path_name = "./data/patient_info.json"
        patient_info_payload = read_json(patient_data_path_name)
        return [patient for patient in patient_info_payload if patient["mhwp_id"] == self.mhwp.user_id]

    def get_patient_records(self):
        '''Returns a list of patient records for current MHWP'''
        patient_record_path = "./data/patient_record.json"
        patient_record_payload = read_json(patient_record_path)
        patients_info = self.get_patients_info()
        patient_ids = set([patient["patient_id"] for patient in patients_info])
        patient_records = [record for record in patient_record_payload if record["patient_id"] in patient_ids] 
        # print(patient_records)
        # for record in patient_records:
        #     record["name"] = self.get_patient_name(record["patient_id"])
        return patient_records

    def get_appointments(self):
        '''Returns a list of appointments for current MWHP'''
        appointment_path_name = "./data/appointment.json"
        appointment_payload = read_json(appointment_path_name)
        return [appointment for appointment in appointment_payload if appointment["mhwp_id"] == self.mhwp.user_id]

    def get_patient_name(self, patient_id):
        '''Returns patient name from patients id'''
        patients = self.get_patients_info()
        patient = next((x for x in patients if x["patient_id"] == patient_id), None)
        if patient is None:
            print("Patient ID provided does not correspond to any patient")
        else:
            return patient["name"]
        
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


# --------------------------------
# Section 1: Appointments Calendar
# --------------------------------
    def view_calendar(self):
        """Display appointments for a MHWP."""
        appointments = self.get_appointments()

        # Initialize data structure for displaying appointments
        data = {
            "Appointment ID": [],
            "Name": [],
            "Time": [],
            "Date": [],
            "Status": [],
            "Notes": []
        }

        # Populate the data dictionary with appointment details
        for appointment in appointments:
            data["Appointment ID"].append(appointment["appointment_id"])
            data["Name"].append(self.get_patient_name(appointment["patient_id"]))
            data["Time"].append(appointment["time_slot"])
            data["Date"].append(appointment["date"])
            data["Status"].append(appointment["status"])
            data["Notes"].append(appointment["notes"])

        # Display the appointments in a formatted table
        if data["Appointment ID"]:
            self.display_manager.print_text(
                style=f"{CYAN}",
                text="📅 Breeze Mental Health Management System - Appointment Calendar"
            )
            create_table(data, "Appointments", display_title=True)
            # self.choose_appointment()

        else:
            self.display_manager.print_text(
                style=f"{RED}",
                text="No appointments available to display."
            )

        # Additional prompt or action for the user
        self.display_manager.print_text(
            style=f"{GREY}",
            text="Use the menu options to handle appointments or return to the main menu."
        )




    def handle_appointment_status(self, appointment, isPending):
        appointments = self.get_appointments()
        self.display_manager.print_text(
            style=f"{CYAN}",
            text=f"You are now handling the status of Appointment ID: {appointment['appointment_id']}."
        )
        self.display_manager.print_text(style=f"{GREY}", text="Press '0' to go back.")
        self.display_manager.print_text(style=f"{RED}", text="Press '1' to cancel the appointment.")
        if isPending:
            self.display_manager.print_text(style=f"{GREEN}", text="Press '2' to confirm the appointment.")
        self.display_manager.print_text(style=f"{LIGHT_YELLOW}", text="Press '3' to update the appointment notes.")

        while True:
            prompt_range = "0-2" if isPending else "0-1"
            new_status = input(
                f"{MAGENTA}Please enter an integer value from {prompt_range} to handle or 3 to add notes: {RESET}"
            ).strip()

            if not self.is_integer(new_status):
                self.display_manager.print_text(style=f"{RED}", text="Please enter a valid integer value.")
                continue

            new_status = int(new_status)

            if new_status == 0:
                self.display_manager.print_text(
                    style=f"{CYAN}",
                    text="Exiting Appointment Handling Screen..."
                )
                break

            if new_status == 3:
                for app in appointments:
                    if app["appointment_id"] == appointment["appointment_id"]:
                        new_note = input("Please enter new note for the appointment: ")
                        update_entry('./data/appointment.json', appointment["appointment_id"], {"notes": new_note})
                        self.display_manager.print_text(
                        style=f"{GREEN}",
                        text=f"Appointment {appointment['appointment_id']} note has been successfully changed."
                    )
                        break
                else:
                    self.display_manager.print_text(
                        style=f"{RED}",
                        text=f"Something went wrong. Unable to change the note of appointment {appointment['appointment_id']}."
                    )
                break

            valid_choices = {1, 2} if isPending else {1}
            if new_status not in valid_choices:
                self.display_manager.print_text(
                    style=f"{RED}",
                    text=f"❌ Invalid choice. Please enter a value from {prompt_range}."
                )
                continue

            # Update appointment status
            try:
                update_status = "CANCELED" if new_status == 1 else "CONFIRMED"
                update_entry('./data/appointment.json', appointment["appointment_id"], {"status": update_status})
                self.display_manager.print_text(
                    style=f"{RESET}{BOLD}",
                    text=f"📅 Appointment {appointment['appointment_id']} status has been successfully changed to {'CANCELED' if new_status == 1 else 'CONFIRMED'}.\n"
                )
                break
            except Exception as e:
                self.display_manager.print_text(
                    style=f"{RED}",
                    text=f"Error: {e}. Please contact the system manager."
                )
                return False


    def choose_appointment(self):
        """MHWP can select a Pending or Confirmed appointment to Confirm/Cancel."""
        self.view_calendar()
        data_appointments = self.get_appointments()

        while True:
            id_input = input(f"{CYAN}{BOLD}Enter appointment ID to handle a Pending or Confirmed appointment: {RESET}").strip()

            if id_input == "back":
                self.display_manager.back_operation()
                self.appointment_menu()
                return
            
            # Validate if input is an integer
            if not self.is_integer(id_input):
                self.display_manager.print_text(
                    style=f"{RED}",
                    text="Invalid input. Please enter an integer value."
                )
                continue
            id_input = int(id_input)
                
            # Check for valid appointment and handle it
            selected_appointment = next((app for app in data_appointments if app["appointment_id"] == id_input), None)
            if not selected_appointment:
                self.display_manager.print_text(
                    style=f"{RED}",
                    text="No matching appointment found. Please enter a valid appointment ID."
                )
                continue

            # Prepare and display appointment details if found
            if selected_appointment["status"] in ["PENDING", "CONFIRMED"]:
                data = {
                    "Appointment ID": [selected_appointment["appointment_id"]],
                    "Name": [self.get_patient_name(selected_appointment["patient_id"])],
                    "Time": [selected_appointment["time_slot"]],
                    "Date": [selected_appointment["date"]],
                    "Status": [selected_appointment["status"]]
                }
                create_table(data, "Selected Appointment", display_title=True)
                if selected_appointment["status"] == "PENDING":
                    self.handle_appointment_status(selected_appointment, isPending=True)
                else:
                    self.handle_appointment_status(selected_appointment, isPending=False)
                return True

            elif selected_appointment["status"] == "CANCELED":
                self.display_manager.print_text(
                    style=f"{RED}",
                    text="This appointment has already been canceled. Please select another appointment."
                )
            
            else:
                self.display_manager.print_text(
                    style=f"{RED}",
                    text="Unable to handle the appointment. Please contact the system manager."
                )
                return False


# ----------------------------
# Section 2: Patient Records
# ----------------------------
    def view_patient_records(self):
        """Display patient records for a MHWP."""
        patient_records = self.get_patient_records()

        data = {
            "Patient ID": [],
            "Name": [],
            "Conditions": [], 
            "Notes": [],
        }
        for patient in patient_records:
            data["Patient ID"].append(patient["patient_id"])
            data["Name"].append(patient["name"])
            data["Conditions"].append(patient["condition"])
            data["Notes"].append(patient["notes"])

        if not data["Patient ID"]:
            self.display_manager.print_text(
            style=f"{RED}",
            text="No patient records yet."
            )
        else:
            create_table(data, title="Patients Records", display_title=True)


    def update_patient_record(self):
        self.view_patient_records()
        while True:
            patient_records = self.get_patient_records()
            if not patient_records:
                break
            patients = {patient["patient_id"]: patient["name"] for patient in patient_records}
            
            id_input = input(f"{CYAN}{BOLD}Choose patient ID to update record ⏳: {RESET}").strip()

            if id_input == "back":
                self.display_manager.back_operation()
                self.patient_records_menu()
                return
            
            if not self.is_integer(id_input):
                print("Please enter an integer value.")
                continue

            id_input = int(id_input)

            if id_input not in patients:
                print(f"{RED}Patient ID not found. Please enter a valid patient ID.{RESET}")
                continue

            record = next((r for r in patient_records if r["patient_id"] == id_input), None)
            if not record:
                print(f"{RED}No patient record yet.{RESET}")
            
            # Display patient record and update options
            data = {
            "Name": [self.get_patient_name(id_input)],
            "Condition": [record["condition"]],
            "Notes": [record["notes"]], 
            }
            create_table(data, "Selected Patient Record", display_title=True)

            # Update patient record
            while True:
                print(f"{BOLD}{MAGENTA}Select the field you want to edit:{RESET}")
                print("1. Update patient condition.")
                print("2. Update patient notes.")
                print("3. Update all fields")
                print("4. Exit")
                choice = input(f"{CYAN}{BOLD}Choose an option ⏳: {RESET}").strip()

                if choice == "1":
                    # Update condition
                    new_condition = input(f"{CYAN}Please enter new patient condition: {RESET}")
                    update_entry('./data/patient_record.json', id_input, {"condition": new_condition})
                    print(f"{GREEN}Patient condition updated successfully.{RESET}")
                    break
                elif choice == "2":
                    # Update notes
                    new_notes = input(f"{CYAN}Please enter new notes for the patient: {RESET}")
                    record["notes"] = new_notes
                    update_entry('./data/patient_record.json', id_input, {"notes": new_notes})
                    print(f"{GREEN}Patient notes updated successfully.{RESET}")
                    break
                elif choice == "3":
                    # Update all fields
                    new_condition = input(f"{CYAN}Please enter new patient condition: {RESET}")
                    new_notes = input(f"{CYAN}Please enter new notes for the patient: {RESET}")
                    update_entry('./data/patient_record.json', id_input, {"condition": new_condition})
                    update_entry('./data/patient_record.json', id_input, {"notes": new_notes})
                    print(f"{GREEN}Patient record updated successfully.\n{RESET}")
                    break
                elif choice == "4" or choice == "back":
                    # Exit back to patient list
                    print(f"{GREY}Exiting to patient selection menu...\n{RESET}")
                    break
                else:
                    print(f"{RED}Invalid choice. Please enter 1, 2, or 3. \n{RESET}")
            break


# ----------------------------
# Section 3: Patient Dashboard
# ----------------------------
    def view_dashboard(self):
        patients = self.get_patients_info()
        cols = ["Patient ID", "Name", "Email", "Emergency Contact"]
        rows = [list(patient.values()) for patient in patients]

        data = {
                "Patient ID": [],
                "Name": [],
                "Email": [], 
                "Emergency Contact": [], 
                "Mood": []
            }
        
        for patient in patients:
            data["Patient ID"].append(patient["patient_id"])
            data["Name"].append(patient["name"])
            data["Email"].append(patient["email"])
            data["Emergency Contact"].append(patient["emergency_contact_email"])
            data["Mood"].append(self.icons[patient["mood_code"]])

        create_table(data,title="Patient Dashboard", display_title=True, display_index=False)


# ---------------------------- TODO: Check if view_patient_summary is needed
    def view_patient_summary(self, patient_id):
        patient_records = self.get_patient_records()
        patients_info = self.get_patients_info()

        target_record = next((x for x in patient_records if x["patient_id"] == patient_id), None)
        target_info = next((x for x in patients_info if x["patient_id"] == patient_id), None)

        data = {
            "Key": ["Patient ID", "Name", "Email", "Emergency Contact Email", "Condition", "Notes", "Mood"],
            "Information": [
                target_info["patient_id"],
                target_info["name"], 
                target_info["email"],
                target_info["emergency_contact_email"],
                target_record["condition"],
                target_record["notes"],
                self.icons[target_info["mood_code"]]
            ]
        }
        title = f"{target_info['name']}'s Summary"
        create_table(data, title=title, display_title=True)
# ----------------------------

# ---------------------------- TODO: Should be moved to admin controller 
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

if __name__ == "__main__":
    mhwp_controller = MHWPController(MHWP(21, "mhwp", "password", "Robert Lewandowski", "robert.lewandowski@example.com", 3, "ACTIVE"))
    mhwp_controller.display_mhwp_homepage()
