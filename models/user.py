class User:
    def __init__(self, user_id, username, password, role):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.role = role

class Admin(User):
    def __init__(self, user_id, username, password):
        super().__init__(user_id, username, password, "admin")

class Patient(User):
    def __init__(self, user_id, username, password, name, email, emergency_contact_email, mhwp_id):
        super().__init__(user_id, username, password, "patient")
        self.name = name
        self.email = email
        self.emergency_contact_email = emergency_contact_email
        self.mhwp_id = mhwp_id

class MHWP(User):
    def __init__(self, user_id, username, password, name, email, patient_count):
        super().__init__(user_id, username, password, "mhwp")
        self.name = name
        self.email = email
        self.patient_count = patient_count
    