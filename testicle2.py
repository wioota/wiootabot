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
    iteration = 0
    gap = 1
    row = 0
    position = 0
    shot = None
    # keep running through pattern until a shot option is available
    while True:
        shot = position + row * 10
        # print "iterations: ", iteration,"shot: ", shot, "row: ", row, "pos: ", position

        # once off board let's move to next position based on which iteration
        if shot > 99:
            iteration += 1
            position = iteration + iteration * gap
            row = 0
            continue

        if iteration > 9:
            # print "too many iters"
            shot = None
            break

        if shot_grid[shot] == "0":
            # print "somewhere to shoot"
            break

        # move to the new position
        row += gap
        position += gap
        if position > 9:
            position = 0

    if not shot and shot != 0:
        # print "hoohah!\n\m"
        indices = get_empty(shot_grid, False)
        shot = indices[random.randint(0, len(indices) - 1)]
    return shot


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
    sys.stdout.write(str(shot))
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
