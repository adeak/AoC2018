from itertools import count
from collections import deque
import numpy as np
from scipy.ndimage.morphology import binary_dilation

def print_map(view):
    printview = np.empty_like(view.T, dtype='U1')
    for char,val in zip('.#|~', count()):
        printview[view.T == val] = char
    print('\n'.join([''.join(row) for row in printview]))

def day17(inp):
    dat = []
    xmin = ymin = np.inf
    xmax = ymax = -np.inf
    for line in inp.strip().split('\n'):
        head,tail = line.strip().split(', ')
        ind = int(head[2:])
        fromto = list(map(int, tail[2:].split('..')))
        assert len(fromto) == 2
        assert fromto[0] < fromto[1]
        dat.append((line[0], ind, fromto))
        if line.startswith('x'):
            xmin = min(xmin, ind)
            xmax = max(xmax, ind)
            ymin = min(ymin, fromto[0])
            ymax = max(ymax, fromto[1])
        else:
            ymin = min(ymin, ind)
            ymax = max(ymax, ind)
            xmin = min(xmin, fromto[0])
            xmax = max(xmax, fromto[1])

    # add one to the size along x in each direction in order to have clayless walls
    xmin -= 1
    size = (xmax - xmin + 1 + 2, ymax - ymin + 1)
    view = np.zeros(size, dtype=int) # zero is sand, 1 is clay, 2 is running water, 3 is still water
    for dir,ind,fromto in dat:
        if dir == 'x':
            view[ind - xmin, fromto[0] - ymin:fromto[1]+1 - ymin] = 1
        else:
            view[fromto[0] - xmin:fromto[1] + 1 - xmin, ind - ymin] = 1
    # spring is at view[500 - xmin, 0 - ymin] except these coordinates are outside the array!

    flowers = [(500 - xmin, max(0, 0 - ymin))] # first pixel where water flows; proper indices from now on
    # flow|er, not flower
    prev_waters = deque([0,0,0], maxlen=3) # number of "wet" pixels in three rounds
    while True:
        # set current flow edge to running water
        #print_map(view)
        #input()
        for i,flower in list(enumerate(flowers))[::-1]:
            view[flower] = 2

            # move "down" if possible
            x0,y0 = flower
            #invalidate = False
            if y0 == size[1] - 1:
                # there's nowhere to flow "down"
                continue
            if view[x0, y0 + 1] == 0:
                # sand; we can flow there, add edge
                view[x0, y0 + 1] = 2
                flowers.append((x0, y0 + 1))
                #invalidate = True

            # move to the side if possible
            if view[x0, y0 + 1] in [1, 3]:
                # clay or still water; we need to start spreading out
                nextpos = (x0 - 1, y0)
                if 0 <= nextpos[0] and view[nextpos] == 0 and nextpos not in flowers:
                    # spread there
                    flowers.append(nextpos)
                    #invalidate = True
                nextpos = (x0 + 1, y0)
                if nextpos[0] < size[0] and view[nextpos] == 0 and nextpos not in flowers:
                    # spread there
                    flowers.append(nextpos)
                    #invalidate = True
                #if invalidate:
                #    # we need to restart the loop over flow-ends
                #    break

        # check for filled cavern rows
        left_walls = (view[:-1,:] == 1) & (view[1:,:] == 2)
        for iwall, jwall in zip(*left_walls.nonzero()):
            water_inds = []
            for iwater in count(iwall+1):
                if iwater > size[0] - 1:
                    # assume that we can't have still water here due to overflows outside...
                    break
                if jwall + 1 < size[1] and view[iwater, jwall + 1] == 0:
                    # then we can still flow down, no still water
                    break
                # the next position can only be sand, running water or a wall
                if view[iwater, jwall] == 0:
                    # we're flowing to the right, no still water here
                    break
                if view[iwater, jwall] == 2:
                    water_inds.append((iwater,jwall))
                if view[iwater, jwall] == 1:
                    # we've reached the other wall, got still water here
                    view[iwall + 1:iwater, jwall] = 3
                    flowers = [flower for flower in flowers if flower not in water_inds]
                    break

        num_water = np.isin(view, [2,3]).sum()
        prev_waters.append(num_water)
        if len(set(prev_waters)) == 1:
            # we're stationary
            #print_map(view)
            return num_water, (view == 3).sum()


if __name__ == "__main__":
    testinp = open('day17.testinp').read()
    inp = open('day17.inp').read()
    print(f'part1-2 test: {day17(testinp)}')
    print(f'part1-2: {day17(inp)}')
    # 35613 too low :(
    # add 13 due to capillaries
    # 35626 too low
    # 35630 too low
    # 35682 "not the right answer"
