# Unit Testing with GoogleTest

**GoogleTest** (gtest) is the most widely used C++ test framework. ROS 2, Chromium, LLVM and countless robotics codebases use it, and **gMock**, its mocking library, lets you test code against fake hardware drivers and services. This lesson covers test cases and assertions, fixtures, parameterised tests, death tests, mocking with gMock, and the design practices (dependency injection through interfaces) that make C++ code testable.

## 1. A first test

```cpp
#include <gtest/gtest.h>

int clamp_speed(int v, int max) { return v > max ? max : (v < -max ? -max : v); }

TEST(ClampSpeed, PassesThroughInRange) {            // TEST(SuiteName, TestName)
    EXPECT_EQ(clamp_speed(5, 10), 5);
}

TEST(ClampSpeed, ClampsBothDirections) {
    EXPECT_EQ(clamp_speed(15, 10), 10);
    EXPECT_EQ(clamp_speed(-15, 10), -10);
}
// link with GTest::gtest_main (provides main), or write main: ::testing::InitGoogleTest(&argc, argv); return RUN_ALL_TESTS();
```

Run it with filters: `./tests --gtest_filter='ClampSpeed.*' --gtest_repeat=100 --gtest_shuffle` (shuffling exposes order dependencies between tests).

## 2. Assertions

| Family | Non-fatal (continues) | Fatal (returns from the test) |
|---|---|---|
| boolean | `EXPECT_TRUE(c)` | `ASSERT_TRUE(c)` |
| equality | `EXPECT_EQ(a, b)`, `EXPECT_NE` | `ASSERT_EQ` … |
| ordering | `EXPECT_LT/LE/GT/GE` | `ASSERT_...` |
| C strings | `EXPECT_STREQ` | |
| floating point | `EXPECT_DOUBLE_EQ(a, b)` (within 4 ULPs), `EXPECT_NEAR(a, b, tol)` | |
| exceptions | `EXPECT_THROW(stmt, Type)`, `EXPECT_NO_THROW` | |
| death | `EXPECT_DEATH(stmt, "regex")` | |

```cpp
TEST(Kinematics, ReachMatches) {
    std::vector<double> q = solve_ik(1.2, 0.6);
    ASSERT_EQ(q.size(), 2u) << "IK must return two joints";   // fatal: no point continuing
    EXPECT_NEAR(fk_x(q), 1.2, 1e-9);                             // custom message via <<
}
```

> [!KEY]
> Use **ASSERT** when continuing would crash or be meaningless (a null pointer, a wrong vector size). Use **EXPECT** otherwise, so one run reports *all* failures. Never compare floating-point results with `EXPECT_EQ`: use `EXPECT_NEAR` with a tolerance that reflects the computation.

## 3. Fixtures: shared setup

```cpp
class OdometryTest : public ::testing::Test {
protected:
    void SetUp() override { odom.reset(0.0, 0.0, 0.0); }    // runs before EACH test
    void TearDown() override {}                              // after each test
    Odometry odom{0.5 /* wheel base */};
};

TEST_F(OdometryTest, StraightLine) {                           // TEST_F uses the fixture
    odom.update(1.0, 1.0, 1.0);                                // left, right wheel distances, dt
    EXPECT_NEAR(odom.x(), 1.0, 1e-12);
    EXPECT_NEAR(odom.theta(), 0.0, 1e-12);
}
```

Each test gets a **fresh** fixture object, so tests stay independent. `SetUpTestSuite()` (static) shares expensive one-time setup.

## 4. Parameterised tests: tables of cases

```cpp
struct WrapCase { double in, out; };
class WrapAngle : public ::testing::TestWithParam<WrapCase> {};

TEST_P(WrapAngle, IntoMinusPiPi) {
    auto [in, out] = GetParam();
    EXPECT_NEAR(wrap(in), out, 1e-12);
}
INSTANTIATE_TEST_SUITE_P(Cases, WrapAngle, ::testing::Values(
    WrapCase{0.0, 0.0}, WrapCase{2.5 * M_PI, 0.5 * M_PI}, WrapCase{-3 * M_PI / 2, M_PI / 2}));   // avoid ±π: the boundary is convention-dependent
```

Typed tests (`TYPED_TEST`) run the same test over several types, for example a container template instantiated with `float` and `double`.

## 5. Mocking with gMock

Design for testability: depend on an **interface**, and inject the real or fake implementation.

```cpp
#include <gmock/gmock.h>

class IMotor {
public:
    virtual ~IMotor() = default;
    virtual void set_velocity(double rad_s) = 0;
    virtual double velocity() const = 0;
};

class MockMotor : public IMotor {
public:
    MOCK_METHOD(void, set_velocity, (double rad_s), (override));
    MOCK_METHOD(double, velocity, (), (const, override));
};

class Controller {                       // the unit under test receives the dependency
public:
    explicit Controller(IMotor& m) : m_(m) {}
    void stop() { if (m_.velocity() != 0.0) m_.set_velocity(0.0); }
private:
    IMotor& m_;
};

using ::testing::Return;
TEST(Controller, StopsMovingMotor) {
    MockMotor motor;
    EXPECT_CALL(motor, velocity()).WillOnce(Return(2.5));
    EXPECT_CALL(motor, set_velocity(0.0)).Times(1);      // verified when the mock is destroyed
    Controller c(motor);
    c.stop();
}
TEST(Controller, DoesNothingWhenStopped) {
    MockMotor motor;
    EXPECT_CALL(motor, velocity()).WillOnce(Return(0.0));
    EXPECT_CALL(motor, set_velocity).Times(0);
    Controller(motor).stop();
}
```

| gMock tool | Meaning |
|---|---|
| `EXPECT_CALL(m, f(args))` | expect the call with matching arguments |
| `.Times(n)`, `AtLeast(n)` | call count |
| `.WillOnce(Return(v))`, `.WillRepeatedly(...)` | scripted results |
| matchers: `_`, `Eq`, `Gt`, `DoubleNear(x, tol)`, `HasSubstr` | argument constraints |
| `InSequence s;` | enforce call order |
| `NiceMock<T>` / `StrictMock<T>` | ignore / fail on uninteresting calls |

> [!WARNING]
> Mock what you **own**: thin interfaces around hardware, networks and clocks. Don't mock value types or third-party APIs directly (wrap them first). Over-mocking produces tests that pass while the real integration is broken, so pair unit tests with integration tests on real (or simulated) hardware.

## 6. Death tests

```cpp
TEST(SafetyDeathTest, AbortsOnInvalidConfig) {
    EXPECT_DEATH(load_config("/nonexistent"), "config not found");   // runs in a child process
}
```

They verify `assert`/`abort` paths. Suffix the suite name with `DeathTest` so these tests run first.

## 7. Practice

- Arrange–Act–Assert in every test. Name tests after the behaviour (`ReturnsEmptyWhenNoPath`).
- Keep tests fast and deterministic: inject clocks and random seeds, no sleeps, no real network.
- Run them under sanitizers in CI (`-fsanitize=address,undefined`), and measure coverage with gcov/lcov (`--coverage`).
- Integrate with CMake via `gtest_discover_tests` and `ctest -j`.

## 8. Exam-ready answers

> [!EXAM]
> **Test fixtures and mocks.** In GoogleTest, a test fixture is a class derived from `::testing::Test` whose `SetUp` and `TearDown` methods run before and after each test defined with `TEST_F`, giving every test a fresh, identically initialised environment and removing duplicated setup. A mock object, defined with gMock's `MOCK_METHOD` in a class implementing an interface, replaces a real dependency in a unit test; expectations set with `EXPECT_CALL` specify which calls, with which arguments and how many times, should occur and what they return, and are verified automatically. Mocks require code to depend on abstractions injected through constructors or parameters (dependency injection), which isolates units from hardware, networks and other slow or nondeterministic components.

## 9. Cheat sheet

| Need | gtest / gmock |
|---|---|
| test | `TEST(Suite, Name) { EXPECT_EQ(a, b); }` |
| fatal check | `ASSERT_*` |
| floats | `EXPECT_NEAR(a, b, tol)` |
| exceptions | `EXPECT_THROW(f(), std::invalid_argument)` |
| fixture | `class F : public ::testing::Test`, `TEST_F(F, Name)` |
| table of cases | `TEST_P` + `INSTANTIATE_TEST_SUITE_P` |
| mock | `MOCK_METHOD(ret, name, (args), (const, override))` |
| expectation | `EXPECT_CALL(mock, f(_)).WillOnce(Return(v))` |
| CMake | `GTest::gtest_main`, `gtest_discover_tests(t)` |

> [!INTERVIEW]
> **"How do you unit-test code that talks to a serial motor controller?"** Introduce an interface (`IMotorBus` with `send(frame)` and `receive()`) and make the controller depend on it through constructor injection. In production, pass the serial implementation. In tests, pass a gMock mock (or a hand-written fake that records frames and plays back scripted replies). Then verify that the right frames are sent and that timeouts and malformed replies are handled, deterministically and without hardware. Add a separate hardware-in-the-loop test for the real driver.
