class Journal:
    def __init__(self, patient_id, timestamp, journal_text):
        self.patient_id = patient_id
        self.timestamp = timestamp
        self.journal_text = journal_text

    # Convert objects to dictionaries to save into JSON files
    def to_dict(self):
        return {
            "patient_id": self.patient_id,
            "timestamp": self.timestamp,
            "journal_text": self.journal_text
        }