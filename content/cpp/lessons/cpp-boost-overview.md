# Boost and the Ecosystem

The C++ standard library is deliberately small, so most real projects depend on a handful of high-quality third-party libraries. **Boost** is the incubator where much of modern C++ was born (smart pointers, `std::function`, `optional`, `variant`, `filesystem`, threads and regex all started there) and it still provides libraries the standard lacks. Around it, a modern ecosystem covers formatting (fmt), logging (spdlog), JSON (nlohmann/json), command-line parsing, testing and package management (vcpkg, Conan). Knowing what exists, and when to prefer the standard library, saves months of reinvention.

## 1. Boost: what's still worth using

| Library | Purpose | Standard equivalent? |
|---|---|---|
| Boost.Asio | asynchronous networking, timers, serial ports (robot drivers!) | `std::net` never landed; Asio is *the* choice |
| Boost.Beast | HTTP and WebSocket on top of Asio | none |
| Boost.Geometry | polygons, R-trees, spatial indexes | none |
| Boost.Graph | graph algorithms (Dijkstra, max-flow, …) | none |
| Boost.Algorithm/String | string utilities (`to_upper`, `split`, `trim`) | partial |
| Boost.Program_options | command-line and config parsing | none |
| Boost.Interprocess | shared memory, IPC containers | none |
| Boost.Container | `flat_map`, `small_vector`, `static_vector` | `std::flat_map` (C++23) |
| Boost.Multiprecision | big integers, high-precision floats | none |
| Boost.Lockfree | lock-free queues | none |
| Boost.Hana / MP11 | metaprogramming | partly (concepts) |

```cpp
#include <boost/algorithm/string.hpp>
#include <iostream>
#include <vector>

int main() {
    std::string line = "  SET speed 1.5  ";
    boost::algorithm::trim(line);
    std::vector<std::string> parts;
    boost::split(parts, line, boost::is_any_of(" "), boost::token_compress_on);
    boost::to_lower(parts[0]);
    std::cout << parts[0] << " " << parts.size() << "\n";      // set 3
}
```

Most of Boost is **header-only**. A few parts need linking (`-lboost_program_options`, `-lboost_filesystem`). With CMake: `find_package(Boost REQUIRED COMPONENTS program_options)` and `target_link_libraries(app PRIVATE Boost::program_options)`.

### Asio in one example: a serial-port/timer style event loop

```cpp
#include <boost/asio.hpp>
#include <chrono>
#include <iostream>

int main() {
    boost::asio::io_context io;
    boost::asio::steady_timer t(io, std::chrono::milliseconds(50));
    int ticks = 0;
    std::function<void(const boost::system::error_code&)> tick = [&](const boost::system::error_code&) {
        if (++ticks < 3) { t.expires_after(std::chrono::milliseconds(50)); t.async_wait(tick); }
    };
    t.async_wait(tick);
    io.run();                                  // runs the event loop until no work remains
    std::cout << "ticks: " << ticks << "\n";   // 3
}
```

Asio's model of asynchronous operations with completion handlers, run by an `io_context`, also powers many robot drivers (`boost::asio::serial_port` for motor controllers and GPS modules).

## 2. Formatting and logging: fmt and spdlog

```cpp
#include <fmt/core.h>
#include <fmt/ranges.h>
fmt::print("pose x={:.2f} y={:+.3f} id={:>4}\n", 1.234, -0.5, 7);
std::string s = fmt::format("{} items: {}", 3, std::vector{1, 2, 3});   // "3 items: [1, 2, 3]"
```

fmt became `std::format` (C++20) and `std::print` (C++23), so prefer the standard versions when available. fmt is still faster, has more features, and works on older compilers.

```cpp
#include <spdlog/spdlog.h>
spdlog::set_level(spdlog::level::debug);
spdlog::info("battery at {}%", 87);
spdlog::warn("obstacle at {:.2f} m", 0.42);
// async, rotating file sinks for long robot runs: spdlog::rotating_logger_mt(...)
```

## 3. JSON: nlohmann/json

```cpp
#include <nlohmann/json.hpp>
using json = nlohmann::json;

struct Waypoint { std::string name; double x, y; };
NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE(Waypoint, name, x, y)       // generates to_json / from_json

json j = json::parse(R"({"mission": "patrol", "waypoints": [{"name": "a", "x": 1, "y": 2}]})");
auto wps = j["waypoints"].get<std::vector<Waypoint>>();
j["waypoints"].push_back(Waypoint{"b", 3.5, -1.0});
std::string out = j.dump(2);                                     // pretty-printed
double x = j.value("speed", 0.5);                                // with a default when the key is missing
```

Alternatives: simdjson (parsing at GB/s), RapidJSON, Boost.JSON, and yaml-cpp for YAML (ROS parameter files).

## 4. Other staples

| Need | Libraries |
|---|---|
| command line | CLI11, cxxopts, Boost.Program_options |
| testing | GoogleTest/gMock, Catch2, doctest |
| benchmarks | Google Benchmark, nanobench |
| linear algebra | Eigen, Blaze, xtensor |
| optimisation, SLAM | Ceres, g2o, GTSAM |
| geometry, point clouds | PCL, Open3D, CGAL |
| serialisation, RPC | Protobuf, FlatBuffers, Cap'n Proto, gRPC |
| networking, messaging | Boost.Asio, ZeroMQ, MQTT (Paho) |
| concurrency | oneTBB, Taskflow, folly |

## 5. Getting dependencies: package managers

| Tool | How |
|---|---|
| system packages (apt) | `apt install libeigen3-dev libopencv-dev libboost-all-dev`: simple, but versions are fixed by the distro |
| **vcpkg** | a `vcpkg.json` manifest plus the CMake toolchain file; builds from source, pins versions with baselines |
| **Conan** | `conanfile.txt`/`.py`, binary caches, profiles for cross-compiling |
| CMake FetchContent | pull a pinned git tag at configure time; good for small header-only libraries |
| ROS (rosdep) | `rosdep install --from-paths src` resolves package.xml dependencies |

> [!KEY]
> **Pin versions** (vcpkg baselines, Conan lockfiles, FetchContent tags) so builds are reproducible. Prefer libraries with CMake config packages (imported targets like `fmt::fmt`), keep third-party code out of your warning flags (`SYSTEM` includes), and review licences: Boost and MIT are permissive, while GPL affects distribution.

## 6. Standard library first?

Before adding a dependency, check C++17/20/23: `std::filesystem`, `std::optional`, `std::variant`, `std::format`/`std::print`, `std::span`, `std::jthread`, `std::expected`, ranges, `std::flat_map`. Each dependency costs build time, upgrade work and supply-chain risk. Add one when it provides substantial, well-maintained capability (Asio, Eigen, spdlog), not for a few utility functions.

## 7. Exam-ready answers

> [!EXAM]
> **The role of Boost.** Boost is a collection of peer-reviewed, portable C++ libraries that serves both as a practical toolkit and as a proving ground for the standard: smart pointers, function wrappers, optional, variant, any, filesystem, regex, thread and chrono were standardised after maturing in Boost. Most Boost libraries are header-only, while some, such as program_options and filesystem, require linking. It remains valuable for capabilities the standard lacks, notably Boost.Asio for asynchronous I/O and networking, Boost.Geometry, Boost.Graph and Boost.Interprocess. Modern projects complement it with focused libraries such as fmt, spdlog and nlohmann/json, managed with package managers like vcpkg or Conan and integrated through CMake imported targets.

## 8. Cheat sheet

| Need | Library | CMake target |
|---|---|---|
| async I/O, serial, timers | Boost.Asio | `Boost::headers` (+ Threads) |
| formatting | fmt / `std::format` | `fmt::fmt` |
| logging | spdlog | `spdlog::spdlog` |
| JSON | nlohmann/json | `nlohmann_json::nlohmann_json` |
| string utilities | Boost.Algorithm | `Boost::headers` |
| CLI parsing | CLI11 | `CLI11::CLI11` |
| packages | vcpkg / Conan / FetchContent | toolchain or imported targets |

> [!INTERVIEW]
> **"Would you add Boost to a new embedded robot project?"** Selectively. Use Boost.Asio for serial and network drivers, or Boost.Geometry if needed, because these are header-only and excellent. Avoid pulling in the whole distribution, prefer standard C++20/23 facilities where they exist, and check binary size, compile time, exception and RTTI requirements (some embedded targets disable them), licences and cross-compilation support. Pin versions through a package manager.
