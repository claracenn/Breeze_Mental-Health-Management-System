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
        else:
            print("User is disabled, cannot edit")

    def disable_user(self, user):
        user.is_disabled = True
    
    def delete_patient(self, patient_del: Patient) -> None:
        patient_data_path_name = "./data/patient_info.json"
        patient_info = read_json(patient_data_path_name)
        fin_json = []

        index = False

        for i in range(len(patient_info)):
            patient = patient_info[i]

            #If the index is found in the patient info
            if patient['patient_id'] == patient_del.get_user_id():
                continue
            else:
                fin_json.append(patient)
        
        #save it in the new patient info
        with open('./data/patient_info.json', 'w+') as file:
            json.dump(fin_json, file, indent=4)

    def delete_mhwp(self, mhwp_del: MHWP):
        pass

    def delete_user(self, user):
        if isinstance(user, Patient):
            return delete_patient(self, user)
        if isinstance(user, MHWP):
            return delete_patient(self, user)
    
    def display_summary(self):
        print(f"Total MHWPs: {len(self.admin.mhwps)}")
        print(f"Total Patients: {len(self.admin.patients)}")

    def get_admin(self):
        return self.admin
    
    def get_user_id(self):
        return self.admin.user_id
    
    def get_username(self):
        return self.admin.username
    
    def get_password(self):
        return self.admin.password
    
    def get_role(self):
        return self.admin.role
    
    def get_is_disabled(self):
        return self.admin.is_disabled
    
    def set_user_id(self, user_id):
        self.admin.user_id = user_id

    def set_username(self, username):
        self.admin.username = username

    def set_password(self, password):
        self.admin.password = password

    def set_role(self, role):
        self.admin.role = role

    def set_is_disabled(self, is_disabled):
        self.admin.is_disabled = is_disabled