# backend.py (CORRIGIDO)

import math
import random
from collections import deque
from dataclasses import dataclass, asdict
from itertools import combinations, count
from random import choice
from typing import Deque, List, Literal, get_args
from copy import copy

SideVar = Literal['left', 'right']


@dataclass
class Side:
    values: Deque[str]
    brackets: bool = False


@dataclass
class Match:
    first: tuple[str, str]
    second: tuple[str, str]


class Bracket:
    def _create_side_distribution(self, side: str) -> List[str]:
        """Cria a lista de distribuição para um lado específico."""
        return [side for _ in range(self.__limit)]

    def __init__(self, limit: int = 8):
        self.__limit = limit
        

        self.distribution = self._create_side_distribution(
            'left'
        ) + self._create_side_distribution('right')
        
        self.athlete_by_side = {
            'left': Side(values=deque(maxlen=self.__limit), brackets=False),
            'right': Side(values=deque(maxlen=self.__limit), brackets=False),
        }
        self.combinations = {'left': None, 'right': None}
        self.brackets = {'left': [], 'right': []}
        self.shuffle_brackets = {'left': [], 'right': []}

    def random_select(self) -> SideVar:
        """Select a random side from the distribution."""
        if self.distribution:
            side = choice(self.distribution)
            self.distribution.remove(side)
            return side

    def add_athlete(
        self, athlete: str, side: SideVar = '', random: bool = False
    ) -> Deque:
        """Add an athlete to the bracket."""
        if random:
            side = self.random_select()

        if side in {'left', 'right'}:
            self.athlete_by_side[side].values.append(athlete)
            return self.athlete_by_side[side].values

    def gen_combinations(self, side: SideVar) -> Deque:
        """Generate combinations of athletes for the given side."""
        if not self.athlete_by_side[side].brackets:
            comb = combinations(self.athlete_by_side[side].values, r=2)
            self.combinations[side] = Side(
                values=deque(maxlen=math.comb(self.__limit, 2)), brackets=True
            )
            self.combinations[side].values.extend(comb)
            return self.combinations[side].values

    def gen_brackets(self) -> Deque:
        """Generate brackets based on the combinations of athletes."""
        for side in get_args(SideVar):
            combination = copy(self.combinations[side].values)
            c = count(1)
            while len(combination) > 0:
                position = next(c)
                try:
                    current_team = combination[0]
                    next_team = combination[position]
                    player_one, player_two = current_team
                    if {player_one, player_two}.isdisjoint(next_team):
                        match = asdict(Match(first=current_team, second=next_team))
                        self.brackets[side].append(match)
                        combination.remove(current_team)
                        combination.remove(next_team)
                        c = count(1)
                except IndexError:
                    break

        return self.brackets

    def gen_shuffle_brackets(self, side: SideVar) -> List[dict]:
        bracket = random.sample(self.brackets[side], len(self.brackets[side]))
        self.shuffle_brackets[side] = bracket
        return bracket

if __name__ == "__main__":
    m = Bracket(limit=8)
    group_1 = ["Carol", "Paloma", "Sarah", "Lari", "Thayna", "Isabella", "Isa Pires", "Rayza"]
    group_2 = ["Clara", "Cinthia", "Sther", "Marina", "Duda", "Inês", "Gabi", "Joana"]
    for name in group_1: m.add_athlete(name, side='left', random=False)
    for name in group_2: m.add_athlete(name, side='right', random=False)
    m.gen_combinations('left'); m.gen_combinations('right')
    m.gen_brackets()