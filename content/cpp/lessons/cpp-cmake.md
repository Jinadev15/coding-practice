# CMake in Depth

Real C++ projects aren't compiled with one `g++` command. They have libraries, executables, tests, third-party dependencies, multiple platforms and build types. **CMake** is the de-facto standard build-system generator: you describe *targets* and their *properties*, and CMake generates Makefiles or Ninja files, IDE projects, and compile databases. ROS 2 (`ament_cmake`), OpenCV, Eigen, LLVM and most robotics stacks use it. This lesson teaches **modern, target-based CMake**: targets, `PUBLIC`/`PRIVATE`/`INTERFACE` usage requirements, `find_package`, multi-directory projects, build types, testing with CTest, and installation, plus the anti-patterns to avoid.

## 1. The minimal project

```cmake
# CMakeLists.txt
cmake_minimum_required(VERSION 3.20)
project(robot_kit VERSION 1.2.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)                 # -std=c++20, not gnu++20
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)         # compile_commands.json for clangd / clang-tidy

add_executable(robot_app src/main.cpp)
```

```bash
cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release     # configure (out-of-source build)
cmake --build build -j                                       # build
ctest --test-dir build --output-on-failure                   # run the tests
```

> [!KEY]
> Always build **out of source** (`-B build`). Generated files never mix with sources, and deleting `build/` resets everything. The two phases are **configure** (`cmake -S -B`, which runs CMakeLists and finds dependencies) and **build** (`cmake --build`, which invokes Ninja or Make).

## 2. Targets and usage requirements

Modern CMake is about **targets** (libraries and executables) and the properties they propagate:

```cmake
add_library(kinematics src/fk.cpp src/ik.cpp)
target_include_directories(kinematics PUBLIC include)            # users of kinematics see include/
target_compile_features(kinematics PUBLIC cxx_std_20)
target_compile_options(kinematics PRIVATE -Wall -Wextra -Wpedantic)  # only when compiling kinematics itself
target_link_libraries(kinematics PUBLIC Eigen3::Eigen PRIVATE spdlog::spdlog)

add_executable(robot_app src/main.cpp)
target_link_libraries(robot_app PRIVATE kinematics)              # inherits include/ and Eigen automatically
```

| Keyword | Applies to the target itself | Propagates to consumers | Use for |
|---|---|---|---|
| `PRIVATE` | ✓ | ✗ | implementation details (warnings, internal deps) |
| `PUBLIC` | ✓ | ✓ | things in your public headers (Eigen types in the API) |
| `INTERFACE` | ✗ | ✓ | header-only libraries |

> [!KEY]
> Ask: does a *user* of my library need this to compile against my headers? If yes, use `PUBLIC` (or `INTERFACE` for header-only); if no, use `PRIVATE`. Getting this right is what makes large builds composable: dependencies flow through `target_link_libraries` instead of global variables.

**Anti-patterns** (old-style CMake to avoid):
- global `include_directories()`, `add_definitions()`, `link_libraries()`
- setting `CMAKE_CXX_FLAGS` for project-specific needs
- `file(GLOB …)` for sources (new files aren't picked up without re-running configure)
- hard-coded paths to libraries

## 3. Libraries: static, shared, header-only, object

```cmake
add_library(geom STATIC geom.cpp)          # .a: linked into the executable
add_library(drivers SHARED drivers.cpp)    # .so: loaded at run time (mind the ABI)
add_library(units INTERFACE)               # header-only
target_include_directories(units INTERFACE include)
add_library(robot::geom ALIAS geom)        # namespaced alias: a typo becomes a configure error, not a link error
```

`BUILD_SHARED_LIBS=ON` switches libraries created without an explicit type. Use `set_target_properties(drivers PROPERTIES VERSION 1.2.0 SOVERSION 1)` for shared-library versioning.

## 4. Finding dependencies

```cmake
find_package(Eigen3 3.4 REQUIRED NO_MODULE)       # provides Eigen3::Eigen
find_package(OpenCV REQUIRED COMPONENTS core imgproc)
find_package(GTest REQUIRED)                       # GTest::gtest, GTest::gtest_main
find_package(Threads REQUIRED)                     # Threads::Threads
target_link_libraries(vision PRIVATE ${OpenCV_LIBS} Threads::Threads)

# fetch a dependency at configure time (pinned!)
include(FetchContent)
FetchContent_Declare(fmt GIT_REPOSITORY https://github.com/fmtlib/fmt.git GIT_TAG 10.2.1)
FetchContent_MakeAvailable(fmt)                    # → fmt::fmt
```

`find_package` searches for `<Pkg>Config.cmake` (provided by modern packages, giving imported targets like `Eigen3::Eigen`) or a `Find<Pkg>.cmake` module. `CMAKE_PREFIX_PATH` adds search locations, and that's how a sourced ROS environment exposes its packages. Package managers: vcpkg and Conan integrate through a toolchain file.

## 5. Multi-directory projects

```text
robot_kit/
├── CMakeLists.txt          # project(), options, add_subdirectory(...)
├── libs/kinematics/CMakeLists.txt
├── libs/drivers/CMakeLists.txt
├── apps/teleop/CMakeLists.txt
└── tests/CMakeLists.txt
```

```cmake
# top-level
option(ROBOT_BUILD_TESTS "Build unit tests" ON)
add_subdirectory(libs/kinematics)
add_subdirectory(apps/teleop)
if(ROBOT_BUILD_TESTS)
  enable_testing()
  add_subdirectory(tests)
endif()
```

Each subdirectory defines its own targets. Targets are global, so `apps/teleop` can link `kinematics` defined elsewhere, but *variables* are scoped per directory (use `PARENT_SCOPE` or cache variables deliberately).

## 6. Build types, options and generator expressions

| `CMAKE_BUILD_TYPE` | Flags (GCC) | Use |
|---|---|---|
| Debug | `-g` | debugging, sanitizers |
| Release | `-O3 -DNDEBUG` | deployment |
| RelWithDebInfo | `-O2 -g -DNDEBUG` | profiling with symbols |
| MinSizeRel | `-Os -DNDEBUG` | embedded |

```cmake
target_compile_options(kinematics PRIVATE
  $<$<CONFIG:Debug>:-fsanitize=address,undefined -fno-omit-frame-pointer>
  $<$<CXX_COMPILER_ID:MSVC>:/W4>)
target_link_options(kinematics PRIVATE $<$<CONFIG:Debug>:-fsanitize=address,undefined>)
```

**Generator expressions** `$<...>` are evaluated at generate time, per configuration, which is needed for multi-config generators (Visual Studio, Ninja Multi-Config). `cmake --preset release` with a `CMakePresets.json` file standardises configure options across a team and CI.

## 7. Testing with CTest

```cmake
add_executable(kinematics_tests tests/test_fk.cpp)
target_link_libraries(kinematics_tests PRIVATE kinematics GTest::gtest_main)
include(GoogleTest)
gtest_discover_tests(kinematics_tests)        # each TEST() becomes a CTest test
```

## 8. Installing and exporting

```cmake
include(GNUInstallDirs)
install(TARGETS kinematics EXPORT robotTargets ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR})
install(DIRECTORY include/ DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
install(EXPORT robotTargets NAMESPACE robot:: DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/robot)
```

That lets other projects `find_package(robot)` and link `robot::kinematics`. ROS 2's `ament_cmake` wraps exactly this (`ament_export_targets`, `ament_package()`).

## 9. Exam-ready answers

> [!EXAM]
> **Target-based CMake.** Modern CMake describes a build as a set of targets (executables, static or shared libraries, interface libraries) with properties such as source files, include directories, compile definitions, options, features and linked dependencies. Properties are attached with `target_*` commands using the scopes PRIVATE (used to build the target only), INTERFACE (required only by consumers) and PUBLIC (both). Linking a target with `target_link_libraries` propagates its interface requirements transitively, so consumers automatically receive the include paths and flags they need. Dependencies are located with `find_package`, which provides imported targets, and the configure step generates native build files for a chosen generator, with builds performed out of source.

## 10. Cheat sheet

| Need | CMake |
|---|---|
| executable / library | `add_executable(a src.cpp)`, `add_library(l STATIC ...)` |
| headers for users | `target_include_directories(l PUBLIC include)` |
| C++ standard | `target_compile_features(l PUBLIC cxx_std_20)` |
| warnings (own code only) | `target_compile_options(l PRIVATE -Wall -Wextra)` |
| dependency | `find_package(X REQUIRED)` + `target_link_libraries(t PRIVATE X::X)` |
| subprojects | `add_subdirectory(dir)` |
| tests | `enable_testing()`, `gtest_discover_tests(t)` |
| configure / build | `cmake -S . -B build -G Ninja`, `cmake --build build` |
| clangd support | `CMAKE_EXPORT_COMPILE_COMMANDS ON` |

> [!INTERVIEW]
> **"What's the difference between PUBLIC and PRIVATE in `target_link_libraries`?"** PRIVATE means the dependency is used only in the target's implementation (.cpp files), so consumers don't get its include paths or link it transitively. PUBLIC means the dependency appears in the target's public headers, so consumers need it too, and CMake propagates its usage requirements. Marking everything PUBLIC leaks dependencies and slows builds. Marking a header-exposed dependency PRIVATE breaks consumers' compiles. INTERFACE is for requirements that only consumers need, typical of header-only libraries.
