
from models.user import MHWP

class MHWPController:
    def __init__(self, mhwp: MHWP):
        self.mhwp = mhwp

    def confirm_appointment(self, appointment):
        appointment.confirmed = True
        print("Appointment confirmed")

    def cancel_appointment(self, appointment):
        print("Appointment cancelled")

    def add_patient_record(self, patient, condition, notes):
        patient.condition = condition
        patient.notes = notes

    def view_dashboard(self):
        for patient in self.mhwp.patients:
            print(f"Patient: {patient.username}, Mood Log: {patient.mood_log}")
    
print(MHWP)