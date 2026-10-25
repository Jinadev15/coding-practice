---
id: py-university-enrollment
title: Consistent Many-to-Many Relationships with an Association Class
difficulty: Hard
order: 1
tags: association, aggregation, composition, association class, bidirectional links, cascades
time_limit: 5
---
## Statement
Model a university where every relationship stays consistent under any sequence of operations:
- **Composition**: a `Department` owns its courses, so removing a course destroys its enrollments.
- **Aggregation**: students belong to the university, independent of departments.
- **Many-to-many with data**: `Enrollment(student, course, grade)` is an **association class**.
- **Bidirectional navigation**: `student.courses` and `course.students` must always agree.

**`Student`**: `id`, `name`, read-only `enrollments` (a tuple sorted by course code), and `courses` (a tuple of `Course` in the same order).
**`Course`**: `code`, `title`, `capacity`, read-only `enrollments` (a tuple sorted by student id), and `students`.
**`Enrollment`**: `student`, `course`, `grade` (None or a float from 0 to 100).

**`University`**

| Method | Contract |
|---|---|
| `add_student(id, name) -> Student` | A duplicate id raises `ValueError`. |
| `department(name) -> Department` | Gets the department, or creates it. |
| `Department.add_course(code, title, capacity) -> Course` | Course codes are unique **across the university** (`ValueError`), and `capacity >= 1`. |
| `Department.remove_course(code)` | **Cascades**: every enrollment disappears from both sides. An unknown code raises `KeyError`. |
| `enroll(student_id, code) -> Enrollment` | An unknown student or course raises `KeyError`. `ValueError("already enrolled")` or `ValueError("course full")`. |
| `drop(student_id, code) -> bool` | |
| `set_grade(student_id, code, grade)` | Not enrolled raises `KeyError`. Outside 0–100 raises `ValueError`. |
| `remove_student(id)` | Drops all of the student's enrollments. Unknown raises `KeyError`. |
| `transcript(student_id) -> list[tuple[str, float \| None]]` | Sorted by course code. |
| `average(student_id) -> float \| None` | Mean of the graded courses, rounded to 2 places. |

The collections exposed to callers must be immutable views (tuples). Mutating a returned value must never change the model.

## Starter
```python
class Student:
    def __init__(self, sid, name):
        self.id, self.name = sid, name
        self.courses = []


class Course:
    def __init__(self, code, title, capacity):
        self.code, self.title, self.capacity = code, title, capacity
        self.students = []


class Department:
    def __init__(self, name):
        self.name = name
        self.courses = {}

    def add_course(self, code, title, capacity):
        self.courses[code] = Course(code, title, capacity)
        return self.courses[code]


class University:
    def __init__(self):
        self.students = {}
        self.departments = {}

    def add_student(self, sid, name):
        self.students[sid] = Student(sid, name)
        return self.students[sid]

    def department(self, name):
        return self.departments.setdefault(name, Department(name))

    def enroll(self, sid, code):
        for d in self.departments.values():
            if code in d.courses:
                d.courses[code].students.append(self.students[sid])
```

## Driver
```python
import sys

def attempt(label, fn):
    try:
        r = fn()
        print(f"{label}: {r!r}" if not hasattr(r, "student") else f"{label}: enrolled {r.student.id} in {r.course.code}")
    except (KeyError, ValueError) as e:
        print(f"{label}: {type(e).__name__}")

def check(u, label):
    ok = True
    studs = u._all_students()
    for s in studs:
        for e in s.enrollments:
            ok &= e.student is s and e in e.course.enrollments and s in e.course.students
        ok &= [c.code for c in s.courses] == sorted(c.code for c in s.courses)
    print(f"[{label}] consistent={ok}")

for cmd in sys.stdin.read().split():
    u = University()
    if cmd == "basic":
        for sid, n in [("s1", "Ada"), ("s2", "Linus"), ("s3", "Grace")]:
            u.add_student(sid, n)
        attempt("dup student", lambda: u.add_student("s1", "x"))
        cs, me = u.department("CS"), u.department("ME")
        print(u.department("CS") is cs)
        cs.add_course("CS101", "Programming", 2); cs.add_course("CS201", "Algorithms", 3); me.add_course("ME110", "Statics", 1)
        attempt("dup course across depts", lambda: me.add_course("CS101", "Again", 5))
        attempt("bad capacity", lambda: me.add_course("ME999", "Zero", 0))
        for sid, code in [("s1", "CS201"), ("s1", "CS101"), ("s2", "CS101"), ("s3", "CS101"), ("s1", "CS101"), ("s9", "CS101"), ("s1", "XX1"), ("s3", "ME110")]:
            attempt(f"enroll {sid} {code}", lambda: u.enroll(sid, code))
        s1 = u.add_student("s4", "Barbara")
        st = [s for s in u._all_students() if s.id == "s1"][0]
        print("s1 courses", [c.code for c in st.courses], "CS101 students", [s.id for s in u.department("CS")._courses_by_code()["CS101"].students])
        attempt("grade", lambda: u.set_grade("s1", "CS101", 91.5))
        attempt("grade s1 CS201", lambda: u.set_grade("s1", "CS201", 78))
        attempt("grade range", lambda: u.set_grade("s1", "CS201", 101))
        attempt("grade not enrolled", lambda: u.set_grade("s3", "CS201", 50))
        print("transcript", u.transcript("s1"), "avg", u.average("s1"), "avg s2", u.average("s2"))
        try:
            st.enrollments += (None,)
        except Exception:
            pass
        print("views immutable:", isinstance(st.enrollments, tuple), len(st.enrollments))
        check(u, "basic")
    elif cmd == "cascade":
        for i in range(1, 6):
            u.add_student(f"s{i}", f"S{i}")
        d = u.department("Robotics")
        d.add_course("R1", "Kinematics", 10); d.add_course("R2", "Control", 2); d.add_course("R3", "Vision", 10)
        for i in range(1, 6):
            u.enroll(f"s{i}", "R1")
            if i % 2: u.enroll(f"s{i}", "R3")
        u.enroll("s2", "R2"); u.set_grade("s2", "R2", 88)
        print("drop", u.drop("s1", "R1"), u.drop("s1", "R1"))
        d.remove_course("R3")
        attempt("remove unknown course", lambda: d.remove_course("R3"))
        print("after course removal:", [(s.id, [c.code for c in s.courses]) for s in u._all_students()])
        attempt("enroll removed", lambda: u.enroll("s2", "R3"))
        u.remove_student("s2")
        attempt("remove unknown student", lambda: u.remove_student("s2"))
        print("R1 students", [s.id for s in d._courses_by_code()["R1"].students], "R2 enrollments", len(d._courses_by_code()["R2"].enrollments))
        attempt("transcript removed", lambda: u.transcript("s2"))
        u.enroll("s3", "R2"); u.enroll("s4", "R2")
        attempt("full", lambda: u.enroll("s5", "R2"))
        check(u, "cascade")
    elif cmd == "load":
        d = u.department("Big")
        for c in range(200):
            d.add_course(f"C{c:03d}", f"Course {c}", 1 + c % 60)
        for s in range(3000):
            u.add_student(f"st{s:04d}", "x")
        ok = full = dup = 0
        for k in range(60000):
            sid, code = f"st{(k * 7) % 3000:04d}", f"C{(k * 13) % 200:03d}"
            try:
                u.enroll(sid, code); ok += 1
                if k % 5 == 0: u.set_grade(sid, code, (k % 101))
            except ValueError as e:
                full += str(e) == "course full"; dup += str(e) == "already enrolled"
        for c in range(0, 200, 10):
            d.remove_course(f"C{c:03d}")
        for s in range(0, 3000, 7):
            u.remove_student(f"st{s:04d}")
        left = sum(len(s.enrollments) for s in u._all_students())
        print("ok", ok, "full", full, "dup", dup, "enrollments left", left, "avg st0001", u.average("st0001"))
        check(u, "load")
```

## Tests
=== sample
basic
---
dup student: ValueError
True
dup course across depts: ValueError
bad capacity: ValueError
enroll s1 CS201: enrolled s1 in CS201
enroll s1 CS101: enrolled s1 in CS101
enroll s2 CS101: enrolled s2 in CS101
enroll s3 CS101: ValueError
enroll s1 CS101: ValueError
enroll s9 CS101: KeyError
enroll s1 XX1: KeyError
enroll s3 ME110: enrolled s3 in ME110
s1 courses ['CS101', 'CS201'] CS101 students ['s1', 's2']
grade: None
grade s1 CS201: None
grade range: ValueError
grade not enrolled: KeyError
transcript [('CS101', 91.5), ('CS201', 78.0)] avg 84.75 avg s2 None
views immutable: True 2
[basic] consistent=True
=== hidden
cascade
---
drop True False
remove unknown course: KeyError
after course removal: [('s1', []), ('s2', ['R1', 'R2']), ('s3', ['R1']), ('s4', ['R1']), ('s5', ['R1'])]
enroll removed: KeyError
remove unknown student: KeyError
R1 students ['s3', 's4', 's5'] R2 enrollments 0
transcript removed: KeyError
full: ValueError
[cascade] consistent=True
=== hidden
load
---
ok 2580 full 8400 dup 49020 enrollments left 1966 avg st0001 None
[load] consistent=True

## Hints
- Store links in **one place per side**: `Student._enrollments: dict[code, Enrollment]` and `Course._enrollments: dict[student_id, Enrollment]`. Only `University` and `Department` methods modify them (`_link`/`_unlink` helpers).
- The judge calls two internal helpers, so provide them: `University._all_students()` (students sorted by id) and `Department._courses_by_code()` (a dict).
- `remove_course`: for each enrollment of the course, remove it from its student's dict, then delete the course. `remove_student` does the reverse.
- The university needs to find a course from any department, so keep a global `code → (department, course)` index, updated by `add_course` and `remove_course`. Give each `Department` a back-reference to its university.

## Solution
```python
from dataclasses import dataclass


@dataclass(eq=False)
class Enrollment:                      # association class: the link carries data
    student: "Student"
    course: "Course"
    grade: float | None = None


class Student:
    def __init__(self, sid: str, name: str):
        self.id, self.name = sid, name
        self._enrollments: dict[str, Enrollment] = {}

    @property
    def enrollments(self) -> tuple[Enrollment, ...]:
        return tuple(self._enrollments[c] for c in sorted(self._enrollments))

    @property
    def courses(self) -> tuple["Course", ...]:
        return tuple(e.course for e in self.enrollments)


class Course:
    def __init__(self, code: str, title: str, capacity: int):
        self.code, self.title, self.capacity = code, title, capacity
        self._enrollments: dict[str, Enrollment] = {}

    @property
    def enrollments(self) -> tuple[Enrollment, ...]:
        return tuple(self._enrollments[s] for s in sorted(self._enrollments))

    @property
    def students(self) -> tuple[Student, ...]:
        return tuple(e.student for e in self.enrollments)


class Department:
    def __init__(self, name: str, university: "University"):
        self.name = name
        self._university = university
        self._courses: dict[str, Course] = {}           # composition: the department owns its courses

    def add_course(self, code: str, title: str, capacity: int) -> Course:
        if capacity < 1:
            raise ValueError("capacity must be >= 1")
        if code in self._university._course_index:
            raise ValueError(f"duplicate course {code}")
        course = Course(code, title, capacity)
        self._courses[code] = course
        self._university._course_index[code] = course
        return course

    def remove_course(self, code: str) -> None:
        course = self._courses.pop(code)                # KeyError if unknown
        for enrollment in list(course._enrollments.values()):   # cascade to both sides
            del enrollment.student._enrollments[code]
        course._enrollments.clear()
        del self._university._course_index[code]

    def _courses_by_code(self) -> dict[str, Course]:
        return dict(self._courses)


class University:
    def __init__(self):
        self._students: dict[str, Student] = {}         # aggregation: independent of departments
        self._departments: dict[str, Department] = {}
        self._course_index: dict[str, Course] = {}

    def add_student(self, sid: str, name: str) -> Student:
        if sid in self._students:
            raise ValueError(f"duplicate student {sid}")
        self._students[sid] = Student(sid, name)
        return self._students[sid]

    def department(self, name: str) -> Department:
        if name not in self._departments:
            self._departments[name] = Department(name, self)
        return self._departments[name]

    def _get(self, sid: str, code: str) -> tuple[Student, Course]:
        return self._students[sid], self._course_index[code]    # KeyError for unknowns

    def enroll(self, sid: str, code: str) -> Enrollment:
        student, course = self._get(sid, code)
        if code in student._enrollments:
            raise ValueError("already enrolled")
        if len(course._enrollments) >= course.capacity:
            raise ValueError("course full")
        e = Enrollment(student, course)
        student._enrollments[code] = e                  # both ends updated together
        course._enrollments[sid] = e
        return e

    def drop(self, sid: str, code: str) -> bool:
        student, course = self._students.get(sid), self._course_index.get(code)
        if not student or not course or code not in student._enrollments:
            return False
        del student._enrollments[code]
        del course._enrollments[sid]
        return True

    def set_grade(self, sid: str, code: str, grade: float) -> None:
        student = self._students[sid]
        e = student._enrollments[code]                  # KeyError if not enrolled
        if not 0 <= grade <= 100:
            raise ValueError("grade must be in [0, 100]")
        e.grade = float(grade)

    def remove_student(self, sid: str) -> None:
        student = self._students.pop(sid)
        for code, e in list(student._enrollments.items()):
            del e.course._enrollments[sid]
        student._enrollments.clear()

    def transcript(self, sid: str) -> list[tuple[str, float | None]]:
        return [(e.course.code, e.grade) for e in self._students[sid].enrollments]

    def average(self, sid: str) -> float | None:
        grades = [e.grade for e in self._students[sid].enrollments if e.grade is not None]
        return round(sum(grades) / len(grades), 2) if grades else None

    def _all_students(self) -> list[Student]:
        return [self._students[s] for s in sorted(self._students)]
```

- **An association class**: a grade belongs to neither the student nor the course alone but to their *relationship*, so `Enrollment` is a first-class object shared by both sides.
- **One controlled entry point** (`enroll`, `drop`, `remove_*`) updates both ends of each link together, so `e in course.enrollments` exactly when `e in student.enrollments` holds after any sequence of operations. The judge checks it after 60,000 random enrollments and cascading deletions.
- **Deletion semantics are explicit**: removing a course (composition) cascades to its enrollments, and removing a student (aggregation) removes their links but no courses.
- **Immutable views**: properties return fresh tuples, so callers can read and navigate freely but can't bypass the invariants by appending to an internal list, which was the starter's bug.
