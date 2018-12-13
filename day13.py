from itertools import count,cycle
import numpy as np

def printer(view, carts):
    """print a given configuration, not actually needed for the main part"""
    tmpview = view.copy()
    for cart in carts:
        tmpview[cart[0], cart[1]] = cart[2]
    print('\n'.join(''.join([c for c in row]) for row in tmpview))

def day13(inp):
    lines = inp.splitlines()
    maxlen = max(map(len, lines))
    view = np.array([list(line) for line in lines])

    # define turns
    leftturn = {'>': '^', '<': 'v', '^': '<', 'v': '>'}
    rightturn = {'>': 'v', '<': '^', '^': '>', 'v': '<'}
    straight = {k:k for k in '><^v'}

    # get carts
    carts_x,carts_y = np.isin(view, list('><^v')).nonzero()
    dirs = view[carts_x, carts_y]
    carts = [(cx,cy,dir,cycle([leftturn, straight, rightturn])) for cx,cy,dir in zip(carts_x, carts_y, dirs)]

    # correct tracks
    horiz = np.isin(dirs, list('><'))
    view[carts_x[horiz], carts_y[horiz]] = '-'
    view[carts_x[~horiz], carts_y[~horiz]] = '|'

    crashes = []
    for tick in count(1):
        carts = sorted(carts)
        crashed = set()
        for i,(cx,cy,dir,turners) in enumerate(carts):
            if i in crashed:
                continue
            dx,dy = {'>': [0,1], '<': [0, -1], '^': [-1,0], 'v': [1,0]}[dir]
            neighb = view[cx + dx, cy + dy]
            try:
                j,cx_other,cy_other = next((j,cx_other,cy_other) for j,(cx_other,cy_other,_,_) in enumerate(carts) if (cx_other,cy_other) == (cx + dx, cy + dy))
                crashed.update({i,j})
                crashes.append((cy_other, cx_other))
                continue
            except StopIteration:
                # no crash
                pass

            # no crash, move on
            if neighb in '/\\':
                if (neighb == '/' and dir in '><') or (neighb == '\\' and dir in '^v'):
                    dir = leftturn[dir]
                else:
                    dir = rightturn[dir]
            if neighb == '+':
                turner = next(turners)
                dir = turner[dir]

            carts[i] = (cx + dx, cy + dy, dir, turners)

        # remove crashed carts
        carts = sorted(cart for i,cart in enumerate(carts) if i not in crashed)

        # check for Highlander
        if len(carts) <= 1:
            return crashes[0], (cy + dy, cx + dx) if carts else None


if __name__ == "__main__":
    testinp = open('day13.testinp').read()
    testinp2 = open('day13.testinp2').read()
    inp = open('day13.inp').read()
    print(day13(testinp))
    print(day13(testinp2))
    print(day13(inp))
