from collections.abc import Callable
from dataclasses import dataclass

@dataclass
class DFA[STATE]:
    S: set[str]
    K: set[STATE]
    q0: STATE
    d: dict[tuple[STATE, str], STATE]
    F: set[STATE]

    def accept(self, word: str) -> bool:
        # incepe de la starea initiala
        current_state = self.q0
        # pentru fiecare litera din cuvant
        for symbol in word:
            # daca exista o tranzitie pe litera curenta, se duce in starea urmatoare
            if (current_state, symbol) in self.d:
                current_state = self.d[(current_state, symbol)]
            # daca nu exista o tranzitie pe litera curenta, cuvantul nu este acceptat
            else:
                return False
        # daca starea in care s-a terminat cuvantul este stare finala, cuvantul este acceptat
        return current_state in self.F

    def remap_states[OTHER_STATE](self, f: Callable[[STATE], 'OTHER_STATE']) -> 'DFA[OTHER_STATE]':
        # optional, but might be useful for subset construction and the lexer to avoid state name conflicts.
        # this method generates a new dfa, with renamed state labels, while keeping the overall structure of the
        # automaton.

        # for example, given this dfa:

        # > (0) -a,b-> (1) ----a----> ((2))
        #               \-b-> (3) <-a,b-/
        #                   /     ⬉
        #                   \-a,b-/

        # applying the x -> x+2 function would create the following dfa:

        # > (2) -a,b-> (3) ----a----> ((4))
        #               \-b-> (5) <-a,b-/
        #                   /     ⬉
        #                   \-a,b-/
        # se aplica f pe fiecare stare din starea initiala, stari finale si stari normale
        new_q0 = frozenset({f(state) for state in self.q0})

        newK = [frozenset({f(state2) for state2 in state}) for state in self.K]
        newK = frozenset(newK)

        newF = [frozenset({f(state2) for state2 in state}) for state in self.F]
        newF = frozenset(newF)
        # se aplica f atat pe starile din tranzitii cat si pe starile din multimea de stari
        self_d2 = {
            (frozenset({f(state1) for state1 in transition[0]}), transition[1]):
            frozenset({f(state2) for state2 in state})
            for transition, state in self.d.items()
        }

        return DFA(self.S, newK, new_q0, self_d2, newF)
