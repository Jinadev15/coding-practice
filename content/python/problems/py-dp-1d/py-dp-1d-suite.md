---
id: py-dp-1d-suite
title: "1-D DP Suite: Stocks with Cooldown, Decodings, Word Breaks, LIS"
difficulty: Hard
order: 1
tags: dynamic programming, state machine, counting, patience sorting
time_limit: 3
---
## Statement
Four 1-D dynamic programs. Inputs reach 200 000 elements, so each must be O(n) or O(n log n). (`count_word_breaks` is O(n · L), where L is the longest word.)

```python
def max_profit_cooldown(prices, fee):
    """Buy/sell one share at a time, any number of transactions. After a SELL you must wait one day
    before buying again, and every sell pays `fee`. Return the maximum profit."""

def decode_ways(s):
    """'A'..'Z' map to '1'..'26'. Count the decodings of the digit string s, modulo 1_000_000_007."""

def count_word_breaks(s, words):
    """Number of ways to split s into a sequence of dictionary words (reuse allowed), mod 1_000_000_007."""

def lis_length(a, strict):
    """Length of the longest increasing subsequence; strictly increasing if strict else non-decreasing."""
```

Test lines are `(function_name, args)` literals or `gen NAME SEED N`.

## Starter
```python
def max_profit_cooldown(prices, fee):
    return 0

def decode_ways(s):
    def go(i):
        if i == len(s): return 1
        if s[i] == "0": return 0
        r = go(i + 1)
        if i + 1 < len(s) and int(s[i:i + 2]) <= 26: r += go(i + 2)
        return r
    return go(0) % 1_000_000_007

def count_word_breaks(s, words):
    return 0

def lis_length(a, strict):
    n = len(a)
    dp = [1] * n
    for i in range(n):
        for j in range(i):
            if a[j] < a[i] or (not strict and a[j] == a[i]):
                dp[i] = max(dp[i], dp[j] + 1)
    return max(dp, default=0)
```

## Driver
```python
import ast
import random
import sys

FUNCS = {f.__name__: f for f in (max_profit_cooldown, decode_ways, count_word_breaks, lis_length)}
for line in sys.stdin.read().splitlines():
    if not line.strip():
        continue
    if line.startswith("gen "):
        _, name, seed, n = line.split()
        rng = random.Random(int(seed)); n = int(n)
        if name == "max_profit_cooldown":
            p = [rng.randrange(1, 10**4) for _ in range(n)]
            print(name, n, max_profit_cooldown(p, 0), max_profit_cooldown(p, 50))
        elif name == "decode_ways":
            s = "".join(rng.choice("1122126") for _ in range(n))
            print(name, n, decode_ways(s), decode_ways(s[:100] + "0" + s[100:]), decode_ways("1" + "0" * 3))
        elif name == "count_word_breaks":
            s = "".join(rng.choice("ab") for _ in range(n))
            print(name, n, count_word_breaks(s, ["a", "b", "ab", "ba", "aab", "abab", "bbbb"]))
        else:
            a = [rng.randrange(n) for _ in range(n)]
            print(name, n, lis_length(a, True), lis_length(a, False), lis_length(sorted(a), True), lis_length(sorted(a), False))
        continue
    name, args = ast.literal_eval(line)
    print(name, "->", FUNCS[name](*args))
```

## Tests
=== sample
("max_profit_cooldown", ([1, 2, 3, 0, 2], 0))
("decode_ways", ("226",))
("count_word_breaks", ("catsanddog", ["cat", "cats", "and", "sand", "dog"]))
("lis_length", ([10, 9, 2, 5, 3, 7, 101, 18], True))
---
max_profit_cooldown -> 3
decode_ways -> 3
count_word_breaks -> 2
lis_length -> 4
=== hidden
("max_profit_cooldown", ([], 0))
("max_profit_cooldown", ([5], 0))
("max_profit_cooldown", ([7, 6, 4, 3, 1], 0))
("max_profit_cooldown", ([1, 3, 2, 8, 4, 9], 2))
("max_profit_cooldown", ([1, 2, 3, 4, 5], 1))
("decode_ways", ("",))
("decode_ways", ("0",))
("decode_ways", ("06",))
("decode_ways", ("10",))
("decode_ways", ("2101",))
("decode_ways", ("27",))
("count_word_breaks", ("", ["a"]))
("count_word_breaks", ("aaaa", ["a", "aa"]))
("count_word_breaks", ("abc", ["ab"]))
("lis_length", ([], True))
("lis_length", ([2, 2, 2], True))
("lis_length", ([2, 2, 2], False))
("lis_length", ([3, 1, 2, 1, 2, 3], False))
---
max_profit_cooldown -> 0
max_profit_cooldown -> 0
max_profit_cooldown -> 0
max_profit_cooldown -> 6
max_profit_cooldown -> 3
decode_ways -> 1
decode_ways -> 0
decode_ways -> 0
decode_ways -> 1
decode_ways -> 1
decode_ways -> 1
count_word_breaks -> 1
count_word_breaks -> 5
count_word_breaks -> 0
lis_length -> 0
lis_length -> 1
lis_length -> 3
lis_length -> 4
=== hidden
gen max_profit_cooldown 1 200000
gen decode_ways 2 200000
---
max_profit_cooldown 200000 263300855 260961457
decode_ways 200000 104193594 15209354 0
=== hidden
gen count_word_breaks 3 100000
gen lis_length 4 200000
---
count_word_breaks 100000 972019552
lis_length 200000 870 872 126606 200000

## Hints
- **Stocks**: three states per day: `hold` (own a share), `sold` (just sold today), `rest` (no share, free to buy). `hold' = max(hold, rest − p)`, `sold' = hold + p − fee`, `rest' = max(rest, sold)`. Update them from the previous day's values simultaneously.
- **Decodings**: `dp[i] = dp[i−1]` (if s[i−1] ≠ '0') `+ dp[i−2]` (if s[i−2:i] is between 10 and 26). Keep two variables.
- **Word breaks**: `ways[i] = Σ ways[i − len(w)]` over words w that end at i. Group the words by length and slice `s[i-L:i]` for each length.
- **LIS**: patience sorting with `bisect_left` (strict) or `bisect_right` (non-decreasing).

## Solution
```python
from bisect import bisect_left, bisect_right

MOD = 1_000_000_007

def max_profit_cooldown(prices, fee):
    hold, sold, rest = float("-inf"), float("-inf"), 0
    for p in prices:
        hold, sold, rest = max(hold, rest - p), hold + p - fee, max(rest, sold)
    return max(sold, rest, 0)

def decode_ways(s):
    if not s:
        return 1
    prev2, prev1 = 1, 0 if s[0] == "0" else 1           # dp[i-2], dp[i-1]
    for i in range(2, len(s) + 1):
        cur = prev1 if s[i - 1] != "0" else 0
        two = s[i - 2:i]
        if "10" <= two <= "26":
            cur += prev2
        prev2, prev1 = prev1, cur % MOD
    return prev1

def count_word_breaks(s, words):
    by_len = {}
    for w in set(words):
        by_len.setdefault(len(w), set()).add(w)
    ways = [1] + [0] * len(s)
    for i in range(1, len(s) + 1):
        total = 0
        for L, ws in by_len.items():
            if L <= i and s[i - L:i] in ws:
                total += ways[i - L]
        ways[i] = total % MOD
    return ways[len(s)]

def lis_length(a, strict):
    tails = []
    find = bisect_left if strict else bisect_right
    for x in a:
        i = find(tails, x)
        if i == len(tails):
            tails.append(x)
        else:
            tails[i] = x
    return len(tails)
```

- **The stock problem** is a *state machine DP*. Instead of an index into the past, the state is "what am I holding, and may I buy?". The cooldown appears as the extra `sold` state, which may only flow into `rest` the next day. Updating all three from the previous day's tuple prevents using today's sale to buy today.
- **Decodings** read the last one or two characters. Comparing two-character strings lexicographically (`"10" <= two <= "26"`) is a neat way to check the range without converting.
- **Word breaks** count paths in a DAG whose vertices are the string positions. Grouping the dictionary by length bounds the work per position by the number of distinct lengths.
- **LIS** with `bisect_left` keeps tails strictly increasing. `bisect_right` lets equal values extend a run, which gives the non-decreasing version.
