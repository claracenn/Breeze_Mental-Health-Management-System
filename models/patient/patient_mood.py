class Mood:
    def __init__(self, patient_id, timestamp, mood_color, mood_comments):
        self.patient_id = patient_id
        self.timestamp = timestamp
        self.mood_color = mood_color
        self.mood_comments = mood_comments

    # Convert objects to dictionaries to save into JSON files
    def to_dict(self):
        return {
            "patient_id": self.patient_id,
            "timestamp": self.timestamp,
            "mood_color": self.mood_color,
            "mood_comments": self.mood_comments
        }