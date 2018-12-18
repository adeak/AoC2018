import numpy as np

def stringify(view):
    """Return a stringified version of the map"""
    printview = np.empty_like(view, dtype='U1')
    for val,char in enumerate('.|#'):
        printview[view == val] = char
    return '\n'.join([''.join(row) for row in printview])

def print_map(view):
    print(stringify(view))

def get_neighbour_counts(padded_view, other_val):
    """Return for each acre how many of its valid neighbours are `other_val`"""
    counts = np.zeros(tuple(n-2 for n in padded_view.shape), dtype=int)
    for from1,to1 in [(None, -2), (1, -1), (2, None)]:
        for from2,to2 in [(None, -2), (1, -1), (2, None)]:
            if (from1,to1) == (from2,to2) == (1,-1):
                # ignore ourselves
                continue
            counts += padded_view[from1:to1, from2:to2] == other_val
    return counts

def day18(inp, it=10):
    mapping = dict((char,val) for val,char in enumerate('.|#'))
    view = np.array([[mapping[char] for char in row] for row in inp.strip().split('\n')])

    scores = []
    hashes = []
    seens = set()
    for tick in range(it):
        #print_map(view)
        #input()

        # pad the edges with nothing
        padded_view = np.pad(view, 1, 'constant', constant_values=-1)
        out_view = view.copy()

        # change open acres
        val,other_val,new_val = 0,1,1
        counts = get_neighbour_counts(padded_view, other_val)
        out_view[(counts >= 3) & (view == val)] = new_val

        # change trees
        val,other_val,new_val = 1,2,2
        counts = get_neighbour_counts(padded_view, other_val)
        val,other_val = 1,2
        out_view[(counts >= 3) & (view == val)] = new_val

        # change lumberyards
        val,other_vals,new_val = 2,(2,1),0
        countses = [get_neighbour_counts(padded_view, other_val) for other_val in other_vals]
        out_view[((countses[0] < 1) | (countses[1] < 1)) & (view == val)] = new_val

        view = out_view

        # store and compare score and current configuration
        score = (view == 1).sum() * (view == 2).sum()
        viewhash = hash(stringify(view))
        # assume that hash collisions are highly unlikely
        if viewhash in seens:
            start = hashes.index(viewhash)
            end = tick - 1 # tick of last in the cycle
            cyclelen = end - start + 1 # length of cycle
            fraction = (it - start) % cyclelen # number of total cycles
            final_index = start + fraction -1
            return scores[final_index]
        scores.append(score)
        seens.add(viewhash)
        hashes.append(viewhash)

    return score


if __name__ == "__main__":
    testinp = open('day18.testinp').read()
    inp = open('day18.inp').read()
    print(f'part1 test: {day18(testinp)}')
    print(f'part1: {day18(inp)}')
    print(f'part2: {day18(inp, it=1000000000)}')
