---
id: py-m1-expression
title: Expression Evaluator
difficulty: Hard
order: 2
tags: parsing, recursion, tokenizer, grammar
---
## Statement
Evaluate integer arithmetic expressions **without `eval`**. The grammar:

```text
expr   := term (('+' | '-') term)*
term   := factor (('*' | '/' | '%') factor)*
factor := ('-' | '+') factor | power
power  := atom ('^' factor)?          # right-associative, binds tighter than unary minus on its left operand
atom   := NUMBER | '(' expr ')'
```

- `/` is **floor division** (Python's `//`), and `%` is Python's `%`.
- `^` is exponentiation and is right-associative: `2^3^2 = 2^9 = 512`. The exponent is always ≥ 0 in the tests.
- `-2^2 = -4` (unary minus applies to the power, as in maths).
- Spaces may appear anywhere.

For each line print the value, or `error` for division/modulo by zero, invalid characters, unbalanced parentheses or any other syntax error.

## Starter
```python
def evaluate(text):
    # return an int, or raise an exception on any error
    pass
```

## Driver
```python
import sys
for line in sys.stdin.read().splitlines():
    if not line.strip():
        continue
    try:
        print(evaluate(line))
    except Exception:
        print("error")
```

## Tests
=== sample
1 + 2 * 3
(1 + 2) * 3
2^3^2
-2^2
7 / 2
-7 / 2
---
7
9
512
-4
3
-4
=== hidden
10 % 3
1 / 0
((4))
2 * (3 + 4) * 5 - 6 / 2
- - 3
(1 + 2
1 + 2)
3 $ 4
2 ^ -1

---
1
error
4
67
3
error
error
error
error
=== hidden
123456789 * 987654321
(-2)^3
-(2^2)^3
100 - 50 - 25
2^10 % 1000
+5 * -2
---
121932631112635269
-8
-64
25
24
-10
=== hidden

1 2
()
5 %0
---
error
error
error

## Hints
- First **tokenise**: numbers (maximal runs of digits) and single-character operators; anything else → error.
- Then write one function per grammar rule (**recursive descent**), sharing a position index. Each function consumes the tokens of its rule and returns a value.
- `power` parses an atom, then if the next token is `^`, parses a **factor** (not an atom) for the exponent. That gives right-associativity. A negative exponent result (as in `2 ^ -1`) must print `error`.
- After parsing `expr`, every token must be consumed, otherwise there's a syntax error (`1 + 2)`).

## Solution
A tokenizer followed by a **recursive-descent parser**: one function per grammar rule. Precedence comes from the call structure (`expr` calls `term`, which calls `factor`, which calls `power`), so lower-precedence operators are handled higher up.

```python
def tokenize(text):
    tokens, i = [], 0
    while i < len(text):
        ch = text[i]
        if ch.isspace():
            i += 1
        elif ch.isdigit():
            j = i
            while j < len(text) and text[j].isdigit():
                j += 1
            tokens.append(int(text[i:j]))
            i = j
        elif ch in "+-*/%^()":
            tokens.append(ch)
            i += 1
        else:
            raise ValueError(f"bad character {ch!r}")
    return tokens

def evaluate(text):
    tokens = tokenize(text)
    pos = 0

    def peek():
        return tokens[pos] if pos < len(tokens) else None

    def take(expected=None):
        nonlocal pos
        tok = peek()
        if tok is None or (expected is not None and tok != expected):
            raise SyntaxError("unexpected token")
        pos += 1
        return tok

    def expr():
        value = term()
        while peek() in ("+", "-"):
            value = value + term() if take() == "+" else value - term()
        return value

    def term():
        value = factor()
        while peek() in ("*", "/", "%"):
            op = take()
            rhs = factor()
            if op == "*":
                value *= rhs
            elif op == "/":
                value //= rhs          # ZeroDivisionError propagates as an error
            else:
                value %= rhs
        return value

    def factor():
        if peek() in ("+", "-"):
            sign = take()
            value = factor()
            return -value if sign == "-" else value
        return power()

    def power():
        base = atom()
        if peek() == "^":
            take()
            exp = factor()
            if exp < 0:
                raise ValueError("negative exponent")
            return base ** exp
        return base

    def atom():
        tok = peek()
        if isinstance(tok, int):
            return take()
        if tok == "(":
            take("(")
            value = expr()
            take(")")
            return value
        raise SyntaxError("expected a number or '('")

    result = expr()
    if pos != len(tokens):
        raise SyntaxError("trailing tokens")
    return result
```

Precedence falls out of the structure: `-2^2` parses as `factor → '-' factor → power(2^2)`, giving −4. `(-2)^3` parses the parenthesised atom first. Right-associativity of `^` comes from the exponent being parsed by `factor`, which can itself contain another `^`. The empty input raises in `atom` (no token). This is a miniature version of what every compiler front end does; you'll meet it again with parse trees in the Trees topic and with the Interpreter design pattern.
