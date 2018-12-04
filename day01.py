from itertools import cycle

def day01a(inp):
    return sum(map(int,inp))

def day01b(inp):
    dat = map(int, inp)
    val = 0
    seens = {val}
    for delta in cycle(dat):
        val += delta
        if val in seens:
            return val
        seens.add(val)

if __name__ == "__main__":
    inp = open('day01.inp').readlines()
    print(day01a(inp))
    print(day01b(inp))
