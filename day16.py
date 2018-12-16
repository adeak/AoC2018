from ast import literal_eval
from operator import add, mul, and_, or_, gt, eq

def binary_maker():
    """Generates instructions that correspond to binary operations"""
    instrs = {}
    # choose operation type
    ops = {'add': add, 'mul': mul, 'ban': and_, 'bor': or_}
    for name,op in ops.items():
        for tail in 'ri':
            def fun(A, B, C, regs, op=op, tail=tail):
                out = regs.copy()
                out[C] = op(regs[A], B if tail == 'i' else regs[B])
                return out
            instrs[name + tail] = fun
    return instrs

def asgn_maker():
    """Generates instructions that correspond to assignments"""
    instrs = {}
    prefix = 'set'
    for tail in 'ri':
        def fun(A, B, C, regs, tail=tail):
            out = regs.copy()
            out[C] = A if tail == 'i' else regs[A]
            return out
        instrs[prefix + tail] = fun
    return instrs

def cmp_maker():
    """Generates instructions that correspond to comparisons"""
    instrs = {}
    # choose operation type
    ops = {'gt': gt, 'eq': eq}
    for name,op in ops.items():
        for tail_A,tail_B in 'ri','rr','ir':
            def fun(A, B, C, regs, op=op, tail_A=tail_A, tail_B=tail_B):
                out = regs.copy()
                out[C] = 1 if op(A if tail_A == 'i' else regs[A], B if tail_B == 'i' else regs[B]) else 0
                return out
            instrs[name + tail_A + tail_B] = fun
    return instrs

def day16(inp, part2=False):
    itinp = iter(inp.split('\n'))

    # create instruction table
    instrs = {**binary_maker(), **asgn_maker(), **cmp_maker()}

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
        matchset = {name for name,fun in instrs.items() if fun(A, B, C, from_reg) == to_reg}
        examples.append((ind, matchset)) # for each example in a list we have (instruction index, matching names) tuples

    # part 1: get counts
    hits = sum(1 for example in examples if len(example[1]) >= 3)

    if not part2:
        return hits

    # part 2: try unravelling suspicions (going iteratively from unambiguous ones)
    known = {}
    while len(known) < 16:
        new_knowns = {ind:next(iter(names)) for ind,names in examples if len(names) == 1}
        assert new_knowns # if this happens we're screwed
        new_names = set(new_knowns.values())
        known.update(new_knowns)
        examples = [example for example in examples if len(example[1]) > 1]
        for ind,candidates in examples:
            candidates -= new_names

    regs = [0]*4
    for ind,*rest in program:
        regs = instrs[known[ind]](*rest, regs)

    return hits,regs[0]


if __name__ == "__main__":
    testinp = open('day16.testinp').read()
    inp = open('day16.inp').read()
    print(f'part1 test: {day16(testinp)}')
    print(f'part2: {day16(inp, part2=True)}')
