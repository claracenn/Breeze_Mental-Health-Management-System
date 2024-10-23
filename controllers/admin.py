
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
    