---
id: py-ctypes-libc
title: Calling the C Library with ctypes
difficulty: Hard
order: 1
tags: ctypes, FFI, callbacks, structures, pointers
---
## Statement
Use **`ctypes`** to call real C functions from the system C library (`libc`) and math library (`libm`), no compiler required. Implement:

```python
def c_strlen(s: str) -> int                         # libc strlen on the UTF-8 bytes of s
def c_sqrt_all(xs: list[float]) -> list[float]       # libm sqrt for each value (declare argtypes/restype!)
def c_qsort(xs: list[int], descending=False) -> list[int]   # libc qsort with a PYTHON comparison callback (CFUNCTYPE)
def c_div(a: int, b: int) -> tuple[int, int]         # libc div(), which returns a struct div_t {int quot; int rem;}
def c_format(fmt: bytes, *ints: int) -> str          # libc snprintf into a ctypes buffer (64 bytes), integer args only
class Point(ctypes.Structure): _fields_ = [("x", ctypes.c_double), ("y", ctypes.c_double)]
def centroid(points: list[tuple[float, float]]) -> tuple[float, float]   # build a ctypes ARRAY of Point, then average in Python by reading the array
```

Rules:
- Load the libraries with `ctypes.CDLL(ctypes.util.find_library("c"))` and `find_library("m")`.
- Always set `argtypes` and `restype`. For example, `sqrt` returns a `double`: without `restype = c_double`, ctypes assumes `int` and you get garbage. (The driver checks that you declared it.)
- `c_qsort` must sort a `(c_int * n)` array **in place** via `libc.qsort`, with a comparison function written in Python and wrapped with `CFUNCTYPE(c_int, POINTER(c_int), POINTER(c_int))`. Keep a reference to the callback object while `qsort` runs.

## Starter
```python
import ctypes
import ctypes.util

libc = ctypes.CDLL(ctypes.util.find_library("c"))
libm = ctypes.CDLL(ctypes.util.find_library("m"))
```

## Driver
```python
import sys

assert libm.sqrt.restype is ctypes.c_double, "declare sqrt's restype"
cmds = sys.stdin.read().splitlines()
for line in cmds:
    name, _, arg = line.partition(" ")
    if name == "strlen":
        print("strlen:", c_strlen(arg))
    elif name == "sqrt":
        print("sqrt:", [round(v, 6) for v in c_sqrt_all([float(x) for x in arg.split()])])
    elif name == "qsort":
        xs = [int(x) for x in arg.split()]
        print("asc:", c_qsort(xs), "desc:", c_qsort(xs, descending=True), "original untouched:", xs == [int(x) for x in arg.split()])
    elif name == "div":
        a, b = map(int, arg.split())
        print("div:", c_div(a, b))
    elif name == "format":
        fmt, *nums = arg.split(" ")
        print("format:", c_format(fmt.encode(), *map(int, nums)))
    elif name == "centroid":
        vals = list(map(float, arg.split()))
        pts = list(zip(vals[::2], vals[1::2]))
        cx, cy = centroid(pts)
        print(f"centroid: ({cx:.3f}, {cy:.3f}) sizeof(Point)={ctypes.sizeof(Point)}")
```

## Tests
=== sample
strlen hello
strlen héllo
sqrt 4 2 0.25
qsort 5 -3 9 0 9 1
div 17 5
div -17 5
format id=%d,speed=%05d 7 42
centroid 0 0 4 0 4 3 0 3
---
strlen: 5
strlen: 6
sqrt: [2.0, 1.414214, 0.5]
asc: [-3, 0, 1, 5, 9, 9] desc: [9, 9, 5, 1, 0, -3] original untouched: True
div: (3, 2)
div: (-3, -2)
format: id=7,speed=00042
centroid: (2.000, 1.500) sizeof(Point)=16
=== hidden
strlen
sqrt 1e6 0
qsort 1
qsort 3 2 1 0 -1 -2 -3 2147483647 -2147483648
div 7 -2
format [%x|%o] 255 8
centroid 1.5 -2.5
---
strlen: 0
sqrt: [1000.0, 0.0]
asc: [1] desc: [1] original untouched: True
asc: [-2147483648, -3, -2, -1, 0, 1, 2, 3, 2147483647] desc: [2147483647, 3, 2, 1, 0, -1, -2, -3, -2147483648] original untouched: True
div: (-3, 1)
format: [ff|10]
centroid: (1.500, -2.500) sizeof(Point)=16

## Hints
- `libc.strlen.argtypes = [ctypes.c_char_p]; libc.strlen.restype = ctypes.c_size_t`, then call it with `s.encode()`.
- `CMP = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))`. The callback receives pointers, so read `a[0]` and `b[0]` and return −1, 0 or 1. Don't return `a[0] - b[0]`, which overflows for extreme ints.
- `qsort(base, count, size, cmp)`: argtypes `[c_void_p, c_size_t, c_size_t, CMP]`.
- `class DivT(ctypes.Structure): _fields_ = [("quot", c_int), ("rem", c_int)]` and `libc.div.restype = DivT`.
- `buf = ctypes.create_string_buffer(64)`; `libc.snprintf(buf, 64, fmt, *[ctypes.c_int(v) for v in ints])`, then `buf.value.decode()`. Variadic C functions need explicit ctypes types for their extra arguments.

## Solution
```python
import ctypes
import ctypes.util

libc = ctypes.CDLL(ctypes.util.find_library("c"))
libm = ctypes.CDLL(ctypes.util.find_library("m"))

libc.strlen.argtypes = [ctypes.c_char_p]
libc.strlen.restype = ctypes.c_size_t
libm.sqrt.argtypes = [ctypes.c_double]
libm.sqrt.restype = ctypes.c_double

CMP = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
libc.qsort.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_size_t, CMP]
libc.qsort.restype = None

class DivT(ctypes.Structure):
    _fields_ = [("quot", ctypes.c_int), ("rem", ctypes.c_int)]

libc.div.argtypes = [ctypes.c_int, ctypes.c_int]
libc.div.restype = DivT
libc.snprintf.restype = ctypes.c_int

class Point(ctypes.Structure):
    _fields_ = [("x", ctypes.c_double), ("y", ctypes.c_double)]


def c_strlen(s):
    return libc.strlen(s.encode("utf-8"))


def c_sqrt_all(xs):
    return [libm.sqrt(x) for x in xs]


def c_qsort(xs, descending=False):
    arr = (ctypes.c_int * len(xs))(*xs)                 # a C copy: the Python list stays untouched
    sign = -1 if descending else 1

    def compare(pa, pb):
        a, b = pa[0], pb[0]
        return sign * ((a > b) - (a < b))               # no subtraction overflow

    callback = CMP(compare)                             # keep a reference alive during the call
    libc.qsort(arr, len(arr), ctypes.sizeof(ctypes.c_int), callback)
    return list(arr)


def c_div(a, b):
    r = libc.div(a, b)
    return (r.quot, r.rem)


def c_format(fmt, *ints):
    buf = ctypes.create_string_buffer(64)
    libc.snprintf(buf, 64, fmt, *[ctypes.c_int(v) for v in ints])
    return buf.value.decode()


def centroid(points):
    arr = (Point * len(points))(*[Point(x, y) for x, y in points])   # contiguous C array of structs
    n = len(arr)
    return (sum(p.x for p in arr) / n, sum(p.y for p in arr) / n)
```

**What crossing the language boundary involves:**
- **Declaring signatures** (`argtypes`/`restype`) is mandatory discipline: ctypes can't read C headers, so a wrong declaration silently corrupts values or crashes. `strlen("héllo")` returns 6 because C counts UTF-8 **bytes**, not characters.
- **Callbacks from C into Python:** `CFUNCTYPE` creates a C-callable function pointer that runs Python code (and takes the GIL) every time `qsort` compares. That's convenient but slow per call, so real code keeps hot loops on one side of the boundary. You must also keep the callback object alive, or C calls freed memory.
- **Structs by value and arrays of structs:** `div` returns a `div_t` struct, mirrored with a `ctypes.Structure`. `(Point * n)` allocates a contiguous C array, the layout NumPy arrays and C APIs share (16 bytes per point).
- **Variadic functions** (`snprintf`) need explicit argument types, because C's default promotions can't be inferred from Python objects.
