---
id: c-knapsack-lis
title: "DP Workshop: Knapsack Counting, LIS Counting, Edit Distance"
difficulty: Hard
order: 1
tags: dynamic programming, knapsack, LIS, Fenwick tree, edit distance, modular counting
time_limit: 3
---
## Statement
A robot's mission planner needs three dynamic-programming engines. The input is a sequence of tasks. Process each one and print one line per task.

**`knapsack W n`**, followed by n lines `weight value` (1 ≤ weight ≤ W ≤ 100 000, n ≤ 300, 1 ≤ value ≤ 10⁶). Each item is used at most once. Print:

`knapsack: best V min_weight X ways C`

- V is the maximum total value with total weight ≤ W.
- X is the smallest total weight of any subset achieving V.
- C is the number of distinct subsets achieving V, modulo 1 000 000 007.
- If no item fits, V = 0, X = 0 and C = 1 (the empty set).

**`lis n`**, followed by n integers, or **`lisgen n x`**, which defines the sequence a₁ = x, aᵢ₊₁ = (aᵢ · 1103515245 + 12345) mod 2³¹, using the values aᵢ mod 1 000 000. For the **strictly increasing** subsequences, print:

`lis: length L count C`

- L is the length of the longest such subsequence.
- C is how many index sequences achieve length L, modulo 1 000 000 007.

n is up to 300 000, so O(n²) is too slow. You need an O(n log n) method.

**`edit s t`**: two non-empty lowercase words (each ≤ 5000 characters). Print `edit: D`, where D is the Levenshtein distance (insert, delete and substitute each cost 1).

## Starter
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(void) {
    char cmd[16];
    while (scanf("%15s", cmd) == 1) {
        /* TODO */
    }
    return 0;
}
```

## Tests
=== sample
knapsack 10 4
5 10
4 40
6 30
3 50
lis 8
10 9 2 5 3 7 101 18
edit kitten sitting
knapsack 5 3
1 1
2 2
3 3
---
knapsack: best 90 min_weight 7 ways 1
lis: length 4 count 4
edit: 3
knapsack: best 5 min_weight 5 ways 1
=== hidden
knapsack 3 2
5 100
4 50
knapsack 6 4
2 3
2 3
2 3
4 6
lis 1
42
lis 5
5 4 3 2 1
lis 6
1 1 1 2 2 2
lis 7
1 3 5 4 7 2 8
edit a a
edit abc xyz
edit intention execution
edit ab abab
knapsack 100000 5
50000 1000000
50000 1000000
50000 1000000
100000 2000000
1 1
---
knapsack: best 0 min_weight 0 ways 1
knapsack: best 9 min_weight 6 ways 4
lis: length 1 count 1
lis: length 1 count 5
lis: length 2 count 9
lis: length 5 count 2
edit: 0
edit: 3
edit: 5
edit: 2
knapsack: best 2000000 min_weight 100000 ways 4
=== hidden
lisgen 300000 12345
lisgen 250000 1
knapsack 100000 300
30344 643003
24466 280111
9080 195188
422 354761
32951 486248
39630 84741
21891 581195
2681 763565
24840 177644
29624 997481
27695 164792
11039 249574
3365 116337
8679 530862
38695 66404
25144 827951
6664 963595
19083 214917
14700 760959
27641 932789
5749 810110
17481 955651
13756 415806
18428 358257
2831 209174
346 922090
26948 57451
24827 886893
32225 145902
1539 248233
27835 771997
7344 625839
254 127122
37926 207273
13308 346258
541 935829
5473 139653
35375 962234
1145 525131
5560 600812
32555 563702
12988 440515
4511 417475
12594 669744
6123 734893
37998 152419
11309 985364
39905 754593
2701 56805
17695 582024
39740 893374
9785 781347
17585 772678
37702 35902
7952 910857
26370 997115
15519 169597
33090 45122
23983 886745
34214 618932
37044 812254
5685 909505
22754 115308
38283 383327
29577 220234
26357 208428
37647 781923
1204 397352
39830 344680
41 454634
7321 223795
14530 465583
17671 340483
5821 322074
18671 108077
33916 822188
3616 26625
24995 818646
36729 846778
28092 521489
22681 743911
16271 593522
4344 445653
15136 100428
26274 534646
24443 901673
36731 387303
9119 699931
19025 179370
16969 30802
3310 985107
11322 275735
10762 126105
39752 155525
779 51199
3992 472319
13671 824788
25486 308532
970 837484
23235 298856
9218 504278
36827 291218
8999 90795
36436 310390
7729 68784
27521 473328
9341 738034
36827 801291
25101 616745
11081 695404
17968 809192
39144 923016
39878 518454
22864 104047
3176 290300
34658 134579
11360 837195
5523 170106
14576 900842
853 212750
11525 496644
29931 620258
36651 572005
25447 87238
11341 575270
31593 621734
17200 561439
4364 987012
1886 609241
38356 932178
28558 570797
20235 548925
34537 563216
4298 920046
37610 568487
19682 67444
14700 755684
9009 108224
6529 733501
32222 475563
3962 514029
3471 711766
39513 30623
24455 255477
30058 242332
24329 863106
37564 655346
32501 918395
15933 37748
39123 88743
3075 710994
26855 426432
38572 72315
5292 198276
2236 637656
11883 88514
4252 31314
23252 654941
30818 573589
35100 497681
1703 737720
4936 350046
5545 820848
21069 8987
30399 470976
38683 155798
25303 501466
9038 111396
22857 703843
15160 473415
8481 201498
14494 114059
7249 55293
7871 78259
5411 390519
6791 777054
1538 490220
34211 210428
24215 916799
5318 247625
359 268818
33937 715950
12935 16234
28788 265568
1458 108270
34043 838830
27339 60612
16466 498680
20651 634654
14464 669981
3842 714283
18035 138654
19671 40781
12235 370611
26426 975890
476 919156
19840 900879
6188 30899
20820 460661
16200 436814
39595 337379
32225 590758
22738 923615
26155 450976
13693 82372
18114 315504
30262 489277
37254 478056
28832 403726
12212 345481
26357 61739
21301 96287
11179 332938
35644 28169
12358 221352
23895 690763
9024 989564
5631 354258
29300 636020
39290 798600
25223 221495
35517 808850
21979 79549
1254 702309
36207 442314
30842 238393
21214 801059
33695 526751
6495 485739
210 298486
34964 215081
4681 234609
708 965727
20621 44062
5996 156355
21533 171232
6295 534370
26462 680719
25917 408335
38441 530797
8838 533437
23424 376433
17690 211799
21001 959479
25235 594872
11956 838351
11675 598498
11243 9910
20056 717445
1319 292048
31378 547928
27993 952328
6144 286060
18675 150693
33878 473409
31380 712815
15209 187787
21696 153795
22784 779742
39381 53313
35745 292120
22566 27502
37917 195463
35243 816362
6329 475481
8818 357284
13815 784160
35595 140889
27708 227103
33775 212671
37265 443650
657 887808
36367 51763
23256 520309
24385 63863
24405 847390
26120 929754
30383 458627
12500 582986
6472 962469
10883 615969
5564 934223
23242 272833
16196 804688
30774 551052
12212 797892
34811 12631
35378 351763
14612 181724
1842 59237
38444 609291
13131 689157
22204 297291
8505 346293
19507 414811
2364 80093
26596 861853
16082 476087
30429 728394
2748 329645
---
lis: length 1091 count 336093163
lis: length 992 count 902380325
knapsack: best 25330166 min_weight 99743 ways 1
=== hidden
lisgen 100000 777
lis 12
1 2 3 4 5 6 1 2 3 4 5 6
---
lis: length 624 count 67195522
lis: length 6 count 7

## Hints
- **Knapsack counting**: keep `best[w]` = the best value with total weight **exactly** w (−1 if unreachable) and `cnt[w]` = how many subsets reach it. For each item, run w from W down to the weight: if `best[w-wt] + v` beats `best[w]`, copy the count; if it ties, add the count. At the end, V is the max over w, X is the first w reaching it, and C is the sum of `cnt[w]` over every w with `best[w] == V`.
- **LIS counting** in O(n log n): compress the values to ranks and keep a Fenwick tree over ranks that stores pairs `(len, count)` for prefix maxima. For each element with rank r, query ranks `< r`: you get `(L, C)`, then insert `(L + 1, C)`, or `(1, 1)` if L = 0, at r. When combining two pairs, the larger len wins, and equal lens add their counts.
- `lisgen` overflows 32 bits: compute in `unsigned long long` and take `& 0x7FFFFFFF`.
- Edit distance: two rolling rows of `int`.

## Solution
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MOD 1000000007LL

static void knapsack(void) {
    int W, n;
    if (scanf("%d %d", &W, &n) != 2) return;
    long long *best = malloc((size_t)(W + 1) * sizeof *best);
    long long *cnt = calloc((size_t)W + 1, sizeof *cnt);
    for (int w = 0; w <= W; w++) best[w] = -1;
    best[0] = 0; cnt[0] = 1;
    for (int i = 0; i < n; i++) {
        int wt; long long v;
        if (scanf("%d %lld", &wt, &v) != 2) return;
        for (int w = W; w >= wt; w--) {
            if (best[w - wt] < 0) continue;
            long long cand = best[w - wt] + v;
            if (cand > best[w]) { best[w] = cand; cnt[w] = cnt[w - wt]; }
            else if (cand == best[w]) cnt[w] = (cnt[w] + cnt[w - wt]) % MOD;
        }
    }
    long long V = 0, ways = 0; int minw = -1;
    for (int w = 0; w <= W; w++) if (best[w] > V) V = best[w];
    for (int w = 0; w <= W; w++)
        if (best[w] == V) { if (minw < 0) minw = w; ways = (ways + cnt[w]) % MOD; }
    printf("knapsack: best %lld min_weight %d ways %lld\n", V, minw, ways);
    free(best); free(cnt);
}

typedef struct { int len; long long cnt; } Pair;

static Pair better(Pair a, Pair b) {
    if (a.len != b.len) return a.len > b.len ? a : b;
    return (Pair){a.len, (a.cnt + b.cnt) % MOD};
}

static int cmp_int(const void *pa, const void *pb) {
    int a = *(const int *)pa, b = *(const int *)pb;
    return (a > b) - (a < b);
}

static void lis(int *a, size_t n) {
    int *sorted = malloc(n * sizeof *sorted);
    memcpy(sorted, a, n * sizeof *a);
    qsort(sorted, n, sizeof *sorted, cmp_int);
    size_t m = 0;                                            /* unique values */
    for (size_t i = 0; i < n; i++) if (m == 0 || sorted[m - 1] != sorted[i]) sorted[m++] = sorted[i];
    Pair *bit = calloc(m + 1, sizeof *bit);                  /* Fenwick tree of prefix "best" pairs */
    for (size_t i = 0; i < n; i++) {
        size_t lo = 0, hi = m;                               /* rank = lower_bound + 1 (1-based) */
        while (lo < hi) { size_t mid = lo + (hi - lo) / 2; if (sorted[mid] < a[i]) lo = mid + 1; else hi = mid; }
        size_t r = lo + 1;
        Pair q = {0, 0};
        for (size_t j = r - 1; j > 0; j -= j & -j) q = better(q, bit[j]);   /* ranks < r: strictly smaller */
        Pair cur = q.len == 0 ? (Pair){1, 1} : (Pair){q.len + 1, q.cnt};
        for (size_t j = r; j <= m; j += j & -j) bit[j] = better(bit[j], cur);
    }
    Pair all = {0, 0};
    for (size_t j = m; j > 0; j -= j & -j) all = better(all, bit[j]);
    printf("lis: length %d count %lld\n", all.len, all.cnt);
    free(sorted); free(bit);
}

static char s[5001], t[5001];

static void edit(void) {
    if (scanf("%5000s %5000s", s, t) != 2) return;
    size_t n = strlen(s), m = strlen(t);
    int *prev = malloc((m + 1) * sizeof *prev), *cur = malloc((m + 1) * sizeof *cur);
    for (size_t j = 0; j <= m; j++) prev[j] = (int)j;
    for (size_t i = 1; i <= n; i++) {
        cur[0] = (int)i;
        for (size_t j = 1; j <= m; j++) {
            int best = prev[j - 1] + (s[i - 1] != t[j - 1]);
            if (prev[j] + 1 < best) best = prev[j] + 1;
            if (cur[j - 1] + 1 < best) best = cur[j - 1] + 1;
            cur[j] = best;
        }
        int *tmp = prev; prev = cur; cur = tmp;
    }
    printf("edit: %d\n", prev[m]);
    free(prev); free(cur);
}

int main(void) {
    char cmd[16];
    while (scanf("%15s", cmd) == 1) {
        if (!strcmp(cmd, "knapsack")) knapsack();
        else if (!strcmp(cmd, "edit")) edit();
        else if (!strcmp(cmd, "lis") || !strcmp(cmd, "lisgen")) {
            size_t n;
            if (scanf("%zu", &n) != 1) return 1;
            int *a = malloc(n * sizeof *a);
            if (!strcmp(cmd, "lis")) {
                for (size_t i = 0; i < n; i++) if (scanf("%d", &a[i]) != 1) return 1;
            } else {
                unsigned long long x;
                if (scanf("%llu", &x) != 1) return 1;
                for (size_t i = 0; i < n; i++) {
                    a[i] = (int)(x % 1000000);
                    x = (x * 1103515245ULL + 12345ULL) & 0x7FFFFFFFULL;
                }
            }
            lis(a, n);
            free(a);
        }
    }
    return 0;
}
```

How each engine works:
- **Knapsack** uses exact-weight states, which makes counting well defined. Iterating the weight downwards keeps each item 0/1. Any subset with the optimal value V lands in some `best[w] == V` state, so summing those counts gives every optimal subset exactly once. That's O(nW) time and O(W) memory.
- **LIS counting** is O(n log n). A Fenwick tree indexed by value rank answers "the best (length, count) among all earlier elements with a smaller value" in O(log n). Strictness comes from querying ranks `< r`, so equal values never extend each other. The classic patience-sorting method finds the length in O(n log n) too, but counting needs this richer structure.
- **Edit distance** is the Wagner–Fischer recurrence with two rolling rows, so O(nm) time and O(m) memory.
