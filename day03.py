import numpy as np

def day03a(inp):
    fab = np.zeros((1000,1000), dtype=int)
    for line in inp:
        lab,_,coords,size = line.split()
        lab = int(lab[1:])
        coords = list(map(int, coords[:-1].split(',')))
        size = list(map(int, size.split('x')))
        fab[coords[0]:coords[0]+size[0], coords[1]:coords[1]+size[1]] += 1
    return (fab > 1).sum()

def day03b(inp):
    fab = np.zeros((1000,1000), dtype=int)
    sizes = {}
    for line in inp:
        lab,_,coords,size = line.split()
        lab = int(lab[1:])
        x,y = map(int, coords[:-1].split(','))
        w,h = map(int, size.split('x'))
        sizes[lab] = w*h
        mask = fab[x:x+w, y:y+h] > 0
        fab[x:x+w, y:y+h][mask] = 0
        fab[x:x+w, y:y+h][~mask] = lab
    size_arr = np.array([size for _,size in sorted(sizes.items())]) # 1-based indices!
    return (np.bincount(fab.ravel())[1:] == size_arr).nonzero()[0][0] # exclude 0 non-label

if __name__ == "__main__":
    inp = open('day03.inp').readlines()
    print(day03a(inp))
    print(day03b(inp))
