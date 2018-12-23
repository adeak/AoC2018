import numpy as np
from scipy.spatial.distance import cdist
from scipy.ndimage.morphology import binary_dilation

def day23(inp, part2=False):
    dat = []
    for line in inp.strip().splitlines():
        posstr,rstr = line[5:].strip().split('>, r=')
        dat.append(list(map(int, posstr.split(','))) + [int(rstr)])

    bots = np.array(dat)
    poses,powers = bots[:,:-1], bots[:,-1]
    strongest = powers.argmax()
    power = powers[strongest]
    dists = cdist([poses[strongest]], poses, metric='cityblock')
    nears = dists <= power

    if not part2:
        return nears.sum()
    
    ## optional visualization of the bots
    #import matplotlib.pyplot as plt
    #from mpl_toolkits.mplot3d import Axes3D
    #fig = plt.figure()
    #ax = fig.add_subplot(111, projection='3d')
    ## temporarily exclude bots that are "far away" from others (i.e. outliers)
    #allnears = (cdist(poses, poses, metric='cityblock') <= powers).sum(-1)
    #keep = allnears > 0.1*allnears.max()
    #ax.scatter(*poses[keep,:].T)
    ##ax.scatter(*poses.T)
    #plt.show()

    # octahedra can only intersect in points that are a corner to at least one of the octahedra
    # -> look at every corner of every octahedron and look for the optimum there
    corners = []
    for ax in range(3):
        for sign in -1,1:
            new_corners = poses.copy()
            new_corners[:, ax] += sign * powers
            corners.append(new_corners)
    corners = np.vstack(corners) # shape (ncorner, 3)

    # find which one is closest to the most bots
    #nears = (abs(corners[:,None,:] - poses).sum(-1) <= powers).sum(-1)
    nears = (cdist(corners, poses, metric='cityblock') <= powers).sum(-1)
    maxnear = nears.max()
    maxcorners = nears == maxnear

    # start brute force from here... unfortunately the intersection of intersections needn't contain any corners
    start = corners[nears.argmax()] # length-3 position

    # naive brute force from here
    pad = 20 # padding from optimal corner; your mileage may vary...
    xmin,ymin,zmin = start
    search_arr = np.zeros((2 * pad + 1, 2 * pad + 1, 2 * pad + 1), dtype=bool)
    search_arr[pad, pad, pad] = True
    mask = search_arr
    nears = maxnear
    best = abs(start).sum()
    while True:
        # compute new edges in proper data coordinates
        edges = [tuple((val + shift) for val,shift in zip(edge, [xmin - pad, ymin - pad, zmin - pad])) for edge in zip(*search_arr.nonzero())]  # shape (nedge, 3)
        if not edges:
            break

        # find how many bots are in range from each edge position, find the maximum closest to the origin
        nearsnow = (cdist(edges, poses, metric='cityblock') <= powers).sum(-1)
        maxnears = nearsnow.max()
        goods = nearsnow == maxnears
        goodedges = np.array([edges[ind] for ind in goods.nonzero()[0]])
        bestdist = abs(goodedges).sum(-1).min()
        if maxnears < nears:
            # we're going further away from optimum, stop
            break
        if maxnears > nears:
            # we've got a new record
            nears = maxnears
            best = bestdist
        if maxnears == nears:
            # we may have to update the best distance
            if best > bestdist:
                best = bestdist

        # get new edges
        mask |= search_arr
        search_arr = binary_dilation(mask)
        search_arr[mask] = False

    return best


if __name__ == "__main__":
    inp = open('day23.inp').read()
    testinp = open('day23.testinp').read()
    testinp2 = open('day23.testinp2').read()
    print(f'part1 test: {day23(testinp)}')
    print(f'part1: {day23(inp)}')
    print(f'part2 test: {day23(testinp2, part2=True)}')
    print(f'part2: {day23(inp, part2=True)}')
