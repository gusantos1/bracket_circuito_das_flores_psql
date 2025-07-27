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
        """
        Gera os jogos (brackets) de forma aleatória, garantindo um número
        balanceado e máximo de jogos através de um sistema de tentativas.
        """
        self.brackets = {'left': [], 'right': []}

        # Calcula o número máximo de jogos esperado. Para 8 atletas, são C(8,2) = 28 duplas,
        # resultando em 28 / 2 = 14 jogos.
        expected_games = math.comb(self.__limit, 2) // 2

        for side in get_args(SideVar):
            if (
                not self.combinations[side]
                or not self.combinations[side].values
            ):
                continue

            # Adiciona um loop de tentativas para garantir o resultado desejado
            MAX_TRIES = 100  # Limite para evitar loops infinitos
            for _ in range(MAX_TRIES):
                # Limpa os resultados da tentativa anterior para este lado
                self.brackets[side] = []

                # Pega e embaralha a lista de combinações
                combination_list = list(self.combinations[side].values)
                random.shuffle(combination_list)

                # Loop para criar os jogos (mesma lógica da versão anterior)
                while len(combination_list) >= 2:
                    current_team = combination_list.pop(0)
                    opponent_found_index = -1
                    for i, next_team in enumerate(combination_list):
                        if set(current_team).isdisjoint(set(next_team)):
                            opponent_found_index = i
                            break

                    if opponent_found_index != -1:
                        next_team = combination_list.pop(opponent_found_index)
                        match = asdict(
                            Match(first=current_team, second=next_team)
                        )
                        self.brackets[side].append(match)

                # --- VERIFICAÇÃO DE SUCESSO ---
                # Se o número de jogos gerados for o esperado, para as tentativas.
                if len(self.brackets[side]) == expected_games:
                    break

            # Se após todas as tentativas não conseguir o número esperado, pode lançar um aviso (opcional)
            if len(self.brackets[side]) != expected_games:
                print(
                    f"Aviso: Não foi possível gerar os {expected_games} jogos esperados para o lado '{side}' após {MAX_TRIES} tentativas."
                )

        return self.brackets

    def gen_brackets(self) -> Deque:
        static_left = [
    {'first': ('Carol', 'Rayza'), 'second': ('Lari', 'Isabella')},           # Jogo 1
    {'first': ('Sarah', 'Isabella'), 'second': ('Thayna', 'Isa Pires')},    # Jogo 2
    {'first': ('Thayna', 'Rayza'), 'second': ('Sarah', 'Isa Pires')},       # Jogo 3
    {'first': ('Sarah', 'Rayza'), 'second': ('Lari', 'Isa Pires')},         # Jogo 4
    {'first': ('Carol', 'Paloma'), 'second': ('Sarah', 'Thayna')},          # Jogo 5
    {'first': ('Paloma', 'Isabella'), 'second': ('Isa Pires', 'Rayza')},    # Jogo 6
    {'first': ('Isabella', 'Rayza'), 'second': ('Lari', 'Thayna')},         # Jogo 7
    {'first': ('Carol', 'Thayna'), 'second': ('Paloma', 'Lari')},           # Jogo 8
    {'first': ('Paloma', 'Isa Pires'), 'second': ('Thayna', 'Isabella')},   # Jogo 9
    {'first': ('Paloma', 'Rayza'), 'second': ('Carol', 'Lari')},            # Jogo 10
    {'first': ('Isabella', 'Isa Pires'), 'second': ('Carol', 'Sarah')},     # Jogo 11
    {'first': ('Sarah', 'Lari'), 'second': ('Carol', 'Isabella')},          # Jogo 12
    {'first': ('Carol', 'Isa Pires'), 'second': ('Paloma', 'Thayna')},      # Jogo 13
    {'first': ('Paloma', 'Sarah'), 'second': ('Lari', 'Rayza')}             # Jogo 14
]


        static_right = [
            {
                'first': ('Clara', 'Ines'),
                'second': ('Duda', 'Joana'),
            },  # Jogo 1
            {
                'first': ('Sther', 'Cinthia'),
                'second': ('Gabi', 'Ines'),
            },  # Jogo 2
            {
                'first': ('Sther', 'Duda'),
                'second': ('Ines', 'Joana'),
            },  # Jogo 3
            {
                'first': ('Marina', 'Clara'),
                'second': ('Gabi', 'Duda'),
            },  # Jogo 4
            {
                'first': ('Sther', 'Ines'),
                'second': ('Gabi', 'Joana'),
            },  # Jogo 5
            {
                'first': ('Marina', 'Ines'),
                'second': ('Cinthia', 'Joana'),
            },  # Jogo 6
            {
                'first': ('Clara', 'Joana'),
                'second': ('Duda', 'Ines'),
            },  # Jogo 7
            {
                'first': ('Marina', 'Duda'),
                'second': ('Sther', 'Gabi'),
            },  # Jogo 8
            {
                'first': ('Sther', 'Clara'),
                'second': ('Gabi', 'Cinthia'),
            },  # Jogo 9
            {
                'first': ('Marina', 'Joana'),
                'second': ('Cinthia', 'Duda'),
            },  # Jogo 10
            {
                'first': ('Sther', 'Joana'),
                'second': ('Clara', 'Cinthia'),
            },  # Jogo 11
            {
                'first': ('Marina', 'Sther'),
                'second': ('Clara', 'Gabi'),
            },  # Jogo 12
            {
                'first': ('Marina', 'Cinthia'),
                'second': ('Clara', 'Duda'),
            },  # Jogo 13
            {
                'first': ('Marina', 'Gabi'),
                'second': ('Cinthia', 'Ines'),
            },  # Jogo 14
        ]
        self.brackets['right'].extend(static_right)
        self.brackets['left'].extend(static_left)

    def gen_shuffle_brackets(self, side: SideVar) -> List[dict]:
        bracket = random.sample(self.brackets[side], len(self.brackets[side]))
        self.shuffle_brackets[side] = bracket
        return bracket


if __name__ == '__main__':
    m = Bracket(limit=8)
    group_1 = [
        'Carol',
        'Paloma',
        'Sarah',
        'Lari',
        'Thayna',
        'Isabella',
        'Isa Pires',
        'Rayza',
    ]
    group_2 = [
        'Clara',
        'Cinthia',
        'Sther',
        'Marina',
        'Duda',
        'Inês',
        'Gabi',
        'Joana',
    ]
    for name in group_1:
        m.add_athlete(name, side='left', random=False)
    for name in group_2:
        m.add_athlete(name, side='right', random=False)
    m.gen_combinations('left')
    m.gen_combinations('right')
    m.gen_brackets()
    1
