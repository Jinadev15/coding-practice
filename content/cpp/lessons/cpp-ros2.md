# ROS 2 with rclcpp

**rclcpp** is ROS 2's C++ client library, the choice for performance-critical and real-time robot code: drivers, controllers (ros2_control), perception pipelines, and Nav2 and MoveIt themselves. The concepts match the Python lesson (nodes, topics, services, parameters, executors, QoS, tf2). This lesson focuses on what's specific to C++: shared-pointer-based APIs, callback signatures, composition (multiple nodes in one process with zero-copy intra-process communication), the executor and callback-group model for concurrency, lifecycle nodes, and real-time considerations. The code targets ROS 2 Lyrical, installed on this machine, and the judge compiles real rclcpp code.

## 1. A minimal node

```cpp
#include <chrono>
#include <rclcpp/rclcpp.hpp>
#include <std_msgs/msg/string.hpp>
using namespace std::chrono_literals;

class Talker : public rclcpp::Node {
public:
    Talker() : Node("talker") {
        pub_ = create_publisher<std_msgs::msg::String>("chatter", 10);
        timer_ = create_wall_timer(100ms, [this] {
            std_msgs::msg::String msg;
            msg.data = "hello " + std::to_string(count_++);
            pub_->publish(msg);
        });
    }
private:
    rclcpp::Publisher<std_msgs::msg::String>::SharedPtr pub_;
    rclcpp::TimerBase::SharedPtr timer_;     // keep handles alive as members, or callbacks stop
    size_t count_ = 0;
};

int main(int argc, char** argv) {
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<Talker>());
    rclcpp::shutdown();
}
```

> [!KEY]
> rclcpp hands out `SharedPtr` handles for publishers, subscriptions, timers, clients and services. **Store them as members**: if a handle goes out of scope (for example a subscription created in the constructor but not saved), it's destroyed and its callback silently never fires. This is the most common rclcpp beginner bug.

## 2. Subscriptions and callback signatures

```cpp
#include <sensor_msgs/msg/laser_scan.hpp>
#include <geometry_msgs/msg/twist.hpp>

class Follower : public rclcpp::Node {
public:
    Follower() : Node("follower") {
        scan_sub_ = create_subscription<sensor_msgs::msg::LaserScan>(
            "scan", rclcpp::SensorDataQoS(),                                    // best effort, depth 5
            [this](sensor_msgs::msg::LaserScan::ConstSharedPtr scan) { on_scan(*scan); });
        cmd_pub_ = create_publisher<geometry_msgs::msg::Twist>("cmd_vel", 10);
    }
private:
    void on_scan(const sensor_msgs::msg::LaserScan& scan) {
        float nearest = std::numeric_limits<float>::infinity();
        for (float r : scan.ranges)
            if (std::isfinite(r) && r >= scan.range_min && r <= scan.range_max) nearest = std::min(nearest, r);
        geometry_msgs::msg::Twist cmd;
        cmd.linear.x = nearest > 0.5f ? 0.3 : 0.0;
        cmd_pub_->publish(cmd);
    }
    rclcpp::Subscription<sensor_msgs::msg::LaserScan>::SharedPtr scan_sub_;
    rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr cmd_pub_;
};
```

Supported callback parameter forms include `const Msg&`, `Msg::ConstSharedPtr`, `Msg::UniquePtr` (take ownership, which enables zero-copy) and versions with `const rclcpp::MessageInfo&`.

## 3. Parameters, services and clients

```cpp
#include <std_srvs/srv/set_bool.hpp>

class ModeNode : public rclcpp::Node {
public:
    ModeNode() : Node("mode_node") {
        max_speed_ = declare_parameter("max_speed", 0.5);
        param_cb_ = add_on_set_parameters_callback([this](const std::vector<rclcpp::Parameter>& ps) {
            rcl_interfaces::msg::SetParametersResult res;
            res.successful = true;
            for (const auto& p : ps)
                if (p.get_name() == "max_speed") {
                    if (p.as_double() < 0) { res.successful = false; res.reason = "negative"; }
                    else max_speed_ = p.as_double();
                }
            return res;
        });
        srv_ = create_service<std_srvs::srv::SetBool>("set_enabled",
            [this](const std_srvs::srv::SetBool::Request::SharedPtr req,
                   std_srvs::srv::SetBool::Response::SharedPtr res) {
                enabled_ = req->data;
                res->success = true;
                res->message = enabled_ ? "enabled" : "disabled";
            });
    }
private:
    double max_speed_;
    bool enabled_ = true;
    OnSetParametersCallbackHandle::SharedPtr param_cb_;
    rclcpp::Service<std_srvs::srv::SetBool>::SharedPtr srv_;
};

// client: auto cli = node->create_client<std_srvs::srv::SetBool>("set_enabled");
// auto req = std::make_shared<std_srvs::srv::SetBool::Request>(); req->data = true;
// auto fut = cli->async_send_request(req);                      // never block inside a callback
// rclcpp::spin_until_future_complete(node, fut);               // from main(), or use a callback form
```

## 4. Executors, callback groups and threading

| Executor | Behaviour |
|---|---|
| `SingleThreadedExecutor` | one thread runs all callbacks sequentially (no data races between callbacks) |
| `MultiThreadedExecutor` | a thread pool, with concurrency controlled by **callback groups** |
| `EventsExecutor` | event-queue based, lower overhead |

```cpp
auto group = create_callback_group(rclcpp::CallbackGroupType::MutuallyExclusive);
rclcpp::SubscriptionOptions opts;
opts.callback_group = group;
// callbacks in a MutuallyExclusive group never run concurrently with each other;
// a Reentrant group lets the same callback run in parallel (you then need your own locking)
rclcpp::executors::MultiThreadedExecutor exec;
exec.add_node(node);
exec.spin();
```

> [!WARNING]
> With a `MultiThreadedExecutor`, callbacks in *different* groups can run at the same time and access shared member data: protect it with a mutex or atomics. The classic deadlock also exists in C++: waiting on a service future inside a callback while the executor thread that would process the response is the one you're blocking.

## 5. Composition and intra-process communication

Nodes compiled as **components** (`rclcpp_components`) can be loaded into one process. With `use_intra_process_comms(true)`, publishing a `std::unique_ptr<Msg>` hands the pointer to subscribers in the same process **without copying or serialising**, which is essential for images and point clouds.

```cpp
auto opts = rclcpp::NodeOptions().use_intra_process_comms(true);
auto msg = std::make_unique<sensor_msgs::msg::PointCloud2>();
// fill msg ...
pub->publish(std::move(msg));            // zero-copy to intra-process subscribers that take UniquePtr
```

## 6. Lifecycle nodes

`rclcpp_lifecycle::LifecycleNode` adds a managed state machine (unconfigured → inactive → active → finalized) with `on_configure`, `on_activate`, `on_deactivate` and `on_cleanup` callbacks. A supervisor can bring up drivers in a deterministic order and recover them without restarting the process. Nav2 is built entirely from lifecycle nodes.

## 7. Real-time considerations

For control loops at 1 kHz:
- Pre-allocate all memory: no `new`, no growing `std::vector` or `std::string` in the loop. Use PMR or arenas (C++ Advanced module).
- Avoid locks shared with non-real-time threads. Use lock-free single-producer single-consumer buffers (`realtime_tools::RealtimeBuffer`).
- Use a dedicated thread with a real-time scheduling policy (`SCHED_FIFO`), `mlockall` to prevent page faults, and CPU isolation.
- Keep DDS traffic and logging off the real-time path (logging allocates).
- **ros2_control** structures hardware interfaces and controllers so that `update()` runs in a real-time loop.

## 8. Building: ament_cmake

```cmake
cmake_minimum_required(VERSION 3.16)
project(my_robot)
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
add_executable(follower src/follower.cpp)
target_link_libraries(follower rclcpp::rclcpp ${sensor_msgs_TARGETS} ${geometry_msgs_TARGETS})
install(TARGETS follower DESTINATION lib/${PROJECT_NAME})
ament_package()
```

Then `colcon build --packages-select my_robot`, `source install/setup.bash` and `ros2 run my_robot follower`.

## 9. Exam-ready answers

> [!EXAM]
> **Executors and callback groups in rclcpp.** In rclcpp, the work of a node (subscription, timer, service and client callbacks) is dispatched by an executor. A single-threaded executor runs all callbacks sequentially in one thread, while a multi-threaded executor uses a thread pool. Callback groups control concurrency within a multi-threaded executor: callbacks in the same mutually exclusive group never run concurrently, whereas a reentrant group allows parallel execution, including of the same callback. Shared state accessed from callbacks in different groups must be synchronised, and blocking inside a callback (for instance waiting synchronously for a service response that the same executor must process) can deadlock. Multiple nodes can be composed into one process and exchange messages through intra-process communication without serialisation, by publishing unique pointers.

## 10. Cheat sheet

| Need | rclcpp |
|---|---|
| node | `class N : public rclcpp::Node { N() : Node("n") {...} };` |
| publisher | `create_publisher<Msg>("topic", 10)` (store the SharedPtr!) |
| subscription | `create_subscription<Msg>("t", qos, [this](Msg::ConstSharedPtr m){...})` |
| timer | `create_wall_timer(100ms, cb)` |
| parameter | `declare_parameter("p", default)`; `add_on_set_parameters_callback` |
| service | `create_service<Srv>("s", [](Req::SharedPtr, Res::SharedPtr){...})` |
| sensor QoS | `rclcpp::SensorDataQoS()` |
| spin | `rclcpp::spin(node)` / an executor with `spin_some` |
| zero-copy | `use_intra_process_comms(true)` + publish `unique_ptr` |
| build | `ament_cmake`, `colcon build` |

> [!INTERVIEW]
> **"Your rclcpp subscription callback never fires, although `ros2 topic echo` shows data."** In C++, first check that the `Subscription::SharedPtr` returned by `create_subscription` is stored in a member (a temporary is destroyed at the end of the constructor). Then check QoS compatibility (`SensorDataQoS` versus reliable), the topic name and namespace, that the node is actually added to a spinning executor, and that no other callback is blocking a single-threaded executor.
