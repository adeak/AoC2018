from collections import defaultdict
import numpy as np

def day22(inp, part2=False):
    depthline,targetline = inp.strip().splitlines()
    depth = int(depthline.split()[-1])
    target = targetline.split()[-1]
    x0,y0 = map(int, target.split(','))

    target = x0,y0
    if part2:
        x0,y0 = 4*x0,4*y0 # buffer for pathfinding... but really x0,y0 should be the target

    erosion = np.zeros((x0 + 1, y0 + 1), dtype=int)
    xinds = np.arange(0, x0 + 1)
    yinds = np.arange(0, y0 + 1)
    m = 20183
    erosion[0, yinds] = (48271 * yinds  + depth) % m
    erosion[xinds, 0] = (16807 * xinds  + depth) % m

    # construct rest of the generalized generalized Pascal triangle
    # i + j = const, const in 0 .. x0 + y0
    for c in range(2, x0 + y0 + 1):
        x = np.arange(1, c + 1)
        y = c - x
        inds = (1 <= x) & (x < x0 + 1) & (1 <= y) & (y < y0 + 1)
        x,y = x[inds],y[inds]
        erosion[x, y] = (erosion[x - 1, y] * erosion[x, y - 1] + depth) % m
        if target in zip(x,y):
            # set target's geologic index to 0
            erosion[target] = (0 + depth) % m

    risk = erosion % 3

    if not part2:
        return risk.sum()

    # part 2:
    x0,y0 = target
    cave = risk # 0 is rocky, 1 is wet, 2 is narrow
    # print cave
    #print('\n'.join(''.join('.=|'[val] for val in row) for row in cave[:x0+1,:y0+1].T))
    # tools are indexed by exclusion: 0 is neither, 1 is torch, 2 is climbing gear
    edges = {(0, (0, 0), 1)} # time, position, tool
    times = defaultdict(dict) # position -> tool -> minimum time to travel
    times[0, 0] = {1: 0, 0: 7, 2: 7} # bit needless but true
    while edges:
        edge = min(edges) # always step from edge with shortest time
        edges -= {edge}
        time,(x,y),tool = edge

        # did we hit the target?
        if (x,y) == (x0,y0):
            # penalty for changing to torch is already included by now
            return time

        new_edges = set()
        for newpos in (x+1,y),(x,y+1),(x-1,y),(x,y-1):
            if not (0 <= newpos[0] < cave.shape[0] and 0 <= newpos[1] < cave.shape[1]):
                continue
            nexttype = cave[newpos]
            # compute time we'd need to reach next position
            # always consider both kinds of tools because we'll never know (and logic is more linear this way)
            # but we can't equip something that is invalid _here_
            for nexttool in {0,1,2} - {nexttype, cave[x, y]}:
                delta = 1 if nexttool == tool else 8
                nexttime = time + delta
                # skip this step if we've been there and faster (with the same tool)
                if newpos in times and nexttool in times[newpos] and times[newpos][nexttool] <= nexttime:
                    continue
                # if we've hit the target add penalty for changing to torch
                if newpos == (x0, y0) and nexttool != 1:
                    nexttime += 7

                # update logistics
                new_edges.add((nexttime, newpos, nexttool))
                times[newpos][nexttool] = nexttime

        # update edges
        edges.update(new_edges)


if __name__ == "__main__":
    inp = open('day22.inp').read()
    testinp = open('day22.testinp').read()
    print(f'part1 test: {day22(testinp)}')
    print(f'part1: {day22(inp)}')
    print(f'part2 test: {day22(testinp, part2=True)}')
    print(f'part2: {day22(inp, part2=True)}')
