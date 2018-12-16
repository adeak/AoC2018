from ast import literal_eval

instrs = {}

def store(fun):
    #def wrapped(A, B, C, regs):
    #    out = fun(A, B, C, regs)
    #    #print(f'{fun.__name__}: {regs} -> {out}')
    #    return out
    #instrs[fun.__name__] = wrapped
    instrs[fun.__name__] = fun
    return fun

@store
def addr(A, B, C, regs):
    out = regs.copy()
    out[C] = regs[A] + regs[B]
    return out

@store
def addi(A, B, C, regs):
    out = regs.copy()
    out[C] = regs[A] + B
    return out

@store
def mulr(A, B, C, regs):
    out = regs.copy()
    out[C] = regs[A] * regs[B]
    return out

@store
def muli(A, B, C, regs):
    out = regs.copy()
    out[C] = regs[A] * B
    return out

@store
def banr(A, B, C, regs):
    out = regs.copy()
    out[C] = regs[A] & regs[B]
    return out

@store
def bani(A, B, C, regs):
    out = regs.copy()
    out[C] = regs[A] & B
    return out

@store
def borr(A, B, C, regs):
    out = regs.copy()
    out[C] = regs[A] | regs[B]
    return out

@store
def bori(A, B, C, regs):
    out = regs.copy()
    out[C] = regs[A] | B
    return out

@store
def setr(A, B, C, regs):
    out = regs.copy()
    out[C] = regs[A]
    return out

@store
def seti(A, B, C, regs):
    out = regs.copy()
    out[C] = A
    return out

@store
def gtir(A, B, C, regs):
    out = regs.copy()
    out[C] = 1 if A > regs[B] else 0
    return out

@store
def gtri(A, B, C, regs):
    out = regs.copy()
    out[C] = 1 if regs[A] > B else 0
    return out

@store
def gtrr(A, B, C, regs):
    out = regs.copy()
    out[C] = 1 if regs[A] > regs[B] else 0
    return out

@store
def eqir(A, B, C, regs):
    out = regs.copy()
    out[C] = 1 if A == regs[B] else 0
    return out

@store
def eqri(A, B, C, regs):
    out = regs.copy()
    out[C] = 1 if regs[A] == B else 0
    return out

@store
def eqrr(A, B, C, regs):
    out = regs.copy()
    out[C] = 1 if regs[A] == regs[B] else 0
    return out


def day16(inp, part2=False):
    itinp = iter(inp.split('\n'))
    hits = 0
    examples = []
    for line in itinp:
        if line.startswith('Before'):
            from_reg = literal_eval(line.split(maxsplit=1)[1])
            ind,A,B,C = map(int, next(itinp).split())
            to_reg = literal_eval(next(itinp).split(maxsplit=1)[1])
            # read empty separator
            next(itinp)
        elif not line:
            # end of part 1
            if not part2:
                break # needed for test case
            next(itinp)
            program = [list(map(int, cmd.split())) for cmd in itinp if cmd.strip()]
            break

        # we have from_reg, the instruction and to_reg
        # see which functions match this example
        matchset = set()
        for name,fun in instrs.items():
            if to_reg == fun(A, B, C, from_reg):
                matchset.add(name)

        examples.append((ind, matchset)) # for each example in a list we have (instruction index, matching names) tuples

        # part 1: get counts
        if len(examples[-1][1]) >= 3:
            # part 1
            hits += 1

    if not part2:
        return hits

    # part 2: try unravelling suspicions (going iteratively from unambiguous ones)
    known = {}
    while len(known) < 16:
        new_knowns = {ind:next(iter(names)) for ind,names in examples if len(names) == 1}
        if not new_knowns:
            print(f'Oh-uh!')
            print(f'known = {known}')
            print(f'examples = {examples}')
            print({ind:len(names) for ind,names in examples})
            break
        new_names = set(new_knowns.values())
        known.update(new_knowns)
        examples = [example for example in examples if len(example[1]) > 1]
        for ind,candidates in examples:
            len0 = len(candidates)
            candidates -= new_names

    regs = [0]*4
    for ind,*rest in program:
        regs = instrs[known[ind]](*rest, regs)

    return hits,regs[0]



if __name__ == "__main__":
    testinp = open('day16.testinp').read()
    #testinp2 = open('day16.testinp2').read()
    inp = open('day16.inp').read()
    print(f'part1 test: {day16(testinp)}')
    #print(f'part1 test: {testinp2} -> {day16(testinp2)}')
    #print(f'part1: {day16(inp)}')
    #print(f'part2 test: {testinp} -> {day16b(testinp)}')
    #print(f'part2 test: {testinp2} -> {day16b(testinp2)}')
    print(f'part2: {day16(inp, part2=True)}')
