import numpy as np
from scipy.spatial.distance import cdist

def day06(inp, thresh=10000):
    coords = np.array([list(map(int, line.split(','))) for line in inp])
    # shift everyone to start from 0
    coords -= coords.min(0)
    w,h = coords.max(0) + 1
    # get the distance of every pixel from every input point
    pxpy = np.mgrid[:w, :h].transpose(1,2,0).reshape(-1,2) # shape (npixels, 2)
    dists = cdist(pxpy, coords, 'cityblock').astype(int) # (npixels, 2) vs (npoints, 2), shape (npixels, npoints)

    # part 1:
    nearests = dists.argmin(-1)     # nearest index, shape (npixels,)
    points = nearests.reshape(w, h) # nearest index, shape (w, h)

    # exclude points that are tied
    tieds = (dists == dists.min(-1, keepdims=True)).sum(-1) > 1 # shape (npixels,)
    points.flat[tieds] = -1

    # exclude edge values, they should be infinite...
    maxval = 0
    for i in range(points.max() + 1):
        xposes,yposes = (points == i).nonzero()
        if xposes.min() == 0 or xposes.max() == w - 1 or yposes.min() == 0 or yposes.max() == h - 1:
            points[points == i] = -1
            continue

        # now we have the final values
        valnow = (points == i).sum()
        maxval = max(valnow, maxval)

    # part 2:
    totals = dists.sum(-1)     # total distance, shape (npixels,)
    goodcount = (totals < thresh).sum()

    return maxval,goodcount


if __name__ == "__main__":
    testinp = open('day06.testinp').readlines()
    inp = open('day06.inp').readlines()
    print(day06(testinp, thresh=32))
    print(day06(inp))
