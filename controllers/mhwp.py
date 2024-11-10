import json
from models.user import MHWP
import pandas as pd
from misc.table import create_table
from utils.data_handler import read_json

class MHWPController:
    '''Class to control various functions of the MHWPs.'''

    def __init__(self, mhwp):
        self.mhwp = mhwp


    def get_patients_info(self):
        '''Returns a list of patient information for current MHWP'''
        patient_data_path_name = "./data/patient_info.json"
        patient_info_payload = read_json(patient_data_path_name)
        return [patient for patient in patient_info_payload if patient["mhwp_id"] == self.mhwp["mhwp_id"]]
 

    def get_patient_records(self):
        '''Returns a list of patient records for current MHWP'''
        patient_record_path = "./data/patient_record.json"
        patient_record_payload = read_json(patient_record_path)
        return [record for record in patient_record_payload]  


    def get_appointments(self):
        '''Returns a list of appointments for current MWHP'''
        appointment_path_name = "./data/appointment.json"
        appointment_payload = read_json(appointment_path_name);
        return [appointment for appointment in appointment_payload if appointment["mhwp_id"] == self.mhwp["mhwp_id"]]


    def get_patient_name(self, patient_id):
        '''Returns patient name from patients id'''
        patients = self.get_patients_info();
        patient = next((x for x in patients if x["patient_id"] == patient_id), None)
        if (patient == None):
            print("Patient ID provided does not correspond to any patient");
        return patient["name"]


    def display_calendar(self):
        appointments = self.get_appointments()
        # cols = ["Date", "Time", "Patient", "Status"]

        data = {
            "Name": [],
            "Time": [],
            "Date": [], 
            "Status": []
        }

        for appointment in appointments:
            data["Name"].append(self.get_patient_name(appointment["patient_id"]))
            data["Time"].append(appointment["time_slot"])
            data["Date"].append(appointment["date"])
            data["Status"].append(appointment["status"])
        create_table(data, "My Calendar", display_title=True)



 


    def handle_appointment(self, appointment):
        pass

        
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

    def display_patient_records(self):
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
        patients = self.get_patients_info()
        # add some sort of sorting/filtering functionality
        cols = ["Patient ID", "Name", "Email", "Emergency Contact"]
        rows = [list(patient.values()) for patient in patients]


        data = {
                "Patient ID": [],
                "Name": [],
                "Email": [], 
                "Emergency Contact": [], 
                # "Conditions": [], 
                # "Mood": []
            }
        
        for patient in patients:
            data["Patient ID"].append(patient["patient_id"])
            data["Name"].append(patient["name"])
            data["Email"].append(patient["email"])
            data["Emergency Contact"].append(patient["emergency_contact_email"])

        create_table(data,title="Toms's Patient Dashboard", display_title=True, display_index=False)
 
        
       






MHWP = {
        "mhwp_id": 21,
        "name": "Robert Lewandowski",
        "email": "robert.lewandowski@example.com",
        }
mhwp1 = MHWPController(MHWP)

# mhwp1.view_dashboard()
# mhwp1.display_calendar()
# print(mhwp1.get_appointments())
# print(mhwp1.get_patients_info())
# print(mhwp1.display_patient_records())
# print(mhwp1.get_patient_records())