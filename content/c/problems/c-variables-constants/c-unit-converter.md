---
id: c-unit-converter
title: Constants and Unit Conversion
difficulty: Easy
order: 1
tags: const, #define, enum, double
---
## Statement
A robot reports distances in **millimetres**, speeds in **encoder ticks per second**, and angles in **degrees**. Using **named constants** (no magic numbers in the calculations):

- `#define MM_PER_M 1000.0`
- `const double WHEEL_RADIUS_M = 0.05;` (5 cm)
- `enum { TICKS_PER_REV = 1024 };`
- `const double PI = 3.14159265358979323846;`

each input line is `mm ticks_per_s degrees`. Print `D m, V m/s, R rad`: the distance in metres (3 decimals), the linear speed in m/s (4 decimals: revolutions per second × 2πr) and the angle in radians (4 decimals).

## Starter
```c
#include <stdio.h>

#define MM_PER_M 1000.0
const double WHEEL_RADIUS_M = 0.05;
enum { TICKS_PER_REV = 1024 };
const double PI = 3.14159265358979323846;

int main(void) {
    double mm, ticks, deg;
    while (scanf("%lf %lf %lf", &mm, &ticks, &deg) == 3) {

    }
    return 0;
}
```

## Tests
=== sample
1500 1024 180
---
1.500 m, 0.3142 m/s, 3.1416 rad
=== hidden
0 0 0
250 512 90
-1000 -2048 -45
---
0.000 m, 0.0000 m/s, 0.0000 rad
0.250 m, 0.1571 m/s, 1.5708 rad
-1.000 m, -0.6283 m/s, -0.7854 rad

## Hints
- Named constants replace magic numbers: `#define` is textual replacement, `const double` is a typed read-only variable, and `enum { N = 1024 };` gives an integer constant.
- Speed: revolutions per second = ticks / TICKS_PER_REV, then multiply by the wheel circumference `2 * PI * WHEEL_RADIUS_M`.
- Use `%.3f` and `%.4f` in `printf` to control the decimals.

## Solution
```c
#include <stdio.h>

#define MM_PER_M 1000.0
const double WHEEL_RADIUS_M = 0.05;
enum { TICKS_PER_REV = 1024 };
const double PI = 3.14159265358979323846;

int main(void) {
    double mm, ticks, deg;
    while (scanf("%lf %lf %lf", &mm, &ticks, &deg) == 3) {
        double metres = mm / MM_PER_M;
        double revs_per_s = ticks / TICKS_PER_REV;
        double speed = revs_per_s * 2.0 * PI * WHEEL_RADIUS_M;
        double rad = deg * PI / 180.0;
        printf("%.3f m, %.4f m/s, %.4f rad\n", metres, speed, rad);
    }
    return 0;
}
```

`ticks / TICKS_PER_REV` is floating-point division because `ticks` is a `double`. With an `int ticks`, `512 / 1024` would be `0`. Named constants make the physics readable and keep each value defined once: change the wheel and you edit one line. `const` gives a typed variable, `#define` a textual macro, and `enum` a typed integer constant expression.
