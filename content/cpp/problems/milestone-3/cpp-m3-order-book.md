---
id: cpp-m3-order-book
title: A Price-Time Priority Matching Engine
difficulty: Expert
order: 1
tags: std::map, std::list, iterators, hashing, data-structure design, performance
time_limit: 4
---
## Statement
Implement the core of an exchange: a **limit order book** with price-time priority matching. The same design is used by trading venues and by auction-based multi-robot task markets. The hidden test replays one million operations.

```cpp
enum class Side { Buy, Sell };
struct Trade { std::uint64_t buy_id, sell_id; std::int64_t price, qty; };
```

**`class OrderBook`**
- **`std::vector<Trade> limit(id, side, price, qty)`**: match against the opposite side while prices cross (a buy matches asks `<= price`, a sell matches bids `>= price`). Best price first, and within a price, **oldest first**. Each fill trades at the **resting** order's price. Any remainder **rests** in the book. A duplicate live id or `qty <= 0` throws `std::invalid_argument`.
- **`std::vector<Trade> market(id, side, qty)`**: matches as much as possible, and the remainder is discarded (never rests). `qty <= 0` throws.
- **`bool cancel(id)`**: false if the id isn't resting.
- **`bool modify(id, new_qty)`**: reducing keeps time priority, **increasing loses it** (the order moves to the back of its price level), and `new_qty <= 0` cancels. False if unknown.
- `std::optional<std::int64_t> best_bid() const` and `best_ask() const`, `std::int64_t volume_at(Side, price) const`, `std::size_t order_count() const`.

Fully filled orders are removed. Ids of removed orders may be reused.

## Starter
```cpp
#include <cstdint>
#include <optional>
#include <stdexcept>
#include <vector>

enum class Side { Buy, Sell };
struct Trade { std::uint64_t buy_id, sell_id; std::int64_t price, qty; };

class OrderBook {
public:
    std::vector<Trade> limit(std::uint64_t id, Side s, std::int64_t price, std::int64_t qty) {
        orders_.push_back({id, s, price, qty});
        return {};
    }
    std::vector<Trade> market(std::uint64_t, Side, std::int64_t) { return {}; }
    bool cancel(std::uint64_t) { return false; }
    bool modify(std::uint64_t, std::int64_t) { return false; }
    std::optional<std::int64_t> best_bid() const { return std::nullopt; }
    std::optional<std::int64_t> best_ask() const { return std::nullopt; }
    std::int64_t volume_at(Side, std::int64_t) const { return 0; }
    std::size_t order_count() const { return orders_.size(); }
private:
    struct O { std::uint64_t id; Side s; std::int64_t p, q; };
    std::vector<O> orders_;
};
```

## Driver
```cpp
#include <cstdio>
#include <iostream>
#include <string>

static void show(const char* label, const std::vector<Trade>& ts) {
    std::printf("%s:", label);
    for (auto& t : ts) std::printf(" [%llu<-%llu %lld@%lld]", (unsigned long long)t.buy_id, (unsigned long long)t.sell_id, (long long)t.qty, (long long)t.price);
    std::printf("\n");
}
static void top(const OrderBook& b) {
    auto bb = b.best_bid(), ba = b.best_ask();
    std::printf("  bid %s ask %s orders %zu\n", bb ? std::to_string(*bb).c_str() : "-", ba ? std::to_string(*ba).c_str() : "-", b.order_count());
}

int main() {
    std::string cmd;
    while (std::cin >> cmd) {
        OrderBook b;
        if (cmd == "basic") {
            show("s1", b.limit(1, Side::Sell, 101, 5)); show("s2", b.limit(2, Side::Sell, 102, 5)); show("s3", b.limit(3, Side::Sell, 101, 3));
            show("b4", b.limit(4, Side::Buy, 99, 10)); top(b);
            show("b5 crosses", b.limit(5, Side::Buy, 102, 10)); top(b);
            std::printf("  vol buy99 %lld buy102 %lld sell102 %lld\n", (long long)b.volume_at(Side::Buy, 99), (long long)b.volume_at(Side::Buy, 102), (long long)b.volume_at(Side::Sell, 102));
            show("m6 sell market", b.market(6, Side::Sell, 4)); top(b);
            show("m7 sell market big", b.market(7, Side::Sell, 100)); top(b);
            try { b.limit(8, Side::Buy, 100, 0); } catch (const std::invalid_argument&) { std::printf("  zero qty rejected\n"); }
            b.limit(9, Side::Buy, 100, 1);
            try { b.limit(9, Side::Buy, 100, 1); } catch (const std::invalid_argument&) { std::printf("  duplicate id rejected\n"); }
        } else if (cmd == "priority") {
            b.limit(1, Side::Buy, 100, 5); b.limit(2, Side::Buy, 100, 5); b.limit(3, Side::Buy, 100, 5);
            bool m1 = b.modify(1, 3), m2 = b.modify(2, 8), m9 = b.modify(9, 1);
            std::printf("modify 1 down %d, modify 2 up %d, modify 9 %d\n", m1, m2, m9);
            show("sell 10", b.limit(10, Side::Sell, 100, 10)); top(b);
            bool c1 = b.cancel(2), c2 = b.cancel(2);
            std::printf("cancel 2 %d again %d\n", c1, c2); top(b);
            b.limit(4, Side::Buy, 100, 2); bool m0 = b.modify(4, 0); std::printf("modify to 0 cancels %d\n", m0); top(b);
            show("sell into empty", b.market(11, Side::Sell, 5));
            b.limit(1, Side::Sell, 105, 2); top(b);
        } else if (cmd == "replay") {
            unsigned long long x = 99, trades = 0, volume = 0, notional = 0;
            std::uint64_t next = 1;
            std::vector<std::uint64_t> live;
            for (int i = 0; i < 1000000; ++i) {
                x = x * 6364136223846793005ULL + 1442695040888963407ULL;
                unsigned op = (x >> 33) % 100;
                Side s = (x >> 20) & 1 ? Side::Buy : Side::Sell;
                std::int64_t px = 1000 + (std::int64_t)((x >> 40) % 41) - 20 + (s == Side::Buy ? -3 : 3);
                std::int64_t q = 1 + (std::int64_t)((x >> 50) % 50);
                std::vector<Trade> ts;
                if (op < 70) { ts = b.limit(next, s, px, q); live.push_back(next++); }
                else if (op < 80) ts = b.market(next++, s, q);
                else if (op < 93 && !live.empty()) { size_t k = (x >> 8) % live.size(); b.cancel(live[k]); live[k] = live.back(); live.pop_back(); }
                else if (!live.empty()) b.modify(live[(x >> 8) % live.size()], q);
                for (auto& t : ts) { trades++; volume += t.qty; notional += (unsigned long long)(t.qty * t.price); }
            }
            std::printf("trades %llu volume %llu notional %llu orders %zu bid %lld ask %lld\n", trades, volume, notional, b.order_count(),
                        (long long)b.best_bid().value_or(-1), (long long)b.best_ask().value_or(-1));
        }
    }
}
```

## Tests
=== sample
basic
---
s1:
s2:
s3:
b4:
  bid 99 ask 101 orders 4
b5 crosses: [5<-1 5@101] [5<-3 3@101] [5<-2 2@102]
  bid 99 ask 102 orders 2
  vol buy99 10 buy102 0 sell102 3
m6 sell market: [4<-6 4@99]
  bid 99 ask 102 orders 2
m7 sell market big: [4<-7 6@99]
  bid - ask 102 orders 1
  zero qty rejected
  duplicate id rejected
=== hidden
priority
---
modify 1 down 1, modify 2 up 1, modify 9 0
sell 10: [1<-10 3@100] [3<-10 5@100] [2<-10 2@100]
  bid 100 ask - orders 1
cancel 2 1 again 0
  bid - ask - orders 0
modify to 0 cancels 1
  bid - ask - orders 0
sell into empty:
  bid - ask 105 orders 1
=== hidden
replay
---
trades 617899 volume 8042448 notional 8042336751 orders 137667 bid 995 ask 998

## Hints
- Use `std::map<int64_t, std::list<Order>>` for each side (bids iterated from the highest, asks from the lowest), plus `std::unordered_map<uint64_t, Locator>`, where the locator stores the side, price and `std::list<Order>::iterator`. `std::list` iterators stay valid while other orders come and go.
- Matching loop: take the best level, fill against its front order while the price crosses and quantity remains, pop fully filled orders, and erase empty levels.
- `modify` upward: `splice` the node to the end of its level's list. That's O(1) and keeps the iterator valid.
- Keep a running count of live orders (or use the size of the id map) for `order_count`.

## Solution
```cpp
#include <cstdint>
#include <functional>
#include <list>
#include <map>
#include <optional>
#include <stdexcept>
#include <unordered_map>
#include <vector>

enum class Side { Buy, Sell };
struct Trade { std::uint64_t buy_id, sell_id; std::int64_t price, qty; };

class OrderBook {
    struct Order { std::uint64_t id; std::int64_t qty; };
    using Level = std::list<Order>;
    struct Locator { Side side; std::int64_t price; Level::iterator it; };

public:
    std::vector<Trade> limit(std::uint64_t id, Side side, std::int64_t price, std::int64_t qty) {
        if (qty <= 0) throw std::invalid_argument("qty must be positive");
        if (index_.count(id)) throw std::invalid_argument("duplicate order id");
        std::vector<Trade> out;
        qty = match(id, side, qty, price, out);
        if (qty > 0) {
            Level& lvl = side == Side::Buy ? bids_[price] : asks_[price];
            lvl.push_back({id, qty});
            index_.emplace(id, Locator{side, price, std::prev(lvl.end())});
        }
        return out;
    }

    std::vector<Trade> market(std::uint64_t id, Side side, std::int64_t qty) {
        if (qty <= 0) throw std::invalid_argument("qty must be positive");
        std::vector<Trade> out;
        match(id, side, qty, std::nullopt, out);
        return out;
    }

    bool cancel(std::uint64_t id) {
        auto f = index_.find(id);
        if (f == index_.end()) return false;
        erase(f);
        return true;
    }

    bool modify(std::uint64_t id, std::int64_t new_qty) {
        auto f = index_.find(id);
        if (f == index_.end()) return false;
        if (new_qty <= 0) { erase(f); return true; }
        Locator& loc = f->second;
        Level& lvl = level(loc.side, loc.price);
        if (new_qty > loc.it->qty) lvl.splice(lvl.end(), lvl, loc.it);   // increase: lose time priority
        loc.it->qty = new_qty;
        return true;
    }

    std::optional<std::int64_t> best_bid() const { return bids_.empty() ? std::nullopt : std::optional(bids_.rbegin()->first); }
    std::optional<std::int64_t> best_ask() const { return asks_.empty() ? std::nullopt : std::optional(asks_.begin()->first); }

    std::int64_t volume_at(Side side, std::int64_t price) const {
        const auto& book = side == Side::Buy ? bids_ : asks_;
        auto it = book.find(price);
        std::int64_t v = 0;
        if (it != book.end()) for (const auto& o : it->second) v += o.qty;
        return v;
    }

    std::size_t order_count() const { return index_.size(); }

private:
    Level& level(Side s, std::int64_t p) { return s == Side::Buy ? bids_.at(p) : asks_.at(p); }

    void erase(std::unordered_map<std::uint64_t, Locator>::iterator f) {
        auto& book = f->second.side == Side::Buy ? bids_ : asks_;
        auto lvl = book.find(f->second.price);
        lvl->second.erase(f->second.it);
        if (lvl->second.empty()) book.erase(lvl);
        index_.erase(f);
    }

    std::int64_t match(std::uint64_t id, Side side, std::int64_t qty, std::optional<std::int64_t> limit, std::vector<Trade>& out) {
        auto& book = side == Side::Buy ? asks_ : bids_;
        while (qty > 0 && !book.empty()) {
            auto lvl = side == Side::Buy ? book.begin() : std::prev(book.end());          // best opposite price
            std::int64_t px = lvl->first;
            if (limit && (side == Side::Buy ? px > *limit : px < *limit)) break;          // no longer crosses
            Level& orders = lvl->second;
            while (qty > 0 && !orders.empty()) {
                Order& rest = orders.front();
                std::int64_t fill = std::min(qty, rest.qty);
                out.push_back(side == Side::Buy ? Trade{id, rest.id, px, fill} : Trade{rest.id, id, px, fill});
                qty -= fill;
                rest.qty -= fill;
                if (rest.qty == 0) { index_.erase(rest.id); orders.pop_front(); }
            }
            if (orders.empty()) book.erase(lvl);
        }
        return qty;
    }

    std::map<std::int64_t, Level> bids_, asks_;          // price levels, each FIFO by time
    std::unordered_map<std::uint64_t, Locator> index_;    // id -> exact node, for O(1) cancel/modify
};
```

- **Price-time priority** falls out of the data structure: a `std::map` orders price levels, and each level's `std::list` keeps arrival order. Matching repeatedly takes the best level's front order.
- **O(1) cancel and modify** through stored `std::list` iterators. List nodes never move, so iterators stay valid as other orders come and go, which a `std::vector` level couldn't guarantee.
- **`splice` for priority loss**: moving a node to the back of its level is constant time and keeps its iterator valid. It's the exchange rule "size up = re-queue".
- **The resting order sets the price**: an aggressive buy at 102 against asks at 101 trades at 101, giving price improvement to the aggressor, as on real venues.
- With a million mixed operations, the book does O(log P) work per new price level and amortised O(1) per fill, cancel or modify.
