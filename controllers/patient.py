from models.user import Patient
from utils.table import create_table
import requests
from bs4 import BeautifulSoup
import pandas as pd

class PatientController:
    def __init__(self, patient: Patient):
        self.patient = patient

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
                self.view_journal()
            elif choice == "2":
                self.add_journal_entry()
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
                self.view_mood()
            elif choice == "2":
                self.add_mood_entry()
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
                    elif sub_choice != "1":
                        print("Invalid choice. Please try again.")
            elif choice == "2":
                break
            else:
                print("Invalid choice. Please try again.")

    # Section 1: Profile methods
    def view_profile(self):
        pass

    def edit_profile(self):
        pass

    # Section 2: Journal methods
    def view_journal(self):
        pass    

    def add_journal_entry(self):
        pass

    # Section 3: Mood methods
    def view_mood(self):
        pass

    def add_mood_entry(self):
        pass

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
                print("No related resources found.")
            else:
                data = {key: [result[key] for result in results] for key in results[0]}
                create_table(data, title="Meditation and Relaxation Resources", display_title=True, display_index=False)

        except requests.exceptions.RequestException as e:
            print(f"An error occurred while fetching the webpage: {e}")

# Testing
if __name__ == "__main__":
    patient_controller = PatientController(Patient(1, "patient", "password"))
    patient_controller.display_patient_homepage()

