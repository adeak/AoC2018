from itertools import count,cycle
import numpy as np
from scipy.ndimage.morphology import binary_dilation


def find_nearest_enemy(unit, others, sames, view):
    """Find nearest enemies on a map (called view), returns distance and nearest coords or None"""
    mask = view == '.' # not walls
    mask[tuple(sames.T)] = False # consider friendly units as walls
    mask[tuple(others.T)] = True # consider enemy units as non-walls
    table = np.zeros_like(view, dtype=bool)
    table[tuple(unit)] = True # seed for pathfinding
    other_set = set((tuple(row) for row in others))
    for dist in count(1):
        old_points = set(zip(*table.nonzero()))
        table = binary_dilation(table, mask=mask)
        new_points = set(zip(*table.nonzero())) - old_points
        if not new_points:
            # no enemy was found
            return None

        new_others = other_set & new_points
        if new_others:
            # we found the nearest enemy, choose in reading order
            nearest = sorted(new_others)[0]
            return dist,nearest

def find_nearest_path(unit, other, distance, sames, view):
    """Find paths to given enemy with a given distance"""
    tmpview = view == '.'
    tmpview[tuple(sames.T)] = True # friends are walls
    def path_finder(unit, other, distance, view):
        if unit == other:
            # we found it!
            return [unit]
        if distance == 0:
            # we didn't find a neighbour on this path
            return None
        x,y = unit
        valid_neighbs = [(x2,y2) for x2,y2 in [(x+1,y),(x,y+1),(x-1,y),(x,y-1)] if 0<=x2<view.shape[0] and 0<=y2<view.shape[1] and view[x2,y2]]
        # loop over each valid neighbour, loop over its subpaths, prepend neighbour to each
        all_subpaths = [subpaths for subpaths in [path_finder(neighb, other, distance-1, view) for neighb in valid_neighbs] if subpaths]
        if not all_subpaths:
            # dead end, return
            return None
        return [[unit] + subpath for subpath in [subpaths for subpaths in all_subpaths if subpaths] if subpath]

    return path_finder(unit[:2], other, distance, tmpview)


def day15(inp):
    view = np.array([list(row) for row in inp.split('\n')])
    free = np.isin(view,'.GE') # not wall
    view[free] = '.'
    goblins = np.array(sorted(zip(*(view == 'G').nonzero(), cycle([200]), cycle([3]), count()))) # (x,y,health,attack,index) tuples, good for sorting
    elves = np.array(sorted(zip(*(view == 'E').nonzero(), cycle([200]), cycle([3]), count()))) # (x,y,health,attack,index) tuples, good for sorting
    for tick in count(1):
        print(f'starting round {tick}')
        print(goblins)
        print(elves)
        units = list(zip([True]*len(goblins) + [False]*len(elves), sorted(goblins.tolist() + elves.tolist())))

        for i,(isgoblin,unit) in enumerate(units):
            *pos,health,attack,index = unit
            # skip units that have already been killed
            if health <= 0:
                continue

            # attack if in range
            others,sames = (elves,goblins) if isgoblin else (goblins,elves)
            living = others[:,2] >= 1
            dists = abs(pos - others[living,:2]).sum(-1) # "crow flies in Manhattan" distance of this unit from every enemy
            inrange = dists.min() == 1
            if inrange:
                # attack nearest with lowest HP
                near_inds = dists == 1
                choice = others[living][near_inds, 2].argmin()
                otherpos = others[living][near_inds][choice, :2]
                others[living][near_inds][choice, 2] -= attack
                print(f'attacking...')
                # if health goes below 1 we'll handle it elsewhere
                # find this in `unit` and change the health there too; that is the source of truth
                for jsgoblin,otherunit in units:
                    if isgoblin ^ jsgoblin:
                        # it's an enemy
                        if np.array_equal(pos, otherunit[:2]):
                            otherunit[2] -= attack
            else:
                # move if nobody is in range
                nearests = find_nearest_enemy(pos, others[:,:2], sames[:,:2], view)
                if not nearests:
                    print(f'unit {i}: no enemy found')
                    # no enemy found, go on
                    continue
                dist,nearest = nearests
                print(dist,nearest)
                # find best path among nearest paths
                paths = find_nearest_path(unit, nearest, dist, sames[:,:2], view)
                print(f'paths: {paths}')
                # paths is a sequence of index 2-tuple sequences, sorting will choose best
                nextpos = next(min(paths))
                unit[:2] = nextpos
        
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
        if not goblins.size or not elves.size:
            return tick*(goblins[:,2].sum() + elves[:,2].sum())

        input()


if __name__ == "__main__":
    testinp = open('day15.testinp').read().strip()
    #testinp2 = open('day15.testinp2').read().strip()
    #testinp3 = open('day15.testinp3').read().strip()
    inp = open('day15.inp').read().strip()
    print(f'part1 test: {testinp} -> {day15(testinp)}')
    #print(f'part1 test: {testinp2} -> {day15(testinp2)}')
    #print(f'part1: {day15(inp)}')
    #print(f'part2 test: {testinp3} -> {day15(testinp3, part2=True)}')
    #print(f'part2: {day15(inp, part2=True)}')
