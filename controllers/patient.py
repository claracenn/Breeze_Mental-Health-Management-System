import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from patient_journal_controller import JournalController
from patient_mood_controller import MoodController
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
        #self.journal_controller = JournalController()
        #self.mood_controller = MoodController()
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
                        "Further Adjustments on Journal", ["Delete Journal Entry", "Update Journal Entry", "Back to Homepage"]
                    )
                    if sub_choice == "3":
                        return
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
                self.view_moods()
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
    # 加载患者数据
    def load_patient_data(self):
        """Load patient data from JSON file."""
        try:
            with open(self.patient_info_file, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            print("Patient info file not found.")
            return []
        except json.JSONDecodeError:
            print("Error decoding JSON file.")
            return []

    # 查看患者资料
    def view_profile(self):
        """Display the patient's profile information based on patient ID."""
        data = self.load_patient_data()
        for patient in data:
            if patient["patient_id"] == self.patient.user_id:
                print(f"Name: {patient['name']}")
                print(f"Email: {patient['email']}")
                print(f"Emergency Contact Email: {patient['emergency_contact_email']}")
                print(f"Assigned MHWP ID: {patient['mhwp_id']}")
                return patient
        print("Patient not found.")
        return None
    
    def edit_profile(self):
        """Edit the patient's profile information and save changes to JSON file."""
        data = self.load_patient_data()
        
        # 查找当前患者数据
        for patient in data:
            if patient["patient_id"] == self.patient.user_id:
                # 显示当前信息并请求输入新的信息
                print("Edit Profile:")
                new_email = input(f"Enter new email (current: {patient['email']}): ").strip()
                new_emergency_contact = input(f"Enter new emergency contact email (current: {patient['emergency_contact_email']}): ").strip()

                # 更新信息，如果用户输入了新的值
                if new_email:
                    patient["email"] = new_email
                if new_emergency_contact:
                    patient["emergency_contact_email"] = new_emergency_contact
                
                # 保存更改回 JSON 文件
                self.save_patient_data(data)
                print("Profile updated successfully.")
                return

        print("Patient not found.")

    def save_patient_data(self, data):
        """Save the updated patient data back to the JSON file."""
        try:
            with open(self.patient_info_file, "w") as file:
                json.dump(data, file, indent=4)
            print("Data saved successfully.")
        except Exception as e:
            print(f"Failed to save data: {e}")


    def edit_profile(self):
        """Edit the patient's profile information and save changes to JSON file."""
        data = self.load_patient_data()
        
        # 查找当前患者数据
        for patient in data:
            if patient["patient_id"] == self.patient.user_id:
                # 显示当前信息并请求输入新的信息
                print("Edit Profile:")
                new_name = input(f"Enter new name (current: {patient['name']}): ").strip()
                new_email = input(f"Enter new email (current: {patient['email']}): ").strip()
                new_emergency_contact = input(f"Enter new emergency contact email (current: {patient['emergency_contact_email']}): ").strip()

                # 更新信息，如果用户输入了新的值
                if new_name:
                    patient["name"] = new_name
                if new_email:
                    patient["email"] = new_email
                if new_emergency_contact:
                    patient["emergency_contact_email"] = new_emergency_contact
                
                # 保存更改回 JSON 文件
                self.save_patient_data(data)
                print("Profile updated successfully.")
                return

        print("Patient not found.")

    def save_patient_data(self, data):
        """Save the updated patient data back to the JSON file."""
        try:
            with open(self.patient_info_file, "w") as file:
                json.dump(data, file, indent=4)
            print("Data saved successfully.")
        except Exception as e:
            print(f"Failed to save data: {e}")


    # Section 2: Journal methods
    # View all journals
    def view_journals(self):
        """Display all journals for the current patient in a table format"""
        journals = read_json(self.journal_file)
        
        if not journals:
            print("No journal entries found.")
            return
            
        # Prepare table
        table_data = {
            "Date": [],
            "Journal Entry": []
        }
        
        for journal in journals:
            # Convert timestamp into more readable format
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
        
        # 感觉可以不需要models里的Journal类，直接用字典就行
        #journal = Journal(
        #    patient_id=self.patient.user_id,
        #    timestamp=current_timestamp,
        #    journal_text=journal_text
        #) 
        journal = {
            "patient_id": self.patient.user_id,
            "timestamp": current_timestamp,
            "journal_text": journal_text
        }
        
        if add_entry(self.journal_file, journal):
            print("Journal saved successfully!")
        else:
            print("Failed to save journal. Please try again.")

    # Delete a journal entry
    def delete_journal(self):
        journal_index = int(input("Enter the index of the journal entry you want to delete: ").strip())
        if delete_entry(self.journal_file, journal_index):
            print("Journal entry deleted successfully!")
        else:
            print("Failed to delete journal entry. Please try again.")

    # Update a journal entry
    def update_journal(self):
        journal_index = int(input("Enter the index of the journal entry you want to update: ").strip())
        new_journal_text = input("Enter the new journal text: ").strip()
        if update_entry(self.journal_file, journal_index, {"journal_text": new_journal_text}):
            print("Journal entry updated successfully!")
        else:
            print("Failed to update journal entry. Please try again.")


    # Section 3: Mood methods
    # Display the mood scale
    def display_mood_scale(self):
        print("""
                MOOD SCALE
        ON A SCALE OF 1-6 WHERE ARE YOU RIGHT NOW?
        1 😢   2 😕   3 😐   4 🙂   5 😊   6 😃
        1 - Very Unhappy (Red)
        2 - Unhappy (Light Red)
        3 - Slightly Unhappy (Orange)
        4 - Slightly Happy (Yellow)
        5 - Happy (Light Green)
        6 - Very Happy (Green)
        """)

    # View all Mood
    def view_moods(self):
        """Display all mood logs for the current patient in a table format"""
        moods = self.mood_controller.view_moods(self.patient.user_id)
        
        if not moods:
            print("No mood entries found.")
            return
            
        # Prepare table
        table_data = {
            "Date": [],
            "Mood": [],
            "Comments": []
        }
        
        # Convert mood colour to expression
        mood_to_emoji = {
            "1_red": "😢 (Very Unhappy)",
            "2_light_red": "😕 (Unhappy)",
            "3_orange": "😐 (Slightly Unhappy)",
            "4_yellow": "🙂 (Slightly Happy)",
            "5_light_green": "😊 (Happy)",
            "6_green": "😃 (Very Happy)"
        }
        
        for mood in moods:
            # Convert timestamp into more readable format
            timestamp = datetime.strptime(mood["timestamp"], "%Y-%m-%dT%H:%M:%S")
            formatted_date = timestamp.strftime("%Y-%m-%d %H:%M")
            
            table_data["Date"].append(formatted_date)
            table_data["Mood"].append(mood_to_emoji.get(mood["mood_color"], mood["mood_color"]))
            table_data["Comments"].append(mood["mood_comments"])
        
        # Create and display table
        create_table(
            data=table_data,
            title="Your Mood History",
            display_title=True
        )

    # Add a new mood entry
    def add_mood(self):
        self.display_mood_scale()
        
        while True:
            try:
                print("\nPlease select your mood (1-6):")
                mood_choice = int(input().strip())
                if 1 <= mood_choice <= 6:
                    break
                print("Please enter a number between 1 and 6.")
            except ValueError:
                print("Please enter a valid number between 1 and 6.")

# 可以试试给字加颜色，如下：
# print("🍃\033[1m Welcome to Breeze Mental Health System\033[0m 🍃", end='\n\n')
# Font and color codes (for reference)
    #Red = "\033[31m"  # use for errors
    #Green = "\033[32m"  # use for success messages
    #Yellow = "\033[33m"  # use for warnings or prompts
    #Cyan = "\033[36m"  # use for general information
    #Reset = "\033[0m"  # to reset text to normal
    #Bold = "\033[1m"  # to make text bold

        mood_colors = {
            1: "1_red",
            2: "2_light_red",
            3: "3_orange",
            4: "4_yellow",
            5: "5_light_green",
            6: "6_green"
        }
        mood_color = mood_colors[mood_choice]

        print("Please enter your mood comments:")
        mood_comments = input().strip()

        current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

        mood = Mood(
            patient_id=self.patient.user_id,
            timestamp=current_timestamp,
            mood_color=mood_color,
            mood_comments=mood_comments
        )
        if self.mood_controller.add_mood(mood):
            print("Mood logged successfully!")
        else:
            print("Failed to log mood. Please try again.")

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

