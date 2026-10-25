---
id: cpp-hanoi-kth-move
title: Tower of Hanoi and Its k-th Move
difficulty: Medium
order: 2
tags: recursion, divide and conquer, Tower of Hanoi
time_limit: 1
---
## Statement
Disks `1..n` (1 is the smallest) start on peg `A`. Move them all to peg `C` using peg `B`, never placing a larger disk on a smaller one, with the minimum number of moves (2ⁿ − 1). Implement the classic recursion and two more functions:

```cpp
void hanoi(int n, char from, char via, char to, std::vector<std::string>& moves);
    // append every move as "d:X->Y" (disk number, from peg, to peg), in order
unsigned long long move_count(int n);                 // 2^n - 1, for n <= 63
std::string kth_move(int n, unsigned long long k);    // the k-th move (1-based) of the optimal solution
                                                      //   A -> C, without generating all the moves
```

For `kth_move`, n can be 60, so the full list would have about 10¹⁸ moves. Use the structure of the recursion instead: the first `2^(n−1) − 1` moves are the solution for `n−1` disks from A to B, the next move is disk `n` from A to C, and the rest is the solution for `n−1` disks from B to C.

**Input:** commands until the end of input: `list n` (n ≤ 10), `count n` (n ≤ 63), `kth n k` (n ≤ 60, 1 ≤ k ≤ 2ⁿ − 1).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

void hanoi(int n, char from, char via, char to, vector<string>& moves) {}
unsigned long long move_count(int n) { return 0; }
string kth_move(int n, unsigned long long k) { return ""; }
```

## Driver
```cpp
int main() {
    string cmd;
    while (cin >> cmd) {
        int n; cin >> n;
        if (cmd == "list") {
            vector<string> m; hanoi(n, 'A', 'B', 'C', m);
            cout << m.size() << " moves:";
            for (auto& s : m) cout << ' ' << s;
            cout << '\n';
        } else if (cmd == "count") {
            cout << move_count(n) << '\n';
        } else {
            unsigned long long k; cin >> k;
            cout << kth_move(n, k) << '\n';
        }
    }
}
```

## Tests
=== sample
list 2
list 3
count 3
kth 3 4
kth 3 7
---
3 moves: 1:A->B 2:A->C 1:B->C
7 moves: 1:A->C 2:A->B 1:C->B 3:A->C 1:B->A 2:B->C 1:A->C
7
3:A->C
1:A->C
=== hidden
list 1
count 1
count 63
kth 1 1
---
1 moves: 1:A->C
1
9223372036854775807
1:A->C
=== hidden
kth 60 1
kth 60 576460752303423488
kth 60 1152921504606846975
kth 60 123456789012345678
---
1:A->B
60:A->C
1:B->C
2:C->B
=== hidden
list 10
kth 10 512
kth 10 1000
=== hidden
list 9
count 6
kth 5 6
kth 10 298
count 6
count 12
kth 1 1
kth 7 51
kth 6 25
kth 3 1
kth 7 126
kth 11 992
kth 2 2
kth 5 25
count 12
=== hidden
list 9
list 10
list 4
count 11
kth 10 371
list 3
kth 1 1
list 2
kth 4 14
kth 3 7
list 4
list 2
kth 3 7
kth 7 74
kth 1 1
=== hidden
kth 3 5
kth 11 691
list 8
kth 2 3
kth 6 47
kth 2 1
count 11
kth 6 59
list 2
kth 12 1743
kth 2 3
kth 4 12
list 5
list 2
kth 11 62
---
1:B->A
1:A->C
255 moves: 1:A->B 2:A->C 1:B->C 3:A->B 1:C->A 2:C->B 1:A->B 4:A->C 1:B->C 2:B->A 1:C->A 3:B->C 1:A->B 2:A->C 1:B->C 5:A->B 1:C->A 2:C->B 1:A->B 3:C->A 1:B->C 2:B->A 1:C->A 4:C->B 1:A->B 2:A->C 1:B->C 3:A->B 1:C->A 2:C->B 1:A->B 6:A->C 1:B->C 2:B->A 1:C->A 3:B->C 1:A->B 2:A->C 1:B->C 4:B->A 1:C->A 2:C->B 1:A->B 3:C->A 1:B->C 2:B->A 1:C->A 5:B->C 1:A->B 2:A->C 1:B->C 3:A->B 1:C->A 2:C->B 1:A->B 4:A->C 1:B->C 2:B->A 1:C->A 3:B->C 1:A->B 2:A->C 1:B->C 7:A->B 1:C->A 2:C->B 1:A->B 3:C->A 1:B->C 2:B->A 1:C->A 4:C->B 1:A->B 2:A->C 1:B->C 3:A->B 1:C->A 2:C->B 1:A->B 5:C->A 1:B->C 2:B->A 1:C->A 3:B->C 1:A->B 2:A->C 1:B->C 4:B->A 1:C->A 2:C->B 1:A->B 3:C->A 1:B->C 2:B->A 1:C->A 6:C->B 1:A->B 2:A->C 1:B->C 3:A->B 1:C->A 2:C->B 1:A->B 4:A->C 1:B->C 2:B->A 1:C->A 3:B->C 1:A->B 2:A->C 1:B->C 5:A->B 1:C->A 2:C->B 1:A->B 3:C->A 1:B->C 2:B->A 1:C->A 4:C->B 1:A->B 2:A->C 1:B->C 3:A->B 1:C->A 2:C->B 1:A->B 8:A->C 1:B->C 2:B->A 1:C->A 3:B->C 1:A->B 2:A->C 1:B->C 4:B->A 1:C->A 2:C->B 1:A->B 3:C->A 1:B->C 2:B->A 1:C->A 5:B->C 1:A->B 2:A->C 1:B->C 3:A->B 1:C->A 2:C->B 1:A->B 4:A->C 1:B->C 2:B->A 1:C->A 3:B->C 1:A->B 2:A->C 1:B->C 6:B->A 1:C->A 2:C->B 1:A->B 3:C->A 1:B->C 2:B->A 1:C->A 4:C->B 1:A->B 2:A->C 1:B->C 3:A->B 1:C->A 2:C->B 1:A->B 5:C->A 1:B->C 2:B->A 1:C->A 3:B->C 1:A->B 2:A->C 1:B->C 4:B->A 1:C->A 2:C->B 1:A->B 3:C->A 1:B->C 2:B->A 1:C->A 7:B->C 1:A->B 2:A->C 1:B->C 3:A->B 1:C->A 2:C->B 1:A->B 4:A->C 1:B->C 2:B->A 1:C->A 3:B->C 1:A->B 2:A->C 1:B->C 5:A->B 1:C->A 2:C->B 1:A->B 3:C->A 1:B->C 2:B->A 1:C->A 4:C->B 1:A->B 2:A->C 1:B->C 3:A->B 1:C->A 2:C->B 1:A->B 6:A->C 1:B->C 2:B->A 1:C->A 3:B->C 1:A->B 2:A->C 1:B->C 4:B->A 1:C->A 2:C->B 1:A->B 3:C->A 1:B->C 2:B->A 1:C->A 5:B->C 1:A->B 2:A->C 1:B->C 3:A->B 1:C->A 2:C->B 1:A->B 4:A->C 1:B->C 2:B->A 1:C->A 3:B->C 1:A->B 2:A->C 1:B->C
1:B->C
1:C->A
1:A->B
2047
1:C->A
3 moves: 1:A->B 2:A->C 1:B->C
1:B->C
1:B->C
3:B->C
31 moves: 1:A->C 2:A->B 1:C->B 3:A->C 1:B->A 2:B->C 1:A->C 4:A->B 1:C->B 2:C->A 1:B->A 3:C->B 1:A->C 2:A->B 1:C->B 5:A->C 1:B->A 2:B->C 1:A->C 3:B->A 1:C->B 2:C->A 1:B->A 4:B->C 1:A->C 2:A->B 1:C->B 3:A->C 1:B->A 2:B->C 1:A->C
3 moves: 1:A->B 2:A->C 1:B->C
2:A->B
=== hidden
kth 33 1785564143
count 15
count 35
kth 44 15743231548620
kth 49 86539023846777
kth 17 46120
kth 32 863697258
kth 14 6067
kth 9 39
kth 44 4537756938367
kth 5 29
kth 51 771702068816576
kth 57 133096263631634685
kth 47 2052511717227
kth 16 59960
---
1:B->A
32767
34359738367
3:B->C
1:C->B
4:C->A
2:C->B
1:A->B
1:C->B
1:A->B
1:B->A
7:B->A
1:C->B
1:C->B
4:A->C
=== hidden
kth 34 16127847293
count 27
kth 5 19
count 36
count 56
count 31
count 12
kth 44 15581338217831
kth 57 127600470464425820
kth 57 60000623644664435
count 21
count 55
count 36
kth 1 1
kth 14 4972
---
1:C->A
134217727
1:A->C
68719476735
72057594037927935
2147483647
4095
1:C->A
3:B->A
1:B->A
2097151
36028797018963967
68719476735
1:A->C
3:A->B
=== hidden
kth 27 18882300
kth 7 32
count 11
kth 14 11502
kth 46 68461404208530
kth 50 2356900844007
count 48
kth 54 5619184583371938
kth 16 20809
kth 42 751746541876
kth 42 1710315077294
kth 3 2
kth 42 3202063027055
kth 33 4803535312
count 45
---
3:C->B
6:A->B
2047
2:C->B
2:C->B
1:B->C
281474976710655
2:C->B
1:A->B
3:A->B
2:A->C
2:A->B
1:C->A
5:A->C
35184372088831

## Hints
- `hanoi(n)` = `hanoi(n−1, from→via)`, then move disk `n`, then `hanoi(n−1, via→to)`. Note how the peg arguments change.
- The first sub-solution has exactly `2^(n−1) − 1` moves. Compare `k` with that number.
- In `kth_move`, recurse into only the part that contains `k`, and pass the swapped peg roles exactly as `hanoi` does.

## Solution
**The full list** follows the leap of faith: move `n−1` disks out of the way (A→B), move disk `n` (A→C), then move the `n−1` disks back on top (B→C). The count satisfies `M(n) = 2M(n−1) + 1`, so `M(n) = 2ⁿ − 1`.

**The k-th move** uses the same three-part structure, but descends into only **one** part. With `half = 2^(n−1) − 1`:

- if `k ≤ half`, it's inside the first sub-solution (with the peg roles swapped);
- if `k = half + 1`, it's disk `n` moving from `from` to `to`;
- otherwise it's move `k − half − 1` of the last sub-solution.

That is n levels of recursion: O(n) instead of O(2ⁿ). This "descend into the right part of a recursive structure" trick reappears in segment trees and in finding the k-th element of recursively defined sequences.

Complexity: `hanoi` O(2ⁿ), `kth_move` O(n).

```cpp
#include <bits/stdc++.h>
using namespace std;

void hanoi(int n, char from, char via, char to, vector<string>& moves) {
    if (n == 0) return;
    hanoi(n - 1, from, to, via, moves);                       // clear the way
    moves.push_back(to_string(n) + ":" + from + "->" + to);   // largest disk
    hanoi(n - 1, via, from, to, moves);                       // rebuild on top
}

unsigned long long move_count(int n) {
    return n == 64 ? ~0ULL : (1ULL << n) - 1;
}

static string kth(int n, unsigned long long k, char from, char via, char to) {
    unsigned long long half = (1ULL << (n - 1)) - 1;          // moves of the first sub-solution
    if (k <= half) return kth(n - 1, k, from, to, via);
    if (k == half + 1) return to_string(n) + ":" + from + "->" + to;
    return kth(n - 1, k - half - 1, via, from, to);
}

string kth_move(int n, unsigned long long k) { return kth(n, k, 'A', 'B', 'C'); }
```
