---
id: cpp-st-undo-editor
title: Text Editor with Undo and Redo
difficulty: Medium
order: 8
tags: stack, undo/redo, command pattern, design
time_limit: 1
---
## Statement
```cpp
class Editor {
public:
    void type(const std::string& w);   // append w at the end of the text
    void del(int k);                   // delete the last min(k, length) characters
    void undo();                       // revert the most recent type/del not yet undone (no-op if none)
    void redo();                       // re-apply the most recently undone edit (no-op if none)
    int length() const;
    char at(int i) const;              // 0-based; precondition 0 <= i < length()
};
```

A new `type` or `del` **clears** the redo history (as in every real editor). `undo` and `redo` themselves are not edits: undoing twice reverts two edits, and `redo` after `undo` restores the text exactly. A `del` that removes 0 characters (empty text, or k = 0) still counts as an edit.

**Input:** `q`, then `q` commands: `type w` (w is 1..20 lowercase letters), `del k` (0 ≤ k ≤ 10⁹), `undo`, `redo`, `len` (print the length), `at i` (print the character at i, or `-` if i is out of range). q ≤ 3·10⁵.

Each command must cost time proportional to the characters it changes, not to the length of the text.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

class Editor {
    string text;
    vector<string> past, future;              // whole-text snapshots: O(length) per edit
public:
    void type(const string& w) { past.push_back(text); future.clear(); text += w; }
    void del(int k) { past.push_back(text); future.clear(); text.resize(text.size() - min<size_t>(k, text.size())); }
    void undo() { if (past.empty()) return; future.push_back(text); text = past.back(); past.pop_back(); }
    void redo() { if (future.empty()) return; past.push_back(text); text = future.back(); future.pop_back(); }
    int length() const { return text.size(); }
    char at(int i) const { return text[i]; }
};
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int q; cin >> q;
    Editor ed;
    string cmd, w;
    while (q-- && cin >> cmd) {
        if (cmd == "type") { cin >> w; ed.type(w); }
        else if (cmd == "del") { long long k; cin >> k; ed.del((int)min<long long>(k, INT_MAX)); }
        else if (cmd == "undo") ed.undo();
        else if (cmd == "redo") ed.redo();
        else if (cmd == "len") cout << ed.length() << '\n';
        else { long long i; cin >> i; cout << (i >= 0 && i < ed.length() ? ed.at((int)i) : '-') << '\n'; }
    }
}
```

## Tests
=== sample
11
type hello
type world
del 3
len
undo
at 9
undo
redo
len
redo
at 7
---
7
d
10
-
=== hidden
7
undo
redo
del 5
type ab
undo
undo
len
---
0
=== hidden
9
type abc
del 100
len
undo
at 2
type x
redo
len
at 3
---
0
c
4
x
=== hidden
11
redo
type ca
type bb
at 9
del 2
at 9
undo
at 0
type accb
type a
type bbc
---
-
-
c
=== hidden
38
type cc
del 4
type bc
undo
undo
undo
type b
del 4
undo
redo
undo
len
del 1
at 11
at 10
del 3
type ccbb
undo
type acc
undo
type abc
type abca
at 3
del 1
at 8
undo
type cbbc
undo
redo
undo
undo
redo
del 0
type bbcb
del 1
type c
type abaa
type aa
---
1
-
-
a
-
=== hidden
1
undo
---

=== hidden
@gen 3887854331 big
=== hidden
@gen 3887854332 big
=== hidden
@gen 3887854333 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
q = r.randint(1, 40) if not big else 300000
print(q)
L = 0
for i in range(q):
    x = r.random()
    if big and i < q // 3:
        w = "".join(r.choice("abcdefghij") for _ in range(20)); print("type", w); L += 20; continue
    if x < 0.3:
        w = "".join(r.choice("abc") for _ in range(r.randint(1, 4 if not big else 20))); print("type", w)
    elif x < 0.45: print("del", r.randint(0, 6) if not big else r.choice([r.randint(0, 30), 10**9]))
    elif x < 0.65: print("undo")
    elif x < 0.8: print("redo")
    elif x < 0.88: print("len")
    else: print("at", r.randint(-1, 12) if not big else r.randint(0, 2000000))
```

## Hints
- Undo reverts the most recent edit first, and redo replays the most recently undone one. That's two stacks.
- Store each edit as a delta (what was typed, or exactly which characters were deleted), not a copy of the whole text.
- A new edit must clear the redo stack. A `del` may remove fewer than `k` characters; store what it really removed.

## Solution
This is the **command pattern** with two stacks. Each edit is stored as a small object that knows how to do itself and how to undo itself:

- `type w` stores `w`; undoing it removes `|w|` characters from the end.
- `del k` stores the characters it actually removed (maybe fewer than `k`); undoing it appends them back.

`undo` pops from the undo stack, reverts the edit and pushes it on the redo stack; `redo` does the mirror image. Any new edit clears the redo stack, because the "future" it described no longer follows from the current text.

Why stacks? Undo always reverts the **most recent** remaining edit (LIFO), and redo always replays the most recently undone one (LIFO again).

The snapshot approach (the starter) is correct but copies the entire text on every edit: O(q · length), which is 10¹⁰ character copies on the big tests. Storing the *delta* makes each command proportional to the characters it changes: O(total characters typed or deleted), amortized over the operations.

`clear()` on the redo stack looks expensive, but every element it destroys was created by an earlier edit, so it is paid for in advance.

```cpp
#include <bits/stdc++.h>
using namespace std;

class Editor {
    struct Edit { bool is_type; string chars; };   // what was typed, or what was deleted
    string text;
    vector<Edit> undo_st, redo_st;
    void apply(const Edit& e) {                     // do the edit forwards
        if (e.is_type) text += e.chars;
        else text.resize(text.size() - e.chars.size());
    }
    void revert(const Edit& e) {                    // do the edit backwards
        if (e.is_type) text.resize(text.size() - e.chars.size());
        else text += e.chars;
    }
public:
    void type(const string& w) {
        Edit e{true, w}; apply(e);
        undo_st.push_back(std::move(e)); redo_st.clear();
    }
    void del(int k) {
        size_t n = min<size_t>(k, text.size());
        Edit e{false, text.substr(text.size() - n)};   // remember exactly what disappears
        apply(e);
        undo_st.push_back(std::move(e)); redo_st.clear();
    }
    void undo() {
        if (undo_st.empty()) return;
        revert(undo_st.back());
        redo_st.push_back(std::move(undo_st.back())); undo_st.pop_back();
    }
    void redo() {
        if (redo_st.empty()) return;
        apply(redo_st.back());
        undo_st.push_back(std::move(redo_st.back())); redo_st.pop_back();
    }
    int length() const { return text.size(); }
    char at(int i) const { return text[i]; }
};
```
