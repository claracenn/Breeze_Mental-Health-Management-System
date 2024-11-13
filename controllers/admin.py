import pandas as pd
from models.user import Admin, MHWP, Patient
from controllers.mhwp import MHWPController
from controllers.patient import PatientController
from utils.data_handler import read_json
import json

##python -m controllers.admin

class AdminController:
    def __init__(self, admin: Admin):
        self.admin = admin

    #Creates a dictionary of a patient and their respective MHWP
    #If the patient doesn't have a MHWP, assign them to MHWP
    #used as input
    def allocate_patient(self, mhwp: MHWP, patient: Patient):
        patient_data_path_name = "./data/patient_info.json"
        patient_info = read_json(patient_data_path_name)

        mhwp_patient_allocation = {}

        for i in range(len(patient_info)):
            patient_details = patient_info[i]

            patient_id = patient_details["patient_id"]
            mhwp_id = patient_details["mhwp_id"]
            
            if patient_id not in mhwp:
                mhwp_patient_allocation[patient_id] = mhwp_id
        
        if patient.user_id not in mhwp_patient_allocation:        
            self.admin.allocate_patient(mhwp, patient)

    #Updates user
    #Checks if they are patients and amends their attributes accordingly
    #Also checks if they are a MHWP and amends their attributes accordingly
    def edit_user(self, user, new_data: dict):
        if not user.is_disabled:
            user.username = new_data.get('username', user.username)
            user.password = new_data.get('password', user.password)
            if isinstance(user, Patient):
                user.mood_log = new_data.get('mood_log', user.mood_log)
                user.journal_entries = new_data.get('journal_entries', user.journal_entries)
            elif isinstance(user, MHWP):
                user.patients = new_data.get('patients', user.patients)
                user.appointments = new_data.get('appointments', user.appointments)
        else:
            raise PermissionError("User is disabled, cannot edit")


    def disable_user(self, user):
        user.is_disabled = True
    
    #deletes a specific patient based on their user id, writes json file 
    #without the patient you want to delete
    def delete_patient(self, patient_del: Patient) -> None:
        patient_data_path_name = "./data/patient_info.json"
        patient_info = read_json(patient_data_path_name)
        fin_json = []

        for i in range(len(patient_info)):
            patient = patient_info[i]

            #Creating a new lists of Patients
            #checks id and username/email
            if (patient['patient_id'] != patient_del.user_id and
            patient['email'] != patient_del.username):
                fin_json.append(patient)
        
        #save it in the new patient info
        with open('./data/patient_info.json', 'w+') as file:
            json.dump(fin_json, file, indent=4)

    #deletes a specific MHWP based on their user id, writes json file 
    #without the MHWP you want to delete
    def delete_mhwp(self, mhwp_del: MHWP):
        mhwp_data_path_name = "./data/mhwp.json"
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
        with open('./data/mhwp.json', 'w+') as file:
            json.dump(fin_json, file, indent=4)

    def delete_user(self, user):
        if isinstance(user, Patient):
            return self.delete_patient(user)
        if isinstance(user, MHWP):
            return self.delete_patient(user)

    def display_summary(self):
        print(f"Total MHWPs: {len(self.admin.mhwps)}")
        print(f"Total Patients: {len(self.admin.patients)}")

# a = Admin(1,"tim","")
# p = Patient(1,"bob","")
# m = MHWP(1, "dr", "")

# ac = AdminController(a)
# ac.delete_user(m)