import json
class Character:
  def __init__(self,name, physical_state = "healthy", mental_state = "happy"):
    self.name = name
    self.inventory = []
    self.player_state = {
      "physical_state": physical_state, # healthy, sick, injured, etc.
      "mental_state": mental_state, # calm, stressed, happy, scared, etc.
      "inventory": []
    }

  def display_player_state(self):
    for state in self.player_state:
      print(f"{state}: {self.player_state[state]}")

  def update_player_state(self, state, updated_state):
    self.player_state[state] = updated_state

  def player_state_json(self):
    return json.dumps(self.player_state)

  def display_inventory(self):
    print("Character's inventory:")
    for item in self.inventory:
      print(item, self.inventory[item])

  def add_item(self, item):
      self.inventory.append(item)
      self.player_state["inventory"].append(item)

  def remove_item(self, item):
    if item in self.inventory:
      self.inventory.remove(item)
    if item in self.player_state["inventory"]:
      self.player_state["inventory"].remove(item)