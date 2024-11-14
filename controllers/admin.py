import pandas as pd
import json
from models.user import Admin, MHWP, Patient
from utils.data_handler import read_json
# from controllers.mhwp import MHWPController
# from controllers.patient import PatientController

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
        patient_info = read_json('./data/patient_info.json')
        mhwp_info = read_json('./data/mhwp_info.json')
        print(f"Total Patients: {len(patient_info)}")
        print(f"Total MHWPs: {len(mhwp_info)}")
        # Optional: Convert to DataFrame for better output
        df_patients = pd.DataFrame(patient_info)
        df_mhwps = pd.DataFrame(mhwp_info)
        print("\nPatients Data:")
        print(df_patients.head())
        print("\nMHWPs Data:")
        print(df_mhwps.head())

def display_menu():
    print("--- Breeze Mental Health Management System ---")
    print("---------------- [Admin Page] ----------------")
    print(" Select one of the following options: ")
    print("1. Allocate a Patient to a MHWP")
    print("2. Edit User")
    print("3. Disable User")
    print("4. Delete User")
    print("5. Display Summary")
    print("6. Exit to Main Page")

def allocate_patient_menu(admin_controller):
    try:
        patient_id = input("Enter Patient ID to allocate: ")
        mhwp_id = input("Enter MHWP ID to assign: ")
        if not patient_id or not mhwp_id:
            raise ValueError("Patient ID and MHWP ID cannot be empty.")
        patient = Patient(patient_id, f"patient{patient_id}", "")
        mhwp = MHWP(mhwp_id, f"mhwp{mhwp_id}", "")
        admin_controller.allocate_patient(mhwp, patient)
        print(f"Patient {patient_id} successfully allocated to MHWP {mhwp_id}.")
    except ValueError as ve:
        print(f"Input Error: {ve}")
    except Exception as e:
        print(f"Error occurred: {e}")

def edit_user_menu(admin_controller):
    try:
        user_type = input("Enter user type (patient/mhwp): ")
        if user_type.lower() not in ["patient", "mhwp"]:
            raise ValueError("Invalid user type. Must be 'patient' or 'mhwp'.")
        user_id = input("Enter User ID: ")
        if not user_id:
            raise ValueError("User ID cannot be empty.")
        new_username = input("Enter new username (leave blank to keep current): ")
        new_password = input("Enter new password (leave blank to keep current): ")
        new_data = {
            "username": new_username,
            "password": new_password
        }
        if user_type.lower() == "patient":
            user = Patient(user_id, f"patient{user_id}", "")
        elif user_type.lower() == "mhwp":
            user = MHWP(user_id, f"mhwp{user_id}", "")
        admin_controller.edit_user(user, new_data)
        print(f"User {user_id} edited successfully.")
    except ValueError as ve:
        print(f"Input Error: {ve}")
    except PermissionError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error occurred: {e}")

def disable_user_menu(admin_controller):
    try:
        user_type = input("Enter user type (patient/mhwp): ")
        if user_type.lower() not in ["patient", "mhwp"]:
            raise ValueError("Invalid user type. Must be 'patient' or 'mhwp'.")
        user_id = input("Enter User ID: ")
        if not user_id:
            raise ValueError("User ID cannot be empty.")
        if user_type.lower() == "patient":
            user = Patient(user_id, f"patient{user_id}", "")
        elif user_type.lower() == "mhwp":
            user = MHWP(user_id, f"mhwp{user_id}", "")
        admin_controller.disable_user(user)
        print(f"User {user_id} has been disabled.")
    except ValueError as ve:
        print(f"Input Error: {ve}")
    except Exception as e:
        print(f"Error occurred: {e}")

def delete_user_menu(admin_controller):
    try:
        user_type = input("Enter user type (patient/mhwp): ")
        if user_type.lower() not in ["patient", "mhwp"]:
            raise ValueError("Invalid user type. Must be 'patient' or 'mhwp'.")
        user_id = input("Enter User ID: ")
        if not user_id:
            raise ValueError("User ID cannot be empty.")
        if user_type.lower() == "patient":
            user = Patient(user_id, f"patient{user_id}", "")
        elif user_type.lower() == "mhwp":
            user = MHWP(user_id, f"mhwp{user_id}", "")
        admin_controller.delete_user(user)
        print(f"User {user_id} deleted successfully.")
    except ValueError as ve:
        print(f"Input Error: {ve}")
    except Exception as e:
        print(f"Error occurred: {e}")

def main():
    admin_user = Admin(1, "admin", "")
    admin_controller = AdminController(admin_user)

    while True:
        display_menu()
        choice = input("Enter your choice: ")
        if choice == '1':
            allocate_patient_menu(admin_controller)
        elif choice == '2':
            edit_user_menu(admin_controller)
        elif choice == '3':
            disable_user_menu(admin_controller)
        elif choice == '4':
            delete_user_menu(admin_controller)
        elif choice == '5':
            admin_controller.display_summary()
        elif choice == '6':
            pass
            # link to main.py file later on
        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    main()

# a = Admin(1,"tim","")
# p = Patient(1,"bob","")
# m = MHWP(1, "dr", "")

# ac = AdminController(a)
# ac.delete_user(m)
