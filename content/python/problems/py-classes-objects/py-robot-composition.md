---
id: py-robot-composition
title: Differential-Drive Robot
difficulty: Medium
order: 2
tags: classes, composition, objects collaborating
---
## Statement
Model a two-wheeled robot with **two classes**:

**`Motor(name, max_rpm)`**
- attribute `rpm` starts at 0
- `set_speed(rpm)` clamps the value to `[-max_rpm, max_rpm]`
- `describe()` → `"NAME:RPM"`

**`Robot(name, max_rpm)`**
- owns two `Motor` objects named `left` and `right`, each with the given `max_rpm`
- `drive(speed, turn)` sets left = speed − turn, right = speed + turn (each clamped by its motor)
- `stop()` sets both to 0
- `spin(rate)` sets left = −rate, right = +rate
- `status()` → `"NAME [left:RPM right:RPM]"`, built with the motors' `describe()`
- `heading_change()` → the turn tendency `right.rpm - left.rpm`

The Robot must **delegate** to the Motor methods. It must never clamp by itself.

## Starter
```python
class Motor:
    pass


class Robot:
    pass
```

## Driver
```python
name, max_rpm = input().split()
bot = Robot(name, int(max_rpm))
for line in iter(input, "END"):
    cmd, *args = line.split()
    getattr(bot, cmd)(*map(int, args))
    print(bot.status(), bot.heading_change())
print(type(bot.left).__name__, bot.left is not bot.right)
```

## Tests
=== sample
rover 1000
drive 500 100
drive 900 300
spin 2000
stop
END
---
rover [left:400 right:600] 200
rover [left:600 right:1000] 400
rover [left:-1000 right:1000] 2000
rover [left:0 right:0] 0
Motor True
=== hidden
arm 50
drive -10 -100
END
---
arm [left:50 right:-50] -100
Motor True

## Hints
- In `Robot.__init__`: `self.left = Motor("left", max_rpm)` and likewise for `right`.
- `status` combines `self.left.describe()` and `self.right.describe()`.

## Solution
Composition: a `Robot` **has** two `Motor`s. Each class does its own job: the motor knows its limits, and the robot knows the drive geometry.

```python
class Motor:
    def __init__(self, name, max_rpm):
        self.name = name
        self.max_rpm = max_rpm
        self.rpm = 0

    def set_speed(self, rpm):
        self.rpm = max(-self.max_rpm, min(self.max_rpm, rpm))

    def describe(self):
        return f"{self.name}:{self.rpm}"


class Robot:
    def __init__(self, name, max_rpm):
        self.name = name
        self.left = Motor("left", max_rpm)
        self.right = Motor("right", max_rpm)

    def drive(self, speed, turn):
        self.left.set_speed(speed - turn)
        self.right.set_speed(speed + turn)

    def stop(self):
        self.drive(0, 0)

    def spin(self, rate):
        self.left.set_speed(-rate)
        self.right.set_speed(rate)

    def status(self):
        return f"{self.name} [{self.left.describe()} {self.right.describe()}]"

    def heading_change(self):
        return self.right.rpm - self.left.rpm
```

Notice that `heading_change` uses the **clamped** speeds. Because the robot delegates, whatever the motors really do is what gets reported. If the robot clamped separately, the two could disagree. Reusing `drive(0, 0)` for `stop()` avoids duplicate logic.
