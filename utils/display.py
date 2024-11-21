class MenuDisplay:
    def __init__(self):
        self.breadcrumbs = []
        self.menu_stack = [] 

    def show_breadcrumbs(self):
        """Displays the navigation breadcrumbs.""" 
        if self.breadcrumbs:
            navigation = f"Navigation: {' > '.join(self.breadcrumbs)}"
            print(f"\n{navigation}")
        else:
            print(f"\nNavigation")

    def print_centered_message(self, message):
        """Display centered message."""
        centered_message = message.center(70)
        print(centered_message)

    def print_divider(self, style, length):
        """Prints a styled divider line."""
        print(style * length)

    def print_title(self, title):
        """Prints a title."""
        print(f"\n{title}")

    def display_menu(self, title, options):
        """Displays a menu (main or sub)."""
        self.show_breadcrumbs()
        self.print_divider(style="=", length=70)
        self.print_centered_message(f"🍃 Breeze Mental Health Management System 🍃")
        self.print_centered_message(f"[{title}]")
        self.print_centered_message("Type 'back' at any time to return to the previous menu.")
        self.print_divider(style="=", length=70)
        for index, option in enumerate(options, start=1):
            print(f"[{index}] {option}")
        self.print_divider(style="=", length=70)
        return input(f"Choose an option ⏳: ").strip().lower()

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
                    print(f"No previous menu to return to. Exiting...")
                    break
                print(f"Returning to the previous menu...")
            elif choice.isdigit() and 1 <= int(choice) <= len(current_options):
                current_action_map[str(choice)]()
            else:
                print(f"Invalid choice. Please try again.")



class MenuDisplay:
    def __init__(self):
        self.breadcrumbs = []
        self.menu_stack = [] 

    def show_breadcrumbs(self):
        """Displays the navigation breadcrumbs.""" 
        if self.breadcrumbs:
            navigation = f"Navigation: {' > '.join(self.breadcrumbs)}"
            print(f"\n{navigation}")
        else:
            print(f"\nNavigation")

    def print_centered_message(self, message):
        """Display centered message."""
        centered_message = message.center(70)
        print(centered_message)

    def print_divider(self, style, length):
        """Prints a styled divider line."""
        print(style * length)

    def print_title(self, title):
        """Prints a title."""
        print(f"\n{title}")

    def display_menu(self, title, options):
        """Displays a menu (main or sub)."""
        self.show_breadcrumbs()
        self.print_divider(style="=", length=70)
        self.print_centered_message(f"🍃 Breeze Mental Health Management System 🍃")
        self.print_centered_message(f"[{title}]")
        self.print_centered_message("Type 'back' at any time to return to the previous menu.")
        self.print_divider(style="=", length=70)
        for index, option in enumerate(options, start=1):
            print(f"[{index}] {option}")
        self.print_divider(style="=", length=70)
        
        # Change the color of 'Choose an option' prompt to RED
        return input(f"\033[91mChoose an option ⏳: \033[0m").strip().lower()  # RED color for the prompt

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
                    print(f"No previous menu to return to. Exiting...")
                    break
                print(f"Returning to the previous menu...")
            elif choice.isdigit() and 1 <= int(choice) <= len(current_options):
                current_action_map[str(choice)]()
            else:
                print(f"Invalid choice. Please try again.")
