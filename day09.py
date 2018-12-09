from itertools import cycle
from collections import deque

class Marbles(deque):
    def moveclock(self, n=1):
        self.rotate(-n)
    
    def movecounter(self, n=1):
        self.rotate(n)
    
    def insertright(self, val):
        self.moveclock()
        self.appendleft(val)

    def remove(self):
        self.popleft()

def day09(inp, factor=1):
    vals = inp.split()
    nplay = int(vals[0])
    nmarb = int(vals[-2])*factor + 1
    marbles = Marbles([0])
    scores = [0]*nplay
    elfit = iter(cycle(range(nplay)))
    for val in range(1, nmarb):
        elf = next(elfit)
        if not val % 23:
            marbles.movecounter(7)
            scores[elf] += val + marbles[0]
            marbles.remove()
        else:
            marbles.moveclock()
            marbles.insertright(val)

    return max(scores)


if __name__ == "__main__":
    testinp = open('day09.testinp').read().strip()
    inp = open('day09.inp').read().strip()
    print(day09(testinp))
    print(day09(inp))
    print(day09(testinp, factor=100))
    print(day09(inp, factor=100))
