import numpy as np

def day11(inp):
    ID = int(inp)
    ngrid = 300
    cells = np.zeros((ngrid, ngrid), dtype=int)
    x,y = np.mgrid[1:ngrid+1, 1:ngrid+1]
    rackID = x + 10
    levels = (((rackID * y + ID)*rackID) % 1000)//100 - 5
    bytesize = levels.strides[-1]
    maxpow = -np.inf
    for ncell in range(1, ngrid + 1):
        # create rolling window using stride tricks
        strided = np.lib.stride_tricks.as_strided(levels,
                                                  shape=(ngrid - ncell + 1, ngrid - ncell + 1, ncell, ncell),
                                                  strides=(bytesize * ngrid, bytesize) * 2)
        powers = strided.sum((-2,-1))
        index = np.unravel_index(powers.argmax(), powers.shape)
        if ncell == 3:
            part1 = (index[0] + 1, index[1] + 1)
        if powers[index] > maxpow:
            maxpow = powers[index]
            part2 = (index[0] + 1, index[1] + 1, ncell)
    return part1, part2


if __name__ == "__main__":
    testinp = open('day11.testinp').read().strip()
    inp = open('day11.inp').read().strip()
    print(day11(testinp))
    print(day11(inp))
