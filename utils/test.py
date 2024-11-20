from display import MenuDisplay

class TestController:
    def __init__(self):
        self.menu_display = MenuDisplay()  # Instance of MenuDisplay

    def main_menu(self):
        """Main menu for testing."""
        options = ["Submenu 1", "Exit"]
        action_map = {
            "1": self.submenu_1,
            "2": self.exit_program,
        }
        self.menu_display.navigate_menu("Main Menu", options, action_map)

    def submenu_1(self):
        """Submenu for testing."""
        options = ["Action 1", "Back to Main Menu"]
        action_map = {
            "1": self.action_1,
            "2": lambda: None,  # Back to main menu
        }
        self.menu_display.navigate_menu("Submenu 1", options, action_map)

    def action_1(self):
        """Simulates an action."""
        print("Action 1 executed!")
        # After executing an action, return to the previous menu

    def exit_program(self):
        """Exits the program."""
        print("Exiting program...")
        self.menu_display.menu_stack.clear()  # Clear the stack to exit the program

if __name__ == "__main__":
    controller = TestController()
    controller.main_menu()
