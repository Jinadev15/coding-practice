---
id: py-tokenizer
title: Regex Tokenizer for a Mini Language
difficulty: Hard
order: 2
tags: regex, tokenizer, finditer, named groups, lexer
---
## Statement
Write the **lexer** of a tiny robot-command language. Each input line is one program. Split it into tokens with **one master regex** built from named groups:

| Token | Pattern |
|---|---|
| `NUMBER` | an integer or decimal: `12`, `3.5`, `.5` (no sign; `-` is an operator) |
| `STRING` | double-quoted, where `\"` is an escaped quote inside: `"say \"hi\""` |
| `KEYWORD` | exactly `move`, `turn`, `if`, `else`, `while`, `let` |
| `IDENT` | a letter or `_`, then letters, digits or `_` (and not a keyword: `lettuce` is an IDENT) |
| `OP` | `==`, `!=`, `<=`, `>=`, `+`, `-`, `*`, `/`, `<`, `>`, `=` (longest match first) |
| `PUNCT` | `(`, `)`, `{`, `}`, `;`, `,` |

Whitespace separates tokens and is skipped. A `#` starts a comment that runs to the end of the line.

Output, for each line, the tokens as `KIND:text` separated by spaces (STRING text includes its quotes, exactly as written). If the line contains a character that starts no valid token (e.g. `@`, or an unterminated string), print `ERROR at COLUMN` instead, where the column is 1-based. Print `EMPTY` for a line with no tokens.

## Starter
```python
import re
import sys

for line in sys.stdin.read().splitlines():
    pass
```

## Tests
=== sample
let speed = 2.5;
move(speed * .5) # half speed
if x >= 10 { turn(-90) } else { say("done \"ok\"") }
lettuce == let
a @ b
   # only a comment
---
KEYWORD:let IDENT:speed OP:= NUMBER:2.5 PUNCT:;
KEYWORD:move PUNCT:( IDENT:speed OP:* NUMBER:.5 PUNCT:)
KEYWORD:if IDENT:x OP:>= NUMBER:10 PUNCT:{ KEYWORD:turn PUNCT:( OP:- NUMBER:90 PUNCT:) PUNCT:} KEYWORD:else PUNCT:{ IDENT:say PUNCT:( STRING:"done \"ok\"" PUNCT:) PUNCT:}
IDENT:lettuce OP:== KEYWORD:let
ERROR at 3
EMPTY
=== hidden
x=1
"unterminated
"a\\" b"
while(i!=3){i=i+1;}
3.14.15
_hidden_9 <= 0009
a<=>b
"tab	inside" ,
---
IDENT:x OP:= NUMBER:1
ERROR at 1
ERROR at 8
KEYWORD:while PUNCT:( IDENT:i OP:!= NUMBER:3 PUNCT:) PUNCT:{ IDENT:i OP:= IDENT:i OP:+ NUMBER:1 PUNCT:; PUNCT:}
NUMBER:3.14 NUMBER:.15
IDENT:_hidden_9 OP:<= NUMBER:0009
IDENT:a OP:<= OP:> IDENT:b
STRING:"tab	inside" PUNCT:,

## Hints
- Build the master pattern as `"|".join(f"(?P<{name}>{pattern})" for name, pattern in SPEC)`. Order matters: put KEYWORD before IDENT, with `\b` after the keyword alternatives, and the two-character operators before the one-character ones.
- Use `pattern.match(line, pos)` in a loop instead of `finditer`. `finditer` silently **skips** characters that don't match, which hides errors. `m.lastgroup` tells you which named group matched.
- String pattern: `"(?:\\.|[^"\\])*"`, meaning any escaped character or any non-quote, non-backslash character, repeated, between quotes.
- Include `SKIP` (whitespace) and `COMMENT` (`#.*`) groups and simply don't output them.

## Solution
```python
import re
import sys

SPEC = [
    ("SKIP",    r"[ \t]+"),
    ("COMMENT", r"\#.*"),
    ("NUMBER",  r"\d+(?:\.\d*)?|\.\d+"),
    ("STRING",  r'"(?:\\.|[^"\\])*"'),
    ("KEYWORD", r"(?:move|turn|if|else|while|let)\b"),
    ("IDENT",   r"[A-Za-z_]\w*"),
    ("OP",      r"==|!=|<=|>=|[+\-*/<>=]"),
    ("PUNCT",   r"[(){};,]"),
]
MASTER = re.compile("|".join(f"(?P<{name}>{pat})" for name, pat in SPEC))

def tokenize(line):
    pos, toks = 0, []
    while pos < len(line):
        m = MASTER.match(line, pos)
        if not m:
            return None, pos + 1                 # 1-based error column
        kind = m.lastgroup
        if kind not in ("SKIP", "COMMENT"):
            toks.append(f"{kind}:{m.group()}")
        pos = m.end()
    return toks, None

for line in sys.stdin.read().splitlines():
    toks, err = tokenize(line)
    if err is not None:
        print(f"ERROR at {err}")
    elif not toks:
        print("EMPTY")
    else:
        print(" ".join(toks))
```

This is the **master-pattern lexer** idiom from the `re` documentation, and it's how many real tokenizers are written:
- One alternation of named groups, tried at the current position with `match(line, pos)`. `m.lastgroup` names the token kind.
- **Order encodes priority:** `KEYWORD` (with `\b`) before `IDENT` makes `let` a keyword but `lettuce` an identifier, and `<=` before `<` gives longest-match for operators. `3.14.15` lexes as `NUMBER:3.14` then `NUMBER:.15`, which is a parser's problem, not the lexer's.
- **Explicit error positions:** a failed `match` at `pos` pinpoints the bad character. `finditer` would skip it silently.
- **The escaped-string pattern** `"(?:\\.|[^"\\])*"` consumes `\"` as a unit, so the closing quote is the first unescaped one. Its two alternatives can't overlap, so there's no catastrophic backtracking.

The next step in a compiler pipeline feeds these tokens to a recursive-descent parser (the Expression Trees problems in the C++ track).
