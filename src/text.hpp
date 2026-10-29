// UTF-8 text with Python's str semantics where the catalog depends on them: lengths and slices count code points,
// whitespace is Unicode whitespace, and lowercasing covers the scripts the data uses.
#pragma once

#include <string>
#include <string_view>
#include <vector>

namespace text {

std::u32string decode(std::string_view utf8);
std::string encode(std::u32string_view code_points);
void append_utf8(std::string& out, char32_t code_point);
// Whether `bytes` is valid UTF-8, the test Python applies when reading a text file.
bool valid_utf8(std::string_view bytes);

// str.isspace() for one code point.
bool is_space(char32_t c);
// str.lower().
std::string lower(std::string_view s);
// " ".join(s.split()): runs of whitespace become one space, ends trimmed.
std::string squeeze(std::string_view s);
// s.split() with no arguments.
std::vector<std::string> split(std::string_view s);
// s.strip() with no arguments.
std::string strip(std::string_view s);
// s.strip(chars), s.lstrip(chars) and s.rstrip(chars) for ASCII `chars`.
std::string strip_chars(std::string_view s, std::string_view chars);
std::string rstrip_chars(std::string_view s, std::string_view chars);
// len(s) and s[:n], in code points.
size_t length(std::string_view s);
std::string prefix(std::string_view s, size_t code_points);

bool starts_with(std::string_view s, std::string_view prefix);
std::string_view remove_prefix(std::string_view s, std::string_view prefix);
std::string replace_all(std::string s, std::string_view from, std::string_view to);
size_t count(std::string_view s, char c);
// f"{n:,}".
std::string group_thousands(long long n);
// hashlib.sha1(s).hexdigest().
std::string sha1_hex(std::string_view s);

bool is_ascii_digit(char c);
bool is_ascii_lower_alnum(char c);

}  // namespace text
