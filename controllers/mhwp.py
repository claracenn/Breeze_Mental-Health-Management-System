
from models.user import MHWP
import pandas as pd
from utils.display_manager import DisplayManager

from utils.data_handler import create_table, read_json, save_json, sanitise_data

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


    def view_homepage(self):
        title = "🏠 MHWP HomePage"
        options = ["Appointments Calendar", "Patient Dashboard", "Patient Records", "Exit"]
        action_map = {
        "1": self.view_calendar,
        "2": self.view_dashboard,
        "3": self.view_patient_records,
        "4": lambda: None,  # Left it to be None to return to log out
        }
        main_menu_title = "🏠 Main Menu"
        self.display_manager.navigate_menu(title, options, action_map, main_menu_title)

        
 
 
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
        # print(patient_records)
        # for record in patient_records:
        #     record["name"] = self.get_patient_name(record["patient_id"])
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
        if isinstance(value,int): return True

        try:
            value = value.strip()
            int(value)  # Try converting to an integer
            return True
        except (ValueError, TypeError):
            return False


    def view_calendar(self):
        """Display appointments for a MHWP."""
        appointments = self.get_appointments()

        # Initialize data structure for displaying appointments
        data = {
            "Appointment ID": [],
            "Name": [],
            "Time": [],
            "Date": [],
            "Status": []
        }

        # Populate the data dictionary with appointment details
        for appointment in appointments:
            data["Appointment ID"].append(appointment["appointment_id"])
            data["Name"].append(self.get_patient_name(appointment["patient_id"]))
            data["Time"].append(appointment["time_slot"])
            data["Date"].append(appointment["date"])
            data["Status"].append(appointment["status"])

        # Display the appointments in a formatted table
        if data["Appointment ID"]:
            self.display_manager.print_text(
                style=f"{CYAN}",
                text="📅 Breeze Mental Health Management System - Appointment Calendar"
            )
            create_table(data, "Appointments", display_title=True)
            self.choose_appointment()

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

        while True:
            prompt_range = "0-2" if isPending else "0-1"
            new_status = input(
                f"{MAGENTA}Please enter an integer value from {prompt_range}: {RESET}"
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

            valid_choices = {1, 2} if isPending else {1}
            if new_status not in valid_choices:
                self.display_manager.print_text(
                    style=f"{RED}",
                    text=f"Invalid choice. Please enter a value from {prompt_range}."
                )
                continue

            # Update appointment status
            for app in appointments:
                if app["appointment_id"] == appointment["appointment_id"]:
                    app["status"] = "CANCELED" if new_status == 1 else "CONFIRMED"
                    save_json('./data/appointment.json', appointments)
                    self.display_manager.print_text(
                        style=f"{GREEN}",
                        text=f"Appointment {appointment['appointment_id']} status has been successfully changed to {'CANCELED' if new_status == 1 else 'CONFIRMED'}."
                    )
                    break
            else:
                self.display_manager.print_text(
                    style=f"{RED}",
                    text=f"Something went wrong. Unable to change the status of appointment {appointment['appointment_id']}."
                )
            break


    # def handle_appointment(self, appointment):
    #     self.handle_appointment_status(appointment, appointment["status"] == "PENDING")
    #     # self.view_calendar()

    def choose_appointment(self):
        """MHWP can select a Pending or Confirmed appointment to Confirm/Cancel."""
        data_appointments = self.get_appointments()

        self.display_manager.print_text(
            style=f"{CYAN}",
            text="Welcome to the Appointment Selection System!"
        )
        self.display_manager.print_text(
            style=f"{GREY}",
            text="You can select a Pending or Confirmed appointment ID to handle."
        )
        self.display_manager.print_text(
            style=f"{GREY}",
            text="Enter '0' to exit the system."
        )

        while True:
            id_input = input(f"{MAGENTA}Choose a Pending or Confirmed appointment ID ('0' to exit): {RESET}").strip()

            if not self.is_integer(id_input):
                self.display_manager.print_text(
                    style=f"{RED}",
                    text="Invalid input. Please enter an integer value."
                )
                continue

            id_input = int(id_input)

            if id_input == 0:
                self.display_manager.print_text(
                    style=f"{CYAN}",
                    text="Thank you for using the appointment system. Exiting..."
                )
                break

            # Check for valid appointment and handle it
            for app in data_appointments:
                if app["appointment_id"] == id_input and app["status"] in ["PENDING", "CONFIRMED"]:
                    # Prepare and display appointment details
                    data = {
                        "Appointment ID": [app["appointment_id"]],
                        "Name": [self.get_patient_name(app["patient_id"])],
                        "Time": [app["time_slot"]],
                        "Date": [app["date"]],
                        "Status": [app["status"]]
                    }
                    create_table(data, "Selected Appointment", display_title=True)

                    # Handle the selected appointment
                    self.handle_appointment_status(app, app["status"] == "PENDING")
                    break
            else:
                self.display_manager.print_text(
                    style=f"{RED}",
                    text="No matching appointment found. Please enter a valid appointment ID."
                )
                continue
            break;


        # After exiting, return to the calendar view
        # self.view_calendar()




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

    

        create_table(data, title="Patients Records", no_data_message="MHWP has no Patient Records",display_title=True)
        if (len(data["Name"]) > 0): self.update_patient_record()



    def update_patient_record(self):
        id_input = ""
        while id_input != 0:
            patient_records = self.get_patient_records()
            patients = {patient["patient_id"]: patient["name"] for patient in patient_records}
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
                        mhwp_input = ''
                        create_table(data, "Selected Patient Record", display_title=True)
                        print("1. Update patient condition.")
                        print("2. Update patient notes.")
                        print("3. Exit")

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
    mhwp_controller = MHWPController(MHWP(22, "mhwp", "password", "name", "email", 3, "ACTIVE"))
    # mhwp_controller.view_MHWP_homepage()


MHWP = {
        "mhwp_id": 22,
        "name": "Robert Lewandowski",
        "email": "robert.lewandowski@example.com",
        }


mhwp1 = MHWPController(MHWP)
# mhwp1.view_patient_summary()
# mhwp1.view_dashboard()
# mhwp1.view_patient_records()
# mhwp1.view_calendar()
mhwp1.view_homepage()

