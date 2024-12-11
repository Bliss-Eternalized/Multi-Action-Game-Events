import openai
import json
# import os
import getpass # Used for secure input.

class Interface:
    """
    The Interface class is responsible for handling front-end communications with the player.
    It provides methods for other classes to communicate with the player and receive results.
    This also serves as a front-end method for interacting with the OpenAI API when needed.
    """
    def __init__(self):
        # Login is handled in a separate function, such that there is an option for exclusive non-AI usage.
        pass

    # Used to access the OpenAI API.
    def openai_login(self):
        print('Enter OpenAI API key (Hidden Input):')
        # os.environ["OPENAI_API_KEY"] = getpass.getpass()
        # self.client = openai.OpenAI()
        self.client = openai.OpenAI(api_key = getpass.getpass())
    
    # Takes a list of ordered options, prints them, and returns the index of the option selected.
    # Guarantees that a valid option is selected by re-prompting the user until a valid option is retrieved.
    def get_multiple_choice_response(self, options):
        # Checks if a valid number of options exist.
        if len(options) > 0:
            valid_option = False
            option_count = 0
            for option in options:
                option_count += 1
                print(str(option_count)+": "+str(option))
            # Loops until a valid option has been retrieved.
            while (valid_option == False):
                try:
                    response = input("Select an Option:\n> ")
                    if response.lower() == "quit" or response.lower() == "q":
                        exit()
                    response = int(response)
                    # Handles whether the option is out of bounds or not.
                    if response < 1 or option_count < response:
                        print("Invalid Option! Please enter a valid option number.")
                        valid_option = False
                    else:
                        valid_option = True
                except ValueError:
                    # Handles if the option isn't an integer.
                    print("Invalid Input! Please enter a valid option number.")
                    valid_option = False

            # Applies an offset of 1 to compensate for the offset in the option index display.
            response -= 1
            return response
        else:
            pass

    # Prints the text and returns the response of the player.
    def get_free_response(self, text):
        print(text)
        response = input("Player's Response:\n> ")
        if response.lower() == "quit" or response.lower() == "q":
            exit()
        return response

    # Prints the text exclusively.
    def narrate(self, text):
        print(text)
        pass
    
    # Modifies the world/character state in accordance with an AI interpretation of the player's actions.
    # Given a user and system prompt in string format, returns a structured output in dictionary format.
    def evaluate_actions(self, user_prompt = "", system_prompt = ""):
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt}, # Hidden to User
                {"role": "user", "content": user_prompt} # Known to User
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "action_eval",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "new_player_state": {
                                "type": "object",
                                "properties": {
                                    "physical_state": {"type": "string"},
                                    "mental_state": {"type": "string"},
                                    "inventory": {
                                        "type": "array",
                                        "items": {
                                            "type": "string"
                                        },
                                        "description": "Insert names of items from the inventory. Unused items or reusable items should show up in the new inventory. Do not create items that did not exist in the original inventory provided. Remove items from the original inventory that were consumed during the player's actions."
                                    }
                                },
                                "required": ["physical_state", "mental_state", "inventory"],
                                "additionalProperties": False
                            },
                            "text_output": {
                                "type": "string",
                                "description": "Update the player on the new scenario, including how other characters/objects within the scene respond to the player's actions. Maintain the context of the scenario."
                            },
                            "scenario_over": {
                                "type": "boolean",
                                "description": "Returns true if the specified exit mission has been satisfied, else return false."
                            },
                            "game_over":{
                                "type": "boolean",
                                "description": "Evaluate if the player has died during the scenario as a result of external factors or enemies. Return true if so, else return false."
                            }
                        },
                        "required": ["new_player_state", "text_output", "scenario_over", "game_over"],
                        "additionalProperties": False
                    },
                    "strict": True
                }
            }
        )

        # Dictionary with contents matching the specified schema.
        # Note that the response content originally appears in string format.
        results = json.loads(response.choices[0].message.content)

        # self.narrate(f"[ DEBUG ] Generated Results: {results}")
        return results