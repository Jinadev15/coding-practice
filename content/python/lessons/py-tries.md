# Tries

A **trie** (prefix tree) stores strings by their characters along root-to-node paths. Every node represents a prefix, and a flag marks the nodes where a stored word ends. Inserting or looking up a word of length L takes O(L), independent of how many words are stored, and tries answer **prefix questions** that hash sets can't: autocomplete, "how many words start with …", longest common prefix, and searching a grid for many words at once. With bits instead of characters, a binary trie solves maximum-XOR problems in O(32) per query.

## 1. A dict-based trie

```python
class Trie:
    __slots__ = ("root",)
    END = "$"                                   # a sentinel key marking the end of a word

    def __init__(self):
        self.root = {}

    def insert(self, word):
        node = self.root
        for ch in word:
            node = node.setdefault(ch, {})
        node[self.END] = True

    def _walk(self, prefix):
        node = self.root
        for ch in prefix:
            node = node.get(ch)
            if node is None:
                return None
        return node

    def search(self, word):
        node = self._walk(word)
        return node is not None and self.END in node

    def starts_with(self, prefix):
        return self._walk(prefix) is not None
```

A node class with `children` and `is_end` fields (plus `__slots__`) is clearer and supports extra per-node data:

```python
class Node:
    __slots__ = ("children", "is_end", "count")
    def __init__(self):
        self.children = {}
        self.is_end = False
        self.count = 0                          # words passing through this node (prefix counts)
```

| Operation | Trie | Hash set |
|---|---|---|
| insert/lookup a word of length L | O(L) | O(L) to hash |
| prefix exists? | O(L) | O(n·L) scan |
| all words with a prefix | O(L + output) | O(n·L) |
| sorted iteration | DFS in character order | sort needed |
| memory | high (a node per prefix) | lower |

## 2. Prefix counting and autocomplete

Store `count` on each node, incremented during insert, so "how many words start with p?" is O(|p|). For **autocomplete**, walk to the prefix node, then DFS (or keep the top-k suggestions per node, ranked by frequency) to list completions.

```python
def complete(trie_root, prefix, limit=5):
    node = trie_root
    for ch in prefix:
        if ch not in node:
            return []
        node = node[ch]
    out = []
    def dfs(n, path):
        if len(out) >= limit:
            return
        if "$" in n:
            out.append(prefix + path)
        for ch in sorted(k for k in n if k != "$"):
            dfs(n[ch], path + ch)
    dfs(node, "")
    return out
```

## 3. Word search II: a trie plus backtracking

Find every dictionary word in a letter grid. Running a separate DFS per word costs O(words × cells × 4^L). With all the words in one trie, a **single** backtracking pass from each cell follows trie edges and stops as soon as the current path isn't a prefix of any word:

```python
def find_words(board, words):
    root = {}
    for w in words:
        node = root
        for ch in w:
            node = node.setdefault(ch, {})
        node["$"] = w                                   # store the word itself at its end node
    R, C, found = len(board), len(board[0]), []

    def dfs(r, c, parent):
        ch = board[r][c]
        node = parent[ch]
        if "$" in node:
            found.append(node.pop("$"))                 # report once
        board[r][c] = "#"
        for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if 0 <= nr < R and 0 <= nc < C and board[nr][nc] in node:
                dfs(nr, nc, node)
        board[r][c] = ch
        if not node:
            parent.pop(ch)                              # prune exhausted branches

    for r in range(R):
        for c in range(C):
            if board[r][c] in root:
                dfs(r, c, root)
    return sorted(found)
```

Removing exhausted branches makes later searches faster and faster. This is the standard solution in interviews.

## 4. Wildcards

`search("b.d")`, where `.` matches any letter: at a `.`, branch into every child. Worst case O(26^k · L) for k wildcards, but fast in practice. The same structure answers "words within edit distance 1" by allowing one substitution while walking.

## 5. Binary trie: maximum XOR

Insert numbers bit by bit from the most significant bit. To maximise `x ^ y` over stored y, walk down preferring the **opposite** bit at each level:

```python
def max_xor_pair(nums, bits=31):
    root = {}
    best = 0
    for x in nums:
        node = root                          # insert x
        for b in range(bits, -1, -1):
            node = node.setdefault(x >> b & 1, {})
        node, cur = root, 0                  # query the best partner for x
        for b in range(bits, -1, -1):
            want = 1 - (x >> b & 1)
            if want in node:
                cur |= 1 << b
                node = node[want]
            else:
                node = node[1 - want]
        best = max(best, cur)
    return best

max_xor_pair([3, 10, 5, 25, 2, 8])   # 28  (5 ^ 25)
```

Each query is O(bits), so n queries cost O(n · 32). Variants include the maximum XOR subarray (insert prefix XORs) and offline queries "max XOR with elements ≤ m" (sort queries and insert progressively).

## 6. Compressed tries and alternatives

- A **radix tree** (Patricia trie) merges single-child chains into string-labelled edges. It saves memory, and it's used in IP routing tables (longest-prefix match), the Linux kernel, and HTTP routers.
- **Aho–Corasick** adds failure links to a trie to match many patterns in one pass over a text (String Algorithms lesson).
- **Suffix tries/trees/arrays** index all suffixes of one text for substring queries.
- For pure membership tests, a hash set is simpler and lighter. Use a trie when you need prefixes or order.

## 7. Exam-ready answers

> [!EXAM]
> **Tries.** A trie is a rooted tree for storing a set of strings in which each edge is labelled with a character and each node represents the prefix spelled by the path from the root; nodes at which stored strings end are marked. Insertion, exact lookup and prefix queries take O(L) time for a key of length L, independent of the number of stored keys, and a depth-first traversal enumerates keys in lexicographic order. Tries support autocomplete, prefix counting, longest-prefix matching and simultaneous multi-pattern search, at the cost of higher memory use than hash tables, which compressed (radix) tries reduce.

## 8. Cheat sheet

| Need | Trie technique |
|---|---|
| exact/prefix lookup | walk the characters |
| count words with a prefix | per-node counter |
| autocomplete | walk + DFS / per-node top-k |
| many words in a grid | trie + backtracking + pruning |
| `.` wildcards | branch at wildcard positions |
| max XOR | binary trie, prefer the opposite bit |
| longest-prefix match (routing) | radix trie |

> [!INTERVIEW]
> **"Design autocomplete for a search box."** Use a trie of the queries, with a frequency on each terminal node, and cache the top-k completions at each node (updated on insert), so a lookup is O(|prefix| + k). For scale: shard by prefix, keep it in memory, rebuild periodically from logs, and add fuzzy matching (edit distance ≤ 1) by allowing limited branching. Mention a radix trie to save memory, and a ternary search tree as an alternative.
