# Stacks and Monotonic Stacks

A **stack** is last-in, first-out: you only touch the top. In Python, a `list` is a perfect stack, with `append` and `pop` both amortised O(1). Stacks model anything nested or deferred: matching brackets, undo history, function calls (the call stack itself), DFS, expression evaluation, and backtracking. The **monotonic stack**, which keeps its elements sorted by popping anything that breaks the order, answers "next greater/smaller element" questions for every position in O(n) total. It's one of the most elegant and most-tested patterns in interviews.

## 1. Stack basics

```python
stack = []
stack.append(3)        # push
stack.append(5)
top = stack[-1]        # peek: 5
stack.pop()            # 5
not stack              # empty check
```

> [!WARNING]
> Don't use `list.insert(0, x)` / `pop(0)` for a stack or queue. They're O(n). For a queue, use `collections.deque`.

## 2. Matching and nesting

```python
def balanced(s):
    pairs = {")": "(", "]": "[", "}": "{"}
    st = []
    for c in s:
        if c in "([{":
            st.append(c)
        elif c in pairs:
            if not st or st.pop() != pairs[c]:
                return False
    return not st                         # leftover openers = unbalanced

balanced("{[()()]}")    # True
balanced("([)]")        # False
```

The same structure solves:
- **simplify a path**: `"/a/./b/../../c/"` → `"/c"`
- **decode a string**: `"3[a2[c]]"` → `"accaccacc"`, pushing `(count, partial)` frames
- validating XML/HTML tags
- **minimum removals to make parentheses valid**

## 3. Expression evaluation

**Reverse Polish notation** (postfix) needs one stack:

```python
import operator
OPS = {"+": operator.add, "-": operator.sub, "*": operator.mul, "/": lambda a, b: int(a / b)}  # truncate toward 0

def eval_rpn(tokens):
    st = []
    for t in tokens:
        if t in OPS:
            b, a = st.pop(), st.pop()     # order matters: a is deeper
            st.append(OPS[t](a, b))
        else:
            st.append(int(t))
    return st[0]

eval_rpn(["2", "1", "+", "3", "*"])   # 9
```

**Infix** expressions with precedence use Dijkstra's **shunting-yard** algorithm (an operator stack plus an output queue), or two stacks (values and operators). On seeing an operator, first apply the stacked operators of greater or equal precedence (for left associativity). A `(` is pushed, and a `)` unwinds to the matching `(`. Compilers, calculators and spreadsheet engines all use this.

## 4. The monotonic stack

**Next greater element** for every index: the brute force is O(n²). With a stack of indices whose values are **decreasing**, each new element "resolves" every smaller element waiting on the stack:

```python
def next_greater(a):
    res = [-1] * len(a)
    st = []                                # indices; a[st] is decreasing from bottom to top
    for i, x in enumerate(a):
        while st and a[st[-1]] < x:
            res[st.pop()] = x              # x is the first greater element to the right of that index
        st.append(i)
    return res

next_greater([2, 1, 2, 4, 3])   # [4, 2, 4, -1, -1]
```

> [!KEY]
> Each index is pushed once and popped at most once, so the total is O(n), despite the nested loop. The invariant is that the stack holds exactly the elements still waiting for an answer, and they're necessarily in decreasing order (a larger element would already have resolved the smaller ones below it).

| Variant | Stack order | Pop condition |
|---|---|---|
| next greater to the right | decreasing | `a[top] < x` |
| next smaller to the right | increasing | `a[top] > x` |
| previous greater/smaller | the same, recording the answer for `i` *after* popping (it's the new top) | |
| circular array | iterate `2n` times with `i % n` | |
| "greater or equal" | change `<` to `<=` (matters with duplicates) | |

### Daily temperatures (distance to the next warmer day)

```python
def daily_temperatures(t):
    res, st = [0] * len(t), []
    for i, x in enumerate(t):
        while st and t[st[-1]] < x:
            j = st.pop()
            res[j] = i - j
        st.append(i)
    return res
```

### Largest rectangle in a histogram: the classic hard one

For each bar, the widest rectangle using its full height extends until the nearest **smaller** bar on each side. An increasing stack finds both boundaries at the moment a bar is popped:

```python
def largest_rectangle(h):
    st, best = [], 0                       # indices with increasing heights
    for i, x in enumerate(h + [0]):        # sentinel 0 flushes the stack at the end
        while st and h[st[-1]] >= x:
            height = h[st.pop()]
            left = st[-1] + 1 if st else 0 # the previous smaller bar is the new top
            best = max(best, height * (i - left))
        st.append(i)
    return best

largest_rectangle([2, 1, 5, 6, 2, 3])   # 10
```

It extends to the **maximal rectangle of 1s in a binary matrix** (run the histogram row by row, O(R·C)), useful for finding the largest free area in an occupancy grid. Other relatives include "sum of subarray minimums" (contribution technique: each element is the minimum of `left × right` subarrays), stock span, "remove k digits to make the smallest number" and "132 pattern".

## 5. Min-stack: O(1) getMin

```python
class MinStack:
    def __init__(self):
        self.st = []                      # (value, min so far)
    def push(self, x):
        self.st.append((x, min(x, self.st[-1][1]) if self.st else x))
    def pop(self):
        return self.st.pop()[0]
    def top(self):
        return self.st[-1][0]
    def get_min(self):
        return self.st[-1][1]
```

Each entry remembers the minimum **below and including** itself, so popping restores the previous minimum automatically.

## 6. Stacks replace recursion

Any recursive DFS can become an explicit stack, which avoids Python's recursion limit (default 1000) on deep trees and graphs:

```python
def dfs_iterative(graph, start):
    seen, order, st = {start}, [], [start]
    while st:
        u = st.pop()
        order.append(u)
        for v in reversed(graph[u]):      # reversed: visit neighbours in natural order
            if v not in seen:
                seen.add(v)
                st.append(v)
    return order
```

## 7. Exam-ready answers

> [!EXAM]
> **Monotonic stacks.** A monotonic stack is a stack whose elements are kept in increasing or decreasing order by popping every element that would violate the order before pushing a new one. When an element is popped because the incoming element is greater (or smaller), the incoming element is that popped element's next greater (or smaller) element, and the element beneath it is its previous one. Since every element is pushed and popped at most once, all such answers for a sequence of n elements are computed in O(n) time. This underlies solutions to next-greater-element, daily temperatures, stock span and largest-rectangle-in-histogram problems.

## 8. Cheat sheet

| Problem | Tool |
|---|---|
| brackets, nesting, undo | plain stack |
| postfix evaluation | value stack |
| infix with precedence | shunting-yard (operator stack) |
| next/previous greater or smaller | monotonic stack of indices |
| histogram / maximal rectangle | increasing stack + sentinel |
| O(1) minimum | store (value, running min) pairs |
| deep DFS | explicit stack instead of recursion |

> [!INTERVIEW]
> **"Why is the monotonic stack O(n) when there's a while loop inside a for loop?"** Use the amortised argument. Every index enters the stack exactly once and leaves at most once, so the total number of pops over the whole run is at most n. The inner loop's work is bounded by the pops, so the total is O(n) + O(n) = O(n).
