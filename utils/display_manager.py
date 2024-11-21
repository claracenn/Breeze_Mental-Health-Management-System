# ANSI color codes for styling
import sys

BOLD = "\033[1m"
UNDERLINE = "\033[4m"
RESET = "\033[0m"
RED = "\033[91m"
GREEN = "\033[92m"
CYAN = "\033[96m"
GREY = "\033[90m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
LIGHT_YELLOW = "\033[93m"
ITALIC = "\033[3m"
ORANGE = "\033[1;33m"  


class DisplayManager:
    def __init__(self):
        self.breadcrumbs = []
        self.menu_stack = [] 

    def show_breadcrumbs(self):
        """Displays the navigation breadcrumbs."""
        if self.breadcrumbs:
            navigation = f"Navigation: {' > '.join(self.breadcrumbs)}"
            print(f"\n{GREY}{navigation}{RESET}")
        else:
            print(f"\n{GREY}Navigation{RESET}")

    def print_centered_message(self, message, style):
        """Display centered message."""
        centered_message = message.center(70)
        print(f"{style}{centered_message}{RESET}")

    def print_divider(self, line, length, style):
        """Prints a styled divider line."""
        print(f"{style}{line * length}{RESET}")

    def print_text(self, style, text):
        """Prints a text with styling."""
        print(f"{style}{text}{RESET}")

    def display_menu(self, title, options):
            """Displays a menu (main or sub)."""
            self.show_breadcrumbs()
            self.print_divider(line="=", length=70, style=f"{BOLD}")
            self.print_centered_message(message="🍃 Breeze Mental Health Management System 🍃", style=f"{GREEN}{BOLD}")
            self.print_divider(line="=", length=70, style=f"{BOLD}")
            self.print_text(text=f"{title}", style=f"{MAGENTA}{BOLD}")
            self.print_text(text="Type 'back' at any time to return to the previous menu.", style=f"{GREY}")
            for index, option in enumerate(options, start=1):
                print(f"{ORANGE}[{index}] {RESET}{BOLD}{option}")
            return input(f"{CYAN}Choose an option ⏳: {RESET}").strip().lower()

    def back_operation(self):
        """Handles the back operation (removes menu state and updates breadcrumbs)."""
        if self.menu_stack and self.breadcrumbs:
            self.menu_stack.pop()
            self.breadcrumbs.pop()
            print(f"{GREY}Returning to the previous menu...{RESET}")
        else:
            print(f"{GREY}No previous menu to return to. Exiting...{RESET}")
            sys.exit()

    def navigate_menu(self, title, options, action_map, main_menu_title):
        """Generalized menu navigation."""
        # Check if resetting to the main menu is required before appending
        if len(self.menu_stack) == 0: 
            self.breadcrumbs = [main_menu_title] 
        else:
            self.breadcrumbs.append(title)

        self.menu_stack.append((title, options, action_map))

        while self.menu_stack:
            current_title, current_options, current_action_map = self.menu_stack[-1]
            choice = self.display_menu(current_title, current_options)

            if choice == "back":
                self.back_operation()
                return
            elif choice.isdigit() and int(choice) == len(current_options):
                # If the user is now in main menu, exit the program
                if current_title == main_menu_title:
                    print(f"{RED}Logging out... Goodbye!{RESET}")
                    sys.exit()
                else:
                    # If not in the main menu, reset breadcrumbs and menu stack to the main menu
                    print(f"{CYAN}Returning to the main menu...{RESET}")
                    self.menu_stack.clear()
                    self.breadcrumbs = [main_menu_title]
                    return "main_menu"
            elif choice.isdigit() and 1 <= int(choice) <= len(current_options):
                current_action_map[str(choice)]()
            else:
                print(f"{RED}Invalid choice. Please try again.{RESET}")
    