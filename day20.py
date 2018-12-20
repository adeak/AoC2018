from itertools import count

class Node():
    def __init__(self, regex):
        self.regex = regex
        self.children = []
        self.parents = []

        # list of steps for this node
        choices = {'N': (0,1), 'E': (1,0), 'S': (0,-1), 'W': (-1,0)}
        self.steps = [choices[c] for c in regex]

    def add_children(self, children):
        self.children.extend(children)

def parser(rest):
    """Parse a regex string, enclosing parentheses are assumed to be present
    
    Return list of graph nodes"""

    if '(' not in rest:
        # then we only have a single path left, including empty string
        return [Node(rest)]

    # otherwise we have choices with an optional prefix
    startind = rest.index('(')
    prefix,rest = rest[:startind],rest[startind:]

    # '(' is now rest[0], find its closing pair
    # also find top-level ors
    opens = 0
    or_inds = []
    for i,c in enumerate(rest):
        if c == '(':
            opens += 1
        if c == ')':
            opens -= 1
        if opens == 1 and c == '|':
            or_inds.append(i - 1)
            # subtracting 1 from the index because we'll drop the leading parenthesis
        if not opens:
            # we've just found our pair
            endind = i
            break

    middles,rest = rest[1:endind],rest[endind+1:]

    # split on pipes that are on the top level
    middle_regexen = (middles[fr + 1:to] for fr,to in zip([-1] + or_inds, or_inds + [None]))
    middle_nodes = [node for middle_regex in middle_regexen for node in parser(middle_regex)]
    rest_nodes = parser(rest)

    subroot = Node(prefix) # potentially with an empty string, we'll prune these later
    for middle_node in middle_nodes:
        middle_node.parents.append(subroot)
        middle_node.add_children(rest_nodes)
        for rest_node in rest_nodes:
            rest_node.parents.append(middle_node)
    subroot.add_children(middle_nodes)

    return [subroot]

def day20(inp):
    regex = inp.strip()[1:-1]

    root = parser(regex)[0]
    # prune empty nodes
    current = root
    remains = set()
    while True:
        remains.update(current.children)
        if not remains:
            break
        current = remains.pop()
        if len(current.regex) == 0:
            # eliminate this node
            parents = current.parents
            children = current.children
            for parent in parents:
                parent.add_children(children)
                parent.children.remove(current)
            for child in children:
                child.parents.extend(parents)
                child.parents.remove(current)

    # start BFS
    edges = [(root, iter(root.steps), (0,0))]
    seens = {(0,0): 0}
    for tick in count(1):
        new_edges = []
        for i, (node, stepiter, (x0,y0)) in enumerate(edges):
            try:
                dx,dy = next(stepiter)
                newpos = (x0+dx, y0+dy)
                if newpos in seens:
                    # nothing to do on this path
                    continue
                seens[newpos] = tick
                new_edges.append((node, stepiter, newpos))
            except StopIteration:
                # we need to go into its children
                children = node.children
                if not children:
                    # then this path ends here
                    continue
                # push all the children onto the queue, continue there
                for child in children:
                    stepiter = iter(child.steps)
                    dx,dy = next(stepiter)
                    newpos = (x0+dx, y0+dy)
                    if newpos in seens:
                        # nothing to do here
                        continue
                    seens[newpos] = tick
                    new_edges.append((child, stepiter, newpos))
        edges = new_edges
        if not new_edges:
            break

    part1 = max(seens.values())
    part2 = sum(1 for val in seens.values() if val >= 1000)

    return part1,part2


if __name__ == "__main__":
    testinp = open('day20.testinp').read()
    testinp2 = open('day20.testinp2').read()
    inp = open('day20.inp').read()
    print(f'part1-2 test1: {day20(testinp)}')
    print(f'part1-2 test2: {day20(testinp2)}')
    print(f'part1-2: {day20(inp)}')
