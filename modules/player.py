from .character import Character
from .interface import Interface

class Player(Character):
    def __init__(self, name, physical_state = "healthy", mental_state = "happy"):
        super().__init__(name, physical_state, mental_state)
        self.interface = Interface()
    
    def inventory_actions(self):
        if len(self.inventory) > 0:
            options_list = ["Exit Inventory"]
            for item in self.inventory:
                options_list.append(item.get_name())
            option = self.interface.get_multiple_choice_response(options_list)
            # Checks that the "exit" action wasn't triggered.
            if option != 0:
                # Triggers actions for that specific item.
                self.inventory[option - 1].item_actions()
        else:
            self.interface.narrate("Your inventory is empty.")
