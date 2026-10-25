---
id: cpp-amortized-dynarray
title: A Dynamic Array and Its Amortised Cost
difficulty: Medium
order: 4
tags: amortised analysis, dynamic arrays, memory management, rule of five
time_limit: 1
---
## Statement
Build the growable array that sits behind `std::vector`, and **measure** why `push_back` is amortised O(1).

```cpp
class DynArray {
public:
    void push_back(long long x);
    void pop_back();                      // never called on an empty array
    long long at(std::size_t i) const;    // 0-based
    std::size_t size() const;
    std::size_t capacity() const;
    long long copies() const;             // total elements moved by reallocations so far
};
```

**Growth and shrink policy** (follow it exactly, because the outputs depend on it):

- The array starts with capacity 0.
- **`push_back` when `size == capacity`:** allocate `max(1, 2·capacity)` slots, move the existing `size` elements over (`copies += size`), then append.
- **`pop_back`:** remove the last element. Then, if `size > 0` and `size ≤ capacity / 4` (integer division), shrink to `capacity / 2` slots and move the elements over (`copies += size`).

Manage the memory yourself with `new[]`/`delete[]` (or `std::unique_ptr<long long[]>`). Don't use `std::vector` inside it.

**Input:** a list of commands until the end of input.

- `P k`: push the next `k` values of a counter that starts at 1 (1, 2, 3, …, continuing across commands).
- `O k`: pop `k` times.
- `S`: print `size capacity copies` and the element at index `size/2` (print `-` if the array is empty).

The total number of operations is up to 3·10⁶.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

class DynArray {
    vector<long long> v;     // replace with your own buffer and counters
public:
    void push_back(long long x) { v.push_back(x); }
    void pop_back() { v.pop_back(); }
    long long at(size_t i) const { return v[i]; }
    size_t size() const { return v.size(); }
    size_t capacity() const { return v.capacity(); }
    long long copies() const { return 0; }
};
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    DynArray d;
    long long next = 1;
    char c;
    while (cin >> c) {
        if (c == 'P') { long long k; cin >> k; while (k--) d.push_back(next++); }
        else if (c == 'O') { long long k; cin >> k; while (k--) d.pop_back(); }
        else {
            cout << d.size() << ' ' << d.capacity() << ' ' << d.copies() << ' ';
            if (d.size()) cout << d.at(d.size() / 2) << '\n'; else cout << "-\n";
        }
    }
}
```

## Tests
=== sample
P 5
S
O 4
S
P 1
S
---
5 8 7 3
1 2 10 1
2 2 10 6
=== hidden
S
P 1
S
O 1
S
---
0 0 0 -
1 1 0 1
0 1 0 -
=== hidden
P 1000000
S
O 999999
S
P 1000000
O 1000000
S
---
1000000 1048576 1048575 500001
1 2 1572862 1
1 2 3145723 1
=== hidden
P 8
O 6
S
P 1
O 1
P 1
O 1
S
---
2 4 9 2
2 4 9 2
=== hidden
P 20
S
P 29
P 20
S
P 26
S
P 23
P 4
P 13
O 125
S
P 3
S
P 13
P 12
P 28
P 38
S
O 54
S
P 34
S
P 13
P 23
P 12
S
P 34
O 49
P 7
P 24
S
P 25
S
O 162
O 6
S
P 32
O 7
O 4
P 7
P 20
P 21
S
P 23
P 8
S
O 36
S
P 7
S
P 23
P 26
O 51
S
P 31
S
O 50
P 38
P 7
O 33
S
O 22
S
P 7
S
O 38
O 7
P 40
O 34
O 7
S
P 9
O 9
S
P 22
P 2
P 13
P 39
P 11
O 17
O 61
P 18
S
---
20 32 31 11
69 128 127 35
95 128 127 48
10 32 367 6
13 32 367 7
104 128 463 178
50 128 463 151
84 128 463 168
132 256 591 246
148 256 591 254
173 256 591 266
5 16 711 3
74 128 823 445
105 128 823 460
69 128 823 442
76 128 823 446
74 128 823 445
105 128 823 460
67 128 823 441
45 128 823 419
52 128 823 434
6 16 951 4
6 16 951 4
33 64 1143 789
=== hidden
P 39
P 34
P 12
P 16
O 69
O 2
O 11
O 16
O 2
P 10
S
O 1
O 9
P 29
S
P 33
S
P 27
S
P 22
P 32
O 87
S
P 35
P 3
P 4
O 90
S
O 2
P 18
O 20
S
O 1
P 28
S
P 9
S
O 21
O 19
O 1
P 31
O 31
P 20
P 2
S
P 17
S
P 3
S
P 15
O 35
O 6
P 1
P 7
O 20
S
O 3
S
O 1
S
P 23
P 35
O 52
O 5
S
P 17
P 34
P 11
S
P 3
S
P 13
O 64
O 14
S
O 1
P 40
O 5
P 5
S
S
---
11 16 204 106
30 32 241 126
63 64 273 142
90 128 337 156
57 128 529 139
9 32 577 115
5 16 609 113
32 32 637 327
41 64 669 331
22 32 775 394
39 64 807 402
42 64 807 404
4 8 835 385
1 2 838 383
0 2 838 -
1 2 931 448
63 64 993 536
66 128 1057 538
1 2 1120 448
40 64 1182 604
40 64 1182 604
=== hidden
P 32
O 13
P 38
S
O 16
S
O 32
O 7
S
P 5
S
O 4
P 6
P 9
O 15
P 16
S
P 14
O 2
O 29
O 1
S
O 1
P 39
P 39
O 61
S
P 22
O 29
O 2
P 11
P 27
O 5
O 22
S
P 24
O 10
S
O 6
P 24
P 15
O 46
O 1
S
O 7
P 7
O 19
S
P 38
O 20
O 10
S
P 2
S
O 8
S
P 17
O 18
P 40
O 1
P 29
S
P 25
S
P 35
S
O 95
O 2
S
P 21
O 9
P 15
P 19
O 13
S
O 13
O 12
O 34
S
P 35
S
S
---
57 64 63 42
41 64 63 34
2 4 93 2
7 8 97 72
19 32 157 97
1 2 220 1
17 64 378 129
19 64 450 222
33 64 450 229
19 64 546 222
0 2 577 -
8 16 663 333
10 16 663 334
2 4 669 330
69 128 838 419
94 128 838 433
129 256 966 450
32 64 1062 401
65 128 1126 515
6 16 1182 388
41 64 1230 584
41 64 1230 584
=== hidden
P 87074
P 39433
O 37732
S
P 38941
S
O 94369
O 31761
O 1344
P 96917
P 43284
S
O 74261
S
P 33293
O 53241
O 44850
P 58153
O 27398
S
P 43040
O 21925
S
P 86099
S
P 11381
P 59980
P 14845
P 93438
S
P 82896
P 81176
S
P 31459
O 316122
S
P 76882
O 17438
S
O 190023
O 11061
S
---
88775 131072 131071 44388
127716 131072 131071 63859
140443 262144 457983 235428
66182 262144 457983 198298
32139 65536 648447 353628
53254 131072 713983 364186
139353 262144 845055 456558
318997 524288 1107199 546380
483069 524288 1107199 628416
198406 524288 1107199 486085
257850 524288 1107199 515807
56766 131072 1303807 365942
=== hidden
P 81421
O 23899
S
P 93235
S
P 13990
P 92747
O 40668
O 153383
O 21855
S
P 35776
S
P 67466
S
O 72371
P 56171
S
P 75945
S
O 50774
P 9152
S
O 62866
S
O 98019
P 24038
O 13004
S
P 27678
O 36891
S
P 56380
O 49263
S
P 78740
P 21197
P 57559
O 69158
P 71689
P 29066
S
P 80989
S
---
57522 131072 131071 28762
150757 262144 262143 99278
41588 131072 327679 20795
77364 131072 327679 38683
144830 262144 458751 312221
128630 262144 458751 304121
204575 262144 458751 414464
162953 262144 458751 393653
100087 262144 458751 289849
13102 32768 610303 530387
3889 8192 671743 1945
11006 32768 745471 579234
200099 262144 974847 792201
281088 524288 1236991 832696
=== hidden
P 47824
S
O 47026
O 655
S
O 83
P 69246
P 64115
S
P 70416
S
P 16717
S
O 82335
S
P 2846
O 97465
O 28904
O 9909
O 3900
S
O 14
P 74687
S
P 43451
O 48433
O 26615
S
P 15455
O 44896
S
O 1776
S
P 89761
S
P 22797
O 108523
P 80294
O 74295
S
O 19392
O 236
S
O 178
S
---
47824 65536 65535 23913
143 512 98047 72
133421 262144 360255 114475
203837 262144 360255 149683
220554 262144 360255 158042
138219 262144 360255 116874
887 2048 490303 48208
75560 131072 619327 308072
43963 131072 619327 292273
14522 32768 668479 277553
12746 32768 668479 276665
102507 131072 766783 443265
22780 65536 897855 281682
3152 8192 926527 271868
2974 8192 926527 271779

## Hints
- Keep three numbers: `size`, `capacity` and `copies`, plus a buffer from `new long long[cap]` (or a `unique_ptr<long long[]>`).
- Write one helper that reallocates to a given capacity. It copies `size` elements and adds `size` to `copies`. Both growing and shrinking use it.
- The shrink rule is checked **after** removing the element, and only when `size > 0`. At `size == 0` the capacity stays as it is.

## Solution
A single `reallocate(newcap)` helper allocates the new buffer, moves the `size_` live elements over, counts them, and releases the old buffer. `unique_ptr<long long[]>` frees it automatically.

**Why it's amortised O(1).** Reaching size `n` by pushes costs at most `1 + 2 + 4 + … < 2n` copies. Look at the `copies` column in the outputs: it never exceeds about twice the number of operations.

**Why shrink at a quarter, not a half.** Shrinking at `size ≤ capacity/4` leaves the array half full after a shrink. If you shrank at half, a push/pop sequence right at the boundary could reallocate on *every* operation (thrashing), and the cost would be O(n) per operation.

Complexity: amortised O(1) per push and pop, O(1) for `at`.

```cpp
#include <bits/stdc++.h>
using namespace std;

class DynArray {
    unique_ptr<long long[]> buf_;
    size_t size_ = 0, cap_ = 0;
    long long copies_ = 0;

    void reallocate(size_t newcap) {
        unique_ptr<long long[]> nb(newcap ? new long long[newcap] : nullptr);
        for (size_t i = 0; i < size_; ++i) nb[i] = buf_[i];
        copies_ += (long long)size_;
        buf_ = std::move(nb);
        cap_ = newcap;
    }
public:
    void push_back(long long x) {
        if (size_ == cap_) reallocate(max<size_t>(1, 2 * cap_));
        buf_[size_++] = x;
    }
    void pop_back() {
        --size_;
        if (size_ > 0 && size_ <= cap_ / 4) reallocate(cap_ / 2);
    }
    long long at(size_t i) const { return buf_[i]; }
    size_t size() const { return size_; }
    size_t capacity() const { return cap_; }
    long long copies() const { return copies_; }
};
```
