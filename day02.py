from collections import Counter
from itertools import combinations

def day02a(inp):
    vals = inp.split()
    twos = sum(1 for val in vals if any(cnt==2 for cnt in Counter(val).values()))
    threes = sum(1 for val in vals if any(cnt==3 for cnt in Counter(val).values()))
    return twos*threes

def day02b(inp):
    vals = inp.split()
    for i,(word1,word2) in enumerate(combinations(vals, 2)):
        if sum(1 for c1,c2 in zip(word1,word2) if c1!=c2) == 1:
            return ''.join(c1 for c1,c2 in zip(word1,word2) if c1==c2)

if __name__ == "__main__":
    inp = open('day02.inp').read()
    print(day02a(inp))
    print(day02b(inp))
