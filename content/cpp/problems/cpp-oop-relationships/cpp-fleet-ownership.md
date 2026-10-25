---
id: cpp-fleet-ownership
title: Ownership and Relationships in a Robot Fleet
difficulty: Hard
order: 1
tags: composition, association, unique_ptr, shared_ptr, weak_ptr, lifetimes, reference stability
time_limit: 4
---
## Statement
Model a fleet's object graph with the correct C++ ownership for each relationship:
- **composition**: the fleet owns robots and chargers;
- **association**: a robot is assigned to a charger, without owning it;
- **shared ownership**: robots share immutable map versions.

**Given value type:** `struct MapData { int version; std::string name; };`

**`class Charger`**: `id()`, `slots()`, `used()`. **`class Robot`**: `id()`, `Charger* charger() const` (the current assignment or nullptr), `std::shared_ptr<const MapData> map() const`. Neither is copyable. Only the `Fleet` mutates them.

**`class Fleet`:**

| Member | Contract |
|---|---|
| `Charger& add_charger(std::string id, int slots)` | Throws `std::invalid_argument` for a duplicate id or `slots < 1`. |
| `Robot& add_robot(std::string id)` | Throws for a duplicate id. The new robot holds the **current** map, if one was published. |
| `Robot* robot(std::string_view)`, `Charger* charger(std::string_view)` | nullptr if unknown. |
| `bool assign(robot, charger)` | False if either is unknown, or the charger is full (unless the robot is already there, which is a no-op returning true). Reassigning frees the old slot. |
| `void unassign(robot)` | Frees the slot, if any. |
| `bool remove_robot(id)` | Frees its slot. False if unknown. |
| `bool remove_charger(id)` | **Unassigns every robot at it first**. False if unknown. |
| `std::vector<std::string> robots_at(charger) const` | Sorted ids. Empty if unknown. |
| `std::shared_ptr<const MapData> publish_map(int version, std::string name)` | Becomes the current map, but robots keep their old map until synced. |
| `void sync_maps()` | Every robot switches to the current map. |
| `robot_count()`, `charger_count()` | |

**References returned by `add_*` must stay valid** while thousands more objects are added. **Old map versions must be freed** as soon as no robot holds them: the judge watches them through `weak_ptr`.

## Starter
```cpp
#include <map>
#include <memory>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

struct MapData { int version; std::string name; };

class Charger {
public:
    Charger(std::string id, int slots) : id_(std::move(id)), slots_(slots) {}
    const std::string& id() const { return id_; }
    int slots() const { return slots_; }
    int used() const { return used_; }
    std::string id_; int slots_, used_ = 0;
};

class Robot {
public:
    explicit Robot(std::string id) : id_(std::move(id)) {}
    const std::string& id() const { return id_; }
    Charger* charger() const { return charger_; }
    std::shared_ptr<const MapData> map() const { return map_; }
    std::string id_; Charger* charger_ = nullptr; std::shared_ptr<const MapData> map_;
};

class Fleet {
public:
    Charger& add_charger(std::string id, int slots) { chargers_.emplace_back(id, slots); return chargers_.back(); }
    Robot& add_robot(std::string id) { robots_.emplace_back(id); return robots_.back(); }
    Robot* robot(std::string_view id) { for (auto& r : robots_) if (r.id() == id) return &r; return nullptr; }
    Charger* charger(std::string_view id) { for (auto& c : chargers_) if (c.id() == id) return &c; return nullptr; }
    bool assign(std::string_view r, std::string_view c) { robot(r)->charger_ = charger(c); return true; }
    void unassign(std::string_view r) { robot(r)->charger_ = nullptr; }
    bool remove_robot(std::string_view) { return false; }
    bool remove_charger(std::string_view) { return false; }
    std::vector<std::string> robots_at(std::string_view) const { return {}; }
    std::shared_ptr<const MapData> publish_map(int v, std::string n) { return std::make_shared<MapData>(MapData{v, n}); }
    void sync_maps() {}
    std::size_t robot_count() const { return robots_.size(); }
    std::size_t charger_count() const { return chargers_.size(); }
private:
    std::vector<Robot> robots_;
    std::vector<Charger> chargers_;
};
```

## Driver
```cpp
#include <cstdio>
#include <iostream>

static void show(Fleet& f, const char* c) {
    auto v = f.robots_at(c);
    std::printf("%s [%d/%d]:", c, f.charger(c) ? f.charger(c)->used() : -1, f.charger(c) ? f.charger(c)->slots() : -1);
    for (auto& s : v) std::printf(" %s", s.c_str());
    std::printf("\n");
}

int main() {
    std::string cmd;
    while (std::cin >> cmd) {
        if (cmd == "assign") {
            Fleet f;
            f.add_charger("dock-a", 2); f.add_charger("dock-b", 1);
            for (const char* r : {"r1", "r2", "r3", "r4"}) f.add_robot(r);
            try { f.add_robot("r1"); } catch (const std::invalid_argument&) { std::printf("dup robot rejected\n"); }
            try { f.add_charger("dock-c", 0); } catch (const std::invalid_argument&) { std::printf("zero slots rejected\n"); }
            bool a1 = f.assign("r1", "dock-a"), a2 = f.assign("r2", "dock-a"), a3 = f.assign("r3", "dock-a"), a4 = f.assign("r3", "dock-b");
            bool a5 = f.assign("r9", "dock-a"), a6 = f.assign("r4", "dock-z"), a7 = f.assign("r1", "dock-a");
            std::printf("assign %d %d %d %d unknown %d %d same %d\n", a1, a2, a3, a4, a5, a6, a7);
            show(f, "dock-a"); show(f, "dock-b");
            bool m1 = f.assign("r2", "dock-b"), m2 = f.assign("r3", "dock-a");
            std::printf("move r2->b (full) %d, r3->a %d\n", m1, m2);
            show(f, "dock-a"); show(f, "dock-b");
            f.unassign("r1"); f.unassign("r4");
            std::printf("r1 charger %s\n", f.robot("r1")->charger() ? "set" : "null");
            show(f, "dock-a");
            bool rr = f.remove_robot("r3"), rr2 = f.remove_robot("r3");
            std::printf("remove r3 %d %d robots %zu\n", rr, rr2, f.robot_count());
            show(f, "dock-a"); show(f, "dock-b");
            f.assign("r1", "dock-b"); f.assign("r4", "dock-b");
            show(f, "dock-b");
            bool rc = f.remove_charger("dock-b");
            std::printf("remove dock-b %d, r1 charger %s, chargers %zu, unknown at: %zu\n", rc, f.robot("r1")->charger() ? "dangling!" : "null", f.charger_count(), f.robots_at("dock-b").size());
        } else if (cmd == "stability") {
            Fleet f;
            Robot& first = f.add_robot("first");
            Charger& dock = f.add_charger("dock", 1000000);
            for (int i = 0; i < 20000; ++i) { f.add_robot("bot" + std::to_string(i)); if (i % 2) f.assign("bot" + std::to_string(i), "dock"); }
            f.assign("first", "dock");
            std::printf("first still %s, charger %s used %d robots %zu\n", first.id().c_str(), first.charger() == &dock ? "dock" : "?", dock.used(), f.robot_count());
            for (int i = 0; i < 20000; i += 3) f.remove_robot("bot" + std::to_string(i));
            std::printf("after removals: robots %zu used %d at-dock %zu first %s\n", f.robot_count(), dock.used(), f.robots_at("dock").size(), first.id().c_str());
        } else if (cmd == "maps") {
            Fleet f;
            f.add_robot("early");
            std::weak_ptr<const MapData> v1 = f.publish_map(1, "warehouse");
            std::printf("early robot map: %s\n", f.robot("early")->map() ? "set" : "none");
            f.add_robot("a"); f.add_robot("b");
            std::printf("a has v%d, v1 alive %d (owners: %ld)\n", f.robot("a")->map()->version, !v1.expired(), v1.use_count());
            std::weak_ptr<const MapData> v2 = f.publish_map(2, "warehouse+dock");
            f.add_robot("c");
            std::printf("a v%d, c v%d, v1 alive %d, v2 alive %d\n", f.robot("a")->map()->version, f.robot("c")->map()->version, !v1.expired(), !v2.expired());
            f.sync_maps();
            std::printf("after sync: a v%d early v%d, v1 alive %d\n", f.robot("a")->map()->version, f.robot("early")->map()->version, !v1.expired());
            auto held = f.robot("a")->map();
            f.publish_map(3, "remodel"); f.sync_maps();
            std::printf("v2 kept alive by outside holder: %d (%s)\n", !v2.expired(), held->name.c_str());
            held.reset();
            std::printf("v2 alive after release: %d\n", !v2.expired());
            f.remove_robot("a"); f.remove_robot("b"); f.remove_robot("c"); f.remove_robot("early");
            std::printf("robots %zu\n", f.robot_count());
        }
    }
}
```

## Tests
=== sample
assign
---
dup robot rejected
zero slots rejected
assign 1 1 0 1 unknown 0 0 same 1
dock-a [2/2]: r1 r2
dock-b [1/1]: r3
move r2->b (full) 0, r3->a 0
dock-a [2/2]: r1 r2
dock-b [1/1]: r3
r1 charger null
dock-a [1/2]: r2
remove r3 1 0 robots 3
dock-a [1/2]: r2
dock-b [0/1]:
dock-b [1/1]: r1
remove dock-b 1, r1 charger null, chargers 1, unknown at: 0
=== hidden
stability
---
first still first, charger dock used 10001 robots 20001
after removals: robots 13334 used 6668 at-dock 6668 first first
=== hidden
maps
---
early robot map: none
a has v1, v1 alive 1 (owners: 3)
a v1, c v2, v1 alive 1, v2 alive 1
after sync: a v2 early v2, v1 alive 0
v2 kept alive by outside holder: 1 (warehouse+dock)
v2 alive after release: 0
robots 0

## Hints
- **Composition**: `std::map<std::string, std::unique_ptr<Robot>, std::less<>>`, and the same for chargers. Heap objects never move, so references stay valid, and `std::less<>` allows lookups by `std::string_view`.
- **Association**: `Robot` keeps a raw `Charger*` (non-owning). Track `used_` on the charger. On removal, clear every robot pointing at the charger **before** destroying it.
- Declare the chargers map **before** the robots map, so robots (which observe chargers) are destroyed first.
- **Shared maps**: the fleet holds `std::shared_ptr<const MapData> current_`, each robot holds its own `shared_ptr`, and an old version is freed when its last holder lets go.
- Make `Fleet` a `friend` of `Robot` and `Charger`, so only it can mutate their relationships.

## Solution
```cpp
#include <map>
#include <memory>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

struct MapData { int version; std::string name; };

class Fleet;

class Charger {
public:
    Charger(std::string id, int slots) : id_(std::move(id)), slots_(slots) {}
    Charger(const Charger&) = delete;
    Charger& operator=(const Charger&) = delete;
    const std::string& id() const { return id_; }
    int slots() const { return slots_; }
    int used() const { return used_; }
private:
    friend class Fleet;
    std::string id_;
    int slots_, used_ = 0;
};

class Robot {
public:
    explicit Robot(std::string id) : id_(std::move(id)) {}
    Robot(const Robot&) = delete;
    Robot& operator=(const Robot&) = delete;
    const std::string& id() const { return id_; }
    Charger* charger() const { return charger_; }
    std::shared_ptr<const MapData> map() const { return map_; }
private:
    friend class Fleet;
    std::string id_;
    Charger* charger_ = nullptr;                     // association: non-owning
    std::shared_ptr<const MapData> map_;             // shared, immutable
};

class Fleet {
public:
    Charger& add_charger(std::string id, int slots) {
        if (slots < 1) throw std::invalid_argument("slots must be >= 1");
        auto [it, inserted] = chargers_.try_emplace(id, nullptr);
        if (!inserted) throw std::invalid_argument("duplicate charger " + id);
        it->second = std::make_unique<Charger>(std::move(id), slots);
        return *it->second;
    }

    Robot& add_robot(std::string id) {
        auto [it, inserted] = robots_.try_emplace(id, nullptr);
        if (!inserted) throw std::invalid_argument("duplicate robot " + id);
        it->second = std::make_unique<Robot>(std::move(id));
        it->second->map_ = current_map_;
        return *it->second;
    }

    Robot* robot(std::string_view id) { auto it = robots_.find(id); return it == robots_.end() ? nullptr : it->second.get(); }
    Charger* charger(std::string_view id) { auto it = chargers_.find(id); return it == chargers_.end() ? nullptr : it->second.get(); }

    bool assign(std::string_view rid, std::string_view cid) {
        Robot* r = robot(rid);
        Charger* c = charger(cid);
        if (!r || !c) return false;
        if (r->charger_ == c) return true;
        if (c->used_ >= c->slots_) return false;
        detach(*r);
        r->charger_ = c;
        ++c->used_;
        return true;
    }

    void unassign(std::string_view rid) { if (Robot* r = robot(rid)) detach(*r); }

    bool remove_robot(std::string_view id) {
        auto it = robots_.find(id);
        if (it == robots_.end()) return false;
        detach(*it->second);
        robots_.erase(it);                           // unique_ptr frees the robot (and its map share)
        return true;
    }

    bool remove_charger(std::string_view id) {
        auto it = chargers_.find(id);
        if (it == chargers_.end()) return false;
        for (auto& [_, r] : robots_)
            if (r->charger_ == it->second.get()) r->charger_ = nullptr;   // unlink observers first
        chargers_.erase(it);
        return true;
    }

    std::vector<std::string> robots_at(std::string_view cid) const {
        std::vector<std::string> out;
        auto it = chargers_.find(cid);
        if (it == chargers_.end()) return out;
        for (const auto& [name, r] : robots_)                 // std::map: already sorted
            if (r->charger_ == it->second.get()) out.push_back(name);
        return out;
    }

    std::shared_ptr<const MapData> publish_map(int version, std::string name) {
        current_map_ = std::make_shared<const MapData>(MapData{version, std::move(name)});
        return current_map_;
    }

    void sync_maps() { for (auto& [_, r] : robots_) r->map_ = current_map_; }

    std::size_t robot_count() const { return robots_.size(); }
    std::size_t charger_count() const { return chargers_.size(); }

private:
    void detach(Robot& r) {
        if (r.charger_) { --r.charger_->used_; r.charger_ = nullptr; }
    }

    // Declaration order matters: chargers outlive robots during destruction.
    std::map<std::string, std::unique_ptr<Charger>, std::less<>> chargers_;
    std::map<std::string, std::unique_ptr<Robot>, std::less<>> robots_;
    std::shared_ptr<const MapData> current_map_;
};
```

- **Composition through `unique_ptr`**: the fleet exclusively owns robots and chargers. Heap allocation gives stable addresses, so `Robot&` handed out by `add_robot` survives 20,000 later insertions. The starter's `vector<Robot>` reallocates, so those references dangle.
- **Association through raw pointers**: a robot *observes* its charger. Raw pointers are the honest type for "non-owning, guaranteed to outlive me". `remove_charger` restores that guarantee by unlinking every observer before destroying the target.
- **Destruction order is part of the design**: members are destroyed in reverse declaration order, so declaring the chargers first makes robots (the observers) die before the chargers they point to.
- **Shared ownership where it's real**: several robots use the same immutable map version, and nobody can say who's last. `shared_ptr<const MapData>` frees each version exactly when its last holder lets go, as the `weak_ptr` probes show. `const` makes the sharing thread-safe for readers.
- **Encapsulated mutation**: `friend class Fleet` lets only the fleet change relationships, so invariants like "`used` equals the number of robots pointing here" can't be broken from outside.
