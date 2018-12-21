from operator import itemgetter

def day21_manual(inp):
    r1 = r2 = r3 = r4 = r5 = 0

    # ignore dead code: same number of instructions for each case

    halters = {}
    ni = 1  # initial r3 = 0 included, why not
    seens = set()
    while True:
        r4 = r3 | 65536  # LABEL:6
        r3 = 7041048
        ni += 2

        while True:
            r3 = (((r3 + (r4 & 255)) & 16777215) * 65899) & 16777215 # LABEL:8
            # r3 = (((r3 + (r4 % 256)) % 16777216) * 65899) % 16777216
            # r3 is at most 16777215
            ni += 6
            if r4 < 256:
                ni += 3
    
                # assume r0 is possibly this first r3
                ni += 2
                if r3 not in halters:
                    halters[r3] = ni
                else:
                    if (r3,r4) in seens:
                        # we're going to cycle from here; stop
                        return (min(halters.items(), key=itemgetter(1))[0],
                                max(halters.items(), key=itemgetter(1))[0])
                seens.add((r3,r4))
                ni += 1 # for the ongoing case if r3 != r0
                break
            else:
                ni += 3
                for r5 in range(r4//256 + 2):
                    ni += 1 # r5 assignment/increment
                    # loop until r1 > r4 <=> (r5 + 1) * 256 > r4 <=> r5 + 1 > r4/256 <=> r5 > r4/256 + 1
                    r1 = (r5 + 1) * 256 # LABEL:18
                    ni += 2
                    if r1 > r4:
                        r4 = r5
                        ni += 5
                        break # GOTO 8
                    ni += 4 # GOTO 18

    return max(halters)


if __name__ == "__main__":
    inp = open('day21.inp').read()
    print(f'part1-2: {day21_manual(inp)}')
