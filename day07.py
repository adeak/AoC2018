from collections import defaultdict

def day07a(inp):
    reqs = defaultdict(list)
    allchars = set()
    for line in inp:
        words = line.split()
        first,second = words[1],words[-3]
        reqs[second].append(first)
        allchars |= {first,second}
    res = ''
    while reqs:
        for c0 in sorted(allchars):
            if not reqs[c0]:
                del reqs[c0]
                res += c0
                allchars -= {c0}
                break
        for c in reqs:
            if c0 in reqs[c]:
                reqs[c].remove(c0)
    return res

def day07b(inp, nwork=5, delta=60):
    reqs = defaultdict(list)
    allchars = set()
    for line in inp:
        words = line.split()
        first,second = words[1],words[-3]
        reqs[second].append(first)
        allchars |= {first,second}
    workers = [[0,''] for _ in range(nwork)]
    alltime = 0
    while True:
        # find things elves can work on
        avails = [c for c in sorted(allchars) if not reqs[c]]
        # assign it to a worker
        for iw,(wtime,_) in enumerate(workers):
            if not avails:
                # keep waiting
                break
            if not wtime:
                # pop one char off if available
                c0 = avails.pop(0)
                allchars -= {c0}
                time = ord(c0) - ord('A') + 1 + delta
                workers[iw] = [time, c0]
        # see who's done first, ignore empty elves
        mintime = min(wtime for wtime,c in workers if wtime)
        alltime += mintime
        # clear those that are done, handle ties
        for iw,(wtime,c0) in enumerate(workers):
            if wtime == mintime:
                del reqs[c0]
                for c in reqs:
                    if c0 in reqs[c]:
                        reqs[c].remove(c0)
                #allchars -= {c0}
                workers[iw] = [0, '']
            elif wtime:
                workers[iw][0] -= mintime
        if sum(t for t,c in workers)==0 and not allchars:
            break

    return alltime

if __name__ == "__main__":
    testinp = open('day07.testinp').readlines()
    inp = open('day07.inp').readlines()
    print(day07a(testinp))
    print(day07a(inp))
    print(day07b(testinp, nwork=2, delta=0))
    print(day07b(inp))
