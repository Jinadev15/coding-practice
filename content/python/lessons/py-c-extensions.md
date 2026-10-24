# C Extensions, ctypes and Cython

Python's superpower in AI and robotics is that it's a **glue language**: NumPy, PyTorch, OpenCV, ROS 2's `rclpy` and most of the scientific stack are thin Python layers over C, C++, CUDA or Fortran. Knowing how Python calls native code lets you speed up hot loops, wrap existing C/C++ libraries (motor drivers, vendor SDKs) and understand what's happening under `import numpy`. This lesson surveys the options: **ctypes**, **cffi**, the **C API**, **Cython**, **pybind11/nanobind** and **Numba**, with their trade-offs.

## 1. The options at a glance

| Tool | You write | Compile step? | Best for |
|---|---|---|---|
| **ctypes** (stdlib) | pure Python declarations of C signatures | no (loads a `.so`/`.dll`) | quick calls into an existing C library |
| **cffi** | C declarations (copied from headers) + Python | optional | cleaner C library wrapping, PyPy-friendly |
| **C API** (`Python.h`) | C code using `PyObject*` | yes | maximum control (CPython's own modules) |
| **Cython** | Python-like `.pyx` with C type annotations | yes | speeding up Python loops, wrapping C |
| **pybind11 / nanobind** | C++ with binding macros | yes | wrapping **C++** classes and templates (PyTorch, Open3D) |
| **Numba** | plain Python + `@njit` | JIT at run time | numeric loops over NumPy arrays |

## 2. ctypes: call a C library with no compiler

```python
import ctypes, ctypes.util

libm = ctypes.CDLL(ctypes.util.find_library("m"))   # the C math library
libm.cos.argtypes = [ctypes.c_double]               # DECLARE the signature, or you get garbage
libm.cos.restype = ctypes.c_double
libm.cos(0.0)                                       # 1.0

# structs and pointers
class Point(ctypes.Structure):
    _fields_ = [("x", ctypes.c_double), ("y", ctypes.c_double)]

buf = (ctypes.c_int * 4)(1, 2, 3, 4)                # a C int[4]
lib = ctypes.CDLL("./libmotor.so")
lib.set_speeds.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_size_t]
lib.set_speeds(buf, 4)
```

> [!DANGER]
> ctypes does **no type checking against the real C function**. A wrong `argtypes`/`restype`, a buffer that's too small, or freeing memory the C side still uses will **crash the interpreter** (segfault), with no Python exception and no traceback. Always declare signatures, and keep wrapped calls in one small, well-tested module.

## 3. The C API in one example

```c
// fastsum.c: a minimal extension module
#define PY_SSIZE_T_CLEAN
#include <Python.h>

static PyObject *fastsum(PyObject *self, PyObject *args) {
    PyObject *seq;
    if (!PyArg_ParseTuple(args, "O", &seq)) return NULL;     // NULL means "an exception is set"
    PyObject *it = PyObject_GetIter(seq);
    if (!it) return NULL;
    long long total = 0;
    PyObject *item;
    while ((item = PyIter_Next(it))) {
        total += PyLong_AsLongLong(item);
        Py_DECREF(item);                                     // manual reference counting!
        if (PyErr_Occurred()) { Py_DECREF(it); return NULL; }
    }
    Py_DECREF(it);
    return PyLong_FromLongLong(total);
}

static PyMethodDef methods[] = {{"fastsum", fastsum, METH_VARARGS, "Sum integers."}, {NULL}};
static struct PyModuleDef mod = {PyModuleDef_HEAD_INIT, "fastsum", NULL, -1, methods};
PyMODINIT_FUNC PyInit_fastsum(void) { return PyModule_Create(&mod); }
```

You see the Python object model from the inside: everything is a `PyObject*`, **reference counts are managed by hand** (`Py_INCREF`/`Py_DECREF`, where a mistake means a leak or a use-after-free), and errors are signalled by returning `NULL` with an exception set. Long-running C code should release the GIL (`Py_BEGIN_ALLOW_THREADS` … `Py_END_ALLOW_THREADS`) so other threads can run.

## 4. Cython: Python syntax, C speed

```cython
# distances.pyx
def total_distance(double[:, ::1] pts):           # a typed memoryview over a NumPy array
    cdef Py_ssize_t i, n = pts.shape[0]
    cdef double total = 0, dx, dy
    for i in range(1, n):                          # compiles to a plain C loop
        dx = pts[i, 0] - pts[i - 1, 0]
        dy = pts[i, 1] - pts[i - 1, 1]
        total += (dx * dx + dy * dy) ** 0.5
    return total
```

Adding `cdef` types turns Python loops into C loops, typically **10–100× faster**. `cython -a` produces an HTML report highlighting the lines that still go through the Python C API (yellow).

## 5. pybind11: wrapping C++ for Python

```cpp
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
namespace py = pybind11;

class PID {
public:
    PID(double kp, double ki, double kd) : kp_(kp), ki_(ki), kd_(kd) {}
    double step(double error, double dt) { integral_ += error * dt; double d = (error - prev_) / dt; prev_ = error; return kp_ * error + ki_ * integral_ + kd_ * d; }
private:
    double kp_, ki_, kd_, integral_ = 0, prev_ = 0;
};

PYBIND11_MODULE(control, m) {
    py::class_<PID>(m, "PID")
        .def(py::init<double, double, double>(), py::arg("kp"), py::arg("ki"), py::arg("kd"))
        .def("step", &PID::step);
}
```

```python
from control import PID          # a C++ class used naturally from Python
pid = PID(kp=1.2, ki=0.1, kd=0.05)
u = pid.step(error=0.3, dt=0.01)
```

This is how robotics teams expose a fast C++ controller or planner to Python for scripting, testing and ML integration. `nanobind` is the newer, lighter successor by the same author.

## 6. Numba: a JIT for numeric Python

```python
from numba import njit
import numpy as np

@njit(cache=True)
def pairwise_min_dist(pts):           # plain Python loops, compiled to machine code via LLVM
    n = pts.shape[0]
    best = np.inf
    for i in range(n):
        for j in range(i + 1, n):
            d = ((pts[i] - pts[j]) ** 2).sum()
            if d < best:
                best = d
    return best ** 0.5
```

## 7. Exam-ready answers

> [!EXAM]
> **Extending Python with native code.** Python can call compiled code in several ways. `ctypes` (standard library) loads shared libraries at run time and calls C functions after their argument and return types are declared, without a compilation step but with no compile-time type checking. `cffi` parses C declarations to generate bindings. The CPython C API allows writing extension modules in C that manipulate `PyObject` pointers, manage reference counts manually and signal errors by returning NULL with an exception set; long-running native code can release the GIL. Cython compiles a Python-like language with optional static C types into C extensions, greatly accelerating loops. pybind11 and nanobind create bindings for C++ classes and functions, and Numba JIT-compiles numeric Python functions. Native extensions underpin the scientific Python ecosystem.

## 8. Cheat sheet

| Goal | Reach for |
|---|---|
| call one C function from a `.so` now | `ctypes` (declare `argtypes`/`restype`!) |
| wrap a C library cleanly | `cffi` |
| speed up a Python loop over arrays | Numba `@njit`, or Cython |
| expose C++ classes to Python | pybind11 / nanobind |
| write a core module with full control | the C API |
| let other threads run during native work | release the GIL |
| package and build | `scikit-build-core` / `meson-python` + `pyproject.toml` |

> [!INTERVIEW]
> **"You have a C++ motion planner and a Python ML pipeline. How do you connect them?"** Wrap the planner with pybind11 (or nanobind): expose the classes and methods, convert STL containers and Eigen matrices automatically (`pybind11/stl.h`, `eigen.h`), and accept NumPy arrays through the buffer protocol to avoid copies. Release the GIL around long computations (`py::call_guard<py::gil_scoped_release>`) so Python threads keep running. Build with CMake through `scikit-build-core` to produce a wheel. Alternatives: run the planner as a separate process communicating over ROS 2 topics or gRPC (looser coupling, process isolation, but serialisation latency), or `ctypes` for a plain C API (fragile for C++). Choose bindings for tight loops and low latency, and IPC for independence and fault isolation.
