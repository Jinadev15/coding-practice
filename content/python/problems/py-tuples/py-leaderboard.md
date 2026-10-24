---
id: py-leaderboard
title: Leaderboard Sort
difficulty: Medium
order: 3
tags: tuples, multi-key sort, lambda
---
## Statement
Each of `n` lines has a player: `name score time` (score and time are integers; time is in seconds).

Rank them: **higher score first**; on equal score, **lower time first**; then **name alphabetically**. Print the ranking as `rank. name score time`.

Players with equal score, time **and** name don't occur.

## Starter
```python
n = int(input())
players = []
for _ in range(n):
    name, score, time = input().split()
    players.append((name, int(score), int(time)))
```

## Tests
=== sample
4
ada 90 300
bob 95 500
cy 90 250
dee 90 250
---
1. bob 95 500
2. cy 90 250
3. dee 90 250
4. ada 90 300
=== hidden
1
solo 0 0
---
1. solo 0 0
=== hidden
3
zed -5 10
amy -5 10
kim 0 999
---
1. kim 0 999
2. amy -5 10
3. zed -5 10

## Hints
- A tuple key sorts lexicographically. Negate the field you want descending: `key=lambda p: (-p[1], p[2], p[0])`.
- `enumerate(..., start=1)` gives the ranks.

## Solution
A tuple sort key encodes all three rules at once: negating the score makes it descending, while time and name stay ascending.

```python
n = int(input())
players = []
for _ in range(n):
    name, score, time = input().split()
    players.append((name, int(score), int(time)))
players.sort(key=lambda p: (-p[1], p[2], p[0]))
for rank, (name, score, time) in enumerate(players, start=1):
    print(f"{rank}. {name} {score} {time}")
```

Negation works for numbers only. To sort *strings* descending as a secondary key, use two stable sorts instead (the Sorting lesson explains this).
