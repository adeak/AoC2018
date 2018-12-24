from operator import attrgetter

class Group:
    def __init__(self, good=None, units=None, HP=None, attack=None, hittype=None, initiative=None, immunity=None, weakness=None, source=None):
        if source:
            self._copy_from(source)
            return

        self.good = good # True if immune system
        self.units = units
        self.HP = HP
        self.attack = attack
        self.hittype = hittype
        self.init = initiative
        self.immunity = set() if immunity is None else immunity
        self.weakness = set() if weakness is None else weakness

    def _copy_from(self, other):
        self.attack = other.attack
        self.good = other.good # True if immune system
        self.units = other.units
        self.HP = other.HP
        self.hittype = other.hittype
        self.init = other.init
        self.immunity = other.immunity
        self.weakness = other.weakness

    def __repr__(self):
        return f'Group(good={self.good}, units={self.units}, HP={self.HP}, attack={self.attack}, hittype={self.hittype}, initiative={self.init}, immunity={self.immunity}, weakness={self.weakness})'

    @property
    def power(self):
        """The effective power of the group"""
        return self.units * self.attack

    @property
    def init_score(self):
        """The score according to which groups can choose targets (effective power then initiative)"""
        return (self.power, self.init)

    def target_score(self, other):
        """The score according to which groups are targeted: (max damage dealt, power, initiative)"""
        return (self.virtual_damage(other),) + self.init_score

    def virtual_damage(self, other):
        """The maximum damage that the other group could deal on us"""
        if other.hittype in self.immunity:
            dmg = 0
        elif other.hittype in self.weakness:
            dmg = other.power * 2
        else:
            dmg = other.power
        return dmg

    def choose_enemy(self, groups):
        """Choose at most one group from among the enemies, return our enemy and the rest of the groups"""
        enemyitem = max(((i,group,group.virtual_damage(self)) for i,group in enumerate(groups) if group.good != self.good),
                        key=lambda item:item[1].target_score(self), default=None)
        if not enemyitem or enemyitem[2] == 0:
            # no enemies left; we're alone in the fight (otherwise the fight is over)
            # or we can't damage anyone
            return None, groups
        i,enemy,dmg = enemyitem
        return enemy, [group for j,group in enumerate(groups) if j != i]

    def take_damage(self, other):
        dmg = self.virtual_damage(other)
        dead = dmg//self.HP
        self.units = max(0, self.units - dead)


def parse_group(line, goodness):
    """Parse a line of input for a given group, return a Group"""
    first,rest = line.split(' hit points ', 1)
    units = int(first.split()[0])
    HP = int(first.split()[4])

    # default: no weaknesses or immunities
    weakness = None
    immunity = None
    if '(' in rest:
        mid,rest = rest[1:].split(') ')
        for dat in mid.split('; '):
            immune_data = dat.startswith('immune to')
            typewords = dat.split(maxsplit=2)[-1]
            types = set(typewords.split(', '))
            if immune_data:
                immunity = types
            else:
                weakness = types

    restwords = rest.split()
    attack = int(restwords[5])
    hittype = restwords[6]
    initiative = int(restwords[-1])

    group = Group(good=goodness, units=units, HP=HP, attack=attack, hittype=hittype, initiative=initiative, immunity=immunity, weakness=weakness)
    return group


def day24(inp, part2=False):
    it = iter(inp.strip().splitlines())
    groups = []
    try:
        while True:
            line = next(it)
            goodness = line.startswith('Immune')
            while True:
                line = next(it).strip()
                if not line:
                    # end block
                    break
                groups.append(parse_group(line, goodness))
    except StopIteration:
        pass

    orig_groups = groups

    boosts = ()
    wins = ()
    # do bisection method for finding the right attack value
    while True:
        if not boosts:
            boost = 0
        elif len(boosts) == 1:
            boost = boosts[0] + 1
        else:
            # boosts = (boost0, boost1)
            # wins = (win0, win1)
            if not wins[1]:
                boost = 2*boosts[1]
            elif wins[0]: # not going to happen
                boost = boosts[0] // 2
            else:
                # boost0 wins, boost1 loses
                boost = int((boosts[0] + boosts[1]) // 2)

        # restore initial state for boosting
        groups = [Group(source=group) for group in orig_groups]
        for group in groups:
            if group.good:
                group.attack += boost
        # sort _after_ boosting: boost affects order
        groups = sorted(groups, key=attrgetter('init_score'), reverse=True)
    
        while len({group.good for group in groups}) == 2:
            # fight while we have two sides
    
            # targeting phase:
            targets = {}
            tmpgroups = groups
            for group in groups:
                enemy,tmpgroups = group.choose_enemy(tmpgroups)
                targets[group] = enemy
            if len(tmpgroups) == len(groups):
                # nobody can damage anybody else even a bit, i.e. we didn't win and never will
                won = False
                break

            # attacking phase:
            old_units = sum(group.units for group in groups)
            for group in sorted(groups, key=attrgetter('init'), reverse=True):
                enemy = targets[group]
                if enemy and enemy.units > 0 and group.units > 0:
                    enemy.take_damage(group)
            new_units = sum(group.units for group in groups)
            if old_units == new_units:
                # we've reached an impasse, i.e. we didn't win and never will
                won = False
                break
    
            # remove dead groups, resort by init score
            groups = sorted([group for group in groups if group.units > 0], key=attrgetter('init_score'), reverse=True)
        else:
            won = groups[0].good
    
        # count number of remaining units
        if boost == 0:
            part1 = sum(group.units for group in groups)
        if won:
            # the immune system has won
            part2 = sum(group.units for group in groups)
            # only part2 for the final winning boost value

        # handle bisection method initial states
        if len(boosts) < 2:
            boosts += boost,
            wins += won,
        if len(boosts) < 2:
            continue

        # choose next bisection step
        if boost > boosts[1]:
            boosts = boosts[1], boost
            wins = wins[1], won
        elif boost < boosts[0]:
            boosts = boost, boosts[0]
            wins = won, wins[0]
        else:
            if won:
                boosts = boosts[0], boost
                wins = wins[0], won
            else:
                boosts = boost, boosts[1]
                wins = won, wins[1]

        # check for end condition
        if boosts[1] - boosts[0] == 1 and wins[1]:
            # we're done, and the last part2 is exactly what we need
            return part1, part2


if __name__ == "__main__":
    inp = open('day24.inp').read()
    testinp = open('day24.testinp').read()
    print(f'part1-2 test: {day24(testinp)}')
    print(f'part1-2: {day24(inp)}')
