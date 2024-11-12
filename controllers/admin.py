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

    def allocate_patient(self, mhwp: MHWP, patient: Patient):
        self.admin.allocate_patient(mhwp, patient)
    
    def edit_patient(self, user, new_data):
        
        return None

    def edit_mhwp(self, user, new_data):

        return None

    def edit_user(self, user, new_data):
        if not user.is_disabled:
            user.username = new_data.get('username', user.username)
            user.password = new_data.get('password', user.password)
            if isinstance(user, Patient):
                return self.edit_patient(user, new_data)
            elif isinstance(user, MHWP):
                return self.edit_mhwp(user, new_data)
        else:
            print("User is disabled, cannot edit")

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

            #If the index is found in the patient info
            if patient['patient_id'] == patient_del.user_id:
                continue
            else:
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

            #If the index is found in the MHWP info
            if mhwp['patient_id'] != mhwp_del.user_id:
                fin_json.append(mhwp)
        
        #save it in the new MHWP info            
        with open('./data/mhwp.json', 'w+') as file:
            json.dump(fin_json, file, indent=4)

    def delete_user(self, user):
        if isinstance(user, Patient):
            return self.delete_patient(self, user)
        if isinstance(user, MHWP):
            return self.delete_patient(self, user)
    
    def display_summary(self):
        print(f"Total MHWPs: {len(self.admin.mhwps)}")
        print(f"Total Patients: {len(self.admin.patients)}")