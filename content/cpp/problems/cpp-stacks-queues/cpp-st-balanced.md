---
id: cpp-st-balanced
title: Balanced Brackets with the First Error Position
difficulty: Easy
order: 2
tags: stack, brackets, parsing
time_limit: 1
---
## Statement
```cpp
int first_error(const std::string& s);
```

`s` contains the bracket pairs `()`, `[]`, `{}`, `<>` and other characters (letters, digits, `+`, …), which are ignored. Return **−1** if every bracket is matched and properly nested. Otherwise return a 0-based index:

1. Scanning left to right, the first **closing** bracket that has no opener to match, or whose matching opener is of a different type (`(]`), is the error.
2. If the scan finishes without such a closer but some openers are never closed, the error is the **leftmost** unclosed opener.

Examples: `a(b[c]d)e` → −1. `([)]` → 2 (the `)` meets an open `[`). `x)` → 1. `((()` → 0 (the opener at 0 is never closed; so is the one at 1, but 0 is leftmost).

**Input:** one string per line until the end of input (1 ≤ length ≤ 10⁶, no spaces). Print one answer per line.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

int first_error(const string& s) {
    int depth = 0;                       // one counter cannot tell ( from [ and forgets positions
    for (int i = 0; i < (int)s.size(); ++i) {
        if (s[i] == '(' || s[i] == '[' || s[i] == '{' || s[i] == '<') ++depth;
        else if (s[i] == ')' || s[i] == ']' || s[i] == '}' || s[i] == '>') { if (--depth < 0) return i; }
    }
    return depth == 0 ? -1 : 0;
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    string s;
    while (cin >> s) cout << first_error(s) << '\n';
}
```

## Tests
=== sample
a(b[c]d)e
([)]
x)
((()
---
-1
2
1
0
=== hidden
<{[()]}>
<<>
}
ab+cd
([{<>}])(
(a)[b]{c}<d>)
---
-1
0
0
-1
8
12
=== hidden
[1a][([
[][]{}[a]
b<{
[b
{}{}{
[]{
<>{[([]
[}][]{
---
4
-1
1
0
4
2
2
1
=== hidden
[]()(1()){}b
(b)[{][
{}[[[](){}<)
b{({<[]>()[
(){}<><a}+><([
(({<>{
{}(<[]1()()>([
{}<{([[][
---
-1
5
11
1
8
0
2
2
=== hidden
[[b]](
+(())
(({[]<>[
[]{()}[]<
(
{{}}[]<><
<{()<(()(
{
---
5
-1
0
8
0
8
0
0
=== hidden
@gen 2289437125 big
=== hidden
@gen 2289437126 big
=== hidden
@gen 2289437127 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
pairs = ["()", "[]", "{}", "<>"]
for _ in range(8 if not big else 2):
    n = r.randint(1, 14) if not big else 1000000
    out, st = [], []
    for _ in range(n):
        x = r.random()
        if x < 0.15: out.append(r.choice("ab+1"))
        elif x < 0.55 or not st:
            p = r.choice(pairs); st.append(p[1]); out.append(p[0])
        else:
            out.append(st.pop() if r.random() > (0.08 if not big else 0.000002) else r.choice(")]}>"))
    if big and r.random() < 0.5:
        out.extend(reversed(st))
    print("".join(out))
```

## Hints
- The bracket that must close next is always the most recently opened one that is still open. Which structure gives you "most recent"?
- Push the index of each opener. On a closer, compare `s[top]` with the opener it needs.
- After the scan, the remaining indices are the unclosed openers, in increasing order. Use a `vector` so you can read the bottom.

## Solution
The most recently opened bracket must close first: that is LIFO, so a stack of open brackets is the natural model. Push every opener; a closer must match the opener on top, which is popped.

Store **indices**, not characters: the character is `s[index]`, and the index is needed for the answer. When the scan ends, the stack holds exactly the unclosed openers in increasing index order, so the leftmost is at the **bottom** (`st.front()` on a vector). A `std::stack` hides its bottom; a vector used as a stack does not.

A single depth counter (the starter) works for one bracket type only, and even then it cannot report which opener is unclosed.

Complexity: O(n) time, O(n) extra memory in the worst case (all openers).

```cpp
#include <bits/stdc++.h>
using namespace std;

int first_error(const string& s) {
    auto opener_of = [](char c) -> char {
        switch (c) { case ')': return '('; case ']': return '['; case '}': return '{'; case '>': return '<'; }
        return 0;                                    // not a closer
    };
    vector<int> st;                                  // indices of unmatched openers
    st.reserve(s.size());
    for (int i = 0; i < (int)s.size(); ++i) {
        char c = s[i];
        if (c == '(' || c == '[' || c == '{' || c == '<') st.push_back(i);
        else if (char want = opener_of(c)) {
            if (st.empty() || s[st.back()] != want) return i;   // nothing to match, or the wrong type
            st.pop_back();
        }
    }
    return st.empty() ? -1 : st.front();             // bottom of the stack = leftmost unclosed opener
}
```
