from collections import deque
from io import StringIO
import numpy as np

def parse_input(inp):
    f = StringIO(inp)

    # parse initial state
    initstr = f.readline().split()[-1]
    init = np.array([1 if c=='#' else 0 for c in initstr], dtype=np.uint8)

    next(f)

    # parse cellular automaton rules
    rulesdct = {}
    for line in f:
        src,to = line.strip().split(' => ')
        src = tuple(1 if c=='#' else 0 for c in src)
        to = 1 if to=='#' else 0
        rulesdct[src] = to
    # define an array for vectorized rule checking
    rules = np.empty((2**5,6), dtype=np.uint8) # for each combination: [state_tuple, new_val]
    for i,state_arr in enumerate(np.mgrid[:2,:2,:2,:2,:2].transpose(1,2,3,4,5, 0).reshape(-1,5)):
        state_tuple = tuple(state_arr)
        if state_tuple in rulesdct:
            rules[i, :] = state_tuple + (rulesdct[state_tuple],)
        else:
            # example input misses the empties
            rules[i, :] = state_tuple + (0,)

    return init, rules


def day12(inp, ngen=20):
    state,rules = parse_input(inp)
    minpos = 0 # index of first pot in state

    bytesize = state.strides[-1]
    vals = deque([0]*5, 5) # check pot sums for 5 generations for "long" runs; 5 chosen by fair dice roll
    for gen in range(ngen):
        # assume that a padding of 5 empties should suffice otherwise space would blow up
        zerosleft = (state==0).nonzero()[0][0]
        zerosright = state.size - 1 - (state==0).nonzero()[0][-1]
        addleft = max(0, 5 - zerosleft)
        addright = max(0, 5 - zerosright)
        state = np.pad(state, (addleft, addright), mode='constant')
        minpos -= addleft # keep track of pot indices

        # create strided view of state for broadcasting (rolling window)
        strided = np.lib.stride_tricks.as_strided(state,
                                                  shape=(state.size - 5 + 1, 5),
                                                  strides=(bytesize, bytesize))

        # compare against the rules, get new values
        pickrule = (strided[:,None,:] == rules[:,:-1]).all(-1)
        # shape (strided.size, 2**5), one-hot encoded choice of each rule
        _,irule = pickrule.nonzero()
        state[2:-2] = rules[irule,-1]
        # 2-2 edge values will stay 0 due to padding

        # compute occupied pot sum for "long" runs
        shiftedpots = state.nonzero()[0]
        properpots = shiftedpots + minpos
        vals.append(properpots.sum())

        # break if there's an arithmetic progression
        if len(set(np.diff(vals))) == 1:
            remaining = ngen - 1 - gen
            return vals[-1] + (vals[-1] - vals[-2])*remaining

    return vals[-1]


if __name__ == "__main__":
    testinp = open('day12.testinp').read().strip()
    inp = open('day12.inp').read().strip()
    print(day12(testinp))
    print(day12(inp))
    print(day12(inp, ngen=50000000000))
