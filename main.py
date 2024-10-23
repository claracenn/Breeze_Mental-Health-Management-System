from models.user import Admin, MHWP, Patient
from controllers.admin import AdminController
from controllers.patient import PatientController
from controllers.mhwp import MHWPController

def main():
    admin = Admin(user_id=1, username="admin1", password="")
    mhwp = MHWP(user_id=2, username="mhwp1", password="")
    patient = Patient(user_id=3, username="patient1", password="")

    admin_controller = AdminController(admin)
    patient_controller = PatientController(patient)
    mhwp_controller = MHWPController(mhwp)

    admin_controller.allocate_patient(mhwp, patient)
    patient_controller.book_appointment(mhwp, "2024-10-24 14:00")
    mhwp_controller.confirm_appointment("2024-10-24 14:00")

if __name__ == "__main__":
    main()
    