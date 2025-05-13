# WiootaBot

A battleship game bot implementation with grid management and shot prediction algorithms.

## Overview

WiootaBot is a Python-based bot designed to play a battleship-style game. It includes grid management for tracking ship positions and a shot prediction algorithm to optimize targeting.

## Files

### [localmanager3.py](/workspace/wiootabot/localmanager3.py)

This file contains the grid management logic, including:
- Ship grid square state definitions
- Grid initialization and management
- Ship placement logic

```python
class ShipGridSquareState(object):
    SEA =                   0
    AIRCRAFT_CARRIER =      1
    BATTLESHIP =            2
    SUBMARINE =             3
    DESTROYER =             4
    PATROL_BOAT =           5
```

### [testicle2.py](/workspace/wiootabot/testicle2.py)

This file contains the shot prediction algorithm that:
- Analyzes the current game state
- Determines optimal shot placement
- Uses a checkerboard pattern for efficient targeting

```python
def get_empty(shot_grid, flag=True):
    indices = []
    for index, state in enumerate(shot_grid):
        if state == "0":
            if flag and find_row(index) % 2 == 0 and index % 2 == 0:
                indices.append(index)
            elif flag and find_row(index) % 2 != 0 and index % 2 != 0:
                indices.append(index)
```

## Usage

To use the WiootaBot:

1. Import the necessary modules
2. Initialize the game grid
3. Run the bot with appropriate parameters

```python
# Example usage
import localmanager3 as manager
import testicle2 as bot

# Initialize game
# ...

# Run bot
# ...
```

## Contributing

Contributions to improve the bot's strategy or efficiency are welcome. Please ensure your code follows the existing style and includes appropriate documentation.