### Runtime Instructions

Run the "demo_world.py" file and ensure that all files maintain their relative file organization.
You may need to install the "openai" module beforehand. When prompted, enter your OpenAI key. The input will be hidden.
The AI portion of the demo occurs within the "Domain of Azi" dynamic area. It's fairly easy to get there.

There are 2 real endings and 1 game over ending. All endings require you to play the AI portion of the demo.

### System Information

This demo features a feedback loop where players can constantly modify the game state indirectly via actions that are evaluated by a model. Using gpt-4o-mini from OpenAI and its structured outputs API, the system can generate outputs which can be interpreted by the game to update various statistics as well as determine whether the game's progression continues. Such features have been integrated into a typical text-based adventure game to demonstrate how actions prior to the feedback loop can affect the loop itself, and how the results of the feedback loop can affect the aftermath of a scenario.

For example, the player's inventory system is directly referenced during the feedback loop, where some items such as potions are consumed upon usage during combat within the action-outcome evaluation feedback loop. Any consumed items do not reappear once the feedback loop is over.

To accomodate for certain multi-turn actions such as charging magical spells before using them, the user prompt contains a one-turn history stating the previous output from last turn. This also helps to inform the system when determining the statistics of entities that aren't explicitly represented through a data structure, such as enemies.

More details are available in the code. demo_world.py demonstrates how a game can be created by using these modules.