# Thinking in Objects: From Problem to Classes

Writing classes is easy. Choosing the *right* classes is the skill. Good object-oriented design starts from the problem domain: finding the concepts, deciding which are **values** and which are **entities**, assigning each **responsibility** to exactly one place, and making invalid states impossible. This lesson walks through that process in Python, using ideas from Domain-Driven Design (Eric Evans), CRC cards and "tell, don't ask", with modern tools: `dataclasses`, `Enum`, `Decimal`, and `__post_init__` validation.

## 1. From requirements to a model

Requirement: *"Customers rent delivery robots by the hour. A rental has a start and end time. Prices are in a currency, with discounts for members. Robots must be charged above 30% to be rented."*

| Step | Result |
|---|---|
| Underline the **nouns** | customer, robot, rental, time, price, currency, discount, member, charge |
| Underline the **verbs** | rent, price, discount, charge, check availability |
| Group into candidate classes | `Customer`, `Robot`, `Rental`, `Money`, `TimeRange`, `PricingPolicy` |
| Find the **invariants** | money never mixes currencies, a time range has start < end, a robot's battery is in [0, 1], a rental needs a robot charged above 30% |
| Assign each invariant to one class | `Money`, `TimeRange`, `Robot`, and the `rent` operation |

**CRC cards** (Class, Responsibilities, Collaborators) are a quick way to test a design: write each class on a card with what it knows and does, then walk through scenarios. A class with no responsibilities is probably just data. A class with ten unrelated ones needs splitting.

## 2. Values and entities

| | Value object | Entity |
|---|---|---|
| Identity | none: equal attributes means the same value | a stable id (this robot, this account) |
| Mutability | immutable (`@dataclass(frozen=True)`) | mutable state over time |
| Equality and hash | by attributes | by id (or identity) |
| Examples | `Money`, `TimeRange`, `Pose`, `Address` | `Robot`, `Customer`, `Rental`, `Account` |

```python
from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True, slots=True)
class Money:
    amount: Decimal
    currency: str

    def __post_init__(self):
        if not isinstance(self.amount, Decimal):
            object.__setattr__(self, "amount", Decimal(str(self.amount)))    # normalise inside the frozen object
        if len(self.currency) != 3 or not self.currency.isupper():
            raise ValueError(f"bad currency {self.currency!r}")

    def __add__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("cannot add different currencies")
        return Money(self.amount + other.amount, self.currency)
```

> [!KEY]
> **Values are immutable and validated at construction**, so every `Money` that exists is valid, and it can be shared, hashed, cached and used as a dict key safely. **Entities** have identity, so two robots with identical battery levels are still different robots. Give them an `id` and define equality on it (or keep the default identity equality).

## 3. Make illegal states unrepresentable

- Use `Enum` instead of strings: `class RentalStatus(Enum): ACTIVE = auto(); RETURNED = auto()`. Typos become `AttributeError`s, not silent bugs.
- Use separate types instead of flags: `ActiveRental` and `ClosedRental`, or a `status` plus methods that check it, rather than six booleans that can contradict each other.
- Use `Decimal` for money (`0.1 + 0.2 != 0.3` in floats), and timezone-aware `datetime`s for time.
- Have constructors (`__post_init__`) **reject** invalid input. Don't let half-valid objects exist.

## 4. Tell, don't ask

```python
# Asking: logic outside, data inside; duplicated wherever robots are rented
if robot.battery > 0.3 and robot.status == "idle":
    robot.status = "rented"

# Telling: the rule lives with the data it protects
class Robot:
    def reserve(self) -> None:
        if self.status is not RobotStatus.IDLE:
            raise RobotUnavailable(self.id)
        if self.battery < 0.3:
            raise BatteryTooLow(self.id, self.battery)
        self.status = RobotStatus.RENTED
```

## 5. Python-specific modelling tools

| Tool | Use |
|---|---|
| `@dataclass(frozen=True, slots=True)` | value objects: `__init__`, `__repr__`, `__eq__` and `__hash__` generated, plus immutability and less memory |
| `__post_init__` | validation and normalisation |
| `@property` | computed attributes, read-only views |
| `functools.total_ordering` / `order=True` | comparable values |
| `typing.Protocol` | describe roles (interfaces) without inheritance |
| `Enum` / `StrEnum` | closed sets of states |
| custom exceptions | domain errors with meaning (`InsufficientFunds`), not bare `ValueError`s everywhere |

## 6. Common smells

- **Anaemic model**: data-only classes, with all the logic in "manager" functions.
- **God object**: a `RobotManager` that does everything.
- **Primitive obsession**: passing `(amount, currency)` tuples and float timestamps around instead of `Money` and `datetime`.
- **Feature envy**: a method that mostly uses another object's data probably belongs to that object.

> [!EXAM]
> **What is the difference between a value object and an entity, and how do you implement each in Python?**
> A value object has no identity: it's defined entirely by its attributes, so two with equal attributes are interchangeable. It should be immutable, validated at construction, and compared and hashed by value. In Python, use `@dataclass(frozen=True)` with `__post_init__` validation, and return new instances from operations. An entity has a stable identity that persists while its attributes change, such as a robot or an account. Implement it as a regular (mutable) class carrying an id, with equality and hashing based on that id (or default identity), and with methods that enforce its invariants as its state changes.
