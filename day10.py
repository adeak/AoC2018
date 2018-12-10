import numpy as np
from itertools import count

def print_array(arr):
    for row in arr.T:
        print(''.join('#' if val else '.' for val in row))

def day10(inp):
    plst = []
    vlst = []
    for line in inp:
        poses,rest = line[10:].strip().split('>',1)
        vs = rest[:-1].split('<')[-1]
        plst.append(poses)
        vlst.append(vs)
    pos = np.fromstring(','.join(plst), sep=',').reshape(-1,2).astype(int)
    v = np.fromstring(','.join(vlst), sep=',').reshape(-1,2).astype(int)
    posnow = pos.copy()
    bboxmin = np.inf,np.inf
    for t in count(-1):
        # check for message: find smallest bbox for points in given time step
        bbox = posnow.ptp(0) + 1
        if bbox[0] < bboxmin[0] or bbox[1] < bboxmin[1]:
            bboxmin = bbox
            prevpos = posnow.copy()
        if bbox[0] > bboxmin[0] or bbox[1] > bboxmin[1]:
            printarr = np.full(prevpos.ptp(0) + 1, False)
            printarr[tuple((prevpos - prevpos.min(0)).T)] = True
            print_array(printarr)
            return(t)
        posnow += v

if __name__ == "__main__":
    testinp = open('day10.testinp').readlines()
    inp = open('day10.inp').readlines()
    print(day10(testinp))
    print(day10(inp))
