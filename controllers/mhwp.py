import json
from models.user import MHWP

class MHWPController:
    '''Class to control various functions of the MHWPs.'''

    def __init__(self, mhwp):
        self.mhwp = mhwp

    def get_patient_name(self, patient_id):
        try:
            with open('./data/patient_info.json', 'r') as patients:
                patient_info = json.load(patients)
        except FileNotFoundError as e: 
            print(f"File cannot be found: {e}")    
        except Exception as e:
            print(f"Unexpected Error Occured: {e}")
        else:
            for patient in patient_info:
                if patient["patient_id"] == patient_id:
                    return patient["name"]

    def display_calendar(self):
        try:
            with open('./data/appointment.json', 'r') as appointments:
                data = json.load(appointments)
        except FileNotFoundError as e: 
            print(f"File cannot be found: {e}")    
        except Exception as e:
            print(f"Unexpected Error Occured: {e}")
        else:
            # cols = ["Date", "Time", "Patient", "Status"]
            print("My Calendar")
            mhwp_id = self.mhwp["mhwp_id"]
            for app in data:
                if app["mhwp_id"] == mhwp_id:
                    print(app["date"], app["time_slot"], self.get_patient_name(app["patient_id"]), app["status"])


    def handle_appointment(self, appointment):
        # parse user input "Y" = confirm appointment
        user_input = input("Press 'Y' to confirm this appointment, or press 'N' to cancel it.")
        
        while user_input != "X":
            if user_input != "Y" or user_input != "N":
                print("Invalid input, please press 'Y' to confirm appointment\n,'N' to cancel appointment,\n'X' to go back")
            else:
                appointment.confirmed = (user_input == "Y")

        return
        
    def choose_appointment(self):
        # Display Pending appointments to MHWP
        try:
            with open('./data/appointment.json', 'r') as appointments:
                data = json.load(appointments)
        except FileNotFoundError as e: 
            print(f"File cannot be found: {e}")    
        except Exception as e:
            print(f"Unexpected Error Occured: {e}")
        else:
            # cols = ["Appointment_id", "Date", "Time", "Patient"]
            print("My Calendar - Pending")
            mhwp_id = self.mhwp["mhwp_id"]
            for app in data:
                if app["mhwp_id"] == mhwp_id and app["status"] == "PENDING":
                    print(app["appointment_id"], app["date"], app["time_slot"], self.get_patient_name(app["patient_id"]))

            # MHWP can choose pending appointment to confirm or cancel
            id_input = ""
            while id_input != "X":
                id_input = input("Choose pending appointment_id to confirm or cancel ('X' to exit): ")
                if id_input == "X": break
                else: id_input = int(id_input)
                for app in data:
                    if app["mhwp_id"] == mhwp_id and app["appointment_id"] == id_input and app["status"] == "PENDING":
                        print(app["appointment_id"], app["date"], app["time_slot"], self.get_patient_name(app["patient_id"]))
                        self.handle_appointment(app)
                        id_input = "X"
                        break
                    else:
                        print("Please enter valid appointment_id, or enter 'X' to exit.")
                        break

    def display_patient_record(self):
        # Find list of patients for a particular MHWP
        try:
            with open('./data/patient_info.json', 'r') as info:
                patient_info = json.load(info)
            with open('./data/patient_record.json', 'r') as record:
                patient_records = json.load(record)
        except FileNotFoundError as e:
            print(f"File cannot be found: {e}")
        except Exception as e:
            print(f"Unexpected Error Occurred: {e}")
        else:
            print("My Patient Records")
            mhwp_id = self.mhwp["mhwp_id"]
            patients = {}
            for pat in patient_info:
                if pat["mhwp_id"] == mhwp_id:
                    patients[pat["patient_id"]] = pat["name"]

            # Display patient list with records
            for rec in patient_records:
                if rec["patient_id"] in patients.keys():
                    print(rec["patient_id"], patients[rec["patient_id"]], rec["condition"], rec["notes"])
            self.update_patient_record(patient_records, patients)

    def update_patient_record(self, patient_records, patients):
        id_input = ""
        while id_input != "X":
            id_input = input("Choose patient_id to update record ('X' to exit): ")
            if id_input == "X": break
            else: id_input = int(id_input)
            if id_input in patients.keys():
                for record in patient_records:
                    if record["patient_id"] == id_input:
                        print("Selected patient record:")
                        print(self.get_patient_name(id_input), record["condition"], record["notes"])
                        print("1. Update patient condition.")
                        print("2. Update patient notes.")
                        print("3. Exit")
                        mhwp_input = ''
                        while mhwp_input not in ['1', '2', '3']:
                            mhwp_input = input("Choose option listed above (Enter 1, 2, or 3): ")
                            if mhwp_input == '1':
                                condition = input("Please enter patient condition: ")
                                record["condition"] = condition
                                try:
                                    with open('./data/patient_record.json', 'w') as update_record:
                                        json.dump(patient_records, update_record, indent=4)
                                except FileNotFoundError as e:
                                    print(f"File cannot be found: {e}")
                                except Exception as e:
                                    print(f"Unexpected error occurred: {e}")
                            elif mhwp_input == '2':
                                note = input("Please enter note for patient: ")
                                record["notes"] = note
                                try:
                                    with open('./data/patient_record.json', 'w') as update_record:
                                        json.dump(patient_records, update_record, indent=4)
                                except FileNotFoundError as e:
                                    print(f"File cannot be found: {e}")
                                except Exception as e:
                                    print(f"Unexpected error occurred: {e}")
                            elif mhwp_input == '3':
                                break
                            else:
                                print("Please enter 1, 2, or 3")

                        break
                break
            else:
                print("Please enter valid patient id.")

    def view_dashboard(self):
        for patient in self.mhwp.patients:
            print(f"Patient: {patient.username}, Mood Log: {patient.mood_log}")



MHWP = {
        "mhwp_id": 21,
        "name": "Robert Lewandowski",
        "email": "robert.lewandowski@example.com"
        }
mhwp1 = MHWPController(MHWP)
mhwp1.display_patient_record()