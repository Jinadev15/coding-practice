---
id: cpp-string-interner
title: A String Interner with Stable Views
difficulty: Hard
order: 1
tags: object lifetime, string_view, dangling, SSO, heterogeneous lookup, allocation-free
time_limit: 3
---
## Statement
A robot's message bus sends the same topic names (`/lidar/front`, `/odom`, …) millions of times. An **interner** stores each distinct string once and hands out cheap `std::string_view`s, so topics compare by pointer and hash in O(1).

```cpp
class Interner {
public:
    std::string_view intern(std::string_view s);            // store s if new; return the canonical view
    std::optional<std::string_view> find(std::string_view s) const;   // canonical view if present
    std::size_t size() const noexcept;                      // number of distinct strings
    std::size_t bytes() const noexcept;                     // total characters stored
};
```

The hidden driver checks every one of these lifetime guarantees:
1. **Stability**: every view returned by `intern` stays valid, with an unchanged `data()` pointer, for the whole lifetime of the interner, no matter how many strings are added later. Careful: `std::vector<std::string>` relocates its strings when it grows, and short strings live *inside* the `std::string` object (SSO), so their characters move too.
2. **Canonical**: interning equal contents always returns the *same pointer*.
3. **No allocation in `find`**: the driver counts calls to global `operator new` during `find` and expects zero. Building a `std::string` key for the lookup allocates whenever the string is longer than the SSO capacity.
4. **Move-only**: `Interner` must be movable, the views must survive a move, and copying must be disabled, because a copy's views would point into the original.

Views can contain any bytes, including `'\0'`.

## Starter
```cpp
#include <string>
#include <string_view>
#include <optional>
#include <vector>
#include <unordered_map>

class Interner {
public:
    std::string_view intern(std::string_view s) {
        auto it = index_.find(std::string(s));
        if (it != index_.end()) return store_[it->second];
        store_.emplace_back(s);
        index_.emplace(std::string(s), store_.size() - 1);
        return store_.back();
    }
    std::optional<std::string_view> find(std::string_view s) const {
        auto it = index_.find(std::string(s));
        if (it == index_.end()) return std::nullopt;
        return std::string_view(store_[it->second]);
    }
    std::size_t size() const noexcept { return store_.size(); }
    std::size_t bytes() const noexcept { std::size_t b = 0; for (auto& s : store_) b += s.size(); return b; }
private:
    std::vector<std::string> store_;
    std::unordered_map<std::string, std::size_t> index_;
};
```

## Driver
```cpp
#include <cstdio>
#include <cstdlib>
#include <new>
#include <iostream>
#include <type_traits>

static std::size_t g_allocs = 0;
static bool g_counting = false;
void* operator new(std::size_t n) {
    if (g_counting) ++g_allocs;
    if (void* p = std::malloc(n ? n : 1)) return p;
    throw std::bad_alloc{};
}
void operator delete(void* p) noexcept { std::free(p); }
void operator delete(void* p, std::size_t) noexcept { std::free(p); }

static_assert(!std::is_copy_constructible_v<Interner>, "Interner must not be copyable");
static_assert(std::is_move_constructible_v<Interner>, "Interner must be movable");

static unsigned long long st;
static unsigned rnd() { st = st * 6364136223846793005ULL + 1442695040888963407ULL; return unsigned(st >> 33); }

int main() {
    std::string cmd;
    Interner in;
    while (std::cin >> cmd) {
        if (cmd == "intern" || cmd == "find") {
            std::string w; std::cin >> w;
            if (cmd == "intern") {
                auto a = in.intern(w);
                auto b = in.intern(std::string(w));
                std::printf("intern %s -> \"%.*s\" same_ptr=%s size=%zu bytes=%zu\n", w.c_str(), int(a.size()), a.data(),
                            a.data() == b.data() ? "yes" : "no", in.size(), in.bytes());
            } else {
                g_allocs = 0; g_counting = true;
                auto r = in.find(w);
                g_counting = false;
                std::printf("find %s -> %s allocations=%zu\n", w.c_str(), r ? "found" : "missing", g_allocs);
            }
        } else if (cmd == "stress") {
            std::size_t n; std::cin >> n >> st;
            Interner local;
            std::vector<std::string> want;
            std::vector<std::string_view> views;
            std::vector<const char*> ptrs;
            want.reserve(n); views.reserve(n); ptrs.reserve(n);
            for (std::size_t i = 0; i < n; ++i) {
                std::size_t len = 1 + rnd() % 40;
                if (rnd() % 3 == 0) len = 1 + rnd() % 6;                 // many short (SSO) strings
                std::string s;
                for (std::size_t k = 0; k < len; ++k) s.push_back(char('a' + rnd() % 3));
                if (rnd() % 50 == 0) s[rnd() % len] = '\0';             // embedded NULs
                auto v = local.intern(s);
                want.push_back(s); views.push_back(v); ptrs.push_back(v.data());
            }
            std::size_t bad_content = 0, bad_ptr = 0, bad_canon = 0;
            for (std::size_t i = 0; i < n; ++i) {
                if (views[i] != want[i]) ++bad_content;
                if (views[i].data() != ptrs[i]) ++bad_ptr;
                if (local.intern(want[i]).data() != ptrs[i]) ++bad_canon;
            }
            g_allocs = 0; g_counting = true;
            std::size_t found = 0;
            for (std::size_t i = 0; i < n; ++i) if (auto r = local.find(want[i]); r && r->data() == ptrs[i]) ++found;
            g_counting = false;
            std::size_t find_allocs = g_allocs;
            Interner moved(std::move(local));
            std::size_t bad_after_move = 0;
            for (std::size_t i = 0; i < n; ++i)
                if (std::string_view(ptrs[i], want[i].size()) != want[i] || moved.intern(want[i]).data() != ptrs[i]) ++bad_after_move;
            std::printf("stress %zu: distinct=%zu bytes=%zu dangling=%zu moved_ptrs=%zu non_canonical=%zu found=%zu find_allocations=%zu after_move_bad=%zu\n",
                        n, moved.size(), moved.bytes(), bad_content, bad_ptr, bad_canon, found, find_allocs, bad_after_move);
        }
    }
}
```

## Tests
=== sample
intern odom
intern /lidar/front_left_long_topic_name
intern odom
find odom
find /lidar/front_left_long_topic_name
find /imu
---
intern odom -> "odom" same_ptr=yes size=1 bytes=4
intern /lidar/front_left_long_topic_name -> "/lidar/front_left_long_topic_name" same_ptr=yes size=2 bytes=37
intern odom -> "odom" same_ptr=yes size=2 bytes=37
find odom -> found allocations=0
find /lidar/front_left_long_topic_name -> found allocations=0
find /imu -> missing allocations=0
=== hidden
stress 2000 1
---
stress 2000: distinct=1482 bytes=27990 dangling=0 moved_ptrs=0 non_canonical=0 found=2000 find_allocations=0 after_move_bad=0
=== hidden
stress 200000 7
---
stress 200000: distinct=112591 bytes=2654406 dangling=0 moved_ptrs=0 non_canonical=0 found=200000 find_allocations=0 after_move_bad=0
=== hidden
intern a
intern b
intern a
find a
find aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
stress 50000 42
---
intern a -> "a" same_ptr=yes size=1 bytes=1
intern b -> "b" same_ptr=yes size=2 bytes=2
intern a -> "a" same_ptr=yes size=2 bytes=2
find a -> found allocations=0
find aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa -> missing allocations=0
stress 50000: distinct=29277 bytes=665660 dangling=0 moved_ptrs=0 non_canonical=0 found=50000 find_allocations=0 after_move_bad=0

## Hints
- Store the characters somewhere that **never moves**: a `std::deque<std::string>` (deque never relocates existing elements on `push_back`, and a `std::string` with long contents keeps its heap buffer), or better, a list of fixed-size `char` blocks (an arena) you copy into.
- Index with `std::unordered_set<std::string_view>`. Its keys are views into your stable storage, so a lookup takes a `string_view` directly, with no `std::string` construction and no allocation.
- With a deque of strings, beware SSO: the deque doesn't move the `std::string` objects, so their internal buffers stay put too. A `std::vector<std::unique_ptr<std::string>>` is also stable.
- Disable copying: `Interner(const Interner&) = delete;`. Default the move operations. Moving an `unordered_set` and a `deque` doesn't move their elements.

## Solution
```cpp
#include <string>
#include <string_view>
#include <optional>
#include <unordered_set>
#include <vector>
#include <memory>
#include <cstring>

class Interner {
public:
    Interner() = default;
    Interner(const Interner&) = delete;
    Interner& operator=(const Interner&) = delete;
    Interner(Interner&&) noexcept = default;
    Interner& operator=(Interner&&) noexcept = default;

    std::string_view intern(std::string_view s) {
        if (auto it = index_.find(s); it != index_.end()) return *it;
        std::string_view stored = copy_into_arena(s);
        index_.insert(stored);
        bytes_ += s.size();
        return stored;
    }

    std::optional<std::string_view> find(std::string_view s) const {
        if (auto it = index_.find(s); it != index_.end()) return *it;
        return std::nullopt;
    }

    std::size_t size() const noexcept { return index_.size(); }
    std::size_t bytes() const noexcept { return bytes_; }

private:
    static constexpr std::size_t kBlock = 64 * 1024;

    std::string_view copy_into_arena(std::string_view s) {
        if (s.size() > kBlock) {                                // oversized: its own block
            blocks_.push_back(std::make_unique<char[]>(s.size()));
            std::memcpy(blocks_.back().get(), s.data(), s.size());
            return {blocks_.back().get(), s.size()};
        }
        if (blocks_.empty() || used_ + s.size() > kBlock) {     // start a new block; old ones never move
            blocks_.push_back(std::make_unique<char[]>(kBlock));
            used_ = 0;
            cur_ = blocks_.back().get();
        }
        char* dst = cur_ + used_;
        if (!s.empty()) std::memcpy(dst, s.data(), s.size());
        used_ += s.size();
        return {dst, s.size()};
    }

    std::vector<std::unique_ptr<char[]>> blocks_;   // the vector may grow; the blocks it points to don't move
    char* cur_ = nullptr;
    std::size_t used_ = 0;
    std::size_t bytes_ = 0;
    std::unordered_set<std::string_view> index_;    // keys view into the blocks
};
```

The design separates **storage** from **lookup**:
- **Storage** is an arena of 64 KB character blocks. Characters are copied in once and never move: when the `blocks_` vector reallocates, it moves the `unique_ptr`s, not the blocks they point to. This is the "stable storage" requirement that `std::vector<std::string>` fails, because growing it relocates every `std::string` object, and short strings keep their characters inside the object (SSO), so their `data()` pointers change and old views dangle.
- **Lookup** is an `unordered_set<string_view>` whose keys point into the arena. `find(std::string_view)` hashes and compares the view directly, so there's nothing to allocate.
- **Moves** transfer the block pointers and the hash set's internal nodes, so existing views stay valid. **Copies** are deleted, because a copy's set would hold views into the *original's* arena, a dangling hazard the type system now rules out.
- The `n` interns cost amortised O(length) each with about one allocation per 64 KB of text, instead of two heap allocations per distinct string.
