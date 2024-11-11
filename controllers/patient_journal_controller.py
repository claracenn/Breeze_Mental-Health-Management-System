import json
import os
from utils.data_handler import read_json

# Construct path relative to the current script's directory
current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, '..', 'data', 'patient_journal.json')

class JournalController:
    def __init__(self, journal_file=file_path):
        self.journal_file = journal_file  

    def load_journals(self):
        """Use data_handler to load the journal"""
        journals = read_json(self.journal_file)
        return journals if journals else []

    def save_journals(self, journals):
        """Save the journal"""
        try:
            with open(self.journal_file, 'w') as file:
                json.dump(journals, file, indent=4)
            return True
        except Exception as e:
            print(f"Error saving journals: {e}")
            return False

    def add_journal(self, journal):
        """Add a new journal entry"""
        journals = self.load_journals()
        
        # Convert Journal object to dictionary
        journal_dict = journal.to_dict()
        
        # Add a new entry
        journals.append(journal_dict)
        
        # Save the renewed journals
        if self.save_journals(journals):
            return True
        return False

    def view_journals(self, patient_id):
        """Browse current user's all journals"""
        journals = self.load_journals()
        
        # Sort in descending order by timestamp (latest first)
        patient_journals = [j for j in journals if j["patient_id"] == patient_id]
        patient_journals.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return patient_journals