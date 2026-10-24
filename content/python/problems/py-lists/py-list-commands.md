---
id: py-list-commands
title: List Command Interpreter
difficulty: Easy
order: 1
tags: list methods, syntax drill
---
## Statement
Start with an empty list and execute `q` commands, one per line. This is a **syntax drill**: each command is one list method.

| Command | Meaning |
|---|---|
| `append e` | add integer `e` at the end |
| `insert i e` | insert `e` before position `i` |
| `remove e` | remove the first occurrence of `e` (guaranteed to exist) |
| `pop` | remove the last element (the list is non-empty) |
| `popat i` | remove the element at index `i` |
| `sort` | sort ascending |
| `reverse` | reverse the order |
| `extend a b c ...` | append several integers |
| `count e` | print how many times `e` occurs |
| `index e` | print the first index of `e` (guaranteed to exist) |
| `print` | print the list in Python's list format, e.g. `[1, 2, 3]` |

## Starter
```python
q = int(input())
lst = []
for _ in range(q):
    cmd, *args = input().split()
    args = list(map(int, args))
```

## Tests
=== sample
12
insert 0 5
insert 1 10
insert 0 6
print
remove 6
append 9
append 1
sort
print
pop
reverse
print
---
[6, 5, 10]
[1, 5, 9, 10]
[9, 5, 1]
=== hidden
8
extend 3 1 3 2 3
count 3
index 2
popat 0
print
remove 3
print
count 7
---
3
3
[1, 3, 2, 3]
[1, 2, 3]
0
=== hidden
5
insert 100 7
insert -1 8
print
reverse
print
---
[8, 7]
[7, 8]
=== hidden
1
print
---
[]

## Hints
- `cmd, *args = input().split()` puts the first word in `cmd` and the rest in the list `args`.
- `print(lst)` already produces the `[1, 2, 3]` format.
- `insert` with an index past the end appends. A negative index counts from the end, like slicing.

## Solution
Each command maps directly to one method. Starred unpacking splits the command word from its arguments.

```python
q = int(input())
lst = []
for _ in range(q):
    cmd, *args = input().split()
    args = list(map(int, args))
    if cmd == "append":
        lst.append(args[0])
    elif cmd == "insert":
        lst.insert(args[0], args[1])
    elif cmd == "remove":
        lst.remove(args[0])
    elif cmd == "pop":
        lst.pop()
    elif cmd == "popat":
        lst.pop(args[0])
    elif cmd == "sort":
        lst.sort()
    elif cmd == "reverse":
        lst.reverse()
    elif cmd == "extend":
        lst.extend(args)
    elif cmd == "count":
        print(lst.count(args[0]))
    elif cmd == "index":
        print(lst.index(args[0]))
    elif cmd == "print":
        print(lst)
```

Notice the third test: `insert 100 7` on an empty list just appends, and `insert -1 8` inserts **before** the last element. `insert` never raises `IndexError`.
