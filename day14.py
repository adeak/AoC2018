from itertools import count

def day14(inp, part2=False):
    nrecstr = inp
    nreclen = len(nrecstr)
    nrec = int(nrecstr)
    recipes = [3, 7]
    elves = [0, 1]
    lastpos = 0
    for tick in count(1):
        news = map(int, str(sum(recipes[elfpos] for elfpos in elves)))
        recipes.extend(news)
        
        if not part2 and len(recipes) >= nrec + 10:
            return ''.join(map(str,recipes[nrec:nrec+10]))

        if part2 and len(recipes) - lastpos > nreclen:
            tail = ''.join(map(str, recipes[lastpos:]))
            if nrecstr in tail:
                return lastpos + tail.index(nrecstr)
            lastpos = len(recipes) - nreclen - 1

        for i,elfpos in enumerate(elves):
            elves[i] = (elfpos + recipes[elfpos] + 1) % len(recipes)


if __name__ == "__main__":
    testinp = open('day14.testinp').read().strip()
    testinp2 = open('day14.testinp2').read().strip()
    testinp3 = open('day14.testinp3').read().strip()
    inp = open('day14.inp').read().strip()
    print(f'part1 test: {testinp} -> {day14(testinp)}')
    print(f'part1 test: {testinp2} -> {day14(testinp2)}')
    print(f'part1: {day14(inp)}')
    print(f'part2 test: {testinp3} -> {day14(testinp3, part2=True)}')
    print(f'part2: {day14(inp, part2=True)}')
