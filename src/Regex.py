from .NFA import NFA
from dataclasses import dataclass


EPSILON = ''

class Regex:
    def __init__(self, value, left, right):
        self.value = value
        self.left = left
        self.right = right
    
    def thompson(self) -> NFA[int]:
        if self.left is None:
            return Letter(self.value).thompson()
        if self.value == '!':
            return Concat(self.left, self.right).thompson()
        elif self.value == '|':
            return Union(self.left, self.right).thompson()
        elif self.value == '*':
            return Star(self.left).thompson()
        elif self.value == '?':
            return QuestionMark(self.left).thompson()
        elif self.value == '+':
            return Plus(self.left).thompson()
    def _display_aux(self):
        """Returns list of strings, width, height, and horizontal coordinate of the root."""
        # No child.
        if self.right is None and self.left is None:
            line = '%s' % self.value
            width = len(line)
            height = 1
            middle = width // 2
            return [line], width, height, middle

        # Only left child.
        if self.right is None:
            lines, n, p, x = self.left._display_aux()
            s = '%s' % self.value
            u = len(s)
            first_line = (x + 1) * ' ' + (n - x - 1) * '_' + s
            second_line = x * ' ' + '/' + (n - x - 1 + u) * ' '
            shifted_lines = [line + u * ' ' for line in lines]
            return [first_line, second_line] + shifted_lines, n + u, p + 2, n + u // 2

        # Only right child.
        if self.left is None:
            lines, n, p, x = self.right._display_aux()
            s = '%s' % self.value
            u = len(s)
            first_line = s + x * '_' + (n - x) * ' '
            second_line = (u + x) * ' ' + '\\' + (n - x - 1) * ' '
            shifted_lines = [u * ' ' + line for line in lines]
            return [first_line, second_line] + shifted_lines, n + u, p + 2, u // 2

        # Two children.
        left, n, p, x = self.left._display_aux()
        right, m, q, y = self.right._display_aux()
        s = '%s' % self.value
        u = len(s)
        first_line = (x + 1) * ' ' + (n - x - 1) * '_' + s + y * '_' + (m - y) * ' '
        second_line = x * ' ' + '/' + (n - x - 1 + u + y) * ' ' + '\\' + (m - y - 1) * ' '
        if p < q:
            left += [n * ' '] * (q - p)
        elif q < p:
            right += [m * ' '] * (p - q)
        zipped_lines = zip(left, right)
        lines = [first_line, second_line] + [a + u * ' ' + b for a, b in zipped_lines]
        return lines, n + m + u, max(p, q) + 2, n + u // 2

    def display(self):
        lines, *_ = self._display_aux()
        for line in lines:
            print(line)

    def height(self):
        if self.left is None and self.right is None:
            return 1
        elif self.left is None:
            return self.right.height() + 1
        elif self.right is None:
            return self.left.height() + 1
        else:
            return max(self.left.height(), self.right.height()) + 1

        
# you should extend this class with the type constructors of regular expressions and overwrite the 'thompson' method
# with the specific nfa patterns. for example, parse_regex('ab').thompson() should return something like:

# >(0) --a--> (1) -epsilon-> (2) --b--> ((3))

# extra hint: you can implement each subtype of regex as a @dataclass extending Regex
@dataclass
class Empty():
    def thompson(self) -> NFA[int]:
        nfa = NFA(set(), {0}, 0, {}, {0})
        return nfa
def generate_ranges(start, end):
    nfa_s = set()
    nfa_d = {}
    for i in range(start, end):
        nfa_s.add(chr(i))
        nfa_d.setdefault((0, chr(i)), set()).add(1)
    return nfa_s, nfa_d
@dataclass
class Letter(Regex):
    letter: str
    def generate_ranges(self, start, end):
        nfa_s = set()
        nfa_d = {}
        for i in range(start, end):
            nfa_s.add(chr(i))
            nfa_d.setdefault((0, chr(i)), set()).add(1)
        return nfa_s, nfa_d

    def thompson(self) -> NFA[int]:
        nfa_s = set()
        nfa_d = {}
        if len(self.letter) > 1:
            if self.letter[1] == '0':
                for i in range(0, 10):
                    nfa_s.add(str(i))
                    nfa_d.setdefault((0, str(i)), set()).add(1)
            elif self.letter[1] == 'A':
                nfa_s, nfa_d = self.generate_ranges(65, 91)
            elif self.letter[1] == 'a':
                nfa_s, nfa_d = self.generate_ranges(97, 123)
            return NFA(nfa_s, {0, 1}, 0, nfa_d, {1})
        nfa = NFA({self.letter}, {0, 1}, 0, {(0, self.letter): {1}}, {1})
        return nfa
@dataclass
class Concat(Regex):
    left: Regex
    right: Regex

    def thompson(self) -> NFA[int]:
        left_nfa = self.left.thompson()
        right_nfa = self.right.thompson()
        
        if(len(left_nfa.K) >= len(right_nfa.K)):
            right_nfa = self.right.thompson().remap_states(lambda x: x + len(left_nfa.K))
        else:
            left_nfa = self.left.thompson().remap_states(lambda x: x + len(right_nfa.K))

        left_nfa.S.update(right_nfa.S)
        left_nfa.K.update(right_nfa.K)
        left_nfa.d.update(right_nfa.d)

        for state in left_nfa.F:
            left_nfa.d.setdefault((state, EPSILON), set()).add(right_nfa.q0)
        left_nfa.F = right_nfa.F
        return left_nfa
@dataclass
class Union(Regex):
    left: Regex
    right: Regex

    def thompson(self) -> NFA[int]:
        left_nfa = self.left.thompson()
        right_nfa = self.right.thompson()

        if len(left_nfa.K) >= len(right_nfa.K):
            right_nfa = self.right.thompson().remap_states(lambda x: x + len(left_nfa.K))
        else:
            left_nfa = self.left.thompson().remap_states(lambda x: x + len(right_nfa.K))

        left_nfa.K |= right_nfa.K
        left_nfa.d.update(right_nfa.d)

        new_q0 = len(left_nfa.K)
        new_F = new_q0 + 1
        left_nfa.K |= {new_q0, new_F}
        left_nfa.d.setdefault((new_q0, EPSILON), set()).update({left_nfa.q0, right_nfa.q0})

        for state in left_nfa.F | right_nfa.F:
            left_nfa.d.setdefault((state, EPSILON), set()).add(new_F)

        left_nfa.S |= right_nfa.S
        left_nfa.q0 = new_q0
        left_nfa.F = {new_F}

        return left_nfa

@dataclass
class Star(Regex):
    regex: Regex

    def thompson(self) -> NFA[int]:
        nfa = self.regex.thompson()
        new_q0 = len(nfa.K)

        for state in nfa.F | {new_q0}:
            nfa.d.setdefault((state, EPSILON), set()).update({nfa.q0, new_q0 + 1})

        nfa.q0 = new_q0
        nfa.F = {new_q0 + 1}
        nfa.K.update({new_q0, new_q0 + 1})

        return nfa
@dataclass
class QuestionMark(Regex):
    regex: Regex

    def thompson(self) -> NFA[int]:
        return Union(Empty(), self.regex).thompson()
@dataclass
class Plus(Regex):
    regex: Regex

    def thompson(self) -> NFA[int]:
        return Concat(Star(self.regex), self.regex).thompson()

def parse_regex(regex: str) -> Regex:
    # create a Regex object by parsing the string
    # you can define additional classes and functions to help with the parsing process
    # the checker will call this function, then the thompson method of the generated object. the resulting NFA's
    # behaviour will be checked using your implementation form stage 1
    precedence = {'*': 4, '+': 3, '?': 3, '!': 2, '|': 1}  # Priorități de operatori

    def is_operator(char):

        return char in precedence

    def higher_precedence(op1, op2):

        return precedence[op1] >= precedence[op2]

    def apply_operator(stack, operator):

        if operator in ['*', '+', '?']:
            return Regex(operator, stack.pop(), None)
        else:
            right = stack.pop()
            left = stack.pop()
            return Regex(operator, left, right)

    stack = []
    operators = []
    mappings = {'9': "[0-9]", 'z': "[a-z]", 'Z': "[A-Z]"}
    hot_keys = {'(', ')', '*', '+', '?', '|', '!'}
    #inlocuieste ! cu \!
    regex = regex.replace('!', '\\!')
    is_interval = False
    for i, char in enumerate(regex):
        if char == ':':
            stack.append(Regex(char, None, None))
            continue
        elif regex[i - 1] != '\\' and char in hot_keys:
            if char == '(':
                if i > 0 and regex[i - 1] != '|':
                    while operators and operators[-1] != '(' and higher_precedence(operators[-1], '!'):
                        stack.append(apply_operator(stack, operators.pop()))
                    if regex[i - 1] != '(' or (regex[i - 1] == '(' and regex[i - 2] == '\\'):
                        operators.append('!')
                operators.append(char)
            elif char == ')':
                while operators and operators[-1] != '(':
                    stack.append(apply_operator(stack, operators.pop()))
                operators.pop()
            else:  # Pentru operatori și alte caractere
                while operators and operators[-1] != '(' and higher_precedence(operators[-1], char):
                    stack.append(apply_operator(stack, operators.pop()))
                operators.append(char)
        else:
            if char in {' ',']','[','\n','\\','\\ '} or is_interval == True:
                if char == '\\':
                    while operators and operators[-1] not in {'!', '(', '|'}:
                        stack.append(apply_operator(stack, operators.pop()))
                    stack.append(Regex(regex[i + 1], None, None))
                    if not (regex[i - 1] in {'(', '|', ' '} or i + 2 < len(regex) and regex[i+2] == '(') or regex[i-1].isalpha() or regex[i-1] == '+':
                        operators.append('!')
                if char == '\n':
                    stack.append(Regex(char, None, None))
                    if i + 1 < len(regex) and not is_operator(regex[i+1]):
                        operators.append('!')
                if char == '[':
                    is_interval = True
                    if i > 0 and regex[i - 1] not in {'|', '('}:
                        while operators and operators[-1] not in {'(', '!'}:
                            stack.append(apply_operator(stack, operators.pop()))
                        operators.append('!')
                if char == ']':
                    is_interval = False
                    if regex[i - 1] in mappings:
                        stack.append(Regex(mappings[regex[i - 1]], None, None))
                continue
            elif i > 0:
                while(regex[i-1] == ' '):
                    i = i - 1
                if regex[i - 1].isalpha():
                    operators.append('!')
                if regex[i - 1] in {'?', '+', '*'}:
                    stack.append(apply_operator(stack, operators.pop()))
                    if char.isalpha():
                        operators.append('!')
            if char.isalpha() or char.isdigit():
                stack.append(Regex(char, None, None))
                if regex[i-1] == '\\' and regex[i] == ' ' or i < len(regex)-1 and regex[i + 1].isdigit() or i > 0 and regex[i-1] == ')':
                    operators.append('!')
            elif char != '\\' and regex[i-1] != '\\' and len(regex) > 1:
                stack.append(Regex(char, None, None))
                if i + 1 >= len(regex) or i + 1 < len(regex) and not regex[i+1] in hot_keys:
                    operators.append('!')
    #print("stacklen ", len(stack))
    #print("stack ", stack[0].value)
    #print(operators)
    while operators:
        if(operators == ['!'] and len(stack) <2):
            break
        stack.append(apply_operator(stack, operators.pop()))
    while(len(stack) > 1):
        stack.append(apply_operator(stack, '!'))
    #stack[0].display()
    #print("stacklen ", len(stack))
    return stack.pop()

