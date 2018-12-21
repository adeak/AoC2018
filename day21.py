from operator import itemgetter
from day16 import instruction_maker

def day21_generic(inp):
    """Generic solution, very slow (runs in ~45 minutes)"""
    instrs = instruction_maker()

    header,*rest = inp.strip().split('\n')
    ip = int(header.split()[1])
    program = [[row.split()[0],*map(int,row.split()[1:])] for row in rest]
    Ni = len(program)

    # try to guess the key register, assuming register 0 only gets compared to this once
    pre_exit,cmp_reg = next((i,({*program[i][1:3]} - {0}).pop()) for i in range(Ni)
                            if program[i][0] == 'eqrr' and 0 in {*program[i][1:3]})

    regs = [0]*6
    ni = 0
    halters = {}
    seens = set()
    while 0 <= regs[ip] < Ni:
        ni += 1
        if regs[ip] == pre_exit:
            # we'd be comparing regs[0] and regs[cmp_reg] now
            val = regs[cmp_reg]
            if val not in halters:
                # this value for regs[0] would halt in ni instructions
                halters[val] = ni
            else:
                if tuple(regs) in seens:
                    # we're just going to cycle from here; stop
                    return (min(halters.items(), key=itemgetter(1))[0],
                            max(halters.items(), key=itemgetter(1))[0])
            seens.add(tuple(regs))
        name,A,B,C = program[regs[ip]]
        regs = instrs[name](A, B, C, regs)
        regs[ip] += 1
    if ip == 0:
        # jump outside without writing it back into the register
        regs[ip] -= 1


def day21_manual():
    """Specific solution, slow (runs in ~1.5 minutes)"""
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
    #print(f'part1-2: {day21_generic(inp)}')
    print(f'part1-2: {day21_manual()}')
