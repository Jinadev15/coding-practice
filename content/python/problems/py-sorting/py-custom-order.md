---
id: py-custom-order
title: Custom Alphabet Order
difficulty: Easy
order: 4
tags: sorting, key function, lookup tables
---
## Statement
An alien language uses the 26 lowercase English letters in a different order. Given that order (one line of 26 letters) and `n` words, print the words sorted **lexicographically by the alien alphabet**, one per line.

As in the usual dictionary order, a word that is a prefix of another comes first.

## Starter
```python
order = input().strip()
n = int(input())
words = [input().strip() for _ in range(n)]
```

## Tests
=== sample
hlabcdefgijkmnopqrstuvwxyz
3
hello
leetcode
apple
---
hello
leetcode
apple
=== hidden
zyxwvutsrqponmlkjihgfedcba
4
apple
app
zoo
b
---
zoo
b
app
apple
=== hidden
abcdefghijklmnopqrstuvwxyz
3
banana
apple
cherry
---
apple
banana
cherry

## Hints
- Build a rank table: `rank = {ch: i for i, ch in enumerate(order)}`.
- Sort with `key=lambda w: [rank[c] for c in w]`. Lists compare lexicographically, and a shorter prefix sorts first automatically.

## Solution
Map each word to the list of its letters' ranks in the alien alphabet. Python compares lists lexicographically, which is exactly dictionary order, including "a prefix comes first".

```python
order = input().strip()
n = int(input())
words = [input().strip() for _ in range(n)]
rank = {ch: i for i, ch in enumerate(order)}
for w in sorted(words, key=lambda w: [rank[c] for c in w]):
    print(w)
```

An alternative builds a translation table, `str.maketrans(order, "abcdefghijklmnopqrstuvwxyz")`, and sorts by `w.translate(table)`. LeetCode 953 asks the reverse question (is this list already sorted?), and LeetCode 269 asks you to *infer* the alphabet from sorted words using topological sort.
