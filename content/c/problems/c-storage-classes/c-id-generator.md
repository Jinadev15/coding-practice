---
id: c-id-generator
title: Static State: ID Generator
difficulty: Medium
order: 1
tags: static locals, internal linkage
---
## Statement
Implement an ID generator with **hidden state** (no globals visible to the driver):

- `int next_id(const char *prefix)` returns a sequence number **per distinct prefix**, starting at 1 (`"robot"` → 1, 2, 3…; `"cam"` has its own counter starting at 1). At most 16 distinct prefixes, each at most 15 characters.
- `int total_ids(void)` returns how many IDs have been issued overall.
- `void reset_ids(void)` resets everything.

Keep the state in `static` variables at file scope (internal linkage) or as static locals. The driver reads commands.

## Starter
```c
#include <string.h>

int next_id(const char *prefix) {
    return 0;
}

int total_ids(void) {
    return 0;
}

void reset_ids(void) {
}
```

## Driver
```c
#include <stdio.h>
#include <string.h>
int main(void) {
    char cmd[16], arg[16];
    while (scanf("%15s", cmd) == 1) {
        if (strcmp(cmd, "id") == 0) { scanf("%15s", arg); printf("%s-%d\n", arg, next_id(arg)); }
        else if (strcmp(cmd, "total") == 0) printf("total %d\n", total_ids());
        else if (strcmp(cmd, "reset") == 0) reset_ids();
    }
    return 0;
}
```

## Tests
=== sample
id robot
id robot
id cam
id robot
total
---
robot-1
robot-2
cam-1
robot-3
total 4
=== hidden
total
id a
reset
id a
id b
total
---
total 0
a-1
a-1
b-1
total 2

## Hints
- `static char names[16][16]; static int counts[16]; static int used = 0, total = 0;`.
- Find the prefix with `strcmp`. If it's missing, copy it into the next slot (`strcpy`, which is safe here because the length is bounded by the driver's `%15s`).

## Solution
```c
#include <string.h>

static char names[16][16];
static int counts[16];
static int used = 0;
static int total = 0;

int next_id(const char *prefix) {
    for (int i = 0; i < used; i++) {
        if (strcmp(names[i], prefix) == 0) {
            total++;
            return ++counts[i];
        }
    }
    strcpy(names[used], prefix);
    counts[used] = 1;
    used++;
    total++;
    return 1;
}

int total_ids(void) {
    return total;
}

void reset_ids(void) {
    used = 0;
    total = 0;
}
```

The `static` at file scope means no other `.c` file can touch `names` or `counts`: only the three functions form the interface. This is module-level encapsulation in C, and it's how `rand()` keeps its seed. The trade-off is that there's exactly **one** generator per program and it isn't thread-safe. The OOP-in-C module fixes that by putting the state in a struct handed to each function.
