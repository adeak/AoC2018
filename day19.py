from day16 import instruction_maker

def day19(inp, part2=False):
    """Brute-force solution, takes _forever_ to run for part 2"""
    instrs = instruction_maker()
    regs = [0]*6
    if part2:
        regs[0] = 1

    header,*rest = inp.strip().split('\n')
    ip = int(header.split()[1])
    program = [[row.split()[0],*map(int,row.split()[1:])] for row in rest]
    Ni = len(program)

    while 0 <= regs[ip] < Ni:
        name,A,B,C = program[regs[ip]]
        regs = instrs[name](A, B, C, regs)
        regs[ip] += 1
    if ip == 0:
        # jump outside without writing it back into the register
        regs[ip] -= 1

    return regs[0]

# def day19_pythonified(part2=False):
#     """Python version of my specific input, would still take forever to run"""
#     r0 = r1 = r2 = r3 = r4 = r5 = 0
# 
#     # initialization
#     r3 = (r3 + 2)**2 * 19 * 11
#     r4 = (r4 + 7) * 22 + 6
#     r3 += r4
#     if part2:
#         r4 = (27 * 28 + 29) * 30 * 14 * 32
#         r3 += r4
# 
#     for r1 in range(1, r3 + 1):
#         for r5 in range(1, r5 + 1):
#             if r1 * r5 == r3:
#                 r0 += r1
# 
#     return r0

def day19_manual(part2=False):
    """Optimized version"""
    r3 = 10551396 if part2 else 996
    return sum(divisor + r3//divisor for divisor in range(1, int(r3**0.5) + 1) if r3/divisor == r3//divisor)


if __name__ == "__main__":
    testinp = open('day19.testinp').read()
    inp = open('day19.inp').read()
    print(f'part1 test: {day19(testinp)}')
    print(f'part1: {day19_manual()}')
    print(f'part2: {day19_manual(part2=True)}')
