---
id: cpp-rclcpp-safety-node
title: An rclcpp Velocity Safety Filter Node
difficulty: Hard
order: 1
tags: ROS 2, rclcpp, publishers, subscriptions, QoS, parameters, services, executors
libs: rclcpp
time_limit: 15
---
## Statement
Write a real **ROS 2 C++ node** with rclcpp. The judge compiles it against ROS 2 Lyrical and runs it in an executor beside a probe node.

`class SafetyFilter : public rclcpp::Node`, default-constructible:
- **Node name** `safety_filter`. **Parameters**: `stop_distance = 0.4`, `slow_distance = 1.0`, `max_speed = 0.8` (doubles). Reject any update that would make `stop_distance` negative, or not less than `slow_distance` (the set fails, and the old value stays).
- **Subscribes** to `scan` (`sensor_msgs::msg::LaserScan`, `rclcpp::SensorDataQoS()`). It keeps the nearest valid range (finite, within `[range_min, range_max]`), or +∞ if none.
- **Subscribes** to `cmd_vel_raw` (`geometry_msgs::msg::Twist`, depth 10). For each command, it publishes on `cmd_vel` (depth 10):
  - While **disabled**: an all-zero Twist.
  - Otherwise `angular.z` passes through, and `linear.x` is clamped to ±`max_speed`. If `nearest <= stop_distance`, `linear.x = min(linear.x, 0)`. Else, if `nearest < slow_distance` and `linear.x > 0`, it's scaled by `(nearest - stop)/(slow - stop)`.
- **Service** `set_enabled` (`std_srvs::srv::SetBool`): sets the flag (initially enabled) and responds with `success = true` and `message` either `"enabled"` or `"disabled"`.

Keep every publisher, subscription, service and parameter-callback handle as a **member**, or the callbacks never fire. Don't call `rclcpp::init`/`spin`: the judge's `main` does.

## Starter
```cpp
#include <rclcpp/rclcpp.hpp>
#include <geometry_msgs/msg/twist.hpp>
#include <sensor_msgs/msg/laser_scan.hpp>
#include <std_srvs/srv/set_bool.hpp>

class SafetyFilter : public rclcpp::Node {
public:
    SafetyFilter() : Node("safety_filter") {
        pub_ = create_publisher<geometry_msgs::msg::Twist>("cmd_vel", 10);
        create_subscription<geometry_msgs::msg::Twist>("cmd_vel_raw", 10,
            [this](geometry_msgs::msg::Twist::ConstSharedPtr m) { pub_->publish(*m); });   // handle not stored!
    }
private:
    rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr pub_;
};
```

## Driver
```cpp
#include <chrono>
#include <cmath>
#include <cstdio>
#include <iostream>
#include <limits>
#include <string>
#include <vector>
using namespace std::chrono_literals;

int main(int argc, char** argv) {
    rclcpp::init(argc, argv);
    auto node = std::make_shared<SafetyFilter>();
    auto probe = std::make_shared<rclcpp::Node>("probe");
    std::vector<std::pair<double, double>> outputs;
    auto out_sub = probe->create_subscription<geometry_msgs::msg::Twist>("cmd_vel", 10,
        [&](geometry_msgs::msg::Twist::ConstSharedPtr m) { outputs.push_back({m->linear.x, m->angular.z}); });
    auto scan_pub = probe->create_publisher<sensor_msgs::msg::LaserScan>("scan", rclcpp::SensorDataQoS());
    auto cmd_pub = probe->create_publisher<geometry_msgs::msg::Twist>("cmd_vel_raw", 10);
    auto client = probe->create_client<std_srvs::srv::SetBool>("set_enabled");
    rclcpp::executors::SingleThreadedExecutor ex;
    ex.add_node(node); ex.add_node(probe);
    auto spin = [&](int n) { for (int i = 0; i < n; ++i) ex.spin_some(5ms); };
    for (int i = 0; i < 400 && (scan_pub->get_subscription_count() == 0 || cmd_pub->get_subscription_count() == 0
                                || out_sub->get_publisher_count() == 0); ++i) spin(1);
    auto r3 = [](double v) { double x = std::round(v * 1000) / 1000; return x == 0 ? 0.0 : x; };
    auto send_scan = [&](std::vector<float> ranges) {
        sensor_msgs::msg::LaserScan s; s.range_min = 0.1f; s.range_max = 10.0f; s.ranges = ranges;
        scan_pub->publish(s); spin(20);
    };
    auto send_cmd = [&](double vx, double wz) -> std::string {
        size_t before = outputs.size();
        geometry_msgs::msg::Twist t; t.linear.x = vx; t.angular.z = wz;
        cmd_pub->publish(t);
        for (int i = 0; i < 400 && outputs.size() == before; ++i) spin(1);
        if (outputs.size() == before) return "(none)";
        char buf[64]; std::snprintf(buf, sizeof buf, "(%.3f, %.3f)", r3(outputs.back().first), r3(outputs.back().second));
        return buf;
    };
    auto call = [&](bool en) -> std::string {
        if (!client->wait_for_service(2s)) return "no service";
        auto req = std::make_shared<std_srvs::srv::SetBool::Request>(); req->data = en;
        auto fut = client->async_send_request(req);
        for (int i = 0; i < 400; ++i) {
            spin(1);
            if (fut.wait_for(0s) == std::future_status::ready) {
                auto r = fut.get();
                return std::string(r->success ? "true " : "false ") + r->message;
            }
        }
        return "timeout";
    };
    const float inf = std::numeric_limits<float>::infinity(), nan = std::numeric_limits<float>::quiet_NaN();
    std::printf("node: %s\n", node->get_name());
    std::string cmd;
    while (std::cin >> cmd) {
        if (cmd == "params") {
            std::printf("params: %.2f %.2f %.2f\n", node->get_parameter("stop_distance").as_double(),
                        node->get_parameter("slow_distance").as_double(), node->get_parameter("max_speed").as_double());
        } else if (cmd == "free") {
            send_scan({5.0f, 3.0f, inf});
            std::printf("free: %s %s %s\n", send_cmd(0.5, 0.2).c_str(), send_cmd(2.0, -0.1).c_str(), send_cmd(-1.5, 0).c_str());
        } else if (cmd == "slow") {
            send_scan({0.7f, 0.05f, nan, 12.0f});
            std::printf("slow: %s %s\n", send_cmd(0.6, 0.3).c_str(), send_cmd(-0.4, 0).c_str());
        } else if (cmd == "stop") {
            send_scan({0.3f, 2.0f});
            std::printf("stop: %s %s\n", send_cmd(0.5, 1.0).c_str(), send_cmd(-0.2, 0).c_str());
        } else if (cmd == "service") {
            std::printf("disable: %s -> %s\n", call(false).c_str(), send_cmd(0.5, 0.5).c_str());
            std::printf("enable: %s -> %s\n", call(true).c_str(), send_cmd(0.5, 0.5).c_str());
        } else if (cmd == "setparams") {
            auto ok = node->set_parameters({rclcpp::Parameter("max_speed", 0.3), rclcpp::Parameter("slow_distance", 2.0)});
            auto bad1 = node->set_parameters({rclcpp::Parameter("stop_distance", -1.0)});
            auto bad2 = node->set_parameters({rclcpp::Parameter("stop_distance", 2.5)});
            std::printf("valid set: %d %d, negative rejected: %d, >= slow rejected: %d, stop still %.2f\n",
                        (int)ok[0].successful, (int)ok[1].successful, (int)!bad1[0].successful, (int)!bad2[0].successful,
                        node->get_parameter("stop_distance").as_double());
            send_scan({1.2f});
            std::printf("after params: %s\n", send_cmd(0.5, 0).c_str());
        }
    }
    rclcpp::shutdown();
}
```

## Tests
=== sample
params
free
stop
---
node: safety_filter
params: 0.40 1.00 0.80
free: (0.500, 0.200) (0.800, -0.100) (-0.800, 0.000)
stop: (0.000, 1.000) (-0.200, 0.000)
=== hidden
slow
service
setparams
free
---
node: safety_filter
slow: (0.300, 0.300) (-0.400, 0.000)
disable: true disabled -> (0.250, 0.500)
enable: true enabled -> (0.000, 0.000)
valid set: 1 1, negative rejected: 1, >= slow rejected: 1, stop still 0.40
after params: (0.150, 0.000)
free: (0.300, 0.200) (0.300, -0.100) (-0.300, 0.000)

## Hints
- Members: `rclcpp::Subscription<sensor_msgs::msg::LaserScan>::SharedPtr scan_sub_;`, `rclcpp::Subscription<geometry_msgs::msg::Twist>::SharedPtr cmd_sub_;`, `rclcpp::Service<std_srvs::srv::SetBool>::SharedPtr srv_;`, `OnSetParametersCallbackHandle::SharedPtr param_cb_;`.
- `declare_parameter("stop_distance", 0.4)` and so on. The set-parameters callback receives the *proposed* values: validate the combination using the proposed value where one is given, and the current value otherwise.
- Read the parameters with `get_parameter("max_speed").as_double()` inside the command callback.
- Valid range: `std::isfinite(r) && r >= scan.range_min && r <= scan.range_max`.

## Solution
```cpp
#include <rclcpp/rclcpp.hpp>
#include <geometry_msgs/msg/twist.hpp>
#include <sensor_msgs/msg/laser_scan.hpp>
#include <std_srvs/srv/set_bool.hpp>
#include <algorithm>
#include <cmath>
#include <limits>

class SafetyFilter : public rclcpp::Node {
public:
    SafetyFilter() : Node("safety_filter") {
        declare_parameter("stop_distance", 0.4);
        declare_parameter("slow_distance", 1.0);
        declare_parameter("max_speed", 0.8);
        param_cb_ = add_on_set_parameters_callback([this](const std::vector<rclcpp::Parameter>& ps) {
            double stop = get_parameter("stop_distance").as_double();
            double slow = get_parameter("slow_distance").as_double();
            for (const auto& p : ps) {
                if (p.get_name() == "stop_distance") stop = p.as_double();
                if (p.get_name() == "slow_distance") slow = p.as_double();
            }
            rcl_interfaces::msg::SetParametersResult res;
            res.successful = stop >= 0.0 && stop < slow;
            if (!res.successful) res.reason = "need 0 <= stop_distance < slow_distance";
            return res;
        });
        pub_ = create_publisher<geometry_msgs::msg::Twist>("cmd_vel", 10);
        scan_sub_ = create_subscription<sensor_msgs::msg::LaserScan>("scan", rclcpp::SensorDataQoS(),
            [this](sensor_msgs::msg::LaserScan::ConstSharedPtr s) { on_scan(*s); });
        cmd_sub_ = create_subscription<geometry_msgs::msg::Twist>("cmd_vel_raw", 10,
            [this](geometry_msgs::msg::Twist::ConstSharedPtr c) { on_cmd(*c); });
        srv_ = create_service<std_srvs::srv::SetBool>("set_enabled",
            [this](const std_srvs::srv::SetBool::Request::SharedPtr req, std_srvs::srv::SetBool::Response::SharedPtr res) {
                enabled_ = req->data;
                res->success = true;
                res->message = enabled_ ? "enabled" : "disabled";
            });
    }

private:
    void on_scan(const sensor_msgs::msg::LaserScan& scan) {
        float best = std::numeric_limits<float>::infinity();
        for (float r : scan.ranges)
            if (std::isfinite(r) && r >= scan.range_min && r <= scan.range_max) best = std::min(best, r);
        nearest_ = best;
    }

    void on_cmd(const geometry_msgs::msg::Twist& in) {
        geometry_msgs::msg::Twist out;
        if (enabled_) {
            const double stop = get_parameter("stop_distance").as_double();
            const double slow = get_parameter("slow_distance").as_double();
            const double vmax = get_parameter("max_speed").as_double();
            double vx = std::clamp(in.linear.x, -vmax, vmax);
            if (nearest_ <= stop) vx = std::min(vx, 0.0);
            else if (nearest_ < slow && vx > 0) vx *= (nearest_ - stop) / (slow - stop);
            out.linear.x = vx;
            out.angular.z = in.angular.z;
        }
        pub_->publish(out);
    }

    rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr pub_;
    rclcpp::Subscription<sensor_msgs::msg::LaserScan>::SharedPtr scan_sub_;
    rclcpp::Subscription<geometry_msgs::msg::Twist>::SharedPtr cmd_sub_;
    rclcpp::Service<std_srvs::srv::SetBool>::SharedPtr srv_;
    OnSetParametersCallbackHandle::SharedPtr param_cb_;
    double nearest_ = std::numeric_limits<double>::infinity();
    bool enabled_ = true;
};
```

- **Stored handles** keep the subscriptions, service and parameter callback alive. The starter's subscription handle is a temporary, destroyed at the end of the constructor, so its callback never runs: the classic rclcpp mistake.
- **QoS matching**: lidar topics are best-effort, and `SensorDataQoS()` subscribes compatibly.
- **Parameter validation** checks the *combination* of proposed and current values atomically, so `stop_distance = 2.5` is refused because it isn't below `slow_distance`.
- **One executor thread** runs all callbacks, so `nearest_` and `enabled_` need no locking here. With a `MultiThreadedExecutor` and separate callback groups, they would need atomics or a mutex.
