---
id: py-inverted-index
title: Inverted Index
difficulty: Medium
order: 3
tags: dict comprehension, sets, search engines
---
## Statement
Search engines use an **inverted index**, which maps each word to the documents containing it. Given `n` documents (one per line, numbered from 1), build the index (lowercase; words are split on whitespace with the punctuation `.,!?;:` stripped from both ends).

Then answer `q` queries. Each query has one or more words, and you must print the sorted document numbers containing **all** of the query words (`none` if there are none).

## Starter
```python
n = int(input())
docs = [input() for _ in range(n)]
q = int(input())
queries = [input().lower().split() for _ in range(q)]
```

## Tests
=== sample
3
The cat sat.
The dog sat on the cat!
A bird.
3
cat
the sat
bird cat
---
1 2
1 2
none
=== hidden
2
Hello, hello world
WORLD peace
3
world
hello
peace hello
---
1 2
1
none
=== hidden
1
x
1
y
---
none

## Hints
- First a list of word **sets**: `[{w.strip(".,!?;:") for w in d.lower().split()} for d in docs]`.
- Index: a dict from word to a set of document numbers. Build it with a loop, or a dict comprehension over the vocabulary.
- AND query: intersect the sets of all query words; a missing word gives the empty set.

## Solution
Normalise each document into a set of words, build word → set-of-doc-ids, then answer each AND query with set intersection.

```python
n = int(input())
docs = [input() for _ in range(n)]
q = int(input())
queries = [input().lower().split() for _ in range(q)]

words_per_doc = [{w.strip(".,!?;:") for w in d.lower().split()} for d in docs]
vocab = set().union(*words_per_doc)
index = {w: {i for i, ws in enumerate(words_per_doc, 1) if w in ws} for w in vocab}

for words in queries:
    result = set.intersection(*(index.get(w, set()) for w in words))
    print(*sorted(result) if result else ["none"])
```

`set.intersection(*sets)` intersects any number of sets at once. Real search engines store **sorted posting lists** and intersect them with a two-pointer merge, the same idea at disk scale. The dict comprehension here is O(|vocab| × n), which is fine for small inputs. A single loop that appends each `(word, doc)` pair is O(total words) and scales better.
