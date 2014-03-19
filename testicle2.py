#!/usr/bin/python
import sys
import random


def get_empty(shot_grid):
    indices = []
    for index, state in enumerate(shot_grid):
        if state == "0":
            if find_row(index) % 2 == 0 and index % 2 == 0:
                indices.append(index)
                # print "even", index, state
            elif find_row(index) % 2 != 0 and index % 2 != 0:
                indices.append(index)
                # print "odd", index, state
        else:
            pass

    return indices


def ship_search(indices, shot_grid):
    #rn = random.randint(0, len(indices) - 1)
    # go through every 3rd
    """
    iteration = 0
    gap = 2
    row = 0
    counter = 0
    shot = None
    while True:
        # the number of iters
        #c 0 3  6  9  1 4  7  10 2 
        #r 0 3  6  9  0 3  6  9  0
        #s 0 33 66 99 1 34 67 *  2
        shot = counter + row * 10
        #print "iterations: ", iteration,"shot: ", shot, "row: ", row, "cnt: ", counter

        if shot > 99:
            iteration = iteration + 1
            counter = iteration + iteration * gap
            row = 0
            continue

        if iteration > 3:
            shot = None
            break

        if shot_grid[shot] == "0" :
            break

        # move to the new position
        row = row + gap
        counter = counter + gap
    
    if not shot and shot <> 0 :
    """
    global shot
    if True:
        #print "hoohah!"
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
    if shot > 99:
        shot = False
    return shot


def main(shot_grid=None):
    """

    :param shot_grid:
    :return:
    """
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
                shot = ship_kill(i, shot_grid)
                break

    if not shot:
        #print "searching...\n"
        shot = ship_search(indices, shot_grid)

    sys.stdout.write(str(shot))
    #print "\n"
    return str(shot)


def ship_kill(i, shot_grid):
    funcs = [left, up, right, down]
    shot = False
    #search all direction
    search_list = []
    for func in funcs:
        target = func(i)
        search_list.append([func.__doc__, target])
        #if we found an existing hit, try determine orientation
        if target and shot_grid[target] == "1":
            if func.__doc__ == "left" or func.__doc__ == "right":
                shot = ship_kill_horizontal(target, shot_grid)
            elif func.__doc__ == "up" or func.__doc__ == "down":
                shot = ship_kill_vertical(target, shot_grid)
        else:
            pass
            #print "invalid: " + func.__doc__ + ", " + str(target) + ", " + shot_grid[target]

        if shot:
            #print "primary: " + str(shot)
            return shot

    #alternatively if we cannot find any consecutive strikes select the first valid unknown
    #print "alternative"
    for func in funcs:
        target = func(i)
        if target and shot_grid[target] == "0":
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
                #print "shoot: " + func.__doc__ + " " + str(target)
                shot = target
                break
            elif target and shot_grid[target] == "1":
                #otherwise keep looking this direction
                i = func(i)
            elif not target or shot_grid[target] == "-1" or counter > 5:
                break

    return shot


def ship_kill_horizontal(i, shot_grid):
    funcs = [left, right]
    #print "looking horizontal...\n"
    return ship_kill_direction(i, shot_grid, funcs)


def ship_kill_vertical(i, shot_grid):
    funcs = [up, down]
    #print "looking vertical...\n"
    return ship_kill_direction(i, shot_grid, funcs)


if __name__ == "__main__":
    main()
