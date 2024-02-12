from .DFA import DFA

from dataclasses import dataclass
from collections.abc import Callable

EPSILON = ''  # this is how epsilon is represented by the checker in the transition function of NFAs
id = 0

@dataclass
class NFA[STATE]:
    S: set[str]
    K: set[STATE]
    q0: STATE
    d: dict[tuple[STATE, str], set[STATE]]
    F: set[STATE]

    def epsilon_closure(self, state: STATE) -> set[STATE]:
        # compute the epsilon closure of a state (you will need this for subset construction)
        # see the EPSILON definition at the top of this file
        closure = set()
        stack = [state]
        # cat timp am elemente carora sa le fac epsilon_closure
        while stack:
            # iau elementul curent din stiva si il adaug in closure
            current_state = stack.pop()
            closure.add(current_state)
            # caut toate starile in care pot ajunge din starea curenta cu epsilon
            for transition, next_state in self.d.items():
                if transition[0] == current_state and transition[1] == EPSILON:
                    for state in next_state:
                        # daca nu i s a facut epislon_closure niciodata
                        if state not in stack and state not in closure:
                            stack.append(state)
        return closure

    def subset_construction(self) -> DFA[frozenset[STATE]]:
        dfa_d = {}
        K = set()
        F = set()
        queue = [set(self.epsilon_closure(self.q0))]
        K.add(frozenset(queue[0]))
        q0 = frozenset(queue[0])
        
        while queue:
            elements = queue.pop()
            for symbol in self.S:
                # daca gaseste o tranzitie pe acelasi simbol al orcarei stari
                # din grupul de stari, adauga starea gasita in multimea de stari noi
                new_states = {state2 for state in elements for state2 in self.d.get((state, symbol), set())}
                # epislon_closure pentru fiecare stare din multimea de stari noi
                new_states |= {state2 for state2 in new_states for state2 in self.epsilon_closure(state2)}
                # daca noua stare din multimea de stari noi nu exista deja in dictionarul dfa_d
                # ea e o stare noua in dfa si trebuie adaugata in coada si in multimea de stari
                if new_states not in dfa_d.values():
                    queue.append(new_states)
                    K.add(frozenset(new_states))
                # daca nu exista deja in dfa_d o tranzitie de la grupul de stari la simbolul respectiv
                # adauga tranzitia in dfa_d
                dfa_d.setdefault((frozenset(elements), symbol), frozenset(new_states))
        # orice noua stare care contine o stare finala din nfa este stare finala in dfa
        for state in K:
            if any(final_state in state for final_state in self.F):
                F.add(state)      
        return DFA(self.S, K, q0, dfa_d, F)
                          
    def remap_states[OTHER_STATE](self, f: 'Callable[[STATE], OTHER_STATE]') -> 'NFA[OTHER_STATE]':
        # optional, but may be useful for the second stage of the project. Works similarly to 'remap_states'
        # from the DFA class. See the comments there for more details.
        # se aplica functia f pe fiecare stare din nfa si se creeaza un nou nfa cu starile modificate
        new_q0 = f(self.q0)
        newK = {f(state) for state in self.K}
        newF = {f(state) for state in self.F}
        # se aplica f atat pe starile din tranzitii cat si pe starile din multimea de stari
        self_d2 = {
            (f(transition[0]), transition[1]): {f(state2) for state2 in state}
            for transition, state in self.d.items()
        }
        return NFA(self.S, newK, new_q0, self_d2, newF)

