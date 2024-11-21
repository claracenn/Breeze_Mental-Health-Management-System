# --------------------------------------------------------------------------------------------------------------------------------
# This file is used to test the MenuDisplay class.
# Check the structure of main menu and sub menus below.
# Hope this helps you understand how the MenuDisplay class is used to display menus and handle navigation.
# --------------------------------------------------------------------------------------------------------------------------------

"""
Parameters:
- title: Title of the current menu.
- options: List of menu options.
- action_map: Dictionary mapping user input to corresponding actions.
- main_menu_title: Title of the main menu.

Function call guidance: 
1) For main menu (admin/patient/mhwp homepage), just call the navigate_menu function with the required parameters.

2) For sub menus (second, third...layers), fetch the result from the navigate_menu function 
   and check if it is "main_menu". If yes, call the main_menu function again.

3) For actions, call the required function and identify if the user input is "back".
   If yes, call the back_operation function to return to the previous menu.
"""

from utils.display_manager import DisplayManager

class TestController:
    def __init__(self):
        self.display_manager = DisplayManager()

    def main_menu(self):
        title = "🏠 Main Menu"
        options = ["Second Layer", "Exit"]
        action_map = {
        "1": self.second_layer,
        "2": lambda: None,  # Left it to be None to return to log out
        }
        main_menu_title = "🏠 Main Menu"
        self.display_manager.navigate_menu(title, options, action_map, main_menu_title)
        
    def second_layer(self):
        title = "🔍 Second Layer"
        options = ["Action 1", "Third Layer", "Back to Main Menu"]
        action_map = {
            "1": self.action_1,
            "2":self.third_layer,
            "3": lambda: None,  # Left it to be None to return to Main Menu
        }
        main_menu_title = "🏠 Main Menu"
        result = self.display_manager.navigate_menu(title, options, action_map, main_menu_title)
        if result == "main_menu":
            self.main_menu()
    
    def third_layer(self):
        title = "⏰ Third Layer"
        options = ["Action 2", "Back to Main Menu"]
        action_map = {
            "1": self.action_2,
            "2": lambda: None,  # Left it to be None to return to Main Menu
        }
        main_menu_title = "🏠 Main Menu"
        result = self.display_manager.navigate_menu(title, options, action_map, main_menu_title)
        if result == "main_menu":
            self.main_menu()

    def action_1(self):
        print("Enter your details for Action 1:")
        name = input("Enter your name: ").strip()
        if name.lower() == "back": # For actions that ask for user input, use back_operation+layer function to return to layer before input.
            self.display_manager.back_operation()
            self.second_layer()
            return
        age = input("Enter your age: ").strip()
        if age.lower() == "back":
            self.display_manager.back_operation()
            self.second_layer()
            return
        print(f"Name: {name}, Age: {age}")
        print("Action 1 executed!")
            
    def action_2(self):
        print("Enter your details for Action 1:")
        name = input("Enter your name: ").strip()
        if name.lower() == "back":
            self.second_layer()
            return
        age = input("Enter your age: ").strip()
        if age.lower() == "back":
            self.second_layer()
            return
        print(f"Name: {name}, Age: {age}")
        print("Action 2 executed!")
    
if __name__ == "__main__":
    controller = TestController()
    controller.main_menu()
