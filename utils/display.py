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

class MenuDisplay:
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

    def print_centered_message(self, message, color):
        """Display centered message."""
        centered_message = message.center(70)
        print(f"{color}{centered_message}{RESET}")

    def print_divider(self, style, length, color):
        """Prints a styled divider line."""
        print(f"{color}{style * length}{RESET}")

    def print_title(self, title):
        """Prints a title with styling."""
        print(f"\n{BOLD}{UNDERLINE}{title}{RESET}")

    def display_menu(self, title, options):
            """Displays a menu (main or sub)."""
            self.show_breadcrumbs()
            self.print_divider(style="=", length=70, color=f"{BOLD}")
            self.print_centered_message("🍃 Breeze Mental Health Management System 🍃", f"{GREEN}{BOLD}")
            self.print_centered_message(f"[{title}]", f"{MAGENTA}")
            self.print_centered_message("Type 'back' at any time to return to the previous menu.", f"{GREY}")
            self.print_divider(style="=", length=70, color=f"{BOLD}")
            for index, option in enumerate(options, start=1):
                print(f"[{index}] {option}")
            return input(f"{CYAN}{ITALIC}Choose an option ⏳: {RESET}").strip().lower()

    def navigate_menu(self, title, options, action_map):
        """Generalized menu navigation."""
        self.menu_stack.append((title, options, action_map))
        self.breadcrumbs.append(title)

        while self.menu_stack:
            current_title, current_options, current_action_map = self.menu_stack[-1]
            choice = self.display_menu(current_title, current_options)
            if choice == "back" or (choice.isdigit() and int(choice) == len(current_options)):
                self.menu_stack.pop()
                self.breadcrumbs.pop()
                if not self.menu_stack:
                    print(f"{GREY}No previous menu to return to. Exiting...{RESET}")
                    break
                print(f"{GREY}Returning to the previous menu...{RESET}")
            elif choice.isdigit() and 1 <= int(choice) <= len(current_options):
                current_action_map[str(choice)]()
            else:
                print(f"{RED}Invalid choice. Please try again.{RESET}")