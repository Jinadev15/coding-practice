# Stacks, Queues and Monotonic Structures

C++ offers `std::stack`, `std::queue` and `std::priority_queue` as **container adaptors** over `std::deque` or `std::vector`, plus `std::deque` itself for double-ended work. This lesson shows how to use them idiomatically (and when to skip the adaptor and use a `vector` directly), and implements the monotonic stack and deque patterns, expression evaluation, and a min-stack in C++. The theory is in the Python Stacks and Queues lessons.

## 1. The adaptors

```cpp
stack<int> st;          st.push(1); st.top(); st.pop();     // LIFO; pop() returns void!
queue<int> q;           q.push(1);  q.front(); q.pop();     // FIFO
deque<int> dq;          dq.push_front(0); dq.push_back(1); dq.pop_front(); dq.back();
priority_queue<int> maxh;                                   // max-heap by default
priority_queue<int, vector<int>, greater<int>> minh;        // min-heap
```

> [!KEY]
> `pop()` returns `void` in every standard adaptor: read `top()`/`front()` first, then `pop()`. This is a deliberate design for exception safety, since returning by value could throw after the element was already removed.

Many C++ programmers use a plain `vector` as a stack (`push_back`, `back`, `pop_back`). It's the same speed, and it supports iteration and indexing, which is handy for monotonic stacks and debugging.

## 2. Monotonic stack: next greater element

```cpp
vector<int> next_greater(const vector<int>& a) {
    int n = a.size();
    vector<int> res(n, -1), st;              // st holds indices, values decreasing
    st.reserve(n);
    for (int i = 0; i < n; ++i) {
        while (!st.empty() && a[st.back()] < a[i]) {
            res[st.back()] = a[i];
            st.pop_back();
        }
        st.push_back(i);
    }
    return res;
}
```

### Largest rectangle in a histogram

```cpp
long long largest_rectangle(const vector<int>& h) {
    vector<int> st;
    long long best = 0;
    int n = h.size();
    for (int i = 0; i <= n; ++i) {
        int cur = (i == n) ? 0 : h[i];       // sentinel 0 flushes the stack
        while (!st.empty() && h[st.back()] >= cur) {
            long long height = h[st.back()];
            st.pop_back();
            int left = st.empty() ? 0 : st.back() + 1;
            best = max(best, height * (i - left));
        }
        st.push_back(i);
    }
    return best;
}
```

Use `long long` for the area: heights of 10⁹ times widths of 10⁵ overflow `int`.

## 3. Expression evaluation with two stacks

```cpp
long long evaluate(const string& s) {
    vector<long long> nums; vector<char> ops;
    auto prec = [](char op) { return (op == '+' || op == '-') ? 1 : 2; };
    auto apply = [&] {
        long long b = nums.back(); nums.pop_back();
        long long a = nums.back(); nums.pop_back();
        char op = ops.back(); ops.pop_back();
        nums.push_back(op == '+' ? a + b : op == '-' ? a - b : op == '*' ? a * b : a / b);  // C++ '/' truncates
    };
    for (size_t i = 0; i < s.size(); ++i) {
        char c = s[i];
        if (isspace((unsigned char)c)) continue;
        if (isdigit((unsigned char)c)) {
            long long v = 0;
            while (i < s.size() && isdigit((unsigned char)s[i])) v = v * 10 + (s[i++] - '0');
            --i; nums.push_back(v);
        } else if (c == '(') ops.push_back(c);
        else if (c == ')') { while (ops.back() != '(') apply(); ops.pop_back(); }
        else {
            while (!ops.empty() && ops.back() != '(' && prec(ops.back()) >= prec(c)) apply();
            ops.push_back(c);
        }
    }
    while (!ops.empty()) apply();
    return nums.back();
}
```

(Unary minus needs the "expect operand" flag shown in the Python Monotonic Stack Suite problem.)

## 4. Min-stack and the two-stack queue

```cpp
class MinStack {
    vector<pair<int,int>> st;                // (value, minimum so far)
public:
    void push(int x) { st.emplace_back(x, st.empty() ? x : min(x, st.back().second)); }
    void pop() { st.pop_back(); }
    int top() const { return st.back().first; }
    int get_min() const { return st.back().second; }
};
```

A queue from two stacks (amortised O(1)) works the same way as in Python. In C++, the trick also gives a **min-queue**: two min-stacks, enabling sliding-window minimum with arbitrary push/pop order.

## 5. Monotonic deque: sliding window minimum and DP optimisation

```cpp
// dp[i] = cost[i] + min(dp[j]) for j in [i-k, i-1]: O(n) with a monotonic deque
vector<long long> dp(n);
deque<int> dq;
for (int i = 0; i < n; ++i) {
    while (!dq.empty() && dq.front() < i - k) dq.pop_front();
    long long best = dq.empty() ? 0 : dp[dq.front()];
    dp[i] = cost[i] + best;
    while (!dq.empty() && dp[dq.back()] >= dp[i]) dq.pop_back();
    dq.push_back(i);
}
```

This "sliding window DP" pattern (jump games with a range, constrained subsequence sums) turns O(n·k) into O(n).

## 6. BFS with `std::queue`

```cpp
vector<int> bfs(const vector<vector<int>>& adj, int s) {
    vector<int> dist(adj.size(), -1);
    queue<int> q;
    dist[s] = 0; q.push(s);
    while (!q.empty()) {
        int u = q.front(); q.pop();
        for (int v : adj[u]) if (dist[v] < 0) { dist[v] = dist[u] + 1; q.push(v); }
    }
    return dist;
}
```

## 7. Exam-ready answers

> [!EXAM]
> **Container adaptors.** `std::stack`, `std::queue` and `std::priority_queue` are container adaptors that restrict an underlying sequence container to a particular interface: LIFO access at the back for stack, FIFO access for queue (`push` at the back, `front` and `pop` at the front), and heap-ordered access to the largest element for `priority_queue`, which maintains a binary heap in a random-access container using `std::push_heap` and `std::pop_heap`. The defaults are `std::deque` for stack and queue and `std::vector` for priority_queue; a custom comparator such as `std::greater` turns the priority queue into a min-heap. Their `pop` member functions return void, so the element must be read before removal.

## 8. Cheat sheet

| Need | C++ |
|---|---|
| stack | `vector` with `push_back/back/pop_back` |
| queue | `queue<T>` or `deque<T>` |
| min-heap | `priority_queue<T, vector<T>, greater<T>>` |
| next greater/smaller | a `vector<int>` monotonic stack of indices |
| window min/max | `deque<int>` of indices |
| O(1) minimum | a stack of (value, min) pairs |

> [!INTERVIEW]
> **"Why does `std::stack::pop` return void?"** For exception safety. If `pop` returned the element by value and the copy or move constructor threw while returning, the element would already be removed and lost. Splitting it into `top()` (by reference) and `pop()` keeps each operation exception-safe. This is Tom Cargill's classic analysis of exception-safe container design.
