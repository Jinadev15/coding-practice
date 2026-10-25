# Relationships: Association, Aggregation, Composition

Objects collaborate through relationships, and modelling them correctly decides whether a system stays consistent as objects are created, linked and deleted. This lesson covers the UML relationships (**association**, **aggregation**, **composition**, **dependency**, **inheritance**) with their multiplicities, how to implement each in Python, keeping **bidirectional links consistent**, association classes, ownership and cascading deletion, and `weakref` to avoid leaks and cycles.

## 1. The relationships

| Relationship | Meaning | Lifetime | Python implementation |
|---|---|---|---|
| **Dependency** | uses temporarily | the duration of a call | a parameter or local variable |
| **Association** | knows about | independent | an attribute holding a reference (or an id) |
| **Aggregation** | has-a, parts can be shared or outlive the whole | independent | a collection of references to externally owned objects |
| **Composition** | owns, parts die with the whole | the whole's lifetime | parts created and held only by the whole, never handed out for external ownership |
| **Inheritance** | is-a | n/a | subclassing (use sparingly, see the composition lesson) |

**Multiplicity**: 1 (exactly one), 0..1 (optional, `X | None`), * (a list or set), with one-to-many and many-to-many combinations.

## 2. Composition: the whole controls the parts

```python
class Robot:
    def __init__(self, robot_id: str):
        self.id = robot_id
        self._wheels = [Wheel(side) for side in ("left", "right")]   # created by the whole
        self._battery = Battery(capacity_wh=500)

    def wheel_speeds(self) -> tuple[float, ...]:                      # expose behaviour, not the parts
        return tuple(w.speed for w in self._wheels)
```

The parts are private, created inside, and never shared, so deleting the robot deletes them. Handing out the internal list (`return self._wheels`) leaks control. Return copies, tuples or read-only views instead.

## 3. Bidirectional associations: keep both ends consistent

```python
class Team:
    def __init__(self, name):
        self.name = name
        self._members: set["Robot"] = set()

    @property
    def members(self) -> frozenset["Robot"]:
        return frozenset(self._members)          # read-only view

    def add(self, robot: "Robot") -> None:
        if robot.team is self:
            return
        if robot.team is not None:
            robot.team.remove(robot)              # leave the old team first
        self._members.add(robot)
        robot._team = self                        # one controlled place updates both ends

    def remove(self, robot: "Robot") -> None:
        self._members.discard(robot)
        if robot._team is self:
            robot._team = None
```

> [!KEY]
> Pick **one side as the owner of the link** and route every change through its methods, so both directions are always updated together. Exposing raw mutable collections (`team.members.append(r)`) lets callers update one end and forget the other, which breaks the invariant "r in t.members ⇔ r.team is t".

## 4. Association classes

When a relationship has its own data, make it a class. A student-course enrollment has a grade and a date. A robot-charger assignment has a slot and a start time.

```python
@dataclass
class Enrollment:
    student: "Student"
    course: "Course"
    grade: float | None = None
```

Many-to-many relationships are usually best modelled through an association class held by a registry (a `University` or `Fleet` object) that keeps indices in both directions.

## 5. Deletion and cascades

Decide for every relationship what happens on deletion:
- **Cascade** (composition): deleting a course deletes its enrollments.
- **Nullify** (optional association): deleting a charger unassigns its robots.
- **Restrict**: refuse to delete a customer with active rentals.

Implement these in the owning aggregate's methods, so no dangling references remain.

## 6. `weakref`: observe without owning

Strong references keep objects alive. Back-references and caches often shouldn't:

```python
import weakref

class Node:
    def __init__(self, parent=None):
        self.children = []                                        # strong refs down
        self._parent = weakref.ref(parent) if parent else None    # weak ref up
    @property
    def parent(self):
        return self._parent() if self._parent else None           # None once the parent is gone
```

`weakref.WeakValueDictionary` makes a registry that doesn't keep its objects alive, and `weakref.finalize` registers cleanup when an object dies.

> [!EXAM]
> **How do you implement a bidirectional association in Python so that it stays consistent?**
> Store the references on both sides as private attributes, and expose them only through read-only properties (a frozenset or tuple for collections). Make one side (or a coordinating aggregate) the single entry point for changes: its `add` and `remove` methods update both ends together, including detaching from a previous partner. Callers can then never change one end without the other, so the invariant (`x in a.items` exactly when `x.owner is a`) always holds. Deletion rules (cascade, nullify or restrict) are implemented in the same place.
