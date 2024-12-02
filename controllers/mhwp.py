from models.user import MHWP
import pandas as pd
from datetime import datetime, timedelta
from utils.display_manager import DisplayManager
from utils.data_handler import *
from utils.email_helper import send_email

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
        options = ["Appointments Calendar", "Patient Records","Log Out"]
        action_map = {
        "1": self.appointment_menu,
        "2": self.patient_records_menu,
        "3": lambda: None  # Left it to be None to return to log out
        }

        # Modify options and actions for disabled mhwp
        if self.mhwp.status == "DISABLED":
            print(f"{RED}Your account is disabled. You can only log out.{RESET}")
            options = [f"{option} (Disabled)" for option in options[:-1]] + ["Log Out"]
            action_map = {"4": lambda: None}
            
        # Display upcoming appointments if any
        upcoming_appointments = self.get_upcoming_appointments()
        if upcoming_appointments:
            print(f"{GREEN}{BOLD}\nUpcoming Appointments in the next 7 days:{RESET}")
            for appt in upcoming_appointments:
                print(f"{BOLD}{appt['date']} {appt['time_slot']} - {appt['status']} with {appt['patient_name']}{RESET}")
        else:
            print(f"{LIGHT_GREEN}No appointments in the next 7 days.{RESET}")

        self.display_manager.navigate_menu(title, options, action_map, main_menu_title)

    def appointment_menu(self):
        title = "📅 Appointments Calendar"
        main_menu_title = "🏠 MHWP HomePage"
        options = ["View Appointments", "Handle Appointments", "Suggest Resources", "View Feedback", "Back to Homepage"]
        action_map = {
            "1": self.view_calendar,
            "2": self.choose_appointment,
            "3": self.suggest_resources,
            "4": self.view_feedback,
            "5": lambda: None
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

    def patient_dashboard_menu(self):
        title = "📋 Patient Dashboard"
        main_menu_title = "🏠 MHWP HomePage"
        options = ["View Patient Dashboard", "Email Emergency Contact", "Back to Homepage"]
        action_map = {
            "1": self.view_dashboard,
            "2": self.contact_emergency,
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
    
    def get_feedback(self):
        '''Returns a list of feedback for all appointments'''
        appointment_path_name = "./data/feedback.json"
        appointment_payload = read_json(appointment_path_name)
        return [appointment for appointment in appointment_payload]

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

    def get_upcoming_appointments(self):
        """Get appointments within the next 7 days for the MHWP."""
        current_date = datetime.now()
        seven_days_later = current_date + timedelta(days=7)

        # Read appointment data
        appointments = self.get_appointments()
        if not appointments:
            return []

        # Filter appointments within the next 7 days for the current mhwp
        upcoming_appointments = []
        for appointment in appointments:
            appointment_date = datetime.strptime(appointment["date"], "%Y-%m-%d")
            if current_date <= appointment_date <= seven_days_later:
                # Find the Patient name based on patient_id
                patient_name = self.get_patient_name(appointment["patient_id"])
                appointment["patient_name"] = patient_name  # Add patient_name to the appointment
                upcoming_appointments.append(appointment)

        return upcoming_appointments


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
            style=f"{MAGENTA}{BOLD}",
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
                f"{CYAN}{BOLD}Please enter an integer value from {prompt_range} to handle appointment or 3 to add notes ⏳: {RESET}"
            ).strip()

            if new_status in ["back", "0"]:
                self.display_manager.print_text(
                    style=f"{GREY}",
                    text="Exiting Appointment Handling Screen..."
                )
                self.display_manager.back_operation()
                self.appointment_menu()
                break
                
            if not self.is_integer(new_status):
                self.display_manager.print_text(style=f"{RED}", text="Please enter a valid integer value.")
                continue

            new_status = int(new_status)

            # Add appointment notes
            if new_status == 3:
                for app in appointments:
                    if app["appointment_id"] == appointment["appointment_id"]:
                        new_note = input("Please enter new note for the appointment: ")
                        update_entry('./data/appointment.json', appointment["appointment_id"], {"notes": new_note})
                        self.display_manager.print_text(
                        style=f"{BOLD}",
                        text=f"Appointment {appointment['appointment_id']} note has been successfully changed."
                    )
                        break
                else:
                    self.display_manager.print_text(
                        style=f"{RED}",
                        text=f"Something went wrong. Unable to change the note of appointment {appointment['appointment_id']}."
                    )
                break
            
            # Update appointment status
            valid_choices = {1, 2} if isPending else {1}
            if new_status not in valid_choices:
                self.display_manager.print_text(
                    style=f"{RED}",
                    text=f"❌ Invalid choice. Please enter a value from {prompt_range}."
                )
                continue

            try:
                update_status = "CANCELLED" if new_status == 1 else "CONFIRMED"
                update_entry('./data/appointment.json', appointment["appointment_id"], {"status": update_status})
                self.display_manager.print_text(
                    style=f"{RESET}{BOLD}",
                    text=f"📅 Appointment {appointment['appointment_id']} status has been successfully changed to {'CANCELLED' if new_status == 1 else 'CONFIRMED'}.\n"
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
            id_input = input(f"{CYAN}{BOLD}Enter appointment ID to handle a Pending or Confirmed appointment ⏳: {RESET}").strip()

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
                    "Status": [selected_appointment["status"]],
                    "Notes": [selected_appointment["notes"]]
                }
                create_table(data, "Selected Appointment", display_title=True)
                if selected_appointment["status"] == "PENDING":
                    self.handle_appointment_status(selected_appointment, isPending=True)
                else:
                    self.handle_appointment_status(selected_appointment, isPending=False)
                return True

            elif selected_appointment["status"] == "CANCELLED":
                self.display_manager.print_text(
                    style=f"{RED}",
                    text="This appointment has already been cancelled. Please select another appointment."
                )
            
            else:
                self.display_manager.print_text(
                    style=f"{RED}",
                    text="Unable to handle the appointment. Please contact the system manager."
                )
                return False
            
    def suggest_resources(self):
        """Allow MHWP to suggest resources to patients from a predefined list."""

        self.view_calendar()
        apps = self.get_appointments()

        while True:
            id_input = input(f"{CYAN}{BOLD}Choose Appointment ID to suggest resources ⏳: {RESET}").strip()

            if id_input == "back":
                self.display_manager.back_operation()
                self.appointment_menu()
                return
            
            if not self.is_integer(id_input):
                self.display_manager.print_text(
                    style=f"{RED}",
                    text="Invalid input. Please enter an integer value."
                )
                continue

            id_input = int(id_input)

            # Find the appointment corresponding to user input
            for app in apps:
                if id_input == app["appointment_id"]:

                    # Display selected patient
                    data = {
                    "Appointment ID": [app["appointment_id"]],
                    "Name": [self.get_patient_name(app["patient_id"])],
                    "Time": [app["time_slot"]],
                    "Date": [app["date"]],
                    "Status": [app["status"]],
                    "Notes": [app["notes"]]
                }
                    create_table(data, "Selected Appointment", display_title=True)

                    # List of resources to choose from
                    resources = {
                        "Number": ["1", "2", "3", "4"],
                        "Resource Name": ["NHS Mental Wellbeing", "Mind Mental Wellbeing", "UK Gov Mental Health", "WHO Mental Health"],
                        "Resource Link": ["https://www.nhs.uk/mental-health/self-help/guides-tools-and-activities/five-steps-to-mental-wellbeing/", "https://www.mind.org.uk/information-support/tips-for-everyday-living/wellbeing/", "https://www.gov.uk/government/publications/wellbeing-in-mental-health-applying-all-our-health/wellbeing-in-mental-health-applying-all-our-health", "https://www.who.int/news-room/fact-sheets/detail/mental-health-strengthening-our-response"]
                    }
                    create_table(resources, "Available Resources", display_title=True)

                    while True:
                        resource_input = input(f"{CYAN}{BOLD}Enter number to choose resource for recommendation ⏳: {RESET}").strip()
                        if resource_input == "back":
                            self.display_manager.back_operation()
                            self.appointment_menu()
                            return
                        
                        if not self.is_integer(resource_input):
                            self.display_manager.print_text(
                                style=f"{RED}",
                                text="Invalid input. Please enter an integer value."
                            )
                            continue

                        resource_input = int(resource_input)
                        if resource_input not in [1, 2, 3, 4]:
                            self.display_manager.print_text(
                                style=f"{RED}",
                                text="Invalid input. Please choose a resource from the list."
                            )
                            continue
                        
                        # Update resources file to display in patients' accounts
                        update_entry('./data/mhwp_resources.json', app["appointment_id"], {"resource_name": resources["Resource Name"][resource_input - 1]})
                        update_entry('./data/mhwp_resources.json', app["appointment_id"], {"resource_link": resources["Resource Link"][resource_input - 1]})
                        return

            else:
                self.display_manager.print_text(
                    style=f"{RED}",
                    text="Invalid input. Please enter a valid appointment ID."
                )
                continue

    def view_feedback(self):
        """Display feedback given by patients for MHWP's appointments."""

        apps = self.get_appointments()
        feedbacks = self.get_feedback()

        # Create a mapping for the MHWP's apppointments and corresponding Patient names
        app_set = {}
        for app in apps:
            app_set[app["appointment_id"]] = self.get_patient_name(app["patient_id"])

        data = {
            "Appointment ID": [],
            "Patient Name": [],
            "Feedback": []
        }

        # Populate the data structure with feedback from patients
        for feedback in feedbacks:
            if feedback["appointment_id"] in app_set:
                data["Appointment ID"].append(feedback["appointment_id"])
                data["Patient Name"].append(app_set[feedback["appointment_id"]])
                data["Feedback"].append(feedback["feedback"])

        create_table(data, title="Patient Feedback", display_title=True)

# ----------------------------
# Section 2: Patient Records
# ----------------------------
    def view_patient_records(self):
        """Display patient records for a MHWP."""
        patient_records = self.get_patient_records()
        patients_info = self.get_patients_info()

        payload = [
            {**val_1, **val_2} 
            for val_1 in patient_records
            for val_2 in patients_info
            if val_1["patient_id"] == val_2["patient_id"]
        ]



        data = {
            "Patient ID": [],
            "Name": [],
            "Email": [],
            "Emergency Contact": [],
            "Conditions": [], 
            "Notes": [],
            "Mood": []
        }
        for patient in payload:
            data["Patient ID"].append(patient["patient_id"])
            data["Name"].append(patient["name"])
            data["Email"].append(patient["name"])
            data["Conditions"].append(patient["condition"])
            data["Notes"].append(patient["notes"])
            data["Emergency Contact"].append(patient["emergency_contact_email"])
            data["Mood"].append(self.icons[patient["mood_code"]])

        if not data["Patient ID"]:
            self.display_manager.print_text(
            style=f"{RED}",
            text="No patient records yet."
            )
        else:
            print(" ")
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
                self.display_manager.print_text(
                    style=f"{RED}",
                    text="Invalid input. Please enter an integer value."
                )
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
            print(" ")
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
                    while True:
                        # MHWP can choose condition from predefined list
                        new_condition = input(f"{CYAN}List of Conditions: 'Anxiety', 'ADHD', 'Depression', 'Stress', 'PTSD', 'Bipolar Disorder', 'OCD', 'Panic Disorder', 'Social Anxiety', and 'GAD (Generalized Anxiety Disorder)'. \nPlease enter new patient condition: {RESET}")
                        if new_condition == "back":
                            self.update_patient_record()
                            return
                        if new_condition not in ['Anxiety', 'ADHD', 'Depression', 'Stress', 'PTSD', 'Bipolar Disorder', 'OCD', 'Panic Disorder', 'Social Anxiety', 'GAD (Generalized Anxiety Disorder)']:
                            print(f"{RED}Invalid choice. Please choose condition from the list. \n{RESET}")
                            continue

                        update_entry('./data/patient_record.json', id_input, {"condition": new_condition})
                        print(f"{GREEN}Patient condition updated successfully.{RESET}")
                        break
                    break
                elif choice == "2":
                    # Update notes
                    new_notes = input(f"{CYAN}Please enter new notes for the patient: {RESET}")
                    record["notes"] = new_notes
                    if new_notes == "back":
                        self.update_patient_record()
                        return
                    update_entry('./data/patient_record.json', id_input, {"notes": new_notes})
                    print(f"{GREEN}Patient notes updated successfully.{RESET}")
                    break
                elif choice == "3":
                    # Update all fields
                    while True:
                        new_condition = input(f"{CYAN}List of Conditions: 'Anxiety', 'ADHD', 'Depression', 'Stress', 'PTSD', 'Bipolar Disorder', 'OCD', 'Panic Disorder', 'Social Anxiety', and 'GAD (Generalized Anxiety Disorder)'. \nPlease enter new patient condition: {RESET}")
                        if new_condition == "back":
                            self.update_patient_record()
                            return
                        if new_condition not in ['Anxiety', 'ADHD', 'Depression', 'Stress', 'PTSD', 'Bipolar Disorder', 'OCD', 'Panic Disorder', 'Social Anxiety', 'GAD (Generalized Anxiety Disorder)']:
                            print(f"{RED}Invalid choice. Please choose condition from the list. \n{RESET}")
                            continue

                        update_entry('./data/patient_record.json', id_input, {"condition": new_condition})
                        print(f"{GREEN}Patient condition updated successfully.{RESET}")
                        break                    

                    new_notes = input(f"{CYAN}Please enter new notes for the patient: {RESET}")
                    if new_notes == "back":
                        self.update_patient_record()
                        return
                    update_entry('./data/patient_record.json', id_input, {"notes": new_notes})
                    print(f"{GREEN}Patient record updated successfully.\n{RESET}")
                    break
                elif choice == "4":
                    # Exit back to patient list
                    print(f"{GREY}Exiting to patient selection menu...\n{RESET}")
                    break
                elif choice == "back":
                    self.update_patient_record()
                    return
                else:
                    print(f"{RED}Invalid choice. Please enter 1, 2, or 3. \n{RESET}")
            break



    def contact_emergency(self):
        self.view_dashboard()
        patients = self.get_patients_info()


        while True:
            id_input = input(f"{CYAN}{BOLD}Choose patient ID to email emergency contact ⏳: {RESET}").strip()

            if id_input == "back":
                self.display_manager.back_operation()
                self.patient_dashboard_menu()
                return
            
            if not self.is_integer(id_input):
                self.display_manager.print_text(
                    style=f"{RED}",
                    text="Invalid input. Please enter an integer value."
                )
                continue

            id_input = int(id_input)
            for patient in patients:
                if id_input == patient["patient_id"]:
                    email = patient["emergency_contact_email"]
                    email_input = input(f"{CYAN}{BOLD}Enter subject for the email ⏳: {RESET}").strip()
                    if email_input == "back":
                        self.display_manager.back_operation()
                        self.patient_dashboard_menu()
                        return

                    subject_input = input(f"{CYAN}{BOLD}Enter message for the email ⏳: {RESET}").strip()
                    if email_input == "back":
                        self.display_manager.back_operation()
                        self.patient_dashboard_menu()
                        return


                    # TODO: Send email to emergency contact
                    first_line = "Dear Sir/Madam,\n"
                    final_line = f"\nSincerely Your Mental Health and Wellbeing Practioner,\n{self.mhwp.name}"
                    email_body = first_line + "\n" + email_input + "\n" + final_line
                    email_success = send_email(email, subject_input, email_body)
                    if (email_success):
                        print(f"{GREEN}Email has been sent succesfully.{RESET}")
                    else:
                        print(f"{RED}Something went wrong. Please try again later...{RESET}")

                    break


            else:
                self.display_manager.print_text(
                    style=f"{RED}",
                    text="Invalid input. Please enter a valid patient ID."
                )
                continue


if __name__ == "__main__":
    mhwp_controller = MHWPController(MHWP(21, "mhwp", "password", "Robert Lewandowski", "robert.lewandowski@example.com", 3, "ACTIVE"))
    mhwp_controller.display_mhwp_homepage()

