
class User:
    def __init__(self, user_id, username, password, role):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.role = role
        self.is_disabled = False

class Admin(User):
    def __init__(self, user_id, username, password):
        super().__init__(user_id, username, password, "admin")
        self.mhwps = []  # List of MHWPs
        self.patients = []  # List of patients
    
    def allocate_patient(self, mhwp, patient):
        # Assign a patient to a MHWP
        mhwp.add_patient(patient)

class Patient(User):
    def __init__(self, user_id, username, password):
        super().__init__(user_id, username, password, "patient")
        self.mood_log = []
        self.journal_entries = []
    
    def track_mood(self, mood_color, comments):
        self.mood_log.append((mood_color, comments))
    
    def add_journal_entry(self, entry):
        self.journal_entries.append(entry)

class MHWP(User):
    def __init__(self, user_id, username, password):
        super().__init__(user_id, username, password, "mhwp")
        self.patients = []  # List of assigned patients
        self.appointments = []  # List of appointments

    def add_patient(self, patient):
        self.patients.append(patient)
    
    def manage_appointment(self, appointment):
        self.appointments.append(appointment)
    