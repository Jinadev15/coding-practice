---
id: c-collatz-c
title: Longest Collatz Chain
difficulty: Medium
order: 2
tags: loops, long long, performance, memoization
---
## Statement
For a limit `L` (1 ≤ L ≤ 3·10^6), find the starting number `s ≤ L` that produces the **longest** Collatz chain (`n → n/2` if even, `3n+1` if odd, until 1), and print `s steps` (smallest `s` on ties).

Intermediate values exceed 2^32, so use `long long`. The large tests need a cache: store the steps for every `n < L` in an array and stop the walk as soon as you reach a cached value.

## Starter
```c
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    int L;
    scanf("%d", &L);

    return 0;
}
```

## Tests
=== sample
10
---
9 19
=== hidden
1
---
1 0
=== hidden
1000000
---
837799 524
=== hidden
3000000
---
2298025 559

## Hints
- `int *steps = calloc(L + 1, sizeof *steps);`, with `steps[1] = 0`.
- For each start: walk with a `long long x`, counting, until `x < start` (already cached, since every smaller start was computed earlier). The answer is then `count + steps[x]`.

## Solution
Every start below the current one has already been computed, so a walk can stop the moment it drops below its own start and reuse the cached value. That turns about 10^8 steps into a few times 10^7.

```c
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    int L;
    scanf("%d", &L);
    int *steps = calloc((size_t)L + 1, sizeof *steps);
    if (!steps) return 1;
    int best = 1, best_steps = 0;
    for (int s = 2; s <= L; s++) {
        long long x = s;
        int count = 0;
        while (x >= s) {
            x = (x % 2 == 0) ? x / 2 : 3 * x + 1;
            count++;
        }
        steps[s] = count + steps[x];
        if (steps[s] > best_steps) {
            best_steps = steps[s];
            best = s;
        }
    }
    printf("%d %d\n", best, best_steps);
    free(steps);
    return 0;
}
```

`calloc` zero-initialises the array (heap memory, explained in the Memory module): 12 MB is too big for the stack. `x` can exceed 2^32 during the walk (837799's chain peaks near 3·10^9), so `long long` is required. The same loop in plain Python takes over 10 seconds.
