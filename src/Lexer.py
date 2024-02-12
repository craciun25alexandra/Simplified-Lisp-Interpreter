from .NFA import NFA, EPSILON
from .Regex import parse_regex
class Lexer:
    def __init__(self, spec: list[tuple[str, str]]) -> None:
        # initialisation should convert the specification to a dfa which will be used in the lex method
        # the specification is a list of pairs (TOKEN_NAME:REGEX)
        self.token_nfas = {}  # Dictionary to store NFAs for each token
        self.finals = {}
        for token_name, regex_pattern in spec:
            regex = parse_regex(regex_pattern)
            nfa = regex.thompson()
            self.token_nfas[token_name] = nfa

        # Combine NFAs of all tokens into a single NFA
        self.combined_nfa = self.combine_nfas(self.token_nfas.values())
        self.combined_dfa = self.combined_nfa.subset_construction()
    
    def combine_nfas(self, nfas):
        combined_nfa = NFA(set(), {0}, 0, {}, set())
        combined_nfa.q0 = 0
        current_state = 1
        for nfa in nfas:
            #print(nfa)
            offset_nfa = nfa.remap_states(lambda x: x + current_state)
            combined_nfa.S.update(offset_nfa.S)
            combined_nfa.K.update(offset_nfa.K)
            combined_nfa.d.update(offset_nfa.d)
            combined_nfa.F.update(offset_nfa.F)
            combined_nfa.d.setdefault((combined_nfa.q0, EPSILON), set()).add(offset_nfa.q0)
            current_state += len(offset_nfa.K)
            for name, nfa2 in self.token_nfas.items():
                if nfa2 == nfa:
                    self.finals[name] = offset_nfa.F

        return combined_nfa

    def lex(self, word: str) -> list[tuple[str, str]] | None:
        # this method splits the lexer into tokens based on the specification and the rules described in the lecture
        # the result is a list of tokens in the form (TOKEN_NAME:MATCHED_STRING)
        # if an error occurs and the lexing fails, you should return none # todo: maybe add error messages as a task
        current_state = self.combined_dfa.q0
        last_accepting = None
        last_accepting_pos = -1
        last_accepting_true_pos = -1
        token_matches = []
        pos = 0
        newlinePos = 0
        line = 0
        true_pos = 0
        #print(self.combined_dfa)
        while pos < len(word):
            if word[pos] not in self.combined_dfa.S: #simbolul nu este in alfabet
                token_matches = [(("", f"No viable alternative at character {true_pos}, line {line}"))]
                return token_matches
            # exista tranzitie din starea curenta cu simbolul curent
            if (current_state, word[pos]) in self.combined_dfa.d and self.combined_dfa.d[(current_state, word[pos])] != frozenset():
                current_state = self.combined_dfa.d[(current_state, word[pos])]
                if word[pos] == '\n':
                    line += 1
                    newlinePos = true_pos + 1 # pentru afisarea erorilor
                pos += 1
                true_pos += 1
                if current_state in self.combined_dfa.F:
                    last_accepting = current_state
                    last_accepting_pos = pos - 1
                    last_accepting_true_pos = true_pos - 1
                    last_accepting_new = sorted(last_accepting)
                    if pos == len(word):
                        ok = False
                        for final in last_accepting_new:
                            if ok:
                                break
                            for name, finals in self.finals.items():
                                if final in finals:
                                    token_matches.append((name, word[:pos]))
                                    ok = True
                                    break
            else:
                if last_accepting is not None:
                    ok = False
                    last_accepting_new = sorted(last_accepting)
                    for final in last_accepting_new:
                        if ok:
                            break
                        for name, finals in self.finals.items():
                            if final in finals:
                                token_matches.append((name, word[:last_accepting_pos + 1]))
                                word = word[last_accepting_pos + 1:]
                                pos = 0
                                true_pos = last_accepting_true_pos + 1
                                ok = True
                                break
                    current_state = self.combined_dfa.q0
                    last_accepting = None
                else:
                    
                    token_matches = [(("", f"No viable alternative at character {true_pos - newlinePos}, line {line}"))]
                    return token_matches
        if last_accepting_pos != len(word) - 1:
            token_matches = [(("", f"No viable alternative at character EOF, line {line}"))]
        return token_matches
        