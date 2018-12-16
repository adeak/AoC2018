from itertools import count,cycle
from operator import itemgetter
import numpy as np
from scipy.ndimage.morphology import binary_dilation

def print_board(view, units):
    """Print the board"""
    plotview = view.copy()
    for isgoblin,unit in units:
        char = 'G' if isgoblin else 'E'
        plotview[unit[0], unit[1]] = char
    print('\33c')
    print('\n'.join([''.join(row) + f'  {[unit[2] for _,unit in units if unit[0] == i]}' for i,row in enumerate(plotview)]))

def manhattan(pos, other):
    """Compute the Manhattan distance of two array-likes of shape (2,) vs (?,2)"""
    # too slow for many short pairs of coordinates, only use for vectorized group distances
    return np.linalg.norm(np.asarray(pos) - np.asarray(other), ord=1, axis=-1) # scalar or shape (?,)

def next_power(power_interval):
    """Get net elf power level using bisection method"""
    start,end = power_interval
    if not end[1]:
        # elves are dead on right side, double the power
        power = 2 * end[0]
    elif start[1]:
        # elves are alive on the left; not actually going to happen
        power = start[0]//2
    else:
        # otherwise we've got the crossover nailed down
        power = (start[0] + end[0])//2
    return power

def find_nearest_paths(pos, others, sames, view):
    """Find paths to nearest enemy-neighbour, return distance and enemy-neighbour and minimum path"""
    # define a mask for dilation: only dilate where mask is True
    mask = view == '.' # not walls
    mask[tuple(sames.T)] = False # consider friendly units as walls
    mask[tuple(others.T)] = False # consider enemy units as walls (we're looking for "in-range" sites)

    # compute "target" positions: first-manhattan-neighbours of enemy positions except already taken
    other_set = set((tuple(row) for row in others)) # set of enemies
    othermask = np.zeros_like(mask, dtype=bool)
    othermask[tuple(others.T)] = True
    local_others = binary_dilation(othermask, mask=mask).nonzero()
    other_set = set(zip(*local_others)) - other_set # "in range" to an enemy

    parents = {tuple(pos): None} # set of seen coordinates; position -> parent position mapping
    edges = {tuple(pos)} # current edge coordinates
    # paths are traversed from end to root

    for dist in count(1):
        # create a mask where edges are True, dilate, check new edge
        edgeview = np.zeros_like(view, dtype=bool)
        edge_inds = tuple(zip(*edges))
        edgeview[edge_inds] = True
        edgeview = binary_dilation(edgeview, mask=mask)
        mask[edge_inds] = False # keep old edges as seen coordinates
        #edgeview[edge_inds] = False # don't consider previous edges in new edges
        old_edges = edges
        edges = set(zip(*edgeview.nonzero())) - edges # these are the new edges

        if not edges:
            # we didn't find any enemies
            return None

        for new_edge_coord in edges:
            # find the "best" (in reading order) parent edge point for logistics
            parent = min({edge for edge in old_edges if sum(abs(xi-xj) for xi,xj in zip(edge, new_edge_coord)) == 1}) # manhattan would be too slow here
            parents[new_edge_coord] = parent

        found_others = edges & other_set
        if found_others:
            # we've found an enemy, follow the path back to the start
            found = min(found_others)
            reversed_path = [found]
            current = found
            while True:
                parent = parents[current]
                if not parent:
                    path = reversed_path
                    path.reverse()
                    return dist,found,path
                reversed_path.append(parent)
                current = parent


def day15a(inp):
    view = np.array([list(row) for row in inp.split('\n')])
    free = np.isin(view, list('.GE')) # not wall
    goblins = np.array(sorted(zip(*(view == 'G').nonzero(), cycle([200]), cycle([3]), count()))) # (x,y,health,attack,index) tuples, good for sorting
    elves = np.array(sorted(zip(*(view == 'E').nonzero(), cycle([200]), cycle([3]), count()))) # (x,y,health,attack,index) tuples, good for sorting
    view[free] = '.'
    rounds = 0
    while True:
        units = list(sorted(zip([True]*len(goblins) + [False]*len(elves), goblins.tolist() + elves.tolist()), key=itemgetter(1)))
        #print_board(view, units)
        #input()

        for i,(isgoblin,unit) in enumerate(units):
            *pos,health,attack,index = unit
            # skip units that have already been killed
            if health <= 0:
                continue

            # check if game is over mid-round
            livetypes = {isgoblin for isgoblin,unit in units if unit[2]>0}
            if len(livetypes) == 1:
                units = [(j,unit) for j,unit in units if unit[2]>0]
                total = sum(unit[2] for _,unit in units)
                return rounds * total

            # move if out of range, otherwise (or after) attack
            goblins = np.array([unit for isgoblin,unit in units if isgoblin])
            elves = np.array([unit for isgoblin,unit in units if not isgoblin])
            others,sames = (elves,goblins) if isgoblin else (goblins,elves)
            living = others[:,2] >= 1
            dists = manhattan(pos, others[living,:2]) # "crow flies in Manhattan" distance of this unit from every enemy
            inrange = dists.min() == 1
            if not inrange:
                # move if nobody is in range
                nearests = find_nearest_paths(pos, others[living,:2], sames[:,:2], view)
                if not nearests:
                    # no enemy found, go on
                    continue
                dist,nearest,minpath = nearests
                unit[:2] = pos = minpath[1]
                for same in sames:
                    if same[4] == unit[4]:
                        # update position data
                        same[:2] = unit[:2]
                dists = manhattan(pos, others[living,:2]) # recompute
            if dists.min() == 1:
                # now we're in range
                # attack nearest with lowest HP, in reading order among those
                near_inds = dists == 1
                HP = others[living][near_inds, 2]
                minHPs = HP == HP.min()
                choice = min(minHPs.nonzero()[0], key=lambda i:tuple(others[living][near_inds][i,:2]))
                otherpos = others[living][near_inds][choice, :2]
                others[living][near_inds][choice, 2] -= attack
                # if health goes below 1 we'll handle it elsewhere
                # find this in `unit` and change the health there too; that is the source of truth
                for jsgoblin,otherunit in units:
                    if isgoblin ^ jsgoblin:
                        # it's an enemy
                        if np.array_equal(otherpos, otherunit[:2]):
                            otherunit[2] -= attack
        
        # step counter for complete rounds
        rounds += 1
            
        # update units
        new_goblins = []
        new_elves = []
        for isgoblin,unit in units:
            if unit[2] < 1:
                # unit is dead
                continue
            if isgoblin:
                new_goblins.append(unit)
            else:
                new_elves.append(unit)
        goblins = np.array(new_goblins)
        elves = np.array(new_elves)

        # check for endgame (no more units left on one side)
        total = goblins[:,2].sum() if goblins.size else elves[:,2].sum()
        if not goblins.size or not elves.size:
            units = [(j,unit) for j,unit in units if unit[2]>0]
            return rounds * total


def day15b(inp):
    view = np.array([list(row) for row in inp.split('\n')])
    goblin_inds0 = (view == 'G').nonzero()
    elf_inds0 = (view == 'E').nonzero()
    num_elves = (view == 'E').sum()
    free = np.isin(view, list('.GE')) # not wall
    view[free] = '.'
    power_interval = []
    elfpower = 4
    while True:
        # loop over elf powers
        goblins = np.array(sorted(zip(*goblin_inds0, cycle([200]), cycle([3]), count()))) # (x,y,health,attack,index) tuples, good for sorting
        elves = np.array(sorted(zip(*elf_inds0, cycle([200]), cycle([elfpower]), count()))) # (x,y,health,attack,index) tuples, good for sorting
        nextattack = False
        rounds = 0
        while True:
            # loop over rounds, while rather than for loop to easily account for "complete rounds"
            units = list(sorted(zip([True]*len(goblins) + [False]*len(elves), goblins.tolist() + elves.tolist()), key=itemgetter(1)))
    
            for i,(isgoblin,unit) in enumerate(units):
                *pos,health,attack,index = unit
                # skip units that have already been killed
                if health <= 0:
                    continue
    
    
                # check if game is over mid-round
                livetypes = {isgoblin for isgoblin,unit in units if unit[2]>0}
                if len(livetypes) == 1:
                    # this round is over, decide on next
                    nextattack = True
                    break

                # move if out of range, otherwise (or after) attack
                goblins = np.array([unit for isgoblin,unit in units if isgoblin])
                elves = np.array([unit for isgoblin,unit in units if not isgoblin])
                others,sames = (elves,goblins) if isgoblin else (goblins,elves)
                living = others[:,2] >= 1
                dists = manhattan(pos, others[living,:2]) # "crow flies in Manhattan" distance of this unit from every enemy
                inrange = dists.min() == 1
                if not inrange:
                    # move if nobody is in range
                    nearests = find_nearest_paths(pos, others[living,:2], sames[:,:2], view)
                    if not nearests:
                        # no enemy found, go on
                        continue
                    dist,nearest,minpath = nearests
                    unit[:2] = pos = minpath[1]
                    for same in sames:
                        if same[4] == unit[4]:
                            # update position data
                            same[:2] = unit[:2]
                    dists = manhattan(pos, others[living,:2]) # recompute
                if dists.min() == 1:
                    # now we're in range
                    # attack nearest with lowest HP, in reading order among those
                    near_inds = dists == 1
                    HP = others[living][near_inds, 2]
                    minHPs = HP == HP.min()
                    choice = min(minHPs.nonzero()[0], key=lambda i:tuple(others[living][near_inds][i,:2]))
                    otherpos = others[living][near_inds][choice, :2]
                    others[living][near_inds][choice, 2] -= attack
                    # if health goes below 1 we'll handle it elsewhere
                    # find this in `unit` and change the health there too; that is the source of truth
                    for jsgoblin,otherunit in units:
                        if isgoblin ^ jsgoblin:
                            # it's an enemy
                            if np.array_equal(otherpos, otherunit[:2]):
                                otherunit[2] -= attack

            # update units
            new_goblins = []
            new_elves = []
            for isgoblin,unit in units:
                if unit[2] < 1:
                    # unit is dead
                    continue
                if isgoblin:
                    new_goblins.append(unit)
                else:
                    new_elves.append(unit)
            goblins = np.array(new_goblins)
            elves = np.array(new_elves)

            if elves.shape[0] < num_elves or not goblins.size:
                # early exit from fight due to dead elves or the elves won
                nextattack = True

            if nextattack:
                # decide next elf power using bisection method
                # keep track of power, winning state of elves and corresponding "outcome"

                # we either killed all goblins or at least an elf died
                win = goblins.size == 0
                total = sum(elf[2] for elf in elves)
                point = (elfpower, win, rounds*total) # (power, elves_survived, outcome) triple
                if len(power_interval) < 2:
                    # we're still starting up with bisection
                    power_interval = sorted(power_interval + [point]) # sort by elfpower
                    elfpower = elfpower*2 if not win else elfpower//2
                    break

                # if we're here: we've got a full power interval [start, end]
                if not win:
                    # the elves lost, go up in power
                    power_interval = sorted([power_interval[1], point])
                else:
                    # the elves won, go down in power
                    power_interval = sorted([power_interval[0], point])

                if power_interval[1][0] - power_interval[0][0] == 1:
                    # then we must have dead elves on the left and winning elves on the right
                    return power_interval[1][2]

                # otherwise choose next power
                elfpower = next_power(power_interval)
                break

            # step counter for complete rounds
            rounds += 1            


if __name__ == "__main__":
    testinp = open('day15.testinp').read().strip()
    testinp2 = open('day15.testinp2').read().strip()
    testinp3 = open('day15.testinp3').read().strip()
    inp = open('day15.inp').read().strip()
    print(f'part1 test: {day15a(testinp)}')
    print(f'part1 test: {day15a(testinp2)}')
    print(f'part1 test: {day15a(testinp3)}')
    print(f'part1: {day15a(inp)}')
    print(f'part2: {day15b(inp)}')
