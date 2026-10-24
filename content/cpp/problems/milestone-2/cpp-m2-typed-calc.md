---
id: cpp-m2-typed-calc
title: A Dynamically Typed Expression Language
difficulty: Expert
order: 2
tags: std::variant, std::visit, std::expected, recursive descent, error handling
---
## Statement
Implement the interpreter core of a small scripting language for robot missions. Values are

```cpp
using Value = std::variant<long long, double, bool, std::string>;
```

Each input line is a statement: `let NAME = EXPR` (bind a variable and print it) or just `EXPR` (evaluate and print). Print results as `int 42`, `float 2.5` (with `std::format("{}")`), `bool true` or `str "text"`, and errors as `error: MESSAGE`.

**Grammar** (lowest to highest precedence):

```
expr    := or
or      := and { "||" and }
and     := cmp { "&&" cmp }
cmp     := sum [ ("==" | "!=" | "<" | "<=" | ">" | ">=") sum ]
sum     := term { ("+" | "-") term }
term    := unary { ("*" | "/" | "%") unary }
unary   := ("-" | "!") unary | call
call    := NAME "(" [ expr { "," expr } ] ")" | primary
primary := INT | FLOAT | "true" | "false" | STRING | NAME | "(" expr ")"
```

`STRING` is double-quoted (no escapes), `INT` is a run of digits, and `FLOAT` is digits with a `.`.

**Typing rules** (anything else is `type error: OP on TYPE and TYPE`, e.g. `type error: - on str and int`. For unary operators and one-argument functions, it's `type error: OP on TYPE`, e.g. `type error: ! on int`, `type error: len on int`. For `max`, it's `type error: max on TYPE and TYPE`):
- `int op int` → int for `+ - * %`. `/` on two ints is **integer division truncating toward zero**. Dividing (or `%`) by zero → `division by zero`.
- If either side is a float (and the other is int or float), the result is a float for `+ - * /`. `%` requires two ints.
- `str + str` → concatenation, and `str * int` → repetition (a count < 0 is a type error).
- Comparisons: numbers compare numerically (int vs float allowed), strings with strings, bools with bools (`==`/`!=` only), and the result is a bool.
- `&&`, `||` and `!` require bools; `&&`/`||` **short-circuit** (the right side isn't evaluated, so `false && (1/0 == 1)` is `false`).
- Unary `-` requires a number.
- Functions: `len(str) → int`, `abs(number)`, `max(a, b)` (numbers), `str(x) → str` (the printed form without the type prefix; strings unquoted), `int(x)` (float truncates toward zero; str parses or errors `bad int`). Unknown function → `unknown function NAME`; wrong arity → `NAME expects N args`.

Other errors: `unknown variable NAME`, and `syntax error at COL` (1-based column of the offending token; the end of the line counts as one past the last character). A failed `let` doesn't bind anything.

Use **`std::expected<Value, std::string>`** to propagate errors through the evaluator (no exceptions in the evaluation path), and **`std::visit`** to dispatch on value types.

## Starter
```cpp
#include <iostream>
#include <string>
#include <variant>

using Value = std::variant<long long, double, bool, std::string>;

int main() {
    std::string line;
    while (std::getline(std::cin, line)) std::cout << "error: not implemented\n";
}
```

## Tests
=== sample
1 + 2 * 3
7 / 2
-7 / 2
7.0 / 2
"ab" + "cd"
"ha" * 3
let speed = 2.5
speed * 2
let name = "rover"
len(name) + 1
1 < 2 && "a" < "b"
false && (1 / 0 == 1)
true || x
"a" - 1
5 % 0
max(3, 7.5)
str(42) + "!"
int("12") + 1
int(-2.9)
foo(1)
len(1, 2)
unknownvar + 1
(1 + 2
1 +
---
int 7
int 3
int -3
float 3.5
str "abcd"
str "hahaha"
float 2.5
float 5
str "rover"
int 6
bool true
bool false
bool true
error: type error: - on str and int
error: division by zero
float 7.5
str "42!"
int 13
int -2
error: unknown function foo
error: len expects 1 args
error: unknown variable unknownvar
error: syntax error at 7
error: syntax error at 4
=== hidden
let a = 10
let b = 3
a / b
a % b
-a % b
a / b * b + a % b == a
abs(-5) + abs(-2.5)
!true || !false
1 == 1.0
"x" == "x"
true == false
true < false
"abc" * -1
"abc" * 0
let s = str(true) + str(1.5) + str("q")
s
int("7x")
let bad = 1 / 0
bad
max("a", 1)
2 * (3 + 4) - -1
1.5 * 2
10000000000 * 3
!(1 < 2)
"unterminated
let = 3
3 4
---
int 10
int 3
int 3
int 1
int -1
bool true
float 7.5
bool true
bool true
bool true
bool false
error: type error: < on bool and bool
error: type error: * on str and int
str ""
str "true1.5q"
str "true1.5q"
error: bad int
error: division by zero
error: unknown variable bad
error: type error: max on str and int
int 15
float 3
int 30000000000
bool false
error: syntax error at 1
error: syntax error at 5
error: syntax error at 3

## Hints
- Tokenize first into `{kind, text, col}` tokens: numbers, strings, names, operators (two-character ones first), parentheses, commas, and an END token.
- The parser and evaluator can be combined: each grammar function returns `std::expected<Value, std::string>`. A tiny macro or helper `TRY(x)` that returns `std::unexpected(x.error())` keeps the code readable.
- Short-circuit: in `and`, if the left value is `false`, still **parse** the right side (to consume its tokens) but don't evaluate it. One way is an "evaluate" flag passed down, where skipped subtrees return a dummy value without checking types.
- `std::visit` with a generic lambda over **two** variants: `std::visit([&](const auto& a, const auto& b) -> Result { ... }, lhs, rhs)` with `if constexpr` on `std::is_same_v<std::decay_t<decltype(a)>, long long>` etc.
- Type names for errors: `int`, `float`, `bool`, `str`, obtained from `index()`.

## Solution
```cpp
#include <iostream>
#include <string>
#include <variant>
#include <expected>
#include <vector>
#include <map>
#include <format>
#include <cctype>
#include <cmath>
#include <charconv>
#include <type_traits>

using Value = std::variant<long long, double, bool, std::string>;
using Result = std::expected<Value, std::string>;
static const char* kType[] = {"int", "float", "bool", "str"};

std::string show(const Value& v, bool quote_str = true) {
    return std::visit([&](const auto& x) -> std::string {
        using T = std::decay_t<decltype(x)>;
        if constexpr (std::is_same_v<T, bool>) return x ? "true" : "false";
        else if constexpr (std::is_same_v<T, std::string>) return quote_str ? "\"" + x + "\"" : x;
        else return std::format("{}", x);
    }, v);
}

struct Token { std::string kind, text; int col; };

std::expected<std::vector<Token>, std::string> tokenize(const std::string& s) {
    std::vector<Token> out;
    std::size_t i = 0;
    while (i < s.size()) {
        char c = s[i];
        int col = static_cast<int>(i) + 1;
        if (std::isspace(static_cast<unsigned char>(c))) { ++i; continue; }
        if (std::isdigit(static_cast<unsigned char>(c))) {
            std::size_t j = i;
            while (j < s.size() && std::isdigit(static_cast<unsigned char>(s[j]))) ++j;
            bool isf = j < s.size() && s[j] == '.';
            if (isf) { ++j; while (j < s.size() && std::isdigit(static_cast<unsigned char>(s[j]))) ++j; }
            out.push_back({isf ? "float" : "int", s.substr(i, j - i), col});
            i = j;
        } else if (std::isalpha(static_cast<unsigned char>(c)) || c == '_') {
            std::size_t j = i;
            while (j < s.size() && (std::isalnum(static_cast<unsigned char>(s[j])) || s[j] == '_')) ++j;
            out.push_back({"name", s.substr(i, j - i), col});
            i = j;
        } else if (c == '"') {
            std::size_t j = s.find('"', i + 1);
            if (j == std::string::npos) return std::unexpected(std::format("syntax error at {}", col));
            out.push_back({"str", s.substr(i + 1, j - i - 1), col});
            i = j + 1;
        } else {
            static const char* two[] = {"==", "!=", "<=", ">=", "&&", "||"};
            std::string op(1, c);
            for (auto t : two) if (s.compare(i, 2, t) == 0) op = t;
            if (op.size() == 1 && std::string("+-*/%()<>!,=").find(c) == std::string::npos)
                return std::unexpected(std::format("syntax error at {}", col));
            out.push_back({"op", op, col});
            i += op.size();
        }
    }
    out.push_back({"end", "", static_cast<int>(s.size()) + 1});
    return out;
}

class Interp {
public:
    std::map<std::string, Value> vars;

    Result run(const std::vector<Token>& toks) {
        t_ = &toks; p_ = 0;
        auto r = expr(true);
        if (r && peek().kind != "end") return syntax();
        return r;
    }

private:
    const std::vector<Token>* t_ = nullptr;
    std::size_t p_ = 0;

    const Token& peek() const { return (*t_)[p_]; }
    bool is_op(const char* o) const { return peek().kind == "op" && peek().text == o; }
    Result syntax() const { return std::unexpected(std::format("syntax error at {}", peek().col)); }

    static std::string terr(const std::string& op, const Value& a, const Value& b) {
        return std::format("type error: {} on {} and {}", op, kType[a.index()], kType[b.index()]);
    }
    static bool is_num(const Value& v) { return v.index() <= 1; }
    static double num(const Value& v) { return v.index() == 0 ? static_cast<double>(std::get<0>(v)) : std::get<1>(v); }

    Result binary(const std::string& op, const Value& a, const Value& b) {
        if (op == "+" && a.index() == 3 && b.index() == 3) return Value{std::get<3>(a) + std::get<3>(b)};
        if (op == "*" && a.index() == 3 && b.index() == 0) {
            long long n = std::get<0>(b);
            if (n < 0) return std::unexpected(terr(op, a, b));
            std::string r;
            for (long long i = 0; i < n; ++i) r += std::get<3>(a);
            return Value{r};
        }
        if (!is_num(a) || !is_num(b)) return std::unexpected(terr(op, a, b));
        if (a.index() == 0 && b.index() == 0) {
            long long x = std::get<0>(a), y = std::get<0>(b);
            if (op == "+") return Value{x + y};
            if (op == "-") return Value{x - y};
            if (op == "*") return Value{x * y};
            if (y == 0) return std::unexpected(std::string("division by zero"));
            return op == "/" ? Value{x / y} : Value{x % y};
        }
        if (op == "%") return std::unexpected(terr(op, a, b));
        double x = num(a), y = num(b);
        if (op == "/" && y == 0) return std::unexpected(std::string("division by zero"));
        return Value{op == "+" ? x + y : op == "-" ? x - y : op == "*" ? x * y : x / y};
    }

    Result compare(const std::string& op, const Value& a, const Value& b) {
        int c;
        if (is_num(a) && is_num(b)) {
            if (a.index() == 0 && b.index() == 0) { auto x = std::get<0>(a), y = std::get<0>(b); c = x < y ? -1 : x > y; }
            else { double x = num(a), y = num(b); c = x < y ? -1 : x > y; }
        } else if (a.index() == 3 && b.index() == 3) {
            c = std::get<3>(a).compare(std::get<3>(b));
            c = c < 0 ? -1 : c > 0;
        } else if (a.index() == 2 && b.index() == 2 && (op == "==" || op == "!=")) {
            c = std::get<2>(a) == std::get<2>(b) ? 0 : 1;
        } else {
            return std::unexpected(terr(op, a, b));
        }
        bool r = op == "==" ? c == 0 : op == "!=" ? c != 0 : op == "<" ? c < 0 : op == "<=" ? c <= 0 : op == ">" ? c > 0 : c >= 0;
        return Value{r};
    }

#define TRY(var, expr_) auto var = (expr_); if (!var) return var

    Result expr(bool ev) { return orx(ev); }

    Result orx(bool ev) {
        TRY(l, andx(ev));
        while (is_op("||")) {
            ++p_;
            bool lv = ev ? (l->index() == 2 ? std::get<2>(*l) : false) : false;
            if (ev && l->index() != 2) { TRY(r, andx(false)); return std::unexpected(terr("||", *l, *r)); }
            TRY(r, andx(ev && !lv));                        // short-circuit: only evaluated if l is false
            if (ev && !lv) {
                if (r->index() != 2) return std::unexpected(terr("||", *l, *r));
                l = Value{std::get<2>(*r)};
            } else if (ev) {
                l = Value{true};
            }
        }
        return l;
    }

    Result andx(bool ev) {
        TRY(l, cmp(ev));
        while (is_op("&&")) {
            ++p_;
            if (ev && l->index() != 2) { TRY(r, cmp(false)); return std::unexpected(terr("&&", *l, *r)); }
            bool lv = ev ? std::get<2>(*l) : false;
            TRY(r, cmp(ev && lv));
            if (ev && lv) {
                if (r->index() != 2) return std::unexpected(terr("&&", *l, *r));
                l = Value{std::get<2>(*r)};
            } else if (ev) {
                l = Value{false};
            }
        }
        return l;
    }

    Result cmp(bool ev) {
        TRY(l, sum(ev));
        for (const char* o : {"==", "!=", "<=", ">=", "<", ">"}) {
            if (is_op(o)) {
                ++p_;
                TRY(r, sum(ev));
                if (!ev) return l;
                return compare(o, *l, *r);
            }
        }
        return l;
    }

    Result sum(bool ev) {
        TRY(l, term(ev));
        while (is_op("+") || is_op("-")) {
            std::string op = peek().text;
            ++p_;
            TRY(r, term(ev));
            if (ev) { TRY(v, binary(op, *l, *r)); l = *v; }
        }
        return l;
    }

    Result term(bool ev) {
        TRY(l, unary(ev));
        while (is_op("*") || is_op("/") || is_op("%")) {
            std::string op = peek().text;
            ++p_;
            TRY(r, unary(ev));
            if (ev) { TRY(v, binary(op, *l, *r)); l = *v; }
        }
        return l;
    }

    Result unary(bool ev) {
        if (is_op("-")) {
            ++p_;
            TRY(v, unary(ev));
            if (!ev) return v;
            if (v->index() == 0) return Value{-std::get<0>(*v)};
            if (v->index() == 1) return Value{-std::get<1>(*v)};
            return std::unexpected(std::format("type error: - on {}", kType[v->index()]));
        }
        if (is_op("!")) {
            ++p_;
            TRY(v, unary(ev));
            if (!ev) return v;
            if (v->index() != 2) return std::unexpected(std::format("type error: ! on {}", kType[v->index()]));
            return Value{!std::get<2>(*v)};
        }
        return primary(ev);
    }

    Result call(const std::string& name, const std::vector<Value>& a) {
        auto arity = [&](std::size_t n) -> bool { return a.size() == n; };
        auto arity_err = [&](int n) { return std::unexpected(std::format("{} expects {} args", name, n)); };
        if (name == "len") {
            if (!arity(1)) return arity_err(1);
            if (a[0].index() != 3) return std::unexpected(std::format("type error: len on {}", kType[a[0].index()]));
            return Value{static_cast<long long>(std::get<3>(a[0]).size())};
        }
        if (name == "abs") {
            if (!arity(1)) return arity_err(1);
            if (a[0].index() == 0) return Value{std::llabs(std::get<0>(a[0]))};
            if (a[0].index() == 1) return Value{std::fabs(std::get<1>(a[0]))};
            return std::unexpected(std::format("type error: abs on {}", kType[a[0].index()]));
        }
        if (name == "max") {
            if (!arity(2)) return arity_err(2);
            if (!is_num(a[0]) || !is_num(a[1])) return std::unexpected(terr("max", a[0], a[1]));
            if (a[0].index() == 0 && a[1].index() == 0) return Value{std::max(std::get<0>(a[0]), std::get<0>(a[1]))};
            return Value{std::max(num(a[0]), num(a[1]))};
        }
        if (name == "str") {
            if (!arity(1)) return arity_err(1);
            return Value{show(a[0], false)};
        }
        if (name == "int") {
            if (!arity(1)) return arity_err(1);
            switch (a[0].index()) {
                case 0: return a[0];
                case 1: return Value{static_cast<long long>(std::trunc(std::get<1>(a[0])))};
                case 3: {
                    const std::string& s = std::get<3>(a[0]);
                    long long v;
                    auto [ptr, ec] = std::from_chars(s.data(), s.data() + s.size(), v);
                    if (ec != std::errc{} || ptr != s.data() + s.size()) return std::unexpected(std::string("bad int"));
                    return Value{v};
                }
                default: return std::unexpected(std::string("type error: int on bool"));
            }
        }
        return std::unexpected(std::format("unknown function {}", name));
    }

    Result primary(bool ev) {
        const Token tk = peek();
        if (tk.kind == "int") { ++p_; return Value{std::stoll(tk.text)}; }
        if (tk.kind == "float") { ++p_; return Value{std::stod(tk.text)}; }
        if (tk.kind == "str") { ++p_; return Value{tk.text}; }
        if (tk.kind == "name") {
            ++p_;
            if (tk.text == "true" || tk.text == "false") return Value{tk.text == "true"};
            if (is_op("(")) {
                ++p_;
                std::vector<Value> args;
                if (!is_op(")")) {
                    for (;;) {
                        TRY(v, expr(ev));
                        args.push_back(*v);
                        if (is_op(",")) { ++p_; continue; }
                        break;
                    }
                }
                if (!is_op(")")) return syntax();
                ++p_;
                if (!ev) return Value{0LL};
                return call(tk.text, args);
            }
            if (!ev) return Value{0LL};
            auto it = vars.find(tk.text);
            if (it == vars.end()) return std::unexpected(std::format("unknown variable {}", tk.text));
            return it->second;
        }
        if (is_op("(")) {
            ++p_;
            TRY(v, expr(ev));
            if (!is_op(")")) return syntax();
            ++p_;
            return v;
        }
        return syntax();
    }
#undef TRY
};

int main() {
    Interp in;
    std::string line;
    while (std::getline(std::cin, line)) {
        auto toks = tokenize(line);
        if (!toks) { std::cout << "error: " << toks.error() << '\n'; continue; }
        std::vector<Token>& t = *toks;
        std::string bind;
        std::vector<Token> body = t;
        if (t.size() >= 2 && t[0].kind == "name" && t[0].text == "let") {
            if (t.size() < 4 || t[1].kind != "name" || t[2].text != "=") {
                std::cout << "error: syntax error at " << (t.size() > 1 ? t[1].col : t[0].col) << '\n';
                continue;
            }
            bind = t[1].text;
            body.assign(t.begin() + 3, t.end());
        }
        Result r = in.run(body);
        if (!r) { std::cout << "error: " << r.error() << '\n'; continue; }
        if (!bind.empty()) in.vars[bind] = *r;
        static const char* names[] = {"int", "float", "bool", "str"};
        std::cout << names[r->index()] << ' ' << show(*r) << '\n';
    }
}
```

**Milestone review:**
- **`std::variant` as a value model:** a closed set of types with no heap allocation for numbers and bools, where `index()` gives cheap type tags and `std::visit` with `if constexpr` dispatches on the active alternative (module 4).
- **`std::expected` error propagation:** every grammar function returns either a value or an error string, and errors flow up without exceptions, so the type signature documents that evaluation can fail (module 6).
- **Recursive descent with a precedence ladder:** one function per level, exactly like the C calculator milestone, now with typed values.
- **Short-circuit evaluation** is implemented by still *parsing* the skipped operand (to stay in sync with the tokens) while *not evaluating* it. The `ev` flag propagates "don't evaluate" down the recursion, so `false && (1/0 == 1)` never divides by zero.
