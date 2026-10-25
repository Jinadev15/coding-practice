---
id: c-m3-astar-planner
title: A* Path Planning on Weighted Occupancy Grids
difficulty: Expert
order: 1
tags: A*, binary heap, graphs, robotics, heuristics, dynamic memory
time_limit: 4
---
## Statement
Implement the global planner of a mobile robot: **A\*** on an 8-connected occupancy grid with terrain costs.

`long long plan(const char *grid, int H, int W)` receives `H*W` characters, row-major:
- `#` is an obstacle.
- `S` and `G` are the start and goal (exactly one of each, both with cost 1).
- `.` is free terrain with cost 1, and `1`–`9` are free terrain with that cost.

Moves:
- Moving **into** a cell with cost `c` costs `10·c` orthogonally and `14·c` diagonally.
- A diagonal move is allowed only if **both** orthogonally adjacent cells are free (no corner cutting).

Return the **minimum total cost** from S to G, or **-1** if G is unreachable. Grids reach 2000×2000. An O(N log N) priority-queue search is required. An admissible heuristic (octile distance) makes it much faster, but Dijkstra also passes.

## Starter
```c
#include <stdlib.h>

long long plan(const char *grid, int H, int W) {
    /* BFS on unit costs: wrong for weights and diagonals */
    int n = H * W, s = -1, g = -1;
    for (int i = 0; i < n; i++) { if (grid[i] == 'S') s = i; if (grid[i] == 'G') g = i; }
    int *dist = malloc(sizeof(int) * n), *q = malloc(sizeof(int) * n), h = 0, t = 0;
    for (int i = 0; i < n; i++) dist[i] = -1;
    dist[s] = 0; q[t++] = s;
    while (h < t) {
        int u = q[h++], r = u / W, c = u % W;
        int dr[] = {1, -1, 0, 0}, dc[] = {0, 0, 1, -1};
        for (int k = 0; k < 4; k++) {
            int nr = r + dr[k], nc = c + dc[k];
            if (nr < 0 || nc < 0 || nr >= H || nc >= W || grid[nr * W + nc] == '#') continue;
            int v = nr * W + nc;
            if (dist[v] < 0) { dist[v] = dist[u] + 10; q[t++] = v; }
        }
    }
    long long ans = dist[g];
    free(dist); free(q);
    return ans;
}
```

## Driver
```c
#include <stdio.h>
#include <string.h>

static char *gen(int H, int W, unsigned seed, int density, int weighted) {
    char *g = malloc((size_t)H * W + 1);
    unsigned x = seed;
    for (int i = 0; i < H * W; i++) {
        x = x * 1103515245u + 12345u;
        int r = (x >> 16) % 100;
        g[i] = r < density ? '#' : (weighted ? (char)('1' + (x >> 8) % 9) : '.');
    }
    g[0] = 'S'; g[(size_t)H * W - 1] = 'G';
    if (W > 1) g[1] = '.';
    if (H > 1) g[W] = '.';
    g[(size_t)H * W] = 0;
    return g;
}

int main(void) {
    char cmd[16];
    while (scanf("%15s", cmd) == 1) {
        if (!strcmp(cmd, "grid")) {
            int H, W; if (scanf("%d %d", &H, &W) != 2) return 1;
            char *g = malloc((size_t)H * W + 1), row[4096];
            for (int r = 0; r < H; r++) { if (scanf("%4095s", row) != 1) return 1; memcpy(g + (size_t)r * W, row, (size_t)W); }
            printf("%lld\n", plan(g, H, W));
            free(g);
        } else if (!strcmp(cmd, "gen")) {
            int H, W, d, w; unsigned seed;
            if (scanf("%d %d %u %d %d", &H, &W, &seed, &d, &w) != 5) return 1;
            char *g = gen(H, W, seed, d, w);
            printf("%lld\n", plan(g, H, W));
            free(g);
        }
    }
    return 0;
}
```

## Tests
=== sample
grid 3 4
S...
.##.
...G
grid 3 3
S#G
.#.
...
---
50
60
=== hidden
grid 3 3
S#.
#..
..G
grid 1 2
SG
grid 2 2
S#
#G
grid 4 6
S.....
.####.
.9....
....#G
---
-1
10
-1
80
=== hidden
grid 5 5
S1111
19991
19G91
19991
11111
grid 3 5
S.#..
..#..
..#.G
---
114
-1
=== hidden
gen 300 300 7 25 0
gen 300 300 11 30 1
gen 50 50 3 60 0
---
4958
20544
-1
=== hidden
gen 2000 2000 42 20 1
---
106642
=== hidden
gen 2000 2000 5 33 0
---
-1

## Hints
- Keep `long long g[n]`, initialised to "infinity", and a binary min-heap of `(f = g + h, node)` pairs. Use **lazy deletion**: pop an entry, and skip it if its `g` is stale.
- Octile heuristic with the minimum cell cost of 1: `h = 10*max(dx,dy) + 4*min(dx,dy)`, since `14 = 10 + 4`. It never overestimates.
- No corner cutting: for a diagonal step `(dr, dc)`, both `(r+dr, c)` and `(r, c+dc)` must be free.
- Stop as soon as the goal is **popped**, not when it's first pushed.

## Solution
```c
#include <stdlib.h>

typedef struct { long long f; int v; } HeapItem;
typedef struct { HeapItem *a; size_t n, cap; } Heap;

static int heap_push(Heap *h, long long f, int v) {
    if (h->n == h->cap) {
        size_t nc = h->cap ? h->cap * 2 : 1024;
        HeapItem *na = realloc(h->a, nc * sizeof *na);
        if (!na) return 0;
        h->a = na; h->cap = nc;
    }
    size_t i = h->n++;
    while (i > 0 && h->a[(i - 1) / 2].f > f) { h->a[i] = h->a[(i - 1) / 2]; i = (i - 1) / 2; }
    h->a[i] = (HeapItem){ f, v };
    return 1;
}

static HeapItem heap_pop(Heap *h) {
    HeapItem top = h->a[0], last = h->a[--h->n];
    size_t i = 0;
    for (;;) {
        size_t l = 2 * i + 1, r = l + 1, m = i;
        long long mf = last.f;
        if (l < h->n && h->a[l].f < mf) { m = l; mf = h->a[l].f; }
        if (r < h->n && h->a[r].f < mf) { m = r; }
        if (m == i) break;
        h->a[i] = h->a[m];
        i = m;
    }
    if (h->n) h->a[i] = last;
    return top;
}

static int cost_of(char ch) { return ch >= '1' && ch <= '9' ? ch - '0' : 1; }

long long plan(const char *grid, int H, int W) {
    const int n = H * W;
    int s = -1, goal = -1;
    for (int i = 0; i < n; i++) { if (grid[i] == 'S') s = i; else if (grid[i] == 'G') goal = i; }
    if (s < 0 || goal < 0) return -1;
    long long *g = malloc(sizeof *g * (size_t)n);
    if (!g) return -1;
    for (int i = 0; i < n; i++) g[i] = -1;          /* -1 = unvisited */
    const int gr = goal / W, gc = goal % W;
    Heap heap = {0};
    g[s] = 0;
    {
        int dx = abs(s % W - gc), dy = abs(s / W - gr);
        heap_push(&heap, 10LL * (dx > dy ? dx : dy) + 4LL * (dx < dy ? dx : dy), s);   /* f(start) = h(start) */
    }
    long long answer = -1;
    static const int DR[8] = {1, -1, 0, 0, 1, 1, -1, -1}, DC[8] = {0, 0, 1, -1, 1, -1, 1, -1};
    while (heap.n) {
        HeapItem it = heap_pop(&heap);
        int u = it.v, r = u / W, c = u % W;
        int dx = abs(c - gc), dy = abs(r - gr);
        long long hu = 10LL * (dx > dy ? dx : dy) + 4LL * (dx < dy ? dx : dy);
        if (it.f != g[u] + hu) continue;            /* stale heap entry */
        if (u == goal) { answer = g[u]; break; }
        for (int k = 0; k < 8; k++) {
            int nr = r + DR[k], nc = c + DC[k];
            if (nr < 0 || nc < 0 || nr >= H || nc >= W) continue;
            int v = nr * W + nc;
            if (grid[v] == '#') continue;
            int diag = k >= 4;
            if (diag && (grid[nr * W + c] == '#' || grid[r * W + nc] == '#')) continue;   /* no corner cutting */
            long long ng = g[u] + (long long)cost_of(grid[v]) * (diag ? 14 : 10);
            if (g[v] < 0 || ng < g[v]) {
                g[v] = ng;
                int vx = abs(nc - gc), vy = abs(nr - gr);
                long long hv = 10LL * (vx > vy ? vx : vy) + 4LL * (vx < vy ? vx : vy);
                if (!heap_push(&heap, ng + hv, v)) { answer = -1; goto done; }
            }
        }
    }
done:
    free(heap.a);
    free(g);
    return answer;
}
```

- **A\*** expands nodes in order of `f = g + h`. With a consistent heuristic, the first time the goal is popped its `g` is optimal.
- **The octile heuristic** (`10·max + 4·min`) is the exact cost on an empty unit-cost grid, so it's admissible and consistent when every cell costs at least 1. On open terrain it cuts expansions dramatically compared with Dijkstra (`h = 0`).
- **Lazy deletion** avoids a decrease-key operation: outdated heap entries are recognised (`f != g + h`) and skipped. That's simpler and usually faster than an indexed heap.
- **No corner cutting** matches how a real robot's footprint behaves. Squeezing diagonally between two obstacles would collide.
- **Integer costs** (10/14 for 1/√2) keep comparisons exact and results deterministic. The approximation error is 1%, which is standard in game and robotics grid planners.
