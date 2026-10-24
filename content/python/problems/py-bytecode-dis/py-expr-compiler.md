---
id: py-expr-compiler
title: Compile Python Expressions to Stack Bytecode
difficulty: Hard
order: 1
tags: ast, compilers, bytecode, stack machine, constant folding
---
## Statement
Build a miniature version of CPython's pipeline: **parse → compile to stack bytecode → (optimise) → execute**, using the `ast` module for parsing.

Supported expressions: integer literals, variable names, `+ - * // %` (binary), unary `-`, comparisons `<`, `>` and `==` (a single comparison, no chains; they produce `1`/`0`), and the conditional expression `A if C else B`.

Instruction set (one per line in the listing):

| Instruction | Effect |
|---|---|
| `PUSH n` | push an integer constant |
| `LOAD name` | push a variable's value (`NameError: name` if undefined at run time) |
| `ADD`, `SUB`, `MUL`, `FLOORDIV`, `MOD` | pop b, pop a, push a op b (Python semantics; division by zero → `ZeroDivisionError`) |
| `NEG` | negate the top |
| `LT`, `GT`, `EQ` | pop b, pop a, push 1 or 0 |
| `JUMP_IF_FALSE k` | pop; if it's 0, jump to instruction index k |
| `JUMP k` | jump to index k |

Input: first line is an expression, second line is variables as `name=value` pairs separated by spaces (possibly empty). Output:
1. `code:` then the listing, one instruction per line, as `  i: INSTR [arg]`;
2. `folded:` then the listing after **constant folding**: any subexpression made only of literals is computed at compile time (so `x * (2 + 3)` becomes `LOAD x / PUSH 5 / MUL`); a conditional whose condition folds to a constant keeps only the chosen branch. Never fold an operation that would raise (keep `1 // 0` unfolded);
3. `max stack: N` (for the folded code, the maximum operand stack depth during execution), or `max stack: -` if execution raised an error;
4. `result: V` or `error: ExceptionName` from executing the folded code.

Anything else (floats, function calls, `and`/`or`, chained comparisons) → print only `unsupported: NodeClassName` (e.g. `unsupported: Call`).

## Starter
```python
import ast
import sys

expr, *rest = sys.stdin.read().split("\n")
```

## Tests
=== sample
x * (2 + 3) - -y
x=4 y=6
---
code:
  0: LOAD x
  1: PUSH 2
  2: PUSH 3
  3: ADD
  4: MUL
  5: LOAD y
  6: NEG
  7: SUB
folded:
  0: LOAD x
  1: PUSH 5
  2: MUL
  3: LOAD y
  4: NEG
  5: SUB
max stack: 2
result: 26
=== hidden
2 * 3 + 4
---
code:
  0: PUSH 2
  1: PUSH 3
  2: MUL
  3: PUSH 4
  4: ADD
folded:
  0: PUSH 10
max stack: 1
result: 10
=== hidden
a if a > b else b
a=3 b=9
---
code:
  0: LOAD a
  1: LOAD b
  2: GT
  3: JUMP_IF_FALSE 6
  4: LOAD a
  5: JUMP 7
  6: LOAD b
folded:
  0: LOAD a
  1: LOAD b
  2: GT
  3: JUMP_IF_FALSE 6
  4: LOAD a
  5: JUMP 7
  6: LOAD b
max stack: 2
result: 9
=== hidden
(1 if 2 > 3 else 7) * n
n=5
---
code:
  0: PUSH 2
  1: PUSH 3
  2: GT
  3: JUMP_IF_FALSE 6
  4: PUSH 1
  5: JUMP 7
  6: PUSH 7
  7: LOAD n
  8: MUL
folded:
  0: PUSH 7
  1: LOAD n
  2: MUL
max stack: 2
result: 35
=== hidden
1 // 0 + x
x=1
---
code:
  0: PUSH 1
  1: PUSH 0
  2: FLOORDIV
  3: LOAD x
  4: ADD
folded:
  0: PUSH 1
  1: PUSH 0
  2: FLOORDIV
  3: LOAD x
  4: ADD
max stack: -
error: ZeroDivisionError
=== hidden
q % 7
---
code:
  0: LOAD q
  1: PUSH 7
  2: MOD
folded:
  0: LOAD q
  1: PUSH 7
  2: MOD
max stack: -
error: NameError
=== hidden
f(3)
---
unsupported: Call
=== hidden
1.5 + 2
---
unsupported: Constant
=== hidden
1 < x < 3
x=2
---
unsupported: Compare
=== hidden
-(-(a - 10)) == a // 1 - 10
a=-17
---
code:
  0: LOAD a
  1: PUSH 10
  2: SUB
  3: NEG
  4: NEG
  5: LOAD a
  6: PUSH 1
  7: FLOORDIV
  8: PUSH 10
  9: SUB
  10: EQ
folded:
  0: LOAD a
  1: PUSH 10
  2: SUB
  3: NEG
  4: NEG
  5: LOAD a
  6: PUSH 1
  7: FLOORDIV
  8: PUSH 10
  9: SUB
  10: EQ
max stack: 3
result: 1
=== hidden
((a + b) * (c + d)) * ((e + f) * (g + h))
a=1 b=2 c=3 d=4 e=5 f=6 g=7 h=8
---
code:
  0: LOAD a
  1: LOAD b
  2: ADD
  3: LOAD c
  4: LOAD d
  5: ADD
  6: MUL
  7: LOAD e
  8: LOAD f
  9: ADD
  10: LOAD g
  11: LOAD h
  12: ADD
  13: MUL
  14: MUL
folded:
  0: LOAD a
  1: LOAD b
  2: ADD
  3: LOAD c
  4: LOAD d
  5: ADD
  6: MUL
  7: LOAD e
  8: LOAD f
  9: ADD
  10: LOAD g
  11: LOAD h
  12: ADD
  13: MUL
  14: MUL
max stack: 4
result: 3465

## Hints
- `ast.parse(expr, mode="eval").body` gives the root node. Walk it recursively with `isinstance` checks or `match`: `ast.Constant` (check `type(value) is int`), `ast.Name`, `ast.BinOp` (`ast.Add`, `ast.Sub`, …), `ast.UnaryOp` (`ast.USub`), `ast.Compare` (exactly one op), `ast.IfExp`.
- A conditional compiles to: `<test>`, `JUMP_IF_FALSE else_start`, `<body>`, `JUMP end`, `<orelse>`. Emit placeholders and patch the jump targets once you know them (backpatching).
- Fold on the **AST** before generating code: a recursive `fold(node)` that returns a `Constant` node when all its children fold to constants, inside a try/except so operations that raise stay unfolded.
- Max stack depth: track the depth while executing (jumps mean the static depth depends on the path taken; here, measure the actual execution).

## Solution
```python
import ast
import operator
import sys

BINOPS = {ast.Add: ("ADD", operator.add), ast.Sub: ("SUB", operator.sub), ast.Mult: ("MUL", operator.mul),
          ast.FloorDiv: ("FLOORDIV", operator.floordiv), ast.Mod: ("MOD", operator.mod)}
CMPOPS = {ast.Lt: ("LT", operator.lt), ast.Gt: ("GT", operator.gt), ast.Eq: ("EQ", operator.eq)}

class Unsupported(Exception):
    pass

def check(node):
    match node:
        case ast.Constant(value=v) if type(v) is int: return
        case ast.Name(): return
        case ast.BinOp(op=op) if type(op) in BINOPS: check(node.left); check(node.right)
        case ast.UnaryOp(op=ast.USub()): check(node.operand)
        case ast.Compare(ops=[op], comparators=[_]) if type(op) in CMPOPS: check(node.left); check(node.comparators[0])
        case ast.IfExp(): check(node.test); check(node.body); check(node.orelse)
        case _: raise Unsupported(type(node).__name__)

def fold(node):
    match node:
        case ast.BinOp():
            l, r = fold(node.left), fold(node.right)
            if isinstance(l, ast.Constant) and isinstance(r, ast.Constant):
                try:
                    return ast.Constant(BINOPS[type(node.op)][1](l.value, r.value))
                except ArithmeticError:
                    pass                       # keep it: the error must happen at run time
            return ast.BinOp(l, node.op, r)
        case ast.UnaryOp():
            o = fold(node.operand)
            return ast.Constant(-o.value) if isinstance(o, ast.Constant) else ast.UnaryOp(node.op, o)
        case ast.Compare():
            l, r = fold(node.left), fold(node.comparators[0])
            if isinstance(l, ast.Constant) and isinstance(r, ast.Constant):
                return ast.Constant(int(CMPOPS[type(node.ops[0])][1](l.value, r.value)))
            return ast.Compare(l, node.ops, [r])
        case ast.IfExp():
            t = fold(node.test)
            if isinstance(t, ast.Constant):
                return fold(node.body) if t.value else fold(node.orelse)
            return ast.IfExp(t, fold(node.body), fold(node.orelse))
        case _:
            return node

def compile_expr(node, code):
    match node:
        case ast.Constant(value=v): code.append(["PUSH", v])
        case ast.Name(id=name): code.append(["LOAD", name])
        case ast.BinOp():
            compile_expr(node.left, code); compile_expr(node.right, code)
            code.append([BINOPS[type(node.op)][0]])
        case ast.UnaryOp():
            compile_expr(node.operand, code); code.append(["NEG"])
        case ast.Compare():
            compile_expr(node.left, code); compile_expr(node.comparators[0], code)
            code.append([CMPOPS[type(node.ops[0])][0]])
        case ast.IfExp():
            compile_expr(node.test, code)
            jf = len(code); code.append(["JUMP_IF_FALSE", None])
            compile_expr(node.body, code)
            j = len(code); code.append(["JUMP", None])
            code[jf][1] = len(code)               # backpatch: the else branch starts here
            compile_expr(node.orelse, code)
            code[j][1] = len(code)                # end of the conditional
    return code

def run(code, env):
    ops = {name: fn for name, fn in BINOPS.values()} | {name: fn for name, fn in CMPOPS.values()}
    stack, pc, depth = [], 0, 0
    while pc < len(code):
        ins = code[pc]
        op = ins[0]
        pc += 1
        if op == "PUSH": stack.append(ins[1])
        elif op == "LOAD":
            if ins[1] not in env: raise NameError(ins[1])
            stack.append(env[ins[1]])
        elif op == "NEG": stack.append(-stack.pop())
        elif op == "JUMP_IF_FALSE":
            if stack.pop() == 0: pc = ins[1]
        elif op == "JUMP": pc = ins[1]
        else:
            b, a = stack.pop(), stack.pop()
            stack.append(int(ops[op](a, b)))
        depth = max(depth, len(stack))
    return stack.pop(), depth

def listing(code):
    return "\n".join(f"  {i}: {ins[0]}" + (f" {ins[1]}" if len(ins) > 1 else "") for i, ins in enumerate(code))

lines = sys.stdin.read().split("\n")
expr = lines[0]
env = {}
if len(lines) > 1:
    for pair in lines[1].split():
        k, v = pair.split("=")
        env[k] = int(v)
tree = ast.parse(expr, mode="eval").body
try:
    check(tree)
except Unsupported as e:
    print(f"unsupported: {e}")
    sys.exit(0)
print("code:")
print(listing(compile_expr(tree, [])))
folded = compile_expr(fold(tree), [])
print("folded:")
print(listing(folded))
try:
    value, depth = run(folded, env)
    print(f"max stack: {depth}")
    print(f"result: {value}")
except Exception as e:
    print(f"max stack: -")
    print(f"error: {type(e).__name__}")
```

This is the same pipeline CPython runs: `ast.parse` produces the tree, a recursive code generator emits stack instructions (operands first, then the operator, which is postfix order), conditionals become jumps whose targets are **backpatched** once the branch lengths are known, and an optimiser folds constants (CPython's AST optimizer folds `24 * 60 * 60` the same way). The VM is a loop over instructions with an operand stack, like `ceval.c`. `max stack` matters because CPython precomputes each code object's `co_stacksize` to allocate the frame's stack exactly.
