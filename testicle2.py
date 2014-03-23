#!/usr/bin/python
import sys
import random


def get_empty(shot_grid, flag=True):
    indices = []
    for index, state in enumerate(shot_grid):
        if state == "0":
            if flag and find_row(index) % 2 == 0 and index % 2 == 0:
                indices.append(index)
                # print "even", index, state
            elif flag and find_row(index) % 2 != 0 and index % 2 != 0:
                indices.append(index)
                # print "odd", index, state

        else:
            pass
    if not len(indices):
        for index, state in enumerate(shot_grid):
            if state == "0":
                indices.append(index)

    return indices


def ship_search(indices, shot_grid):
    SEA = 0
    AIRCRAFT_CARRIER = 1
    BATTLESHIP = 2
    SUBMARINE = 3
    DESTROYER = 4
    PATROL_BOAT = 5

    SHIPS = [
        (AIRCRAFT_CARRIER, 5),
        (BATTLESHIP, 4),
        (SUBMARINE, 3),
        (DESTROYER, 3),
        (PATROL_BOAT, 2),
    ]
    orientations = {
        'HORIZONTAL': 0,
        'VERTICAL': 1
    }

    ships = list(SHIPS)
    weights = []
    for i in range(0, 100, 1):
        weights.append(0)
    # print "len:", len(weights)
    shot = False
    # for every cell on the board
    for i in range(0, 99, 1):
        # sys.stdout.write(str(i))
        # for every ship remaining
        for ship_type, ship_size in ships:
            # for each possible orientation...
            for orientation in orientations:
                # print orientation, orientations[orientation]
                if orientation == 'HORIZONTAL':
                    func = right
                else:
                    func = down
                cells = ship_scan_o(i, shot_grid, ship_size, func)

                if cells:
                    # print cells
                    for cell in cells:
                        # print "cell:", cell
                        # this is wrong - need to check all are 0 before weights can be updated
                        weights[cell] += 1
                    # print_weights(weights)

    shot = weights.index(max(weights))
    return shot


def print_weights(weights):
    for i, val in enumerate(weights):
        # sys.stdout.write(str(val))
        if (i+1) % 10 == 0:
            # sys.stdout.write("\n")
            pass

def ship_scan_o(start_cell, shot_grid, length, o_func):
    ship_cells = []
    shot = start_cell
    # print repr(o_func)
    for i in range(0, length, 1):
        shot = o_func(shot)
        if shot_grid[shot] != "0":
            return False
        else:
            ship_cells.append(shot)
    return ship_cells


def find_row(i):
    return abs(i / 10) + 1


def up(i):
    """up"""
    shot = i - 10
    if shot < 0:
        shot = False
    return shot


def down(i):
    """down"""
    shot = i + 10
    if shot > 99:
        shot = False
    return shot


def left(i):
    """left"""
    shot = i - 1
    if find_row(shot) < find_row(i):
        shot = False
    return shot


def right(i):
    """right"""
    shot = i + 1
    if shot > 99 or find_row(shot) > find_row(i):
        shot = False
    return shot


def main(shot_grid=None):
    # print "=========================================================================="
    if not shot_grid:
        shot_grid = []
    if len(sys.argv) > 1:
        shot_grid = sys.argv[1]

    if shot_grid:
        shot_grid = shot_grid.split(',')

    #do we still have places to shoot at?
    indices = get_empty(shot_grid)

    shot = False
    if indices and len(indices):
        # go through shot grid and find a hit on a ship not sunk
        for i, state in enumerate(shot_grid):
            if state == "1":
                # print "start:", i, "\n"
                shot = ship_kill(i, shot_grid)
                break

    if not shot:
        # print "searching...\n"
        shot = ship_search(indices, shot_grid)

    # print "***"
    # sys.stdout.write(str(shot))
    # print "\n***\n"
    return str(shot)


def ship_kill(i, shot_grid):
    funcs = [left, up, right, down]
    shot = False
    # search all direction
    for func in funcs:
        target = func(i)
        # if we found an existing hit, try determine orientation
        if target and shot_grid[target] == "1":
            if func.__doc__ == "left" or func.__doc__ == "right":
                # print "horizontal:", func.__doc__, target
                shot = ship_kill_horizontal(target, shot_grid)
            elif func.__doc__ == "up" or func.__doc__ == "down":
                # print "vertical", func.__doc__, target
                shot = ship_kill_vertical(target, shot_grid)
        else:
            pass
            # print "can't find adjoining hit: " + func.__doc__ + ", " + str(target) + ", " + shot_grid[target]

        # print shot
        if shot:
            # print "destroy: " + str(shot), "\n"
            return shot

    #alternatively if we cannot find any consecutive strikes select the first valid unknown
    # print "instead just pick first adjacent unknown cell"
    for func in funcs:
        target = func(i)
        if target and shot_grid[target] == "0":
            # print "look:", func.__doc__
            shot = target

    return shot


def ship_kill_direction(i, shot_grid, funcs):
    shot = None
    start = i
    for func in funcs:
        i = start

        shot = False
        counter = 0
        while not shot:
            counter += 1
            target = func(i)
            # if we find a valid shot to take
            if target and shot_grid[target] == "0":
                # print "shoot: " + func.__doc__ + " " + str(target)
                shot = target
                # print "shot is:", str(shot)
                break
            elif target and shot_grid[target] == "1":
                #otherwise keep looking this direction
                i = func(i)
                # print "looking:", func.__doc__
            elif not target:
                # print "no target:", target
                break
            elif shot_grid[target] == "-1":
                # print "previous miss"
                break
            # make sure we stop looking after our longest ships worth of cells
            elif counter > 5:
                break
        if shot:
            break
    # print "our shot is", shot
    return shot


def ship_kill_horizontal(i, shot_grid):
    funcs = [right, left]
    # print "looking horizontal...\n"
    return ship_kill_direction(i, shot_grid, funcs)


def ship_kill_vertical(i, shot_grid):
    funcs = [down, up]
    # print "looking vertical...\n"
    return ship_kill_direction(i, shot_grid, funcs)


if __name__ == "__main__":
    main()
