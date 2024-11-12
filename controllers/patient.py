import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.patient.patient_journal import Journal
from models.patient.patient_mood import Mood
from models.user import Patient
from utils.data_handler import *
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import json

class PatientController:
    def __init__(self, patient: Patient):
        self.patient = patient
        self.journal_file = "data/patient_journal.json"
        self.mood_file = "data/patient_mood.json"
        self.patient_info_file = "data/patient_info.json"

    def display_menu(self, title, options):
        """Generic method to display a menu and get user input."""
        print(f"\n{title}")
        for index, option in enumerate(options, start=1):
            print(f"{index}. {option}")
        return input("Choose an option: ")

    # Main menu
    def display_patient_homepage(self):
        """Display the patient homepage."""
        while True:
            choice = self.display_menu(
                "Welcome to the Patient Homepage",
                [
                    "My Profile",
                    "My Journal",
                    "My Mood",
                    "My Appointments",
                    "Search Resources",
                    "Log Out",
                ],
            )
            if choice == "1":
                self.profile_menu()
            elif choice == "2":
                self.journal_menu()
            elif choice == "3":
                self.mood_menu()
            elif choice == "4":
                self.appointment_menu()
            elif choice == "5":
                self.resource_menu()
            elif choice == "6":
                print("Logging out...")
                break
            else:
                print("Invalid choice. Please try again.")

    # Sub menus
    def profile_menu(self):
        """Display the profile menu."""
        while True:
            choice = self.display_menu(
                "Profile Menu", ["View Profile", "Edit Profile", "Back to Homepage"]
            )
            if choice == "1":
                self.view_profile()
            elif choice == "2":
                self.edit_profile()
            elif choice == "3":
                break
            else:
                print("Invalid choice. Please try again.")

    def journal_menu(self):
        while True:
            choice = self.display_menu(
                "Journal Menu", ["View Journal Entries", "Add Journal Entry", "Back to Homepage"]
            )
            if choice == "1":
                while True:
                    self.view_journals()
                    # Submenu for continue searching
                    sub_choice = self.display_menu(
                        "Further Adjustments on Journal", ["Delete Journal Entry", "Update Journal Entry", "Back to Journal Menu"]
                    )
                    if sub_choice == "3":
                        break
                    elif sub_choice == "1":
                        self.delete_journal()
                    elif sub_choice == "2":
                        self.update_journal()
            elif choice == "2":
                self.add_journal()
            elif choice == "3":
                break
            else:
                print("Invalid choice. Please try again.")

    def mood_menu(self):
        while True:
            choice = self.display_menu(
                "Mood Menu", ["View Mood Log", "Add Mood Entry", "Back to Homepage"]
            )
            if choice == "1":
                while True:
                    self.view_moods()
                    # Submenu for continue searching
                    sub_choice = self.display_menu(
                        "Further Adjustments on Mood", ["Delete Mood Entry", "Update Mood Entry", "Back to Mood Menu"]
                    )
                    if sub_choice == "3":
                        break
                    elif sub_choice == "1":
                        self.delete_mood()
                    elif sub_choice == "2":
                        self.update_mood()
            elif choice == "2":
                self.add_mood()
            elif choice == "3":
                break
            else:
                print("Invalid choice. Please try again.")

    def appointment_menu(self):
        while True:
            choice = self.display_menu(
                "Appointment Menu",
                ["View Appointment", "Make New Appointment", "Edit Appointment", "Back to Homepage"],
            )
            if choice == "1":
                self.view_appointment()
            elif choice == "2":
                self.make_appointment()
            elif choice == "3":
                self.edit_appointment()
            elif choice == "4":
                break
            else:
                print("Invalid choice. Please try again.")

    def resource_menu(self):
        while True:
            choice = self.display_menu(
                "Search Resources", ["Search by Keyword", "Back to Homepage"]
            )
            if choice == "1":
                while True:
                    self.search_by_keyword()
                    # Submenu for continue searching
                    sub_choice = self.display_menu(
                        "Search Resources", ["Continue Searching", "Back to Homepage"]
                    )
                    if sub_choice == "2":
                        return
            elif choice == "2":
                break
            else:
                print("Invalid choice. Please try again.")


    # Section 1: Profile methods
    def view_profile(self):
        """Display the patient's profile information based on patient ID."""
        data = read_json(self.patient_info_file)
        for patient in data:
            if patient["patient_id"] == self.patient.user_id:
                print("\nYour Profile:")
                print(f"Name: {patient['name']}")
                print(f"Email: {patient['email']}")
                print(f"Emergency Contact Email: {patient['emergency_contact_email']}")
                print(f"Assigned MHWP ID: {patient['mhwp_id']}")
                return patient
        print("Patient not found.")
        return None

    def edit_profile(self):
        """Edit the patient's profile information and save changes to JSON file."""
        data = read_json(self.patient_info_file)
        
        for patient in data:
            if patient["patient_id"] == self.patient.user_id:
                # Show current profile information and request new information
                print("\nEdit Profile:")
                new_name = input(f"Enter new name (current: {patient['name']}): ").strip()
                new_email = input(f"Enter new email (current: {patient['email']}): ").strip()
                new_emergency_contact = input(f"Enter new emergency contact email (current: {patient['emergency_contact_email']}): ").strip()

                # Update information if user entered new values
                if new_name:
                    patient["name"] = new_name
                if new_email:
                    patient["email"] = new_email
                if new_emergency_contact:
                    patient["emergency_contact_email"] = new_emergency_contact

                save_json(self.patient_info_file, data)
                print("Profile updated successfully.")
                return

        print("Patient not found.")
        return None

    # Section 2: Journal methods
    # View all journals
    def view_journals(self):
        """Display all journals for the current patient in a table format"""
        journals = read_json(self.journal_file)
       
        if not journals:
            print("No journal entries found.")
            return
        
        # Filter entries for the current patient
        patient_journals = [
        {"index": i, **j} for i, j in enumerate(journals) if j["patient_id"] == self.patient.user_id
        ]

        # Exit if no entries found for this patient
        if not patient_journals:
            print("No journal entries found for this patient.")
            return
    
        # Sort in descending order by timestamp (latest first)
        patient_journals.sort(key=lambda x: x["timestamp"], reverse=True)
            
        # Prepare table
        table_data = {
            "Date": [],
            "Journal Entry": []
        }

        # Create a mapping of user-visible indices to actual indices in the file
        self.current_patient_journal_map = {}  # Maps display index to actual JSON index
        
        for idx, journal in enumerate(patient_journals):
        # Map user-visible index (1-based) to actual JSON file index
            self.current_patient_journal_map[idx + 1] = journal["index"]
            
            # Format timestamp
            timestamp = datetime.strptime(journal["timestamp"], "%Y-%m-%dT%H:%M:%S")
            formatted_date = timestamp.strftime("%Y-%m-%d %H:%M")
            
            table_data["Date"].append(formatted_date)
            table_data["Journal Entry"].append(journal["journal_text"])
        
        # Create and display table
        create_table(
            data=table_data,
            title="Your Journal Entries",
            display_title=True,
            display_index=True
        )
    
    # Add a new journal entry
    def add_journal(self):
        print("Type your journal, tap enter when you finish:")
        journal_text = input().strip()
        
        current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        
        journal = Journal(
           patient_id=self.patient.user_id,
           timestamp=current_timestamp,
           journal_text=journal_text
        ) 
        journal = journal.to_dict()
                
        if add_entry(self.journal_file, journal):
            print("Journal saved successfully!")
        else:
            print("Failed to save journal. Please try again.")

    # Delete a journal entry
    def delete_journal(self):
        journal_index = int(input("Enter the index of the journal entry you want to delete: ").strip())
        # Retrieve the actual index in the JSON file
        actual_index = self.current_patient_journal_map.get(journal_index)
        
        if actual_index is None:
            print("Invalid index for the current patient.")
            return
        
        if delete_entry(self.journal_file, actual_index + 1):
            print("Journal entry deleted successfully!")
        else:
            print("Failed to delete journal entry. Please try again.")

    # Update a journal entry
    def update_journal(self):
        journal_index = int(input("Enter the index of the journal entry you want to update: ").strip())
        # Retrieve the actual index in the JSON file
        actual_index = self.current_patient_journal_map.get(journal_index)
        
        if actual_index is None:
            print("Invalid index for the current patient.")
            return
        
        new_journal_text = input("Enter the new journal text: ").strip()
        if update_entry(self.journal_file, actual_index + 1, {"journal_text": new_journal_text}):
            print("Journal entry updated successfully!")
        else:
            print("Failed to update journal entry. Please try again.")


    # Section 3: Mood methods
    # Display the mood scale
    def display_mood_scale(self):
        # Define ANSI color codes for each mood level
        RED = "\033[91m\033[1m"
        LIGHT_RED = "\033[91m"
        ORANGE = "\033[93m\033[1m"
        YELLOW = "\033[93m"
        LIGHT_GREEN = "\033[92m"
        GREEN = "\033[92m\033[1m"
        RESET = "\033[0m"  # Resets the color to default

        # Print the Mood Scale with colors
        print(f"""
                      MOOD SCALE
        ON A SCALE OF 1-6 WHERE ARE YOU RIGHT NOW?
        
        {RED}1 😢{RESET}   {LIGHT_RED}2 😕{RESET}   {ORANGE}3 😐{RESET}   {YELLOW}4 🙂{RESET}   {LIGHT_GREEN}5 😊{RESET}   {GREEN}6 😃{RESET}

        {RED}1 - Very Unhappy (Red){RESET}
        {LIGHT_RED}2 - Unhappy (Light Red){RESET}
        {ORANGE}3 - Slightly Unhappy (Orange){RESET}
        {YELLOW}4 - Slightly Happy (Yellow){RESET}
        {LIGHT_GREEN}5 - Happy (Light Green){RESET}
        {GREEN}6 - Very Happy (Green){RESET}
        """)


    # View all Mood
    def view_moods(self):
        # Define ANSI color codes for each mood level
        RED = "\033[91m\033[1m"
        LIGHT_RED = "\033[91m"
        ORANGE = "\033[93m\033[1m"
        YELLOW = "\033[93m"
        LIGHT_GREEN = "\033[92m"
        GREEN = "\033[92m\033[1m"
        RESET = "\033[0m"  # Resets the color to default

        """Display all mood logs for the current patient in a table format and map their indices."""
        moods = read_json(self.mood_file)
        
        if not moods:
            print("No mood entries found.")
            return
        
        # Filter for the current patient's mood entries
        patient_moods = [
            {"index": i, **m} for i, m in enumerate(moods) if m["patient_id"] == self.patient.user_id
        ]

        if not patient_moods:
            print("No mood entries found for this patient.")
            return
        
        # Sort moods by timestamp in descending order
        patient_moods.sort(key=lambda x: x["timestamp"], reverse=True)
        
        # Prepare table data and create an index map
        table_data = {
            "Date": [],
            "Mood": [],
            "Comments": []
        }
        self.current_patient_mood_map = {}  # Map user-visible index to JSON index

        # Define mood color and emoji mapping
        mood_to_emoji = {
            "1_red": f"{RED}😢 (Very Unhappy){RESET}",
            "2_light_red": f"{LIGHT_RED}😕 (Unhappy){RESET}",
            "3_orange": f"{ORANGE}😐 (Slightly Unhappy){RESET}",
            "4_yellow": f"{YELLOW}🙂 (Slightly Happy){RESET}",
            "5_light_green": f"{LIGHT_GREEN}😊 (Happy){RESET}",
            "6_green": f"{GREEN}😃 (Very Happy){RESET}"
        }
        
        for idx, mood in enumerate(patient_moods):
            # Map user-visible index to actual JSON index
            self.current_patient_mood_map[idx + 1] = mood["index"]
            
            # Format timestamp
            timestamp = datetime.strptime(mood["timestamp"], "%Y-%m-%dT%H:%M:%S")
            formatted_date = timestamp.strftime("%Y-%m-%d %H:%M")
            
            table_data["Date"].append(formatted_date)
            table_data["Mood"].append(mood_to_emoji.get(mood["mood_color"], mood["mood_color"]))
            table_data["Comments"].append(mood["mood_comments"])
        
        # Display the table
        create_table(
            data=table_data,
            title="Your Mood History",
            display_title=True,
            display_index=True
        )


    # Add a new mood entry
    def add_mood(self):
        self.display_mood_scale()
        
        while True:
            try:
                mood_choice = int(input("\nPlease select your mood (1-6):").strip())
                if 1 <= mood_choice <= 6:
                    break
                print("Please enter a number between 1 and 6.")
            except ValueError:
                print("Please enter a valid number between 1 and 6.")

        mood_colors = {
            1: "1_red",
            2: "2_light_red",
            3: "3_orange",
            4: "4_yellow",
            5: "5_light_green",
            6: "6_green"
        }
        mood_color = mood_colors[mood_choice]

        mood_comments = input("Please enter your mood comments:").strip()

        current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

        mood = Mood(
            patient_id=self.patient.user_id,
            timestamp=current_timestamp,
            mood_color=mood_color,
            mood_comments=mood_comments
        )

        mood = mood.to_dict()

        if add_entry(self.mood_file, mood):
            print("Mood logged successfully!")
        else:
            print("Failed to log mood. Please try again.")

    # Delete a mood entry
    def delete_mood(self):
        mood_index = int(input("Enter the index of the mood entry you want to delete: ").strip())
        
        # Get the actual JSON index from the mapping
        actual_index = self.current_patient_mood_map.get(mood_index)
        
        if actual_index is None:
            print("Invalid index for the current patient.")
            return
                
        if delete_entry(self.mood_file, actual_index + 1):  
            print("Mood entry deleted successfully!")
        else:
            print("Failed to delete mood entry. Please try again.")

    # Update a mood entry
    def update_mood(self):
        mood_index = int(input("Enter the index of the mood entry you want to update: ").strip())
        
        # Get the actual JSON index from the mapping
        actual_index = self.current_patient_mood_map.get(mood_index)
        
        if actual_index is None:
            print("Invalid index for the current patient.")
            return
        
        new_mood_comments = input("Enter the new mood comments: ").strip()
        
        if update_entry(self.mood_file, actual_index + 1, {"mood_comments": new_mood_comments}):  
            print("Mood entry updated successfully!")
        else:
            print("Failed to update mood entry. Please try again.")


    # Section 4: Appointment methods
    def view_appointment(self):
        pass 

    def make_appointment(self):
        pass

    def edit_appointment(self):
        pass

    # Section 5: Resource methods
    def search_by_keyword(self):
        keyword = input("Enter a keyword to search for related resources: ")
        url = f"https://www.freemindfulness.org/_/search?query={keyword}"

        try:
            response = requests.get(url, timeout=10) 
            html_content = response.text 
            soup = BeautifulSoup(html_content, "html.parser")

            results = []
            for div in soup.find_all('div', class_='gtazFe'):
                a_tag = div.find('a')
                if a_tag:
                    title = a_tag.text.strip()
                    href = a_tag['href']
                    results.append({'Title': title, 'URL': href})

            if len(results) == 0:
                # Print the constructed file path and current working directory
                print("Journal file path:", self.journal_file)
                print("Current working directory:", os.getcwd())
                print("No related resources found.")
            else:
                data = {key: [result[key] for result in results] for key in results[0]}
                create_table(data, title="Meditation and Relaxation Resources", display_title=True, display_index=False)

        except requests.exceptions.RequestException as e:
            print(f"An error occurred while fetching the webpage: {e}")


# Testing
if __name__ == "__main__":
    patient_controller = PatientController(Patient(1, "patient", "password", "email", "emergency_contact_email", "mhwp_id"))
    patient_controller.display_patient_homepage()                  

