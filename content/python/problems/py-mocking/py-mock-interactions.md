---
id: py-mock-interactions
title: Verify Interactions with Mocks
difficulty: Medium
order: 1
tags: unittest.mock, Mock, side_effect, assert_called_with, test doubles
---
## Statement
A robot fleet service sends an overheat alert. The function under test talks to three collaborators, so it is tested with **test doubles**, not real hardware:

```python
def check_motor(motor_id, sensor, notifier, clock, limit=80.0):
    """Read sensor.temperature(motor_id).
    - If the reading is above `limit`, call notifier.send(motor_id, f"{motor_id} overheating: {temp:.1f}C at {clock()}")
      exactly once and return "ALERT".
    - If reading is <= limit, do not notify and return "OK".
    - If sensor.temperature raises TimeoutError, retry ONCE; if it fails again, call
      notifier.send(motor_id, f"{motor_id} sensor offline at {clock()}") and return "OFFLINE".
    - clock() is called only when a message is actually sent (exactly once per message)."""
```

Write `check(check_motor)` that uses **`unittest.mock.Mock`** to build the sensor, notifier and clock, and raises `AssertionError` if the implementation is wrong. The judge runs it against the correct version (must pass) and against mutants that each break one interaction rule (each must be caught).

Useful tools: `Mock(return_value=...)`, `Mock(side_effect=[TimeoutError(), 75.0])` (a list makes successive calls return or raise the items in turn), `m.assert_called_once_with(...)`, `m.assert_not_called()`, `m.call_count`, `m.call_args_list`.

## Starter
```python
from unittest.mock import Mock

def check(check_motor):
    sensor = Mock()
    sensor.temperature.return_value = 90.0
    notifier = Mock()
    clock = Mock(return_value="12:00")
    assert check_motor("m1", sensor, notifier, clock) == "ALERT"
```

## Driver
```python
import sys

def correct(motor_id, sensor, notifier, clock, limit=80.0):
    try:
        temp = sensor.temperature(motor_id)
    except TimeoutError:
        try:
            temp = sensor.temperature(motor_id)
        except TimeoutError:
            notifier.send(motor_id, f"{motor_id} sensor offline at {clock()}")
            return "OFFLINE"
    if temp > limit:
        notifier.send(motor_id, f"{motor_id} overheating: {temp:.1f}C at {clock()}")
        return "ALERT"
    return "OK"

def m_ge_limit(motor_id, sensor, notifier, clock, limit=80.0):
    temp = None
    try:
        temp = sensor.temperature(motor_id)
    except TimeoutError:
        try:
            temp = sensor.temperature(motor_id)
        except TimeoutError:
            notifier.send(motor_id, f"{motor_id} sensor offline at {clock()}")
            return "OFFLINE"
    if temp >= limit:
        notifier.send(motor_id, f"{motor_id} overheating: {temp:.1f}C at {clock()}")
        return "ALERT"
    return "OK"

def m_no_retry(motor_id, sensor, notifier, clock, limit=80.0):
    try:
        temp = sensor.temperature(motor_id)
    except TimeoutError:
        notifier.send(motor_id, f"{motor_id} sensor offline at {clock()}")
        return "OFFLINE"
    if temp > limit:
        notifier.send(motor_id, f"{motor_id} overheating: {temp:.1f}C at {clock()}")
        return "ALERT"
    return "OK"

def m_double_send(motor_id, sensor, notifier, clock, limit=80.0):
    r = correct(motor_id, sensor, notifier, clock, limit)
    if r == "ALERT":
        notifier.send(motor_id, "repeat")
    return r

def m_eager_clock(motor_id, sensor, notifier, clock, limit=80.0):
    now = clock()
    try:
        temp = sensor.temperature(motor_id)
    except TimeoutError:
        try:
            temp = sensor.temperature(motor_id)
        except TimeoutError:
            notifier.send(motor_id, f"{motor_id} sensor offline at {now}")
            return "OFFLINE"
    if temp > limit:
        notifier.send(motor_id, f"{motor_id} overheating: {temp:.1f}C at {now}")
        return "ALERT"
    return "OK"

def m_wrong_id(motor_id, sensor, notifier, clock, limit=80.0):
    try:
        temp = sensor.temperature("all")
    except TimeoutError:
        try:
            temp = sensor.temperature("all")
        except TimeoutError:
            notifier.send(motor_id, f"{motor_id} sensor offline at {clock()}")
            return "OFFLINE"
    if temp > limit:
        notifier.send(motor_id, f"{motor_id} overheating: {temp:.1f}C at {clock()}")
        return "ALERT"
    return "OK"

def m_bad_format(motor_id, sensor, notifier, clock, limit=80.0):
    try:
        temp = sensor.temperature(motor_id)
    except TimeoutError:
        try:
            temp = sensor.temperature(motor_id)
        except TimeoutError:
            notifier.send(motor_id, f"{motor_id} sensor offline at {clock()}")
            return "OFFLINE"
    if temp > limit:
        notifier.send(motor_id, f"{motor_id} overheating: {temp}C at {clock()}")
        return "ALERT"
    return "OK"

def m_ignore_limit(motor_id, sensor, notifier, clock, limit=80.0):
    return correct(motor_id, sensor, notifier, clock, 80.0)

def m_retry_forever(motor_id, sensor, notifier, clock, limit=80.0):
    for _ in range(3):
        try:
            temp = sensor.temperature(motor_id)
            break
        except TimeoutError:
            continue
    else:
        notifier.send(motor_id, f"{motor_id} sensor offline at {clock()}")
        return "OFFLINE"
    if temp > limit:
        notifier.send(motor_id, f"{motor_id} overheating: {temp:.1f}C at {clock()}")
        return "ALERT"
    return "OK"

MUTANTS = [("ge_limit", m_ge_limit), ("no_retry", m_no_retry), ("double_send", m_double_send),
           ("eager_clock", m_eager_clock), ("wrong_id", m_wrong_id), ("bad_format", m_bad_format),
           ("ignore_limit", m_ignore_limit), ("retry_three_times", m_retry_forever)]

def caught(impl):
    try:
        check(impl)
    except Exception:
        return True
    return False

which = sys.stdin.read().split() or [n for n, _ in MUTANTS]
print("passes on the correct implementation:", not caught(correct))
for name, impl in MUTANTS:
    if name in which:
        print(f"mutant {name}: {'killed' if caught(impl) else 'SURVIVED'}")
```

## Tests
=== sample
double_send no_retry
---
passes on the correct implementation: True
mutant no_retry: killed
mutant double_send: killed
=== hidden
ge_limit no_retry double_send eager_clock wrong_id bad_format ignore_limit retry_three_times
---
passes on the correct implementation: True
mutant ge_limit: killed
mutant no_retry: killed
mutant double_send: killed
mutant eager_clock: killed
mutant wrong_id: killed
mutant bad_format: killed
mutant ignore_limit: killed
mutant retry_three_times: killed

## Hints
- Use a temperature like `91.04`, so `{temp:.1f}` (`91.0`) and `{temp}` (`91.04`) produce different strings, then `notifier.send.assert_called_once_with("m1", "m1 overheating: 91.0C at 12:00")`.
- For the OK path, assert both `notifier.send.assert_not_called()` **and** `clock.assert_not_called()`.
- Retry: `side_effect=[TimeoutError(), 70.0]` must return `"OK"` with no message, and `side_effect=[TimeoutError(), TimeoutError(), 70.0]` must return `"OFFLINE"` after exactly 2 sensor calls.
- Test the boundary (`80.0` is OK) and a custom `limit=` argument.

## Solution
```python
from unittest.mock import Mock

def check(check_motor):
    def doubles(temps, now="12:00"):
        sensor = Mock()
        if isinstance(temps, list):
            sensor.temperature.side_effect = temps
        else:
            sensor.temperature.return_value = temps
        return sensor, Mock(), Mock(return_value=now)

    # alert path: exact message, one send, one clock read, sensor asked about this motor
    s, n, c = doubles(91.04)
    assert check_motor("m1", s, n, c) == "ALERT"
    n.send.assert_called_once_with("m1", "m1 overheating: 91.0C at 12:00")
    c.assert_called_once_with()
    s.temperature.assert_called_once_with("m1")

    # boundary: exactly the limit is OK; nothing sent, clock untouched
    s, n, c = doubles(80.0)
    assert check_motor("m2", s, n, c) == "OK"
    n.send.assert_not_called()
    c.assert_not_called()

    # custom limit is honoured
    s, n, c = doubles(60.0)
    assert check_motor("m3", s, n, c, limit=50.0) == "ALERT"

    # one timeout, then success: retried, no message
    s, n, c = doubles([TimeoutError(), 70.0])
    assert check_motor("m4", s, n, c) == "OK"
    assert s.temperature.call_count == 2
    n.send.assert_not_called()

    # two timeouts: offline after exactly two attempts
    s, n, c = doubles([TimeoutError(), TimeoutError(), 70.0], now="13:30")
    assert check_motor("m5", s, n, c) == "OFFLINE"
    assert s.temperature.call_count == 2
    n.send.assert_called_once_with("m5", "m5 sensor offline at 13:30")
```

Each block pins one rule of the contract. Mocks let you assert on **interactions** (who was called, with what, how many times) as well as return values:
- `assert_called_once_with` catches duplicate sends and wrong formatting at once.
- `assert_not_called` on the clock catches the eager read. That's a real bug class: reading time or randomness when it isn't needed makes code harder to reason about.
- A `side_effect` list scripts a sequence of outcomes, which is the standard way to test retry logic without waiting on a real flaky sensor.
