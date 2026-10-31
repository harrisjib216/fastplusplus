#include "text.hpp"

#include <cstdint>
#include <cstdio>

namespace text {

std::u32string decode(std::string_view utf8) {
    std::u32string out;
    out.reserve(utf8.size());
    for (size_t i = 0; i < utf8.size();) {
        unsigned char c = utf8[i];
        char32_t code;
        int extra;
        if (c < 0x80) {
            code = c;
            extra = 0;
        } else if ((c & 0xE0) == 0xC0) {
            code = c & 0x1F;
            extra = 1;
        } else if ((c & 0xF0) == 0xE0) {
            code = c & 0x0F;
            extra = 2;
        } else {
            code = c & 0x07;
            extra = 3;
        }
        ++i;
        for (int k = 0; k < extra && i < utf8.size(); ++k, ++i) code = (code << 6) | (utf8[i] & 0x3F);
        out += code;
    }
    return out;
}

void append_utf8(std::string& out, char32_t c) {
    if (c < 0x80) {
        out += static_cast<char>(c);
    } else if (c < 0x800) {
        out += static_cast<char>(0xC0 | (c >> 6));
        out += static_cast<char>(0x80 | (c & 0x3F));
    } else if (c < 0x10000) {
        out += static_cast<char>(0xE0 | (c >> 12));
        out += static_cast<char>(0x80 | ((c >> 6) & 0x3F));
        out += static_cast<char>(0x80 | (c & 0x3F));
    } else {
        out += static_cast<char>(0xF0 | (c >> 18));
        out += static_cast<char>(0x80 | ((c >> 12) & 0x3F));
        out += static_cast<char>(0x80 | ((c >> 6) & 0x3F));
        out += static_cast<char>(0x80 | (c & 0x3F));
    }
}

std::string encode(std::u32string_view code_points) {
    std::string out;
    out.reserve(code_points.size());
    for (char32_t c : code_points) append_utf8(out, c);
    return out;
}

bool valid_utf8(std::string_view bytes) {
    for (size_t i = 0; i < bytes.size();) {
        unsigned char c = bytes[i];
        if (c < 0x80) {
            ++i;
            continue;
        }
        int extra;
        char32_t smallest;
        if ((c & 0xE0) == 0xC0) extra = 1, smallest = 0x80;
        else if ((c & 0xF0) == 0xE0) extra = 2, smallest = 0x800;
        else if ((c & 0xF8) == 0xF0) extra = 3, smallest = 0x10000;
        else return false;
        char32_t code = c & (0x3F >> extra);
        for (int k = 1; k <= extra; ++k) {
            if (i + k >= bytes.size()) return false;
            unsigned char next = bytes[i + k];
            if ((next & 0xC0) != 0x80) return false;
            code = (code << 6) | (next & 0x3F);
        }
        // Overlong forms, surrogates and code points past U+10FFFF are errors, as in Python's decoder.
        if (code < smallest || code > 0x10FFFF || (code >= 0xD800 && code < 0xE000)) return false;
        i += extra + 1;
    }
    return true;
}

bool is_space(char32_t c) {
    return (c >= 0x09 && c <= 0x0D) || (c >= 0x1C && c <= 0x20) || c == 0x85 || c == 0xA0 || c == 0x1680
        || (c >= 0x2000 && c <= 0x200A) || c == 0x2028 || c == 0x2029 || c == 0x202F || c == 0x205F || c == 0x3000;
}

namespace {

char32_t lower_one(char32_t c) {
    if (c >= 'A' && c <= 'Z') return c + 32;
    if (c < 0x80) return c;
    // Latin-1 Supplement, except the multiplication sign.
    if ((c >= 0xC0 && c <= 0xDE) && c != 0xD7) return c + 32;
    // Latin Extended-A: mostly even uppercase, odd lowercase.
    if (c >= 0x100 && c <= 0x137 && c % 2 == 0) return c + 1;
    if (c >= 0x139 && c <= 0x148 && c % 2 == 1) return c + 1;
    if (c >= 0x14A && c <= 0x177 && c % 2 == 0) return c + 1;
    if (c == 0x178) return 0xFF;
    if (c >= 0x179 && c <= 0x17E && c % 2 == 1) return c + 1;
    // Greek and Cyrillic capitals.
    if (c >= 0x391 && c <= 0x3AB && c != 0x3A2) return c + 32;
    if (c >= 0x410 && c <= 0x42F) return c + 32;
    if (c >= 0x400 && c <= 0x40F) return c + 80;
    // Fullwidth Latin.
    if (c >= 0xFF21 && c <= 0xFF3A) return c + 32;
    return c;
}

}  // namespace

std::string lower(std::string_view s) {
    bool ascii = true;
    for (unsigned char c : s) {
        if (c >= 0x80) {
            ascii = false;
            break;
        }
    }
    if (ascii) {
        std::string out(s);
        for (char& c : out) {
            if (c >= 'A' && c <= 'Z') c = static_cast<char>(c + 32);
        }
        return out;
    }
    std::u32string code_points = decode(s);
    std::string out;
    for (char32_t c : code_points) {
        // U+0130 (İ) lowercases to "i" plus a combining dot above.
        if (c == 0x130) {
            out += 'i';
            append_utf8(out, 0x307);
        } else {
            append_utf8(out, lower_one(c));
        }
    }
    return out;
}

std::vector<std::string> split(std::string_view s) {
    std::vector<std::string> words;
    std::u32string code_points = decode(s);
    std::u32string word;
    for (char32_t c : code_points) {
        if (is_space(c)) {
            if (!word.empty()) words.push_back(encode(word)), word.clear();
        } else {
            word += c;
        }
    }
    if (!word.empty()) words.push_back(encode(word));
    return words;
}

std::string squeeze(std::string_view s) {
    std::string out;
    for (const auto& word : split(s)) {
        if (!out.empty()) out += ' ';
        out += word;
    }
    return out;
}

std::string strip(std::string_view s) {
    std::u32string code_points = decode(s);
    size_t start = 0;
    size_t end = code_points.size();
    while (start < end && is_space(code_points[start])) ++start;
    while (end > start && is_space(code_points[end - 1])) --end;
    return encode(std::u32string_view(code_points).substr(start, end - start));
}

std::string strip_chars(std::string_view s, std::string_view chars) {
    size_t start = s.find_first_not_of(chars);
    if (start == std::string_view::npos) return {};
    size_t end = s.find_last_not_of(chars);
    return std::string(s.substr(start, end - start + 1));
}

std::string rstrip_chars(std::string_view s, std::string_view chars) {
    size_t end = s.find_last_not_of(chars);
    return end == std::string_view::npos ? std::string() : std::string(s.substr(0, end + 1));
}

size_t length(std::string_view s) {
    size_t n = 0;
    for (unsigned char c : s) {
        if ((c & 0xC0) != 0x80) ++n;
    }
    return n;
}

std::string prefix(std::string_view s, size_t code_points) {
    size_t n = 0;
    for (size_t i = 0; i < s.size(); ++i) {
        if ((static_cast<unsigned char>(s[i]) & 0xC0) != 0x80) {
            if (n == code_points) return std::string(s.substr(0, i));
            ++n;
        }
    }
    return std::string(s);
}

bool starts_with(std::string_view s, std::string_view p) { return s.substr(0, p.size()) == p; }

std::string_view remove_prefix(std::string_view s, std::string_view p) {
    return starts_with(s, p) ? s.substr(p.size()) : s;
}

std::string replace_all(std::string s, std::string_view from, std::string_view to) {
    if (from.empty()) return s;
    std::string out;
    size_t pos = 0;
    while (true) {
        size_t hit = s.find(from, pos);
        if (hit == std::string::npos) break;
        out.append(s, pos, hit - pos);
        out += to;
        pos = hit + from.size();
    }
    out.append(s, pos, std::string::npos);
    return out;
}

size_t count(std::string_view s, char c) {
    size_t n = 0;
    for (char x : s) n += x == c;
    return n;
}

std::string group_thousands(long long n) {
    std::string digits = std::to_string(n < 0 ? -n : n);
    std::string out;
    for (size_t i = 0; i < digits.size(); ++i) {
        if (i && (digits.size() - i) % 3 == 0) out += ',';
        out += digits[i];
    }
    return n < 0 ? "-" + out : out;
}

bool is_ascii_digit(char c) { return c >= '0' && c <= '9'; }
bool is_ascii_lower_alnum(char c) { return (c >= 'a' && c <= 'z') || is_ascii_digit(c); }

std::string sha1_hex(std::string_view message) {
    uint32_t h[5] = {0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0xC3D2E1F0};
    std::string data(message);
    uint64_t bits = static_cast<uint64_t>(data.size()) * 8;
    data += static_cast<char>(0x80);
    while (data.size() % 64 != 56) data += '\0';
    for (int i = 7; i >= 0; --i) data += static_cast<char>((bits >> (i * 8)) & 0xFF);
    auto rotl = [](uint32_t x, int n) { return (x << n) | (x >> (32 - n)); };
    for (size_t chunk = 0; chunk < data.size(); chunk += 64) {
        uint32_t w[80];
        for (int i = 0; i < 16; ++i) {
            w[i] = (static_cast<uint32_t>(static_cast<unsigned char>(data[chunk + 4 * i])) << 24)
                | (static_cast<uint32_t>(static_cast<unsigned char>(data[chunk + 4 * i + 1])) << 16)
                | (static_cast<uint32_t>(static_cast<unsigned char>(data[chunk + 4 * i + 2])) << 8)
                | static_cast<uint32_t>(static_cast<unsigned char>(data[chunk + 4 * i + 3]));
        }
        for (int i = 16; i < 80; ++i) w[i] = rotl(w[i - 3] ^ w[i - 8] ^ w[i - 14] ^ w[i - 16], 1);
        uint32_t a = h[0], b = h[1], c = h[2], d = h[3], e = h[4];
        for (int i = 0; i < 80; ++i) {
            uint32_t f, k;
            if (i < 20) f = (b & c) | (~b & d), k = 0x5A827999;
            else if (i < 40) f = b ^ c ^ d, k = 0x6ED9EBA1;
            else if (i < 60) f = (b & c) | (b & d) | (c & d), k = 0x8F1BBCDC;
            else f = b ^ c ^ d, k = 0xCA62C1D6;
            uint32_t t = rotl(a, 5) + f + e + k + w[i];
            e = d, d = c, c = rotl(b, 30), b = a, a = t;
        }
        h[0] += a, h[1] += b, h[2] += c, h[3] += d, h[4] += e;
    }
    char out[41];
    std::snprintf(out, sizeof out, "%08x%08x%08x%08x%08x", h[0], h[1], h[2], h[3], h[4]);
    return out;
}

}  // namespace text
