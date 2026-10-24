# Regular Expressions

A **regular expression** (regex) is a tiny pattern language for describing sets of strings: "a word followed by `=` and digits", "an email-like token", "a NMEA GPS sentence". Python's `re` module searches, extracts, splits and rewrites text with regexes. They're indispensable for log parsing, data cleaning, tokenisers and validation. They're also easy to get wrong: greedy matching, escaping, and catastrophic backtracking. This lesson builds the syntax systematically and teaches you when **not** to use a regex.

## 1. Always use raw strings

```python
import re
re.findall(r"\d+", "a1b22c333")      # ['1', '22', '333']
```

Write patterns as **raw strings** `r"..."`. In a normal string, `"\b"` is a backspace character, not the regex word boundary, and `"\\d"` needs doubled backslashes. A raw string passes backslashes through to `re` untouched.

## 2. Syntax

| Pattern | Matches |
|---|---|
| `.` | any character except newline |
| `\d` `\w` `\s` | digit, word char `[A-Za-z0-9_]` (plus Unicode letters), whitespace |
| `\D` `\W` `\S` | the complements |
| `[abc]` `[a-z0-9]` `[^,]` | character class, range, negated class |
| `^` `$` | start / end of the string (of each line with `re.M`) |
| `\b` | word boundary (zero-width) |
| `a\|b` | alternation |
| `(...)` | capturing group |
| `(?:...)` | non-capturing group |
| `(?P<name>...)` | named group |
| `\1`, `(?P=name)` | backreference to a group |

**Quantifiers** apply to the previous item:

| Greedy | Lazy | Meaning |
|---|---|---|
| `*` | `*?` | 0 or more |
| `+` | `+?` | 1 or more |
| `?` | `??` | 0 or 1 |
| `{n}`, `{n,m}` | `{n,m}?` | exactly n, or between n and m |

### Greedy vs lazy

```python
re.findall(r"<.+>", "<a><b>")     # ['<a><b>']: greedy grabs as MUCH as possible
re.findall(r"<.+?>", "<a><b>")    # ['<a>', '<b>']: lazy grabs as little as possible
re.findall(r"<[^>]+>", "<a><b>")  # ['<a>', '<b>']: a negated class: clearer and faster
```

## 3. The functions

| Function | Returns |
|---|---|
| `re.search(p, s)` | the first match **anywhere**, or `None` |
| `re.match(p, s)` | a match only at the **start** of `s` |
| `re.fullmatch(p, s)` | a match only if the **whole** string matches (use it for validation) |
| `re.findall(p, s)` | list of strings (or of group tuples if the pattern has groups) |
| `re.finditer(p, s)` | iterator of match objects (lazy, has positions) |
| `re.sub(p, repl, s)` | new string with replacements (`repl` can be a function) |
| `re.split(p, s)` | split on the pattern |
| `re.compile(p, flags)` | a reusable compiled pattern object |

```python
re.match(r"\d", "a1")                 # None: match anchors at position 0
re.fullmatch(r"\d+", "123")           # <re.Match object; span=(0, 3), match='123'>
```

### Match objects and groups

```python
m = re.search(r"(?P<key>\w+)=(?P<val>\d+)", "speed=42 mode=x")
m.group(0)        # 'speed=42': the whole match
m.group("key")    # 'speed'
m["val"]          # '42'
m.groupdict()     # {'key': 'speed', 'val': '42'}
m.span()          # (0, 8)
```

`findall` changes shape when there are groups:

```python
re.findall(r"(\d+)-(\d+)", "1-2 3-4")     # [('1', '2'), ('3', '4')]: tuples of groups
```

> [!WARNING]
> Adding parentheses just for grouping, like `(ab)+`, makes `findall` return the group instead of the whole match. Use `(?:ab)+` when you don't want to capture.

### Substitution and splitting

```python
re.sub(r"(\w+)@(\w+)", r"\2 at \1", "ada@lab bob@uni")   # 'lab at ada uni at bob'
re.sub(r"\d+", lambda m: str(int(m.group()) * 2), "a1 b20")   # 'a2 b40'
re.sub(r"\s+", " ", "  a \n b  ").strip()                 # 'a b': normalise whitespace
re.split(r"[,;]\s*", "a, b;c ;d")                         # ['a', 'b', 'c ', 'd']
```

## 4. Lookarounds (zero-width assertions)

| Syntax | Meaning |
|---|---|
| `X(?=Y)` | X followed by Y (Y isn't consumed) |
| `X(?!Y)` | X **not** followed by Y |
| `(?<=Y)X` | X preceded by Y (Y must have a fixed width) |
| `(?<!Y)X` | X not preceded by Y |

```python
re.findall(r"(?<=\$)\d+", "cost $30 and $45")    # ['30', '45']: digits after $, without the $
re.fullmatch(r"(?=.*\d)(?=.*[A-Z]).{8,}", pw)     # password: has a digit, an uppercase letter, length >= 8
```

## 5. Flags

| Flag | Inline | Effect |
|---|---|---|
| `re.I` | `(?i)` | case-insensitive |
| `re.M` | `(?m)` | `^`/`$` match at every line |
| `re.S` | `(?s)` | `.` also matches newline |
| `re.X` | `(?x)` | verbose: whitespace and `#` comments allowed in the pattern |
| `re.A` | `(?a)` | `\w`, `\d` are ASCII only |

```python
DATE = re.compile(r"""
    (?P<year>\d{4}) -     # year
    (?P<month>\d{2}) -    # month
    (?P<day>\d{2})        # day
""", re.X)
DATE.fullmatch("2026-10-24").groupdict()   # {'year': '2026', 'month': '10', 'day': '24'}
```

Compile patterns you reuse in loops: `re` caches recent patterns, but a module-level compiled constant is clearer and avoids even the cache lookup.

## 6. Catastrophic backtracking

Python's engine is a **backtracking** matcher. Nested quantifiers over overlapping alternatives can take **exponential time** on non-matching input:

```python
re.fullmatch(r"(a+)+b", "a" * 30)    # tries ~2^30 ways to split the a's before failing
```

This is ReDoS (regex denial of service), and it has taken down real production systems. Avoid patterns like `(a+)+`, `(a|a)*` and `(.*)*`. Make alternatives mutually exclusive, use specific classes (`[^,]*` instead of `.*`), and never run user-supplied patterns on servers. Python 3.11+ supports possessive quantifiers (`a++`) and atomic groups (`(?>...)`), which forbid backtracking into a group.

> [!TIP]
> **When not to use a regex:** for fixed substrings use `in`, `str.startswith` and `str.split`. For structured formats (JSON, CSV, HTML, XML) use real parsers. Regexes can't parse nested structures like balanced parentheses. A regex is the right tool for **flat, line-oriented text patterns**.

## 7. Exam-ready answers

> [!EXAM]
> **Regular expressions in Python.** A regular expression is a pattern describing a set of strings, built from literals, character classes (`[a-z]`, `\d`, `\w`, `\s`), anchors (`^`, `$`, `\b`), alternation (`|`), groups (`(...)`, named `(?P<name>...)`, non-capturing `(?:...)`) and quantifiers (`*`, `+`, `?`, `{m,n}`), which are greedy by default and lazy when followed by `?`. The `re` module provides `search` (first match anywhere), `match` (match at the start), `fullmatch` (whole-string match), `findall` and `finditer` (all matches), `sub` (replacement) and `split`; match objects expose groups and positions. Patterns should be written as raw strings, may be precompiled with `re.compile`, and can use flags such as `IGNORECASE`, `MULTILINE`, `DOTALL` and `VERBOSE`. Lookahead and lookbehind assertions test context without consuming characters.

## 8. Cheat sheet

| Need | Pattern / code |
|---|---|
| validate the whole string | `re.fullmatch(p, s)` |
| all numbers (int/float, signed) | `r"[-+]?\d+(?:\.\d+)?"` |
| `key=value` pairs | `dict(re.findall(r"(\w+)=(\S+)", s))` |
| collapse whitespace | `re.sub(r"\s+", " ", s)` |
| shortest match | `.*?` or a negated class `[^>]*` |
| don't capture | `(?:...)` |
| readable big pattern | `re.compile(r"""...""", re.X)` |
| literal user text in a pattern | `re.escape(text)` |

> [!INTERVIEW]
> **"Extract all `key=value` pairs from a log line where values may be quoted and contain spaces."** Use `re.findall(r'(\w+)=("[^"]*"|\S+)', line)`: alternation tries a quoted value (any non-quote characters between quotes) first, then falls back to a run of non-spaces. Then strip the quotes. Point out the negated class `[^"]*` instead of `.*?` (no backtracking surprises), use `finditer` for very long lines, and say you'd switch to `shlex.split` or a real parser if escaping rules get more complex.
