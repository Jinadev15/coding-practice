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

## Worked example: keeping both sides consistent

A `Team` has many `Robot`s and each robot knows its team. That bidirectional association is easy to corrupt if callers update one side only, so give **one** method responsibility for both ends:

```python
class Team:
    def __init__(self, name):
        self.name = name
        self._robots: set["Robot"] = set()
    @property
    def robots(self) -> frozenset["Robot"]:
        return frozenset(self._robots)          # read-only view: callers can't bypass add()
    def add(self, robot: "Robot") -> None:
        if robot.team is self:
            return
        if robot.team is not None:
            robot.team._robots.discard(robot)   # leave the old team
        self._robots.add(robot)
        robot._team = self

class Robot:
    def __init__(self, name):
        self.name, self._team = name, None
    @property
    def team(self):
        return self._team
    def __repr__(self):
        return self.name

red, blue, r1 = Team("red"), Team("blue"), Robot("r1")
red.add(r1); blue.add(r1)
print(red.robots, blue.robots, r1.team.name)
```

```output
frozenset() frozenset({r1}) blue
```

**Composition vs aggregation in one sentence:** if destroying the whole destroys the parts (a `Robot` owns its `Battery`), it is composition. If the parts live on independently (a `Team` and its `Robot`s), it is aggregation, a kind of association.

## Common mistakes

- **Exposing the mutable list** (`team.robots.append(r)`). This bypasses the invariant. Return a tuple or frozenset instead.
- **Strong reference cycles holding big objects alive.** Use `weakref` for back-pointers that shouldn't own the target, such as observers and caches.
- **Forgetting cascades.** When a team is deleted, what happens to its robots? Decide, then implement it in one place.

## Check your understanding

1. A `Course` has `Enrollment` objects linking `Student`s with a grade. What is `Enrollment` in UML terms?
2. Why return `frozenset` instead of the internal set?

<details><summary>Answers</summary>

1. An association class: the link itself has data (the grade, the date).
2. So callers can't change the set without going through `add`/`remove`, which keep both sides consistent.

</details>
