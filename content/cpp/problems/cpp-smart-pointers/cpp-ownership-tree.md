---
id: cpp-ownership-tree
title: Ownership Tree with Smart Pointers
difficulty: Hard
order: 1
tags: unique_ptr, weak_ptr, shared_ptr, ownership, destructors
---
## Statement
Model a robot's **frame tree** (like ROS TF): each frame owns its children, and each child knows its parent without owning it.

```cpp
struct Frame {
    std::string name;
    Frame* parent = nullptr;                          // non-owning back pointer
    std::vector<std::unique_ptr<Frame>> children;     // owning
    ~Frame();                                         // logs "destroy NAME"
};
```

Implement:

- `Frame* add_child(Frame& parent, const std::string& name)`: create the child with `std::make_unique`, return a raw **observer** pointer
- `std::string path(const Frame* f)`: `"world/base/arm"` by walking parent pointers
- `std::unique_ptr<Frame> detach(Frame& parent, const std::string& name)`: remove the named child from `parent` and **return ownership** of it (or nullptr if absent), setting its `parent` to nullptr
- `~Frame()` logs `destroy NAME` to the global `std::vector<std::string> LOG`

The driver builds a tree, detaches a subtree, and lets ownership end, checking the destruction order.

## Starter
```cpp
#include <memory>
#include <string>
#include <vector>
#include <algorithm>

std::vector<std::string> LOG;

struct Frame {
    std::string name;
    Frame* parent = nullptr;
    std::vector<std::unique_ptr<Frame>> children;
    explicit Frame(std::string n) : name(std::move(n)) {}
    ~Frame() {}
};

Frame* add_child(Frame& parent, const std::string& name) { return nullptr; }
std::string path(const Frame* f) { return ""; }
std::unique_ptr<Frame> detach(Frame& parent, const std::string& name) { return nullptr; }
```

## Driver
```cpp
#include <iostream>
int main() {
    {
        auto world = std::make_unique<Frame>("world");
        Frame* base = add_child(*world, "base");
        Frame* arm = add_child(*base, "arm");
        Frame* grip = add_child(*arm, "gripper");
        add_child(*world, "camera");
        std::cout << path(grip) << '\n';
        std::unique_ptr<Frame> arm_owned = detach(*base, "arm");
        std::cout << (arm_owned ? path(arm_owned.get()) : "none") << '\n';
        std::cout << (detach(*base, "nope") ? "found" : "none") << '\n';
        std::cout << "base children: " << base->children.size() << '\n';
        LOG.push_back("-- drop arm --");
        arm_owned.reset();
        LOG.push_back("-- drop world --");
    }
    for (auto& s : LOG) std::cout << s << '\n';
}
```

## Tests
=== sample
---
world/base/arm/gripper
arm
none
base children: 0
-- drop arm --
destroy arm
destroy gripper
-- drop world --
destroy world
destroy base
destroy camera

## Hints
- `parent.children.push_back(std::make_unique<Frame>(name)); auto* c = parent.children.back().get(); c->parent = &parent; return c;`
- `detach`: find with `std::find_if` on the `unique_ptr`s, `std::move` the found one out, then `erase` it from the vector.
- Destruction order: a frame's destructor body runs **first** (logging its name), then its members are destroyed, which destroys the `children` vector and so recursively the children, in vector order.

## Solution
Owning edges are `unique_ptr` (parent → child), so each frame has exactly one owner and destroying an owner destroys its whole subtree. Back edges are raw observer pointers, which can't create cycles. Ownership can be handed out (`detach`) by moving the `unique_ptr`.

```cpp
#include <memory>
#include <string>
#include <vector>
#include <algorithm>

std::vector<std::string> LOG;

struct Frame {
    std::string name;
    Frame* parent = nullptr;
    std::vector<std::unique_ptr<Frame>> children;
    explicit Frame(std::string n) : name(std::move(n)) {}
    ~Frame() { LOG.push_back("destroy " + name); }
};

Frame* add_child(Frame& parent, const std::string& name) {
    parent.children.push_back(std::make_unique<Frame>(name));
    Frame* c = parent.children.back().get();
    c->parent = &parent;
    return c;
}

std::string path(const Frame* f) {
    std::string p = f->name;
    for (const Frame* cur = f->parent; cur; cur = cur->parent)
        p = cur->name + "/" + p;
    return p;
}

std::unique_ptr<Frame> detach(Frame& parent, const std::string& name) {
    auto it = std::find_if(parent.children.begin(), parent.children.end(),
                           [&](const std::unique_ptr<Frame>& c) { return c->name == name; });
    if (it == parent.children.end()) return nullptr;
    std::unique_ptr<Frame> owned = std::move(*it);
    parent.children.erase(it);
    owned->parent = nullptr;
    return owned;
}
```

If children held `shared_ptr` to their parents, the tree would be a reference cycle and nothing would ever be destroyed. Using `weak_ptr` (or, as here, a raw observer pointer from a clear owner) breaks it. The output shows **parent-first** destruction (`destroy world` before `destroy base`), because a destructor body runs before the members it contains are destroyed.
