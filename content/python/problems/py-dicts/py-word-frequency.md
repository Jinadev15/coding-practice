---
id: py-word-frequency
title: Word Frequency Report
difficulty: Medium
order: 4
tags: counting, sorting dict items, text processing
---
## Statement
Read a text of several lines (until the end of input). Words are maximal runs of **letters**; everything else separates words. Comparison is **case-insensitive** (count `The` and `the` as `the`).

Print the `k` most frequent words, where `k` is given on the first line, as `word count`, sorted by **count descending** and then **alphabetically**. If there are fewer than `k` distinct words, print them all.

## Starter
```python
import sys
k = int(sys.stdin.readline())
text = sys.stdin.read()
```

## Tests
=== sample
3
The cat and the hat.
The bat, and THE rat!
---
the 4
and 2
bat 1
=== hidden
10
one
---
one 1
=== hidden
2
Don't stop; don't-stop!! Stop?
---
stop 3
don 2
=== hidden
1
123 456 !!!
---
=== hidden
2
b a c b a c
---
a 2
b 2

## Hints
- Build words character by character: extend the current word while `ch.isalpha()`, and finish it otherwise. (Regular expressions make this a one-liner later: `re.findall(r"[a-z]+", text.lower())`.)
- Count with a dict, then sort `items()` with `key=lambda kv: (-kv[1], kv[0])`.

## Solution
Tokenise by scanning characters (letters extend the current word; anything else ends it), count in a dict, then sort with a two-part key.

```python
import sys
k = int(sys.stdin.readline())
text = sys.stdin.read().lower()

counts = {}
word = []
for ch in text + " ":          # the sentinel space flushes the last word
    if ch.isalpha():
        word.append(ch)
    elif word:
        w = "".join(word)
        counts[w] = counts.get(w, 0) + 1
        word = []

ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
for w, c in ranked[:k]:
    print(w, c)
```

The trailing **sentinel** character guarantees the final word is counted without duplicating the flush logic after the loop. That's a common trick in parsing loops. In `Don't`, the apostrophe splits the text into `don` and `t`. Defining "word" precisely is the real difficulty of text processing.
