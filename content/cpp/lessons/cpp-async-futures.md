# Futures, Promises and async

Threads plus shared variables plus condition variables is low-level plumbing. C++11 also offers **task-based** concurrency: `std::async` runs a function asynchronously and returns a **`std::future`**, a one-shot channel that delivers the **result or the exception** when the work finishes. `std::promise` is the writing end of such a channel, and `std::packaged_task` wraps a callable so its result goes into a future. These are the pieces of a **thread pool**. This lesson covers all of them, plus their pitfalls.

## 1. `std::async` and `std::future`

```cpp
#include <future>

int expensive(int n) { /* ... */ return n * n; }

std::future<int> f = std::async(std::launch::async, expensive, 12);   // runs on another thread
do_other_work();
int result = f.get();             // blocks until ready; get() can be called ONCE
```

| Launch policy | Behaviour |
|---|---|
| `std::launch::async` | runs on a new thread (as if) immediately |
| `std::launch::deferred` | runs lazily **in the caller's thread** when `get()`/`wait()` is called |
| default (`async \| deferred`) | the implementation chooses: **don't rely on it** |

> [!DANGER]
> The future returned by `std::async` **blocks in its destructor** until the task completes. So `std::async(std::launch::async, f);` used as a statement (ignoring the result) runs **synchronously**: the temporary future's destructor waits right there. Keep the futures alive while you want concurrency:
> ```cpp
> std::vector<std::future<int>> futs;
> for (int i = 0; i < 8; ++i) futs.push_back(std::async(std::launch::async, work, i));
> for (auto& f : futs) total += f.get();
> ```

## 2. Exceptions travel through futures

```cpp
auto f = std::async(std::launch::async, [] () -> int {
    throw std::runtime_error("sensor offline");
});
try {
    f.get();                            // rethrows the task's exception HERE, in the caller
} catch (const std::exception& e) {
    std::cerr << e.what() << '\n';
}
```

This is the big advantage over raw threads, where an escaping exception terminates the program.

## 3. `std::promise`: set the result from anywhere

```cpp
std::promise<Frame> frame_promise;
std::future<Frame> frame_future = frame_promise.get_future();

std::thread camera([p = std::move(frame_promise)]() mutable {
    try {
        p.set_value(capture());        // fulfil the promise
    } catch (...) {
        p.set_exception(std::current_exception());
    }
});
Frame f = frame_future.get();
camera.join();
```

A promise destroyed without a value makes the future throw `std::future_error` (broken promise). `std::shared_future` allows multiple threads to `get()` the same result.

## 4. `std::packaged_task` and a thread pool

```cpp
std::packaged_task<int(int)> task([](int x) { return x + 1; });
std::future<int> f = task.get_future();
std::thread t(std::move(task), 41);   // or call task(41) on any thread later
std::cout << f.get();                  // 42
t.join();
```

`packaged_task` separates **what to compute** from **where and when**, which is exactly what a thread pool needs:

```cpp
class ThreadPool {
public:
    explicit ThreadPool(std::size_t n) {
        for (std::size_t i = 0; i < n; ++i)
            workers_.emplace_back([this](std::stop_token st) {
                for (;;) {
                    std::function<void()> job;
                    {
                        std::unique_lock lk(m_);
                        cv_.wait(lk, [&] { return stopping_ || !jobs_.empty(); });
                        if (stopping_ && jobs_.empty()) return;
                        job = std::move(jobs_.front());
                        jobs_.pop();
                    }
                    job();                                   // run outside the lock
                }
            });
    }
    template <class F, class... A>
    auto submit(F&& f, A&&... a) -> std::future<std::invoke_result_t<F, A...>> {
        using R = std::invoke_result_t<F, A...>;
        auto task = std::make_shared<std::packaged_task<R()>>(
            [f = std::forward<F>(f), ...a = std::forward<A>(a)]() mutable { return f(a...); });
        std::future<R> fut = task->get_future();
        { std::lock_guard lk(m_); jobs_.emplace([task] { (*task)(); }); }
        cv_.notify_one();
        return fut;
    }
    ~ThreadPool() {
        { std::lock_guard lk(m_); stopping_ = true; }
        cv_.notify_all();                                    // the jthreads join automatically
    }
private:
    std::mutex m_;
    std::condition_variable cv_;
    std::queue<std::function<void()>> jobs_;
    bool stopping_ = false;
    std::vector<std::jthread> workers_;                      // declared last: destroyed (joined) first
};
```

(A `shared_ptr` holds the move-only `packaged_task` because `std::function` requires copyable callables. C++23's `std::move_only_function` removes that need.)

## 5. When to use what

| Need | Tool |
|---|---|
| run one function in parallel and get its result | `std::async(std::launch::async, ...)` |
| a result produced by an event or a callback | `std::promise` / `std::future` |
| many small tasks, a bounded number of threads | a thread pool (`packaged_task` + a queue) |
| data-parallel loops | parallel algorithms (`std::execution::par`), OpenMP, TBB |
| continuous streams of messages | a blocking queue between threads |
| async I/O composition | coroutines / Asio, `std::execution` (C++26) |

`std::future` has no `then()` for continuations. Composing many async steps needs a library or coroutines.

## 6. Exam-ready answers

> [!EXAM]
> **Futures and promises.** A `std::future` is a handle to a result that will become available later; `get()` blocks until the result is ready and returns it, or rethrows the exception stored by the producing task, and may be called once (`std::shared_future` allows multiple retrievals). `std::async` runs a callable according to a launch policy, asynchronously on another thread or deferred until the result is requested, and returns a future whose destructor waits for an asynchronously launched task to complete. A `std::promise` is the producer end of a future, set with `set_value` or `set_exception`; `std::packaged_task` wraps a callable so that invoking it stores its result in an associated future, enabling thread pools that execute queued tasks on a fixed set of worker threads.

## 7. Cheat sheet

| Need | Code |
|---|---|
| run async | `auto f = std::async(std::launch::async, fn, args...);` |
| get the result or exception | `f.get()` |
| wait with a timeout | `f.wait_for(10ms) == std::future_status::ready` |
| set a result from elsewhere | `std::promise<T> p; p.set_value(v);` |
| propagate an error | `p.set_exception(std::current_exception());` |
| a task for a pool | `std::packaged_task<R()>` |
| many readers of one result | `std::shared_future<T>` |

> [!INTERVIEW]
> **"What's the gotcha with ignoring the return value of `std::async`?"** The future returned by `std::async` with the async policy blocks in its destructor until the task finishes. If you don't store it, the temporary future is destroyed at the end of the full expression, so the call waits right there and runs synchronously, silently removing all concurrency. Store the futures and call `get()` later. Also: the default launch policy may defer execution until `get()`, so specify `std::launch::async` when you need real parallelism, and remember that `get()` can be called only once.
