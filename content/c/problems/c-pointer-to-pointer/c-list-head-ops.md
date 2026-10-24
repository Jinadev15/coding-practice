---
id: c-list-head-ops
title: Linked List with Double Pointers
difficulty: Medium
order: 1
tags: pointer to pointer, linked list, malloc
---
## Statement
Implement a singly linked list using `Node **` so that operations can change the head:

- `void push_front(Node **head, int v)`
- `void push_back(Node **head, int v)`: walk with a `Node **` cursor, so the empty list needs no special case
- `int remove_value(Node **head, int v)`: remove the **first** node with value v, free it, and return 1 (or return 0 if absent). Use the pointer-to-pointer technique, with no `prev` variable.
- `void free_list(Node **head)`: free all nodes and set `*head = NULL`

## Starter
```c
#include <stdlib.h>

typedef struct Node {
    int val;
    struct Node *next;
} Node;

void push_front(Node **head, int v) {
}

void push_back(Node **head, int v) {
}

int remove_value(Node **head, int v) {
    return 0;
}

void free_list(Node **head) {
}
```

## Driver
```c
#include <stdio.h>
#include <string.h>
static void print(const Node *n) {
    printf("[");
    for (; n; n = n->next) printf("%d%s", n->val, n->next ? " " : "");
    printf("]\n");
}
int main(void) {
    Node *head = NULL;
    char cmd[8]; int v;
    while (scanf("%7s", cmd) == 1) {
        if (!strcmp(cmd, "front")) { scanf("%d", &v); push_front(&head, v); }
        else if (!strcmp(cmd, "back")) { scanf("%d", &v); push_back(&head, v); }
        else if (!strcmp(cmd, "rm")) { scanf("%d", &v); printf("rm %d -> %d\n", v, remove_value(&head, v)); }
        else if (!strcmp(cmd, "print")) print(head);
    }
    free_list(&head);
    printf("freed %s\n", head == NULL ? "ok" : "BAD");
    return 0;
}
```

## Tests
=== sample
back 2
front 1
back 3
print
rm 1
rm 9
print
---
[1 2 3]
rm 1 -> 1
rm 9 -> 0
[2 3]
freed ok
=== hidden
rm 5
print
back 7
back 7
rm 7
print
rm 7
print
---
rm 5 -> 0
[]
rm 7 -> 1
[7]
rm 7 -> 1
[]
freed ok

## Hints
- `push_back`: `Node **p = head; while (*p) p = &(*p)->next; *p = new_node;`.
- `remove_value`: the same walk. When `(*p)->val == v`: `Node *dead = *p; *p = dead->next; free(dead);`.
- `*p` is "the link that points to the current node" (the head pointer itself, or some node's `next`), so removing the head isn't a special case.

## Solution
A `Node **` cursor points at the **link** (the head pointer or a `next` field) rather than at a node. Rewriting `*p` therefore works the same whether it's the head or the middle of the list. Linus Torvalds calls this having "good taste" in pointer code.

```c
#include <stdlib.h>

typedef struct Node {
    int val;
    struct Node *next;
} Node;

static Node *new_node(int v, Node *next) {
    Node *n = malloc(sizeof *n);
    if (!n) exit(1);
    n->val = v;
    n->next = next;
    return n;
}

void push_front(Node **head, int v) {
    *head = new_node(v, *head);
}

void push_back(Node **head, int v) {
    Node **p = head;
    while (*p) p = &(*p)->next;
    *p = new_node(v, NULL);
}

int remove_value(Node **head, int v) {
    for (Node **p = head; *p; p = &(*p)->next) {
        if ((*p)->val == v) {
            Node *dead = *p;
            *p = dead->next;
            free(dead);
            return 1;
        }
    }
    return 0;
}

void free_list(Node **head) {
    Node *n = *head;
    while (n) {
        Node *next = n->next;
        free(n);
        n = next;
    }
    *head = NULL;
}
```

`free_list` saves `next` **before** freeing the node. Reading `n->next` after `free(n)` is a use-after-free. Setting `*head = NULL` at the end means the caller's pointer can't dangle.
