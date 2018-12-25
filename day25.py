from scipy.spatial.distance import cdist

def day25(inp):
    points = [[int(val) for val in line.split(',')] for line in inp.strip().split('\n')]
    # calculate distances once, operate with indices afterward
    alldists = cdist(points, points, metric='cityblock')

    constellations = [] # list of lists of ints
    rest_points = list(range(len(points)))
    while rest_points:
        ipoint = rest_points[0]
        rest_points = rest_points[1:]
        # do BFS
        edges = {ipoint}
        while rest_points:
            dists = alldists[[j for j in edges],:][:, [k for k in rest_points]]
            keepinds = (dists.min(0) <= 3).nonzero()[0]
            old_edges = edges
            new_edges = edges | {p for k,p in enumerate(rest_points) if k in keepinds}
            rest_points = [p for k,p in enumerate(rest_points) if k not in keepinds]
            if new_edges == old_edges:
                # this constellation is done
                constellations.append(list(edges))
                break
            edges = new_edges
        else:
            constellations.append(list(edges))

    return len(constellations)


if __name__ == "__main__":
    inp = open('day25.inp').read()
    testinp = open('day25.testinp').read()
    testinp2 = open('day25.testinp2').read()
    print(f'test: {day25(testinp)}')
    print(f'test: {day25(testinp2)}')
    print(f'{day25(inp)}')
