---
id: cpp-window-toolkit
title: Sliding Windows and STL Two-Pointer Algorithms
difficulty: Medium
order: 9
tags: sliding window, two pointers, deque, STL algorithms, erase-remove
time_limit: 2
---
## Statement
Implement four array utilities. Each must be O(n), or O(n log n) where noted:

```cpp
int longest_sum_at_most(const std::vector<int>& a, long long S);
    // a[i] >= 0: length of the longest contiguous subarray with sum <= S
std::vector<int> window_minimums(const std::vector<int>& a, int k);
    // min of every window of size k (1 <= k <= n), using a monotonic deque
std::string min_cover(const std::string& s, const std::string& t);
    // shortest substring of s containing all chars of t with multiplicity; leftmost on ties; "" if none
void compact_sorted_unique(std::vector<int>& v);
    // sort v and remove duplicates IN PLACE using std::sort + std::unique + erase (O(n log n))
```

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

int longest_sum_at_most(const vector<int>& a, long long S) {
    int best = 0;
    for (size_t i = 0; i < a.size(); ++i) {
        long long s = 0;
        for (size_t j = i; j < a.size(); ++j) { s += a[j]; if (s <= S) best = max(best, int(j - i + 1)); }
    }
    return best;
}
vector<int> window_minimums(const vector<int>& a, int k) {
    vector<int> out;
    for (size_t i = 0; i + k <= a.size(); ++i) out.push_back(*min_element(a.begin() + i, a.begin() + i + k));
    return out;
}
string min_cover(const string& s, const string& t) { return ""; }
void compact_sorted_unique(vector<int>& v) { sort(v.begin(), v.end()); }
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    string cmd;
    while (cin >> cmd) {
        if (cmd == "sum") {
            int n; long long S; cin >> n >> S;
            vector<int> a(n); for (auto& x : a) cin >> x;
            cout << "longest_sum_at_most(" << S << ") = " << longest_sum_at_most(a, S) << '\n';
        } else if (cmd == "winmin") {
            int n, k; cin >> n >> k;
            vector<int> a(n); for (auto& x : a) cin >> x;
            auto r = window_minimums(a, k);
            cout << "window_minimums:";
            for (int x : r) cout << ' ' << x;
            cout << '\n';
        } else if (cmd == "cover") {
            string s, t; cin >> s >> t;
            cout << "min_cover = \"" << min_cover(s, t) << "\"\n";
        } else if (cmd == "unique") {
            int n; cin >> n;
            vector<int> v(n); for (auto& x : v) cin >> x;
            compact_sorted_unique(v);
            cout << "unique (" << v.size() << "):";
            for (int x : v) cout << ' ' << x;
            cout << '\n';
        } else if (cmd == "gen") {
            int n; unsigned seed; cin >> n >> seed;
            mt19937 rng(seed);
            vector<int> a(n); for (auto& x : a) x = rng() % 1000;
            auto w = window_minimums(a, 1000);
            long long ws = accumulate(w.begin(), w.end(), 0LL);
            string s(n, 'a'); for (auto& c : s) c = char('a' + rng() % 6);
            string cov = min_cover(s, "abcdefabcdef");
            vector<int> v(n); for (auto& x : v) x = rng() % (n / 2 + 1);
            compact_sorted_unique(v);
            cout << "gen n=" << n << ": longest=" << longest_sum_at_most(a, 100000) << " winmin_sum=" << ws
                 << " cover_len=" << cov.size() << " cover=" << cov << " unique=" << v.size() << '\n';
        }
    }
}
```

## Tests
=== sample
sum 6 7
2 1 5 1 1 3
winmin 8 3
1 3 -1 -3 5 3 6 7
cover ADOBECODEBANC ABC
unique 7
3 1 3 2 1 9 2
---
longest_sum_at_most(7) = 3
window_minimums: -1 -3 -3 -3 3 3
min_cover = "BANC"
unique (4): 1 2 3 9
=== hidden
sum 1 0
5
sum 3 0
0 0 0
sum 4 100
1 2 3 4
winmin 1 1
42
winmin 5 5
5 4 3 2 1
cover a aa
cover aa aa
cover xyzzyx zx
unique 1
7
unique 4
2 2 2 2
---
longest_sum_at_most(0) = 0
longest_sum_at_most(0) = 3
longest_sum_at_most(100) = 4
window_minimums: 42
window_minimums: 1
min_cover = ""
min_cover = "aa"
min_cover = "xyz"
unique (1): 7
unique (1): 2
=== hidden
gen 1000000 3
---
gen n=1000000: longest=237 winmin_sum=574259 cover_len=12 cover=aacdfedbfbec unique=432310

## Hints
- **longest_sum_at_most**: expand right, and while `sum > S` shrink left. The values are non-negative, so validity is monotone.
- **window_minimums**: a deque of indices with increasing values. Pop the back while it's ≥ the new value, and pop the front when it leaves the window.
- **min_cover**: `array<int,128> need`, plus a counter `missing = t.size()`. Record strictly shorter windows so the leftmost one wins ties.
- **unique**: `v.erase(unique(v.begin(), v.end()), v.end());` after sorting.

## Solution
```cpp
#include <bits/stdc++.h>
using namespace std;

int longest_sum_at_most(const vector<int>& a, long long S) {
    long long sum = 0;
    int best = 0;
    for (size_t l = 0, r = 0; r < a.size(); ++r) {
        sum += a[r];
        while (sum > S) sum -= a[l++];
        best = max(best, int(r - l + 1));
    }
    return best;
}

vector<int> window_minimums(const vector<int>& a, int k) {
    deque<int> dq;
    vector<int> out;
    out.reserve(a.size() >= (size_t)k ? a.size() - k + 1 : 0);
    for (int i = 0; i < (int)a.size(); ++i) {
        while (!dq.empty() && a[dq.back()] >= a[i]) dq.pop_back();
        dq.push_back(i);
        if (dq.front() <= i - k) dq.pop_front();
        if (i >= k - 1) out.push_back(a[dq.front()]);
    }
    return out;
}

string min_cover(const string& s, const string& t) {
    if (t.empty()) return "";
    array<int, 256> need{};
    for (unsigned char c : t) ++need[c];
    int missing = (int)t.size(), best_l = 0, best_len = INT_MAX;
    for (int l = 0, r = 0; r < (int)s.size(); ++r) {
        if (need[(unsigned char)s[r]]-- > 0) --missing;
        while (missing == 0) {
            if (r - l + 1 < best_len) { best_len = r - l + 1; best_l = l; }
            if (++need[(unsigned char)s[l++]] > 0) ++missing;
        }
    }
    return best_len == INT_MAX ? "" : s.substr(best_l, best_len);
}

void compact_sorted_unique(vector<int>& v) {
    sort(v.begin(), v.end());
    v.erase(unique(v.begin(), v.end()), v.end());
}
```

These are the Python sliding-window patterns, written with C++'s tools:
- **Counting windows** use a fixed `array<int, 256>` indexed by `unsigned char`, much faster than a hash map and safe for any byte value.
- **The monotonic deque** stores indices, so it can expire elements by position, and each index is pushed and popped once.
- **The erase–remove idiom**: `unique` performs the reader/writer two-pointer compaction and returns the new logical end, and `erase` trims the container.
- `out.reserve(...)` avoids repeated reallocation when producing a million results.
