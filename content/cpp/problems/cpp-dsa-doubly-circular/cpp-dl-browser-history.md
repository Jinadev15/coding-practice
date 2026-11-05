---
id: cpp-dl-browser-history
title: Browser History with Back and Forward
difficulty: Medium
order: 3
tags: doubly linked list, cursor, design
time_limit: 2
---
## Statement
Model a browser tab's history as a doubly linked list of pages with a **cursor** on the current page:

```cpp
class BrowserHistory {
public:
    explicit BrowserHistory(const std::string& homepage);
    ~BrowserHistory();
    void visit(const std::string& url);   // clear (and DELETE) all forward history, then add url after current and move to it
    std::string back(int steps);          // move back up to `steps` pages; return the current url
    std::string forward(int steps);       // move forward up to `steps` pages; return the current url
};
```

Visiting a new page **discards** the forward pages. Free those nodes right away. Moving past either end stops at the first or last page.

**Input:** the homepage, then commands `visit u`, `back k`, `fwd k` (up to 2·10⁵ commands; total steps ≤ 2·10⁷). Print the url after each back/fwd.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

class BrowserHistory {
    string cur;
public:
    explicit BrowserHistory(const string& home) : cur(home) {}
    void visit(const string& url) { cur = url; }
    string back(int) { return cur; }
    string forward(int) { return cur; }
};
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    string home; cin >> home;
    BrowserHistory b(home);
    string c; unsigned long long h = 0; int shown = 0;
    while (cin >> c) {
        if (c == "visit") { string u; cin >> u; b.visit(u); continue; }
        int k; cin >> k;
        string r = c == "back" ? b.back(k) : b.forward(k);
        if (shown++ < 25) cout << r << ' ';
        for (char ch : r) h = h * 131 + (unsigned char)ch;
    }
    cout << "| " << h << '\n';
}
```

## Tests
=== sample
leetcode.com
visit google.com
visit facebook.com
visit youtube.com
back 1
back 1
fwd 1
visit linkedin.com
fwd 2
back 2
back 7
---
facebook.com google.com facebook.com linkedin.com google.com leetcode.com | 11250965816169162595
=== hidden
home
back 1
fwd 1
visit a
visit b
back 1
visit c
fwd 5
back 100
---
home home a c home | 3440624730621323399
=== hidden
home
visit u27
fwd 1
visit u2
fwd 1
back 2
visit u39
visit u5
visit u2
fwd 3
fwd 2
visit u50
fwd 3
fwd 2
visit u48
visit u19
back 2
visit u7
visit u39
fwd 3
back 1
back 1
back 1
back 1
fwd 1
visit u12
fwd 3
visit u15
visit u5
visit u9
fwd 3
---
u27 u2 home u2 u2 u50 u50 u50 u39 u7 u50 u2 u5 u2 u12 u9 | 17708511928319874329
=== hidden
home
visit u3
visit u30
fwd 3
fwd 3
fwd 3
visit u47
visit u20
visit u37
fwd 2
visit u21
visit u24
back 3
back 1
visit u42
visit u36
visit u45
visit u12
fwd 3
fwd 3
fwd 3
fwd 2
visit u39
fwd 2
fwd 1
back 1
fwd 2
visit u41
visit u28
fwd 1
fwd 3
---
u30 u30 u30 u37 u20 u47 u12 u12 u12 u12 u39 u39 u12 u39 u28 u28 | 6858694758933862565
=== hidden
home
visit u23
back 2
visit u15
fwd 1
visit u30
fwd 2
visit u34
fwd 1
visit u14
fwd 1
back 3
visit u40
visit u14
fwd 1
visit u27
fwd 1
back 2
back 2
visit u44
fwd 2
back 3
fwd 1
visit u21
fwd 1
visit u4
fwd 1
back 1
visit u19
visit u38
visit u48
---
home u15 u30 u34 u14 u15 u14 u27 u40 home u44 home u44 u21 u4 u21 | 359277236714024757
=== hidden
@gen 1607717145 big
=== hidden
@gen 1607717146 big
=== hidden
@gen 1607717147 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
out = ["home"]
for i in range(30 if not big else 200000):
    c = r.random()
    if c < 0.4: out.append(f"visit u{r.randint(0, 50 if not big else 10**6)}")
    elif c < 0.7: out.append(f"back {r.randint(1, 3 if not big else 100)}")
    else: out.append(f"fwd {r.randint(1, 3 if not big else 100)}")
print("\n".join(out))
```

## Hints
- Keep a pointer to the current page. back and forward just move it along prev/next until the steps run out or you hit an end.
- visit: everything after the current page is discarded, so delete those nodes, then link the new page after the current one.
- The destructor frees the remaining chain starting from the first page.

## Solution
The history is a line of pages, and the **cursor** is the current page. `prev` and `next` pointers make moving in both directions O(1) per step. Stop at the ends by checking for `nullptr`.

`visit` truncates: everything after the cursor becomes unreachable, so free it immediately (otherwise it would leak until the destructor, or forever). Then append the new page right after the cursor.

The same cursor-in-a-list model underlies undo/redo stacks and text editor buffers. An array plus an index works too (and is cache-friendlier). Here the point is practising cursor manipulation and ownership.

Complexity: O(steps) per move, visit O(1) plus the number of pages freed. Each page is created and freed once.

```cpp
#include <bits/stdc++.h>
using namespace std;

class BrowserHistory {
    struct Page { string url; Page* prev; Page* next; };
    Page* head_;
    Page* cur_;
public:
    explicit BrowserHistory(const string& home) : head_(new Page{home, nullptr, nullptr}), cur_(head_) {}
    BrowserHistory(const BrowserHistory&) = delete;
    BrowserHistory& operator=(const BrowserHistory&) = delete;
    ~BrowserHistory() { while (head_) { Page* n = head_->next; delete head_; head_ = n; } }

    void visit(const string& url) {
        Page* f = cur_->next;                         // drop the whole forward history
        while (f) { Page* n = f->next; delete f; f = n; }
        cur_->next = new Page{url, cur_, nullptr};
        cur_ = cur_->next;
    }
    string back(int steps) {
        while (steps-- > 0 && cur_->prev) cur_ = cur_->prev;
        return cur_->url;
    }
    string forward(int steps) {
        while (steps-- > 0 && cur_->next) cur_ = cur_->next;
        return cur_->url;
    }
};
```
