---
id: c-permutations
title: Permutations by Backtracking
difficulty: Medium
order: 1
tags: recursion, backtracking, strings
---
## Statement
Given a string of **distinct** lowercase letters (length 1–8), print all its permutations in **lexicographic order**, one per line, then the count.

Use recursion with backtracking: sort the letters first, then at each position try each unused letter in order.

## Starter
```c
#include <stdio.h>
#include <string.h>

int main(void) {
    char s[16];
    scanf("%15s", s);

    return 0;
}
```

## Tests
=== sample
cab
---
abc
acb
bac
bca
cab
cba
6
=== hidden
z
---
z
1
=== hidden
dcba

## Hints
- Sort `s` (n ≤ 8, so insertion sort is fine).
- `void gen(int depth)`: if `depth == n`, print the buffer; otherwise for each `i` with `!used[i]`, set `buf[depth] = s[i]`, mark it used, recurse, then unmark it.
- The count is n!, but count the leaves as you print them.

## Solution
Sorting the input and always trying letters in increasing order makes the depth-first enumeration come out in lexicographic order. The `used` array is the state that gets set and undone around each recursive call, which is the essence of backtracking.

```c
#include <stdio.h>
#include <string.h>

static char s[16], buf[16];
static int used[16], n, count;

static void gen(int depth) {
    if (depth == n) {
        buf[n] = '\0';
        puts(buf);
        count++;
        return;
    }
    for (int i = 0; i < n; i++) {
        if (used[i]) continue;
        used[i] = 1;
        buf[depth] = s[i];
        gen(depth + 1);
        used[i] = 0;
    }
}

int main(void) {
    scanf("%15s", s);
    n = (int)strlen(s);
    for (int i = 1; i < n; i++) {
        char key = s[i];
        int j = i - 1;
        while (j >= 0 && s[j] > key) { s[j + 1] = s[j]; j--; }
        s[j + 1] = key;
    }
    gen(0);
    printf("%d\n", count);
    return 0;
}
```

The recursion depth is only n (≤ 8), but the number of leaves is n! = 40,320. Exponential output is unavoidable here. For "next permutation" without recursion, see the classic O(n) algorithm behind `std::next_permutation` in C++.
