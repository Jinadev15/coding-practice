---
id: cpp-target-resolver
title: CMake Usage-Requirement Resolver
difficulty: Hard
order: 1
tags: CMake, targets, PUBLIC/PRIVATE/INTERFACE, transitive propagation, topological sort
time_limit: 2
---
## Statement
Implement the core of what CMake does with `target_include_directories` and `target_link_libraries`: propagate **usage requirements** through the target graph.

Input lines:
- `target NAME KIND`, where KIND is `executable`, `static`, `shared` or `interface`
- `include NAME SCOPE DIR`, where SCOPE is `PRIVATE`, `PUBLIC` or `INTERFACE`
- `link NAME SCOPE DEP`, where DEP is another target or an external library name (one not declared as a target)
- `query NAME`

The rules, as in CMake:
- A target **compiles with** its own `PRIVATE` and `PUBLIC` include dirs, plus the **interface** include dirs of every target it links (any scope).
- A target's **interface** include dirs are its own `PUBLIC` and `INTERFACE` dirs, plus the interface dirs of the dependencies it links `PUBLIC` or `INTERFACE` (transitively).
- **Link line** for an executable: a depth-first search from the executable's links, in declaration order, that visits each name **once**. Every linked dependency (any scope) is linked, and, transitively, so are the dependencies each library links with any scope (static libraries need their private dependencies at final link time). Record each name in **post-order**, then reverse the list, so every library comes before the libraries it depends on. Interface targets contribute their dependencies but never appear themselves. External names appear as given.

For `query NAME`, print:

```
NAME compile: dir1 dir2 ...      (dedup, first occurrence order: own private/public in declaration order,
                                  then each dependency's interface dirs in link-declaration order)
NAME interface: dir1 ...          (same ordering rules)
NAME link: lib1 lib2 ...          (only for executables; for libraries print "NAME link: -")
```

If the link graph between targets has a **cycle**, print `error: cycle involving NAME` for the queried target instead.

## Starter
```cpp
#include <iostream>
#include <string>

int main() {
    std::string line;
    while (std::getline(std::cin, line)) {
    }
}
```

## Tests
=== sample
target math static
target app executable
include math PUBLIC include/math
include math PRIVATE src/math_detail
link app PRIVATE math
query math
query app
---
math compile: include/math src/math_detail
math interface: include/math
math link: -
app compile: include/math
app interface:
app link: math
=== hidden
target eigen interface
include eigen INTERFACE /usr/include/eigen3
target geom static
include geom PUBLIC geom/include
include geom PRIVATE geom/src
link geom PUBLIC eigen
link geom PRIVATE fmt
target ctrl shared
include ctrl PUBLIC ctrl/include
link ctrl PRIVATE geom
link ctrl PUBLIC pthread
target app executable
include app PRIVATE app/src
link app PRIVATE ctrl
link app PRIVATE geom
query geom
query ctrl
query app
query eigen
---
geom compile: geom/include geom/src /usr/include/eigen3
geom interface: geom/include /usr/include/eigen3
geom link: -
ctrl compile: ctrl/include geom/include /usr/include/eigen3
ctrl interface: ctrl/include
ctrl link: -
app compile: app/src ctrl/include geom/include /usr/include/eigen3
app interface:
app link: ctrl pthread geom fmt
eigen compile:
eigen interface: /usr/include/eigen3
eigen link: -
=== hidden
target a static
target b static
target c executable
link a PUBLIC b
link b PRIVATE a
link c PRIVATE a
include a INTERFACE a/inc
query c
target d static
include d PUBLIC d/inc
include d PUBLIC d/inc
link d PRIVATE m
target e executable
link e PRIVATE d
link e PRIVATE d
query e
---
error: cycle involving c
e compile: d/inc
e interface:
e link: d m

## Hints
- Store per target: kind, includes in declaration order with their scopes, and links in declaration order with their scopes.
- `interface(T)` = own PUBLIC/INTERFACE dirs + `interface(dep)` for PUBLIC/INTERFACE links, memoised, with a visiting set to detect cycles.
- `compile(T)` = own PRIVATE/PUBLIC + `interface(dep)` for every target link.
- Link order: DFS with a `done` set (external names are leaves), appending each name in post-order the first time it finishes, then reverse. Skip interface targets when emitting. This is a topological order: dependents before dependencies.

## Solution
```cpp
#include <algorithm>
#include <functional>
#include <iostream>
#include <map>
#include <set>
#include <sstream>
#include <string>
#include <vector>

struct Target {
    std::string kind;
    std::vector<std::pair<std::string, std::string>> includes;   // (scope, dir)
    std::vector<std::pair<std::string, std::string>> links;      // (scope, dep)
};

std::map<std::string, Target> T;

struct Cycle { std::string at; };

static void add_unique(std::vector<std::string>& out, const std::string& s) {
    if (std::find(out.begin(), out.end(), s) == out.end()) out.push_back(s);
}

std::vector<std::string> interface_dirs(const std::string& name, std::set<std::string>& visiting) {
    if (!T.count(name)) return {};
    if (visiting.count(name)) throw Cycle{name};
    visiting.insert(name);
    std::vector<std::string> out;
    const Target& t = T[name];
    for (auto& [scope, dir] : t.includes)
        if (scope != "PRIVATE") add_unique(out, dir);
    for (auto& [scope, dep] : t.links)
        if (scope != "PRIVATE")
            for (auto& d : interface_dirs(dep, visiting)) add_unique(out, d);
    visiting.erase(name);
    return out;
}

std::vector<std::string> compile_dirs(const std::string& name) {
    std::vector<std::string> out;
    const Target& t = T[name];
    for (auto& [scope, dir] : t.includes)
        if (scope != "INTERFACE") add_unique(out, dir);
    for (auto& [scope, dep] : t.links) {
        std::set<std::string> visiting{name};
        for (auto& d : interface_dirs(dep, visiting)) add_unique(out, d);
    }
    return out;
}

std::vector<std::string> link_line(const std::string& name) {
    std::vector<std::string> post;
    std::set<std::string> visiting, done;
    std::function<void(const std::string&)> dfs = [&](const std::string& n) {
        if (done.count(n)) return;
        if (T.count(n)) {
            if (visiting.count(n)) throw Cycle{n};
            visiting.insert(n);
            for (auto& [scope, dep] : T[n].links) dfs(dep);
            visiting.erase(n);
        }
        done.insert(n);
        post.push_back(n);                                          // post-order: after its dependencies
    };
    for (auto& [scope, dep] : T[name].links) dfs(dep);
    std::vector<std::string> out;
    for (auto it = post.rbegin(); it != post.rend(); ++it)          // reverse: dependents first
        if (!(T.count(*it) && T[*it].kind == "interface")) out.push_back(*it);
    return out;
}

static std::string join(const std::vector<std::string>& v) {
    std::string s;
    for (auto& x : v) s += " " + x;
    return s;
}

int main() {
    std::string line;
    while (std::getline(std::cin, line)) {
        std::istringstream in(line);
        std::string cmd, a, b, c;
        in >> cmd >> a >> b >> c;
        if (cmd == "target") T[a].kind = b;
        else if (cmd == "include") T[a].includes.push_back({b, c});
        else if (cmd == "link") T[a].links.push_back({b, c});
        else if (cmd == "query") {
            try {
                auto comp = compile_dirs(a);
                std::set<std::string> v;
                auto iface = interface_dirs(a, v);
                std::vector<std::string> link;
                if (T[a].kind == "executable") link = link_line(a);
                std::cout << a << " compile:" << join(comp) << "\n";
                std::cout << a << " interface:" << join(iface) << "\n";
                std::cout << a << " link:" << (T[a].kind == "executable" ? join(link) : " -") << "\n";
            } catch (const Cycle& cy) {
                std::cout << "error: cycle involving " << a << "\n";
            }
        }
    }
}
```

This is the mechanism behind modern, target-based CMake:
- **Usage requirements** flow along PUBLIC and INTERFACE edges only, so a PRIVATE dependency (`geom` → `fmt`, `ctrl` → `geom`) never leaks its headers into consumers' compile lines.
- **Linking is different**: static libraries carry unresolved symbols, so their private dependencies still have to appear on the final executable's link line (`fmt` shows up for `app`), after every library that needs them. Reversed DFS post-order is a topological order: every library comes before the libraries it needs, so `ctrl` precedes `geom`, and `geom` precedes `fmt`.
- **Interface targets** (header-only libraries such as Eigen) contribute requirements but produce no binary to link.
- **Cycles** between targets are rejected, which is what CMake does for most cyclic graphs involving non-static libraries.
