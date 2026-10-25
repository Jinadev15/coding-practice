# Static and Shared Libraries

A library packages compiled code for reuse: libc, libm, OpenCV, the ROS 2 client libraries, a vendor's motor-driver SDK. In C you'll build and consume two kinds. **Static** archives (`.a`) are copied into the executable at link time. **Shared** objects (`.so` on Linux, `.dll` on Windows, `.dylib` on macOS) are loaded at run time and shared between processes. This lesson covers how to build both, how the linker resolves symbols, symbol visibility, how the dynamic loader finds libraries, ABI stability and versioning, and dynamic loading for plugins.

## 1. Building both kinds

```c
/* geo.c */
double area(double w, double h) { return w * h; }
static double helper(double x) { return x * 2; }            /* internal linkage: not exported */
double twice_area(double w, double h) { return helper(area(w, h)); }
```

```bash
gcc -c -fPIC geo.c                 # object file; -fPIC: position-independent code (required for .so)
ar rcs libgeo.a geo.o              # static archive = bundle of .o files with an index
gcc -shared -o libgeo.so geo.o     # shared object
nm libgeo.a                        # T = exported text symbol, t = local
```

```output
geo.o:
0000000000000000 T area
000000000000001e t helper
0000000000000036 T twice_area
```

Link a program against either: `gcc main.c -L. -lgeo -o app`. `-lgeo` searches for `libgeo.so` first, then `libgeo.a`, in the `-L` directories and then the system ones. Force static with `-l:libgeo.a` or `-static`.

## 2. Static vs shared

| | Static `.a` | Shared `.so` |
|---|---|---|
| Linking | code copied into the executable | reference recorded; loaded at startup |
| Executable size | larger | smaller |
| Memory | each process has its own copy | pages shared between processes |
| Updates | rebuild every program | replace the .so (security fixes!) |
| Deployment | one self-contained file | the .so must be found at run time |
| Startup | fastest | dynamic loading and relocation cost |
| Typical use | embedded firmware (no loader), small tools, containers | system libraries, big frameworks, plugins |

Microcontroller firmware is always statically linked: there's no OS loader.

## 3. How the static linker resolves symbols

The linker processes inputs **left to right**. It keeps a set of undefined symbols, and from an archive it pulls in only the members that define a currently undefined symbol.

> [!DANGER]
> The order matters: `gcc -lgeo main.c` fails with "undefined reference to `area`". When `libgeo.a` was scanned, nothing was undefined yet, so nothing was pulled in. Put libraries **after** the objects that use them, and dependent libraries before their dependencies: `-lopencv_imgproc -lopencv_core`. For mutually dependent archives, use `-Wl,--start-group ... -Wl,--end-group`.

Other link errors:
- "multiple definition of `x`": a non-static variable or function defined in a header included twice. Use `extern` in the header and define it in one `.c` file.
- "undefined reference": a missing `-l`, wrong order, a C++ name-mangling mismatch (fix with `extern "C"`), or a missing definition.

## 4. Symbol visibility

By default, every non-`static` function in a shared library is exported. That bloats the dynamic symbol table, slows loading, blocks optimisation, and turns internals into ABI you can never change. Export only the public API:

```c
/* geo_api.h */
#if defined(GEO_BUILD)
#  define GEO_API __attribute__((visibility("default")))
#else
#  define GEO_API
#endif
GEO_API double area(double w, double h);
```

Compile with `-fvisibility=hidden -DGEO_BUILD`, so only `GEO_API` symbols appear in `nm -D libgeo.so`. On Windows, the equivalent is `__declspec(dllexport/dllimport)`.

## 5. Finding shared libraries at run time

```bash
$ ./app
./app: error while loading shared libraries: libgeo.so: cannot open shared object file
```

The dynamic loader (`ld-linux.so`) searches, in order:
1. `DT_RPATH`/`DT_RUNPATH` embedded in the binary (`-Wl,-rpath,'$ORIGIN/../lib'`, where `$ORIGIN` is the executable's directory).
2. `LD_LIBRARY_PATH`.
3. `/etc/ld.so.cache` (rebuilt with `ldconfig` after installing to `/usr/local/lib`).
4. `/lib`, `/usr/lib`.

Diagnose with `ldd ./app` (resolved libraries), `readelf -d ./app` (NEEDED and RUNPATH entries), and `LD_DEBUG=libs ./app`. ROS 2 workspaces work by sourcing `setup.bash`, which extends `LD_LIBRARY_PATH` and `AMENT_PREFIX_PATH`.

## 6. ABI and versioning

The **API** is source compatibility. The **ABI** is binary compatibility: symbol names, function signatures, struct layouts and sizes, enum values, and calling conventions. Changes that **break the ABI** without breaking the API include:
- Adding a field to a public struct, which changes `sizeof` and field offsets in callers' code.
- Reordering enum values.
- Changing a parameter from `int` to `long`.
- Turning a function into a macro or an inline function.

Techniques for stable C ABIs:
- **Opaque handles**: `typedef struct Geo Geo; Geo *geo_create(void);`. Clients never see the layout (see the Master OOP module).
- **Size or version fields** in structs passed across the boundary: `struct Config { uint32_t size; ... }`. The library reads only the fields that fit in `size`, the pattern used by Win32 and Vulkan.
- **Only append** new functions and fields. Never reorder or remove.
- **sonames**: `gcc -shared -Wl,-soname,libgeo.so.1 -o libgeo.so.1.2.0`. The executable records `libgeo.so.1`, so compatible updates (1.2 to 1.3) drop in, and an incompatible major version (`.so.2`) installs side by side.

## 7. Dynamic loading: plugins

```c
#include <dlfcn.h>
void *h = dlopen("./libplanner_astar.so", RTLD_NOW | RTLD_LOCAL);
if (!h) { fprintf(stderr, "%s\n", dlerror()); return 1; }
typedef const struct PlannerApi *(*GetApi)(void);
GetApi get = (GetApi)dlsym(h, "planner_get_api");   /* one well-known entry point */
const struct PlannerApi *api = get();
if (api->abi_version != PLANNER_ABI_VERSION) { /* refuse incompatible plugins */ }
api->plan(...);
dlclose(h);
```

This is how ROS 2 loads components and `pluginlib` plugins (controllers, planners, costmap layers), and how GIMP, Python extension modules and game engines load code chosen at run time. The pattern is one exported function that returns a **versioned table of function pointers**: a vtable across a binary boundary.

> [!EXAM]
> **Compare static and shared libraries, and explain why link order matters for static archives.**
> A static library is an archive of object files whose needed members are copied into the executable at link time. The result is self-contained, but it's larger and must be relinked to pick up fixes. A shared library is loaded by the dynamic loader at run time and its pages are shared between processes, so executables are smaller and the library can be updated independently. The costs are run-time lookup (rpath, `LD_LIBRARY_PATH`, the ld.so cache) and the need to keep the ABI stable. The static linker scans inputs left to right and extracts an archive member only to satisfy symbols that are undefined at that point, so a library must appear after the objects that reference it, and dependent libraries before their dependencies.
