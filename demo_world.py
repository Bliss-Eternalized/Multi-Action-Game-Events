from modules.interface import Interface # Module for I/O with Player, including multiple-choice responses.
from modules.world_map import WorldMap, Area # Modules for creating/navigating the world.
from modules.player import Player # Representation of the player.
from modules.item import Item # Module for items.

interface = Interface()
interface.openai_login() # Login to access the OpenAI API for dynamic areas. Comment out if this isn't being tested.
interface.narrate("Loading into the land of Azi. Respond with q or quit to exit the game.")

"""
Tags List for Output Clarifications
[ Action ]
[ Block ]
[ Description ]
[ Debug ]
[ ##### Check ] - Used to directly indicate outputs as a result of a prerequisite requirement.

"""

player = Player("Player")
# World Map Loader
map = WorldMap(interface, player)

# Blocks & Resolutions
spells = []
# Helpful to print additional messages before returning whether entry was successful
def mana_lock():
    if "mana_break" in spells:
        interface.narrate("[ Ability Check ] With a bit of mana, the gate surrenders to your will and opens.")
        return True
    interface.narrate("[ Ability Check ] You try to open the gate, but it is locked. No physical lock exists.")
    return False

def learn_mana_break_spell():
    if "mana_break" in spells:
        interface.narrate("[ Block ] You have already learned this spell!")
    else:
        interface.narrate("[ Description ] You imagine hands, seeping out of the edge of your vision and clinging onto the locked gates, forcefully pushing them asides as mana ripples around you.")
        interface.narrate("[ Action ] You have learned the mana break spell.")
        spells.append("mana_break")

# Items

magical_staff = Item("Magical Staff", "Used for casting spells.", "Within the ironwood, you find an engraved signature, saying \"G10\".")
smoke_grenade = Item("Smoke Grenade", "Produces a cloud of smoke. May be useful in combat.")
mystery_potion = Item("Mystery Potion", "Effects may vary. Drink at your own risk.", "Liquids aren't supposed to change colors, right?")
mana_choke = Item("Mana Choke Spell Scroll", "Choke your opponents out using your mana.", "An offensive variant of mana break.")
crown = Item("Monarch's Crown", "The fallen crown of Dem-0.", "The combination of gold and obsidian strikes a familiar sense of unfinished business.")

def drink_mystery_potion():
    if "mana_break" in spells:
        interface.narrate("[ Ability Check ] A reward for your patience. Your character gains a new spell.")
        interface.narrate("[ Description ] You imagine hands, now rising from the ground beneath you, resting on the neck of your next target.")
        interface.narrate("[ Action ] You have learned the mana choke spell. This may be used during fights.")
        player.add_item(mana_choke)
    else:
        interface.narrate("[ Ability Check ] You lack any marks of a mage.")
        interface.narrate("[ Action ] Your character develops brute strength.")
        player.update_player_state("physical_state", "strong")
    player.remove_item(mystery_potion)

def wear_crown():
    interface.narrate("[ Ending 1/2 ]")
    interface.narrate("As the crown rests on your head, the entire world around you starts to crumble.")
    interface.get_free_response("Rising from the decaying ground, a spirit greets you.")
    interface.narrate("It pays no attention to your words or actions. With one swift motion of their hand, the world reconstructs itself.")
    interface.narrate("All hail the new monarch. You cannot escape Azi. Ever.")
    exit()

def break_crown():
    interface.narrate("[ Ending 2/2 ]")
    interface.narrate("As the crown shatters from your sheer force, the entire world around you starts to crumble.")
    interface.get_free_response("Rising from the decaying ground, a spirit greets you.")
    interface.narrate("It pays no attention to your words or actions. It tries to make a motion with their hand, but it fails.")
    interface.narrate("The spirit frantically repeats the motion, until it finally resigns in defeat, and returns back to the void.")
    interface.narrate("The last bits of the ground beneath you finally collapse, and you fall.")
    interface.get_free_response("... \n(Enter anything to continue.)")
    interface.narrate("At last, control of your body has been returned to you.")
    interface.narrate("In front of you is a portal to Azi.")
    interface.narrate("You have escaped Azi.")
    exit()

mystery_potion.add_item_action("Drink Mystery Potion", None, drink_mystery_potion)
crown.add_item_action("Wear Crown", None, wear_crown)
crown.add_item_action("Break Crown", None, break_crown)
player.add_item(mystery_potion)
player.add_item(magical_staff)


# More Custom Area Actions
def loot_dem0():
    interface.narrate("[ Description ] You rustle through the layered robes and armor of the body, then you decided that it wasn't worth the effort. So, you snatched the crown instead.")
    interface.narrate("[ Action ] You have acquired the crown. This is available in your inventory.")
    player.add_item(crown)
    domain.remove_area_action("Loot Dem-0's Corpse")

# Create and configure areas.
portal = Area("Portal of Azi", "No one has ever managed to escape Azi before. It's a one-way trip.")
bridge = Area("Bridge", "The portal remains closed. It's too late for regrets.", "Faint hints of mana linger in the air. A stronger presence awaits you.")
gates = Area("Gates of Dem-0", "An imposing gate blocking the entrance to the residence of the monarch of Azi.", "The gate is infused with a mana lock, which can only be undone with a certain spell.")
domain = Area("Remnants of Dem-0", "The monarch of Azi, Dem-0, finally lies still on the pavement.", "It appears that you have defeated the monarch.", mana_lock)
domain.init_DYNAMIC("Domain of Dem-0", "The monarch of Azi, Dem-0, awaits you in combat. Their sword invites you into the domain, as the gate closes behind you. Only one person can leave this domain alive.", "Mystery surrounds the monarch, almost as if the monarch is only a prototype.", "The monarch of Azi, Dem-0, must be killed in combat. End the scenario when the monarch, otherwise known as Dem-0 is dead.")
portal.create_path(bridge)
bridge.create_2way_path(gates)
gates.add_area_action("Learn Mana Break Spell", None, learn_mana_break_spell)
gates.create_2way_path(domain)
domain.add_area_action("Loot Dem-0's Corpse", None, loot_dem0)

# Add areas.
map.add_area(portal)
map.add_area(bridge)
map.add_area(gates)
map.add_area(domain)

# Sample Gameplay Loop
map.start()
while True:
    map.act()