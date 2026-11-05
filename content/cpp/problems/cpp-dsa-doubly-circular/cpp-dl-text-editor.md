---
id: cpp-dl-text-editor
title: A Text Editor with a Cursor
difficulty: Hard
order: 4
tags: doubly linked list, cursor, sentinel, design
time_limit: 2
---
## Statement
Implement a text buffer with a cursor that sits **between** characters:

```cpp
class TextEditor {
public:
    ~TextEditor();
    void add_text(const std::string& text);   // insert at the cursor; the cursor ends after the inserted text
    int delete_text(int k);                   // delete up to k chars LEFT of the cursor; return how many were deleted
    std::string cursor_left(int k);           // move left up to k; return the (up to) 10 chars left of the cursor
    std::string cursor_right(int k);          // move right up to k; return the (up to) 10 chars left of the cursor
};
```

Use a doubly linked list of characters with a sentinel. The cursor is a pointer to the node **immediately left of the cursor** (the sentinel when the cursor is at the start). Inserting and deleting at the cursor are then O(1) per character. With a `std::string`, each operation in the middle would be O(n).

**Input:** commands `add text`, `del k`, `left k`, `right k` (up to 10⁵ commands, total characters and steps ≤ 2·10⁶). Print each command's return value (`#` marks an empty string).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

class TextEditor {
    string s; size_t cur = 0;
public:
    void add_text(const string& t) { s += t; cur = s.size(); }      // always appends at the end
    int delete_text(int k) { return 0; }
    string cursor_left(int k) { return ""; }
    string cursor_right(int k) { return ""; }
};
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    TextEditor e; string c; unsigned long long h = 0; int shown = 0;
    while (cin >> c) {
        string out;
        if (c == "add") { string t; cin >> t; e.add_text(t); continue; }
        int k; cin >> k;
        if (c == "del") out = to_string(e.delete_text(k));
        else out = c == "left" ? e.cursor_left(k) : e.cursor_right(k);
        if (out.empty()) out = "#";
        if (shown++ < 25) cout << out << ' ';
        for (char ch : out) h = h * 131 + (unsigned char)ch;
        h = h * 7 + 1;
    }
    cout << "| " << h << '\n';
}
```

## Tests
=== sample
add leetcode
del 4
add practice
right 3
left 8
del 10
left 2
right 6
---
4 etpractice leet 4 # practi | 3008300727521114094
=== hidden
del 5
left 1
right 1
add a
left 1
add bc
right 9
del 1
---
0 # # # bca 1 | 8194831319632612936
=== hidden
add xyac
left 5
add zaccc
right 4
add acy
left 5
del 2
add z
left 6
right 3
right 2
add zyzzy
left 2
del 4
add b
right 5
add ay
del 4
left 1
left 3
add cxba
left 2
add yabba
right 1
add xxz
---
# zacccxyac zacccxy 2 # zac zaccc zaccczyz 4 zaccbzyzac 4 zaccbzy zacc zacccx cccxyabbab | 14430046914286731613
=== hidden
del 2
del 2
left 4
add b
add c
add zbc
del 3
add xccay
add zzaa
right 3
left 1
del 2
add acca
del 2
add yaac
left 1
del 2
left 6
right 1
add xc
left 2
left 4
del 2
add z
add c
---
0 0 # 3 cxccayzzaa bcxccayzza 2 2 ccayzacyaa 2 bcxcc bcxcca bcxcca bc 2 | 1200841914073706189
=== hidden
add xaz
add zcz
add b
left 6
add zaa
right 4
add bxbc
left 5
right 3
right 2
del 3
add xzycb
right 6
right 3
del 3
add aa
left 4
add xxxcx
add zzyx
add zcb
del 3
del 3
add zcaxb
right 4
right 5
---
x xzaaazzc xzaaazz xzaaazzcbx aaazzcbxbc 3 zcbxzycbzb zcbxzycbzb 3 zaaazzcbxz 3 3 zzcaxbycaa zzcaxbycaa | 15604971299840870846
=== hidden
@gen 2758717489 big
=== hidden
@gen 2758717490 big
=== hidden
@gen 2758717491 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
out = []
for _ in range(25 if not big else 100000):
    c = r.random()
    if c < 0.35: out.append("add " + "".join(r.choice("abcxyz") for _ in range(r.randint(1, 5 if not big else 15))))
    elif c < 0.55: out.append(f"del {r.randint(1, 4 if not big else 15)}")
    elif c < 0.78: out.append(f"left {r.randint(1, 6 if not big else 15)}")
    else: out.append(f"right {r.randint(1, 6 if not big else 15)}")
print("\n".join(out))
```

## Hints
- Let the cursor be a pointer to the character node just LEFT of it, with the sentinel meaning "at the start".
- Typing links a new node after the cursor node and moves the cursor onto it. Backspace unlinks the cursor node and moves the cursor to its prev.
- For the returned context, walk back up to 10 nodes from the cursor, then reverse the collected characters.

## Solution
**Representation:**

- A circular doubly linked list of characters with a sentinel.
- The cursor is the **node to its left**, or the sentinel at the very start of the text.

Choosing "the node left of the cursor" makes every operation local:

- **type:** link a new node after `cur_`, then advance `cur_` to it;
- **backspace:** unlink `cur_`, and the cursor becomes its `prev`;
- **move:** follow `prev`/`next` until the steps run out or you hit the sentinel.

Each character inserted or deleted costs O(1), and each move step costs O(1). The context string walks at most 10 nodes.

This is the essence of real editor data structures, such as **gap buffers** (two stacks of characters on either side of the cursor) and **ropes** (balanced trees of chunks). A gap buffer is an equally good solution here: two `std::string`s used as stacks.

Complexity: O(1) per character typed or deleted, O(1) per cursor step.

```cpp
#include <bits/stdc++.h>
using namespace std;

class TextEditor {
    struct C { char ch; C* prev; C* next; };
    C s_{0, &s_, &s_};          // sentinel: s_.next is the first char, s_.prev the last
    C* cur_ = &s_;              // node immediately LEFT of the cursor (sentinel = start of text)

    string left_context() const {
        string r;
        for (const C* p = cur_; p != &s_ && r.size() < 10; p = p->prev) r += p->ch;
        reverse(r.begin(), r.end());
        return r;
    }
public:
    TextEditor() = default;
    TextEditor(const TextEditor&) = delete;
    TextEditor& operator=(const TextEditor&) = delete;
    ~TextEditor() { C* c = s_.next; while (c != &s_) { C* n = c->next; delete c; c = n; } }

    void add_text(const string& t) {
        for (char ch : t) {
            C* x = new C{ch, cur_, cur_->next};    // link after the cursor node
            cur_->next->prev = x;
            cur_->next = x;
            cur_ = x;                              // the cursor moves past the new char
        }
    }
    int delete_text(int k) {
        int done = 0;
        while (done < k && cur_ != &s_) {
            C* x = cur_;
            cur_ = x->prev;
            x->prev->next = x->next;
            x->next->prev = x->prev;
            delete x;
            ++done;
        }
        return done;
    }
    string cursor_left(int k) {
        while (k-- > 0 && cur_ != &s_) cur_ = cur_->prev;
        return left_context();
    }
    string cursor_right(int k) {
        while (k-- > 0 && cur_->next != &s_) cur_ = cur_->next;
        return left_context();
    }
};
```
