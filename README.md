# Formal Language and Automata Project
We will interpret a functional language, inspired by Lisp ("List Processing"), but much simplified. The text is parsed into tokens using a lexer, and then the expressions are interpreted.

A program is a list of atoms, where an atom can be:
```
a natural number
an empty list ()
a lambda expression
a function invocation
another list of atoms
```

The output is a number, or a list consisting only of:
```
numbers
other lists (composed only of numbers or other lists)
```
A list in the form (f x) can be evaluated as long as f is:
```
a lambda expression
a function from the standard library
```
For simplicity, we will limit ourselves to 2 standard functions:
```
+, which when applied to a list, recursively sums the elements of the list and returns an atom (it cannot be applied to lists that contain other functions/expressions)
++, which when applied to a list, concatenates all component lists (if there are atoms in the list, they are added to the resulting list)
```
