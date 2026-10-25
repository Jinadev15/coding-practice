---
id: cpp-range-query-engine
title: "Range-Query Engine: Fenwick, Lazy Segment Tree, Trie"
difficulty: Hard
order: 1
tags: Fenwick tree, lazy segment tree, trie, order statistics, inversions
time_limit: 3
---
## Statement
Implement three structures used by a robot fleet's telemetry server:

```cpp
long long count_inversions(const std::vector<int>& a);   // pairs i<j with a[i] > a[j]; values up to 1e9; O(n log n)

class RangeAddMax {                                      // n zeros initially
public:
    explicit RangeAddMax(int n);
    void add(int l, int r, long long v);                 // a[l..r-1] += v
    long long max(int l, int r);                         // max of a[l..r-1]
    long long sum(int l, int r);                         // sum of a[l..r-1]
};

class PrefixCounter {                                    // lowercase words
public:
    void insert(const std::string& w);                   // duplicates count separately
    int count(const std::string& prefix) const;          // words starting with prefix
    std::string kth(int k) const;                        // k-th word (0-based) in sorted order (with duplicates)
};
```

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

long long count_inversions(const vector<int>& a) {
    long long c = 0;
    for (size_t i = 0; i < a.size(); ++i) for (size_t j = i + 1; j < a.size(); ++j) c += a[i] > a[j];
    return c;
}
class RangeAddMax {
    vector<long long> a;
public:
    explicit RangeAddMax(int n) : a(n, 0) {}
    void add(int l, int r, long long v) { for (int i = l; i < r; ++i) a[i] += v; }
    long long max(int l, int r) { return *max_element(a.begin() + l, a.begin() + r); }
    long long sum(int l, int r) { return accumulate(a.begin() + l, a.begin() + r, 0LL); }
};
class PrefixCounter {
    vector<string> ws;
public:
    void insert(const string& w) { ws.push_back(w); }
    int count(const string& p) const { return count_if(ws.begin(), ws.end(), [&](const string& w) { return w.rfind(p, 0) == 0; }); }
    string kth(int k) const { auto c = ws; sort(c.begin(), c.end()); return c[k]; }
};
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    string cmd;
    while (cin >> cmd) {
        if (cmd == "inv") {
            int n; cin >> n; vector<int> a(n); for (auto& x : a) cin >> x;
            cout << "inversions = " << count_inversions(a) << '\n';
        } else if (cmd == "seg") {
            int n, q; cin >> n >> q;
            RangeAddMax t(n);
            cout << "seg:";
            while (q--) {
                string op; int l, r; cin >> op >> l >> r;
                if (op == "add") { long long v; cin >> v; t.add(l, r, v); }
                else if (op == "max") cout << " max=" << t.max(l, r);
                else cout << " sum=" << t.sum(l, r);
            }
            cout << '\n';
        } else if (cmd == "trie") {
            int n, q; cin >> n >> q;
            PrefixCounter pc;
            for (int i = 0; i < n; ++i) { string w; cin >> w; pc.insert(w); }
            cout << "trie:";
            while (q--) {
                string op, x; cin >> op >> x;
                if (op == "count") cout << " count(" << (x == "-" ? "" : x) << ")=" << pc.count(x == "-" ? "" : x);
                else cout << " kth(" << x << ")=" << pc.kth(stoi(x));
            }
            cout << '\n';
        } else if (cmd == "gen") {
            int n; unsigned seed; cin >> n >> seed;
            mt19937 rng(seed);
            vector<int> a(n); for (auto& x : a) x = rng() % 1000000000;
            RangeAddMax t(n);
            long long acc = 0;
            for (int i = 0; i < n; ++i) {
                int l = rng() % n, r = l + 1 + rng() % (n - l);
                if (i % 3 == 0) t.add(l, r, (long long)(rng() % 2001) - 1000);
                else if (i % 3 == 1) acc += t.max(l, r);
                else acc += t.sum(l, r) % 1000003;
            }
            PrefixCounter pc;
            for (int i = 0; i < n; ++i) { string w(1 + rng() % 8, 'a'); for (auto& c : w) c = char('a' + rng() % 4); pc.insert(w); }
            long long tc = 0; string kw;
            for (int i = 0; i < n; ++i) { string p(1 + rng() % 3, 'a'); for (auto& c : p) c = char('a' + rng() % 4); tc += pc.count(p); }
            for (int i = 0; i < 1000; ++i) kw = pc.kth(rng() % n);
            cout << "gen n=" << n << ": inv=" << count_inversions(a) << " seg_acc=" << acc << " trie_counts=" << tc << " last_kth=" << kw << '\n';
        }
    }
}
```

## Tests
=== sample
inv 5
2 4 1 3 5
seg 5 6
add 1 4 3
max 0 5
sum 0 5
add 0 2 -5
max 0 2
sum 1 3
trie 5 5
apple app apply ape app
count ap count app count b kth 0 kth 4
---
inversions = 3
seg: max=3 sum=9 max=-2 sum=1
trie: count(ap)=5 count(app)=4 count(b)=0 kth(0)=ape kth(4)=apply
=== hidden
inv 1
7
inv 4
1 1 1 1
inv 4
4 3 2 1
seg 1 3
max 0 1
add 0 1 -9
max 0 1
seg 4 4
add 0 4 1000000000000
add 2 3 -1
max 0 4
sum 0 4
trie 3 4
b a c
count - kth 0 kth 1 kth 2
---
inversions = 0
inversions = 0
inversions = 6
seg: max=0 max=-9
seg: max=1000000000000 sum=3999999999999
trie: count()=3 kth(0)=a kth(1)=b kth(2)=c
=== hidden
gen 200000 13
---
gen n=200000: inv=10024704084 seg_acc=-3926493116 trie_counts=4207021102 last_kth=abaac

## Hints
- **Inversions**: compress the values, then scan with a Fenwick tree of counts, adding `seen − (count of values ≤ x)` for each element.
- **RangeAddMax**: a recursive lazy segment tree storing (max, sum) per node, with a pending add tag. An add of v raises max by v and sum by v × length.
- **PrefixCounter**: an index-based trie with `array<int,26>` children and a `pass` count per node (words through it) plus an `end` count (words ending there). `kth` descends: at each node, first consume the words ending here, then walk the children in order, skipping whole subtrees by their `pass` counts.

## Solution
```cpp
#include <bits/stdc++.h>
using namespace std;

long long count_inversions(const vector<int>& a) {
    vector<int> vals(a);
    sort(vals.begin(), vals.end());
    vals.erase(unique(vals.begin(), vals.end()), vals.end());
    int m = vals.size();
    vector<int> bit(m + 1, 0);
    long long inv = 0;
    for (size_t seen = 0; seen < a.size(); ++seen) {
        int r = int(lower_bound(vals.begin(), vals.end(), a[seen]) - vals.begin()) + 1;
        int le = 0;
        for (int i = r; i > 0; i -= i & -i) le += bit[i];
        inv += (long long)seen - le;
        for (int i = r; i <= m; i += i & -i) ++bit[i];
    }
    return inv;
}

class RangeAddMax {
    int n;
    vector<long long> mx, sm, lz;
    void apply(int x, int len, long long v) { mx[x] += v; sm[x] += v * len; lz[x] += v; }
    void push(int x, int lo, int hi) {
        if (!lz[x]) return;
        int mid = (lo + hi) / 2;
        apply(2 * x, mid - lo, lz[x]);
        apply(2 * x + 1, hi - mid, lz[x]);
        lz[x] = 0;
    }
    void add(int l, int r, long long v, int x, int lo, int hi) {
        if (r <= lo || hi <= l) return;
        if (l <= lo && hi <= r) { apply(x, hi - lo, v); return; }
        push(x, lo, hi);
        int mid = (lo + hi) / 2;
        add(l, r, v, 2 * x, lo, mid);
        add(l, r, v, 2 * x + 1, mid, hi);
        mx[x] = std::max(mx[2 * x], mx[2 * x + 1]);
        sm[x] = sm[2 * x] + sm[2 * x + 1];
    }
    pair<long long, long long> query(int l, int r, int x, int lo, int hi) {
        if (r <= lo || hi <= l) return {LLONG_MIN, 0};
        if (l <= lo && hi <= r) return {mx[x], sm[x]};
        push(x, lo, hi);
        int mid = (lo + hi) / 2;
        auto A = query(l, r, 2 * x, lo, mid), B = query(l, r, 2 * x + 1, mid, hi);
        return {std::max(A.first, B.first), A.second + B.second};
    }
public:
    explicit RangeAddMax(int n) : n(n), mx(4 * n, 0), sm(4 * n, 0), lz(4 * n, 0) {}
    void add(int l, int r, long long v) { add(l, r, v, 1, 0, n); }
    long long max(int l, int r) { return query(l, r, 1, 0, n).first; }
    long long sum(int l, int r) { return query(l, r, 1, 0, n).second; }
};

class PrefixCounter {
    struct Node { array<int, 26> next; int pass = 0, end = 0; Node() { next.fill(-1); } };
    vector<Node> t{1};
public:
    void insert(const string& w) {
        int cur = 0;
        ++t[0].pass;
        for (char ch : w) {
            int c = ch - 'a';
            if (t[cur].next[c] < 0) { t[cur].next[c] = (int)t.size(); t.emplace_back(); }
            cur = t[cur].next[c];
            ++t[cur].pass;
        }
        ++t[cur].end;
    }
    int count(const string& p) const {
        int cur = 0;
        for (char ch : p) { cur = t[cur].next[ch - 'a']; if (cur < 0) return 0; }
        return t[cur].pass;
    }
    string kth(int k) const {
        string out;
        int cur = 0;
        while (true) {
            if (k < t[cur].end) return out;            // a word ending here comes first in sorted order
            k -= t[cur].end;
            for (int c = 0; c < 26; ++c) {
                int nx = t[cur].next[c];
                if (nx < 0) continue;
                if (k < t[nx].pass) { out += char('a' + c); cur = nx; break; }
                k -= t[nx].pass;                       // skip the whole subtree
            }
        }
    }
};
```

- **Inversions** turn pair comparisons into prefix counts over compressed ranks. That's O(n log n) with a tiny constant: one sort plus 2 log n Fenwick steps per element.
- **The lazy segment tree** supports range add with *two* aggregates at once. One tag updates both, because adding v shifts every element: the max rises by v and the sum by v × length. Tags are pushed down only when a later operation needs a child.
- **The trie with subtree counts** turns sorted-order queries into a single descent. Words ending at a node precede everything below it (a prefix sorts first), and whole sibling subtrees are skipped using their `pass` counts. That's O(|word| · 26) per `kth`, without ever sorting the dictionary.
