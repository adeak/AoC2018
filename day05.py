# # original, memory error
# def day05a(inp):
#     i = 0
#     chem = inp
#     have = []
#     while i < len(chem) - 2:
#         if abs(ord(chem[i]) - ord(chem[i+1])) == 32:
#             # annihilate chem[i] and chem[i+1]
#             chem = chem[:i] + chem[i+2:]
#             # step one back
#             i -= 1
#         else:
#             i += 1
#     return len(chem)

class Linked():
    def __init__(self, c):
        self.val = c
        self.prev = None
        self.next = None

def day05a(inp):
    i = 0
    root = Linked(inp[0])
    prev = root
    for c in inp[1:]:
        t = Linked(c)
        prev.next = t
        t.prev = prev
        prev = t

    link = root
    while True:
        nxt = link.next
        if not nxt:
            break
        if abs(ord(link.val) - ord(nxt.val)) == 32:
            # annihilate link and next
            prevgood = link.prev
            nextgood = nxt.next
            if not prevgood:
                link = nextgood
                link.prev = None
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
