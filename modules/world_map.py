from .interface import Interface
from .action import Action
from .player import Player
from enum import Enum
import string

class Area_Type(Enum):
    STATIC = 0 # Fixed Planning
    DYNAMIC = 1 # AI-Backed Planning

class Area:
    """
    The Area class is an abstraction of a node for the world map.
    It provides area-specific methods for controlling interactions within the area.

    STATIC SCENARIO:
    Players have access to multiple set options.
    The description is an initial description of the area.
    The details are only reviewed upon inspecting the area.

    DYNAMIC SCENARIO:
    Players can use any option.
    Success depends on an AI evaluation model.
    The description is an initial description of the scenario. Be heavily detailed, as it will be fed into the AI.
    The details are static guidelines for the AI that are not visible to the player. Be heavily detailed, and feel free to break immersion.
    The exit mission states how to leave the scenario. By heavily detailed/specific, as it will be fed into the AI.
    The area converts into a static scenario once the dynamic scenario is over.
    """

    def default_can_enter():
        return True
    
    def __init__(self, name: string, desc: string, details = "", can_enter = default_can_enter):
        # Should refer directly to area objects.
        self.paths = [] # List of areas that the player could traverse to.
        self.area_type = Area_Type.STATIC # Area Type, determines how encounters occur.
        self.name = name # Name of the area.
        self.desc = desc # General description of the area.
        self.details = details # More details upon using inspect.
        self.can_enter = can_enter # Criteria to check whether the player can enter or not.

        self.force_action = False # Forces the player to trigger a specific action upon entry.
        self.custom_actions = [] # Used in static areas, or the aftermath of a dynamic scenario.
    
        self.area_cleared = True # Stores whether the player can leave or not.

        self.interface = Interface()

    # Previous constructor specifies the aftermath of the dynamic scenario.
    def init_DYNAMIC(self, name: string, desc: string, details = "", exit_mission = ""):
        self.area_type = Area_Type.DYNAMIC
        self.area_cleared = False

        # Uploads a copy of the static scenario properties, will restore later once the dynamic scenario is over.
        self.aftermath_name = self.name
        self.aftermath_desc = self.desc
        self.aftermath_details = self.details

        self.name = name # Name of the area.
        self.desc = desc # Description of the initial scenario.
        self.details = details # Hidden details for AI, including output guidelines and world rules.
        self.exit_mission = exit_mission # Criteria to leave the scenario.
    
    def set_interface(self, interface: Interface):
        # Overrides the instance of the interface with the provided one.
        # Used to gain access to the OpenAI API via an interface that the player already logged into.
        self.interface = interface

    def get_name(self):
        return self.name
    
    def get_desc(self):
        return self.desc

    def set_name(self, new_name: string):
        self.name = new_name

    def set_desc(self, new_desc: string):
        self.desc = new_desc

    def set_entry_criteria(self, can_enter = default_can_enter):
        self.can_enter = can_enter

    # Used exclusively for dynamic areas. Long string to be fed into an AI model for evaluation.
    def set_exit_mission(self, exit_mission):
        self.exit_mission = exit_mission

    # Returns all paths.
    def get_paths(self):
        return self.paths
    
    # Creates a path towards another area.
    # Returns True upon successful creation, False if the path already exists.
    def create_path(self, new_area):
        if not (new_area in self.paths):
            self.paths.append(new_area)
            return True
        return False
    
    # Creates a path towards another area, and creates a path from that area back to the current area.
    # No return values.
    def create_2way_path(self, new_area):
        self.create_path(new_area)
        new_area.create_path(self)

    # Removes a path to another area.
    # Returns True upon successful removal, False if the specified path was not found.
    def remove_path(self, target_area):
        if target_area in self.paths:
            self.paths.remove(target_area)
            return True
        return False
    
    # Removes a path towards another area, and removes a path from that area back to the current area.
    # No return values.
    def remove_2way_path(self, target_area):
        self.remove_path(target_area)
        target_area.remove_path(self)

    # Use None to use the default preconditions function.
    # Actions only apply to static scenarios or dynamic scenario aftermaths.
    def add_area_action(self, action_name = "Mysterious Action", precond_func = Action.default_precond_func, action_func = Action.default_action_func):
        if precond_func == None:
            self.custom_actions.append(Action(action_name, Action.default_precond_func, action_func))
        else:
            self.custom_actions.append(Action(action_name, precond_func, action_func))
    
    # action_name is the search term for removing these actions.
    # Returns true upon a successful removal, else returns false.
    def remove_area_action(self, action_name: string):
        for action in self.custom_actions:
            if action.get_name() == action_name:
                self.custom_actions.remove(action)
                return True
        return False   

    # Prompts the player for a list of possible options, or triggers the dynamic scenario depending on the area type.
    # Returns the resulting area from the sequence of actions.
    def area_actions(self, player: Player):
        if Area_Type(self.area_type) == Area_Type.STATIC:
            options_list = ["Navigate to Area", "Inspect Current Area", "Open Inventory"]
            for action in self.custom_actions:
                options_list.append(action.get_name())
            option = self.interface.get_multiple_choice_response(options_list)
            if option == 0:
                self.interface.narrate("\n[ Navigate ] You look around for areas to explore.")
                area = self.navigate()
                # Verifies that leaving the area was successful.
                if bool(area) != False:
                    # Verifies that entering the target area was successful.
                    if area.enter_area() == True:
                        return area
            elif option == 1:
                self.inspect()
            elif option == 2:
                player.inventory_actions()
            else:
                # Calls a custom action.
                self.custom_actions[option - 3].run_action()
            # Ensures that the character stays in the current area.
            return self
        elif Area_Type(self.area_type) == Area_Type.DYNAMIC:
            previous_scenario = "No event has occured previously yet."
            current_scenario = self.desc
            scenario_over = False
            game_over = False
            system_prompt = "Evaluate the proposed actions of the player within the context of the current scenario and determine whether it is plausible, given the player's current capabilities and equipment."
            system_prompt += "\nThe player can only dictate the actions of themselves. Ignore any narrations within the \"Player's Actions\" section that dictate the world state or the state of other characters asides from the player"
            system_prompt += "\nIf the actions are plausible, then generate a description about the state of the player and the effects of the player's actions."
            system_prompt += "\nIf the actions are not plausible, then generate a description about the state of the player and their failed attempt at conducting such actions."
            system_prompt += "\nActions are automatically considered not plausible if they would take more than 10 seconds to conduct the action. In this case, truncate the recognized response, and clearly state that the rest of the actions could not be performed due to a time constraint."
            system_prompt += "\nThen, generate plausible actions from all other characters involved in the scenario asides from the player. Follow the rules provided in the scenario for expected results and restrictions about the game world."
            system_prompt += "\nIn any combat scenario, it is expected for these other characters to prepare to use an attack. If the character has already made preparations during the previous output, then attempt the action."
            system_prompt += "\nIf the player fails to interrupt the preparations for an attack and fails to directly counter the attack itself, then inflict damage on the player. Do not immediately kill the player if they are not in a weakened state."
            system_prompt += "\nExit Mission: \"{self.exit_mission}\". Consider the scenario to be over when the exit mission has been satisfied, and scenario_over should be updated accordingly."
            system_prompt += "\nFor context, the player is a mage from a fantasy world. All powerful magical attacks need to be charged for one turn, and they are considered ready if the previous output indicates that a charge has already been complete."
            system_prompt += "\nIf a charged attack is unused, output that the attack remains charged and is ready for use during the next turn. Similarly, enemies can also charge powerful attacks, but they can also use powerful physical attacks."
            system_prompt += "\nAttempts at charging powerful attacks may be interrupted by the actions of other entities, such as using an attack. Losing focus is not a valid reason; the action should physically interrupt the charge in some way. This applies to both the player and their enemies."
            system_prompt += "\nThe player is considered dead if they have sustained a powerful attack followed by any attack, or if they sustain multiple consecutive normal attacks. Refer to the player's physical health information, and degrade it accordingly with every instance of damage."
            system_prompt += "\nAny character is considered dead if they have passed, fallen, died, been killed, been slain, withered away, etc. Evaluate for whether the exit mission has been satisfied if any death is mentioned."
            system_prompt += "\nNobody is invincible. Other characters should grow weaker from exhaustion as the number of turns continue. If the turn number is greater than 15, then all non-player characters in the scenario should have significantly lower defense, and be more vulnerable to all attacks. Do not state this explicitly."
            system_prompt += "\nDo not create any new characters within the scenario, unless it is a direct result of an explicit summon, such as using a spell to raise undead creatures."
            system_prompt += "\nDo not create any new lines or use any tabs in any output."
            turn = 0 # Tracks the number of turns.
            # Loops until the scenario ends or the game ends.
            while scenario_over == False and game_over == False:
                turn += 1
                # Constructs a string representation of the inventory
                inventory_list = []
                for item in player.inventory:
                    inventory_list.append(item.get_name())

                # Output current information, prompt model with new information.
                self.interface.narrate(f"[ Description ] {current_scenario}")
                response = self.interface.get_free_response("The player is now allowed to make a move. Attempt an action.")
                user_prompt = f"Scenario:\n{current_scenario}\n{self.details}\n\nPlayer's Actions:\n{response}\n\nPlayer's Inventory:\n{inventory_list}\n\nPlayer's State:\n{player.player_state}\n\nPrevious Output:\n{previous_scenario}\n\nTurn Number:\n{turn}"
                results = self.interface.evaluate_actions(user_prompt, system_prompt)

                # Process Results
                previous_scenario = current_scenario
                current_scenario = results["text_output"]
                scenario_over = results["scenario_over"]
                game_over = results["game_over"]

                # Process Player Inventory Changes
                # Only account for removing items, not adding items.
                inventory_list = results["new_player_state"]["inventory"]
                for item in player.inventory:
                    if not item.get_name() in inventory_list: 
                        player.remove_item(item)

                # Process Player State Changes
                player.update_player_state("physical_state", results["new_player_state"]["physical_state"])
                player.update_player_state("mental_state", results["new_player_state"]["mental_state"])

                self.interface.narrate(f"[ DEBUG ] Player's State: {player.player_state}")
                self.interface.narrate(f"[ DEBUG ] Player's Inventory: {player.player_state}")

            # Narrate the conclusion of the scenario.
            self.interface.narrate(f"[ Description ] {current_scenario}")

            # Check for game over state.
            if game_over == True:
                self.interface.narrate("[ Game Over ] The player has died.")
                exit()
            # Scenario is over. Trigger static options.
            self.area_type = Area_Type.STATIC
            
            # Updates area with aftermath details.
            self.name = self.aftermath_name
            self.desc = self.aftermath_desc
            self.details = self.aftermath_details

            # Prints the aftermath.
            self.interface.narrate(f"\n[ Pass ] The scenario has been cleared.")
            self.interface.narrate(f"\nNow Watching {self.name}")
            self.interface.narrate(f"[ Description ] {self.desc}")

            # Recursive call to trigger the area's static actions.
            return self.area_actions(player)
        else:
            return self
    
    # Prompts the player to navigate to an area.
    # Returns the area that the player traversed to, False if there are no paths to traverse or if traversal is blocked.
    def navigate(self):
        if len(self.paths) > 0:
            if self.area_cleared == True:
                options_list = ["Stay Here"]
                for area in self.paths:
                    options_list.append(area.get_name())
                option = self.interface.get_multiple_choice_response(options_list)
                # Triggers the "stay" action.
                if option == 0:
                    return False
                return self.paths[option - 1]
            else:
                self.interface.narrate("\n[ Block ] This area has not been cleared. You cannot leave.")
                return False
        self.interface.narrate("\n[ Block ] Dead end. You cannot leave.")
        return False
    
    # Shows more details about the area.
    def inspect(self):
        if self.details != "":
            self.interface.narrate(f"\n[ Inspect ] {self.details}")
        else:
            self.interface.narrate("\n[ Inspect ] There isn't anything notable to inspect.")
    
    # Returns whether entry was successful or not.
    def enter_area(self):
        if self.can_enter() == True:
            self.interface.narrate(f"\nEntering {self.name}")
            if Area_Type(self.area_type) != Area_Type.DYNAMIC:
                self.interface.narrate(f"[ Description ] {self.desc}")
            return True
        self.interface.narrate(f"\n[ Block ] You are unable to enter \"{self.name}\".")
        return False

class WorldMap:
    """
    The World Map is responsible for storing all areas, and traversing through areas.
    Contains a reference to the player, as this is the actual interface for playing the game.
    """
    def __init__(self, interface: Interface, player: Player):
        self.areas = [] # Stores a list of all areas within the current world map.
        self.starting_area = False
        self.current_area = False
        self.interface = interface
        self.player = player

    # Gets the current area. Returns False if no current area exists.
    def get_current_area(self):
        return self.current_area

    # Adds an area to the world map.
    # The first area added becomes the starting area.
    def add_area(self, new_area: Area):
        if len(self.areas) == 0:
            self.starting_area = new_area
        self.areas.append(new_area)
        # Adds the imported interface with OpenAI access into the area.
        new_area.set_interface(self.interface)
    
    # Resets the current area to the starting area, and returns the starting area. Returns False if no starting area exists.
    def start(self):
        self.current_area = self.starting_area
        if self.starting_area != False:
            self.starting_area.enter_area()
        return self.starting_area
    
    # Triggers the actions of the current area. Automatically updates if it results in traversing to a new area.
    def act(self):
        if self.current_area != False:
            self.current_area = self.current_area.area_actions(self.player)
