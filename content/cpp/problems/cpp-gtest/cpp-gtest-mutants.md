---
id: cpp-gtest-mutants
title: Write GoogleTest Cases That Kill the Mutants
difficulty: Hard
order: 1
tags: GoogleTest, unit testing, mutation testing, fixtures, interfaces, boundary cases
libs: gtest
time_limit: 5
---
## Statement
This time **you write the tests**. The unit under test is a bounded FIFO queue of ints, used to buffer encoder readings, exposed through an interface:

```cpp
struct IQueue {
    virtual ~IQueue() = default;
    virtual bool push(int v) = 0;      // false (and no change) if full
    virtual bool pop(int& out) = 0;    // false if empty; otherwise the OLDEST element
    virtual std::size_t size() const = 0;
    virtual bool full() const = 0;
};
extern std::function<std::unique_ptr<IQueue>(std::size_t capacity)> make_queue;   // set by the judge
```

Write GoogleTest `TEST`/`TEST_F` cases that create queues **only** through `make_queue(capacity)`. The judge links your tests against the correct implementation (every test must pass) and against several **mutants**, each with one subtle bug (each must make at least one test fail). Write at least four tests.

Think about wrap-around after many push/pop cycles, capacity boundaries, rejected pushes leaving the state unchanged, FIFO order, and `size()` after every kind of operation.

## Starter
```cpp
#include <gtest/gtest.h>
#include <cstddef>
#include <functional>
#include <memory>

struct IQueue {
    virtual ~IQueue() = default;
    virtual bool push(int v) = 0;
    virtual bool pop(int& out) = 0;
    virtual std::size_t size() const = 0;
    virtual bool full() const = 0;
};
extern std::function<std::unique_ptr<IQueue>(std::size_t)> make_queue;

TEST(Queue, PushThenPop) {
    auto q = make_queue(2);
    ASSERT_TRUE(q->push(7));
    int v = 0;
    ASSERT_TRUE(q->pop(v));
    EXPECT_EQ(v, 7);
}
```

## Driver
```cpp
#include <algorithm>
#include <iostream>
#include <string>
#include <vector>

std::function<std::unique_ptr<IQueue>(std::size_t)> make_queue;

namespace judge {
struct Ring : IQueue {
    std::vector<int> buf; std::size_t head = 0, count = 0;
    explicit Ring(std::size_t cap) : buf(cap) {}
    bool push(int v) override { if (count == buf.size()) return false; buf[(head + count) % buf.size()] = v; ++count; return true; }
    bool pop(int& out) override { if (!count) return false; out = buf[head]; head = (head + 1) % buf.size(); --count; return true; }
    std::size_t size() const override { return count; }
    bool full() const override { return count == buf.size(); }
};
struct Lifo : Ring { using Ring::Ring;                                   // pops the NEWEST element
    bool pop(int& out) override { if (!count) return false; out = buf[(head + count - 1) % buf.size()]; --count; return true; } };
struct OffByOne : Ring { using Ring::Ring;                               // accepts capacity + 1 (overwrites)
    bool push(int v) override { if (count > buf.size()) return false; buf[(head + count) % buf.size()] = v; ++count; return true; } };
struct NoWrap : Ring { using Ring::Ring;                                 // write index never wraps: clamps at the end
    bool push(int v) override { if (count == buf.size()) return false; buf[std::min(head + count, buf.size() - 1)] = v; ++count; return true; } };
struct FullLies : Ring { using Ring::Ring;
    bool full() const override { return count + 1 >= buf.size(); } };
struct SizeStale : Ring { using Ring::Ring;                              // size not updated by pop
    std::size_t popped = 0;
    bool pop(int& out) override { bool ok = Ring::pop(out); if (ok) ++popped; return ok; }
    std::size_t size() const override { return count + popped; } };
struct OverwriteWhenFull : Ring { using Ring::Ring;                      // drops the OLDEST instead of rejecting
    bool push(int v) override { if (count == buf.size()) { head = (head + 1) % buf.size(); --count; } return Ring::push(v); } };
struct PopEmptyTrue : Ring { using Ring::Ring;
    bool pop(int& out) override { if (!count) { out = 0; return true; } return Ring::pop(out); } };
}

template <class Q> static void use() { make_queue = [](std::size_t c) { return std::unique_ptr<IQueue>(new Q(c)); }; }

static int run_all() {
    auto& listeners = ::testing::UnitTest::GetInstance()->listeners();
    delete listeners.Release(listeners.default_result_printer());          // silence gtest's console output
    return RUN_ALL_TESTS();
}

int main(int argc, char** argv) {
    ::testing::InitGoogleTest(&argc, argv);
    std::string which;
    std::vector<std::string> wanted;
    while (std::cin >> which) wanted.push_back(which);
    use<judge::Ring>();
    bool ok = run_all() == 0;
    int tests = ::testing::UnitTest::GetInstance()->total_test_count();
    std::cout << "tests written: " << (tests >= 4 ? "4+" : std::to_string(tests)) << "\n";
    std::cout << "correct implementation passes: " << (ok ? "yes" : "no") << "\n";
    struct M { const char* name; void (*set)(); };
    M mutants[] = {{"lifo", use<judge::Lifo>}, {"off_by_one", use<judge::OffByOne>}, {"no_wrap", use<judge::NoWrap>},
                   {"full_lies", use<judge::FullLies>}, {"size_stale", use<judge::SizeStale>},
                   {"overwrite_when_full", use<judge::OverwriteWhenFull>}, {"pop_empty_true", use<judge::PopEmptyTrue>}};
    for (auto& m : mutants) {
        bool want = wanted.empty();
        for (auto& w : wanted) want |= (w == m.name);
        if (!want) continue;
        m.set();
        bool killed = RUN_ALL_TESTS() != 0;
        std::cout << "mutant " << m.name << ": " << (killed ? "killed" : "SURVIVED") << "\n";
    }
}
```

## Tests
=== sample
lifo pop_empty_true
---
tests written: 4+
correct implementation passes: yes
mutant lifo: killed
mutant pop_empty_true: killed
=== hidden
lifo off_by_one no_wrap full_lies size_stale overwrite_when_full pop_empty_true
---
tests written: 4+
correct implementation passes: yes
mutant lifo: killed
mutant off_by_one: killed
mutant no_wrap: killed
mutant full_lies: killed
mutant size_stale: killed
mutant overwrite_when_full: killed
mutant pop_empty_true: killed

## Hints
- **FIFO order**: push 1, 2, 3 and expect pops 1, 2, 3 (kills `lifo`).
- **Capacity**: with capacity 3, push 3 values and expect `full()` to be true, and false after 2 pushes (`full_lies`). The 4th push must return false, and the queue must still pop 1, 2, 3 (`off_by_one`, `overwrite_when_full`).
- **Wrap-around**: capacity 3, then repeat "push, push, pop, pop" many times while checking the values (`no_wrap`).
- **size()** after pushes **and pops** (`size_stale`); `pop` on an empty queue returns false (`pop_empty_true`).
- Use `ASSERT_*` when continuing makes no sense (for example a failed `pop`), so a mutant can't crash later in the test.

## Solution
```cpp
#include <gtest/gtest.h>
#include <cstddef>
#include <functional>
#include <memory>

struct IQueue {
    virtual ~IQueue() = default;
    virtual bool push(int v) = 0;
    virtual bool pop(int& out) = 0;
    virtual std::size_t size() const = 0;
    virtual bool full() const = 0;
};
extern std::function<std::unique_ptr<IQueue>(std::size_t)> make_queue;

class QueueTest : public ::testing::Test {
protected:
    std::unique_ptr<IQueue> q = make_queue(3);
    int pop_value() {
        int v = -999;
        EXPECT_TRUE(q->pop(v));
        return v;
    }
};

TEST_F(QueueTest, StartsEmpty) {
    int v;
    EXPECT_EQ(q->size(), 0u);
    EXPECT_FALSE(q->full());
    EXPECT_FALSE(q->pop(v));
}

TEST_F(QueueTest, FifoOrder) {
    ASSERT_TRUE(q->push(1));
    ASSERT_TRUE(q->push(2));
    ASSERT_TRUE(q->push(3));
    EXPECT_EQ(pop_value(), 1);
    EXPECT_EQ(pop_value(), 2);
    EXPECT_EQ(pop_value(), 3);
}

TEST_F(QueueTest, FullIsExactAtCapacity) {
    q->push(1);
    q->push(2);
    EXPECT_FALSE(q->full());
    q->push(3);
    EXPECT_TRUE(q->full());
}

TEST_F(QueueTest, RejectedPushChangesNothing) {
    for (int i = 1; i <= 3; ++i) ASSERT_TRUE(q->push(i));
    EXPECT_FALSE(q->push(4));
    EXPECT_EQ(q->size(), 3u);
    EXPECT_EQ(pop_value(), 1);
    EXPECT_EQ(pop_value(), 2);
    EXPECT_EQ(pop_value(), 3);
}

TEST_F(QueueTest, SizeTracksPushAndPop) {
    q->push(5);
    q->push(6);
    EXPECT_EQ(q->size(), 2u);
    pop_value();
    EXPECT_EQ(q->size(), 1u);
}

TEST_F(QueueTest, WrapsAroundManyTimes) {
    for (int round = 0; round < 10; ++round) {
        ASSERT_TRUE(q->push(2 * round));
        ASSERT_TRUE(q->push(2 * round + 1));
        EXPECT_EQ(pop_value(), 2 * round);
        EXPECT_EQ(pop_value(), 2 * round + 1);
        EXPECT_EQ(q->size(), 0u);
    }
}
```

Each test pins down one contract clause, and each mutant violates at least one of them:
- FIFO order catches `lifo`.
- Exact capacity and `full()` catch `full_lies` and `off_by_one`.
- A rejected push that leaves the contents intact catches `overwrite_when_full`.
- Size after pops catches `size_stale`.
- Repeated cycles that move the head across the buffer boundary catch `no_wrap`.
- Popping from empty catches `pop_empty_true`.

The fixture gives every test a fresh queue built through the injected factory. That dependency injection is what lets the same suite run against many implementations, the mechanism mutation-testing tools such as Mull use to measure how strong a C++ test suite really is.
