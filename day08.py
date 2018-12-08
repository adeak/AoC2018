from functools import lru_cache

class Node():
    def __init__(self, nchild, nmeta, parent=None):
        self.nchild = int(nchild)
        self.nmeta = int(nmeta)
        self.children = []
        self.meta = []
        self.parent = parent

@lru_cache(None)
def recurse_sum(node):
    """Compute the value of a node using recursion"""
    if not node.nchild:
        return sum(node.meta)
    # otherwise: index into children
    return sum(recurse_sum(node.children[i - 1]) for i in node.meta if 0 < i <= node.nchild)

def day08(inp):
    it = iter(inp.split())
    # get root data
    nchild,nmeta = next(it),next(it)
    root = Node(nchild, nmeta)
    current = root
    metasum = 0
    while True:
        if len(current.children) != current.nchild:
            # next specification is a subnode, enter
            nchild,nmeta = next(it),next(it)
            child = Node(nchild, nmeta, current)
            current.children.append(child)
            current = child
            continue
        # otherwise: start read metadata for current, go back a level
        current.meta[:] = (int(next(it)) for _ in range(current.nmeta))
        metasum += sum(current.meta)

        current = current.parent
        if not current:
            break

    # compute value sum
    valuesum = recurse_sum(root)
    return metasum,valuesum


if __name__ == "__main__":
    testinp = open('day08.testinp').read().strip()
    inp = open('day08.inp').read().strip()
    print(day08(testinp))
    print(day08(inp))
