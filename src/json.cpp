#include "json.hpp"

#include <algorithm>
#include <charconv>
#include <cmath>
#include <cstdlib>
#include <cstdio>
#include <cstring>

#include "text.hpp"

namespace json {

namespace {

class Parser {
public:
    explicit Parser(std::string_view text) : text_(text) {}

    Value document() {
        Value value = parse_value();
        skip_space();
        if (pos_ != text_.size()) fail("extra data");
        return value;
    }

private:
    std::string_view text_;
    size_t pos_ = 0;

    [[noreturn]] void fail(const char* what) const {
        throw Error{std::string(what) + " at byte " + std::to_string(pos_)};
    }

    void skip_space() {
        while (pos_ < text_.size() && (text_[pos_] == ' ' || text_[pos_] == '\t' || text_[pos_] == '\n' || text_[pos_] == '\r')) {
            ++pos_;
        }
    }

    bool consume(std::string_view word) {
        if (text_.substr(pos_, word.size()) != word) return false;
        pos_ += word.size();
        return true;
    }

    Value parse_value() {
        skip_space();
        if (pos_ >= text_.size()) fail("unexpected end");
        Value value;
        switch (text_[pos_]) {
        case '{': return parse_object();
        case '[': return parse_array();
        case '"':
            value.kind = Value::Kind::string;
            value.text = parse_string();
            return value;
        case 't':
            if (!consume("true")) fail("bad literal");
            value.kind = Value::Kind::boolean;
            value.boolean = true;
            return value;
        case 'f':
            if (!consume("false")) fail("bad literal");
            value.kind = Value::Kind::boolean;
            return value;
        case 'n':
            if (!consume("null")) fail("bad literal");
            return value;
        default: return parse_number();
        }
    }

    Value parse_object() {
        Value value;
        value.kind = Value::Kind::object;
        ++pos_;
        skip_space();
        if (consume("}")) return value;
        while (true) {
            skip_space();
            if (pos_ >= text_.size() || text_[pos_] != '"') fail("expected a key");
            std::string key = parse_string();
            skip_space();
            if (!consume(":")) fail("expected ':'");
            value.set(std::move(key), parse_value());
            skip_space();
            if (consume(",")) continue;
            if (consume("}")) return value;
            fail("expected ',' or '}'");
        }
    }

    Value parse_array() {
        Value value;
        value.kind = Value::Kind::array;
        ++pos_;
        skip_space();
        if (consume("]")) return value;
        while (true) {
            value.array.push_back(parse_value());
            skip_space();
            if (consume(",")) continue;
            if (consume("]")) return value;
            fail("expected ',' or ']'");
        }
    }

    unsigned hex4() {
        if (pos_ + 4 > text_.size()) fail("short \\u escape");
        unsigned code = 0;
        for (int i = 0; i < 4; ++i) {
            char c = text_[pos_++];
            code <<= 4;
            if (c >= '0' && c <= '9') code |= c - '0';
            else if (c >= 'a' && c <= 'f') code |= c - 'a' + 10;
            else if (c >= 'A' && c <= 'F') code |= c - 'A' + 10;
            else fail("bad \\u escape");
        }
        return code;
    }

    std::string parse_string() {
        ++pos_;
        std::string out;
        while (true) {
            if (pos_ >= text_.size()) fail("unterminated string");
            char c = text_[pos_++];
            if (c == '"') return out;
            if (c != '\\') {
                out += c;
                continue;
            }
            if (pos_ >= text_.size()) fail("unterminated escape");
            char e = text_[pos_++];
            switch (e) {
            case '"': out += '"'; break;
            case '\\': out += '\\'; break;
            case '/': out += '/'; break;
            case 'b': out += '\b'; break;
            case 'f': out += '\f'; break;
            case 'n': out += '\n'; break;
            case 'r': out += '\r'; break;
            case 't': out += '\t'; break;
            case 'u': {
                char32_t code = hex4();
                if (code >= 0xD800 && code < 0xDC00 && text_.substr(pos_, 2) == "\\u") {
                    size_t save = pos_;
                    pos_ += 2;
                    char32_t low = hex4();
                    if (low >= 0xDC00 && low < 0xE000) {
                        code = 0x10000 + ((code - 0xD800) << 10) + (low - 0xDC00);
                    } else {
                        pos_ = save;
                    }
                }
                text::append_utf8(out, code);
                break;
            }
            default: fail("bad escape");
            }
        }
    }

    Value parse_number() {
        size_t start = pos_;
        if (text_[pos_] == '-') ++pos_;
        bool real = false;
        while (pos_ < text_.size()) {
            char c = text_[pos_];
            if (c >= '0' && c <= '9') {
                ++pos_;
            } else if (c == '.' || c == 'e' || c == 'E' || c == '+' || c == '-') {
                real = true;
                ++pos_;
            } else {
                break;
            }
        }
        std::string number(text_.substr(start, pos_ - start));
        if (number.empty() || number == "-") fail("expected a value");
        Value value;
        if (real) {
            value.kind = Value::Kind::real;
            value.real = std::strtod(number.c_str(), nullptr);
        } else {
            value.kind = Value::Kind::integer;
            // Python ints print without a sign on zero.
            value.text = number == "-0" ? "0" : number;
        }
        return value;
    }
};

void dump_string(std::string& out, std::string_view s) {
    out += '"';
    for (unsigned char c : s) {
        switch (c) {
        case '"': out += "\\\""; break;
        case '\\': out += "\\\\"; break;
        case '\n': out += "\\n"; break;
        case '\r': out += "\\r"; break;
        case '\t': out += "\\t"; break;
        case '\b': out += "\\b"; break;
        case '\f': out += "\\f"; break;
        default:
            if (c < 0x20) {
                char buffer[8];
                std::snprintf(buffer, sizeof buffer, "\\u%04x", c);
                out += buffer;
            } else {
                out += static_cast<char>(c);
            }
        }
    }
    out += '"';
}

void dump(std::string& out, const Value& value) {
    switch (value.kind) {
    case Value::Kind::null: out += "null"; break;
    case Value::Kind::boolean: out += value.boolean ? "true" : "false"; break;
    case Value::Kind::integer: out += value.text; break;
    case Value::Kind::real:
        if (std::isnan(value.real)) out += "NaN";
        else if (std::isinf(value.real)) out += value.real > 0 ? "Infinity" : "-Infinity";
        else out += float_repr(value.real);
        break;
    case Value::Kind::string: dump_string(out, value.text); break;
    case Value::Kind::array:
        out += '[';
        for (size_t i = 0; i < value.array.size(); ++i) {
            if (i) out += ", ";
            dump(out, value.array[i]);
        }
        out += ']';
        break;
    case Value::Kind::object:
        out += '{';
        for (size_t i = 0; i < value.object.size(); ++i) {
            if (i) out += ", ";
            dump_string(out, value.object[i].first);
            out += ": ";
            dump(out, value.object[i].second);
        }
        out += '}';
        break;
    }
}

// repr(str): single quotes unless the string has a single quote and no double quote.
std::string repr_string(std::string_view s) {
    bool single = s.find('\'') != std::string_view::npos;
    bool dbl = s.find('"') != std::string_view::npos;
    char quote = single && !dbl ? '"' : '\'';
    std::string out(1, quote);
    for (char32_t c : text::decode(s)) {
        if (c == static_cast<char32_t>(quote) || c == '\\') {
            out += '\\';
            out += static_cast<char>(c);
        } else if (c == '\n') {
            out += "\\n";
        } else if (c == '\r') {
            out += "\\r";
        } else if (c == '\t') {
            out += "\\t";
        } else if (c < 0x20 || c == 0x7f) {
            char buffer[8];
            std::snprintf(buffer, sizeof buffer, "\\x%02x", static_cast<unsigned>(c));
            out += buffer;
        } else {
            text::append_utf8(out, c);
        }
    }
    out += quote;
    return out;
}

}  // namespace

Value Value::of(std::string s) {
    Value value;
    value.kind = Kind::string;
    value.text = std::move(s);
    return value;
}

bool Value::truthy() const {
    switch (kind) {
    case Kind::null: return false;
    case Kind::boolean: return boolean;
    case Kind::integer: return text != "0";
    case Kind::real: return real != 0;
    case Kind::string: return !text.empty();
    case Kind::array: return !array.empty();
    case Kind::object: return !object.empty();
    }
    return false;
}

const Value* Value::find(std::string_view key) const {
    if (kind != Kind::object) return nullptr;
    for (const auto& [name, value] : object) {
        if (name == key) return &value;
    }
    return nullptr;
}

const Value& Value::get(std::string_view key) const {
    const Value* value = find(key);
    return value ? *value : null_value();
}

bool Value::present(std::string_view key) const {
    const Value& value = get(key);
    return !value.is_null() && !(value.is_string() && value.text.empty());
}

void Value::set(std::string key, Value value) {
    for (auto& [name, existing] : object) {
        if (name == key) {
            existing = std::move(value);
            return;
        }
    }
    object.emplace_back(std::move(key), std::move(value));
}

const Value& null_value() {
    static const Value null;
    return null;
}

Value parse(std::string_view text) { return Parser(text).document(); }

std::string dumps(const Value& value) {
    std::string out;
    dump(out, value);
    return out;
}

std::string float_repr(double value) {
    if (value == 0) return std::signbit(value) ? "-0.0" : "0.0";
    // Shortest round-trip digits, as Python's repr finds them, then Python's layout.
    char buffer[64];
    auto result = std::to_chars(buffer, buffer + sizeof buffer, value, std::chars_format::scientific);
    std::string sci(buffer, result.ptr);
    bool negative = sci[0] == '-';
    if (negative) sci.erase(0, 1);
    size_t e = sci.find('e');
    std::string digits = sci.substr(0, e);
    digits.erase(std::remove(digits.begin(), digits.end(), '.'), digits.end());
    int exponent = std::atoi(sci.c_str() + e + 1);
    while (digits.size() > 1 && digits.back() == '0') digits.pop_back();

    std::string out = negative ? "-" : "";
    if (exponent >= -4 && exponent < 16) {
        if (exponent >= 0) {
            std::string whole = digits.substr(0, std::min<size_t>(digits.size(), exponent + 1));
            whole.append(exponent + 1 - whole.size(), '0');
            std::string fraction = digits.size() > static_cast<size_t>(exponent + 1) ? digits.substr(exponent + 1) : "0";
            out += whole + "." + fraction;
        } else {
            out += "0." + std::string(-exponent - 1, '0') + digits;
        }
    } else {
        out += digits.substr(0, 1);
        if (digits.size() > 1) out += "." + digits.substr(1);
        char exp[8];
        std::snprintf(exp, sizeof exp, "e%c%02d", exponent < 0 ? '-' : '+', std::abs(exponent));
        out += exp;
    }
    return out;
}

std::string repr(const Value& value) {
    switch (value.kind) {
    case Value::Kind::null: return "None";
    case Value::Kind::boolean: return value.boolean ? "True" : "False";
    case Value::Kind::integer: return value.text;
    case Value::Kind::real: return float_repr(value.real);
    case Value::Kind::string: return repr_string(value.text);
    case Value::Kind::array: {
        std::string out = "[";
        for (size_t i = 0; i < value.array.size(); ++i) {
            if (i) out += ", ";
            out += repr(value.array[i]);
        }
        return out + "]";
    }
    case Value::Kind::object: {
        std::string out = "{";
        for (size_t i = 0; i < value.object.size(); ++i) {
            if (i) out += ", ";
            out += repr_string(value.object[i].first) + ": " + repr(value.object[i].second);
        }
        return out + "}";
    }
    }
    return {};
}

std::string str(const Value& value) {
    return value.is_string() ? value.text : repr(value);
}

}  // namespace json
