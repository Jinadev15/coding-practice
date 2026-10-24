---
id: cpp-coroutine-generator
title: Build Your Own Coroutine Generator
difficulty: Expert
order: 1
tags: coroutines, co_yield, promise_type, coroutine_handle, iterators, RAII
---
## Statement
Implement a coroutine return type `Generator<T>` from scratch, **without** `std::generator`, that works with range-for, plus three coroutines that use it:

```cpp
template <typename T> class Generator;            // move-only; destroys its coroutine frame (RAII)
// Generator<T> must provide begin()/end() returning an input iterator, so that
//     for (T x : gen) ...   works and lazily resumes the coroutine for each element.

Generator<long long> primes();                     // infinite: 2, 3, 5, 7, ...
Generator<std::string> tokens(std::string text);   // splits on spaces lazily (consecutive spaces produce no empty tokens)
Generator<int> merge_sorted(std::vector<int> a, std::vector<int> b);   // yields the merge of two sorted vectors
```

Requirements:
- **Lazy:** nothing runs until the first element is requested (`initial_suspend` returns `std::suspend_always`).
- An exception thrown inside the coroutine must propagate to the consumer when it advances. Store it with `std::current_exception()` in `unhandled_exception` and rethrow it from the iterator's `++`/`begin`.
- Coroutine parameters must be taken **by value**, because the frame outlives the call expression. (Why is `tokens(const std::string&)` dangerous?)

The driver also counts how many prime candidates were tested, to prove laziness.

## Starter
```cpp
#include <coroutine>
#include <exception>
#include <string>
#include <vector>

template <typename T>
class Generator {
public:
    struct promise_type;
};
```

## Driver
```cpp
#include <iostream>
#include <utility>

long long g_tested = 0;

Generator<int> faulty() {
    co_yield 1;
    co_yield 2;
    throw std::runtime_error("sensor failure");
}

int main() {
    int which;
    std::cin >> which;
    if (which == 1) {
        int count = 0;
        for (long long p : primes()) {
            std::cout << p << ' ';
            if (++count == 10) break;
        }
        std::cout << "\ntested " << g_tested << " candidates\n";
        auto gen = tokens("  move  forward 10   meters ");
        for (const std::string& t : gen) std::cout << '[' << t << ']';
        std::cout << '\n';
        for (int x : merge_sorted({1, 4, 9}, {2, 3, 10, 11})) std::cout << x << ' ';
        std::cout << '\n';
    } else {
        Generator<int> g = faulty();
        Generator<int> moved = std::move(g);            // move-only RAII handle
        try {
            for (int x : moved) std::cout << "got " << x << '\n';
        } catch (const std::runtime_error& e) {
            std::cout << "caught: " << e.what() << '\n';
        }
        auto lazy = primes();
        std::cout << "created, tested " << g_tested << '\n';   // still 0: nothing ran yet
        long long sum = 0;
        int n = 0;
        for (long long p : lazy) { sum += p; if (++n == 1000) break; }
        std::cout << "sum of first 1000 primes = " << sum << '\n';
        for (int x : merge_sorted({}, {})) std::cout << x;
        std::cout << "empty merge done\n";
        for (auto& t : tokens("")) std::cout << t;
        std::cout << "empty tokens done\n";
    }
}
```

## Tests
=== sample
1
---
2 3 5 7 11 13 17 19 23 29 
tested 28 candidates
[move][forward][10][meters]
1 2 3 4 9 10 11 
=== hidden
2
---
got 1
got 2
caught: sensor failure
created, tested 0
sum of first 1000 primes = 3682913
empty merge done
empty tokens done

## Hints
- `promise_type` needs: `get_return_object()`, `initial_suspend()`, `final_suspend() noexcept` (both returning `std::suspend_always`), `yield_value(T v)` (store the value, return `std::suspend_always`), `return_void()` and `unhandled_exception()`.
- The iterator holds a `std::coroutine_handle<promise_type>`. `begin()` resumes once (to produce the first value), `++` resumes again, and the iterator equals `end()` (use `std::default_sentinel_t`) when `handle.done()`.
- After each `resume()`, check `promise().exception` and rethrow it.
- Destroy the handle in `~Generator()`. Make the class move-only: delete the copy operations, and in the move constructor `std::exchange` the handle with `nullptr`.
- `primes()` must increment the global `g_tested` for every candidate it checks.

## Solution
```cpp
#include <coroutine>
#include <exception>
#include <string>
#include <vector>
#include <optional>
#include <utility>
#include <iterator>

template <typename T>
class Generator {
public:
    struct promise_type {
        std::optional<T> value;
        std::exception_ptr exception;

        Generator get_return_object() { return Generator{std::coroutine_handle<promise_type>::from_promise(*this)}; }
        std::suspend_always initial_suspend() noexcept { return {}; }    // lazy start
        std::suspend_always final_suspend() noexcept { return {}; }      // keep the frame until we destroy it
        std::suspend_always yield_value(T v) { value = std::move(v); return {}; }
        void return_void() noexcept {}
        void unhandled_exception() { exception = std::current_exception(); }
    };

    using handle = std::coroutine_handle<promise_type>;

    class iterator {
    public:
        using iterator_category = std::input_iterator_tag;
        using value_type = T;
        using difference_type = std::ptrdiff_t;
        iterator() = default;
        explicit iterator(handle h) : h_(h) { advance(); }
        const T& operator*() const { return *h_.promise().value; }
        iterator& operator++() { advance(); return *this; }
        void operator++(int) { advance(); }
        bool operator==(std::default_sentinel_t) const { return !h_ || h_.done(); }
    private:
        void advance() {
            h_.resume();                                      // run to the next co_yield (or the end)
            if (h_.promise().exception) std::rethrow_exception(h_.promise().exception);
        }
        handle h_{};
    };

    explicit Generator(handle h) : h_(h) {}
    Generator(Generator&& o) noexcept : h_(std::exchange(o.h_, {})) {}
    Generator& operator=(Generator&& o) noexcept {
        if (this != &o) { if (h_) h_.destroy(); h_ = std::exchange(o.h_, {}); }
        return *this;
    }
    Generator(const Generator&) = delete;
    Generator& operator=(const Generator&) = delete;
    ~Generator() { if (h_) h_.destroy(); }                    // RAII: free the coroutine frame

    iterator begin() { return iterator{h_}; }
    std::default_sentinel_t end() { return {}; }

private:
    handle h_;
};

extern long long g_tested;

Generator<long long> primes() {
    for (long long n = 2;; ++n) {
        ++g_tested;
        bool prime = true;
        for (long long d = 2; d * d <= n; ++d)
            if (n % d == 0) { prime = false; break; }
        if (prime) co_yield n;
    }
}

Generator<std::string> tokens(std::string text) {             // by value: the frame owns its copy
    std::size_t i = 0;
    while (i < text.size()) {
        while (i < text.size() && text[i] == ' ') ++i;
        std::size_t j = i;
        while (j < text.size() && text[j] != ' ') ++j;
        if (j > i) co_yield text.substr(i, j - i);
        i = j;
    }
}

Generator<int> merge_sorted(std::vector<int> a, std::vector<int> b) {
    std::size_t i = 0, j = 0;
    while (i < a.size() || j < b.size()) {
        if (j == b.size() || (i < a.size() && a[i] <= b[j])) co_yield a[i++];
        else co_yield b[j++];
    }
}
```

**How the pieces fit:**
- **The compiler transforms each coroutine into a state machine** whose locals (`n`, `i`, `text`) live in a heap-allocated *frame*. `co_yield v` calls `promise.yield_value(v)` and suspends. `handle.resume()` continues from that point.
- **`promise_type` is the customisation point:** it decides laziness (`initial_suspend`), where yielded values go, and what happens to exceptions. Capturing them with `std::current_exception` and rethrowing in the consumer makes errors flow naturally across the suspension boundary.
- **RAII for frames:** the `Generator` owns the handle and destroys the frame, which is why it must be move-only (two owners would double-destroy).
- **Laziness, proven:** creating `primes()` tests nothing, and taking 10 primes tests only 28 candidates (2 through 29). An infinite sequence costs only what you consume.
- **Dangling-reference trap:** a coroutine taking `const std::string&` would store the *reference* in its frame. If called with a temporary (`tokens("...")`), the string dies at the end of the call expression while the frame still points at it. Taking parameters by value copies them into the frame.
