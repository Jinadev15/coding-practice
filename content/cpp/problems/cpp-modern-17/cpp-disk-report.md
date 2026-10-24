---
id: cpp-disk-report
title: Disk Usage Report with std::filesystem
difficulty: Medium
order: 1
tags: std::filesystem, structured bindings, std::optional, map
---
## Statement
Robot log directories fill up disks. Write a C++17 disk-usage analyser with `std::filesystem`:

```cpp
struct Report {
    std::uintmax_t total_bytes = 0;
    std::size_t files = 0, dirs = 0;                       // dirs excludes the root itself
    std::map<std::string, std::uintmax_t> bytes_by_ext;    // extension (".bag", ".txt", "" for none)
    std::vector<std::pair<std::string, std::uintmax_t>> largest;   // the top 3 files by size (relative paths, '/'-separated); ties by path
    std::optional<std::string> deepest;                    // the relative path of the deepest file (ties: lexicographically smallest)
};
Report analyse(const std::filesystem::path& root);
std::vector<std::string> find_empty_dirs(const std::filesystem::path& root);   // sorted relative paths of directories with NO entries
std::uintmax_t prune(const std::filesystem::path& root, const std::string& ext);   // delete all files with this extension; return bytes freed
```

The driver builds a directory tree in a scratch folder from the input (lines `PATH SIZE` create files filled with SIZE bytes, and lines `PATH/` create empty directories), calls your functions, prints the results, and cleans up.

Use `recursive_directory_iterator`, `path::extension()`, `relative()`, `file_size()` and `remove()`. Structured bindings make the map loops pleasant.

## Starter
```cpp
#include <filesystem>
#include <map>
#include <optional>
#include <string>
#include <vector>
#include <cstdint>

struct Report {
    std::uintmax_t total_bytes = 0;
    std::size_t files = 0, dirs = 0;
    std::map<std::string, std::uintmax_t> bytes_by_ext;
    std::vector<std::pair<std::string, std::uintmax_t>> largest;
    std::optional<std::string> deepest;
};

Report analyse(const std::filesystem::path& root) { return {}; }
std::vector<std::string> find_empty_dirs(const std::filesystem::path& root) { return {}; }
std::uintmax_t prune(const std::filesystem::path& root, const std::string& ext) { return 0; }
```

## Driver
```cpp
#include <iostream>
#include <fstream>

namespace fs = std::filesystem;

void print(const Report& r) {
    std::cout << "total " << r.total_bytes << " bytes in " << r.files << " files, " << r.dirs << " dirs\n";
    for (const auto& [ext, b] : r.bytes_by_ext) std::cout << "  [" << (ext.empty() ? "(none)" : ext) << "] " << b << '\n';
    std::cout << "  largest:";
    for (const auto& [p, b] : r.largest) std::cout << ' ' << p << '=' << b;
    std::cout << "\n  deepest: " << r.deepest.value_or("-") << '\n';
}

int main() {
    fs::path root = fs::current_path() / "scratch_tree";
    fs::remove_all(root);
    fs::create_directories(root);
    std::string path, prune_ext;
    std::uintmax_t size;
    while (std::cin >> path) {
        if (path == "PRUNE") { std::cin >> prune_ext; continue; }
        if (path.back() == '/') { fs::create_directories(root / path); continue; }
        std::cin >> size;
        fs::create_directories((root / path).parent_path());
        std::ofstream(root / path, std::ios::binary) << std::string(size, 'x');
    }
    print(analyse(root));
    std::cout << "empty dirs:";
    for (const auto& d : find_empty_dirs(root)) std::cout << ' ' << d;
    std::cout << '\n';
    if (!prune_ext.empty()) {
        std::cout << "pruned " << prune(root, prune_ext) << " bytes of " << prune_ext << '\n';
        print(analyse(root));
    }
    fs::remove_all(root);
}
```

## Tests
=== sample
logs/run1.bag 500
logs/run2.bag 700
logs/notes.txt 40
config/robot.yaml 120
config/old/
README 10
deep/a/b/c/trace.csv 64
PRUNE .bag
---
total 1434 bytes in 6 files, 7 dirs
  [(none)] 10
  [.bag] 1200
  [.csv] 64
  [.txt] 40
  [.yaml] 120
  largest: logs/run2.bag=700 logs/run1.bag=500 config/robot.yaml=120
  deepest: deep/a/b/c/trace.csv
empty dirs: config/old
pruned 1200 bytes of .bag
total 234 bytes in 4 files, 7 dirs
  [(none)] 10
  [.csv] 64
  [.txt] 40
  [.yaml] 120
  largest: config/robot.yaml=120 deep/a/b/c/trace.csv=64 logs/notes.txt=40
  deepest: deep/a/b/c/trace.csv
=== hidden
single.dat 0
---
total 0 bytes in 1 files, 0 dirs
  [.dat] 0
  largest: single.dat=0
  deepest: single.dat
empty dirs:
=== hidden
a/x.log 100
b/x.log 100
c/x.log 100
d/x.log 99
e/
f/g/
f/h.tmp 5
PRUNE .log
---
total 404 bytes in 5 files, 7 dirs
  [.log] 399
  [.tmp] 5
  largest: a/x.log=100 b/x.log=100 c/x.log=100
  deepest: a/x.log
empty dirs: e f/g
pruned 399 bytes of .log
total 5 bytes in 1 files, 7 dirs
  [.tmp] 5
  largest: f/h.tmp=5
  deepest: f/h.tmp

## Hints
- `for (const auto& e : fs::recursive_directory_iterator(root))`: check `e.is_directory()` / `e.is_regular_file()`, and use `e.file_size()`.
- Relative paths: `fs::relative(e.path(), root).generic_string()` gives `/` separators on every platform.
- Depth: count the components of the relative path, `std::distance(rel.begin(), rel.end())`.
- An empty directory satisfies `fs::is_empty(dir)`.
- When pruning, **collect** the paths first, then remove them. Deleting while a `recursive_directory_iterator` is iterating is unsafe.

## Solution
```cpp
#include <filesystem>
#include <map>
#include <optional>
#include <string>
#include <vector>
#include <cstdint>
#include <algorithm>
#include <iterator>

namespace fs = std::filesystem;

struct Report {
    std::uintmax_t total_bytes = 0;
    std::size_t files = 0, dirs = 0;
    std::map<std::string, std::uintmax_t> bytes_by_ext;
    std::vector<std::pair<std::string, std::uintmax_t>> largest;
    std::optional<std::string> deepest;
};

Report analyse(const fs::path& root) {
    Report r;
    std::vector<std::pair<std::string, std::uintmax_t>> all;
    long best_depth = -1;
    for (const auto& e : fs::recursive_directory_iterator(root)) {
        if (e.is_directory()) { ++r.dirs; continue; }
        if (!e.is_regular_file()) continue;
        auto size = e.file_size();
        fs::path rel = fs::relative(e.path(), root);
        std::string rels = rel.generic_string();
        r.total_bytes += size;
        ++r.files;
        r.bytes_by_ext[e.path().extension().string()] += size;
        all.emplace_back(rels, size);
        long depth = std::distance(rel.begin(), rel.end());
        if (depth > best_depth || (depth == best_depth && rels < *r.deepest)) {
            best_depth = depth;
            r.deepest = rels;
        }
    }
    std::sort(all.begin(), all.end(), [](const auto& a, const auto& b) {
        return a.second != b.second ? a.second > b.second : a.first < b.first;
    });
    all.resize(std::min<std::size_t>(3, all.size()));
    r.largest = std::move(all);
    return r;
}

std::vector<std::string> find_empty_dirs(const fs::path& root) {
    std::vector<std::string> out;
    for (const auto& e : fs::recursive_directory_iterator(root))
        if (e.is_directory() && fs::is_empty(e.path()))
            out.push_back(fs::relative(e.path(), root).generic_string());
    std::sort(out.begin(), out.end());
    return out;
}

std::uintmax_t prune(const fs::path& root, const std::string& ext) {
    std::vector<fs::path> victims;
    std::uintmax_t freed = 0;
    for (const auto& e : fs::recursive_directory_iterator(root))
        if (e.is_regular_file() && e.path().extension() == ext) {
            freed += e.file_size();
            victims.push_back(e.path());
        }
    for (const auto& p : victims) fs::remove(p);      // remove after iterating, never during
    return freed;
}
```

`std::filesystem` replaces the platform-specific `opendir`/`stat`/`FindFirstFile` code with one portable API: paths compose with `/`, `extension()` and `relative()` do the string surgery, and `recursive_directory_iterator` walks the tree. The C++17 additions make the result type expressive: `std::optional` for "there may be no files", and structured bindings for map and pair iteration. Collecting the files to delete before removing them avoids invalidating the directory iterator. That's the same "don't mutate while iterating" rule as for containers.
