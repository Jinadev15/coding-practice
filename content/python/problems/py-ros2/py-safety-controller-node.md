---
id: py-safety-controller-node
title: A ROS 2 Safety Controller Node (rclpy)
difficulty: Hard
order: 1
tags: ROS 2, rclpy, publisher, subscription, QoS, parameters, services, executors
time_limit: 20
---
## Statement
Write a real **ROS 2 node** with rclpy. The judge runs it in an executor next to a probe node that publishes lidar scans and teleop commands, calls your service, and changes your parameters. The node is a velocity safety filter between teleop and the motor driver.

`class SafetyController(rclpy.node.Node)`, constructed with no arguments:
- **Node name**: `safety_controller`.
- **Parameters** (declared with defaults): `stop_distance = 0.4`, `slow_distance = 1.0`, `max_speed = 0.8`. Changes at runtime take effect for the next command. Reject a negative `stop_distance` (the set must fail: return `SetParametersResult(successful=False)`).
- **Subscribes** to `scan` (`sensor_msgs/msg/LaserScan`, QoS `qos_profile_sensor_data`). It keeps the nearest **valid** range: finite and within `[range_min, range_max]`. If there are no valid ranges, the nearest is infinity.
- **Subscribes** to `cmd_vel_raw` (`geometry_msgs/msg/Twist`, depth 10). For each command, it publishes on `cmd_vel` (`Twist`, depth 10):
  1. If the node is **disabled**, an all-zero Twist.
  2. Otherwise `angular.z` passes through, and `linear.x` is first clamped to `[-max_speed, max_speed]`. Then, if `nearest <= stop_distance`, forward motion is blocked (`linear.x = min(linear.x, 0.0)`). Else, if `nearest < slow_distance` and `linear.x > 0`, it's scaled by `(nearest - stop) / (slow - stop)`.
- **Service** `set_enabled` (`std_srvs/srv/SetBool`): it sets the enabled flag (initially enabled) and responds with `success=True` and `message` either `"enabled"` or `"disabled"`.

Don't call `rclpy.init`/`spin` yourself: the judge owns the executor. Avoid naming a method `handle`, because it shadows `Node.handle`.

## Starter
```python
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class SafetyController(Node):
    def __init__(self):
        super().__init__("safety_controller")
        self.pub = self.create_publisher(Twist, "cmd_vel", 10)
        self.create_subscription(Twist, "cmd_vel_raw", self.on_cmd, 10)

    def on_cmd(self, msg):
        self.pub.publish(msg)
```

## Driver
```python
import math
import sys
import rclpy
from rclpy.executors import SingleThreadedExecutor
from rclpy.parameter import Parameter
from rclpy.qos import qos_profile_sensor_data
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from std_srvs.srv import SetBool

rclpy.init()
node = SafetyController()
probe = rclpy.create_node("probe")
outputs = []
probe.create_subscription(Twist, "cmd_vel", lambda m: outputs.append((round(m.linear.x, 3) + 0.0, round(m.angular.z, 3) + 0.0)), 10)
scan_pub = probe.create_publisher(LaserScan, "scan", qos_profile_sensor_data)
cmd_pub = probe.create_publisher(Twist, "cmd_vel_raw", 10)
client = probe.create_client(SetBool, "set_enabled")
ex = SingleThreadedExecutor()
ex.add_node(node); ex.add_node(probe)

def spin(n=30):
    for _ in range(n):
        ex.spin_once(timeout_sec=0.01)

def wait_connected():
    for _ in range(300):
        if scan_pub.get_subscription_count() and cmd_pub.get_subscription_count() and outputs_sub_ready():
            return True
        spin(1)
    return False

def outputs_sub_ready():
    return node.count_subscribers("cmd_vel") > 0

def send_scan(ranges, rmin=0.1, rmax=10.0):
    s = LaserScan(); s.range_min = rmin; s.range_max = rmax; s.ranges = [float(r) for r in ranges]
    scan_pub.publish(s); spin()

def send_cmd(vx, wz):
    before = len(outputs)
    t = Twist(); t.linear.x = float(vx); t.angular.z = float(wz)
    cmd_pub.publish(t)
    for _ in range(200):
        spin(1)
        if len(outputs) > before:
            break
    return outputs[-1] if len(outputs) > before else None

def call(enabled):
    client.wait_for_service(timeout_sec=2.0)
    fut = client.call_async(SetBool.Request(data=enabled))
    for _ in range(300):
        spin(1)
        if fut.done():
            r = fut.result()
            return (r.success, r.message)
    return None

print("node name:", node.get_name(), "| connected:", wait_connected())
for cmd in sys.stdin.read().split():
    if cmd == "params":
        print("params:", [node.get_parameter(p).value for p in ("stop_distance", "slow_distance", "max_speed")])
    elif cmd == "free":
        send_scan([5.0, 3.0, float("inf")])
        print("free:", send_cmd(0.5, 0.2), send_cmd(2.0, -0.1), send_cmd(-1.5, 0.0))
    elif cmd == "slow":
        send_scan([0.7, 0.05, float("nan"), 12.0])          # 0.05 < range_min, nan and 12 invalid: nearest 0.7
        print("slow:", send_cmd(0.6, 0.3), send_cmd(-0.4, 0.0))
    elif cmd == "stop":
        send_scan([0.3, 2.0])
        print("stop:", send_cmd(0.5, 1.0), send_cmd(-0.2, 0.0))
    elif cmd == "noscan":
        send_scan([float("nan"), 0.01])
        print("no valid ranges:", send_cmd(0.5, 0.0))
    elif cmd == "service":
        print("disable:", call(False), "->", send_cmd(0.5, 0.5))
        print("enable:", call(True), "->", send_cmd(0.5, 0.5))
    elif cmd == "setparams":
        res = node.set_parameters([Parameter("max_speed", value=0.3), Parameter("slow_distance", value=2.0)])
        bad = node.set_parameters([Parameter("stop_distance", value=-1.0)])
        print("set ok:", [r.successful for r in res], "negative rejected:", not bad[0].successful,
              "stop still:", node.get_parameter("stop_distance").value)
        send_scan([1.2])
        print("after params:", send_cmd(0.5, 0.0))
ex.shutdown()
node.destroy_node(); probe.destroy_node()
rclpy.shutdown()
```

## Tests
=== sample
params
free
stop
---
node name: safety_controller | connected: True
params: [0.4, 1.0, 0.8]
free: (0.5, 0.2) (0.8, -0.1) (-0.8, 0.0)
stop: (0.0, 1.0) (-0.2, 0.0)
=== hidden
slow
noscan
service
setparams
free
---
node name: safety_controller | connected: True
slow: (0.3, 0.3) (-0.4, 0.0)
no valid ranges: (0.5, 0.0)
disable: (True, 'disabled') -> (0.0, 0.0)
enable: (True, 'enabled') -> (0.5, 0.5)
set ok: [True, True] negative rejected: True stop still: 0.4
after params: (0.15, 0.0)
free: (0.3, 0.2) (0.3, -0.1) (-0.3, 0.0)

## Hints
- `from rclpy.qos import qos_profile_sensor_data`; `from std_srvs.srv import SetBool`; `from rcl_interfaces.msg import SetParametersResult`.
- In `__init__`: `self.declare_parameter("stop_distance", 0.4)` and so on; `self.add_on_set_parameters_callback(self.on_params)`. The callback receives the list of new `Parameter`s and returns `SetParametersResult(successful=...)`.
- Read the current values with `self.get_parameter("stop_distance").value` inside `on_cmd`, so updates apply immediately.
- Valid ranges: `[r for r in scan.ranges if math.isfinite(r) and scan.range_min <= r <= scan.range_max]`.
- Service handler signature: `def on_set_enabled(self, request, response): ...; return response`.

## Solution
```python
import math
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from rcl_interfaces.msg import SetParametersResult
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from std_srvs.srv import SetBool

class SafetyController(Node):
    def __init__(self):
        super().__init__("safety_controller")
        self.declare_parameter("stop_distance", 0.4)
        self.declare_parameter("slow_distance", 1.0)
        self.declare_parameter("max_speed", 0.8)
        self.add_on_set_parameters_callback(self.on_params)
        self.nearest = math.inf
        self.enabled = True
        self.pub = self.create_publisher(Twist, "cmd_vel", 10)
        self.create_subscription(LaserScan, "scan", self.on_scan, qos_profile_sensor_data)
        self.create_subscription(Twist, "cmd_vel_raw", self.on_cmd, 10)
        self.create_service(SetBool, "set_enabled", self.on_set_enabled)

    def on_params(self, params):
        for p in params:
            if p.name == "stop_distance" and p.value < 0:
                return SetParametersResult(successful=False, reason="stop_distance must be >= 0")
        return SetParametersResult(successful=True)

    def on_scan(self, scan):
        valid = [r for r in scan.ranges if math.isfinite(r) and scan.range_min <= r <= scan.range_max]
        self.nearest = min(valid, default=math.inf)

    def on_set_enabled(self, request, response):
        self.enabled = bool(request.data)
        response.success = True
        response.message = "enabled" if self.enabled else "disabled"
        return response

    def on_cmd(self, cmd):
        out = Twist()
        if self.enabled:
            stop = self.get_parameter("stop_distance").value
            slow = self.get_parameter("slow_distance").value
            vmax = self.get_parameter("max_speed").value
            vx = max(-vmax, min(vmax, cmd.linear.x))
            if self.nearest <= stop:
                vx = min(vx, 0.0)                              # may still back away
            elif self.nearest < slow and vx > 0:
                vx *= (self.nearest - stop) / (slow - stop)
            out.linear.x = vx
            out.angular.z = cmd.angular.z
        self.pub.publish(out)
```

The node uses the essential rclpy building blocks:
- **Event-driven callbacks**: scans update state, and commands trigger filtered outputs. Nothing blocks, so a single-threaded executor serves every subscription and the service promptly.
- **QoS matching**: lidar drivers publish best-effort (`qos_profile_sensor_data`). A default (reliable) subscription wouldn't receive anything from them.
- **Live parameters**: values are read on every command, and the set-parameters callback validates updates atomically, so an invalid `stop_distance` is refused and the old value stays.
- **The service** toggles the filter. Its handler fills and returns the response object.
- **Safety logic**: clamping happens before the obstacle rules, braking applies only to forward motion (reversing away is allowed), and invalid lidar returns (NaN, below `range_min`) are ignored instead of being treated as zero-distance obstacles.
