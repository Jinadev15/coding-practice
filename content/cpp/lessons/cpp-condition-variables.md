# Condition Variables

A mutex protects shared state. A **condition variable** lets threads **wait efficiently** until that state changes: "wait until the queue has an item", "wait until the frame is ready", "wait until shutdown is requested". Without one you'd busy-wait (spinning and burning a CPU core) or sleep-poll (adding latency). `std::condition_variable` is the building block for producer–consumer queues, thread pools, barriers and pipeline stages.

## 1. The pattern

```cpp
#include <condition_variable>
#include <mutex>
#include <queue>

std::mutex m;
std::condition_variable cv;
std::queue<int> jobs;
bool done = false;

void producer() {
    for (int i = 0; i < 10; ++i) {
        {
            std::lock_guard lock(m);
            jobs.push(i);
        }                               // unlock before notifying (avoids waking a thread that immediately blocks)
        cv.notify_one();
    }
    {
        std::lock_guard lock(m);
        done = true;
    }
    cv.notify_all();                    // wake every consumer so they can see `done`
}

void consumer() {
    for (;;) {
        std::unique_lock lock(m);
        cv.wait(lock, [] { return !jobs.empty() || done; });   // the predicate guards against spurious wake-ups
        if (jobs.empty()) return;      // done and drained
        int job = jobs.front();
        jobs.pop();
        lock.unlock();                 // process outside the lock
        process(job);
    }
}
```

## 2. What `wait` does

`cv.wait(lock, pred)` is equivalent to:

```cpp
while (!pred()) {
    cv.wait(lock);    // ATOMICALLY: release the mutex and sleep; on wake, re-acquire the mutex before returning
}
```

> [!KEY]
> - **Always use a predicate** (or a `while` loop). Wake-ups can be **spurious** (the OS can wake you for no reason), and by the time you re-acquire the mutex, another consumer may have taken the item.
> - The **state must change under the mutex** before notifying. If the producer sets `ready = true` without the lock, the consumer can check the predicate, decide to sleep, and miss the notification that happens in between: a **lost wake-up**, and the thread sleeps forever.
> - `wait` requires `std::unique_lock`, because it has to unlock and relock.

## 3. notify_one vs notify_all

| Call | Wakes | Use when |
|---|---|---|
| `notify_one()` | one waiting thread | one unit of work became available (a single item pushed) |
| `notify_all()` | all waiting threads | a state change everyone must observe (shutdown, a barrier released, a config changed) |

## 4. Timed waits

```cpp
using namespace std::chrono_literals;
std::unique_lock lock(m);
if (!cv.wait_for(lock, 50ms, [] { return frame_ready; })) {
    handle_timeout();                       // the predicate was still false after 50 ms: sensor stalled?
}
cv.wait_until(lock, deadline, pred);        // an absolute deadline, for fixed-rate loops
```

Robots use timed waits for watchdogs: if no new sensor frame arrives within the deadline, enter a safe state.

## 5. A reusable blocking queue

```cpp
template <typename T>
class BlockingQueue {
public:
    void push(T v) {
        { std::lock_guard l(m_); q_.push(std::move(v)); }
        cv_.notify_one();
    }
    std::optional<T> pop() {                     // blocks; nullopt after close() once drained
        std::unique_lock l(m_);
        cv_.wait(l, [&] { return !q_.empty() || closed_; });
        if (q_.empty()) return std::nullopt;
        T v = std::move(q_.front());
        q_.pop();
        return v;
    }
    void close() {
        { std::lock_guard l(m_); closed_ = true; }
        cv_.notify_all();
    }
private:
    std::mutex m_;
    std::condition_variable cv_;
    std::queue<T> q_;
    bool closed_ = false;
};
```

A bounded version adds a second condition variable ("not full") so producers block when the queue is full (backpressure).

## 6. C++20 alternatives

| Primitive | Semantics |
|---|---|
| `std::latch` | a one-shot countdown: threads `count_down()`, waiters `wait()` until it reaches zero (start gates, "all workers initialised") |
| `std::barrier` | a reusable phase barrier, with an optional completion function per phase |
| `std::counting_semaphore<N>` | `acquire()`/`release()` on a counter (resource pools, bounded queues) |
| `std::atomic<T>::wait/notify_one` | lightweight waiting on an atomic value |
| `std::condition_variable_any` + `std::stop_token` | waits that wake up when a `jthread` stop is requested |

## 7. Exam-ready answers

> [!EXAM]
> **Condition variables.** A condition variable allows threads to block until notified that some shared state, protected by an associated mutex, has changed. A waiting thread holds a `std::unique_lock` and calls `wait`, which atomically releases the mutex and suspends the thread, then re-acquires the mutex before returning. Because wake-ups may be spurious and the state may have changed again before the mutex is re-acquired, the condition must be re-checked in a loop or by passing a predicate to `wait`. The notifying thread modifies the state while holding the mutex, to avoid lost wake-ups, and then calls `notify_one` to wake a single waiter or `notify_all` to wake all of them. Timed variants (`wait_for`, `wait_until`) return when a timeout expires. Condition variables implement producer–consumer queues, thread pools and other blocking coordination.

## 8. Cheat sheet

| Need | Code |
|---|---|
| wait for a condition | `cv.wait(lk, [&]{ return cond; });` |
| signal one item | change the state under the lock, then `cv.notify_one()` |
| broadcast a state change | `cv.notify_all()` |
| a watchdog timeout | `if (!cv.wait_for(lk, 50ms, pred)) ...` |
| stop the consumers | set `closed = true` under the lock + `notify_all` |
| a one-shot gate | `std::latch` |
| phase sync | `std::barrier` |

> [!INTERVIEW]
> **"Why must you check the predicate in a loop when using a condition variable?"** For two reasons. First, spurious wake-ups: implementations may return from `wait` without any notification. Second, stolen wake-ups: between the notify and the moment the woken thread re-acquires the mutex, another thread can consume the item or change the state. In both cases the condition may be false after `wait` returns, so you must re-check it before proceeding. The predicate overload of `wait` does this loop for you. Also mention that the state must be modified under the same mutex, or wake-ups can be lost.
