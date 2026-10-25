---
id: py-grade-records
title: Grade Records
difficulty: Easy
order: 1
tags: starred unpacking, parsing
---
## Statement
Each of `n` lines has a student record: a name followed by **one or more** integer scores, separated by commas, e.g. `ada,90,85,77`.

For each student print `name avg best worst`, with the average to 1 decimal place. Then print the name of the student with the highest average (the earliest such student if there's a tie).

Use starred unpacking to separate the name from the scores.

## Starter
```python
n = int(input())
for _ in range(n):
    name, *scores = input().split(",")
```

## Tests
=== sample
3
ada,90,85,77
bob,60
cy,100,50
---
ada 84.0 90 77
bob 60.0 60 60
cy 75.0 100 50
ada
=== hidden
2
x,1,2
y,2,1
---
x 1.5 2 1
y 1.5 2 1
x
=== hidden
1
solo,0,0,0,100
---
solo 25.0 100 0
solo

## Hints
- Split each line on commas: `name, *scores = line.split(",")` puts the first field in `name` and the rest in a list.
- Convert the scores with `list(map(int, scores))`, then use `sum`, `len`, `max`, `min`.
- Track the best average as you go, replacing it only when the new average is strictly greater so the earliest student wins ties.

## Solution
`name, *scores = parts` handles any number of scores. A strict `>` comparison keeps the earliest student on ties.

```python
n = int(input())
best_name, best_avg = None, float("-inf")
for _ in range(n):
    name, *scores = input().split(",")
    scores = list(map(int, scores))
    avg = sum(scores) / len(scores)
    print(f"{name} {avg:.1f} {max(scores)} {min(scores)}")
    if avg > best_avg:
        best_name, best_avg = name, avg
print(best_name)
```

`float("-inf")` is a safe starting value for a running maximum: every real average beats it.
