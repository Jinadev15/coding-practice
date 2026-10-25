---
id: py-banking-ledger
title: "Case Study: A Ledger-Based Banking Core"
difficulty: Expert
order: 1
tags: case study, polymorphism, append-only ledger, double entry, idempotency, Decimal, invariants
time_limit: 5
---
## Statement
Implement the banking core from the case-study lesson. Every money movement is an **immutable ledger entry**, transfers are **double-entry and atomic**, and retried transfer requests are **idempotent**.

**Exceptions** (subclasses of `BankError`): `UnknownAccount`, `InvalidRequest`, `InsufficientFunds`, `WithdrawalLimit`.

**Entries**: `Entry(seq, account, kind, amount, day, ref)` is a frozen dataclass. `seq` starts at 1 globally, `amount` is a **signed** `Decimal`, and `kind` is one of `"deposit"`, `"withdrawal"`, `"transfer_in"`, `"transfer_out"`, `"interest"`. All amounts are quantized to 0.01.

**Account types**
- **Checking(overdraft)**: a withdrawal is allowed if `balance − amount ≥ −overdraft`.
- **Savings(monthly_rate)**: needs `balance ≥ amount` (else `InsufficientFunds`), and allows at most **6 withdrawals per month** (month = `day // 30`; else `WithdrawalLimit`). Transfers out count as withdrawals.

**`Bank`**

| Method | Contract |
|---|---|
| `open_checking(number, overdraft=Decimal("0"))`, `open_savings(number, monthly_rate)` | A duplicate number raises `InvalidRequest`. |
| `deposit(number, amount, day) -> Decimal` | Returns the new balance. Requires `amount > 0`. |
| `withdraw(number, amount, day) -> Decimal` | |
| `transfer(request_id, src, dst, amount, day) -> Receipt` | `Receipt(ref, src, dst, amount)`, where ref is `"T1"`, `"T2"`, …. It writes `transfer_out` (−) and `transfer_in` (+) entries sharing the ref. The same account on both sides, or a non-positive amount, raises `InvalidRequest`. **A repeated `request_id` returns the original receipt, or re-raises the original exception, without executing again.** |
| `post_interest(day) -> Decimal` | For each savings account (in account-number order) with a positive balance, posts `(balance × rate)` quantized half-even to 0.01, if > 0. Returns the total. |
| `statement(number, from_day, to_day)` | `[(seq, kind, amount, running_balance)]` for that account's entries within the inclusive day range. The running balance counts **all** earlier entries. |
| `balance(number)`, `check_invariants() -> bool` | Invariants: each balance equals the sum of its entries, every transfer ref sums to zero, and the sum of all balances equals deposits − withdrawals + interest. |

Unknown accounts raise `UnknownAccount` everywhere. Validation happens **before** any entry is written.

## Starter
```python
from dataclasses import dataclass
from decimal import Decimal


class BankError(Exception): pass
class UnknownAccount(BankError): pass
class InvalidRequest(BankError): pass
class InsufficientFunds(BankError): pass
class WithdrawalLimit(BankError): pass


@dataclass
class Receipt:
    ref: str
    src: str
    dst: str
    amount: Decimal


class Bank:
    def __init__(self):
        self.balances = {}

    def open_checking(self, number, overdraft=Decimal("0")): self.balances[number] = Decimal(0)
    def open_savings(self, number, monthly_rate): self.balances[number] = Decimal(0)
    def deposit(self, number, amount, day):
        self.balances[number] += amount
        return self.balances[number]
    def withdraw(self, number, amount, day):
        self.balances[number] -= amount
        return self.balances[number]
    def transfer(self, request_id, src, dst, amount, day):
        self.balances[src] -= amount
        self.balances[dst] += amount
        return Receipt("T1", src, dst, amount)
    def balance(self, number): return self.balances[number]
    def check_invariants(self): return True
```

## Driver
```python
import sys
from decimal import Decimal as D

def attempt(label, fn):
    try:
        print(f"{label}: {fn()}")
    except BankError as e:
        print(f"{label}: {type(e).__name__}")

for cmd in sys.stdin.read().split():
    b = Bank()
    b.open_checking("CHK-1", overdraft=D("100")); b.open_savings("SAV-1", D("0.01")); b.open_checking("CHK-2")
    if cmd == "basic":
        attempt("dup", lambda: b.open_savings("CHK-1", D("0.02")))
        attempt("deposit", lambda: b.deposit("CHK-1", D("250.005"), 1))
        attempt("deposit 0", lambda: b.deposit("CHK-1", D("0"), 1))
        attempt("unknown", lambda: b.deposit("NOPE", D("5"), 1))
        attempt("overdraft ok", lambda: b.withdraw("CHK-1", D("320"), 2))
        attempt("overdraft too far", lambda: b.withdraw("CHK-1", D("40"), 2))
        attempt("savings empty", lambda: b.withdraw("SAV-1", D("1"), 2))
        attempt("transfer", lambda: b.transfer("req-1", "CHK-1", "SAV-1", D("30"), 3))
        attempt("transfer no funds", lambda: b.transfer("req-2", "CHK-2", "SAV-1", D("10"), 3))
        attempt("retry req-1", lambda: b.transfer("req-1", "CHK-1", "SAV-1", D("30"), 4))
        attempt("retry req-2", lambda: b.transfer("req-2", "CHK-2", "SAV-1", D("10"), 4))
        attempt("self transfer", lambda: b.transfer("req-3", "SAV-1", "SAV-1", D("1"), 4))
        print("balances", b.balance("CHK-1"), b.balance("SAV-1"), b.balance("CHK-2"))
        attempt("deposit savings", lambda: b.deposit("SAV-1", D("1000"), 5))
        attempt("interest", lambda: b.post_interest(30))
        for row in b.statement("SAV-1", 0, 100): print(" ", row)
        print("invariants", b.check_invariants())
    elif cmd == "limits":
        b.deposit("SAV-1", D("100"), 0)
        for i in range(7):
            attempt(f"w{i}", lambda: b.withdraw("SAV-1", D("1"), 5 + i))
        attempt("transfer counts", lambda: b.transfer("t", "SAV-1", "CHK-2", D("1"), 20))
        attempt("next month", lambda: b.withdraw("SAV-1", D("1"), 31))
        attempt("transfer next month", lambda: b.transfer("t2", "SAV-1", "CHK-2", D("2.50"), 32))
        print("stmt CHK-2", b.statement("CHK-2", 0, 60))
        print("stmt SAV-1 days 30-40", b.statement("SAV-1", 30, 40))
        print("invariants", b.check_invariants())
    elif cmd == "load":
        accts = ["CHK-1", "SAV-1", "CHK-2"]
        for i in range(20):
            b.open_savings(f"S{i:02d}", D("0.005")); b.open_checking(f"C{i:02d}", D("50")); accts += [f"S{i:02d}", f"C{i:02d}"]
        x = 3; errors = {}
        for day in range(360):
            for k in range(30):
                x = (x * 1103515245 + 12345) % (1 << 31)
                a, c = accts[x % len(accts)], accts[(x >> 8) % len(accts)]
                amt = D(x % 50000) / 100 + D("0.01")
                try:
                    op = (x >> 16) % 4
                    if op == 0: b.deposit(a, amt, day)
                    elif op == 1: b.withdraw(a, amt / 4, day)
                    else: b.transfer(f"r{(x >> 3) % 9000}", a, c, amt / 3, day)
                except BankError as e:
                    errors[type(e).__name__] = errors.get(type(e).__name__, 0) + 1
            if day % 30 == 29:
                b.post_interest(day)
        total = sum(b.balance(a) for a in accts)
        print("total", total, "errors", dict(sorted(errors.items())), "invariants", b.check_invariants())
```

## Tests
=== sample
basic
---
dup: InvalidRequest
deposit: 250.00
deposit 0: InvalidRequest
unknown: UnknownAccount
overdraft ok: -70.00
overdraft too far: InsufficientFunds
savings empty: InsufficientFunds
transfer: Receipt(ref='T1', src='CHK-1', dst='SAV-1', amount=Decimal('30.00'))
transfer no funds: InsufficientFunds
retry req-1: Receipt(ref='T1', src='CHK-1', dst='SAV-1', amount=Decimal('30.00'))
retry req-2: InsufficientFunds
self transfer: InvalidRequest
balances -100.00 30.00 0.00
deposit savings: 1030.00
interest: 10.30
  (4, 'transfer_in', Decimal('30.00'), Decimal('30.00'))
  (5, 'deposit', Decimal('1000.00'), Decimal('1030.00'))
  (6, 'interest', Decimal('10.30'), Decimal('1040.30'))
invariants True
=== hidden
limits
---
w0: 99.00
w1: 98.00
w2: 97.00
w3: 96.00
w4: 95.00
w5: 94.00
w6: WithdrawalLimit
transfer counts: WithdrawalLimit
next month: 93.00
transfer next month: Receipt(ref='T1', src='SAV-1', dst='CHK-2', amount=Decimal('2.50'))
stmt CHK-2 [(10, 'transfer_in', Decimal('2.50'), Decimal('2.50'))]
stmt SAV-1 days 30-40 [(8, 'withdrawal', Decimal('-1.00'), Decimal('93.00')), (9, 'transfer_out', Decimal('-2.50'), Decimal('90.50'))]
invariants True
=== hidden
load
---
total 580559.39 errors {'InsufficientFunds': 164, 'InvalidRequest': 129, 'WithdrawalLimit': 2021} invariants True

## Hints
- Use one `_post(account, kind, amount, day, ref)` method that appends an `Entry` to `self._ledger` and updates a cached balance. Nothing else may change balances.
- Polymorphism replaces type checks: an `Account` base class with `check_withdraw(amount, day)` (raising the right exception) and `record_withdraw(day)`, overridden by `Checking` and `Savings`.
- Idempotency: `self._requests[request_id]` stores either the `Receipt` or the exception instance. On a repeat, return the receipt or `raise` the stored exception.
- Validate everything (accounts, amount, `check_withdraw`) before writing either leg. Then both entries are written together.

## Solution
```python
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_EVEN
from itertools import count

CENT = Decimal("0.01")


class BankError(Exception): pass
class UnknownAccount(BankError): pass
class InvalidRequest(BankError): pass
class InsufficientFunds(BankError): pass
class WithdrawalLimit(BankError): pass


@dataclass(frozen=True)
class Entry:
    seq: int
    account: str
    kind: str
    amount: Decimal
    day: int
    ref: str


@dataclass(frozen=True)
class Receipt:
    ref: str
    src: str
    dst: str
    amount: Decimal


def money(x) -> Decimal:
    return Decimal(x).quantize(CENT, rounding=ROUND_HALF_EVEN)


class Account:
    def __init__(self, number: str):
        self.number = number
        self.balance = Decimal("0.00")

    def check_withdraw(self, amount: Decimal, day: int) -> None:
        raise NotImplementedError

    def record_withdraw(self, day: int) -> None:
        pass


class Checking(Account):
    def __init__(self, number, overdraft: Decimal):
        super().__init__(number)
        self.overdraft = money(overdraft)

    def check_withdraw(self, amount, day):
        if self.balance - amount < -self.overdraft:
            raise InsufficientFunds(self.number)


class Savings(Account):
    MAX_PER_MONTH = 6

    def __init__(self, number, monthly_rate: Decimal):
        super().__init__(number)
        self.rate = Decimal(monthly_rate)
        self._withdrawals: dict[int, int] = {}

    def check_withdraw(self, amount, day):
        if self.balance < amount:
            raise InsufficientFunds(self.number)
        if self._withdrawals.get(day // 30, 0) >= self.MAX_PER_MONTH:
            raise WithdrawalLimit(self.number)

    def record_withdraw(self, day):
        m = day // 30
        self._withdrawals[m] = self._withdrawals.get(m, 0) + 1


class Bank:
    def __init__(self):
        self._accounts: dict[str, Account] = {}
        self._ledger: list[Entry] = []
        self._seq = count(1)
        self._refs = count(1)
        self._requests: dict[str, Receipt | BankError] = {}

    def _open(self, acct: Account):
        if acct.number in self._accounts:
            raise InvalidRequest(f"duplicate account {acct.number}")
        self._accounts[acct.number] = acct

    def open_checking(self, number, overdraft=Decimal("0")):
        self._open(Checking(number, overdraft))

    def open_savings(self, number, monthly_rate):
        self._open(Savings(number, monthly_rate))

    def _get(self, number) -> Account:
        try:
            return self._accounts[number]
        except KeyError:
            raise UnknownAccount(number) from None

    def _post(self, acct: Account, kind: str, amount: Decimal, day: int, ref: str = "") -> None:
        self._ledger.append(Entry(next(self._seq), acct.number, kind, amount, day, ref))
        acct.balance += amount                          # the only place balances change

    @staticmethod
    def _positive(amount) -> Decimal:
        amt = money(amount)
        if amt <= 0:
            raise InvalidRequest("amount must be positive")
        return amt

    def deposit(self, number, amount, day) -> Decimal:
        acct, amt = self._get(number), self._positive(amount)
        self._post(acct, "deposit", amt, day)
        return acct.balance

    def withdraw(self, number, amount, day) -> Decimal:
        acct, amt = self._get(number), self._positive(amount)
        acct.check_withdraw(amt, day)                   # polymorphic rule
        self._post(acct, "withdrawal", -amt, day)
        acct.record_withdraw(day)
        return acct.balance

    def transfer(self, request_id, src, dst, amount, day) -> Receipt:
        if request_id in self._requests:                # idempotent replay
            prior = self._requests[request_id]
            if isinstance(prior, BankError):
                raise prior
            return prior
        try:
            a, b, amt = self._get(src), self._get(dst), self._positive(amount)
            if a is b:
                raise InvalidRequest("same account")
            a.check_withdraw(amt, day)
        except BankError as e:
            self._requests[request_id] = e
            raise
        ref = f"T{next(self._refs)}"
        self._post(a, "transfer_out", -amt, day, ref)   # both legs written together
        self._post(b, "transfer_in", amt, day, ref)
        a.record_withdraw(day)
        receipt = Receipt(ref, src, dst, amt)
        self._requests[request_id] = receipt
        return receipt

    def post_interest(self, day) -> Decimal:
        total = Decimal("0.00")
        for number in sorted(self._accounts):
            acct = self._accounts[number]
            if isinstance(acct, Savings) and acct.balance > 0:
                interest = money(acct.balance * acct.rate)
                if interest > 0:
                    self._post(acct, "interest", interest, day)
                    total += interest
        return total

    def statement(self, number, from_day, to_day):
        self._get(number)
        running, rows = Decimal("0.00"), []
        for e in self._ledger:
            if e.account != number:
                continue
            running += e.amount
            if from_day <= e.day <= to_day:
                rows.append((e.seq, e.kind, e.amount, running))
        return rows

    def balance(self, number) -> Decimal:
        return self._get(number).balance

    def check_invariants(self) -> bool:
        per_account: dict[str, Decimal] = {n: Decimal("0") for n in self._accounts}
        refs: dict[str, Decimal] = {}
        external = Decimal("0")
        for e in self._ledger:
            per_account[e.account] += e.amount
            if e.ref:
                refs[e.ref] = refs.get(e.ref, Decimal("0")) + e.amount
            else:
                external += e.amount                    # deposits, withdrawals, interest
        return (all(per_account[n] == a.balance for n, a in self._accounts.items())
                and all(v == 0 for v in refs.values())
                and sum(a.balance for a in self._accounts.values()) == external)
```

- **The ledger is the source of truth**: entries are frozen and append-only, and the cached balances are verified against them by `check_invariants()` after 10,000 random operations.
- **Double entry**: every transfer writes two entries with the same ref that sum to zero, so money can't appear or vanish through transfers. The global invariant "Σ balances = deposits − withdrawals + interest" checks exactly that.
- **Polymorphism instead of type switches**: `check_withdraw` encodes each account type's rule (overdraft vs funds plus a monthly withdrawal cap), so the `Bank` never asks "is this savings?" when validating.
- **Validate, then commit**: all checks happen before the first entry is written. A failing transfer leaves no half-transfer behind.
- **Idempotency**: request ids map to their outcome, success or failure, so a client retrying after a timeout gets the same answer and money moves only once.
