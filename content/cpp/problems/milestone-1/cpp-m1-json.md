---
id: cpp-m1-json
title: Polymorphic JSON Document Model
difficulty: Hard
order: 2
tags: polymorphism, unique_ptr, recursion, parsing, clone, composite
---
## Statement
Build a JSON document model with a **class hierarchy**: an abstract `Value` with concrete `Null`, `Bool`, `Number` (integers only, `long long`), `String`, `Array` and `Object` (which keeps keys in **insertion order**; a duplicate key replaces the value but keeps the original position). Children are owned through `std::unique_ptr<Value>`.

The first input line is a JSON document. It may contain any whitespace between tokens, strings with the escapes `\"`, `\\`, `\n` and `\t`, and negative integers. Each following line is a query:

| Query | Output |
|---|---|
| `compact` | the document with no whitespace, e.g. `{"a":[1,true]}` |
| `pretty` | indented by 2 spaces per level: one element per line, `"key": value` with a space after the colon, `[]` and `{}` for empty containers |
| `get PATH` | the compact form of the value at PATH, or `not found` |
| `type PATH` | `null`, `bool`, `number`, `string`, `array` or `object`, or `not found` |
| `stats` | `null=a bool=b number=c string=d array=e object=f`: node counts in the whole tree |
| `sum PATH` | the sum of all numbers anywhere inside the value at PATH (recursively) |
| `clone-test PATH` | deep-copies the value at PATH, appends the number `999` to the copy if it's an array (otherwise does nothing to it), then prints `original=<compact> copy=<compact>`. The original must be unchanged |

A PATH is a sequence of steps, `.key` or `[index]`, starting from the root, written as `$`: for example `$`, `$.robots[1].name`, `$[0]`. Keys contain only letters, digits and `_`.

On invalid JSON, print `parse error at N` (the 1-based column) and ignore the queries.

## Starter
```cpp
#include <iostream>
#include <memory>
#include <string>
#include <vector>

class Value {
public:
    virtual ~Value() = default;
};

int main() {
    std::string doc;
    std::getline(std::cin, doc);
    std::string q;
    while (std::getline(std::cin, q)) {
    }
}
```

## Tests
=== sample
{"name": "rover", "wheels": 4, "sensors": ["lidar", "imu"], "pose": {"x": -2, "y": 7}, "active": true, "note": null}
compact
type $.sensors
get $.pose.x
get $.sensors[1]
get $.sensors[5]
sum $
stats
clone-test $.sensors
pretty
---
{"name":"rover","wheels":4,"sensors":["lidar","imu"],"pose":{"x":-2,"y":7},"active":true,"note":null}
array
-2
"imu"
not found
9
null=1 bool=1 number=3 string=3 array=1 object=2
original=["lidar","imu"] copy=["lidar","imu",999]
{
  "name": "rover",
  "wheels": 4,
  "sensors": [
    "lidar",
    "imu"
  ],
  "pose": {
    "x": -2,
    "y": 7
  },
  "active": true,
  "note": null
}
=== hidden
[]
compact
pretty
stats
sum $
clone-test $
get $[0]
type $
---
[]
[]
null=0 bool=0 number=0 string=0 array=1 object=0
0
original=[] copy=[999]
not found
array
=== hidden
  { "a" : { } , "b" : [ [ ] , { "k" : "v\"q\\" } ] , "a" : 3 , "esc" : "tab\tnl\n" }
compact
pretty
get $.a
get $.b[1].k
type $.b[0]
sum $.b
clone-test $.b[1]
---
{"a":3,"b":[[],{"k":"v\"q\\"}],"esc":"tab\tnl\n"}
{
  "a": 3,
  "b": [
    [],
    {
      "k": "v\"q\\"
    }
  ],
  "esc": "tab\tnl\n"
}
3
"v\"q\\"
array
0
original={"k":"v\"q\\"} copy={"k":"v\"q\\"}
=== hidden
{"a": [1, 2,]}
compact
---
parse error at 13
=== hidden
{"deep": [[[[[[1]]]], 2], [3, [4, [5]]]], "neg": -10}
sum $
sum $.deep[1]
get $.deep[0][0][0][0][0][0]
get $.deep[0][0][0][0][0][0][0]
type $.neg
stats
clone-test $.deep[1][1]
---
5
12
1
not found
number
null=0 bool=0 number=6 string=0 array=9 object=1
original=[4,[5]] copy=[4,[5],999]
=== hidden
{"x": tru}
---
parse error at 7
=== hidden
"just a string"
compact
type $
get $.x
---
"just a string"
string
not found
=== hidden
{"unterminated": "abc
---
parse error at 22

## Hints
- Give `Value` pure virtual functions: `type()`, `write(std::string& out, int indent, bool pretty)`, `clone()`, and a `visit` hook for `stats`/`sum` (or just `virtual void accumulate(Stats&) const`).
- The parser is recursive descent over the document string with a position index. `parse_value` dispatches on the first non-space character. On any error, throw an exception carrying the column, caught in `main`.
- `Object` can store `std::vector<std::pair<std::string, std::unique_ptr<Value>>>` to keep insertion order (lookups are linear, which is fine here).
- Path lookup: walk step by step using `dynamic_cast<const Object*>` / `dynamic_cast<const Array*>`, or add virtual `child(key)` / `child(index)` returning `nullptr` by default.
- When writing strings, escape `"`, `\`, newline and tab back.

## Solution
```cpp
#include <iostream>
#include <memory>
#include <string>
#include <vector>
#include <utility>
#include <stdexcept>
#include <cctype>

struct Stats { long long counts[6] = {0, 0, 0, 0, 0, 0}; long long sum = 0; };
enum Kind { NUL, BOOL, NUM, STR, ARR, OBJ };
static const char* kNames[] = {"null", "bool", "number", "string", "array", "object"};

class Value {
public:
    virtual ~Value() = default;
    virtual Kind kind() const = 0;
    virtual void write(std::string& out, int indent, bool pretty) const = 0;
    virtual std::unique_ptr<Value> clone() const = 0;
    virtual void accumulate(Stats& s) const { ++s.counts[kind()]; }
    virtual const Value* child(const std::string&) const { return nullptr; }
    virtual const Value* child(long long) const { return nullptr; }
};
using P = std::unique_ptr<Value>;

static void newline(std::string& out, int indent) { out += '\n'; out.append(static_cast<std::size_t>(indent) * 2, ' '); }
static void write_string(std::string& out, const std::string& s) {
    out += '"';
    for (char c : s) {
        if (c == '"') out += "\\\"";
        else if (c == '\\') out += "\\\\";
        else if (c == '\n') out += "\\n";
        else if (c == '\t') out += "\\t";
        else out += c;
    }
    out += '"';
}

class Null final : public Value {
public:
    Kind kind() const override { return NUL; }
    void write(std::string& out, int, bool) const override { out += "null"; }
    P clone() const override { return std::make_unique<Null>(); }
};
class Bool final : public Value {
public:
    explicit Bool(bool b) : b_(b) {}
    Kind kind() const override { return BOOL; }
    void write(std::string& out, int, bool) const override { out += b_ ? "true" : "false"; }
    P clone() const override { return std::make_unique<Bool>(b_); }
private:
    bool b_;
};
class Number final : public Value {
public:
    explicit Number(long long v) : v_(v) {}
    Kind kind() const override { return NUM; }
    void write(std::string& out, int, bool) const override { out += std::to_string(v_); }
    P clone() const override { return std::make_unique<Number>(v_); }
    void accumulate(Stats& s) const override { Value::accumulate(s); s.sum += v_; }
private:
    long long v_;
};
class String final : public Value {
public:
    explicit String(std::string s) : s_(std::move(s)) {}
    Kind kind() const override { return STR; }
    void write(std::string& out, int, bool) const override { write_string(out, s_); }
    P clone() const override { return std::make_unique<String>(s_); }
private:
    std::string s_;
};
class Array final : public Value {
public:
    void push(P v) { items_.push_back(std::move(v)); }
    Kind kind() const override { return ARR; }
    void write(std::string& out, int indent, bool pretty) const override {
        if (items_.empty()) { out += "[]"; return; }
        out += '[';
        for (std::size_t i = 0; i < items_.size(); ++i) {
            if (i) out += ',';
            if (pretty) newline(out, indent + 1);
            items_[i]->write(out, indent + 1, pretty);
        }
        if (pretty) newline(out, indent);
        out += ']';
    }
    P clone() const override {
        auto a = std::make_unique<Array>();
        for (const auto& v : items_) a->push(v->clone());
        return a;
    }
    void accumulate(Stats& s) const override { Value::accumulate(s); for (const auto& v : items_) v->accumulate(s); }
    const Value* child(long long i) const override {
        return i >= 0 && static_cast<std::size_t>(i) < items_.size() ? items_[static_cast<std::size_t>(i)].get() : nullptr;
    }
private:
    std::vector<P> items_;
};
class Object final : public Value {
public:
    void set(std::string k, P v) {
        for (auto& [key, val] : items_) if (key == k) { val = std::move(v); return; }
        items_.emplace_back(std::move(k), std::move(v));
    }
    Kind kind() const override { return OBJ; }
    void write(std::string& out, int indent, bool pretty) const override {
        if (items_.empty()) { out += "{}"; return; }
        out += '{';
        for (std::size_t i = 0; i < items_.size(); ++i) {
            if (i) out += ',';
            if (pretty) newline(out, indent + 1);
            write_string(out, items_[i].first);
            out += pretty ? ": " : ":";
            items_[i].second->write(out, indent + 1, pretty);
        }
        if (pretty) newline(out, indent);
        out += '}';
    }
    P clone() const override {
        auto o = std::make_unique<Object>();
        for (const auto& [k, v] : items_) o->set(k, v->clone());
        return o;
    }
    void accumulate(Stats& s) const override { Value::accumulate(s); for (const auto& kv : items_) kv.second->accumulate(s); }
    const Value* child(const std::string& k) const override {
        for (const auto& [key, val] : items_) if (key == k) return val.get();
        return nullptr;
    }
private:
    std::vector<std::pair<std::string, P>> items_;
};

struct ParseError { std::size_t col; };

class Parser {
public:
    explicit Parser(const std::string& s) : s_(s) {}
    P parse_document() {
        P v = value();
        ws();
        if (i_ != s_.size()) fail();
        return v;
    }
private:
    [[noreturn]] void fail() { throw ParseError{i_ + 1}; }
    void ws() { while (i_ < s_.size() && std::isspace(static_cast<unsigned char>(s_[i_]))) ++i_; }
    bool eat(char c) { ws(); if (i_ < s_.size() && s_[i_] == c) { ++i_; return true; } return false; }
    void need(char c) { if (!eat(c)) fail(); }
    bool word(const char* w) {
        std::string_view sv(w);
        if (s_.compare(i_, sv.size(), sv) == 0) { i_ += sv.size(); return true; }
        return false;
    }
    std::string str() {
        need('"');
        std::string out;
        while (true) {
            if (i_ >= s_.size()) fail();
            char c = s_[i_++];
            if (c == '"') return out;
            if (c == '\\') {
                if (i_ >= s_.size()) fail();
                char e = s_[i_++];
                if (e == '"' || e == '\\') out += e;
                else if (e == 'n') out += '\n';
                else if (e == 't') out += '\t';
                else { --i_; fail(); }
            } else out += c;
        }
    }
    P value() {
        ws();
        if (i_ >= s_.size()) fail();
        char c = s_[i_];
        if (c == '{') {
            ++i_;
            auto o = std::make_unique<Object>();
            if (eat('}')) return o;
            do {
                ws();
                std::string k = str();
                need(':');
                o->set(std::move(k), value());
            } while (eat(','));
            need('}');
            return o;
        }
        if (c == '[') {
            ++i_;
            auto a = std::make_unique<Array>();
            if (eat(']')) return a;
            do { a->push(value()); } while (eat(','));
            need(']');
            return a;
        }
        if (c == '"') return std::make_unique<String>(str());
        if (c == '-' || std::isdigit(static_cast<unsigned char>(c))) {
            std::size_t st = i_;
            if (c == '-') ++i_;
            if (i_ >= s_.size() || !std::isdigit(static_cast<unsigned char>(s_[i_]))) fail();
            while (i_ < s_.size() && std::isdigit(static_cast<unsigned char>(s_[i_]))) ++i_;
            return std::make_unique<Number>(std::stoll(s_.substr(st, i_ - st)));
        }
        if (word("true")) return std::make_unique<Bool>(true);
        if (word("false")) return std::make_unique<Bool>(false);
        if (word("null")) return std::make_unique<Null>();
        fail();
    }
    const std::string& s_;
    std::size_t i_ = 0;
};

static const Value* resolve(const Value* v, const std::string& path) {
    if (path.empty() || path[0] != '$') return nullptr;
    std::size_t i = 1;
    while (v && i < path.size()) {
        if (path[i] == '.') {
            std::size_t j = ++i;
            while (j < path.size() && (std::isalnum(static_cast<unsigned char>(path[j])) || path[j] == '_')) ++j;
            v = v->child(path.substr(i, j - i));
            i = j;
        } else if (path[i] == '[') {
            std::size_t j = path.find(']', i);
            if (j == std::string::npos) return nullptr;
            v = v->child(std::stoll(path.substr(i + 1, j - i - 1)));
            i = j + 1;
        } else return nullptr;
    }
    return v;
}

static std::string compact(const Value& v) { std::string s; v.write(s, 0, false); return s; }

int main() {
    std::string doc;
    std::getline(std::cin, doc);
    P root;
    try {
        root = Parser(doc).parse_document();
    } catch (const ParseError& e) {
        std::cout << "parse error at " << e.col << '\n';
        return 0;
    }
    std::string line;
    while (std::getline(std::cin, line)) {
        std::string cmd = line.substr(0, line.find(' '));
        std::string arg = line.find(' ') == std::string::npos ? "" : line.substr(line.find(' ') + 1);
        if (cmd == "compact") std::cout << compact(*root) << '\n';
        else if (cmd == "pretty") { std::string s; root->write(s, 0, true); std::cout << s << '\n'; }
        else if (cmd == "stats") {
            Stats st; root->accumulate(st);
            for (int k = 0; k < 6; ++k) std::cout << (k ? " " : "") << kNames[k] << '=' << st.counts[k];
            std::cout << '\n';
        } else {
            const Value* v = resolve(root.get(), arg);
            if (!v) { std::cout << "not found\n"; continue; }
            if (cmd == "get") std::cout << compact(*v) << '\n';
            else if (cmd == "type") std::cout << kNames[v->kind()] << '\n';
            else if (cmd == "sum") { Stats st; v->accumulate(st); std::cout << st.sum << '\n'; }
            else if (cmd == "clone-test") {
                P copy = v->clone();
                if (auto* a = dynamic_cast<Array*>(copy.get())) a->push(std::make_unique<Number>(999));
                std::cout << "original=" << compact(*v) << " copy=" << compact(*copy) << '\n';
            }
        }
    }
}
```

**Design review:**
- **Composite + polymorphism:** containers hold `unique_ptr<Value>`, so a tree of mixed node types has a single, clear owner per node. Destroying the root frees everything through the virtual destructor.
- **Virtual operations instead of type switches:** `write`, `clone`, `accumulate` and `child` are virtual, so adding a node type means adding one class. `child()` returns `nullptr` by default, which makes path resolution uniform: "not an object" and "missing key" become the same failure.
- **`clone()` is a deep, polymorphic copy.** The `clone-test` query proves the copy is independent. A shallow copy of `unique_ptr` wouldn't even compile, which is the type system enforcing ownership.
- **The parser throws** a small `ParseError` carrying the column, the C++ counterpart of the sticky error code in the C calculator. Because every node is owned by a `unique_ptr`, a partially built tree is freed automatically when the exception propagates.
