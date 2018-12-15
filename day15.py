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
    print('\n'.join([''.join(row) + f'  {[unit[2] for _,unit in units if unit[0] == i]}' for i,row in enumerate(plotview)]))
    #print(units)

def find_nearest_paths(pos, others, sames, view):
    """Find paths to nearest enemy-neighbour, return distance and enemy-neighbour and minimum path"""
    # define a mask for dilation: only dilate where mask is True
    mask = view == '.' # not walls
    #print(f'find_nearest_paths: sames = {sames}')
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
            parent = min({edge for edge in old_edges if sum(abs(xi-xj) for xi,xj in zip(edge, new_edge_coord))==1})
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


def day15(inp):
    view = np.array([list(row) for row in inp.split('\n')])
    free = np.isin(view, list('.GE')) # not wall
    goblins = np.array(sorted(zip(*(view == 'G').nonzero(), cycle([200]), cycle([3]), count()))) # (x,y,health,attack,index) tuples, good for sorting
    elves = np.array(sorted(zip(*(view == 'E').nonzero(), cycle([200]), cycle([3]), count()))) # (x,y,health,attack,index) tuples, good for sorting
    view[free] = '.'
    for tick in count(1):
        #print(f'starting round {tick}')
        #print('goblins:')
        #print(goblins)
        #print('elves:')
        #print(elves)
        #units = list(zip([True]*len(goblins) + [False]*len(elves), sorted(goblins.tolist() + elves.tolist())))
        units = list(sorted(zip([True]*len(goblins) + [False]*len(elves), goblins.tolist() + elves.tolist()), key=itemgetter(1)))
        #print_board(view, units)
        #input()

        #print_board(view, units)
        #print(goblins)
        #print(elves)

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
                #print(units)
                print(f'game finished _within_ round {tick}, health={total}')
                print_board(view, units)
                return((tick-1)*total)
            # move if out of range, otherwise (or after) attack
            goblins = np.array([unit for isgoblin,unit in units if isgoblin])
            elves = np.array([unit for isgoblin,unit in units if not isgoblin])
            others,sames = (elves,goblins) if isgoblin else (goblins,elves)
            living = others[:,2] >= 1
            dists = abs(pos - others[living,:2]).sum(-1) # "crow flies in Manhattan" distance of this unit from every enemy
            inrange = dists.min() == 1
            if not inrange:
                # move if nobody is in range
                #print(isgoblin,unit)
                nearests = find_nearest_paths(pos, others[living,:2], sames[:,:2], view)
                if not nearests:
                    #print(f'unit {i}: no connected enemy found')
                    # no enemy found, go on
                    continue
                dist,nearest,minpath = nearests
                #print(dist,nearest,minpath)
                unit[:2] = pos = minpath[1]
                for same in sames:
                    if same[4] == unit[4]:
                        # update position data
                        same[:2] = unit[:2]
                dists = abs(pos - others[living,:2]).sum(-1) # recompute
            if dists.min() == 1:
                # now we're in range
                # attack nearest with lowest HP, in reading order among those
                near_inds = dists == 1
                HP = others[living][near_inds, 2]
                minHPs = HP == HP.min()
                choice = min(minHPs.nonzero()[0], key=lambda i:tuple(others[living][near_inds][i,:2]))
                #print(f'neighbour choices: {[(i, HP[i], tuple(others[living][near_inds][i,:2])) for i in range(HP.size)]}')
                #print(f'chosen: {choice}')
                otherpos = others[living][near_inds][choice, :2]
                others[living][near_inds][choice, 2] -= attack
                #print(f'{"G" if isgoblin else "E"} unit {pos} attacked {otherpos}')
                #print(f'unit {i} {pos} attacking...')
                #print(f'units before attack:')
                #print(units)
                # if health goes below 1 we'll handle it elsewhere
                # find this in `unit` and change the health there too; that is the source of truth
                for jsgoblin,otherunit in units:
                    if isgoblin ^ jsgoblin:
                        # it's an enemy
                        #print(otherpos,otherunit[:2])
                        if np.array_equal(otherpos, otherunit[:2]):
                            otherunit[2] -= attack
                #print(f'units after attack:')
                #print(units)
        
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
        #print_board(view, units)
        total = goblins[:,2].sum() if goblins.size else elves[:,2].sum()
        #print(tick, total)
        if not goblins.size or not elves.size:
            print(f'game finished _after_ round {tick}, health={total}')
            units = [(j,unit) for j,unit in units if unit[2]>0]
            print_board(view, units)
            return tick*total


def day15b(inp):
    view = np.array([list(row) for row in inp.split('\n')])
    goblin_inds0 = (view == 'G').nonzero()
    elf_inds0 = (view == 'E').nonzero()
    num_elves = (view == 'E').sum()
    free = np.isin(view, list('.GE')) # not wall
    view[free] = '.'
    #for elfpower in count(4):
    for elfpower in count(34):
        goblins = np.array(sorted(zip(*goblin_inds0, cycle([200]), cycle([3]), count()))) # (x,y,health,attack,index) tuples, good for sorting
        elves = np.array(sorted(zip(*elf_inds0, cycle([200]), cycle([elfpower]), count()))) # (x,y,health,attack,index) tuples, good for sorting
        nextattack = False
        for tick in count(1):
            if nextattack:
                break
            #print(f'starting round {tick}')
            #print('goblins:')
            #print(goblins)
            #print('elves:')
            #print(elves)
            #units = list(zip([True]*len(goblins) + [False]*len(elves), sorted(goblins.tolist() + elves.tolist())))
            units = list(sorted(zip([True]*len(goblins) + [False]*len(elves), goblins.tolist() + elves.tolist()), key=itemgetter(1)))
            #print("\33c")
            #print()
            #print(f'round {tick-1} over...')
            #print_board(view, units)
            #input()
    
            #print_board(view, units)
            #print(goblins)
            #print(elves)
    
            for i,(isgoblin,unit) in enumerate(units):
                *pos,health,attack,index = unit
                # skip units that have already been killed
                if health <= 0:
                    continue
    
    
                # check if game is over mid-round
                livetypes = {isgoblin for isgoblin,unit in units if unit[2]>0}
                if len(livetypes) == 1:
                    elves = [unit for isgoblin,unit in units if unit[2] > 0 and not isgoblin]
                    if len(elves) < num_elves:
                        # at least an elf died
                        print(f"elves didn't win flawlessly with attack {elfpower} _within_ round {tick} (lost {num_elves - len(elves)} elves)")
                        if elves: print((tick-1)*sum(elf[2] for elf in elves))
                        nextattack = True
                        break

                    # else they've won flawlessly
                    total = sum(elf[2] for elf in elves)
                    print(f'Elves finally win flawlessly with attack {elfpower} _within_ round {tick}, health={total}')
                    print_board(view, units)
                    return((tick-1)*total)
                # move if out of range, otherwise (or after) attack
                goblins = np.array([unit for isgoblin,unit in units if isgoblin])
                elves = np.array([unit for isgoblin,unit in units if not isgoblin])
                others,sames = (elves,goblins) if isgoblin else (goblins,elves)
                living = others[:,2] >= 1
                dists = abs(pos - others[living,:2]).sum(-1) # "crow flies in Manhattan" distance of this unit from every enemy
                inrange = dists.min() == 1
                if not inrange:
                    # move if nobody is in range
                    #print(isgoblin,unit)
                    nearests = find_nearest_paths(pos, others[living,:2], sames[:,:2], view)
                    if not nearests:
                        #print(f'unit {i}: no connected enemy found')
                        # no enemy found, go on
                        continue
                    dist,nearest,minpath = nearests
                    #print(dist,nearest,minpath)
                    unit[:2] = pos = minpath[1]
                    for same in sames:
                        if same[4] == unit[4]:
                            # update position data
                            same[:2] = unit[:2]
                    dists = abs(pos - others[living,:2]).sum(-1) # recompute
                if dists.min() == 1:
                    # now we're in range
                    # attack nearest with lowest HP, in reading order among those
                    near_inds = dists == 1
                    HP = others[living][near_inds, 2]
                    minHPs = HP == HP.min()
                    choice = min(minHPs.nonzero()[0], key=lambda i:tuple(others[living][near_inds][i,:2]))
                    #print(f'neighbour choices: {[(i, HP[i], tuple(others[living][near_inds][i,:2])) for i in range(HP.size)]}')
                    #print(f'chosen: {choice}')
                    otherpos = others[living][near_inds][choice, :2]
                    others[living][near_inds][choice, 2] -= attack
                    #print(f'{"G" if isgoblin else "E"} unit {pos} attacked {otherpos}')
                    #print(f'unit {i} {pos} attacking...')
                    #print(f'units before attack:')
                    #print(units)
                    # if health goes below 1 we'll handle it elsewhere
                    # find this in `unit` and change the health there too; that is the source of truth
                    for jsgoblin,otherunit in units:
                        if isgoblin ^ jsgoblin:
                            # it's an enemy
                            #print(otherpos,otherunit[:2])
                            if np.array_equal(otherpos, otherunit[:2]):
                                otherunit[2] -= attack
                    #print(f'units after attack:')
                    #print(units)

            if nextattack:
                break
            
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
            #print_board(view, units)
            if not goblins.size or not elves.size:
                if elves.shape[0] != num_elves:
                    # elves lost (again)
                    print(f"elves didn't win flawlessly with attack {elfpower} _after_ round {tick} (lost {num_elves - elves.shape[0]} elves)")
                    if elves.size: print(tick*elves[:,2].sum())
                    nextattack = True # redundant, really
                    break

                total = elves[:,2].sum()
                print(f'Elves won flawlessly with attack {elfpower} _after_ round {tick}, health={total}')
                units = [(j,unit) for j,unit in units if unit[2]>0]
                print_board(view, units)
                return tick*total

if __name__ == "__main__":
    testinp = open('day15.testinp').read().strip()
    testinp2 = open('day15.testinp2').read().strip()
    testinp3 = open('day15.testinp3').read().strip()
    testinp4 = open('day15.testinp4').read().strip()
    inp = open('day15.inp').read().strip()
    #print(f'part1 test: {testinp} -> {day15(testinp)}')
    #print(f'part1 test: {testinp2} -> {day15(testinp2)}')
    #print(f'part1 test: {testinp3} -> {day15(testinp3)}')
    print(f'part1 test: {testinp4} -> {day15(testinp4)}')
    print(f'part1: {day15(inp)}')
    # 71*2777 == 197167 too high
    #print(f'part2 test: {testinp} -> {day15b(testinp)}')
    #print(f'part2 test: {testinp2} -> {day15b(testinp2)}')
    #print(f'part2 test: {testinp3} -> {day15b(testinp3)}')
    print(f'part2: {day15b(inp)}')
    # 23*1526 == 35098 too low
    # 24*1526 == 36624 too low
    # 37827 too high
    # 36150 not right
