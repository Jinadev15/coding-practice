# std::thread

C++11 brought threads into the standard library: portable, type-safe, RAII-friendly concurrency, without platform APIs like pthreads or Win32. Unlike Python, C++ threads run **truly in parallel** on multiple cores, which is exactly why robot perception pipelines, game engines and trading systems are written in C++. And unlike Python, a mistake in C++ concurrency is **undefined behaviour**. This lesson covers creating threads, passing arguments safely, joining and detaching, `std::jthread`, and thread lifetime rules.

## 1. Creating and joining

```cpp
#include <thread>
#include <iostream>

void scan(int sensor_id, int samples) {
    for (int i = 0; i < samples; ++i) { /* read the sensor */ }
}

int main() {
    std::thread t1(scan, 1, 1000);                 // starts running immediately
    std::thread t2([] { std::cout << "lambda thread\n"; });
    t1.join();                                     // wait for completion
    t2.join();
    std::cout << std::thread::hardware_concurrency() << " hardware threads\n";
}
```

> [!DANGER]
> A `std::thread` that is still **joinable** when it's destroyed calls **`std::terminate()`**: the program aborts. Every `std::thread` must be `join()`ed or `detach()`ed before its destructor runs, **including when an exception is thrown** between creation and join. Use `std::jthread` (below) or an RAII guard.

## 2. Passing arguments: copies by default

Arguments are **copied** (or moved) into the new thread's storage, even if the function takes a reference:

```cpp
void fill(std::vector<int>& v) { v.push_back(42); }

std::vector<int> data;
// std::thread t(fill, data);              // compile error: can't bind a copied temporary to a non-const reference
std::thread t(fill, std::ref(data));       // std::ref passes a real reference
t.join();

auto buf = std::make_unique<Frame>();
std::thread t2(process, std::move(buf));   // move-only types must be moved in
```

> [!WARNING]
> Passing a reference or pointer to a **local variable** into a thread that outlives the scope creates a dangling reference: undefined behaviour. The same applies to lambdas capturing by reference (`[&]`) in detached threads. Make sure the referenced object outlives the thread, or capture by value.

## 3. `std::jthread` (C++20): RAII threads

```cpp
#include <thread>
#include <stop_token>

void worker(std::stop_token st, int id) {
    while (!st.stop_requested()) {         // cooperative cancellation
        do_work(id);
    }
}

{
    std::jthread t(worker, 7);             // the stop_token is passed automatically as the first argument
    std::this_thread::sleep_for(std::chrono::milliseconds(100));
}                                          // the destructor calls request_stop(), then join(): no terminate, no leak
```

`jthread` joins automatically and supports **cooperative cancellation** through `std::stop_token` / `std::stop_source`, and `std::stop_callback` can run code when a stop is requested. Prefer `jthread` in new code.

## 4. Detaching, and why to avoid it

```cpp
std::thread logger(log_loop);
logger.detach();                           // runs independently; can no longer be joined
```

Detached threads keep running after `main` returns, and get killed abruptly at process exit while possibly using destroyed globals. Their errors are unobservable. Use them rarely. Background services should be joinable threads with a stop mechanism.

## 5. Thread identity, sleeping and yielding

```cpp
std::this_thread::get_id();
std::this_thread::sleep_for(std::chrono::milliseconds(10));
std::this_thread::sleep_until(next_tick);   // fixed-rate control loops: avoid drift
std::this_thread::yield();                  // hint: let others run
thread_local int scratch = 0;               // one instance per thread
```

```cpp
// a fixed-rate 100 Hz loop without drift
auto next = std::chrono::steady_clock::now();
while (running) {
    control_step();
    next += std::chrono::milliseconds(10);
    std::this_thread::sleep_until(next);    // sleep_for(10ms) would accumulate the step's own duration
}
```

## 6. Exceptions in threads

An exception escaping a thread function calls `std::terminate`. To transfer errors to another thread, catch them and store them in a `std::exception_ptr`, or use `std::async`/`std::promise`, which carry exceptions through futures (later lesson).

## 7. Exam-ready answers

> [!EXAM]
> **`std::thread`.** A `std::thread` object starts a new thread of execution running a callable with the given arguments, which are copied or moved into thread-owned storage, so references must be passed with `std::ref` and the referenced objects must outlive the thread. Before destruction a thread must be joined, which waits for it to finish, or detached, which lets it run independently; destroying a joinable thread calls `std::terminate`. `std::jthread` (C++20) joins automatically in its destructor and supports cooperative cancellation through stop tokens. Exceptions escaping a thread's function terminate the program. `std::thread::hardware_concurrency` reports the number of hardware threads, and `std::this_thread` provides sleeping, yielding and the current thread's identifier. Unlike CPython, C++ threads execute in parallel on multiple cores.

## 8. Cheat sheet

| Need | Code |
|---|---|
| start a thread | `std::thread t(f, args...);` / `std::jthread t(f, args...);` |
| wait | `t.join();` (automatic for `jthread`) |
| pass by reference | `std::ref(x)` / `std::cref(x)` |
| pass a move-only type | `std::move(p)` |
| cancellable worker | `jthread` + `std::stop_token` |
| fixed-rate loop | `sleep_until(next += period)` |
| per-thread variable | `thread_local` |
| core count | `std::thread::hardware_concurrency()` |

> [!INTERVIEW]
> **"What happens if a `std::thread` object goes out of scope without `join()` or `detach()`?"** Its destructor calls `std::terminate()`, aborting the program. The design forces you to decide explicitly what happens to the thread, rather than silently leaking or blocking. The trap is exceptions thrown between creating the thread and calling `join()`: the stack unwinds, the joinable thread is destroyed, and the program terminates. The solutions are RAII: `std::jthread` (C++20) joins in its destructor, or a scope guard. Also mention passing references with `std::ref` and object lifetimes.
