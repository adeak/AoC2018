class Linked():
    def __init__(self, c):
        self.val = ord(c)
        self.prev = None
        self.next = None
    def __xor__(self, other):
        return abs(self.val - other.val) == 32

def day05a(inp):
    i = 0

    # create linked list
    root = Linked(inp[0])
    prev = root
    for c in inp[1:]:
        t = Linked(c)
        prev.next = t
        t.prev = prev
        prev = t

    # compute reactions
    link = root
    while True:
        nxt = link.next
        if not nxt:
            break
        if link ^ nxt:
            # annihilate link and next
            prevgood = link.prev
            nextgood = nxt.next
            if not prevgood:
                link = nextgood
                link.prev = None
                root = link # not actually used later
            elif not nextgood:
                link = prevgood
                link.next = None
                break
            else:
                prevgood.next = nextgood
                nextgood.prev = prevgood
                link = prevgood
        else:
            link = nxt

    # count remaining links
    nlinks = 0
    while True:
        nlinks += 1
        link = link.prev
        if not link:
            break
    return nlinks


def day05b(inp):
    types = set(inp)
    types = {c.lower() for c in types}
    shortest = float('inf')
    for c in types:
        chem = inp.replace(c, '').replace(c.upper(), '')
        length = day05a(chem)
        if length < shortest:
            shortest = length
    return shortest


if __name__ == "__main__":
    inp = open('day05.inp').read().strip()
    print(day05a(inp))
    print(day05b(inp))
