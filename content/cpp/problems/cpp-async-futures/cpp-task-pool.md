---
id: cpp-task-pool
title: A Thread Pool Returning Futures
difficulty: Hard
order: 1
tags: thread pool, packaged_task, futures, condition_variable, perfect forwarding
time_limit: 3
---
## Statement
Implement a fixed-size **thread pool** whose `submit` returns a `std::future` of the task's result:

```cpp
class ThreadPool {
public:
    explicit ThreadPool(std::size_t workers);
    ~ThreadPool();                                   // finishes ALL queued tasks, then joins the workers
    template <class F, class... Args>
    auto submit(F&& f, Args&&... args) -> std::future<std::invoke_result_t<F, Args...>>;
    std::size_t pending() const;                     // tasks queued but not yet started
};
```

- Exceptions thrown by tasks must reach the caller through `future::get()`.
- `submit` after destruction has begun throws `std::runtime_error`, but the driver doesn't test this.
- Tasks may submit other tasks (nested submission must not deadlock, as long as the outer task doesn't block waiting on the inner one).

The driver submits many tasks with sleeps (to check parallelism within the time limit), tasks that throw, move-only arguments, and checks that the destructor drains the queue.

## Starter
```cpp
#include <future>
#include <functional>
#include <type_traits>

class ThreadPool {
public:
    explicit ThreadPool(std::size_t) {}
    template <class F, class... Args>
    auto submit(F&& f, Args&&... args) -> std::future<std::invoke_result_t<F, Args...>> {
        return std::async(std::launch::deferred, std::forward<F>(f), std::forward<Args>(args)...);
    }
    std::size_t pending() const { return 0; }
};
```

## Driver
```cpp
#include <iostream>
#include <vector>
#include <memory>
#include <atomic>
#include <chrono>
#include <thread>
#include <string>

int main() {
    using namespace std::chrono;
    int which;
    std::cin >> which;
    if (which == 1) {
        auto t0 = steady_clock::now();
        std::vector<std::future<int>> futs;
        {
            ThreadPool pool(8);
            for (int i = 0; i < 32; ++i)
                futs.push_back(pool.submit([](int x) { std::this_thread::sleep_for(milliseconds(100)); return x * x; }, i));
            long long sum = 0;
            for (auto& f : futs) sum += f.get();
            auto ms = duration_cast<milliseconds>(steady_clock::now() - t0).count();
            std::cout << "sum of squares: " << sum << " | parallel (< 1500 ms): " << (ms < 1500) << '\n';
            auto bad = pool.submit([]() -> int { throw std::runtime_error("motor fault"); });
            try { bad.get(); } catch (const std::runtime_error& e) { std::cout << "exception propagated: " << e.what() << '\n'; }
            auto p = std::make_unique<std::string>("owned");
            auto mv = pool.submit([](std::unique_ptr<std::string> s) { return *s + "!"; }, std::move(p));
            std::cout << "move-only argument: " << mv.get() << '\n';
            auto v = pool.submit([] { std::cout << "void task ran\n"; });
            v.get();
        }
    } else {
        std::atomic<int> done{0};
        {
            ThreadPool pool(2);
            for (int i = 0; i < 50; ++i)
                pool.submit([&done] { std::this_thread::sleep_for(std::chrono::milliseconds(2)); ++done; });
        }   // the destructor must finish all 50 queued tasks
        std::cout << "drained on destruction: " << done.load() << '\n';
        ThreadPool pool(3);
        auto outer = pool.submit([&pool] {
            auto inner = pool.submit([] { return 21; });
            return inner.get() * 2;                  // OK: other workers are free to run inner
        });
        std::cout << "nested submit: " << outer.get() << '\n';
    }
}
```

## Tests
=== sample
1
---
sum of squares: 10416 | parallel (< 1500 ms): 1
exception propagated: motor fault
move-only argument: owned!
void task ran
=== hidden
2
---
drained on destruction: 50
nested submit: 42

## Hints
- Members: `std::mutex m_; std::condition_variable cv_; std::queue<std::function<void()>> jobs_; bool stopping_ = false; std::vector<std::jthread> workers_;`. Declare `workers_` **last**, so the workers are joined before the other members are destroyed.
- `submit`: wrap the call in a `std::packaged_task<R()>` held by a `std::shared_ptr` (since `std::function` needs a copyable callable), take its future, push `[task] { (*task)(); }`, and `notify_one`.
- Bind the arguments into the task with a lambda init-capture pack: `[f = std::forward<F>(f), ...a = std::forward<Args>(args)]() mutable { return std::invoke(std::move(f), std::move(a)...); }`.
- Worker loop: wait until `stopping_ || !jobs_.empty()`, exit only when stopping **and** empty (to drain), and run each job outside the lock.

## Solution
```cpp
#include <future>
#include <functional>
#include <type_traits>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <queue>
#include <vector>
#include <memory>
#include <stdexcept>

class ThreadPool {
public:
    explicit ThreadPool(std::size_t workers) {
        for (std::size_t i = 0; i < workers; ++i)
            workers_.emplace_back([this] { run(); });
    }

    ~ThreadPool() {
        {
            std::lock_guard lk(m_);
            stopping_ = true;
        }
        cv_.notify_all();
        workers_.clear();                                    // join: the workers drain the queue first
    }

    template <class F, class... Args>
    auto submit(F&& f, Args&&... args) -> std::future<std::invoke_result_t<F, Args...>> {
        using R = std::invoke_result_t<F, Args...>;
        auto task = std::make_shared<std::packaged_task<R()>>(
            [f = std::forward<F>(f), ... a = std::forward<Args>(args)]() mutable -> R {
                return std::invoke(std::move(f), std::move(a)...);
            });
        std::future<R> fut = task->get_future();
        {
            std::lock_guard lk(m_);
            if (stopping_) throw std::runtime_error("submit on a stopping pool");
            jobs_.emplace([task] { (*task)(); });
        }
        cv_.notify_one();
        return fut;
    }

    std::size_t pending() const {
        std::lock_guard lk(m_);
        return jobs_.size();
    }

private:
    void run() {
        for (;;) {
            std::function<void()> job;
            {
                std::unique_lock lk(m_);
                cv_.wait(lk, [&] { return stopping_ || !jobs_.empty(); });
                if (stopping_ && jobs_.empty()) return;      // drain everything before exiting
                job = std::move(jobs_.front());
                jobs_.pop();
            }
            job();                                           // packaged_task stores the result or exception in the future
        }
    }

    mutable std::mutex m_;
    std::condition_variable cv_;
    std::queue<std::function<void()>> jobs_;
    bool stopping_ = false;
    std::vector<std::jthread> workers_;                      // last: joined before the queue is destroyed
};
```

- **`packaged_task` + `future`:** the task object stores the return value, *or the exception*, in its shared state, so callers get results and errors through `get()` without any extra plumbing. That's what makes thread pools composable.
- **Type erasure:** the queue holds `std::function<void()>`, any job regardless of its return type. The `shared_ptr` makes the move-only `packaged_task` copyable for `std::function` (C++23's `std::move_only_function` removes this need).
- **Perfect forwarding with a pack init-capture** (`...a = std::forward<Args>(args)`, C++20) moves move-only arguments like `unique_ptr` into the task.
- **Graceful shutdown:** the destructor sets `stopping_` and joins, and the workers exit only once the queue is empty, so no submitted work is lost. Member declaration order guarantees the queue outlives the workers.
