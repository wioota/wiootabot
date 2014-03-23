#import logging.config
import sys
import inspect
import os
import os.path
import random
import time
import traceback
from operator import itemgetter

# Grids ------------------------------------------------------------------------

class ShipGridSquareState(object):
    SEA =                   0
    AIRCRAFT_CARRIER =      1
    BATTLESHIP =            2
    SUBMARINE =             3
    DESTROYER =             4
    PATROL_BOAT =           5


class ShotGridSquareState(object):
    UNKNOWN =   0
    MISS =      -1
    HIT =       1
    SUNK =      2


class Grid(object):

    SIZE = 10

    def __init__(self, init_val):
        """Populate the grid with an initial value."""
        self.squares = [init_val] * (self.SIZE ** 2)

    def get(self, x, y):
        return self.squares[(y * self.SIZE) + x]

    def put(self, x, y, val):
        self.squares[(y * self.SIZE) + x] = val

    def valid_coord(self, x, y):
        """Return whether x,y are valid grid coordinates."""
        return x >= 0 and x < self.SIZE and y >= 0 and y < self.SIZE

    def rand_square(self):
        """Return the coordinates of a random grid square."""
        x = random.randint(0, self.SIZE-1)
        y = random.randint(0, self.SIZE-1)
        return x, y

    def __str__(self):
        """Return string representation of the grid.

        Used for serialising the grid for transmission to bot script.
        """
        return ','.join(map(str, self.squares))

    @classmethod
    def index_to_coord(cls, i):
        y = i / cls.SIZE
        x = i % cls.SIZE
        return x, y


class ShipGrid(Grid):

    def get_ship_squares(self, ship_type):
        """Generate a list of index positions for the squares that contain the
        ship `ship_type`.
        """
        for i, val in enumerate(self.squares):
            if val == ship_type:
                yield i


# Ship Manager -----------------------------------------------------------------

class ShipManager(object):

    # (ship_type, ship_size)
    SHIPS = [
        (ShipGridSquareState.AIRCRAFT_CARRIER,  5),
        (ShipGridSquareState.BATTLESHIP,        4),
        (ShipGridSquareState.SUBMARINE,         3),
        (ShipGridSquareState.DESTROYER,         3),
        (ShipGridSquareState.PATROL_BOAT,       2),
        ]

    @classmethod
    def arrange_on_grid(cls, ship_grid):
        """Randomly arrange the ships `SHIPS` in the grid `ship_grid`.

        To place a ship, first a random start square in the grid is picked, 
        then a random orientation is picked (horizontal, vertical). The 
        sequence of coordinates in the grid that would occupy the ship given 
        the random start square and orientation is then identified. An attempt 
        to place the ship in this sequence of coordinates is then made. If the 
        attempt fails (see `attempt_to_place_ship_in_seq' for possible reasons) 
        then start again by picking a new random start square.

        Finish when all ships have been successfully placed.
        """

        ships = list(cls.SHIPS)
        random.shuffle(ships)
        for ship_type, ship_size in ships:
            while True:
                r_x, r_y = ship_grid.rand_square()
                if random.choice([True, False]):
                    # vertical
                    seq = [(x, r_y) for x in range(r_x, r_x + ship_size)]
                else:
                    # horizontal
                    seq = [(r_x, y) for y in range(r_y, r_y + ship_size)]
                success = \
                    cls._attempt_to_place_ship_in_seq(
                        ship_grid, ship_type, ship_size, seq)
                if success:
                    break

    @staticmethod
    def _attempt_to_place_ship_in_seq(ship_grid, ship_type, ship_size, seq):
        """Attempt to place the ship of type `ship_type` with length 
        `ship_size` in the grid `ship_grid` in the squares identified by the 
        list of coordinates `seq`.

        The attempt will fail if:
            * Any coordinates are invalid for the grid
            * A square identified by a coordinate already contains a ship part

        Returns whether the ship was successfully placed.
        """

        for x, y in seq:
            if not ship_grid.valid_coord(x, y) or \
                ship_grid.get(x, y) != ShipGridSquareState.SEA:
                return False

        for x, y in seq:
            ship_grid.put(x, y, ship_type)
        return True


# Game Manager -----------------------------------------------------------------

class GameManager(object):

    _BOT_MOVE_TIMEOUT = 10 # max secs a bot can take to make a move

    @classmethod
    def play(cls, bot, seed=None):
        """Generate a random ship arragement and play the game until the bot
        has hit/sunk all ships. The number of moves taken by the bot is
        returned. To make the game deterministic a seed can be provided for
        the random number generator.

        A BotIllegalMoveException is raised if the bot attempts to play an
        illegal move.

        Returns a summary of the game.

            `ships`: a list of grid squares indicating which are occupied by
                ships (1) and which are just sea (0)

            `moves`: a list of moves made by the bot and their outcome, of the
                form [(move_grid_index, hit_or_miss), ...] eg:

                    [(3, -1), (13, 1), (14, 1), (39, -1), ...]

        """

        if seed is None:
            print "NO SEED!"
            seed = random.random()
        random.seed(seed)

        # init game state
        ship_grid = ShipGrid(ShipGridSquareState.SEA)
        shot_grid = Grid(ShotGridSquareState.UNKNOWN)
        ShipManager.arrange_on_grid(ship_grid)

        # repeatedly ask the bot to play moves until all ships are hit/sunk
        try:
            moves = []
            while not cls._all_ships_hit(shot_grid):
                move = cls._play_next_bot_move(bot, ship_grid, shot_grid)
                moves.append(move)
            return {
                "success":      True,
                "moves":        moves,
                "ships":        ship_grid.squares,
                }

        except _BotMoveIllegalException as e:
            data = e.data.copy()
            data.update({
                "success":      False,
                "error":        "Bot made an illegal move",
                "seed":         seed,
                })
            return data

        except _BotMoveTimeoutException:
            return {
                "success":      False,
                "error":        "Bot timeout",
                "seed":         seed,
                }

        except _BotErrorException:
            return {
                "success":      False,
                "error":        "Bot syntax error",
                "seed":         seed,
                }

    @staticmethod
    def _all_ships_hit(shot_grid):
        """Return whether all ships have been hit/sunk.

        This is calculated by comparing the number of hits in the shot grid 
        `hits_made` with the number of squares occupied by ships in the ship 
        grid `hits_to_win`.
        """
        hits_made = len(filter(
            lambda x: x == ShotGridSquareState.SUNK, shot_grid.squares))
        # index 1 of `SHIPS` is the ship size
        hits_to_win = sum(map(itemgetter(1), ShipManager.SHIPS))
        return hits_made == hits_to_win

    @classmethod
    def _play_next_bot_move(cls, bot, ship_grid, shot_grid):
        """Run the bot script against the current `shot_grid` to obtain the
        next move, then attempt to update the `shot_grid` by playing the move.
        """

        bot_move = bot.main(str(shot_grid))
        # validate the bot move
        try:
            bot_move = int(bot_move)
        except ValueError:
            # print "\n", str(shot_grid), str(bot_move), "\n"
            raise _BotMoveIllegalException({
                "game_state":   str(shot_grid),
                "move":         str(bot_move),
                })
        if bot_move < 0 or bot_move >= len(shot_grid.squares):
            # print "\n", str(shot_grid), str(bot_move), "\n"
            raise _BotMoveIllegalException({
                "game_state":   str(shot_grid),
                "move":         bot_move,
                })
        x, y = Grid.index_to_coord(bot_move)
        if shot_grid.get(x, y) != ShotGridSquareState.UNKNOWN:
            # print "\n", str(shot_grid), str(bot_move), "\n"
            raise _BotMoveIllegalException({
                "game_state":   str(shot_grid),
                "move":         bot_move,
                })

        # make bot move
        square_revealed = ship_grid.get(x, y)

        # miss
        if square_revealed == ShipGridSquareState.SEA:
            move_result = ShotGridSquareState.MISS
            shot_grid.put(x, y, ShotGridSquareState.MISS)

        # hit (maybe sunk)
        else:
            move_result = ShotGridSquareState.HIT
            shot_grid.put(x, y, ShotGridSquareState.HIT)

            ship_type = square_revealed
            is_sunk = True
            for i in ship_grid.get_ship_squares(ship_type):
                if shot_grid.squares[i] == ShotGridSquareState.UNKNOWN:
                    is_sunk = False
                    break
                    
            if is_sunk:
                move_result = ShotGridSquareState.SUNK
                for i in ship_grid.get_ship_squares(ship_type):
                    shot_grid.squares[i] = ShotGridSquareState.SUNK
                 
        # return move summary
        return (bot_move, move_result)


class _BotException(Exception):
    """Abstract superclass for all bot exception."""

    def __init__(self, data):
        data["type"] = self.__class__.__name__
        data["msg"] = self.__doc__
        self.data = data

    def __str__(self):
        for k, v in self.data:
            if k == "game_state":
                for i, val in enumerate(v):
                    sys.stdout.write(str(val))
                    if (i+1) % 10 == 0:
                        sys.stdout.write("\n")
        else:
            print k, v

class _BotMoveIllegalException(_BotException): 
    """The bot made an illegal move."""
    pass


class _BotMoveTimeoutException(_BotException): 
    """The bot took too long to make a move."""
    pass


class _BotErrorException(_BotException):
    """The bot encountered an error during execution."""
    pass
    
# Main -------------------------------------------------------------------------
def main():
    module = "testicle2"
    bot_path = os.path.join(os.path.dirname(os.path.abspath(inspect.getsourcefile(lambda _: None))), module + ".py")
    bot = __import__(module)
    summary = GameManager.play(bot)
    print "\n"
    for k, v in summary.items():
        if k == "moves" or k == "ships":
            print k, len(v)
            if k == "ships":
                for i, val in enumerate(v):
                    sys.stdout.write(str(val))
                    if (i+1) % 10 == 0:
                        sys.stdout.write("\n")
            else:
                print v
        else:
            print k,v

    # sys.stdout.write(str(summary))

if __name__ == "__main__":
    main()
