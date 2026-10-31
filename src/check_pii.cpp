// Fails if tracked files carry personal data: a contributor's home-directory path to this checkout, a personal email
// address, or a credential. With --commits, also fails if any commit in the history of HEAD has a personal email
// address as its author or committer (commits use a GitHub noreply address).
//
// Prompts rendered on a personal machine embed the checkout's absolute path (agents need absolute output paths), so
// run this before committing them; --fix rewrites such paths to /path/to/<repo>. CI runs it on every push. Cloud
// container paths (/home/user, /home/claude) are not personal and are allowed.
//
// The three patterns are matched by hand rather than with <regex>, which is slow on the catalog's large files.
#include "check_pii.hpp"

#include <array>
#include <cstdio>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>
#include <vector>

#include "catalog.hpp"
#include "text.hpp"

namespace fs = std::filesystem;

namespace {

struct Match {
    size_t start;
    size_t end;
};

// The code point at `i` and its length in bytes.
std::pair<char32_t, size_t> at(std::string_view s, size_t i) {
    unsigned char c = s[i];
    if (c < 0x80) return {c, 1};
    size_t n = (c & 0xE0) == 0xC0 ? 2 : (c & 0xF0) == 0xE0 ? 3 : 4;
    char32_t code = c & (0x3F >> (n - 1));
    for (size_t k = 1; k < n && i + k < s.size(); ++k) code = (code << 6) | (s[i + k] & 0x3F);
    return {code, n};
}

// \w for a str pattern: letters, digits and underscore, in the scripts the data uses.
bool is_word(char32_t c) {
    if (c < 0x80) return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == '_';
    return (c >= 0xC0 && c <= 0x24F && c != 0xD7 && c != 0xF7) || (c >= 0x370 && c <= 0x52F) || (c >= 0x3040 && c <= 0x30FF)
        || (c >= 0x4E00 && c <= 0x9FFF) || (c >= 0xAC00 && c <= 0xD7AF);
}

// [^\s"'`]
bool is_path_char(char32_t c) { return !text::is_space(c) && c != '"' && c != '\'' && c != '`'; }

// /(?:Users|home)/(?!(?:user|claude)/)[^/\s"'`]+/(?:[^\s"'`]*/)?(fastpp)\b
std::vector<Match> home_paths(std::string_view s) {
    static constexpr std::string_view repo = "fastpp";
    std::vector<Match> out;
    for (size_t i = s.find('/'); i < s.size(); i = i < s.size() ? s.find('/', i) : i) {
        size_t p;
        if (s.compare(i, 7, "/Users/") == 0) p = i + 7;
        else if (s.compare(i, 6, "/home/") == 0) p = i + 6;
        else {
            ++i;
            continue;
        }
        if (s.compare(p, 5, "user/") == 0 || s.compare(p, 7, "claude/") == 0) {
            ++i;
            continue;
        }
        // The user's directory: one or more path characters other than '/', then '/'.
        size_t q = p;
        while (q < s.size() && s[q] != '/') {
            auto [c, n] = at(s, q);
            if (!is_path_char(c)) break;
            q += n;
        }
        if (q == p || q >= s.size() || s[q] != '/') {
            ++i;
            continue;
        }
        // Then the repository name right after some '/' in the run of path characters that follows; the greedy
        // optional group prefers the last one.
        size_t run_start = q + 1;
        size_t end = std::string_view::npos;
        size_t k = run_start;
        auto try_repo = [&](size_t at_pos) {
            if (s.compare(at_pos, repo.size(), repo) != 0) return;
            size_t after = at_pos + repo.size();
            if (after < s.size() && is_word(at(s, after).first)) return;
            end = after;
        };
        try_repo(run_start);
        while (k < s.size()) {
            auto [c, n] = at(s, k);
            if (!is_path_char(c)) break;
            if (c == '/') try_repo(k + 1);
            k += n;
        }
        if (end == std::string_view::npos) {
            ++i;
            continue;
        }
        out.push_back({i, end});
        i = end;
    }
    return out;
}

bool is_local_char(char c) {
    return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == '.' || c == '_' || c == '%'
        || c == '+' || c == '-';
}

bool is_letter_or_dot(char c) { return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || c == '.'; }

// The end of (?:gmail|...|aol)\.[a-z.]+ (case-insensitive) starting at `p`, or npos.
size_t email_domain_end(std::string_view s, size_t p) {
    static constexpr std::array<std::string_view, 11> providers = {
        "gmail", "googlemail", "outlook", "hotmail", "live", "icloud", "me", "yahoo", "proton", "protonmail", "aol"};
    for (std::string_view provider : providers) {
        if (p + provider.size() > s.size()) continue;
        if (text::lower(s.substr(p, provider.size())) != provider) continue;
        size_t dot = p + provider.size();
        if (dot >= s.size() || s[dot] != '.') continue;
        size_t end = dot + 1;
        while (end < s.size() && is_letter_or_dot(s[end])) ++end;
        if (end > dot + 1) return end;
    }
    return std::string_view::npos;
}

// [A-Za-z0-9._%+-]+@(?:gmail|googlemail|outlook|hotmail|live|icloud|me|yahoo|proton|protonmail|aol)\.[a-z.]+, re.I
std::vector<Match> personal_emails(std::string_view s) {
    std::vector<Match> out;
    // The leftmost match ends its local part at some '@': from each '@', back up over the local part, but not into
    // the previous match.
    for (size_t i = 0, at_sign; (at_sign = s.find('@', i)) != std::string_view::npos;) {
        size_t start = at_sign;
        while (start > i && is_local_char(s[start - 1])) --start;
        size_t end = start < at_sign ? email_domain_end(s, at_sign + 1) : std::string_view::npos;
        if (end == std::string_view::npos) {
            i = at_sign + 1;
            continue;
        }
        out.push_back({start, end});
        i = end;
    }
    return out;
}

bool is_personal_email(std::string_view s) {
    size_t at_sign = s.find('@');
    if (at_sign == 0 || at_sign == std::string_view::npos) return false;
    for (size_t i = 0; i < at_sign; ++i) {
        if (!is_local_char(s[i])) return false;
    }
    return email_domain_end(s, at_sign + 1) == s.size();
}

template <typename Accept>
size_t run_end(std::string_view s, size_t p, Accept accept) {
    while (p < s.size() && accept(s[p])) ++p;
    return p;
}

// ghp_ tokens, fine-grained PATs, Anthropic keys, AWS access key ids, Slack tokens and PEM private keys.
std::vector<Match> credentials(std::string_view s) {
    auto alnum = [](char c) { return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9'); };
    auto alnum_underscore = [&](char c) { return alnum(c) || c == '_'; };
    auto alnum_dash = [&](char c) { return alnum(c) || c == '-'; };
    auto upper_digit = [](char c) { return (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9'); };
    auto upper_space = [](char c) { return (c >= 'A' && c <= 'Z') || c == ' '; };

    auto match_at = [&](size_t i) -> size_t {
        auto token = [&](std::string_view lead, auto accept, size_t minimum) -> size_t {
            if (s.compare(i, lead.size(), lead) != 0) return std::string_view::npos;
            size_t start = i + lead.size();
            size_t end = run_end(s, start, accept);
            return end - start >= minimum ? end : std::string_view::npos;
        };
        if (size_t end = token("ghp_", alnum, 20); end != std::string_view::npos) return end;
        if (size_t end = token("github_pat_", alnum_underscore, 20); end != std::string_view::npos) return end;
        if (size_t end = token("sk-ant-", alnum_dash, 10); end != std::string_view::npos) return end;
        if (s.compare(i, 4, "AKIA") == 0 && i + 20 <= s.size()) {
            bool ok = true;
            for (size_t k = i + 4; k < i + 20; ++k) ok = ok && upper_digit(s[k]);
            if (ok) return i + 20;
        }
        if (s.compare(i, 3, "xox") == 0 && i + 4 < s.size() && (s[i + 3] == 'b' || s[i + 3] == 'p' || s[i + 3] == 'a') && s[i + 4] == '-') {
            size_t start = i + 5;
            size_t end = run_end(s, start, alnum_dash);
            if (end - start >= 10) return end;
        }
        static constexpr std::string_view begin = "-----BEGIN ";
        static constexpr std::string_view key = "PRIVATE KEY";
        if (s.compare(i, begin.size(), begin) == 0) {
            size_t start = i + begin.size();
            size_t end = run_end(s, start, upper_space);
            std::string_view run = s.substr(start, end - start);
            size_t last = run.rfind(key);
            if (last != std::string_view::npos) return start + last + key.size();
        }
        return std::string_view::npos;
    };

    std::vector<Match> out;
    for (size_t i = s.find_first_of("gsAx-"); i < s.size(); i = i < s.size() ? s.find_first_of("gsAx-", i) : i) {
        size_t end = match_at(i);
        if (end == std::string_view::npos) {
            ++i;
            continue;
        }
        out.push_back({i, end});
        i = end;
    }
    return out;
}

std::string shell_quote(const std::string& s) { return "'" + text::replace_all(s, "'", "'\\''") + "'"; }

std::string run(const std::string& command) {
    std::unique_ptr<FILE, int (*)(FILE*)> pipe(popen(command.c_str(), "r"), pclose);
    if (!pipe) throw std::runtime_error("can't run " + command);
    std::string out;
    std::array<char, 65536> buffer;
    size_t n;
    while ((n = fread(buffer.data(), 1, buffer.size(), pipe.get())) > 0) out.append(buffer.data(), n);
    int status = pclose(pipe.release());
    if (status != 0) throw std::runtime_error(command + " failed");
    return out;
}

// What Python's read_text() sees: universal newlines.
std::string universal_newlines(const std::string& raw) {
    if (raw.find('\r') == std::string::npos) return raw;
    std::string out;
    out.reserve(raw.size());
    for (size_t i = 0; i < raw.size(); ++i) {
        if (raw[i] == '\r') {
            out += '\n';
            if (i + 1 < raw.size() && raw[i + 1] == '\n') ++i;
        } else {
            out += raw[i];
        }
    }
    return out;
}

}  // namespace

int check_pii(const fs::path& root, bool commits, bool fix) {
    std::vector<std::string> problems;
    std::string git = "git -C " + shell_quote(root.string());
    if (commits) {
        std::string log = run(git + " log --format='%h %ae %ce' HEAD");
        size_t start = 0;
        while (start < log.size()) {
            size_t end = log.find('\n', start);
            if (end == std::string::npos) end = log.size();
            std::vector<std::string> fields = text::split(std::string_view(log).substr(start, end - start));
            start = end + 1;
            if (fields.empty()) continue;
            bool personal = false;
            for (size_t i = 1; i < fields.size(); ++i) personal = personal || is_personal_email(fields[i]);
            if (personal) problems.push_back("commit " + fields[0] + ": personal email address as author or committer");
        }
    }

    std::string listing = run(git + " ls-files -z");
    size_t start = 0;
    while (start < listing.size()) {
        size_t end = listing.find('\0', start);
        if (end == std::string::npos) end = listing.size();
        std::string name = listing.substr(start, end - start);
        start = end + 1;
        if (name.empty()) continue;
        fs::path path = root / name;
        std::error_code error;
        if (!fs::is_regular_file(path, error)) continue;
        std::string raw;
        try {
            raw = read_file(path);
        } catch (const std::runtime_error&) {
            continue;
        }
        if (!text::valid_utf8(raw)) continue;
        std::string content = universal_newlines(raw);

        if (fix) {
            std::vector<Match> found = home_paths(content);
            if (!found.empty()) {
                std::string fixed;
                size_t from = 0;
                for (const Match& m : found) {
                    fixed.append(content, from, m.start - from);
                    fixed += "/path/to/fastpp";
                    from = m.end;
                }
                fixed.append(content, from, std::string::npos);
                content = std::move(fixed);
                write_file(path, content);
            }
        }
        const std::pair<const char*, std::vector<Match> (*)(std::string_view)> kinds[] = {
            {"home path", home_paths}, {"personal email", personal_emails}, {"credential", credentials}};
        for (const auto& [kind, find] : kinds) {
            for (const Match& m : find(content)) {
                size_t line = 1 + text::count(std::string_view(content).substr(0, m.start), '\n');
                problems.push_back(name + ":" + std::to_string(line) + ": " + kind);
            }
        }
    }

    for (size_t i = 0; i < problems.size() && i < 50; ++i) std::cout << problems[i] << "\n";
    if (!problems.empty()) {
        std::cout.flush();
        std::cerr << problems.size() << " finding(s); home paths can be fixed with --fix\n";
        return 1;
    }
    std::cout << "check-pii: clean\n";
    return 0;
}
