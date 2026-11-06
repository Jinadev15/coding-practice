---
id: cpp-insertion-sort-trace
title: Insertion Sort, Pass by Pass
difficulty: Easy
order: 1
tags: sorting, insertion sort, inversions, tracing
time_limit: 1
---
## Statement
Implement insertion sort and show its work:

```cpp
long long insertion_sort(std::vector<int>& a, std::vector<std::string>& trace);
```

- Sort `a` ascending with insertion sort. For each `i = 1 … n−1`, take `a[i]` as the key and shift every larger element of the sorted prefix one step right.
- After each pass `i`, append the whole array to `trace` (numbers separated by spaces) **only when n ≤ 12**.
- Return the total number of **shifts** (single-element moves to the right). This equals the number of inversions in the input.

Equal elements must **not** be shifted past each other. Compare with `>`, which also keeps the sort stable.

**Input:** cases until the end of input: `n`, followed by `n` integers (n ≤ 3000). Print the trace lines, then `shifts: X`.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

long long insertion_sort(vector<int>& a, vector<string>& trace) {
    sort(a.begin(), a.end());
    return 0;
}
```

## Driver
```cpp
int main() {
    int n;
    while (cin >> n) {
        vector<int> a(n);
        for (auto& x : a) cin >> x;
        vector<string> trace;
        long long s = insertion_sort(a, trace);
        for (auto& t : trace) cout << t << '\n';
        cout << "shifts: " << s << '\n';
    }
}
```

## Tests
=== sample
5
5 2 4 6 1
---
2 5 4 6 1
2 4 5 6 1
2 4 5 6 1
1 2 4 5 6
shifts: 6
=== hidden
1
7
4
4 3 2 1
6
2 2 1 1 3 3
---
shifts: 0
3 4 2 1
2 3 4 1
1 2 3 4
shifts: 6
2 2 1 1 3 3
1 2 2 1 3 3
1 1 2 2 3 3
1 1 2 2 3 3
1 1 2 2 3 3
shifts: 4
=== hidden
12
3 4 5 -5 -2 -2 5 1 0 -4 -3 2
13
13 12 11 10 9 8 7 6 5 4 3 2 1
---
3 4 5 -5 -2 -2 5 1 0 -4 -3 2
3 4 5 -5 -2 -2 5 1 0 -4 -3 2
-5 3 4 5 -2 -2 5 1 0 -4 -3 2
-5 -2 3 4 5 -2 5 1 0 -4 -3 2
-5 -2 -2 3 4 5 5 1 0 -4 -3 2
-5 -2 -2 3 4 5 5 1 0 -4 -3 2
-5 -2 -2 1 3 4 5 5 0 -4 -3 2
-5 -2 -2 0 1 3 4 5 5 -4 -3 2
-5 -4 -2 -2 0 1 3 4 5 5 -3 2
-5 -4 -3 -2 -2 0 1 3 4 5 5 2
-5 -4 -3 -2 -2 0 1 2 3 4 5 5
shifts: 38
shifts: 78
=== hidden
11
-5 4 1 5 2 0 2 3 -1 -1 0
7
-3 1 -1 -3 2 3 -5
4
-4 3 1 1
7
-2 2 -2 -5 -2 -3 5
---
-5 4 1 5 2 0 2 3 -1 -1 0
-5 1 4 5 2 0 2 3 -1 -1 0
-5 1 4 5 2 0 2 3 -1 -1 0
-5 1 2 4 5 0 2 3 -1 -1 0
-5 0 1 2 4 5 2 3 -1 -1 0
-5 0 1 2 2 4 5 3 -1 -1 0
-5 0 1 2 2 3 4 5 -1 -1 0
-5 -1 0 1 2 2 3 4 5 -1 0
-5 -1 -1 0 1 2 2 3 4 5 0
-5 -1 -1 0 0 1 2 2 3 4 5
shifts: 31
-3 1 -1 -3 2 3 -5
-3 -1 1 -3 2 3 -5
-3 -3 -1 1 2 3 -5
-3 -3 -1 1 2 3 -5
-3 -3 -1 1 2 3 -5
-5 -3 -3 -1 1 2 3
shifts: 9
-4 3 1 1
-4 1 3 1
-4 1 1 3
shifts: 2
-2 2 -2 -5 -2 -3 5
-2 -2 2 -5 -2 -3 5
-5 -2 -2 2 -2 -3 5
-5 -2 -2 -2 2 -3 5
-5 -3 -2 -2 -2 2 5
-5 -3 -2 -2 -2 2 5
shifts: 9
=== hidden
6
2 0 -4 3 0 -3
7
2 2 0 2 -5 1 1
10
-5 -4 -4 0 -1 5 -4 0 -2 -3
2
5 -1
---
0 2 -4 3 0 -3
-4 0 2 3 0 -3
-4 0 2 3 0 -3
-4 0 0 2 3 -3
-4 -3 0 0 2 3
shifts: 9
2 2 0 2 -5 1 1
0 2 2 2 -5 1 1
0 2 2 2 -5 1 1
-5 0 2 2 2 1 1
-5 0 1 2 2 2 1
-5 0 1 1 2 2 2
shifts: 12
-5 -4 -4 0 -1 5 -4 0 -2 -3
-5 -4 -4 0 -1 5 -4 0 -2 -3
-5 -4 -4 0 -1 5 -4 0 -2 -3
-5 -4 -4 -1 0 5 -4 0 -2 -3
-5 -4 -4 -1 0 5 -4 0 -2 -3
-5 -4 -4 -4 -1 0 5 0 -2 -3
-5 -4 -4 -4 -1 0 0 5 -2 -3
-5 -4 -4 -4 -2 -1 0 0 5 -3
-5 -4 -4 -4 -3 -2 -1 0 0 5
shifts: 14
-1 5
shifts: 1
=== hidden
6
-2 -2 0 5 -2 0
11
-3 3 -4 2 -2 -4 -1 -5 -4 -5 5
10
-5 -1 -2 5 4 2 -4 -4 4 4
10
-2 -3 4 -5 3 4 3 -5 -3 0
---
-2 -2 0 5 -2 0
-2 -2 0 5 -2 0
-2 -2 0 5 -2 0
-2 -2 -2 0 5 0
-2 -2 -2 0 0 5
shifts: 3
-3 3 -4 2 -2 -4 -1 -5 -4 -5 5
-4 -3 3 2 -2 -4 -1 -5 -4 -5 5
-4 -3 2 3 -2 -4 -1 -5 -4 -5 5
-4 -3 -2 2 3 -4 -1 -5 -4 -5 5
-4 -4 -3 -2 2 3 -1 -5 -4 -5 5
-4 -4 -3 -2 -1 2 3 -5 -4 -5 5
-5 -4 -4 -3 -2 -1 2 3 -4 -5 5
-5 -4 -4 -4 -3 -2 -1 2 3 -5 5
-5 -5 -4 -4 -4 -3 -2 -1 2 3 5
-5 -5 -4 -4 -4 -3 -2 -1 2 3 5
shifts: 31
-5 -1 -2 5 4 2 -4 -4 4 4
-5 -2 -1 5 4 2 -4 -4 4 4
-5 -2 -1 5 4 2 -4 -4 4 4
-5 -2 -1 4 5 2 -4 -4 4 4
-5 -2 -1 2 4 5 -4 -4 4 4
-5 -4 -2 -1 2 4 5 -4 4 4
-5 -4 -4 -2 -1 2 4 5 4 4
-5 -4 -4 -2 -1 2 4 4 5 4
-5 -4 -4 -2 -1 2 4 4 4 5
shifts: 16
-3 -2 4 -5 3 4 3 -5 -3 0
-3 -2 4 -5 3 4 3 -5 -3 0
-5 -3 -2 4 3 4 3 -5 -3 0
-5 -3 -2 3 4 4 3 -5 -3 0
-5 -3 -2 3 4 4 3 -5 -3 0
-5 -3 -2 3 3 4 4 -5 -3 0
-5 -5 -3 -2 3 3 4 4 -3 0
-5 -5 -3 -3 -2 3 3 4 4 0
-5 -5 -3 -3 -2 0 3 3 4 4
shifts: 22
=== hidden
@gen 192202406 big
=== hidden
@gen 192202407 big
=== hidden
@gen 192202408 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
if sys.argv[2] == "small":
    for _ in range(4):
        n = r.randint(1, 12); print(n); print(*[r.randint(-5, 5) for _ in range(n)])
else:
    n = 3000; print(n); print(*[r.randint(-10**9, 10**9) for _ in range(n)])
```

## Hints
- Save `key = a[i]`, then shift elements right while the element before the gap is **greater** than the key.
- Count one shift each time an element moves right.
- Record the trace after every pass `i`, including passes where nothing moved.

## Solution
The prefix `a[0..i−1]` is always sorted. The key `a[i]` slides left past every **strictly larger** element, and each step is one shift.

**Why shifts = inversions.** Each shift moves the key past exactly one element that was bigger than it and before it in the input, which is one inversion. Every inversion gets resolved exactly once this way.

That's why insertion sort is O(n + inversions). On nearly sorted data it is close to linear.

Complexity: O(n²) worst case, O(n) on sorted input.

```cpp
#include <bits/stdc++.h>
using namespace std;

long long insertion_sort(vector<int>& a, vector<string>& trace) {
    long long shifts = 0;
    for (size_t i = 1; i < a.size(); ++i) {
        int key = a[i];
        size_t j = i;
        while (j > 0 && a[j - 1] > key) {       // strictly greater: equal elements stay put (stable)
            a[j] = a[j - 1];
            --j; ++shifts;
        }
        a[j] = key;
        if (a.size() <= 12) {
            string line;
            for (size_t k = 0; k < a.size(); ++k) line += (k ? " " : "") + to_string(a[k]);
            trace.push_back(line);
        }
    }
    return shifts;
}
```
