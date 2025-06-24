import math
from collections import deque
from dataclasses import dataclass
from hashlib import md5
from itertools import combinations, product
from random import choice
from typing import Deque, Iterable, Literal, get_args

SideVar = Literal['left', 'right']


@dataclass
class Side:
    values: Deque[str]
    brackets: bool = False


@dataclass
class Match:
    first: tuple[str, str]
    second: tuple[str, str]
    game: int
    first_result: int = 0
    second_result: int = 0
    winner: tuple[str, str] = None


class Bracket:
    def __init__(self, limit: int = 8):
        self.__limit = limit
        self.__lambda_distribution = lambda side: [
            side for i in range(self.__limit)
        ]
        self.distribution = self.__lambda_distribution(
            'left'
        ) + self.__lambda_distribution('right')
        self.athlete_by_side = {
            'left': Side(values=deque(maxlen=self.__limit), brackets=False),
            'right': Side(values=deque(maxlen=self.__limit), brackets=False),
        }
        self.combinations = {'left': None, 'right': None}
        self.brackets = {'left': {}, 'right': {}}
        self.__hash_matches = {'left': set(), 'right': set()}

    def random_select(self) -> SideVar:
        if self.distribution:
            side = choice(self.distribution)
            self.distribution.remove(side)
            return side

    def add_athlete(
        self, athlete: str, side: SideVar = '', random: bool = False
    ) -> Deque:
        if random:
            side = self.random_select()

        if side in {'left', 'right'}:
            self.athlete_by_side[side].values.append(athlete)
            return self.athlete_by_side[side].values

    def gen_combinations(self, side: SideVar) -> Deque:
        if not self.athlete_by_side[side].brackets:
            comb = combinations(self.athlete_by_side[side].values, r=2)
            self.combinations[side] = Side(
                values=deque(maxlen=math.comb(self.__limit, 2)), brackets=True
            )
            self.combinations[side].values.extend(comb)
            return self.combinations[side].values

    @staticmethod
    def gen_hash(first: Iterable, second: Iterable) -> str:
        encoded_string = str(first + second).encode('utf-8')
        return md5(encoded_string).hexdigest()

    def gen_brackets(self) -> Deque:
        "o(n)"
        for side in get_args(SideVar):
            comb = self.combinations[side].values
            for a_team, b_team in product(comb, comb): # Remover produto (Combinação simples)
                a_one, a_two = a_team
                if a_one not in b_team and a_two not in b_team:
                    hash_match = self.gen_hash(a_team, b_team)
                    hash_reverse_match = self.gen_hash(
                        b_team, a_team
                    )  # (1, 2) vs (3, 4) is the same as (3, 4) vs (1, 2)
                    if hash_match not in self.__hash_matches[side]:
                        match = Match(
                            first=a_team,
                            second=b_team,
                            game=len(self.brackets[side]) + 1,
                        )
                        self.brackets[side][hash_match] = match
                        self.__hash_matches[side].add(hash_match)
                        self.__hash_matches[side].add(hash_reverse_match)
        return self.brackets

    def get_match(self, side: SideVar, hash_match: str):
        return self.brackets[side].get(hash_match)

    def set_result(
        self,
        side: SideVar,
        hash_match: str,
        first_result: int,
        second_result: int,
        winner: tuple[str, str],
    ) -> Match:
        match = self.get_match(side, hash_match)
        match.first_result = first_result
        match.second_result = second_result
        match.winner = winner
        self.brackets[side][hash_match] = match
        return self.brackets[side][hash_match]


m = Bracket(limit=8)

#athletes
group_1 = [
    "Carol",
    "Paloma",
    "Sarah",
    "Lari",
    "Thayna",
    "Isabella",
    "Isa Pires",
    "Rayza"
]

group_2 = [
    "Clara",
    "Cinthia",
    "Sther",
    "Marina",
    "Duda",
    "Inês",
    "Gabi",
    "Joana"
]



#left
for name in group_1:
    m.add_athlete(name, side='left', random=False)

#right
for name in group_2:
    m.add_athlete(name, side='right', random=False)

# Combinations
m.gen_combinations('left')
m.gen_combinations('right')

# Brackets
m.gen_brackets()
1
