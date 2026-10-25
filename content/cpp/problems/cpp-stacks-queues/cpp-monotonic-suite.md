---
id: cpp-monotonic-suite
title: Monotonic Stacks and Deques in C++
difficulty: Hard
order: 1
tags: monotonic stack, deque, histogram, sliding-window DP, stock span
time_limit: 2
---
## Statement
```cpp
long long max_rectangle(const std::vector<std::string>& grid);
    // largest all-'1' axis-aligned rectangle in a binary grid (rows of '0'/'1'); O(R*C)
std::vector<int> stock_span(const std::vector<int>& prices);
    // span[i] = number of consecutive days ending at i with price <= prices[i]
long long best_jump_score(const std::vector<int>& score, int k);
    // start at index 0, end at n-1, each jump moves forward 1..k steps; maximise the sum of visited scores.
    // dp[i] = score[i] + max(dp[i-k..i-1]) using a monotonic deque: O(n)
long long sum_subarray_max_minus_min(const std::vector<int>& a);
    // sum over all subarrays of (max - min); O(n) with four monotonic passes
```

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

long long max_rectangle(const vector<string>& grid) { return 0; }
vector<int> stock_span(const vector<int>& p) {
    vector<int> s(p.size());
    for (size_t i = 0; i < p.size(); ++i) { int j = i; while (j >= 0 && p[j] <= p[i]) --j; s[i] = i - j; }
    return s;
}
long long best_jump_score(const vector<int>& score, int k) {
    int n = score.size();
    vector<long long> dp(n, LLONG_MIN);
    dp[0] = score[0];
    for (int i = 1; i < n; ++i)
        for (int j = max(0, i - k); j < i; ++j) dp[i] = max(dp[i], dp[j] + score[i]);
    return dp[n - 1];
}
long long sum_subarray_max_minus_min(const vector<int>& a) {
    long long s = 0;
    for (size_t i = 0; i < a.size(); ++i) {
        int mx = a[i], mn = a[i];
        for (size_t j = i; j < a.size(); ++j) { mx = max(mx, a[j]); mn = min(mn, a[j]); s += mx - mn; }
    }
    return s;
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    string cmd;
    while (cin >> cmd) {
        if (cmd == "rect") {
            int r; cin >> r;
            vector<string> g(r); for (auto& row : g) cin >> row;
            cout << "max_rectangle = " << max_rectangle(g) << '\n';
        } else if (cmd == "span") {
            int n; cin >> n;
            vector<int> p(n); for (auto& x : p) cin >> x;
            auto s = stock_span(p);
            cout << "stock_span:"; for (int x : s) cout << ' ' << x; cout << '\n';
        } else if (cmd == "jump") {
            int n, k; cin >> n >> k;
            vector<int> s(n); for (auto& x : s) cin >> x;
            cout << "best_jump_score(k=" << k << ") = " << best_jump_score(s, k) << '\n';
        } else if (cmd == "range") {
            int n; cin >> n;
            vector<int> a(n); for (auto& x : a) cin >> x;
            cout << "sum(max-min) = " << sum_subarray_max_minus_min(a) << '\n';
        } else if (cmd == "gen") {
            int n; unsigned seed; cin >> n >> seed;
            mt19937 rng(seed);
            int side = 1500;
            vector<string> g(side, string(side, '1'));
            for (auto& row : g) for (auto& c : row) if (rng() % 100 < 4) c = '0';
            vector<int> p(n); for (auto& x : p) x = rng() % 1000;
            auto s = stock_span(p);
            vector<int> sc(n); for (auto& x : sc) x = int(rng() % 2001) - 1000;
            vector<int> a(n); for (auto& x : a) x = rng() % 1000000;
            cout << "gen n=" << n << ": rect=" << max_rectangle(g) << " span_sum=" << accumulate(s.begin(), s.end(), 0LL)
                 << " jump=" << best_jump_score(sc, 5000) << " range=" << sum_subarray_max_minus_min(a) << '\n';
        }
    }
}
```

## Tests
=== sample
rect 4
10100
10111
11111
10010
span 7
100 80 60 70 60 75 85
jump 6 2
1 -1 -2 4 -7 3
range 3
1 2 3
---
max_rectangle = 6
stock_span: 1 1 1 2 1 4 6
best_jump_score(k=2) = 7
sum(max-min) = 4
=== hidden
rect 1
0
rect 1
1
rect 2
111
111
span 1
5
span 4
1 1 1 1
jump 1 3
-5
jump 4 1
-1 -2 -3 -4
jump 5 4
-5 -100 -100 -100 7
range 1
9
range 4
4 -2 -3 4
---
max_rectangle = 0
max_rectangle = 1
max_rectangle = 6
stock_span: 1
stock_span: 1 2 3 4
best_jump_score(k=3) = -5
best_jump_score(k=1) = -10
best_jump_score(k=4) = 2
sum(max-min) = 0
sum(max-min) = 35
=== hidden
gen 300000 4
---
gen n=300000: rect=420 span_sum=48630861 jump=75373887 range=44993681771365852

## Hints
- **max_rectangle**: maintain the column heights per row and run the largest-rectangle-in-histogram stack with a 0 sentinel. Use `long long` areas.
- **stock_span**: a monotonic stack of indices with strictly greater prices. `span = i − (previous greater index)`.
- **best_jump_score**: a deque of indices with decreasing dp values. Drop indices < i − k from the front, then dp[i] = score[i] + dp[front], then pop from the back while dp[back] ≤ dp[i].
- **max − min**: Σ max − Σ min. For Σ max, each element is the max of `left × right` subarrays, with left = the distance to the previous **greater-or-equal** element and right = the distance to the next **strictly greater** one (an asymmetric tie rule). The same for min.

## Solution
```cpp
#include <bits/stdc++.h>
using namespace std;

long long max_rectangle(const vector<string>& grid) {
    if (grid.empty()) return 0;
    int C = grid[0].size();
    vector<int> h(C + 1, 0);                      // h[C] = 0 sentinel
    vector<int> st;
    long long best = 0;
    for (const auto& row : grid) {
        for (int c = 0; c < C; ++c) h[c] = row[c] == '1' ? h[c] + 1 : 0;
        st.clear();
        for (int i = 0; i <= C; ++i) {
            while (!st.empty() && h[st.back()] >= h[i]) {
                long long height = h[st.back()];
                st.pop_back();
                int left = st.empty() ? 0 : st.back() + 1;
                best = max(best, height * (i - left));
            }
            st.push_back(i);
        }
    }
    return best;
}

vector<int> stock_span(const vector<int>& p) {
    vector<int> span(p.size()), st;
    for (int i = 0; i < (int)p.size(); ++i) {
        while (!st.empty() && p[st.back()] <= p[i]) st.pop_back();
        span[i] = st.empty() ? i + 1 : i - st.back();
        st.push_back(i);
    }
    return span;
}

long long best_jump_score(const vector<int>& score, int k) {
    int n = score.size();
    vector<long long> dp(n);
    deque<int> dq;
    dp[0] = score[0];
    dq.push_back(0);
    for (int i = 1; i < n; ++i) {
        while (dq.front() < i - k) dq.pop_front();
        dp[i] = score[i] + dp[dq.front()];
        while (!dq.empty() && dp[dq.back()] <= dp[i]) dq.pop_back();
        dq.push_back(i);
    }
    return dp[n - 1];
}

static long long contribution(const vector<int>& a, bool want_max) {
    int n = a.size();
    auto better = [&](int x, int y) { return want_max ? x > y : x < y; };
    vector<int> left(n), right(n), st;
    for (int i = 0; i < n; ++i) {                 // previous element that is better-or-equal
        while (!st.empty() && better(a[i], a[st.back()])) st.pop_back();
        left[i] = st.empty() ? i + 1 : i - st.back();
        st.push_back(i);
    }
    st.clear();
    for (int i = n - 1; i >= 0; --i) {            // next element that is strictly better
        while (!st.empty() && !better(a[st.back()], a[i])) st.pop_back();
        right[i] = st.empty() ? n - i : st.back() - i;
        st.push_back(i);
    }
    long long s = 0;
    for (int i = 0; i < n; ++i) s += (long long)a[i] * left[i] * right[i];
    return s;
}

long long sum_subarray_max_minus_min(const vector<int>& a) {
    return contribution(a, true) - contribution(a, false);
}
```

- **Maximal rectangle** is R histogram problems of width C, each O(C) with the increasing stack. The sentinel height 0 at the end empties the stack without extra code.
- **Stock span** pops every price ≤ today's, so the new top is the previous strictly greater day, and the span is the distance to it.
- **Jump DP**: the monotonic deque keeps candidate predecessors in decreasing dp order. The front is the best in the window [i−k, i−1], and a predecessor dominated by a newer, better one is discarded. That's O(n) instead of O(n·k).
- **Contribution technique**: each element is the maximum (or minimum) of exactly `left × right` subarrays. The asymmetric tie rule (≥ on one side, > on the other) assigns each subarray with tied extremes to exactly one index. Products are computed in `long long` (10⁶ × 1.5·10⁵ × 1.5·10⁵ needs 64 bits).
