import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from models.user import Patient
from utils.data_handler import *
from controllers.mhwp import MHWPController
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import json



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

"""
==================================
Patient Controller Class
==================================
"""
class PatientController:
    def __init__(self, patient: Patient):
        self.patient = patient
        self.journal_file = "data/patient_journal.json"
        self.mood_file = "data/patient_mood.json"
        self.patient_info_file = "data/patient_info.json"
        self.appointment_file = "data/appointment.json"
        self.request_log_file = "data/mhwp_change_request.json"
        self.mhwp_info_file = "data/mhwp_info.json"

    def display_menu(self, title, options):
        """Generic method to display a menu with subdued styling."""
        print(f"\n{BOLD}{UNDERLINE}{title}{RESET}")
        print("-" * 50)  # Divider line
        for index, option in enumerate(options, start=1):
            # [1] Frame it
            print(f"{BLACK}[{index}]{RESET} {option}")
        print("-" * 50)
        return input(f"{BROWN_RED}Choose an option ⏳: {RESET}")  
    def display_patient_homepage(self):
        """Display the patient homepage."""
        while True:
            user_status = self.patient.status
            print(f"Debug: User status is {user_status}")  # 这里打印出状态，确认是否为 "DISABLED"

            choice = self.display_menu(
                "🏠 Patient Homepage",
                [
                    "Profile",
                    "Journal",
                    "Mood",
                    "Appointments",
                    "Resources",
                    "Log Out",
                ]
            )

            if user_status == "DISABLED":
                if choice != "6":  # 如果用户选择的是不是 Log Out，提示错误
                    print(f"{RED}Your account is disabled. You can only log out.{RESET}")
                    continue  # 重新显示菜单，跳过其他选项的操作
            else:
                # 当状态不是 DISABLED 时，正常处理选项
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

            # 如果选择了 Log Out，就退出
            if choice == "6":  
                print(f"{BOLD}Logging out...{RESET}")
                break
            else:
                # 如果选择无效，提示错误
                print(f"{DARK_GREY}Invalid choice. Please try again.{RESET}")






    # Sub menus
    def profile_menu(self):
        """Display the profile menu."""
        while True:
            choice = self.display_menu(
                "👤 Profile Menu", ["View Profile", "Edit Profile", "Back to Homepage"]
            )
            if choice == "1":
                self.view_profile()
            elif choice == "2":
                self.edit_profile()
            elif choice == "3":
                break
            else:
                print(f"{DARK_GREY}Invalid choice. Please try again.{RESET}")

    def journal_menu(self):
        while True:
            choice = self.display_menu(
                "📔 Journal Menu", ["View Journal Entries", "Add Journal Entry", "Back to Homepage"]
            )
            if choice == "1":
                self.view_journals()
            elif choice == "2":
                self.add_journal()
            elif choice == "3":
                break
            else:
                print(f"{DARK_GREY}Invalid choice. Please try again.{RESET}")

    def mood_menu(self):
        while True:
            choice = self.display_menu(
                "😊 Mood Menu", ["View Mood Log", "Add Mood Entry", "Back to Homepage"]
            )
            if choice == "1":
                self.view_moods()
            elif choice == "2":
                self.add_mood()
            elif choice == "3":
                break
            else:
                print(f"{DARK_GREY}Invalid choice. Please try again.{RESET}")

    def appointment_menu(self):
        while True:
            choice = self.display_menu(
                "📅 Appointment Menu",
                ["View Appointment", "Make New Appointment", "Cancel Appointment", "Back to Homepage"],
            )
            if choice == "1":
                self.view_appointment()
            elif choice == "2":
                self.make_appointment()
            elif choice == "3":
                self.cancel_appointment()
            elif choice == "4":
                break
            else:
                print(f"{DARK_GREY}Invalid choice. Please try again.{RESET}")

    def resource_menu(self):
        while True:
            choice = self.display_menu(
                "🔍 Search Resources", ["Search by Keyword", "Back to Homepage"]
            )
            if choice == "1":
                self.search_by_keyword()
            elif choice == "2":
                break
            else:
                print(f"{DARK_GREY}Invalid choice. Please try again.{RESET}")


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
            mhwp_data = read_json("data/mhwp_info.json")

            for patient in data:
                if patient["patient_id"] == self.patient.user_id:
                    print(f"\nEdit Profile:")
                    while True:
                        choice = self.display_menu(
                            "Select the field you want to edit (Current value in parentheses)",
                            [
                                f"Name (current: {patient['name']})",
                                f"Email (current: {patient['email']})",
                                f"Emergency Contact (current: {patient['emergency_contact_email']})",
                                f"MHWP (current: {patient.get('mhwp_id', 'None')})",
                                "Edit All",
                                "Back to Profile Menu",
                            ]
                        )
                        
                        if choice == "4":
                            self.display_eligible_mhwps(patient["patient_id"], patient["mhwp_id"])
                            return  
                        elif choice == "1":
                            new_name = input("Enter new name: ").strip()
                            if new_name:
                                patient["name"] = new_name
                                print("Name updated successfully.")
                        elif choice == "2":
                            new_email = input("Enter new email: ").strip()
                            if new_email:
                                patient["email"] = new_email
                                print("Email updated successfully.")
                        elif choice == "3":
                            new_contact = input("Enter new emergency contact email: ").strip()
                            if new_contact:
                                patient["emergency_contact_email"] = new_contact
                                print("Emergency contact updated successfully.")
                        elif choice == "5":
                            new_name = input("Enter new name: ").strip()
                            new_email = input("Enter new email: ").strip()
                            new_contact = input("Enter new emergency contact email: ").strip()
                            if new_name:
                                patient["name"] = new_name
                            if new_email:
                                patient["email"] = new_email
                            if new_contact:
                                patient["emergency_contact_email"] = new_contact
                            print("All fields updated successfully.")
                        elif choice == "6":
                            print("Returning to Profile Menu.")
                            break
                        else:
                            print("Invalid choice. Please try again.")

                    save_json(self.patient_info_file, data)
                    break
            else:
                print("Patient not found.")

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
        request_log = read_json(self.request_log_file)
        new_request = {
            "user_id": patient_id,
            "current_mhwp_id": current_mhwp_id,
            "target_mhwp_id": target_mhwp_id,
            "reason": reason,
            "status": "pending",
            "requested_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        request_log.append(new_request)
        save_json(self.request_log_file, request_log)


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
        print("Type your journal, tap enter when you finish:")
        journal_text = input().strip()
        
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
        """Delete a journal entry for the current patient."""
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

    def update_journal(self):
        """Update a journal entry for the current patient."""
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
        """Delete a mood entry for the current patient."""
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

    def update_mood(self):
        """Update a mood entry for the current patient."""
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


# ----------------------------
# Section 4: Appointment methods
# ----------------------------
    def view_appointment(self):
        try:
            patient_info = read_json(self.patient_info_file)
            appointment = read_json(self.appointment_file)

            patient = next((p for p in patient_info if p["patient_id"] == self.patient.user_id), None)
            if not patient:
                print("Patient not found.")
                return
            
            # Filter appointments for the current patient
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
                    selected_date_idx = int(input("Select a date by index: ").strip()) - 1
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
                except Exception as e:
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
                    selected_slot_index = int(input("Select a time slot: ")) - 1
                    if selected_slot_index not in range(len(available_time_slots)):
                        print("❌ Invalid selection.") 
                        continue #return to time slot selection
                    selected_time_slot = available_time_slots[selected_slot_index]
                    break
                except Exception as e:
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
            display_index = int(input("Enter the index of the appointment you want to cancel: "))
            if display_index not in self.appointment_id_map:
                print("Invalid number. Please choose a number from the list above.")
                return
                
            actual_appointment_id = self.appointment_id_map[display_index]

            appointments = read_json(self.appointment_file)
            
            for appointment in appointments:
                if appointment["appointment_id"] == actual_appointment_id:
                    appointment["status"] = "CANCELLED"
                    appointment["last_updated"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                    if save_json(self.appointment_file, appointments):
                        print("✅ Appointment cancelled successfully!")
                        return
            print("❌ Failed to cancel appointment. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

# ----------------------------
# Section 5: Resource methods
# ----------------------------
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
    patient_controller = PatientController(Patient(1, "patient", "password", "name", "email", "emergency_contact_email", 21))
    patient_controller.display_patient_homepage()
