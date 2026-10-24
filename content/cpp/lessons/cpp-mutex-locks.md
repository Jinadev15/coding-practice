# Mutexes and Locks

When threads share data and at least one writes, you need **synchronisation**. Otherwise you have a **data race**, which in C++ is **undefined behaviour**, not just "wrong numbers". A **mutex** (mutual exclusion) lets one thread at a time into a critical section. C++ wraps mutexes in RAII lock types (`lock_guard`, `unique_lock`, `scoped_lock`, `shared_lock`) so that locks are always released, even on exceptions. This lesson covers them, plus how to avoid deadlock.

## 1. Data races are undefined behaviour

```cpp
int counter = 0;
void inc() { for (int i = 0; i < 1'000'000; ++i) ++counter; }   // a read-modify-write

std::thread a(inc), b(inc);
a.join(); b.join();
std::cout << counter;   // anything: lost updates, or worse; the compiler may assume no other thread exists
```

> [!DANGER]
> The C++ memory model says that two threads accessing the same memory location, at least one writing, without synchronisation, is a **data race = undefined behaviour**. The optimiser may keep values in registers, reorder operations or tear writes. Detect races with **ThreadSanitizer**: `g++ -fsanitize=thread -g`.

## 2. `std::mutex` + `std::lock_guard`

```cpp
#include <mutex>

std::mutex m;
int counter = 0;

void inc() {
    for (int i = 0; i < 1'000'000; ++i) {
        std::lock_guard<std::mutex> lock(m);     // lock() now, unlock() at scope exit, even on exceptions
        ++counter;
    }
}
```

Never call `m.lock()`/`m.unlock()` by hand: an early `return` or exception leaves it locked forever.

> [!TIP]
> Keep critical sections short, and design for **less sharing**: give each thread its own data, then combine at the end (thread-local partial sums, then one reduction). Locking a million times in a loop serialises the threads. Compute locally and lock once.

## 3. The lock types

| Type | Features | Use |
|---|---|---|
| `std::lock_guard<M>` | locks in its constructor, unlocks in its destructor; nothing else | the default for simple critical sections |
| `std::unique_lock<M>` | movable, can `unlock()`/`lock()` again, deferred or try locking, timeouts | **condition variables**, handing off ownership |
| `std::scoped_lock<Ms...>` (C++17) | locks **several mutexes at once, deadlock-free** | multi-resource operations |
| `std::shared_lock<SM>` | shared (reader) ownership of a `std::shared_mutex` | read-mostly data |

```cpp
std::unique_lock lk(m, std::defer_lock);   // don't lock yet
if (lk.try_lock()) { /* got it */ }
lk.unlock();                               // release early
```

## 4. Other mutex types

| Mutex | Purpose |
|---|---|
| `std::mutex` | basic, non-recursive |
| `std::recursive_mutex` | the same thread may lock it repeatedly (often a design smell) |
| `std::timed_mutex` | `try_lock_for(duration)`: give up after a timeout |
| `std::shared_mutex` (C++17) | many readers **or** one writer |

```cpp
class SensorRegistry {
    mutable std::shared_mutex m_;           // mutable: const getters still lock
    std::map<std::string, double> latest_;
public:
    double read(const std::string& k) const {
        std::shared_lock lock(m_);          // many readers at once
        return latest_.at(k);
    }
    void write(const std::string& k, double v) {
        std::unique_lock lock(m_);          // exclusive
        latest_[k] = v;
    }
};
```

## 5. Deadlock and `std::scoped_lock`

```cpp
void transfer(Account& a, Account& b, int amt) {
    std::lock_guard la(a.m);
    std::lock_guard lb(b.m);     // thread 1: transfer(x, y) and thread 2: transfer(y, x) can DEADLOCK
    ...
}

void transfer_safe(Account& a, Account& b, int amt) {
    std::scoped_lock lock(a.m, b.m);   // locks both using a deadlock-avoidance algorithm (std::lock)
    ...
}
```

Deadlock-avoidance rules: lock several mutexes with `std::scoped_lock`, **always acquire in a consistent global order**, never call unknown code (callbacks, virtual functions) while holding a lock, and never hold a lock while waiting on another thread's result.

## 6. One-time initialisation

```cpp
std::once_flag init_flag;
void init_driver() { std::call_once(init_flag, [] { open_serial_port(); }); }

Config& config() {                 // function-local statics are initialised thread-safely (C++11)
    static Config c = load_config();
    return c;
}
```

## 7. Exam-ready answers

> [!EXAM]
> **Mutexes and locks.** A data race, unsynchronised concurrent access to the same memory location where at least one access is a write, is undefined behaviour in C++. A `std::mutex` provides mutual exclusion; it should be managed with RAII lock objects so it is released on all paths including exceptions: `std::lock_guard` locks for the duration of a scope, `std::unique_lock` adds deferred, timed and re-lockable ownership and is required by condition variables, `std::scoped_lock` locks multiple mutexes at once using a deadlock-avoidance algorithm, and `std::shared_lock` with `std::shared_mutex` allows concurrent readers. Deadlock arises from circular waiting and is avoided by acquiring multiple locks together or in a consistent global order and by not holding locks while calling unknown code. `std::call_once` and function-local statics provide thread-safe one-time initialisation.

## 8. Cheat sheet

| Need | Code |
|---|---|
| protect a scope | `std::lock_guard lock(m);` |
| lock two mutexes safely | `std::scoped_lock lock(m1, m2);` |
| with a condition variable | `std::unique_lock lk(m);` |
| readers/writers | `std::shared_mutex` + `shared_lock` / `unique_lock` |
| lock in const methods | a `mutable std::mutex` member |
| once only | `std::call_once(flag, f)` |
| find races | `-fsanitize=thread` |

> [!INTERVIEW]
> **"What's the difference between `lock_guard`, `unique_lock` and `scoped_lock`?"** `lock_guard` is the minimal RAII wrapper: lock on construction, unlock on destruction, non-movable, no other operations. `unique_lock` owns a lock flexibly: deferred locking, `try_lock`, timeouts, manual unlock and relock, movable. That's required for `condition_variable::wait`, which must unlock and relock. `scoped_lock` (C++17) takes any number of mutexes and locks them all with a deadlock-avoidance algorithm, the right tool for operations spanning several resources, and with a single mutex it's like `lock_guard`. Use the simplest one that works.
