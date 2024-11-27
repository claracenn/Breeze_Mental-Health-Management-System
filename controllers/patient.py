import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from models.user import Patient
from utils.data_handler import *
from utils.display_manager import DisplayManager
from controllers.mhwp import MHWPController
import urllib.request
import urllib.parse
import ssl
from html.parser import HTMLParser
import pandas as pd
from datetime import datetime, timedelta
from utils.email_helper import send_email


"""
==================================
Initialise ANSI color codes
==================================
"""
BOLD = "\033[1m"
UNDERLINE = "\033[4m"
BLACK = "\033[30m"  
BROWN_RED = "\033[91m"  
DARK_GREY = "\033[90m"
RESET = "\033[0m"
RED = "\033[91m\033[1m"
LIGHT_RED = "\033[91m"
ORANGE = "\033[93m\033[1m"
YELLOW = "\033[93m"
LIGHT_GREEN = "\033[92m"
GREEN = "\033[92m\033[1m"
GREY = "\033[90m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"

"""
==================================
Patient Controller Class
==================================
"""
# ----------------------------
# Homepage and Menus
# ----------------------------
class PatientController:
    def __init__(self, patient):
        self.patient = patient
        self.display_manager = DisplayManager()
        self.journal_file = "data/patient_journal.json"
        self.mood_file = "data/patient_mood.json"
        self.patient_info_file = "data/patient_info.json"
        self.appointment_file = "data/appointment.json"
        self.request_log_file = "data/request_log.json"
        self.mhwp_info_file = "data/mhwp_info.json"
        self.feedback_file = "data/feedback.json"
        self.skip_upcoming_appointments = False

    def get_upcoming_appointments(self):
        """Get appointments within the next 7 days for the patient."""
        current_date = datetime.now()
        seven_days_later = current_date + timedelta(days=7)

        # Read appointment data
        appointments = read_json(self.appointment_file)
        if not appointments:
            return []

        # Read MHWP info to get mhwp_name
        mhwp_info = read_json(self.mhwp_info_file)

        # Filter appointments within the next 7 days for the current patient
        upcoming_appointments = []
        for appointment in appointments:
            if appointment["patient_id"] == self.patient.user_id:
                appointment_date = datetime.strptime(appointment["date"], "%Y-%m-%d")
                if current_date <= appointment_date <= seven_days_later:
                    # Find the MHWP name based on mhwp_id
                    mhwp_id = appointment["mhwp_id"]
                    mhwp_name = next((mhwp["name"] for mhwp in mhwp_info if mhwp["mhwp_id"] == mhwp_id), "Unknown MHWP")
                    appointment["mhwp_name"] = mhwp_name  # Add mhwp_name to the appointment
                    upcoming_appointments.append(appointment)

        return upcoming_appointments

    def display_patient_homepage(self):
        title = "🏠 Patient Homepage"
        main_menu_title = "🏠 Patient Homepage"
        
        options = [
            "Profile",
            "Journal",
            "Mood",
            "Appointments",
            "Resources",
            "Feedback",
            "Log Out",
        ]
        action_map = {
            "1": self.profile_menu,
            "2": self.journal_menu,
            "3": self.mood_menu,
            "4": self.appointment_menu,
            "5": self.resource_menu,
            "6": self.feedback_menu,
            "7": lambda: None,  # Back to Homepage handled in navigate_menu
        }

        # Modify options and actions for disabled patients
        if self.patient.status == "DISABLED":
            print(f"{RED}Your account is disabled. You can only log out.{RESET}")
            options = [f"{option} (Disabled)" for option in options[:-1]] + ["Log Out"]
            action_map = {"7": lambda: print(f"{BOLD}Logging out...{RESET}")}

        # Display upcoming appointments only on the first visit
        if self.skip_upcoming_appointments:
            upcoming_appointments = self.get_upcoming_appointments()
            if upcoming_appointments:
                print(f"{GREEN}\nUpcoming Appointments in the next 7 days:{RESET}")
                for appt in upcoming_appointments:
                    print(f"{BOLD}{appt['date']} {appt['time_slot']} - {appt['status']} with {appt['mhwp_name']}{RESET}")
            else:
                print(f"{LIGHT_GREEN}No appointments in the next 7 days.{RESET}")
            self.skip_upcoming_appointments = True

        # Display upcoming appointments if any
        upcoming_appointments = self.get_upcoming_appointments()
        if upcoming_appointments:
            print(f"{GREEN}\nUpcoming Appointments in the next 7 days:{RESET}")
            for appt in upcoming_appointments:
                print(f"{BOLD}{appt['date']} {appt['time_slot']} - {appt['status']} with {appt['mhwp_name']}{RESET}")
        else:
            print(f"{LIGHT_GREEN}No appointments in the next 7 days.{RESET}")

        # Call the navigate_menu method from the DisplayManager to show the menu
        while True:
            choice = self.display_manager.navigate_menu(title, options, action_map, main_menu_title)

            if choice == "7":
                break  # Log out
            elif choice in action_map:
                if self.patient.status == "DISABLED" and choice != "7":
                    print(f"{RED}Your account is disabled. You can only log out.{RESET}")
                else:
                    action_map[choice]()  # Execute the selected action
            else:
                print(f"{RED}Invalid choice. Please try again.{RESET}")  

    def profile_menu(self):
        """Display the profile menu."""
        title = "👤 Profile Menu"
        main_menu_title = "🏠 Patient Homepage"
        options = ["View Profile", "Edit Profile", "Back to Homepage"]
        action_map = {
            "1": self.view_profile,
            "2": self.edit_profile,
            "3": lambda: None,  # Back to Homepage handled in navigate_menu
        }
        result = self.display_manager.navigate_menu(title, options, action_map, main_menu_title)
        if result == "main_menu":
            self.display_patient_homepage()

    def journal_menu(self):
        title = "📔 Journal Menu"
        main_menu_title = "🏠 Patient Homepage"
        options = ["View Journal Entries", "Add Journal Entry", "Update Journal", "Delete Journal", "Back to Homepage"]
        action_map = {
            "1": self.view_journals,  # Changed to new submenu function
            "2": self.add_journal,
            "3": self.update_journal,
            "4": self.delete_journal,
            "5": lambda: None,  # Back to Homepage handled in navigate_menu
        }
        result = self.display_manager.navigate_menu(title, options, action_map, main_menu_title)
        if result == "main_menu":
            self.display_patient_homepage()

    def mood_menu(self):
        title = "😊 Mood Menu"
        main_menu_title = "🏠 Patient Homepage"
        options = ["View Mood Log", "Add Mood Entry", "Update Mood Entry", "Delete Mood Entry", "Back to Homepage"]
        action_map = {
            "1": self.view_moods,
            "2": self.add_mood,
            "3": self.update_mood,
            "4": self.delete_mood,
            "5": lambda: None,  # Back to Homepage handled in navigate_menu
        }
        result = self.display_manager.navigate_menu(title, options, action_map, main_menu_title)
        if result == "main_menu":
            self.display_patient_homepage()

    def appointment_menu(self):
        title = "📅 Appointment Menu"
        main_menu_title = "🏠 Patient Homepage"
        options = [
            "View Appointment",
            "Make New Appointment",
            "Cancel Appointment",
            "Back to Homepage",
        ]
        action_map = {
            "1": self.view_appointment,
            "2": self.make_appointment,
            "3": self.cancel_appointment,
            "4": lambda: None,  # Back to Homepage handled in navigate_menu
        }
        result = self.display_manager.navigate_menu(title, options, action_map, main_menu_title)
        if result == "main_menu":
            self.display_patient_homepage()

    def resource_menu(self):
        title = "📚 Resource Menu"
        main_menu_title = "🏠 Patient Homepage"
        options = ["Search by Keyword", "Back to Homepage"]
        action_map = {
            "1": self.search_by_keyword,
            "2": lambda: None,  # Back to Homepage handled in navigate_menu
        }
        result = self.display_manager.navigate_menu(title, options, action_map, main_menu_title)
        if result == "main_menu":
            self.display_patient_homepage()

    def feedback_menu(self):
        title = "📚 Feedback Menu"
        main_menu_title = "🏠 Patient Homepage"
        options = ["Provide a feedback", "View your feedbacks", "Back to Homepage"]
        action_map = {
            "1": self.add_feedback,
            "2": self.view_feedback,
            "3": lambda: None,  # Back to Homepage handled in navigate_menu
        }
        result = self.display_manager.navigate_menu(title, options, action_map, main_menu_title)
        if result == "main_menu":
            self.display_patient_homepage()


# ----------------------------
# Section 1: Profile methods
# ----------------------------
    def view_profile(self):
        """Display the patient's profile information based on patient ID."""
        data = read_json(self.patient_info_file)
        for patient in data:
            if patient["patient_id"] == self.patient.user_id:
                print(f"\n{BOLD}Your Profile:{RESET}")
                print(f"🆔 PatientID: {patient['patient_id']}")
                print(f"👤 Name: {patient['name']}")
                print(f"📧 Email: {patient['email']}")
                print(f"📞 Emergency Contact: {patient['emergency_contact_email']}")
                print(f"🏥 Assigned MHWP ID: {patient['mhwp_id']}")
                return patient
        print(f"{DARK_GREY}Patient not found.{RESET}")


    def edit_profile(self):
            """Edit the patient's profile information and save changes to JSON file."""
            data = read_json(self.patient_info_file)

            for patient in data:
                if patient["patient_id"] == self.patient.user_id:
                    print(f"\n{BOLD}📃 Edit Profile:")
                    while True:
                        # Display a simple menu for editing profile
                        print(f"{BOLD}{MAGENTA}\nSelect the field you want to edit:{RESET}")
                        print(f"1. Name (current: {patient['name']})")
                        print(f"2. Email (current: {patient['email']})")
                        print(f"3. Emergency Contact (current: {patient['emergency_contact_email']})")
                        print(f"4. Change MHWP (current: {patient.get('mhwp_id', 'None')})")
                        print(f"5. Edit All")
                        print(f"6. Back to Profile Menu")
                        
                        # Get user choice and handle it
                        choice = input(f"{CYAN}{BOLD}Choose an option ⏳: {RESET}").strip()
                        if choice == "back":
                            self.display_manager.back_operation()
                            self.profile_menu()
                            return
                        if choice == "4":
                            self.display_eligible_mhwps(patient["patient_id"], patient["mhwp_id"])
                            self.profile_menu()
                            return  
                        elif choice == "1":
                            new_name = input("Enter new name: ").strip()
                            if new_name == "back":
                                self.display_manager.back_operation()
                                self.profile_menu()
                                return
                            if new_name:
                                patient["name"] = new_name
                                print(f"{GREEN}Name updated successfully.")
                        elif choice == "2":
                            new_email = input("Enter new email: ").strip()
                            if new_email == "back":
                                self.display_manager.back_operation()
                                self.profile_menu()
                                return
                            if new_email:
                                patient["email"] = new_email
                                print(f"{GREEN}Email updated successfully.")
                        elif choice == "3":
                            new_contact = input("Enter new emergency contact email: ").strip()
                            if new_contact == "back":
                                self.display_manager.back_operation()
                                self.profile_menu()
                                return
                            if new_contact:
                                patient["emergency_contact_email"] = new_contact
                                print(f"{GREEN}Emergency contact updated successfully.")
                        elif choice == "5":
                            new_name = input("Enter new name: ").strip()
                            if new_name == "back":
                                self.display_manager.back_operation()
                                self.profile_menu()
                                return
                            new_email = input("Enter new email: ").strip()
                            if new_email == "back":
                                self.display_manager.back_operation()
                                return
                            new_contact = input("Enter new emergency contact email: ").strip()
                            if new_contact == "back":
                                self.display_manager.back_operation()
                                self.profile_menu()
                                return
                            if new_name:
                                patient["name"] = new_name
                            if new_email:
                                patient["email"] = new_email
                            if new_contact:
                                patient["emergency_contact_email"] = new_contact
                            print(f"{GREEN}All fields updated successfully.")
                        elif choice == "6":
                            print(f"{GREY}Returning to Profile Menu.")
                            break
                        else:
                            print(f"{RED}Invalid choice. Please try again.")
                            
                    # Save the updated data back to the file
                    save_json(self.patient_info_file, data)
                    break
            else:
                print(f"{RED}Patient not found. Please try again.")
                self.profile_menu()


    def display_eligible_mhwps(self, patient_id, current_mhwp_id):
        """Display a list of eligible MHWPs (patient_count < 4) for the patient to select from."""
        
        MHWPController.calculate_patient_counts(self.patient_info_file, "data/mhwp_info.json")
        mhwp_data = read_json("data/mhwp_info.json")

        # Show eligible mhwp
        eligible_mhwps = [mhwp for mhwp in mhwp_data if mhwp.get("patient_count", 0) < 4]
        if not eligible_mhwps:
            print("No available MHWPs with less than 4 patients.")
            return

        print("\nEligible MHWPs:")
        display_data = {
            "MHWP ID": [mhwp["mhwp_id"] for mhwp in eligible_mhwps],
            "Name": [mhwp["name"] for mhwp in eligible_mhwps],
            "Email": [mhwp["email"] for mhwp in eligible_mhwps],
            "Patient Count": [mhwp["patient_count"] for mhwp in eligible_mhwps]
        }
        create_table(display_data, title="Eligible MHWPs", display_title=True, display_index=True)

        selected_idx = int(input("Select a new MHWP by index: ").strip()) - 1
        if 0 <= selected_idx < len(eligible_mhwps):
            new_mhwp_id = eligible_mhwps[selected_idx]["mhwp_id"]
            reason = input("Enter the reason for changing MHWP: ").strip()
            self.create_mhwp_change_request(patient_id, current_mhwp_id, new_mhwp_id, reason)
            print("Your request to change MHWP has been submitted and is pending approval.")
        else:
            print("Invalid selection.")


    def create_mhwp_change_request(self, patient_id, current_mhwp_id, target_mhwp_id, reason):
        """Create a new MHWP change request and save it to request_log.json."""
        # Ensure request_log is initialized properly
        request_log = read_json(self.request_log_file)
        
        # If read_json returns None, initialize an empty list
        if request_log is None:
            request_log = []
        
        new_request = {
            "user_id": patient_id,
            "current_mhwp_id": current_mhwp_id,
            "target_mhwp_id": target_mhwp_id,
            "reason": reason,
            "status": "pending",
            "requested_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # Append the new request
        request_log.append(new_request)

        # Save the updated request log back to the file
        save_json(self.request_log_file, request_log)
        print("Your request to change MHWP has been submitted and is pending approval.")

# ----------------------------
# Section 2: Journal methods
# ----------------------------
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
    

    def add_journal(self):
        """Add a new journal entry for the current patient."""
        journal_text = input(f"{CYAN}{BOLD}Type your journal, tap enter when you finish: {RESET}\n").strip()
        if journal_text == "back":
            self.display_manager.back_operation() 
            self.journal_menu()
            return
        
        current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        
        journal = {
            "patient_id": self.patient.user_id,
            "timestamp": current_timestamp,
            "journal_text": journal_text
        }
                
        if add_entry(self.journal_file, journal):
            print("Journal saved successfully!")
        else:
            print("Failed to save journal. Please try again.")

    def delete_journal(self):
        # display the journal
        self.view_journals()

        """Delete a journal entry for the current patient."""
        journal_index = input(f"{CYAN}{BOLD}Enter the index of the journal entry you want to delete: {RESET}\n").strip()
        if journal_index == "back":
            self.display_manager.back_operation() 
            self.journal_menu()
            return
        journal_index = int(journal_index)
        # Retrieve the actual index in the JSON file
        actual_index = self.current_patient_journal_map.get(journal_index)
        
        if actual_index is None:
            print("Invalid index for the current patient.")
            return
        
        if delete_entry(self.journal_file, actual_index + 1):
            print("Journal entry deleted successfully!")
        else:
            print("Failed to delete journal entry. Please try again.")


    def update_journal(self):
        # Display all journals for the current patient in a table format
        self.view_journals()

        """Update a journal entry for the current patient."""
        journal_index = input(f"{CYAN}{BOLD}Enter the index of the journal entry you want to update: {RESET}\n").strip()
        if journal_index == "back":
            self.display_manager.back_operation() 
            self.journal_menu()
            return
        journal_index = int(journal_index)
        # Retrieve the actual index in the JSON file
        actual_index = self.current_patient_journal_map.get(journal_index)
        
        if actual_index is None:
            print("Invalid index for the current patient.")
            return
        
        # Get the new journal text
        new_journal_text = input(f"{CYAN}{BOLD}Type your new journal text, tap enter when you finish: {RESET}\n").strip()
        if new_journal_text == "back":
            self.display_manager.back_operation() 
            self.journal_menu()
            return
        
        # Update the journal entry in the JSON file
        if update_entry(self.journal_file, actual_index + 1, {"journal_text": new_journal_text}):
            print("Journal entry updated successfully!")
        else:
            print("Failed to update journal entry. Please try again.")

# ----------------------------
# Section 3: Mood methods
# ----------------------------
    def display_mood_scale(self):
        """Display the mood scale with colors and emojis."""
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


    def view_moods(self):
        """Display all mood logs for the current patient."""
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


    def add_mood(self):
        """Add a new mood entry for the current patient."""
        self.display_mood_scale()
        
        while True:
            try:
                mood_choice = input(f"{CYAN}{BOLD}Please select your mood (1-6): {RESET}\n").strip()
                if mood_choice == "back":
                    self.display_manager.back_operation() 
                    self.mood_menu()
                    return
                mood_choice = int(mood_choice)
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

        mood_comments = input(f"{CYAN}{BOLD}Please enter your mood comments: {RESET}\n").strip()
        if mood_comments == "back":
            self.display_manager.back_operation()
            self.mood_menu()
            return

        current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

        mood = {
            "patient_id": self.patient.user_id,
            "timestamp": current_timestamp,
            "mood_color": mood_color,
            "mood_comments": mood_comments
        }

        if add_entry(self.mood_file, mood):
            print("Mood logged successfully!")
        else:
            print("Failed to log mood. Please try again.")


    def delete_mood(self):
        self.view_moods()
        """Delete a mood entry for the current patient."""
        mood_index = input(f"{CYAN}{BOLD}Enter the index of the mood entry you want to delete: {RESET}\n").strip()
        if mood_index == "back":
            self.display_manager.back_operation()
            self.mood_menu()
            return
        mood_index = int(mood_index)

        # Get the actual JSON index from the mapping
        actual_index = self.current_patient_mood_map.get(mood_index)
        
        if actual_index is None:
            print("Invalid index for the current patient.")
            return
                
        if delete_entry(self.mood_file, actual_index + 1):  
            print("Mood entry deleted successfully!")
        else:
            print("Failed to delete mood entry. Please try again.")

    def update_mood(self):
        self.view_moods()
        """Update a mood entry for the current patient."""
        mood_index = input(f"{CYAN}{BOLD}Enter the index of the mood entry you want to update: {RESET}\n").strip()
        if mood_index == "back":
            self.display_manager.back_operation()
            self.mood_menu()
            return
        mood_index = int(mood_index)
        
        # Get the actual JSON index from the mapping
        actual_index = self.current_patient_mood_map.get(mood_index)
        
        if actual_index is None:
            print("Invalid index for the current patient.")
            return
        
        new_mood_comments = input(f"{CYAN}{BOLD}Enter the new mood comments: {RESET}\n").strip()
        if new_mood_comments == "back":
            self.display_manager.back_operation()
            self.mood_menu()
            return
        
        if update_entry(self.mood_file, actual_index + 1, {"mood_comments": new_mood_comments}):  
            print("Mood entry updated successfully!")
        else:
            print("Failed to update mood entry. Please try again.")


# ----------------------------
# Section 4: Appointment methods
# ----------------------------
    def view_appointment(self, status=None):
        try:
            patient_info = read_json(self.patient_info_file)
            appointment = read_json(self.appointment_file)

            patient = next((p for p in patient_info if p["patient_id"] == self.patient.user_id), None)
            if not patient:
                print("Patient not found.")
                return
            
            # Filter appointments for the current patient
            if status:
                patient_appointments = [a for a in appointment if a["patient_id"] == self.patient.user_id and a["status"] == status]
            else:
                patient_appointments = [a for a in appointment if a["patient_id"] == self.patient.user_id]
            if not patient_appointments:
                print("No appointments found for this patient.")
                return
            
            # # Sort appointments by date and time slot
            # try:
            #     patient_appointments.sort(
            #         key=lambda x: (
            #             datetime.strptime(x["date"], "%Y-%m-%d"),
            #             x["time_slot"]
            #         )
            #     )
            # except ValueError as e:
            #     print(f"Warning: Some appointments have invalid date formats. Showing unsorted results.")
            
            # Prepare table data
            mhwp_info = read_json(self.mhwp_info_file)
            
            table_data = {
                "Date": [],
                "Time Slot": [],
                "Your MHWP": [],
                "Notes": [],
                "Status": []
            }

            # Create mapping between display index (the key) and actual appointment ID (the value)
            self.appointment_id_map = {}  
            
            # Populate table data
            for idx, appt in enumerate(patient_appointments, 1):
                self.appointment_id_map[idx] = appt["appointment_id"]  
                table_data["Date"].append(appt.get("date", "N/A"))
                table_data["Time Slot"].append(appt.get("time_slot", "N/A"))
                mhwp_name = next(
                    (m["name"] for m in mhwp_info if m["mhwp_id"] == appt.get("mhwp_id")),
                    "Unknown"
                )
                table_data["Your MHWP"].append(mhwp_name)
                table_data["Notes"].append(appt.get("notes", ""))
                table_data["Status"].append(appt.get("status", "Unknown"))
            
            # Display the table
            create_table(
                data=table_data,
                title="Your Appointments",
                display_title=True,
                display_index=True  # Show display index
            )

        except Exception as e:
            print(f"An error occurred while viewing appointments: {str(e)}")


    def make_appointment(self):
        """Make appointment with MHWP."""
        try:
            patient_info = read_json(self.patient_info_file)
            appointment = read_json(self.appointment_file)
            mhwp_info = read_json(self.mhwp_info_file)

            patient = next((p for p in patient_info if p["patient_id"] == self.patient.user_id), None)
            if not patient:
                print("Patient not found.")
                return
                
            today = datetime.now().date()
            all_dates = [(today + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(1, 8)]
            all_time_slots = [
                "09:00 - 10:00", "10:00 - 11:00", "11:00 - 12:00",
                "14:00 - 15:00", "15:00 - 16:00", "16:00 - 17:00"
                ]
            
            # Display available dates
            while True:
                available_dates = []
                for date in all_dates:
                    mhwp_appointments = [
                        a for a in appointment
                        if a["mhwp_id"] == self.patient.mhwp_id and a["date"] == date and a["status"] in ["PENDING", "CONFIRMED"]
                    ]
                    booked_slots = [a["time_slot"] for a in mhwp_appointments]
                    if len(booked_slots) < len(all_time_slots):
                        available_dates.append(date)

                if not available_dates:
                    print("❗️ No available dates for appointment.")
                    return
                else:
                    print("📅 Available Dates:")
                    for idx, date in enumerate(available_dates, start=1):
                        print(f"{idx}. {date}")
                
                try:
                    # Select date
                    selected_date_idx = input("Select a date by index: ").strip()
                    if selected_date_idx == "back":
                        self.display_manager.back_operation()
                        self.appointment_menu()
                        return
                    selected_date_idx = int(selected_date_idx) - 1
                    if selected_date_idx < 0 or selected_date_idx >= len(available_dates):
                        print("❌ Invalid selection.")
                        continue
                    selected_date = available_dates[selected_date_idx]

                    # Check if the patient already has an appointment on the selected date
                    patient_appointments = [a for a in appointment if a["patient_id"] == self.patient.user_id]
                    if any(a["date"] == selected_date for a in patient_appointments):
                        print("❗️ You already have an appointment on this date. Please choose another date.")
                        continue #return to date selection
                    break
                except ValueError:
                    print("❌ Invalid selection.")
            
            # Display available time slots
            while True:
                mhwp_appointments = [a for a in mhwp_appointments if a["mhwp_id"] == self.patient.mhwp_id 
                                        and a["date"] == selected_date
                                        and a["status"] in ["PENDING", "CONFIRMED"]
                                    ]   
                booked_time_slots = [a["time"] for a in mhwp_appointments]
                available_time_slots = [t for t in all_time_slots if t not in booked_time_slots]
                print("⏰ Available Time Slots:")
                for i, slot in enumerate(available_time_slots, 1):
                    print(f"{i}. {slot}")

                # Select time slot
                try:
                    selected_slot_index = input("Select a time slot: ")
                    if selected_slot_index == "back":
                        self.display_manager.back_operation()
                        self.appointment_menu()
                        return
                    selected_slot_index = int(selected_slot_index) - 1
                    if selected_slot_index not in range(len(available_time_slots)):
                        print("❌ Invalid selection.") 
                        continue #return to time slot selection
                    selected_time_slot = available_time_slots[selected_slot_index]
                    break
                except ValueError:
                    print("❌ Invalid selection.")

            # Confirm appointment
            new_appointment = {
                "appointment_id": len(appointment) + 1,
                "patient_id": self.patient.user_id,
                "mhwp_id": self.patient.mhwp_id,
                "date": selected_date,
                "time_slot": selected_time_slot,
                "status": "PENDING",
                "notes": "",
                "create_time": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                "last_updated": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            }
            
            # Add and save the new appointment
            add_entry(self.appointment_file, new_appointment)
            print("😊 Appointment booked successfully!")
            print(f"📅 Date: {selected_date}, ⏰Time Slot: {selected_time_slot}")

        except Exception as e:
            print(f"An error occurred: {e}")
            

    def cancel_appointment(self):
        self.view_appointment()
        try:
            display_index = input(f"{CYAN}{BOLD}Enter the index of the appointment you want to cancel: {RESET}\n").strip()
            if display_index == "back":
                self.display_manager.back_operation()
                self.appointment_menu()
                return
            try:
                display_index = int(display_index)
                if display_index not in self.appointment_id_map:
                    print("Invalid number. Please choose a number from the list above.")
                    return
            except ValueError:
                print("Invalid input. Please enter a valid number.")
                return
                
            actual_appointment_id = self.appointment_id_map[display_index]

            appointments = read_json(self.appointment_file)
            for appointment in appointments:
                if appointment["appointment_id"] == actual_appointment_id:
                    appointment["status"] = "CANCELLED"
                    appointment["last_updated"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                    if save_json(self.appointment_file, appointments):
                        print("✅ Appointment cancelled successfully!")
                        mhwp_info = read_json(self.mhwp_info_file)
                        mhwp_email = next((m["email"] for m in mhwp_info if m["mhwp_id"] == appointment["mhwp_id"]), None)
                        subject = "Your Patient Canceled an Appointment"
                        message_body = f'''
                            Your Patient Canceled an Appointment.\n
                            Patient Name: {self.patient.name}\n
                            Patient ID: {self.patient.user_id}\n
                            Date: {appointment["date"]}\n
                            Time Slot: {appointment["time_slot"]}\n
                            Breeze Mental Health and Wellbeing App
                        '''
                        if mhwp_email:
                            send_email(mhwp_email, subject, message_body)
                        else:
                            print("❌ Failed to send email to MHWP. Please try again.")

                        return
            print("❌ Failed to cancel appointment. Please try again.")
        except ValueError:
            print("Please enter a valid number.")


# ----------------------------
# Section 5: Resource methods
# ----------------------------
    def search_by_keyword(self):
        """Search for meditation and relaxation resources by keyword."""
        def parse_results(response_content):
            results = []
            is_target_div = False
            is_target_link = False
            current_link = None
            current_title = []

            def handle_starttag(tag, attrs):
                """ HTMLParser callback for handling start tags """
                nonlocal is_target_div, is_target_link, current_link
                attrs_dict = dict(attrs)

                # Detect the target div with class "gtazFe"
                if tag == "div" and attrs_dict.get("class", "").strip() == "gtazFe":
                    is_target_div = True
                # Detect the <a> tag and start accumulating the link and text
                elif is_target_div and tag == "a":
                    is_target_link = True
                    current_link = attrs_dict.get("href")

            def handle_endtag(tag):
                """ HTMLParser callback for handling end tags """
                nonlocal is_target_div, is_target_link, current_link, current_title
                # End of the <a> tag
                if tag == "a" and is_target_link:
                    is_target_link = False
                # End of the target div
                if tag == "div" and is_target_div:
                    is_target_div = False
                    if current_link and current_title:
                        # Join all accumulated title parts and append to results
                        full_title = "".join(current_title).strip()
                        results.append({"Title": full_title, "URL": current_link})
                        current_link = None
                        current_title = []

            def handle_data(data):
                """ HTMLParser callback for handling data """
                nonlocal current_title
                if is_target_link:
                    current_title.append(data)

            # Create the HTML parser
            parser = HTMLParser()
            parser.handle_starttag = handle_starttag
            parser.handle_endtag = handle_endtag
            parser.handle_data = handle_data

            # Feed the parser with the HTML content
            parser.feed(response_content)
            return results

        # Fetch the HTML content and parse results
        keyword = input(f"{CYAN}{BOLD}Enter a keyword to search for related resources 🔍: {RESET}").strip()
        if keyword == "back":
            self.display_manager.back_operation()
            self.resource_menu()
            return

        url = f"https://www.freemindfulness.org/_/search?query={keyword}"

        try:
            context = ssl._create_unverified_context()
            with urllib.request.urlopen(url, context=context) as response:
                html_content = response.read().decode("utf-8")

            results = parse_results(html_content)
            if results:
                print(f"{BOLD}{MAGENTA}Found {len(results)} resource ⬇️ : {RESET}")
                data = {key: [result[key] for result in results] for key in results[0]}
                create_table(data, title="Meditation and Relaxation Resources", display_title=True, display_index=False)
            else:
                print("No related resources found.")

        except Exception as e:
            print(f"Error occurred: {e}")


# ----------------------------
# Section 6: Feedback methods
# ----------------------------
    def add_feedback(self):
        # show all appointments
        self.view_feedback()

        # Let patient choose which appointment to provide feedback for
        while True:
            try:
                display_index = input(f"{CYAN}{BOLD}Enter the index of the appointment you want to provide feedback for: {RESET}\n").strip()
                if display_index == "back":
                    self.display_manager.back_operation()
                    self.feedback_menu()
                    return
                display_index = int(display_index)
                if display_index not in self.appointment_id_map:
                    print("Invalid number. Please choose a number from the list above.")
                    continue
                break
            except ValueError:
                print("Invalid input. Please enter a valid number.")

        # Get the feedback
        feedback_content = input(f"{CYAN}{BOLD}Please enter your feedback: {RESET}\n").strip()
        if feedback_content == "back":
            self.display_manager.back_operation()
            self.feedback_menu()
            return
        
        # Add feedback to feedback.json file
        current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        actual_appointment_id = self.appointment_id_map[display_index]
        feedback = {
            "appointment_id": actual_appointment_id,
            "feedback": feedback_content,
            "create_time": current_timestamp
        }

        if add_entry(self.feedback_file, feedback):
            print("✅ Feedback added successfully!")
            return
        else:
            print("❌ Failed to add feedback. Please try again.")


    def view_feedback(self):
        try:
            patient_info = read_json(self.patient_info_file)
            appointment = read_json(self.appointment_file)
            mhwp_info = read_json(self.mhwp_info_file)
            feedback_info = read_json(self.feedback_file)

            patient = next((p for p in patient_info if p["patient_id"] == self.patient.user_id), None)
            if not patient:
                print("Patient not found.")
                return
            
            # Filter appointments for the current patient
            patient_appointments = [a for a in appointment if a["patient_id"] == self.patient.user_id and a["status"] == "CONFIRMED"]
            if not patient_appointments:
                print("No appointments found for this patient.")
                return
            
            # Prepare table data
            
            
            table_data = {
                "Date": [],
                "Time Slot": [],
                "Your MHWP": [],
                "Notes": [],
                "Your Feedback": []
            }

            # Create mapping between display index (the key) and actual appointment ID (the value)
            self.appointment_id_map = {}  
            
            # Populate table data
            for idx, appt in enumerate(patient_appointments, 1):
                self.appointment_id_map[idx] = appt["appointment_id"]  
                table_data["Date"].append(appt.get("date", "N/A"))
                table_data["Time Slot"].append(appt.get("time_slot", "N/A"))
                mhwp_name = next(
                    (m["name"] for m in mhwp_info if m["mhwp_id"] == appt.get("mhwp_id")),
                    "Unknown"
                )
                table_data["Your MHWP"].append(mhwp_name)
                table_data["Notes"].append(appt.get("notes", ""))
                feedback = next(
                    (f["feedback"] for f in feedback_info if f["appointment_id"] == appt.get("appointment_id")),
                    "N/A"
                )
                table_data["Your Feedback"].append(feedback)
            
            # Display the table
            create_table(
                data=table_data,
                title="Your Feedbacks",
                display_title=True,
                display_index=True  # Show display index
            )

        except Exception as e:
            print(f"An error occurred while viewing feedbacks: {str(e)}")


# Testing
if __name__ == "__main__":
    patient_controller = PatientController(Patient(1, "patient", "password", "name", "email", "emergency_contact_email", 21, "ACTIVE"))
    patient_controller.display_patient_homepage()
