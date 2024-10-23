
from models.user import Patient

class PatientController:
    def __init__(self, patient: Patient):
        self.patient = patient

    def edit_profile(self, new_data):
        self.patient.username = new_data.get('username', self.patient.username)
        self.patient.email = new_data.get('email', self.patient.email)

    def track_mood(self, mood_color, comments):
        self.patient.track_mood(mood_color, comments)

    def journal(self, entry):
        self.patient.add_journal_entry(entry)

    def book_appointment(self, mhwp, appointment):
        mhwp.manage_appointment(appointment)
        print("Appointment requested, awaiting confirmation")
    