import json
from utils.data_handler import read_json
import os

# Construct path relative to the current script's directory
current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, '..', 'data', 'patient_mood.json')

class MoodController:
    def __init__(self, mood_file=file_path):
        self.mood_file = mood_file

    def load_moods(self):
        """Use data_handler to load the journal"""
        moods = read_json(self.mood_file)
        return moods if moods else []

    def save_moods(self, moods):
        """Save the mood"""
        try:
            with open(self.mood_file, 'w') as file:
                json.dump(moods, file, indent=4)
            return True
        except Exception as e:
            print(f"Error saving moods: {e}")
            return False

    def add_mood(self, mood):
        """Add a new mood entry"""
        moods = self.load_moods()
        
        # Convert Journal object to dictionary
        mood_dict = mood.to_dict()
        
        # Add a new entry
        moods.append(mood_dict)
        
        # Save the renewed moods
        if self.save_moods(moods):
            return True
        return False

    def view_moods(self, patient_id):
        """Browse current user's all moods"""
        moods = self.load_moods()
        
        # Sort in descending order by timestamp (latest first)
        patient_moods = [m for m in moods if m["patient_id"] == patient_id]
        patient_moods.sort(key = lambda x : x["timestamp"], reverse=True)
        
        return patient_moods