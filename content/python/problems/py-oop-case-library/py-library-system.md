---
id: py-library-system
title: "Case Study: Library Management System"
difficulty: Hard
order: 1
tags: case study, aggregate root, entities, enums, Decimal, deque, injected time, domain exceptions
time_limit: 5
---
## Statement
Implement the library from the case-study lesson. `Library` is the **aggregate root**: every state change goes through it. Dates are `datetime.date` objects passed in by the caller (injected time).

**Domain exceptions** (all subclass `LibraryError`): `UnknownItem`, `NotAvailable`, `LimitReached`, `FinesOutstanding`, `ReservedForAnother`, `AlreadyHeld`.

**Rules**
- `Tier.STANDARD`: at most 3 active loans, 14-day loans. `Tier.PREMIUM`: at most 10 loans, 28-day loans.
- Fines are `Decimal("0.25")` per day late, capped at `Decimal("10.00")` per loan, added to the member's balance when the item is **returned**.

| Method | Contract |
|---|---|
| `add_title(isbn, title, author)` | |
| `add_copy(isbn, barcode)` | `UnknownItem` for an unknown title. A duplicate barcode raises `ValueError`. |
| `add_member(member_id, tier)` | |
| `checkout(member_id, barcode, today) -> date` | Returns the due date. Checks run in this order: unknown member or barcode gives `UnknownItem`; balance `>= 5.00` gives `FinesOutstanding`; at the tier limit gives `LimitReached`; the copy on loan gives `NotAvailable`; the copy **on the hold shelf** for someone else gives `ReservedForAnother`. A member collecting their hold-shelf copy removes their hold. |
| `return_copy(barcode, today) -> Decimal` | Returns the fine charged. If the title has holds, the copy goes to the **hold shelf** for the first member in the queue (FIFO). Otherwise it's available. Unknown barcode or not on loan gives `UnknownItem`. |
| `place_hold(member_id, isbn)` | A member who already has a hold on the title, or a copy of it on loan, raises `AlreadyHeld`. |
| `pay(member_id, amount) -> Decimal` | Returns the remaining balance, which never goes negative. |
| `loans(member_id) -> list[tuple[str, date]]` | (barcode, due), sorted by barcode. |
| `overdue(today) -> list[tuple[str, str, int]]` | (member, barcode, days late) for active loans past due, sorted by member then barcode. |
| `available(isbn) -> int`, `balance(member_id) -> Decimal` | |

## Starter
```python
from datetime import date, timedelta
from decimal import Decimal
from enum import Enum


class LibraryError(Exception): pass
class UnknownItem(LibraryError): pass
class NotAvailable(LibraryError): pass
class LimitReached(LibraryError): pass
class FinesOutstanding(LibraryError): pass
class ReservedForAnother(LibraryError): pass
class AlreadyHeld(LibraryError): pass


class Tier(Enum):
    STANDARD = "standard"
    PREMIUM = "premium"


class Library:
    def __init__(self):
        self.copies = {}
        self.members = {}

    def add_title(self, isbn, title, author): pass
    def add_copy(self, isbn, barcode): self.copies[barcode] = None
    def add_member(self, member_id, tier): self.members[member_id] = tier

    def checkout(self, member_id, barcode, today):
        self.copies[barcode] = member_id
        return today + timedelta(days=14)

    def return_copy(self, barcode, today):
        self.copies[barcode] = None
        return Decimal("0")
```

## Driver
```python
import sys
from datetime import date, timedelta
from decimal import Decimal

D = lambda m, d: date(2026, m, d)

def attempt(label, fn):
    try:
        print(f"{label}: {fn()}")
    except LibraryError as e:
        print(f"{label}: {type(e).__name__}")
    except ValueError:
        print(f"{label}: ValueError")

for cmd in sys.stdin.read().split():
    lib = Library()
    lib.add_title("111", "Probabilistic Robotics", "Thrun")
    lib.add_title("222", "Clean Code", "Martin")
    for bc, isbn in [("A1", "111"), ("A2", "111"), ("B1", "222")]:
        lib.add_copy(isbn, bc)
    lib.add_member("ana", Tier.STANDARD); lib.add_member("ben", Tier.PREMIUM); lib.add_member("cy", Tier.STANDARD)
    if cmd == "loans":
        attempt("dup barcode", lambda: lib.add_copy("111", "A1"))
        attempt("unknown title", lambda: lib.add_copy("999", "Z1"))
        attempt("ana A1", lambda: lib.checkout("ana", "A1", D(3, 1)))
        attempt("ben A1", lambda: lib.checkout("ben", "A1", D(3, 1)))
        attempt("ben A2", lambda: lib.checkout("ben", "A2", D(3, 2)))
        attempt("ghost", lambda: lib.checkout("zed", "B1", D(3, 2)))
        attempt("available 111", lambda: lib.available("111"))
        attempt("ana B1", lambda: lib.checkout("ana", "B1", D(3, 5)))
        print("ana loans", lib.loans("ana"))
        print("overdue 3/20", lib.overdue(D(3, 20)))
        attempt("return A1 on time", lambda: lib.return_copy("A1", D(3, 15)))
        attempt("return B1 late", lambda: lib.return_copy("B1", D(3, 24)))
        attempt("return again", lambda: lib.return_copy("B1", D(3, 25)))
        attempt("return A2 very late", lambda: lib.return_copy("A2", D(6, 30)))
        print("balances", lib.balance("ana"), lib.balance("ben"))
    elif cmd == "limits":
        for i in range(4):
            lib.add_copy("222", f"C{i}")
        for i in range(4):
            attempt(f"ana C{i}", lambda: lib.checkout("ana", f"C{i}", D(1, 1)))
        attempt("return late", lambda: lib.return_copy("C0", D(2, 5)))
        attempt("ana blocked by fines", lambda: lib.checkout("ana", "C0", D(2, 6)))
        attempt("pay 3", lambda: lib.pay("ana", Decimal("3")))
        attempt("ana after partial pay", lambda: lib.checkout("ana", "C0", D(2, 6)))
        attempt("overpay", lambda: lib.pay("ana", Decimal("100")))
        attempt("ben premium 28 days", lambda: lib.checkout("ben", "C3", D(2, 1)))
    elif cmd == "holds":
        lib.checkout("ana", "A1", D(4, 1)); lib.checkout("ana", "A2", D(4, 1))
        attempt("ben holds 111", lambda: lib.place_hold("ben", "111"))
        attempt("cy holds 111", lambda: lib.place_hold("cy", "111"))
        attempt("ben holds again", lambda: lib.place_hold("ben", "111"))
        attempt("ana holds own", lambda: lib.place_hold("ana", "111"))
        attempt("return A1", lambda: lib.return_copy("A1", D(4, 10)))
        attempt("available 111", lambda: lib.available("111"))
        attempt("cy takes A1", lambda: lib.checkout("cy", "A1", D(4, 11)))
        attempt("ben takes A1", lambda: lib.checkout("ben", "A1", D(4, 11)))
        attempt("return A2", lambda: lib.return_copy("A2", D(4, 12)))
        attempt("cy takes A2", lambda: lib.checkout("cy", "A2", D(4, 12)))
        attempt("return A1 (no holds)", lambda: lib.return_copy("A1", D(4, 20)))
        attempt("available 111", lambda: lib.available("111"))
        attempt("ana takes A1", lambda: lib.checkout("ana", "A1", D(4, 21)))
    elif cmd == "load":
        for i in range(500):
            lib.add_copy("111" if i % 2 else "222", f"X{i:03d}")
        for m in range(60):
            lib.add_member(f"m{m:02d}", Tier.PREMIUM if m % 3 == 0 else Tier.STANDARD)
        day = date(2026, 1, 1); fines = Decimal("0"); errors = {}
        active = []
        for step in range(8000):
            day += timedelta(days=step % 2)
            member, bc = f"m{(step * 7) % 60:02d}", f"X{(step * 13) % 500:03d}"
            try:
                if step % 3 == 2 and active:
                    fines += lib.return_copy(active.pop(0), day)
                else:
                    lib.checkout(member, bc, day); active.append(bc)
                    if step % 11 == 0: lib.place_hold(f"m{(step * 5) % 60:02d}", "111")
            except LibraryError as e:
                errors[type(e).__name__] = errors.get(type(e).__name__, 0) + 1
                if isinstance(e, FinesOutstanding): lib.pay(member, Decimal("50"))
        print("fines", fines, "errors", dict(sorted(errors.items())), "overdue", len(lib.overdue(day)))
```

## Tests
=== sample
loans
---
dup barcode: ValueError
unknown title: UnknownItem
ana A1: 2026-03-15
ben A1: NotAvailable
ben A2: 2026-03-30
ghost: UnknownItem
available 111: 0
ana B1: 2026-03-19
ana loans [('A1', datetime.date(2026, 3, 15)), ('B1', datetime.date(2026, 3, 19))]
overdue 3/20 [('ana', 'A1', 5), ('ana', 'B1', 1)]
return A1 on time: 0.00
return B1 late: 1.25
return again: UnknownItem
return A2 very late: 10.00
balances 1.25 10.00
=== hidden
limits
---
ana C0: 2026-01-15
ana C1: 2026-01-15
ana C2: 2026-01-15
ana C3: LimitReached
return late: 5.25
ana blocked by fines: FinesOutstanding
pay 3: 2.25
ana after partial pay: 2026-02-20
overpay: 0
ben premium 28 days: 2026-03-01
=== hidden
holds
---
ben holds 111: None
cy holds 111: None
ben holds again: AlreadyHeld
ana holds own: AlreadyHeld
return A1: 0.00
available 111: 0
cy takes A1: ReservedForAnother
ben takes A1: 2026-05-09
return A2: 0.00
cy takes A2: 2026-04-26
return A1 (no holds): 0.00
available 111: 1
ana takes A1: 2026-05-05
=== hidden
load
---
fines 26123.25 errors {'AlreadyHeld': 237, 'FinesOutstanding': 2493, 'LimitReached': 49, 'ReservedForAnother': 49} overdue 67

## Hints
- Model the copy status as an `Enum` with `AVAILABLE`, `ON_LOAN` and `ON_HOLD_SHELF`, plus `held_for` (a member id) for the shelf case.
- Keep the indices in the root: `copies[barcode]`, `loans[barcode] -> Loan`, `holds[isbn] -> deque[member_id]`, and each member's set of active barcodes.
- `return_copy`: compute the fine with `min(cap, 0.25 × days_late)`, add it to the balance, close the loan, then check `holds[isbn]` (`popleft`) to decide the copy's new status.
- Count a member's active loans directly from the index, and compare against the tier limit before checking availability, following the documented order.

## Solution
```python
from collections import deque
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from enum import Enum, auto


class LibraryError(Exception): pass
class UnknownItem(LibraryError): pass
class NotAvailable(LibraryError): pass
class LimitReached(LibraryError): pass
class FinesOutstanding(LibraryError): pass
class ReservedForAnother(LibraryError): pass
class AlreadyHeld(LibraryError): pass


class Tier(Enum):
    STANDARD = ("standard", 3, 14)
    PREMIUM = ("premium", 10, 28)

    def __init__(self, label, limit, days):
        self.label, self.limit, self.days = label, limit, days


class CopyStatus(Enum):
    AVAILABLE = auto()
    ON_LOAN = auto()
    ON_HOLD_SHELF = auto()


FINE_PER_DAY = Decimal("0.25")
FINE_CAP = Decimal("10.00")
BLOCKING_BALANCE = Decimal("5.00")


@dataclass
class Copy:
    barcode: str
    isbn: str
    status: CopyStatus = CopyStatus.AVAILABLE
    held_for: str | None = None


@dataclass
class Member:
    id: str
    tier: Tier
    balance: Decimal = Decimal("0")


@dataclass
class Loan:
    barcode: str
    member_id: str
    due: date

    def fine(self, today: date) -> Decimal:
        return min(FINE_CAP, FINE_PER_DAY * max(0, (today - self.due).days))


class Library:
    def __init__(self):
        self._titles: dict[str, tuple[str, str]] = {}
        self._copies: dict[str, Copy] = {}
        self._members: dict[str, Member] = {}
        self._loans: dict[str, Loan] = {}                     # barcode -> active loan
        self._holds: dict[str, deque[str]] = {}               # isbn -> FIFO queue of member ids

    def add_title(self, isbn, title, author):
        self._titles[isbn] = (title, author)
        self._holds.setdefault(isbn, deque())

    def add_copy(self, isbn, barcode):
        if isbn not in self._titles:
            raise UnknownItem(isbn)
        if barcode in self._copies:
            raise ValueError(f"duplicate barcode {barcode}")
        self._copies[barcode] = Copy(barcode, isbn)

    def add_member(self, member_id, tier):
        self._members[member_id] = Member(member_id, tier)

    def _member(self, member_id) -> Member:
        try:
            return self._members[member_id]
        except KeyError:
            raise UnknownItem(member_id) from None

    def _active(self, member_id) -> list[Loan]:
        return [l for l in self._loans.values() if l.member_id == member_id]

    def checkout(self, member_id, barcode, today) -> date:
        member = self._member(member_id)
        copy = self._copies.get(barcode)
        if copy is None:
            raise UnknownItem(barcode)
        if member.balance >= BLOCKING_BALANCE:
            raise FinesOutstanding(member_id)
        if len(self._active(member_id)) >= member.tier.limit:
            raise LimitReached(member_id)
        if copy.status is CopyStatus.ON_LOAN:
            raise NotAvailable(barcode)
        if copy.status is CopyStatus.ON_HOLD_SHELF:
            if copy.held_for != member_id:
                raise ReservedForAnother(barcode)
            queue = self._holds[copy.isbn]
            if member_id in queue:
                queue.remove(member_id)
        due = today + timedelta(days=member.tier.days)
        copy.status, copy.held_for = CopyStatus.ON_LOAN, None
        self._loans[barcode] = Loan(barcode, member_id, due)
        return due

    def return_copy(self, barcode, today) -> Decimal:
        loan = self._loans.pop(barcode, None)
        if loan is None:
            raise UnknownItem(barcode)
        fine = loan.fine(today)
        self._members[loan.member_id].balance += fine
        copy = self._copies[barcode]
        queue = self._holds[copy.isbn]
        if queue:
            copy.status, copy.held_for = CopyStatus.ON_HOLD_SHELF, queue.popleft()
        else:
            copy.status, copy.held_for = CopyStatus.AVAILABLE, None
        return fine

    def place_hold(self, member_id, isbn) -> None:
        self._member(member_id)
        if isbn not in self._titles:
            raise UnknownItem(isbn)
        queue = self._holds[isbn]
        on_loan = any(self._copies[l.barcode].isbn == isbn for l in self._active(member_id))
        shelf = any(c.isbn == isbn and c.held_for == member_id for c in self._copies.values())
        if member_id in queue or on_loan or shelf:
            raise AlreadyHeld(member_id)
        queue.append(member_id)

    def pay(self, member_id, amount: Decimal) -> Decimal:
        member = self._member(member_id)
        member.balance = max(Decimal("0"), member.balance - amount)
        return member.balance

    def loans(self, member_id):
        return sorted((l.barcode, l.due) for l in self._active(member_id))

    def overdue(self, today):
        return sorted((l.member_id, l.barcode, (today - l.due).days) for l in self._loans.values() if today > l.due)

    def available(self, isbn) -> int:
        return sum(1 for c in self._copies.values() if c.isbn == isbn and c.status is CopyStatus.AVAILABLE)

    def balance(self, member_id) -> Decimal:
        return self._member(member_id).balance
```

- **The aggregate root owns the invariants**: copy status, loans, holds and balances change only through `Library` methods, so "a copy is on loan if and only if a loan exists" and "the hold shelf belongs to the first queued member" always hold.
- **Enums with data** (`Tier` carries its limit and loan days) put each policy in one place, and new tiers are one line.
- **Domain exceptions** carry meaning (`ReservedForAnother` versus `NotAvailable`). A CLI or web layer maps them to messages, and the domain knows nothing about the interface.
- **Decimal money and injected dates** make fines exact (0.25 × 9 days = 2.25, capped at 10.00) and scenarios reproducible. Years of library time run in milliseconds.
- **FIFO holds** with `deque` model fairness explicitly. A returned copy is reserved for exactly one member until they collect it.
