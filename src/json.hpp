// A small JSON value for the catalog's records. Objects keep their key order, and printing follows Python's
// json.dumps(ensure_ascii=False) and str(): the format the catalog was first published in, kept so the exports and
// pages stay byte-stable.
#pragma once

#include <string>
#include <string_view>
#include <utility>
#include <vector>

namespace json {

struct Value;
using Array = std::vector<Value>;
using Object = std::vector<std::pair<std::string, Value>>;

struct Value {
    enum class Kind { null, boolean, integer, real, string, array, object };

    Kind kind = Kind::null;
    bool boolean = false;
    std::string text;  // the string, or an integer's digits
    double real = 0;
    Array array;
    Object object;

    static Value of(std::string s);

    bool is_null() const { return kind == Kind::null; }
    bool is_string() const { return kind == Kind::string; }
    bool is_object() const { return kind == Kind::object; }
    bool is_array() const { return kind == Kind::array; }
    bool is_bool() const { return kind == Kind::boolean; }

    // Python truthiness: None, False, 0, 0.0, "", [] and {} are false.
    bool truthy() const;

    // The member called `key`, or nullptr. Missing and null are different, as in Python's `key in d`.
    const Value* find(std::string_view key) const;
    // d.get(key): the member, or a null value when it's missing.
    const Value& get(std::string_view key) const;
    // Python `d.get(key) not in (None, "")`.
    bool present(std::string_view key) const;
    // Sets or replaces a member, keeping the position of an existing key.
    void set(std::string key, Value value);
};

// Throws json::Error on malformed input. Duplicate keys keep the first position and the last value, as Python does.
Value parse(std::string_view text);

struct Error {
    std::string message;
};

// json.dumps(value, ensure_ascii=False).
std::string dumps(const Value& value);
// str(value) in an f-string.
std::string str(const Value& value);
// repr(value).
std::string repr(const Value& value);
// repr(float): the shortest digits that round-trip, fixed between 1e-4 and 1e16, scientific outside.
std::string float_repr(double value);

const Value& null_value();

}  // namespace json
