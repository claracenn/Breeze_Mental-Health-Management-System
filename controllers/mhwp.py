
from models.user import MHWP
import pandas as pd

from utils.data_handler import create_table, read_json, save_json, sanitise_data


"""
==================================
Initialise ANSI color codes
==================================
"""
BOLD = "\033[1m"
UNDERLINE = "\033[4m"
BLACK = "\033[30m"  
BROWN_RED = "\033[91m"  
DARK_GREY = "\033[90m"
RESET = "\033[0m"
RED = "\033[91m\033[1m"
LIGHT_RED = "\033[91m"
ORANGE = "\033[93m\033[1m"
YELLOW = "\033[93m"
LIGHT_GREEN = "\033[92m"
GREEN = "\033[92m\033[1m"

"""
==================================
MHWP Controller Class
==================================
"""

class MHWPController:

    def __init__(self, mhwp):
        self.mhwp = mhwp

    def view_menu(self, title, options):
        """Generic method to display a menu with subdued styling."""
        print(f"\n{BOLD}{UNDERLINE}{title}{RESET}")
        print("-" * 50)  # Divider line
        for index, option in enumerate(options, start=1):
            # [1] Frame it
            print(f"{BLACK}[{index}]{RESET} {option}")
        print("-" * 50)
        return input(f"{BROWN_RED}Choose an option ⏳: {RESET}")  

    # Main menu
    def view_MHWP_homepage(self):
        """Display the MHWP homepage."""
        # Check if account is active
        if self.mhwp.status == "ACTIVE":
            while True:
                choice = self.view_menu(
                    "🏠 MHWP Homepage",
                    [
                        "View Appointments Calendar",
                        "View Patient Dashboard",
                        "View Patient Records",
                        "Log Out",
                    ],
                )
                if choice == "1":
                    self.view_calendar()
                elif choice == "2":
                    self.view_dashboard()
                elif choice == "3":
                    self.view_patient_records()
                elif choice == "4":
                    print(f"{BOLD}Logging out...{RESET}")
                    break
                else:
                    print(f"{DARK_GREY}Invalid choice. Please try again.{RESET}")
        else:
            # Disabled account can only log out
            print(f"{RED}Your account is disabled. You can only log out.{RESET}")
            while True:
                choice = self.view_menu(
                    "🏠 MHWP Homepage",
                    [
                        "View Appointments Calendar (disabled)",
                        "View Patient Dashboard (disabled)",
                        "View Patient Records (disabled)",
                        "Log Out",
                    ],
                )
                if choice == "1" or choice == "2" or choice == "3":
                    print("Your account has been disabled. You cannot access this option.")
                elif choice == "4":
                    print(f"{BOLD}Logging out...{RESET}")
                    break
                else:
                    print(f"{DARK_GREY}Invalid choice. Please try again.{RESET}")


    def get_patients_info(self):
        '''Returns a list of patient information for current MHWP'''
        patient_data_path_name = "./data/patient_info.json"
        patient_info_payload = read_json(patient_data_path_name)
        return [patient for patient in patient_info_payload if patient["mhwp_id"] == self.mhwp["mhwp_id"]]
 

    def get_patient_records(self):
        '''Returns a list of patient records for current MHWP'''
        patient_record_path = "./data/patient_record.json"
        patient_record_payload = read_json(patient_record_path)
        patients_info = self.get_patients_info()
        patient_ids = set([patient["patient_id"] for patient in patients_info])
        patient_records = [record for record in patient_record_payload if record["patient_id"] in patient_ids] 
        for record in patient_records:
            record["name"] = self.get_patient_name(record["patient_id"])
        return patient_records


    def get_appointments(self):
        '''Returns a list of appointments for current MWHP'''
        appointment_path_name = "./data/appointment.json"
        appointment_payload = read_json(appointment_path_name)
        return [appointment for appointment in appointment_payload if appointment["mhwp_id"] == self.mhwp["mhwp_id"]]


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
        try:
            value = value.strip()
            int(value)  # Try converting to an integer
            return True
        except (ValueError, TypeError):
            return False


    def view_calendar(self):
        '''Display appointments for a MHWP'''
        appointments = self.get_appointments()

        data = {
            "Appointment ID": [],
            "Name": [],
            "Time": [],
            "Date": [], 
            "Status": []
        }

        for appointment in appointments:
            data["Appointment ID"].append(appointment["appointment_id"])
            data["Name"].append(self.get_patient_name(appointment["patient_id"]))
            data["Time"].append(appointment["time_slot"])
            data["Date"].append(appointment["date"])
            data["Status"].append(appointment["status"])
        create_table(data, "My Calendar", display_title=True)

        self.choose_appointment()

    def handle_appointment_status(self, appointment, isPending):
        appointments = self.get_appointments()
        print(f"You are now handling the status of {appointment['appointment_id']}.")
        print("Press '0' to go back.")
        print("Press '1' to cancel the appointment.")
        if isPending: print("Press '2' to confirm the appointment.")

        new_status = input("Please enter your choice here: ")
        while new_status != "0":
            if not self.is_integer(new_status):
                new_status = input(f"Please enter an integer value from {'0-2' if isPending else '0-1'}: ")
                continue
            else:
                new_status = int(new_status)

            if new_status == 0:
                print("Exiting Appointment Handling Screen....")
                break

            if (isPending and not sanitise_data(new_status, {1, 2})) or (not isPending and not sanitise_data(new_status, {1})):
                print(f"Please enter an integer value from {'0-2' if isPending else '0-1'}: ")
                continue

            for app in appointments:
                if app["appointment_id"] != appointment["appointment_id"]: continue
                app["status"] = "CANCELED" if new_status == 1 else "CONFIRMED"
                save_json('./data/appointment.json', appointments)
                print(f"Appointment {appointment['appointment_id']} status has successfully been changed to {'CANCELED' if new_status == 1 else 'CONFIRMED'}")
                break
            else:
                print(f"Something went wrong. Was not able to change the status of appointment {appointment['appointment_id']}")

    def handle_appointment(self, appointment):
        self.handle_appointment_status(appointment, appointment["status"] == "PENDING")
        self.view_calendar()

    def choose_appointment(self):
        '''MHWP can select Pending appointment to Confirm/Cancel'''
        data_appointments = self.get_appointments()

        id_input = ""
        while id_input != "0":
            id_input = input("Choose Pending or Confirmed appointment ID ('0' to exit): ")
            if not self.is_integer(id_input):
                print("Please enter an integer value.")
                continue
            else:
                id_input = int(id_input)
            if id_input == 0:
                print("Thank you for using the appointment system.")

            for app in data_appointments:
                if app["appointment_id"] == id_input and (app["status"] == "PENDING" or app['status'] == "CONFIRMED"):
                    data = {
                        "Appointment ID": [app["appointment_id"]],
                        "Name": [self.get_patient_name(app["patient_id"])],
                        "Time": [app["time_slot"]],
                        "Date": [app["date"]], 
                        "Status": [app["status"]]
                    }
                    create_table(data, "Selected Appointment", display_title=True)
                    self.handle_appointment(app)
                    break
            else:
                print("Please enter valid appointment_id, or enter '0' to exit.")

    def view_patient_records(self):
        patient_info = self.get_patients_info()
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

        create_table(data, title="Patients Records", display_title=True)
        self.update_patient_record()

    def update_patient_record(self):
        patient_records = self.get_patient_records()
        patients = {patient["patient_id"]: patient["name"] for patient in patient_records}
        
        id_input = ""
        while id_input != "0":
            id_input = input("Choose patient ID to update record ('0' to exit): ")
            if not self.is_integer(id_input):
                print("Please enter an integer value.")
                continue
            else:
                id_input = int(id_input)
            if id_input == 0:
                continue
            if id_input in patients.keys():
                for record in patient_records:
                    if record["patient_id"] == id_input:
                        data = {
                        "Name": [self.get_patient_name(id_input)],
                        "Condition": [record["condition"]],
                        "Notes": [record["notes"]], 
                    }
                        create_table(data, "Selected Patient Record", display_title=True)
                        print("1. Update patient condition.")
                        print("2. Update patient notes.")
                        print("3. Exit")
                        mhwp_input = ''
                        while mhwp_input not in ['1', '2', '3']:
                            mhwp_input = input("Choose option listed above (Enter 1, 2, or 3): ")
                            if mhwp_input == '1':
                                condition = input("Please enter patient condition: ")
                                record["condition"] = condition
                                save_json('./data/patient_record.json', patient_records)
                            elif mhwp_input == '2':
                                note = input("Please enter note for patient: ")
                                record["notes"] = note
                                save_json('./data/patient_record.json', patient_records)
                            elif mhwp_input == '3':
                                continue
                            else:
                                print("Please enter 1, 2, or 3")
                        else:
                            print("Thank you for using the Patient Record system.")

                        break
                break
            else:
                print("Please enter valid patient id.")
        else:
            print("Thank you for using the Patient Record system.")



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

        create_table(data,title="Toms's Patient Dashboard", display_title=True, display_index=False)



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

if __name__ == "__main__":
    # MHWP = {
    #         "mhwp_id": 21,
    #         "name": "Robert Lewandowski",
    #         "email": "robert.lewandowski@example.com",
    #         }
    # mhwp1 = MHWPController(MHWP)
    # mhwp1.view_MHWP_homepage()
    mhwp_controller = MHWPController(MHWP(22, "mhwp2", "", "Erling Haaland", "erling.haaland@example.com", 3, "ACTIVE"))
    mhwp_controller.view_MHWP_homepage()