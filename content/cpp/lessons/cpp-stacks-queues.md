# Stacks from Scratch

A **stack** is a pile of plates: you can only add a plate on top (**push**), look at the top plate (**top**), or take the top plate off (**pop**). The last item in is the first item out: **LIFO**. That one restriction is why stacks show up everywhere: matching brackets, undo buttons, evaluating `3 + 4 * 2`, browser history, depth-first search, and the call stack that runs every C++ function you write.

This lesson builds a stack yourself, then uses it for the classic stack problems. The next lessons build on it: monotonic stacks, queues and deques, and heaps.

## 1. Why a stack?

Whenever the problem has **nesting** or **"most recent first"** behaviour, think stack:

- The bracket that must close next is the most recently opened one.
- Undo reverts the most recent edit.
- A function returns to the caller that called it most recently.
- In `a + b * c`, the `*` that arrived *later* is applied *first*.

All three operations are O(1), and the structure is tiny, so a stack is often the difference between an O(n²) rescan and an O(n) single pass.

```text
push 1   push 2   push 3   pop -> 3   top -> 2
                  | 3 |
         | 2 |    | 2 |    | 2 |
| 1 |    | 1 |    | 1 |    | 1 |     top is the last element
```

## 2. Building a stack

### 2.1 Array-based with doubling

Keep the elements in a buffer `data[0..size-1]`. The top is `data[size-1]`. Push writes at `size`, pop reads at `size-1`. When the buffer is full, allocate one twice as large and copy.

```cpp
#include <bits/stdc++.h>
using namespace std;

class IntStack {
    int* data_ = new int[1];
    int size_ = 0, cap_ = 1;
    void grow() {
        int* fresh = new int[2 * cap_];
        for (int i = 0; i < size_; ++i) fresh[i] = data_[i];
        delete[] data_;
        data_ = fresh;
        cap_ *= 2;
    }
public:
    IntStack() = default;
    ~IntStack() { delete[] data_; }
    IntStack(const IntStack&) = delete;             // one owner per buffer
    IntStack& operator=(const IntStack&) = delete;

    void push(int x) { if (size_ == cap_) grow(); data_[size_++] = x; }
    void pop()       { --size_; }                     // precondition: !empty()
    int  top() const { return data_[size_ - 1]; }     // precondition: !empty()
    bool empty() const { return size_ == 0; }
    int  size() const { return size_; }
};

int main() {
    IntStack s;
    for (int i = 1; i <= 5; ++i) s.push(i * 10);
    while (!s.empty()) { cout << s.top() << ' '; s.pop(); }   // 50 40 30 20 10
    cout << '\n';
}
```

**Why doubling is O(1) amortized.** A copy costs O(size), but after a copy to capacity `2c` you need `c` more pushes before the next one. The total copying for n pushes is at most 1 + 2 + 4 + … + n < 2n, so each push costs O(1) *on average over the sequence*. Growing by a constant (+10) instead would make n pushes cost O(n²).

**Shrinking.** If you want memory back after many pops, halve the capacity when the size drops to **a quarter**, not a half. At a half, a push at the boundary doubles and the next pop halves: O(n) per operation, forever. At a quarter, the new buffer is half full, so many operations must happen before the next resize. (The first problem asks you to implement exactly this.)

### 2.2 Linked-list-based

A singly linked list where the head is the top also gives O(1) push and pop, with no copying ever, but every push is a heap allocation and the nodes are scattered in memory.

```cpp
#include <bits/stdc++.h>
using namespace std;

class ListStack {
    struct Node { int val; Node* next; };
    Node* head_ = nullptr;
    int size_ = 0;
public:
    ~ListStack() { while (head_) pop(); }
    void push(int x) { head_ = new Node{x, head_}; ++size_; }
    void pop() { Node* old = head_; head_ = head_->next; delete old; --size_; }
    int top() const { return head_->val; }
    bool empty() const { return head_ == nullptr; }
};

int main() {
    ListStack s;
    s.push(1); s.push(2); s.push(3);
    cout << s.top() << '\n';   // 3
    s.pop();
    cout << s.top() << '\n';   // 2
}
```

### 2.3 What to use in real code

| Option | Notes |
|---|---|
| `std::vector<T>` with `push_back`, `back`, `pop_back` | the default: contiguous, fast, and you can index into it or read the bottom |
| `std::stack<T>` | an adaptor over `std::deque` (or `vector`): only `push/top/pop`, nothing else visible |
| a linked list | only when you need stable addresses or splice operations |

> [!KEY]
> `std::stack::pop()` returns `void`. Read `top()` first, then `pop()`. Calling either on an empty stack is undefined behaviour: check `empty()` first.

In this module we mostly use a `vector` as a stack, because many algorithms need to peek below the top or read the bottom.

## 3. Balanced brackets

**Problem:** is `{[()()]}` properly nested? Push every opener. On a closer, the top must be its matching opener; pop it. At the end the stack must be empty.

```cpp
#include <bits/stdc++.h>
using namespace std;

bool balanced(const string& s) {
    vector<char> st;
    for (char c : s) {
        if (c == '(' || c == '[' || c == '{') st.push_back(c);
        else if (c == ')' || c == ']' || c == '}') {
            char want = c == ')' ? '(' : c == ']' ? '[' : '{';
            if (st.empty() || st.back() != want) return false;
            st.pop_back();
        }
    }
    return st.empty();
}

int main() {
    for (string s : {"{[()()]}", "([)]", "((", "a(b)c"}) cout << s << ": " << balanced(s) << '\n';
}
```

Dry run of `([)]`:

```text
(   push        [ ( ]
[   push        [ ( [ ]
)   top is [ but ) needs (   -> not balanced
```

A single counter works only for one bracket type: `([)]` has balanced counts but bad nesting. Push **indices** instead of characters when you need to report *where* the error is.

## 4. Min stack: augmenting each element

**Problem:** support `push`, `pop`, `top` and `get_min`, all O(1).

The insight: a stack changes only at the top, so "the minimum of this element and everything below it" never changes while the element is in the stack. Store it with the element.

```cpp
#include <bits/stdc++.h>
using namespace std;

class MinStack {
    vector<pair<int,int>> v;    // (value, min of everything up to here)
public:
    void push(int x) { v.push_back({x, v.empty() ? x : min(x, v.back().second)}); }
    void pop() { v.pop_back(); }
    int top() const { return v.back().first; }
    int get_min() const { return v.back().second; }
};

int main() {
    MinStack s;
    s.push(5); s.push(3); s.push(7);
    cout << s.get_min() << '\n';   // 3
    s.pop(); s.pop();
    cout << s.get_min() << '\n';   // 5
}
```

The same trick gives max, sum or gcd of the stack in O(1). It is your first **augmented data structure**: extra information maintained alongside each element.

## 5. Expression evaluation

### 5.1 Postfix (Reverse Polish) evaluation

In postfix, operators come after their operands: `3 4 2 * +` means `3 + 4 * 2`. No parentheses and no precedence are needed: an operator applies to the two most recent values.

```cpp
#include <bits/stdc++.h>
using namespace std;

long long eval_postfix(const vector<string>& tokens) {
    vector<long long> st;
    for (const string& t : tokens) {
        if (t.size() == 1 && string("+-*/").find(t[0]) != string::npos) {
            long long b = st.back(); st.pop_back();    // right operand is on top!
            long long a = st.back(); st.pop_back();
            st.push_back(t == "+" ? a + b : t == "-" ? a - b : t == "*" ? a * b : a / b);
        } else st.push_back(stoll(t));                  // handles "-3" too
    }
    return st.back();
}

int main() {
    cout << eval_postfix({"3", "4", "2", "*", "+"}) << '\n';   // 11
    cout << eval_postfix({"10", "3", "-"}) << '\n';            // 7
}
```

```text
3 4 2 * +
3   [3]
4   [3 4]
2   [3 4 2]
*   b=2, a=4 -> 8    [3 8]
+   b=8, a=3 -> 11   [11]
```

### 5.2 Infix to postfix: the shunting-yard algorithm

Dijkstra's shunting-yard algorithm converts `3 + 4 * 2` to `3 4 2 * +` with one **operator stack**:

1. An operand goes straight to the output.
2. An operator `o`: while the top of the stack is an operator that must be applied **before** `o`, pop it to the output. Then push `o`. "Before" means: higher precedence, or equal precedence and `o` is **left**-associative.
3. `(` is pushed as a barrier. `)` pops to the output until the `(`, then discards it.
4. At the end, pop everything to the output.

Associativity matters on ties: `a - b - c` is `(a - b) - c` (left), so the stacked `-` leaves first. But `2 ^ 3 ^ 2` is `2 ^ (3 ^ 2)` (right), so the stacked `^` must wait.

```cpp
#include <bits/stdc++.h>
using namespace std;

int prec(char o) { return o == '^' ? 3 : (o == '*' || o == '/') ? 2 : 1; }

string to_postfix(const string& s) {          // single-character operands
    string out;
    vector<char> ops;
    for (char c : s) {
        if (isalnum((unsigned char)c)) out += c;
        else if (c == '(') ops.push_back(c);
        else if (c == ')') {
            while (ops.back() != '(') { out += ops.back(); ops.pop_back(); }
            ops.pop_back();
        } else {
            while (!ops.empty() && ops.back() != '(' &&
                   (prec(ops.back()) > prec(c) || (prec(ops.back()) == prec(c) && c != '^'))) {
                out += ops.back(); ops.pop_back();
            }
            ops.push_back(c);
        }
    }
    while (!ops.empty()) { out += ops.back(); ops.pop_back(); }
    return out;
}

int main() {
    cout << to_postfix("a+b*c") << '\n';      // abc*+
    cout << to_postfix("(a+b)*c") << '\n';    // ab+c*
    cout << to_postfix("a-b-c") << '\n';      // ab-c-
    cout << to_postfix("2^3^2") << '\n';      // 232^^
}
```

Dry run of `a+b*c-d`:

```text
token  output        ops
a      a
+      a             +
b      ab            +
*      ab            + *      (* beats +, so + stays)
c      abc           + *
-      abc*+         -        (pop * (higher), pop + (equal, left-assoc))
d      abc*+d        -
end    abc*+d-
```

### 5.3 Evaluating infix directly: two stacks

Replace the output string by a **value stack**: whenever shunting-yard would emit an operator, apply it to the top two values instead. Unary minus needs one extra bit of state: a `-` is unary when you are *expecting an operand* (at the start, after `(`, or after another operator). Push it as a separate high-precedence prefix operator. The calculator problem walks through this.

## 6. Undo, redo and decoding: the stack as saved state

A stack is the natural place to **put something aside and come back to it later, in reverse order**.

- **Undo/redo:** keep each edit as a small object (what was typed, or exactly what was deleted). Undo pops it from the undo stack, reverts it, and pushes it on the redo stack. A new edit clears the redo stack. Store *deltas*, not snapshots of the whole document, or every edit costs O(document).
- **Decoding `3[a2[bc]]`:** at each `[`, push the text built so far and the repeat count, then start a fresh string. At `]`, pop, and append the inner string `k` times to the popped text. The stack holds exactly what a recursive decoder would keep in its local variables.

```cpp
#include <bits/stdc++.h>
using namespace std;

string decode(const string& s) {
    vector<pair<string,int>> st;
    string cur; int k = 0;
    for (char c : s) {
        if (isdigit((unsigned char)c)) k = k * 10 + (c - '0');
        else if (c == '[') { st.push_back({cur, k}); cur.clear(); k = 0; }
        else if (c == ']') {
            auto [outer, times] = st.back(); st.pop_back();
            for (int i = 0; i < times; ++i) outer += cur;
            cur = outer;
        } else cur += c;
    }
    return cur;
}

int main() { cout << decode("3[a2[bc]]") << '\n'; }   // abcbcabcbcabcbc
```

## 7. The call stack, and simulating recursion

Every function call pushes a **stack frame** holding its parameters, local variables and the return address. Returning pops it. Recursion is just many frames of the same function:

```text
fact(3)                       call stack (top at the bottom of the list)
 └─ fact(2)                   fact(3): n=3, waiting at "n * fact(n-1)"
     └─ fact(1)               fact(2): n=2, waiting
         returns 1            fact(1): n=1  -> returns 1, frame popped
```

The call stack is small: typically **8 MB** on Linux and 1 MB on Windows. A recursive DFS on a path of 10⁶ nodes needs 10⁶ frames and **crashes** with a stack overflow. The fix is to keep the frames yourself, in a `vector` on the heap. A frame must hold everything the function needs when it resumes. For a tree DFS that is `(node, index of the next child)`:

```cpp
#include <bits/stdc++.h>
using namespace std;

// pre- and post-order of a tree given as child lists, without recursion
void dfs_iterative(const vector<vector<int>>& ch, int root) {
    vector<pair<int,size_t>> st{{root, 0}};
    cout << "enter " << root << '\n';
    while (!st.empty()) {
        auto [v, i] = st.back();
        if (i < ch[v].size()) {
            st.back().second++;                  // resume here next time
            int c = ch[v][i];
            cout << "enter " << c << '\n';       // "call" dfs(c)
            st.push_back({c, 0});
        } else {
            cout << "exit " << v << '\n';        // "return" from dfs(v)
            st.pop_back();
        }
    }
}

int main() {
    vector<vector<int>> ch = {{1, 2}, {3}, {}, {}};
    dfs_iterative(ch, 0);   // enter 0, enter 1, enter 3, exit 3, exit 1, enter 2, exit 2, exit 0
}
```

The shortcut "pop a node, push all its children" gives a valid pre-order but no moment when a subtree is *finished*, so it cannot compute post-order work such as exit times or subtree sizes. The `(node, iterator)` frame is the general technique for turning any recursion into a loop.

## 8. Complexity summary

| Operation | Array stack | Linked stack |
|---|---|---|
| push | O(1) amortized (O(n) on a resize) | O(1), one allocation |
| pop, top, empty | O(1) | O(1) |
| memory | ≤ 2× (≤ 4× with quarter shrinking) | one node + pointer per element |

Most stack algorithms in this lesson are O(n) overall because **each element is pushed once and popped at most once**. Even with a `while` loop inside a `for` loop, the total number of pops can't exceed the number of pushes. Remember that argument; the monotonic stack lesson uses it constantly.

## 9. Recognising a stack problem

- Nesting: brackets, tags, nested `k[...]`, parentheses in expressions.
- "Most recent unmatched / unfinished" thing.
- Undo, back button, backtracking.
- Recursion that may be too deep, or that you need to pause and resume.
- Operators with precedence.
- "Next greater / previous smaller" (the monotonic stack, next lesson).

## 10. Common mistakes

- **Calling `top()` or `pop()` on an empty stack.** Undefined behaviour, often a silent wrong answer.
- **Wrong operand order** in postfix evaluation: the top is the *right* operand. `+` and `*` hide this bug.
- **Treating `-3` as an operator** because it starts with `-`.
- **Forgetting associativity** in shunting-yard: `^` is right-associative.
- **Storing snapshots** for undo: O(n) per edit instead of O(change).
- **Growing an array by a constant** instead of a factor: O(n²) total.
- **Shrinking at half capacity:** thrashing at the boundary.
- **Holding a reference to `v.back()`** and then calling `push_back`: the vector may reallocate and the reference dangles.

## 11. Interview and exam questions

> [!INTERVIEW] "Why is `vector::push_back` O(1) if it sometimes copies everything?"
> Capacity doubles, so the copies cost 1 + 2 + 4 + … < 2n over n pushes. That is O(1) amortized: any sequence of n pushes costs O(n) in total, even though one push can cost O(n).

> [!INTERVIEW] "Design a stack with O(1) get_min."
> Store pairs (value, min so far), or a second stack pushed when x ≤ current min. Use ≤, not <, so duplicate minimums survive a pop.

> [!EXAM] Convert `a*(b+c)^d-e` to postfix.
> `a b c + d ^ * e -`. The parentheses group `b+c`; `^` binds tighter than `*`; `-` is applied last.

> [!INTERVIEW] "Your recursive DFS crashes on large inputs. Why, and how do you fix it?"
> Each call uses a frame on a call stack of only a few MB. A path-shaped input needs n frames. Keep the frames yourself in a heap-allocated vector: `(node, next child index)`.

## Check your understanding

1. Why does halving capacity at size = capacity/2 cause thrashing?
2. In `a b -` (postfix), which value is popped first and which operand is it?
3. In shunting-yard, the stack holds `+` and the next token is `-`. What happens? And if the stack holds `^` and the next token is `^`?
4. What should a min-stack's second stack do when you push a value equal to the current minimum?
5. Why can't "pop a node, push all children" compute post-order exit times?

<details><summary>Answers</summary>

1. After halving, the buffer is exactly full, so the next push doubles again, and the following pop halves again: every operation costs O(n). Halving at a quarter leaves the buffer half full after the resize.
2. `b` is popped first, and it is the *right* operand; then `a`. The result is `a − b`.
3. `+` and `-` have equal precedence and are left-associative, so `+` is popped to the output, then `-` is pushed. With `^` on top and `^` arriving, nothing is popped (right-associative): the new `^` is pushed on top.
4. Push it too (use ≤). Otherwise popping one copy of the minimum would also remove the minimum that the other copy still needs.
5. Once a node is popped it is gone from the stack, so there is no later moment at which "all of its children are finished". A frame with a child index keeps the node on the stack until its last child returns.

</details>
