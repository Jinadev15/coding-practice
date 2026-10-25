---
id: cpp-count-and-say
title: Count and Say
difficulty: Easy
order: 4
tags: recursion, strings, run-length encoding
time_limit: 1
---
## Statement
The **count-and-say** sequence is defined recursively:

- `term(1) = "1"`
- `term(n)` is `term(n−1)` *read aloud*: describe each run of equal digits as *count, then digit*.

So `1 → "one 1" = 11 → "two 1s" = 21 → "one 2, one 1" = 1211 → 111221 → 312211 → …`

```cpp
std::string count_and_say(int n);     // 1 <= n <= 35
```

**Input:** several values of `n`, one per line. For each, print the **length** of `term(n)`, then the term itself if it has at most 80 characters, or its first 40 characters followed by `...` otherwise.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

string count_and_say(int n) {
    return "1";
}
```

## Driver
```cpp
int main() {
    int n;
    while (cin >> n) {
        string s = count_and_say(n);
        cout << s.size() << ' ' << (s.size() <= 80 ? s : s.substr(0, 40) + "...") << '\n';
    }
}
```

## Tests
=== sample
1
4
6
---
1 1
4 1211
6 312211
=== hidden
2
3
10
---
2 11
2 21
20 13211311123113112211
=== hidden
30
35
20
---
4462 3113112221131112311332111213122112311311...
16774 1113122113121113222123211211131211121311...
302 1113122113121113222123211211131211121311...
=== hidden
13
10
15
12
10
3
---
46 1321132132111213122112311311222113111221131221
20 13211311123113112211
78 311311222113111231131112132112311321322112111312211312111322212311322113212221
34 3113112221232112111312211312113211
20 13211311123113112211
2 21
=== hidden
11
13
14
14
1
5
---
26 11131221133112132113212221
46 1321132132111213122112311311222113111221131221
62 11131221131211131231121113112221121321132132211331222113112211
62 11131221131211131231121113112221121321132132211331222113112211
1 1
6 111221
=== hidden
10
3
11
1
6
10
---
20 13211311123113112211
2 21
26 11131221133112132113212221
1 1
6 312211
20 13211311123113112211
=== hidden
19
9
11
20
28
6
---
226 1321132132211331121321231231121113112221...
14 31131211131221
26 11131221133112132113212221
302 1113122113121113222123211211131211121311...
2606 1321132132211331121321231231121113112221...
6 312211
=== hidden
6
14
3
31
31
7
---
6 312211
62 11131221131211131231121113112221121321132132211331222113112211
2 21
5808 1321132132211331121321231231121113112221...
5808 1321132132211331121321231231121113112221...
8 13112221
=== hidden
33
13
10
33
5
32
---
9898 3113112221131112311332111213122112311311...
46 1321132132111213122112311311222113111221131221
20 13211311123113112211
9898 3113112221131112311332111213122112311311...
6 111221
7586 1113122113121113222123211211131211121311...

## Hints
- Base case: `n == 1` returns `"1"`. Otherwise get the previous term recursively.
- Scan the previous term in runs. An inner `while` loop finds where the current run of equal digits ends.
- Append the count (`to_string(len)`) **then** the digit.

## Solution
This is linear recursion: `term(n)` is defined from `term(n−1)`, so the function asks for the previous term and then **run-length encodes** it.

For the encoding, scan with two indices. `j` walks forward while the digit equals `prev[i]`, so `[i, j)` is one run. Append the run length and the digit, then jump `i` to `j`.

The terms grow by a factor of about 1.30 per step (Conway's constant). `term(35)` has about 30,000 characters, so the total work is dominated by the last few terms. The recursion is only 35 levels deep. A loop would work just as well, and the recursive form simply mirrors the definition.

Complexity: O(total length of all terms).

```cpp
#include <bits/stdc++.h>
using namespace std;

string count_and_say(int n) {
    if (n == 1) return "1";                          // base case
    string prev = count_and_say(n - 1);              // trust the smaller term
    string out;
    for (size_t i = 0; i < prev.size(); ) {
        size_t j = i;
        while (j < prev.size() && prev[j] == prev[i]) ++j;   // [i, j) is one run
        out += to_string(j - i);
        out += prev[i];
        i = j;
    }
    return out;
}
```
