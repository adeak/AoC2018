from collections import defaultdict
import numpy as np

def parse_guards(inp):
    guards = defaultdict(lambda: defaultdict(list))
    for line in sorted(inp):
        date = line[1:17]
        day,hour = date.split()
        if 'Guard' in line:
            ID = int(line.split()[3][1:])
            continue
        minute = int(hour.split(':')[-1])
        if 'asleep' in line:
            sleeptime = [minute]
        if 'wakes' in line:
            sleeptime.append(minute)
            guards[ID][day].append(sleeptime)

    return guards
    

def day04a(inp):
    guards = parse_guards(inp)
    totals = defaultdict(int)
    for ID,guard in guards.items():
        for day,sleeptimes in guard.items():
            for sleeptime in sleeptimes:
                totals[ID] += sleeptime[1] - sleeptime[0]
    guard = max(guards, key=lambda k:totals[k])
    slept = np.zeros(60, dtype=int)
    for day,sleeptimes in guards[guard].items():
        for fromtime,totime in sleeptimes:
            slept[fromtime:totime] += 1
    goodmin = slept.argmax()
    return guard*goodmin


def day04b(inp):
    guards = parse_guards(inp)
    slepts = {ID: np.zeros(60, dtype=int) for ID in guards}
    for ID,guard in guards.items():
        for day,sleeptimes in guard.items():
            for fromtime,totime in sleeptimes:
                slepts[ID][fromtime:totime] += 1
    maxsleep,goodmin = max([sleeps.max(), sleeps.argmax()] for sleeps in slepts.values())
    guard = next(ID for ID,sleeps in slepts.items() if sleeps.max()==maxsleep)
    return guard*goodmin


if __name__ == "__main__":
    inp = open('day04.inp').readlines()
    print(day04a(inp))
    print(day04b(inp))
