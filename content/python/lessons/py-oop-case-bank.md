# Case Study: Banking System

Banking is the domain where correctness matters most: money must never be created or destroyed by a bug, every change must be auditable, and retries must not double-charge. This case study designs a small banking core with **accounts**, an **append-only ledger**, **atomic transfers**, **idempotency keys**, account types with different rules (overdraft, interest), and invariants you can check at any time.

## 1. Requirements

- Account types:
  - **Checking**: an overdraft limit, so the balance may go down to `-overdraft`.
  - **Savings**: the balance can't go below 0, with a maximum of 6 withdrawals per month and monthly interest.
- Operations: deposit, withdraw, transfer between accounts, monthly interest posting, and a statement for a period.
- **Every movement is a ledger entry** (immutable). Balances are derived from the ledger, or cached and verifiable against it.
- **Transfers are atomic**: both legs or neither.
- **Idempotency**: a request carrying an id that was already processed returns the original result instead of executing again. This protects against network retries.

## 2. The ledger as the source of truth

```python
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

class Kind(Enum):
    DEPOSIT = "deposit"; WITHDRAWAL = "withdrawal"; TRANSFER_IN = "transfer_in"
    TRANSFER_OUT = "transfer_out"; INTEREST = "interest"

@dataclass(frozen=True)
class Entry:
    seq: int
    account: str
    kind: Kind
    amount: Decimal          # signed: + credit, - debit
    day: int
    ref: str                 # links the two legs of a transfer
```

Accountants have used **double-entry bookkeeping** since the 15th century: every transfer writes two entries that sum to zero. The global invariant is that the **sum of all entries equals deposits minus withdrawals plus interest**, and each account's balance is the sum of its entries. A `check_invariants()` method recomputes these and asserts. Run it in tests after every scenario.

## 3. Polymorphic rules

```python
class Account:
    def __init__(self, number: str): self.number, self.balance = number, Decimal("0")
    def can_withdraw(self, amount: Decimal, day: int) -> bool:
        raise NotImplementedError
    def after_withdraw(self, day: int) -> None:
        pass

class Checking(Account):
    def __init__(self, number, overdraft: Decimal):
        super().__init__(number); self.overdraft = overdraft
    def can_withdraw(self, amount, day): return self.balance - amount >= -self.overdraft

class Savings(Account):
    MAX_MONTHLY = 6
    def __init__(self, number, rate: Decimal):
        super().__init__(number); self.rate = rate; self._month_withdrawals = {}
    def can_withdraw(self, amount, day):
        month = day // 30
        return self.balance >= amount and self._month_withdrawals.get(month, 0) < self.MAX_MONTHLY
    def after_withdraw(self, day):
        m = day // 30
        self._month_withdrawals[m] = self._month_withdrawals.get(m, 0) + 1
```

The `Bank` (aggregate root) asks `can_withdraw` (polymorphism replaces type checks) and then records entries. Interest uses `Decimal.quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)` (banker's rounding) and is posted as a ledger entry.

## 4. Atomic transfers and idempotency

```python
def transfer(self, request_id: str, src: str, dst: str, amount: Decimal, day: int) -> Receipt:
    if request_id in self._processed:
        return self._processed[request_id]        # retry-safe: same answer, no double charge
    a, b = self._get(src), self._get(dst)          # validate everything first...
    if amount <= 0 or a is b:
        raise InvalidRequest()
    if not a.can_withdraw(amount, day):
        raise InsufficientFunds(src)
    ref = f"T{next(self._refs)}"                   # ...then commit both legs together
    self._post(a, Kind.TRANSFER_OUT, -amount, day, ref)
    self._post(b, Kind.TRANSFER_IN, amount, day, ref)
    a.after_withdraw(day)
    receipt = Receipt(ref, src, dst, amount)
    self._processed[request_id] = receipt
    return receipt
```

**Validate, then commit** gives atomicity in memory. A database would wrap both inserts in one transaction. Failed requests are recorded too, so a retry gets the same error. Pay attention to whether a failure should be cached: for business rejections, yes. For transient faults, no.

> [!EXAM]
> **Why do banking systems use an append-only ledger and idempotency keys?**
> An append-only ledger records every money movement as an immutable entry. Balances are derived from it (or verified against it), there's a complete audit trail, and errors are corrected with compensating entries rather than by rewriting history. Double-entry transfers make each transfer's legs sum to zero, so invariants like "total money is conserved" can be checked at any time. Idempotency keys handle the reality of networks: a client that times out and retries a transfer must not move the money twice. The bank stores each request id with its outcome and returns the stored result for duplicates.

## Worked example: balance as a fold over the ledger

The key decision in this case study is that **balances are never stored**. They are computed from an append-only list of entries. A minimal version:

```python
from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True)
class Entry:
    account: str
    amount: Decimal        # +credit / -debit
    txn_id: str

class Ledger:
    def __init__(self):
        self.entries: list[Entry] = []
        self.seen: set[str] = set()

    def balance(self, account: str) -> Decimal:
        return sum((e.amount for e in self.entries if e.account == account), Decimal("0"))

    def transfer(self, txn_id: str, src: str, dst: str, amount: Decimal) -> str:
        if txn_id in self.seen:              # idempotency: a retried request does nothing twice
            return "DUPLICATE"
        if amount <= 0 or self.balance(src) < amount:
            return "REJECTED"
        # both legs together, or neither: a transfer always sums to zero
        self.entries += [Entry(src, -amount, txn_id), Entry(dst, amount, txn_id)]
        self.seen.add(txn_id)
        return "OK"

L = Ledger()
L.entries.append(Entry("alice", Decimal("100"), "seed"))
print(L.transfer("t1", "alice", "bob", Decimal("30")))
print(L.transfer("t1", "alice", "bob", Decimal("30")))   # network retry
print(L.balance("alice"), L.balance("bob"))
```

```output
OK
DUPLICATE
70 30
```

- **Why a ledger?** You get the history for free and the books always balance. A bug can't silently "create" money, because every transfer has two equal and opposite entries.
- **Why idempotency keys?** Mobile networks retry requests. Without the `seen` set, a retry would move the money twice.

## Common mistakes

- **Using `float` for money.** `0.1 + 0.2 != 0.3`. Use `Decimal` or integer minor units.
- **Updating two stored balances one after the other.** A crash between the two updates loses money. Write both legs in one transaction.
- **Checking the balance and then writing without a lock**, when transfers can run concurrently.

## Check your understanding

1. How would an overdraft limit fit into the polymorphic rules section?
2. Why is `Entry` frozen?

<details><summary>Answers</summary>

1. As an account-type policy: `can_withdraw(balance, amount)` returns `balance - amount >= -limit` for overdraft accounts and `>= 0` for savings accounts.
2. History must never change. Corrections are new reversing entries, which keeps an audit trail.

</details>
