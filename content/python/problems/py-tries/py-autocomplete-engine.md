---
id: py-autocomplete-engine
title: Weighted Autocomplete Engine and Max XOR
difficulty: Hard
order: 1
tags: trie, autocomplete, top-k, binary trie, XOR
time_limit: 6
---
## Statement
Build the autocomplete engine for a robot's voice-command console, plus a binary-trie utility.

```python
class Autocomplete:
    def add(self, word, weight):      # insert or update a command (a new weight REPLACES the old one)
    def remove(self, word) -> bool:   # delete a command; False if absent
    def count(self, prefix) -> int:   # number of stored commands starting with prefix
    def top(self, prefix, k) -> list: # up to k commands with this prefix, by (-weight, word)

def max_xor(nums):
    """Maximum a ^ b over pairs from nums (len >= 1; a single element gives 0). Non-negative ints < 2**31."""
```

The workload has 60 000 operations. `count` must be O(|prefix|), using per-node counters. `top` may traverse the prefix's subtree, but the tests keep those subtrees moderate. Keeping a cached per-node top list is a fine optimisation too.

## Starter
```python
class Autocomplete:
    def __init__(self):
        self.words = {}
    def add(self, word, weight):
        self.words[word] = weight
    def remove(self, word):
        return self.words.pop(word, None) is not None
    def count(self, prefix):
        return sum(1 for w in self.words if w.startswith(prefix))
    def top(self, prefix, k):
        return sorted((w for w in self.words if w.startswith(prefix)), key=lambda w: (-self.words[w], w))[:k]

def max_xor(nums):
    return max(a ^ b for a in nums for b in nums)
```

## Driver
```python
import random
import sys

def script(lines):
    ac = Autocomplete()
    for line in lines:
        p = line.split()
        if p[0] == "add":
            ac.add(p[1], int(p[2]))
        elif p[0] == "remove":
            print("remove", p[1], ac.remove(p[1]))
        elif p[0] == "count":
            pre = p[1] if len(p) > 1 else ""
            print("count", repr(pre), ac.count(pre))
        elif p[0] == "top":
            pre = p[1] if len(p) > 2 else ""
            print("top", repr(pre), ac.top(pre, int(p[-1])))
        elif p[0] == "xor":
            print("max_xor", max_xor([int(x) for x in p[1:]]))

def workload(seed, n):
    rng = random.Random(seed)
    ac = Autocomplete()
    syll = ["mo", "ve", "ar", "gr", "ip", "st", "op", "ro", "ta", "te"]
    acc = 0
    words = []
    for i in range(n):
        r = rng.random()
        if r < 0.5 or not words:
            w = "".join(rng.choice(syll) for _ in range(rng.randrange(2, 6)))
            ac.add(w, rng.randrange(1000)); words.append(w)
        elif r < 0.6:
            acc += ac.remove(rng.choice(words))
        elif r < 0.8:
            pre = "".join(rng.choice(syll) for _ in range(rng.randrange(1, 3)))
            acc += ac.count(pre)
        else:
            pre = "".join(rng.choice(syll) for _ in range(rng.randrange(2, 4)))
            res = ac.top(pre, 3)
            acc += len(res) + sum(len(x) for x in res)
    print("workload", n, acc, ac.count(""), ac.top("mo", 3))
    nums = [rng.randrange(2**31) for _ in range(80000)]
    print("max_xor big", max_xor(nums))

data = [l for l in sys.stdin.read().splitlines() if l.strip()]
if data and data[0].startswith("workload"):
    _, s, n = data[0].split()
    workload(int(s), int(n))
else:
    script(data)
```

## Tests
=== sample
add move 5
add moveto 9
add mode 5
add stop 7
top mo 2
count mo
count st
remove mode
count mo
xor 3 10 5 25 2 8
---
top 'mo' ['moveto', 'mode']
count 'mo' 3
count 'st' 1
remove mode True
count 'mo' 2
max_xor 28
=== hidden
count
top x 3
add a 1
add a 9
count a
top 3
add ab 9
add abc 9
top a 5
remove a
remove a
count a
top a 1
top ab 10
xor 7
xor 0 0
xor 1 2 4 8
---
count '' 0
top 'x' []
count 'a' 1
top '' ['a']
top 'a' ['a', 'ab', 'abc']
remove a True
remove a False
count 'a' 2
top 'a' ['ab']
top 'ab' ['ab', 'abc']
max_xor 0
max_xor 0
max_xor 12
=== hidden
workload 5 60000
---
workload 60000 4571211 11419 ['mostgrstte', 'motegrveip', 'mostarro']
max_xor big 2147483647

## Hints
- Node: `children` dict, `count` (words in this subtree) and `weight` (`None` if no word ends here). On `add` of a new word, increment `count` along the path; for an existing word, just update the weight. On `remove`, decrement along the path and prune nodes whose count drops to 0.
- `top`: walk to the prefix node, then collect `(-weight, word)` pairs from its subtree with an explicit stack, and use `heapq.nsmallest(k, ...)`.
- `max_xor`: insert numbers bit by bit (bit 30 down to 0); for each number, walk preferring the opposite bit. Use nested lists `[child0, child1]` for speed.

## Solution
```python
import heapq

class _Node:
    __slots__ = ("children", "count", "weight")
    def __init__(self):
        self.children = {}
        self.count = 0
        self.weight = None

class Autocomplete:
    def __init__(self):
        self.root = _Node()

    def _find(self, s):
        node = self.root
        for ch in s:
            node = node.children.get(ch)
            if node is None:
                return None
        return node

    def add(self, word, weight):
        end = self._find(word)
        if end is not None and end.weight is not None:
            end.weight = weight                    # update: the counts don't change
            return
        node = self.root
        node.count += 1
        for ch in word:
            node = node.children.setdefault(ch, _Node())
            node.count += 1
        node.weight = weight

    def remove(self, word):
        end = self._find(word)
        if end is None or end.weight is None:
            return False
        node = self.root
        node.count -= 1
        for ch in word:
            child = node.children[ch]
            child.count -= 1
            if child.count == 0:
                del node.children[ch]              # prune the empty branch
                return True
            node = child
        node.weight = None
        return True

    def count(self, prefix):
        node = self._find(prefix)
        return node.count if node else 0

    def top(self, prefix, k):
        node = self._find(prefix)
        if node is None or k <= 0:
            return []
        found, stack = [], [(node, prefix)]
        while stack:
            n, s = stack.pop()
            if n.weight is not None:
                found.append((-n.weight, s))
            for ch, child in n.children.items():
                stack.append((child, s + ch))
        return [w for _, w in heapq.nsmallest(k, found)]

def max_xor(nums):
    root = [None, None]
    best = 0
    for x in nums:
        node = root                                 # insert
        for b in range(30, -1, -1):
            bit = x >> b & 1
            if node[bit] is None:
                node[bit] = [None, None]
            node = node[bit]
        node, cur = root, 0                         # query the best partner seen so far (including x itself)
        for b in range(30, -1, -1):
            want = 1 - (x >> b & 1)
            if node[want] is not None:
                cur |= 1 << b
                node = node[want]
            else:
                node = node[1 - want]
        best = max(best, cur)
    return best
```

- **Per-node counters** make `count(prefix)` a walk of |prefix| steps. They also make deletion clean: when a child's count reaches zero, the whole branch below it is dead and is removed in one step.
- **Updates versus inserts** must be distinguished, or counts drift: re-adding an existing word only changes its weight.
- `top` collects the subtree's words and uses `heapq.nsmallest` with `(-weight, word)` keys, which encodes "highest weight first, alphabetical on ties". Production systems cache the top-k at every node, so a query never has to traverse the subtree.
- **The binary trie** answers "best XOR partner" in 31 steps by greedily making the highest bits differ, so 200 000 numbers cost about 12 million steps, versus 2·10¹⁰ pairs.
