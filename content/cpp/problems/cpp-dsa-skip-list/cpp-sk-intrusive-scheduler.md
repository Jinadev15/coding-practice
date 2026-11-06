---
id: cpp-sk-intrusive-scheduler
title: Intrusive Lists: a Round-Robin Scheduler
difficulty: Medium
order: 2
tags: intrusive list, list_head, container_of, offsetof, kernel style
time_limit: 2
---
## Statement
In the Linux kernel, a list node is not a separate allocation that points at the data. Instead the **link is embedded inside the object** (`struct list_head`), and `container_of` recovers the object from a pointer to its link. One object can sit in several lists at once by embedding several links, with no extra allocation per list.

Build a round-robin task scheduler this way. Each task lives in **two** circular doubly linked lists at the same time: `all` (every live task, in creation order) and `ready` (runnable tasks, in queue order).

```cpp
struct list_head { list_head *next, *prev; };
#define container_of(ptr, type, member) ((type*)((char*)(ptr) - offsetof(type, member)))
struct Task { int id; list_head all; list_head ready; bool runnable; };

class Scheduler {
public:
    Scheduler(); ~Scheduler();                    // the destructor frees every remaining task
    void create(int id);   // new task: append to `all` and to the back of `ready`
    void sleep(int id);    // remove from `ready` if it is there
    void wake(int id);     // append to the back of `ready` if it is not there
    int  run();            // front of `ready` runs: return its id and move it to the back; -1 if none
    void kill(int id);     // remove from both lists and delete the task
    std::vector<int> all_ids() const;    // walk `all` with container_of
    std::vector<int> ready_ids() const;  // walk `ready` with container_of
};
```

Implement the list primitives on sentinel-headed circular lists (`list_init`, `list_add_tail`, `list_del`) and use `container_of` to get from a `list_head*` back to its `Task`. An `unordered_map<int, Task*>` finds tasks by id. All operations except the two listings must be O(1). Commands always name a live task for sleep/wake/kill, and `create` uses an id that is not live.

**Input:** `q`, then `q` commands: `C id`, `S id`, `W id`, `R`, `K id`, `A` (list all), `Q` (list ready). q ≤ 2·10⁵, at most 60 listing commands, 0 ≤ id < 10⁹.

**Output:** each `R` prints the id it ran (or `-1`), 20 per line; each listing prints `A` or `Q`, then `count: first 20 ids | checksum`.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

struct list_head { list_head *next, *prev; };
#define container_of(ptr, type, member) ((type*)((char*)(ptr) - offsetof(type, member)))
struct Task { int id; list_head all; list_head ready; bool runnable; };

class Scheduler {
    list_head all_, ready_;            // sentinels
    unordered_map<int, Task*> byId;
public:
    Scheduler() {}                      // TODO: init both sentinels
    ~Scheduler() {}                     // TODO: free all tasks
    void create(int id) {}
    void sleep(int id) {}
    void wake(int id) {}
    int run() { return -1; }
    void kill(int id) {}
    vector<int> all_ids() const { return {}; }
    vector<int> ready_ids() const { return {}; }
};
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int q; cin >> q;
    Scheduler s; string out; int cnt = 0;
    auto list = [&](char tag, const vector<int>& v) {
        if (!out.empty() && out.back() == ' ') out.back() = '\n';
        string first; unsigned long long hs = 0;
        for (size_t i = 0; i < v.size(); ++i) { if (i < 20) first += " " + to_string(v[i]); hs = hs * 1000003 + (unsigned)v[i]; }
        out += string(1, tag) + ' ' + to_string(v.size()) + ':' + first + " | " + to_string(hs) + '\n'; cnt = 0;
    };
    while (q--) {
        char c; cin >> c; int id = 0;
        if (c == 'C' || c == 'S' || c == 'W' || c == 'K') cin >> id;
        if (c == 'C') s.create(id);
        else if (c == 'S') s.sleep(id);
        else if (c == 'W') s.wake(id);
        else if (c == 'K') s.kill(id);
        else if (c == 'R') { out += to_string(s.run()); out += (++cnt % 20 == 0) ? '\n' : ' '; }
        else if (c == 'A') list('A', s.all_ids());
        else list('Q', s.ready_ids());
    }
    while (!out.empty() && (out.back() == ' ' || out.back() == '\n')) out.pop_back();
    cout << out << '\n';
}
```

## Tests
=== sample
13
C 1
C 2
C 3
R
R
S 1
R
Q
W 1
R
K 2
A
Q
---
1 2 3
Q 2: 2 3 | 2000009
2
A 2: 1 3 | 1000006
Q 2: 3 1 | 3000010
=== hidden
6
R
C 7
R
R
S 7
R
---
-1 7 7 -1
=== hidden
10
C 5
C 6
S 5
S 5
W 6
Q
K 5
A
Q
R
---
Q 1: 6 | 6
A 1: 6 | 6
Q 1: 6 | 6
6
=== hidden
40
C 0
C 1
R
R
Q
R
A
R
C 2
R
R
W 1
S 1
W 1
R
R
R
W 1
R
R
R
R
R
W 0
C 3
R
R
K 2
R
W 3
R
R
R
R
R
C 4
S 0
S 0
R
W 1
---
0 1
Q 2: 0 1 | 1
0
A 2: 0 1 | 1
1 0 1 2 0 1 2 0 1 2 0 1 2 0 3 1 0 3 1 3
=== hidden
40
C 0
S 0
S 0
R
S 0
R
W 0
C 1
Q
R
C 2
Q
R
R
W 0
R
S 2
R
R
R
C 3
S 3
C 4
R
C 5
R
W 3
R
R
R
C 6
C 7
R
K 6
R
C 8
R
C 9
R
W 4
---
-1 -1
Q 2: 0 1 | 1
0
Q 3: 1 0 2 | 1000006000011
1 0 2 1 0 1 0 1 4 0 5 1 3 4 0
=== hidden
20
C 0
C 1
C 2
R
C 3
C 4
R
R
C 5
C 6
R
A
R
K 0
R
R
A
R
W 5
R
---
0 1 2 0
A 7: 0 1 2 3 4 5 6 | 8567392169877094111
3 4 1
A 6: 1 2 3 4 5 6 | 8567392169877094111
2 5
=== hidden
@gen 3033390200 big
=== hidden
@gen 3033390201 big
=== hidden
@gen 3033390202 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
q = r.randint(5, 40) if not big else 200000
live, run_, nxt, out, lists = [], set(), 0, [], 0
for _ in range(q):
    x = r.random()
    if lists < 60 and r.random() < (0.1 if not big else 0.0002):
        out.append(r.choice("AQ")); lists += 1
    elif not live or x < 0.25:
        i = r.randint(0, 10**9 - 1) if big else nxt; nxt += 1
        while i in live: i = r.randint(0, 10**9 - 1)
        live.append(i); run_.add(i); out.append(f"C {i}")
    elif x < 0.4:
        i = r.choice(live); run_.discard(i); out.append(f"S {i}")
    elif x < 0.55:
        i = r.choice(live); run_.add(i); out.append(f"W {i}")
    elif x < 0.6:
        j = r.randrange(len(live)); i = live[j]; live[j] = live[-1]; live.pop(); run_.discard(i); out.append(f"K {i}")
    else:
        out.append("R")
print(len(out)); print("\n".join(out))
```

## Hints
- With a circular sentinel, an empty list is `h->next == h`, and inserting before the sentinel appends at the tail.
- `container_of(p, Task, ready)` subtracts `offsetof(Task, ready)` from the link's address to get the Task. Use the member name that matches the list you are walking.
- Keep a flag that says whether the task is in `ready`, so sleep/wake are idempotent. Free tasks by walking `all` and advancing before `delete`.

## Solution
**Intrusive links.** `Task` contains two `list_head` members. The `all` list threads through every task's `all` member, the `ready` list through every `ready` member. Both lists are circular with a **sentinel** (`all_`, `ready_` in the scheduler), so insertion and removal never test for null.

**container_of.** Walking a list gives `list_head*` pointers. `offsetof(Task, ready)` is the byte distance from the start of a `Task` to its `ready` member, so subtracting it from the link's address yields the `Task*`. This needs `Task` to be a standard-layout type (plain members, no virtual functions), which it is.

**Operations.**

- `create`: allocate once, `list_add_tail` into both lists.
- `sleep`/`wake`: `list_del` / `list_add_tail` on the `ready` link only. The `runnable` flag says whether the task is currently in `ready`. (`list_del` re-initialises the link to point at itself, the kernel's `list_del_init`, so a stale link can't corrupt anything.)
- `run`: take `ready_.next`, unlink it and append it at the back: round robin.
- `kill`: unlink from both lists, erase from the map, `delete`.

No operation allocates except `create`, and removing a task from a list needs no search: you already hold its link. That's the point of intrusive lists. Compare `std::list<Task*>`: one extra allocation per list membership and an iterator to store per list to get O(1) removal.

The scheduler deletes copying because its sentinels point to themselves; a copy would point into the original.

Complexity: O(1) per command (expected, for the hash map), O(n) per listing.

```cpp
#include <bits/stdc++.h>
using namespace std;

struct list_head { list_head *next, *prev; };
#define container_of(ptr, type, member) ((type*)((char*)(ptr) - offsetof(type, member)))
struct Task { int id; list_head all; list_head ready; bool runnable; };

static void list_init(list_head* h) { h->next = h->prev = h; }
static void list_add_tail(list_head* n, list_head* h) {     // insert n just before the sentinel h
    n->prev = h->prev; n->next = h;
    h->prev->next = n; h->prev = n;
}
static void list_del(list_head* n) {
    n->prev->next = n->next; n->next->prev = n->prev;
    list_init(n);                                          // a removed link points at itself
}

class Scheduler {
    list_head all_, ready_;
    unordered_map<int, Task*> byId;
public:
    Scheduler() { list_init(&all_); list_init(&ready_); }
    ~Scheduler() {
        for (list_head* p = all_.next; p != &all_; ) {
            Task* t = container_of(p, Task, all);
            p = p->next;
            delete t;
        }
    }
    Scheduler(const Scheduler&) = delete;               // the sentinels are self-referencing
    Scheduler& operator=(const Scheduler&) = delete;
    void create(int id) {
        Task* t = new Task{id, {}, {}, true};
        list_add_tail(&t->all, &all_);
        list_add_tail(&t->ready, &ready_);
        byId[id] = t;
    }
    void sleep(int id) { Task* t = byId[id]; if (t->runnable) { list_del(&t->ready); t->runnable = false; } }
    void wake(int id)  { Task* t = byId[id]; if (!t->runnable) { list_add_tail(&t->ready, &ready_); t->runnable = true; } }
    int run() {
        if (ready_.next == &ready_) return -1;
        list_head* p = ready_.next;
        list_del(p); list_add_tail(p, &ready_);            // rotate to the back
        return container_of(p, Task, ready)->id;
    }
    void kill(int id) {
        Task* t = byId[id]; byId.erase(id);
        list_del(&t->all);
        if (t->runnable) list_del(&t->ready);
        delete t;
    }
    vector<int> all_ids() const {
        vector<int> v;
        for (const list_head* p = all_.next; p != &all_; p = p->next) v.push_back(container_of(p, const Task, all)->id);
        return v;
    }
    vector<int> ready_ids() const {
        vector<int> v;
        for (const list_head* p = ready_.next; p != &ready_; p = p->next) v.push_back(container_of(p, const Task, ready)->id);
        return v;
    }
};
```
