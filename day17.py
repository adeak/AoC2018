from itertools import count
import numpy as np

def print_map(view):
    printview = np.empty_like(view.T, dtype='U1')
    for val,char in enumerate('.#|~'):
        printview[view.T == val] = char
    print('\n'.join([''.join(row) for row in printview]))

def day17(inp):
    DRY,CLAY,WET,STILL = range(4)

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

    # add one to the size along x in each direction in order to have clayless walls on the side
    xmin -= 1
    size = (xmax - xmin + 1 + 2, ymax - ymin + 1)
    view = np.zeros(size, dtype=int) # zero is sand, 1 is clay, 2 is running water, 3 is still water
    for dir,ind,fromto in dat:
        if dir == 'x':
            view[ind-xmin, fromto[0]-ymin:fromto[1]+1-ymin] = CLAY
        else:
            view[fromto[0]-xmin:fromto[1]+1-xmin, ind-ymin] = CLAY
    # spring is at view[500 - xmin, 0 - ymin] except these coordinates are outside the array!

    # keep track of pixels that actively propagate the flow
    flowers = {(500 - xmin, max(0, 0 - ymin))} # first pixel where water flows; proper indices from now on
    # (flow|er, not flower)
    prev_water = 0
    while True:
        #print_map(view)
        #input()
        for x0,y0 in flowers.copy():
            # move "down" if possible, include "this" pixel
            for y in count(y0):
                # wet this pixel
                view[x0, y] = WET
                # move the corresponding edge pixel
                flowers.add((x0, y))
                flowers -= {(x0, y - 1)}

                if y == size[1] - 1 or view[x0, y + 1] == WET:
                    # we reached the bottom or an existing flow, stop flowing
                    break
                if view[x0, y + 1] in {CLAY, STILL}:
                    # we can't keep flowing down, start flowing horizontally
                    for x in range(x0 - 1, -1, -1):
                        # flow to the left
                        if view[x, y] == CLAY:
                            # we hit a wall
                            break
                        view[x, y] = WET
                        flowers.add((x, y))
                        flowers -= {(x + 1, y)}
                        if view[x, y + 1] not in {CLAY, STILL}:
                            # we have to stop flowing in this direction
                            break
                    for x in range(x0 + 1, size[1]):
                        # flow to the right
                        if view[x, y] == CLAY:
                            # we hit a wall
                            break
                        view[x, y] = WET
                        flowers.add((x, y))
                        flowers -= {(x - 1, y)}
                        if view[x, y + 1] not in {CLAY, STILL}:
                            # we have to stop flowing in this direction
                            break
                    break

        # check for filled cavern rows
        left_walls = (view[:-1,:] == CLAY) & (view[1:,:] == WET)
        for iwall, jwall in zip(*left_walls.nonzero()):
            water_inds = set()
            for iwater in count(iwall+1):
                assert iwater <= size[0] - 1 # opposite should never happen, edge should always be free

                if jwall + 1 < size[1] and view[iwater, jwall + 1] == DRY:
                    # then we can flow down here, no still water
                    break
                # the next position can only be sand, running water or a wall; sand means we can't be still
                if view[iwater, jwall] == DRY:
                    # we're flowing to the right
                    break
                if view[iwater, jwall] == WET:
                    water_inds.add((iwater,jwall))
                if view[iwater, jwall] == CLAY:
                    # we've reached the other wall, means still water here
                    view[iwall + 1:iwater, jwall] = STILL
                    # update edges with flows from previous row
                    new_flowers = {(iwall + 1 + iedge, jwall - 1) for iedge in (view[iwall + 1:iwater, jwall - 1] == WET).nonzero()[0]}
                    flowers = (flowers | new_flowers) - water_inds
                    break

        num_water = np.isin(view, [WET, STILL]).sum()
        if num_water == prev_water:
            # we're stationary
            return num_water, (view == STILL).sum()
        prev_water = num_water


if __name__ == "__main__":
    testinp = open('day17.testinp').read()
    inp = open('day17.inp').read()
    print(f'part1-2 test: {day17(testinp)}')
    print(f'part1-2: {day17(inp)}')
