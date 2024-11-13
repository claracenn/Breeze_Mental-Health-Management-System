
from models.user import Admin, MHWP, Patient

class AdminController:
    def __init__(self, admin: Admin):
        self.admin = admin

    def allocate_patient(self, mhwp: MHWP, patient: Patient):
        self.admin.allocate_patient(mhwp, patient)
    
    def edit_user(self, user, new_data):
        if not user.is_disabled:
            user.username = new_data.get('username', user.username)
            user.password = new_data.get('password', user.password)
        else:
            print("User is disabled, cannot edit")

    def disable_user(self, user):
        user.is_disabled = True
    
    def display_summary(self):
        print(f"Total MHWPs: {len(self.admin.mhwps)}")
        print(f"Total Patients: {len(self.admin.patients)}")

    def approve_request(self, request_id):
            """Approve an MHWP change request and update the patient's MHWP ID."""
            request_log = read_json("data/request_log.json")
            patient_data = read_json("data/patient_info.json")
    
            for request in request_log:
                if request["user_id"] == request_id and request["status"] == "pending":
                    request["status"] = "approved"

                    for patient in patient_data:
                        if patient["patient_id"] == request["user_id"]:
                            patient["mhwp_id"] = request["target_mhwp_id"]
                            break
         
                    save_json("data/request_log.json", request_log)
                    save_json("data/patient_info.json", patient_data)
                    print("Request approved and patient's MHWP ID updated.")
                    return
            print("Request not found or already approved.")
        
