from .interface import Interface
from .action import Action

import string

class Item:
    def __init__(self, name: string, desc: string, details = ""):
      self.custom_actions = []
      self.name = name
      self.desc = desc
      self.details = details
      self.interface = Interface()

    def get_name(self):
       return self.name
    
    # Use None to use the default preconditions function.
    # Actions only apply to static scenarios or dynamic scenario aftermaths.
    def add_item_action(self, action_name = "Mysterious Action", precond_func = Action.default_precond_func, action_func = Action.default_action_func):
        if precond_func == None:
            self.custom_actions.append(Action(action_name, Action.default_precond_func, action_func))
        else:
            self.custom_actions.append(Action(action_name, precond_func, action_func))

    # action_name is the search term for removing these actions.
    # Returns true upon a successful removal, else returns false.
    def remove_item_action(self, action_name = ""):
        if action_name == "":
            return False
        for action in self.custom_actions:
            if action.get_name() == action_name:
                self.custom_actions.remove(action)
                return True
        return False       

    # Helper method for the item's actions.
    def inspect(self):
        if self.details != "":
            self.interface.narrate(f"\n[ Inspect ] {self.details}")
        else:
            self.interface.narrate("\n[ Inspect ] There isn't anything notable to inspect.")

    # Used to trigger an interface to interact with the item.
    def item_actions(self):
      self.interface.narrate(f"\n{self.name} - {self.desc}")
      options_list = ["Cancel", "Inspect Item"]
      for action in self.custom_actions:
        options_list.append(action.get_name())
      option = self.interface.get_multiple_choice_response(options_list)
      if option == 0:
        return
      elif option == 1:
        self.inspect()
      else:
        # Calls a custom action.
        self.custom_actions[option - 2].run_action()
