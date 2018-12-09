from itertools import cycle

class Marble():
    def __init__(self, c):
        self.val = c
        self.prev = None
        self.next = None
    
    def getclock(self, n=1):
        current = self
        for _ in range(n):
            current = current.next
        return current
    
    def getcounter(self, n=1):
        current = self
        for _ in range(n):
            current = current.prev
        return current
    
    def insertright(self, val):
        new = Marble(val)
        new.prev = self
        new.next = self.next
        self.next.prev = new
        self.next = new
        return new

    def remove(self):
        self.prev.next = self.next
        self.next.prev = self.prev

def day09(inp, factor=1):
    vals = inp.split()
    nplay = int(vals[0])
    nmarb = int(vals[-2])*factor + 1
    current = Marble(0)
    current.next = current.prev = current
    scores = [0]*nplay
    elfit = iter(cycle(range(nplay)))
    for val in range(1, nmarb):
        elf = next(elfit)
        if not val % 23:
            to_del = current.getcounter(7)
            scores[elf] += val + to_del.val
            current = to_del.getclock()
            to_del.remove()
        else:
            current = current.getclock().insertright(val)

    return max(scores)


def day09b(inp):
    pass

if __name__ == "__main__":
    testinp = open('day09.testinp').read().strip()
    inp = open('day09.inp').read().strip()
    print(day09(testinp))
    print(day09(inp))
    print(day09(testinp, factor=100))
    print(day09(inp, factor=100))
