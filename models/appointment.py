
class Appointment:
    def __init__(self, patient, mhwp, date_time):
        self.patient = patient
        self.mhwp = mhwp
        self.date_time = date_time
        self.confirmed = False
    