# POSIX Threads

Threads run concurrently **within one process**, sharing its memory, file descriptors and heap. POSIX threads (pthreads) are the standard C threading API on Linux, macOS and most embedded RTOSes with a POSIX layer. Robotics middleware (ROS 2 executors), servers, and any program that uses multiple CPU cores rely on them. This lesson covers creating and joining threads, mutexes, condition variables, the producer–consumer pattern, read–write locks, thread-local storage, and how to avoid data races and deadlocks. (C11's `<threads.h>`, from the Modern C lesson, offers a similar portable API.)

## 1. Creating and joining threads

```c
#define _POSIX_C_SOURCE 200809L
#include <pthread.h>
#include <stdio.h>

typedef struct { int id; long long lo, hi, result; } Job;

static void *sum_range(void *arg) {
    Job *j = arg;
    long long s = 0;
    for (long long i = j->lo; i < j->hi; i++) s += i;
    j->result = s;                        /* each thread writes only its own Job: no race */
    return NULL;
}

int main(void) {
    enum { T = 4 };
    pthread_t th[T];
    Job jobs[T];
    long long N = 100000000, chunk = N / T;
    for (int i = 0; i < T; i++) {
        jobs[i] = (Job){i, i * chunk, i == T - 1 ? N : (i + 1) * chunk, 0};
        pthread_create(&th[i], NULL, sum_range, &jobs[i]);
    }
    long long total = 0;
    for (int i = 0; i < T; i++) {
        pthread_join(th[i], NULL);        /* wait, and make its writes visible to us */
        total += jobs[i].result;
    }
    printf("%lld\n", total);
}
```

Compile with `-pthread`. `pthread_join` is also a synchronisation point: everything the thread wrote is visible after the join returns. Detached threads (`pthread_detach`) clean up automatically but can't be joined.

> [!WARNING]
> Don't pass `&i` (the loop variable) as the thread argument. By the time the thread reads it, the loop may have changed it. Give each thread its own argument struct, as above.

## 2. Data races and mutexes

```c
static long long counter = 0;
static pthread_mutex_t lock = PTHREAD_MUTEX_INITIALIZER;

static void *work(void *arg) {
    (void)arg;
    for (int i = 0; i < 1000000; i++) {
        pthread_mutex_lock(&lock);
        counter++;                        /* critical section: one thread at a time */
        pthread_mutex_unlock(&lock);
    }
    return NULL;
}
```

> [!DANGER]
> A **data race** (two threads accessing the same memory, at least one writing, without synchronisation) is undefined behaviour in C11. `counter++` is a load, add and store, and unsynchronised threads lose updates. Detect races with `-fsanitize=thread`.

Locking per increment is slow. Prefer per-thread partial results combined at the end, or atomics (`atomic_fetch_add`) for simple counters.

## 3. Condition variables: waiting for a state change

A condition variable lets a thread sleep until another thread signals that some **predicate** over shared state might now be true. It's always used with a mutex and a `while` loop:

```c
typedef struct {
    int buf[16];
    int head, tail, count;
    pthread_mutex_t m;
    pthread_cond_t not_full, not_empty;
} Queue;

void q_push(Queue *q, int v) {
    pthread_mutex_lock(&q->m);
    while (q->count == 16)                        /* WHILE, not if: spurious wakeups and stolen slots */
        pthread_cond_wait(&q->not_full, &q->m);   /* atomically unlocks, sleeps, relocks */
    q->buf[q->tail] = v;
    q->tail = (q->tail + 1) % 16;
    q->count++;
    pthread_cond_signal(&q->not_empty);
    pthread_mutex_unlock(&q->m);
}

int q_pop(Queue *q) {
    pthread_mutex_lock(&q->m);
    while (q->count == 0)
        pthread_cond_wait(&q->not_empty, &q->m);
    int v = q->buf[q->head];
    q->head = (q->head + 1) % 16;
    q->count--;
    pthread_cond_signal(&q->not_full);
    pthread_mutex_unlock(&q->m);
    return v;
}
```

> [!KEY]
> - `pthread_cond_wait` must be called with the mutex held. It releases the mutex while sleeping and reacquires it before returning.
> - Always re-check the predicate in a `while` loop: wakeups can be **spurious**, and another thread may have consumed the item first.
> - `signal` wakes one waiter; `broadcast` wakes all (needed for shutdown flags, or when different waiters wait for different conditions on the same variable).

This **bounded producer–consumer queue** decouples a fast sensor-reading thread from a slower processing thread, and the bound provides backpressure.

### Shutdown

Add a `closed` flag protected by the mutex. A consumer waits `while (count == 0 && !closed)`. To close, set the flag and `broadcast` so every waiter wakes up and exits.

## 4. Deadlock and how to avoid it

A deadlock needs four conditions at once: mutual exclusion, hold-and-wait, no preemption, and circular wait. Break any one:

| Technique | How |
|---|---|
| **lock ordering** | every thread acquires locks in the same global order (e.g. by address or by id) |
| try-lock and back off | `pthread_mutex_trylock`, release everything on failure, retry |
| one lock | coarser locking, simpler but less parallel |
| no nested locking | design APIs so callbacks never run while holding a lock |

```c
void transfer(Account *a, Account *b, long amt) {
    Account *first = a < b ? a : b, *second = a < b ? b : a;   /* consistent order by address */
    pthread_mutex_lock(&first->m);
    pthread_mutex_lock(&second->m);
    a->balance -= amt; b->balance += amt;
    pthread_mutex_unlock(&second->m);
    pthread_mutex_unlock(&first->m);
}
```

## 5. Other primitives

| Primitive | Use |
|---|---|
| `pthread_rwlock_t` | many concurrent readers or one writer (config tables, maps) |
| `pthread_once` | thread-safe one-time initialisation |
| `pthread_barrier_t` | all threads wait at a point (phased parallel algorithms) |
| `sem_t` (`<semaphore.h>`) | counting semaphore (resource pools; `sem_post` is async-signal-safe) |
| `pthread_spinlock_t` | busy-waiting lock for very short sections (rarely better than a mutex) |
| `_Thread_local` / `__thread` / `pthread_key_t` | per-thread data (errno is thread-local) |
| `pthread_setaffinity_np` (Linux) | pin threads to cores (real-time control loops) |
| `SCHED_FIFO` + `pthread_attr_setschedparam` | real-time priorities for control threads |

## 6. Performance notes

- **False sharing**: per-thread counters packed into one cache line slow each other down. Pad each to 64 bytes (`_Alignas(64)`).
- **Lock contention** serialises the threads. Shrink critical sections, shard data, or use per-thread accumulation.
- **Amdahl's law**: with a serial fraction s, the speedup with N threads is ≤ 1 / (s + (1 − s)/N).
- Creating threads costs microseconds. Use a **thread pool** for many small tasks.

## 7. Exam-ready answers

> [!EXAM]
> **Mutexes and condition variables.** A mutex provides mutual exclusion: only the thread holding it may execute the protected critical section, which prevents data races on shared state and also establishes the memory-visibility ordering between threads. A condition variable lets threads wait efficiently for a predicate over shared state to become true: `pthread_cond_wait` atomically releases the associated mutex and blocks, reacquiring the mutex before returning, and other threads call `pthread_cond_signal` or `pthread_cond_broadcast` after changing the state. Because wakeups may be spurious and the state may change before the woken thread runs, the predicate must be re-checked in a loop. Together they implement patterns such as bounded producer–consumer queues.

## 8. Cheat sheet

| Need | pthreads |
|---|---|
| start/wait | `pthread_create` / `pthread_join` |
| protect shared data | `pthread_mutex_lock/unlock` |
| wait for a condition | `while (!pred) pthread_cond_wait(&cv, &m);` |
| wake waiters | `pthread_cond_signal` / `broadcast` |
| avoid deadlock | a global lock order |
| one-time init | `pthread_once` |
| readers/writer | `pthread_rwlock_t` |
| detect races | `-fsanitize=thread` |

> [!INTERVIEW]
> **"Why must `pthread_cond_wait` be in a while loop?"** For three reasons: spurious wakeups are allowed by POSIX; with `signal`, another thread may grab the resource between the signal and the woken thread reacquiring the mutex (a "stolen wakeup"); and with `broadcast`, several threads wake but only one can proceed. Re-checking the predicate under the mutex handles all three. Using `if` causes rare, timing-dependent bugs.
