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

from utils.display_manager import DisplayManager


class InputManager:
    def __init__(self):
        self.input_stack = []
        self.display_manager = DisplayManager()

    def handle_user_input(self, prompts, validations):
        """
        Handles user input with support for resets and back navigation.

        Parameters:
        - prompt: The input prompt message.
        - validate: An optional validation function for input. 
                    Should raise an exception or return False for invalid input.
        - allow_reset: If True, allows the user to type "reset" to retry the current input.
        - allow_back: If True, allows the user to type "back" to return to the previous menu.

        Returns:
        - The validated input as a string.
        """
        if len(prompts) != len(validations):
            raise ValueError("The number of prompts and validations must match.")

        # Initialize inputs dictionary
        inputs = {}
        for index in range(len(prompts)):
            prompt = prompts[index]
            validate = validations[index] if validations[index] else None

        while True:
            try:
                user_input = input(prompt).strip()
            
                # Handle reset command
                if user_input.lower() == "reset":
                    if self.input_stack:
                        previous_index, previous_prompt, previous_validate = self.input_stack.pop()
                        index = previous_index - 1  # Step back to the previous input
                        break
                    else:
                        print(f"{RED}No previous input to reset to.{RESET}")
                        continue

                # Handle back command
                if user_input.lower() == "back":
                    if self.display_manager:
                        self.display_manager.back_operation() 
                    else:
                        print(f"{RED}Back navigation is not available.{RESET}")
                        continue

                # Validate input if a validation function is provided
                if validate and callable(validate):
                    if validate(user_input):
                        self.input_stack.append((index, prompt, validate)) # Save the current state
                        inputs[f"field_{index}"] = user_input # Save valid input
                        break 
                    else:
                        print(f"{RED}Invalid input. Please try again.{RESET}")
                        continue
                else:
                    self.input_stack.append((index, prompt, validate))  # Save the current state
                    inputs[f"field_{index}"] = user_input  # Save input without validation
                    break 

            except Exception as e:
                print(f"{RED}Error: {str(e)}{RESET}")

        return inputs