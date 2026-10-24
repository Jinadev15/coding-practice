---
id: c-two-pointer-sum
title: Pair Sum with Pointer Walking
difficulty: Medium
order: 1
tags: pointer arithmetic, two pointers, sorted array
---
## Statement
Implement `int find_pair(const int *begin, const int *end, int target, const int **x, const int **y)` on a **sorted** range `[begin, end)`:

- find two elements at **different positions** whose sum is `target`
- write pointers to them through `x` and `y` (with `*x` pointing earlier than `*y`), and return 1
- return 0 if no pair exists

Use only pointers (`lo` and `hi`) moving toward each other, with no indices. If several pairs exist, the two-pointer sweep's first find is the one expected (move `lo` forward when the sum is too small, `hi` back when it's too big).

## Starter
```c
int find_pair(const int *begin, const int *end, int target, const int **x, const int **y) {
    return 0;
}
```

## Driver
```c
#include <stdio.h>
int main(void) {
    int n, target;
    scanf("%d %d", &n, &target);
    static int a[200000];
    for (int i = 0; i < n; i++) scanf("%d", &a[i]);
    const int *x, *y;
    if (find_pair(a, a + n, target, &x, &y))
        printf("%d+%d at %td,%td\n", *x, *y, x - a, y - a);
    else
        printf("none\n");
    return 0;
}
```

## Tests
=== sample
5 9
1 2 4 5 7
---
2+7 at 1,4
=== hidden
1 4
2
---
none
=== hidden
4 6
3 3 3 3
---
3+3 at 0,3
=== hidden
0 5

---
none
=== hidden
6 -3
-5 -4 -1 0 2 9
---
-5+2 at 0,4

## Hints
- `const int *lo = begin, *hi = end - 1;` but only when `begin < end`.
- Loop `while (lo < hi)`: compare `*lo + *hi` with the target, using `long long` to avoid overflow.

## Solution
```c
int find_pair(const int *begin, const int *end, int target, const int **x, const int **y) {
    if (end - begin < 2) return 0;
    const int *lo = begin, *hi = end - 1;
    while (lo < hi) {
        long long s = (long long)*lo + *hi;
        if (s == target) {
            *x = lo;
            *y = hi;
            return 1;
        }
        if (s < target) lo++;
        else hi--;
    }
    return 0;
}
```

The `end - begin < 2` check happens **before** computing `end - 1`, because for an empty range `end - 1` would point before the array, which is undefined behaviour even if never dereferenced. Positions come out by pointer subtraction (`x - a`). This is the same algorithm as the Python Two Pointers topic, expressed as C++-style iterators.
