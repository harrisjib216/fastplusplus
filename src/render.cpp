// Renders the catalog from every wave's verified.json, the enrichment records and data/decisions.json:
//
//   catalog/README.md                          index of domains
//   catalog/<domain>/README.md                 one page per domain: its categories and top picks
//   catalog/<domain>/<category>/README.md      one page per category: ranked table of entries
//   catalog/<domain>/<category>/<entry>.md     one page per entry
//   catalog/rejected.md                        candidates whose evidence did not hold up
//   catalog/catalog.jsonl, catalog/catalog.csv machine-readable exports (schema: docs/schema.md)
//   README.md                                  only the blocks between <!-- fastpp:NAME --> and <!-- /fastpp:NAME -->
//
// The output is deterministic, so CI renders again and fails when the committed files differ.
#include "render.hpp"

#include <algorithm>
#include <cstdlib>
#include <filesystem>
#include <iostream>
#include <map>
#include <set>
#include <stdexcept>
#include <tuple>

#include "catalog.hpp"
#include "json.hpp"
#include "text.hpp"

namespace fs = std::filesystem;
using json::Value;

namespace {

const std::map<std::string, int, std::less<>> tier_rank = {{"A", 0}, {"B", 1}, {"C", 2}, {"D", 3}};
const std::map<std::string, std::string, std::less<>> tier_text = {
    {"A", "reproducible public benchmark"}, {"B", "independent or peer-reviewed measurement"},
    {"C", "first-party claim"}, {"D", "directional, no numbers"}};
const std::map<std::string, int, std::less<>> status_rank = {{"active", 0}, {"finished", 1}, {"slow", 2}, {"mixed", 2},
                                                              {"stale", 3}, {"unknown", 4}, {"abandoned", 5}};
const std::map<std::string, std::string, std::less<>> status_icon = {
    {"active", "🟢"}, {"finished", "🔵"}, {"slow", "🟡"}, {"mixed", "🟡"}, {"stale", "🟡"}, {"unknown", "⚪"},
    {"abandoned", "🔴"}};
const std::string legend =
    "<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent "
    "or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. "
    "Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. "
    "*Study only* means no usable open-source license: read the idea, don't copy the code.</sub>";
const char* const tiers[] = {"A", "B", "C", "D"};

// ---------------------------------------------------------------- text helpers

// str(value or ""): what an f-string shows for a value that might be missing.
std::string text_of(const Value& value) { return value.truthy() ? json::str(value) : std::string(); }

// A slug of letters and digits: every other run of characters becomes `separator`, then the ends are trimmed.
std::string slug(std::string_view s, char separator) {
    std::string out;
    bool gap = false;
    for (char c : s) {
        if (text::is_ascii_lower_alnum(c)) {
            if (gap) out += separator;
            gap = false;
            out += c;
        } else {
            gap = true;
        }
    }
    if (gap && !out.empty()) out += separator;
    return text::strip_chars(out, std::string(1, separator));
}

// File name of an entry's enrichment record (data/waveN/enrich/raw/<slug>.json). It doesn't lowercase: capitals
// become underscores, as the pipeline that wrote the files did.
std::string enrich_slug(std::string_view id) { return slug(text::remove_prefix(id, "https://"), '_'); }

std::string page_slug(std::string_view id) {
    std::string_view s = text::remove_prefix(id, "https://");
    s = text::remove_prefix(s, "http://");
    s = text::remove_prefix(s, "github.com/");
    std::string out = slug(text::lower(s), '-');
    if (out.size() > 80) out = text::rstrip_chars(out.substr(0, 70), "-") + "-" + text::sha1_hex(id).substr(0, 8);
    return out;
}

void translate_prose(std::string& out, std::string_view s) {
    for (char c : s) {
        switch (c) {
        case '<': out += "&lt;"; break;
        case '>': out += "&gt;"; break;
        case '*': out += "\\*"; break;
        case '~': out += "\\~"; break;
        case '$': out += "\\$"; break;
        default: out += c;
        }
    }
}

// Data prose to Markdown. Outside code spans, escape what GitHub would otherwise act on: unknown HTML tags are
// dropped, single tildes strike through ("~2x ... ~3x"), dollar pairs become math, asterisks emphasis.
std::string esc(std::string_view raw) {
    std::string s = text::replace_all(std::string(raw), "\r", "");
    std::string out;
    size_t i = 0;
    while (i < s.size()) {
        size_t open = s.find('`', i);
        if (open == std::string::npos) {
            translate_prose(out, std::string_view(s).substr(i));
            break;
        }
        size_t close = s.find_first_of("`\n", open + 1);
        if (close != std::string::npos && s[close] == '`') {
            translate_prose(out, std::string_view(s).substr(i, open - i));
            out.append(s, open, close + 1 - open);
            i = close + 1;
        } else {
            translate_prose(out, std::string_view(s).substr(i, open + 1 - i));
            i = open + 1;
        }
    }
    return out;
}

std::string esc(const Value& value) { return esc(text_of(value)); }

std::string trunc(const std::string& raw, size_t limit = 0) {
    std::string t = text::squeeze(raw);
    if (limit && text::length(t) > limit) {
        t = text::prefix(t, limit);
        size_t space = t.rfind(' ');
        if (space != std::string::npos) t = t.substr(0, space);
        t = text::rstrip_chars(t, ",;:.") + "…";
        if (text::count(t, '`') % 2) t = text::replace_all(t, "`", "");
    }
    return t;
}

std::string cell(const std::string& raw, size_t limit = 0) {
    return text::replace_all(esc(trunc(raw, limit)), "|", "\\|");
}

std::string cell(const Value& value, size_t limit = 0) { return cell(text_of(value), limit); }

bool has_link_break(std::string_view u) {
    for (char32_t c : text::decode(u)) {
        if (text::is_space(c) || c == '(' || c == ')' || c == '<' || c == '>') return true;
    }
    return false;
}

std::string url(const std::string& raw) {
    std::string u = text::strip(raw);
    return has_link_break(u) ? "<" + u + ">" : u;
}

bool is_web(std::string_view u) { return text::starts_with(u, "http://") || text::starts_with(u, "https://"); }

// re.match(r"[a-z][a-z0-9+.-]*:", s)
bool has_scheme(std::string_view s) {
    if (s.empty() || s[0] < 'a' || s[0] > 'z') return false;
    size_t i = 1;
    while (i < s.size() && (text::is_ascii_lower_alnum(s[i]) || s[i] == '+' || s[i] == '.' || s[i] == '-')) ++i;
    return i < s.size() && s[i] == ':';
}

// Markdown link; ids with a non-web scheme (private:, paper:) stay plain text.
std::string link(const std::string& label, const std::string& target) {
    if (target.empty() || (has_scheme(target) && !is_web(target))) return label;
    return "[" + label + "](" + url(target) + ")";
}

std::string link(const std::string& label, const Value& target) { return link(label, text_of(target)); }

// The items of a list, the characters of a string, or the keys of an object, as Python iterates them.
std::vector<Value> items(const Value& value) {
    std::vector<Value> out;
    if (value.is_array()) return value.array;
    if (value.is_string()) {
        for (char32_t c : text::decode(value.text)) {
            std::string one;
            text::append_utf8(one, c);
            out.push_back(Value::of(one));
        }
    } else if (value.is_object()) {
        for (const auto& [key, _] : value.object) out.push_back(Value::of(key));
    }
    return out;
}

std::string bullets(const Value& list) {
    std::string out;
    for (const Value& item : items(list)) {
        if (text::strip(json::str(item)).empty()) continue;
        if (!out.empty()) out += '\n';
        out += "- " + esc(item);
    }
    return out;
}

std::string yes_no(const Value& value) {
    bool one = (value.is_bool() && value.boolean) || (value.kind == Value::Kind::integer && value.text == "1")
        || (value.kind == Value::Kind::real && value.real == 1);
    bool zero = (value.is_bool() && !value.boolean) || (value.kind == Value::Kind::integer && value.text == "0")
        || (value.kind == Value::Kind::real && value.real == 0);
    return one ? "yes" : zero ? "no" : "not stated";
}

std::string join(const std::vector<std::string>& parts, std::string_view separator) {
    std::string out;
    for (size_t i = 0; i < parts.size(); ++i) {
        if (i) out += separator;
        out += parts[i];
    }
    return out;
}

// ---------------------------------------------------------------- entry facts

struct Entry {
    Value record;      // the verified record, with the category alias applied
    Value enrichment;  // the enrichment record
    std::string record_path;
    std::string enrichment_path;
    std::string page;

    const Value& get(std::string_view key) const { return record.get(key); }
    std::string id() const { return text_of(get("id")); }
    std::string name() const { return text_of(get("name")); }
    std::string domain() const { return text_of(get("domain")); }
    std::string category() const { return text_of(get("category")); }
    std::string tier() const { return text_of(get("evidence_tier")); }
};

std::string status(const Entry& e) {
    const Value& raw = e.get("maintenance_status");
    std::string s = text::lower(text::strip(raw.truthy() ? json::str(raw) : "unknown"));
    std::u32string code_points = text::decode(s);
    size_t end = 0;
    while (end < code_points.size()) {
        char32_t c = code_points[end];
        if (text::is_space(c) || c == ':' || c == ';' || c == ',' || c == '(') break;
        ++end;
    }
    std::string word = text::encode(std::u32string_view(code_points).substr(0, end));
    return status_rank.count(word) ? word : "unknown";
}

// The first "<number>[kM] [GitHub] stars" in stars_or_usage, as a count.
long long stars(const Entry& e) {
    std::string s = text_of(e.get("stars_or_usage"));
    for (size_t start = 0; start < s.size(); ++start) {
        if (!text::is_ascii_digit(s[start])) continue;
        size_t i = start + 1;
        while (i < s.size() && (text::is_ascii_digit(s[i]) || s[i] == ',' || s[i] == '.')) ++i;
        std::string number = text::replace_all(s.substr(start, i - start), ",", "");
        auto skip_space = [&](size_t j) {
            while (j < s.size()) {
                size_t step = 1;
                char32_t c = static_cast<unsigned char>(s[j]);
                if (c >= 0x80) {
                    std::u32string one = text::decode(s.substr(j, 4));
                    c = one.empty() ? 0 : one[0];
                    step = c < 0x800 ? 2 : c < 0x10000 ? 3 : 4;
                }
                if (!text::is_space(c)) break;
                j += step;
            }
            return j;
        };
        size_t j = skip_space(i);
        double multiplier = 1;
        if (j < s.size() && (s[j] == 'k' || s[j] == 'K')) multiplier = 1e3, ++j;
        else if (j < s.size() && (s[j] == 'm' || s[j] == 'M')) multiplier = 1e6, ++j;
        if (j < s.size() && s[j] == '+') ++j;
        j = skip_space(j);
        size_t after_github = std::string::npos;
        if (s.compare(j, 6, "GitHub") == 0) {
            size_t k = skip_space(j + 6);
            if (k > j + 6) after_github = k;
        }
        auto matches_stars = [&](size_t k) { return s.compare(k, 5, "stars") == 0; };
        if ((after_github != std::string::npos && matches_stars(after_github)) || matches_stars(j)) {
            return static_cast<long long>(std::strtod(number.c_str(), nullptr) * multiplier);
        }
    }
    return 0;
}

std::string lang_short(const Entry& e) {
    const Value& raw = e.get("language");
    std::string lang = text::strip(raw.truthy() ? json::str(raw) : "?");
    // re.split(r"\s*\(|;|, | with | plus ", lang, maxsplit=1)[0]: cut where the earliest separator starts. A
    // parenthesis takes the whitespace before it.
    std::u32string code_points = text::decode(lang);
    size_t cut = code_points.size();
    if (size_t paren = code_points.find(U'('); paren != std::u32string::npos) {
        while (paren > 0 && text::is_space(code_points[paren - 1])) --paren;
        cut = paren;
    }
    for (std::u32string_view separator : {U";", U", ", U" with ", U" plus "}) {
        cut = std::min(cut, std::u32string_view(code_points).find(separator));
    }
    std::string head = text::encode(std::u32string_view(code_points).substr(0, cut));
    std::string out = text::prefix(text::strip(head), 24);
    return out.empty() ? "?" : out;
}

bool copyable(const Entry& e) {
    const Value& usability = e.get("usability");
    return usability.is_string() && usability.text == "copyable";
}

std::string license_cell(const Entry& e) {
    const Value& raw = e.get("license");
    std::string lic = cell(raw.truthy() ? json::str(raw) : "no license", 28);
    return copyable(e) ? lic : lic + " (study only)";
}

std::string links_cell(const Entry& e) {
    std::vector<std::string> parts;
    for (auto [label, key] : {std::pair{"repository", "repo_url"}, std::pair{"benchmark", "benchmark_url"}}) {
        std::string u = text_of(e.get(key));
        if (!u.empty() && is_web(u)) parts.push_back(link(label, u));
    }
    if (!parts.empty()) return join(parts, " · ");
    return text::starts_with(text_of(e.get("repo_url")), "private:") ? "private repository, not published yet"
                                                                      : "paper only";
}

bool rank_before(const Entry& a, const Entry& b) {
    auto key = [](const Entry& e) {
        return std::tuple(tier_rank.at(e.tier()), !copyable(e), status_rank.at(status(e)), -stars(e), text::lower(e.name()));
    };
    return key(a) < key(b);
}

// ---------------------------------------------------------------- loading

struct Loaded {
    std::vector<Entry> entries;
    std::vector<std::string> missing;
    std::vector<std::string> dropped;
};

std::vector<fs::path> waves(const fs::path& data) {
    std::vector<fs::path> out;
    for (const auto& item : fs::directory_iterator(data)) {
        if (item.is_directory() && text::starts_with(item.path().filename().string(), "wave")) out.push_back(item.path());
    }
    std::sort(out.begin(), out.end(), [](const fs::path& a, const fs::path& b) { return a.filename().string() < b.filename().string(); });
    return out;
}

Loaded load_entries(const Catalog& catalog) {
    Loaded loaded;
    std::map<std::string, size_t> seen;
    for (const fs::path& wave : waves(catalog.data)) {
        fs::path verified = wave / "verified.json";
        if (!fs::exists(verified)) continue;
        Value records = json::parse(read_file(verified));
        for (Value& record : records.array) {
            std::string id = text_of(record.get("id"));
            fs::path enrichment = wave / "enrich" / "raw" / (enrich_slug(id) + ".json");
            if (!fs::exists(enrichment)) {
                loaded.missing.push_back(text_of(record.get("name")));
                continue;
            }
            Entry e;
            e.enrichment = json::parse(read_file(enrichment));
            e.record_path = fs::relative(verified, catalog.root).generic_string();
            e.enrichment_path = fs::relative(enrichment, catalog.root).generic_string();
            std::string category = text_of(record.get("category"));
            if (auto alias = catalog.category_aliases.find(category); alias != catalog.category_aliases.end()) {
                record.set("category", Value::of(alias->second));
            }
            e.record = std::move(record);
            if (!catalog.has_domain(e.domain()) || !catalog.category_titles.count(e.category())) {
                throw std::runtime_error("no display title for " + e.domain() + "/" + e.category() + " (" + id
                                         + "): add it to data/catalog_meta.json");
            }
            if (auto earlier = seen.find(id); earlier != seen.end()) {
                // One id verified in two waves: keep the earlier verification.
                Entry& kept = loaded.entries[earlier->second];
                auto order = [](const Entry& r) {
                    const Value& date = r.get("verification").get("date");
                    return std::pair(date.is_null() && !r.get("verification").find("date") ? std::string() : json::str(date), r.record_path);
                };
                loaded.dropped.push_back(id + " (" + kept.record_path + " / " + e.record_path + ")");
                if (order(e) < order(kept)) kept = std::move(e);
                continue;
            }
            seen[id] = loaded.entries.size();
            loaded.entries.push_back(std::move(e));
        }
    }
    std::vector<Entry*> by_id;
    for (Entry& e : loaded.entries) by_id.push_back(&e);
    std::stable_sort(by_id.begin(), by_id.end(), [](const Entry* a, const Entry* b) { return a->id() < b->id(); });
    std::map<std::pair<std::string, std::string>, std::set<std::string>> used;
    for (Entry* e : by_id) {
        std::string base = page_slug(e->id());
        std::string s = base;
        auto& taken = used[{e->domain(), e->category()}];
        for (int n = 2; taken.count(s) || s == "readme"; ++n) s = base + "-" + std::to_string(n);
        taken.insert(s);
        e->page = "catalog/" + e->domain() + "/" + e->category() + "/" + s + ".md";
    }
    return loaded;
}

// Category -> (baselines, languages, where they win) from the spec's Part 3 and Part 4 tables.
std::map<std::string, std::vector<std::string>> spec_baselines(const Catalog& catalog) {
    std::map<std::string, std::vector<std::string>> out;
    std::string spec = read_file(catalog.root / "pipeline" / "spec.md");
    size_t start = 0;
    while (start <= spec.size()) {
        size_t end = spec.find('\n', start);
        if (end == std::string::npos) end = spec.size();
        std::string_view line(spec.data() + start, end - start);
        if (!line.empty() && line.back() == '\r') line.remove_suffix(1);
        start = end + 1;
        if (!text::starts_with(line, "| ")) continue;
        std::string trimmed = text::strip_chars(text::strip(line), "|");
        std::vector<std::string> cols;
        size_t from = 0;
        while (true) {
            size_t bar = trimmed.find('|', from);
            cols.push_back(text::strip(std::string_view(trimmed).substr(from, bar == std::string::npos ? std::string::npos : bar - from)));
            if (bar == std::string::npos) break;
            from = bar + 1;
        }
        bool slug_like = !cols[0].empty()
            && std::all_of(cols[0].begin(), cols[0].end(), [](char c) { return text::is_ascii_lower_alnum(c) || c == '-'; });
        if (cols.size() >= 2 && slug_like) out[cols[0]] = std::vector<std::string>(cols.begin() + 1, cols.end());
    }
    return out;
}

using Spec = std::map<std::string, std::vector<std::string>>;

std::string what_they_beat(const Catalog& catalog, const std::string& domain, const std::string& category,
                           const std::vector<const Entry*>& members, const Spec& spec) {
    if (domain == catalog.cross_language_domain) return catalog.cross_language_baseline;
    if (auto row = spec.find(category); row != spec.end() && !text::starts_with(row->second[0], "(")) {
        return row->second[0];
    }
    // Counter.most_common(3): by count, ties in order of first appearance.
    std::vector<std::pair<std::string, int>> counts;
    for (const Entry* e : members) {
        std::string baseline = trunc(text_of(e->get("baseline")), 60);
        auto hit = std::find_if(counts.begin(), counts.end(), [&](const auto& c) { return c.first == baseline; });
        if (hit == counts.end()) counts.emplace_back(baseline, 1);
        else ++hit->second;
    }
    std::stable_sort(counts.begin(), counts.end(), [](const auto& a, const auto& b) { return a.second > b.second; });
    std::vector<std::string> top;
    for (size_t i = 0; i < counts.size() && i < 3; ++i) top.push_back(counts[i].first);
    return join(top, "; ");
}

// ---------------------------------------------------------------- pages

std::vector<std::string> parts(std::string_view path) {
    std::vector<std::string> out;
    size_t start = 0;
    while (start <= path.size()) {
        size_t end = path.find('/', start);
        if (end == std::string_view::npos) end = path.size();
        std::string_view part = path.substr(start, end - start);
        if (!part.empty() && part != ".") out.emplace_back(part);
        start = end + 1;
    }
    return out;
}

std::string parent(std::string_view path) {
    size_t slash = path.rfind('/');
    return slash == std::string_view::npos ? "." : std::string(path.substr(0, slash));
}

// Relative link from one repo file to another.
std::string rel(std::string_view from_page, std::string_view to_path) {
    std::vector<std::string> a = parts(parent(from_page));
    std::vector<std::string> b = parts(to_path);
    size_t i = 0;
    while (i < a.size() && i < b.size() && a[i] == b[i]) ++i;
    std::vector<std::string> out(a.size() - i, "..");
    out.insert(out.end(), b.begin() + i, b.end());
    std::string joined = join(out, "/");
    return joined.empty() ? "." : joined;
}

std::string crumbs(std::string_view page, const std::vector<std::pair<std::string, std::string>>& trail) {
    std::vector<std::string> links;
    for (const auto& [label, path] : trail) links.push_back(link(label, rel(page, path)));
    return "<sub>" + join(links, " › ") + "</sub>";
}

std::map<std::string, int> tier_counts(const std::vector<const Entry*>& es) {
    std::map<std::string, int> counts = {{"A", 0}, {"B", 0}, {"C", 0}, {"D", 0}};
    for (const Entry* e : es) {
        if (counts.count(e->tier())) ++counts[e->tier()];
    }
    return counts;
}

std::string tier_summary(const std::map<std::string, int>& t, bool grouped = false) {
    std::vector<std::string> out;
    for (const char* k : tiers) out.push_back((grouped ? text::group_thousands(t.at(k)) : std::to_string(t.at(k))) + " tier " + k);
    return join(out, " · ");
}

class Renderer {
public:
    Renderer(const Catalog& catalog, std::map<std::string, Value> decisions)
        : catalog_(catalog), decisions_(std::move(decisions)) {}

    const Value& decision(const std::string& id) const {
        auto hit = decisions_.find(id);
        return hit == decisions_.end() ? json::null_value() : hit->second;
    }

    size_t decision_count() const { return decisions_.size(); }

    std::string entry_table(const std::string& page, const std::vector<const Entry*>& es, bool with_category = false) const {
        std::vector<std::string> rows = {
            "| # | Project | What it is | " + std::string(with_category ? "Category | " : "") + "Tier | Language | License | Status |",
            "|--:|---|---|" + std::string(with_category ? "---|" : "") + ":-:|---|---|---|"};
        int i = 0;
        for (const Entry* e : es) {
            ++i;
            std::string category;
            if (with_category) {
                category = " " + link(cell(catalog_.category_titles.at(e->category())), rel(page, parent(e->page) + "/README.md")) + " |";
            }
            rows.push_back("| " + std::to_string(i) + " | " + link("**" + cell(e->name(), 60) + "**", rel(page, e->page)) + " | "
                           + cell(e->enrichment.get("one_liner"), 170) + " |" + category + " **" + e->tier() + "** | "
                           + cell(lang_short(*e)) + " | " + license_cell(*e) + " | " + status_icon.at(status(*e)) + " " + status(*e) + " |");
        }
        return join(rows, "\n");
    }

    std::string render_entry(const Entry& e) const {
        const Value& x = e.enrichment;
        const std::string& page = e.page;
        std::string d = e.domain(), c = e.category();
        const Value& v = e.get("verification");
        const Value& dec = decision(e.id());
        const Value& language = e.get("language");
        const Value& license = e.get("license");
        std::vector<std::string> out = {
            "# " + esc(e.get("name")),
            crumbs(page, {{"fastpp", "README.md"}, {"Catalog", "catalog/README.md"}, {catalog_.domain_title(d), "catalog/" + d + "/README.md"},
                          {catalog_.category_titles.at(c), "catalog/" + d + "/" + c + "/README.md"}}),
            "**Tier " + e.tier() + "** (" + tier_text.at(e.tier()) + ") · " + (copyable(e) ? "Copyable" : "Study only") + " · `"
                + esc(language.truthy() ? json::str(language) : "?") + "` · `" + esc(license.truthy() ? json::str(license) : "no license")
                + "` · " + status_icon.at(status(e)) + " " + status(e),
            "> " + esc(x.get("one_liner"))};

        std::vector<std::pair<std::string, Value>> facts = {
            {"Beats", e.get("baseline")}, {"Claimed result", e.get("claimed_speedup")}, {"Workload", e.get("workload")},
            {"Metric", e.get("metric")}, {"Hardware", e.get("hardware")}, {"Compiler and flags", e.get("compiler_and_flags")}};
        if (d == catalog_.cross_language_domain) {
            facts.push_back({"Kind", Value::of(e.get("language_level_claim").truthy() ? "language-level claim" : "library or program")});
            facts.push_back({"Same algorithm as the baseline", Value::of(yes_no(e.get("same_algorithm")))});
            facts.push_back({"Same optimization level", Value::of(yes_no(e.get("same_opt_level")))});
            facts.push_back({"Why it wins", e.get("why_faster")});
        }
        facts.push_back({"Adoption", e.get("stars_or_usage")});
        facts.push_back({"Last commit", e.get("last_commit")});
        facts.push_back({"Links", Value::of(links_cell(e))});
        std::vector<std::string> rows;
        for (const auto& [k, value] : facts) {
            if (value.is_null() || (value.is_string() && value.text.empty())) continue;
            rows.push_back("| **" + k + "** | " + (k == "Links" ? value.text : cell(value)) + " |");
        }
        out.push_back("| | |\n|---|---|\n" + join(rows, "\n"));

        std::vector<std::pair<std::string, std::string>> sections = {
            {"Verdict", esc(x.get("verified_claims_summary"))},
            {"Use it when", bullets(x.get("when_to_use"))},
            {"Skip it when", bullets(x.get("when_not_to_use"))},
            {"How it is fast", esc(x.get("how_it_is_fast"))},
            {"Compared with alternatives", esc(x.get("pick_this_over_siblings_when"))}};
        const Value& integration = x.get("integration");
        if (integration.truthy()) {
            const std::pair<const char*, const char*> labels[] = {
                {"form", "Form"}, {"dependencies", "Dependencies"}, {"min_toolchain", "Minimum toolchain"},
                {"platforms", "Platforms"}, {"thread_safety", "Thread safety"}, {"drop_in_for_baseline", "Drop-in for the baseline"}};
            std::vector<std::string> lines;
            for (const auto& [key, label] : labels) {
                if (!integration.present(key)) continue;
                const Value& value = integration.get(key);
                lines.push_back("| **" + std::string(label) + "** | " + (value.is_bool() ? cell(yes_no(value)) : cell(value)) + " |");
            }
            sections.push_back({"Integration", "| | |\n|---|---|\n" + join(lines, "\n")});
        }
        std::vector<std::string> caveats;
        for (const char* key : {"caveats", "tradeoffs"}) {
            if (e.get(key).truthy()) caveats.push_back(esc(e.get(key)));
        }
        sections.push_back({"Gotchas", bullets(x.get("gotchas"))});
        sections.push_back({"Known shortcomings", bullets(dec.get("shortcomings"))});
        sections.push_back({"Caveats and trade-offs", join(caveats, "\n\n")});
        sections.push_back({"Maintenance", esc(x.get("status_note"))});
        for (const auto& [title, body] : sections) {
            if (!text::strip(body).empty()) out.push_back("## " + title + "\n\n" + body);
        }

        auto value_or = [](const Value& object, const char* key, const char* fallback) {
            const Value* value = object.find(key);
            return value ? json::str(*value) : std::string(fallback);
        };
        std::vector<std::string> audit = {
            "- **Verification** (" + value_or(v, "date", "undated") + "): " + esc(v.find("verdict") ? v.get("verdict") : Value::of("n/a"))
            + "; tier before verification " + value_or(v, "tier_before", "?") + ", tier now " + e.tier() + "."};
        if (v.get("tier_reason").truthy()) audit.push_back("- **Tier reason:** " + esc(v.get("tier_reason")));
        if (v.get("retier").truthy()) {
            const Value& r = v.get("retier");
            audit.push_back("- **Retiered** " + value_or(r, "from", "?") + " to " + value_or(r, "to", "?") + ": " + esc(r.get("reason")));
        }
        if (v.get("notes").truthy()) audit.push_back("- **Verifier notes:** " + esc(v.get("notes")));
        if (e.get("corrected_fields").truthy()) {
            std::vector<std::string> fields;
            for (const Value& field : items(e.get("corrected_fields"))) fields.push_back("`" + json::str(field) + "`");
            audit.push_back("- **Fields the verifier corrected:** " + join(fields, ", "));
        }
        if (dec.get("measurements").truthy()) {
            std::vector<std::string> measurements;
            for (const Value& m : items(dec.get("measurements"))) measurements.push_back(json::str(m));
            audit.push_back("- **Shortcomings recorded by:** " + esc(join(measurements, "; ")));
        }
        for (const auto& [label, urls] : {std::pair<std::string, const Value&>{"Pages the verifier opened", v.get("urls_opened")},
                                          std::pair<std::string, const Value&>{"Sources the enricher read", x.get("sources_read")}}) {
            if (!urls.truthy()) continue;
            std::vector<std::string> lines;
            for (const Value& item : items(urls)) {
                std::string u = json::str(item);
                bool plain_web = (text::starts_with(u, "http://") || text::starts_with(u, "https://")) && u.size() > (u[4] == 's' ? 8 : 7)
                    && !has_link_break(u.substr(u[4] == 's' ? 8 : 7));
                lines.push_back(plain_web ? "  - <" + u + ">" : "  - " + cell(u));
            }
            audit.push_back("- **" + label + ":**\n" + join(lines, "\n"));
        }
        audit.push_back("- **Raw records:** [" + e.record_path + "](" + rel(page, e.record_path) + ") (id `" + e.id() + "`) · ["
                        + e.enrichment_path + "](" + rel(page, e.enrichment_path) + ") (enrichment confidence "
                        + value_or(x, "confidence", "n/a") + ")");
        out.push_back("<details>\n<summary><b>Audit trail</b></summary>\n\n" + join(audit, "\n") + "\n\n</details>");
        return join(out, "\n\n") + "\n";
    }

    std::string render_category(const std::string& d, const std::string& c, const std::vector<const Entry*>& es, const Spec& spec) const {
        std::string page = "catalog/" + d + "/" + c + "/README.md";
        auto t = tier_counts(es);
        size_t copies = std::count_if(es.begin(), es.end(), [](const Entry* e) { return copyable(*e); });
        std::vector<std::string> lines = {
            "# " + catalog_.category_titles.at(c),
            crumbs(page, {{"fastpp", "README.md"}, {"Catalog", "catalog/README.md"}, {catalog_.domain_title(d), "catalog/" + d + "/README.md"}}),
            "**What these beat:** " + cell(what_they_beat(catalog_, d, c, es, spec)) + "  \n**" + std::to_string(es.size()) + " "
                + (es.size() == 1 ? "entry" : "entries") + ":** " + tier_summary(t) + " · " + std::to_string(copies) + " copyable, "
                + std::to_string(es.size() - copies) + " study only"};
        if (auto row = spec.find(c); d == catalog_.cross_language_domain && row != spec.end() && row->second.size() >= 2) {
            lines.push_back("**Languages swept:** " + cell(row->second[0]) + "  \n**Where they tend to win:** " + cell(row->second[1]));
        }
        lines.push_back(entry_table(page, es));
        lines.push_back(legend);
        return join(lines, "\n\n") + "\n";
    }

    using Domain = std::vector<std::pair<std::string, std::vector<const Entry*>>>;

    static std::vector<const Entry*> flatten(const Domain& by_category) {
        std::vector<const Entry*> es;
        for (const auto& [_, list] : by_category) es.insert(es.end(), list.begin(), list.end());
        return es;
    }

    std::vector<const std::pair<std::string, std::vector<const Entry*>>*> by_title(const Domain& by_category) const {
        std::vector<const std::pair<std::string, std::vector<const Entry*>>*> out;
        for (const auto& item : by_category) out.push_back(&item);
        std::stable_sort(out.begin(), out.end(), [&](auto* a, auto* b) {
            return text::lower(catalog_.category_titles.at(a->first)) < text::lower(catalog_.category_titles.at(b->first));
        });
        return out;
    }

    std::string render_domain(const std::string& d, const Domain& by_category, const Spec& spec) const {
        std::string page = "catalog/" + d + "/README.md";
        std::vector<const Entry*> es = flatten(by_category);
        auto t = tier_counts(es);
        std::vector<std::string> rows = {"| Category | Entries | A | B | C | D | What they beat |", "|---|--:|--:|--:|--:|--:|---|"};
        for (const auto* item : by_title(by_category)) {
            const auto& [c, list] = *item;
            auto ct = tier_counts(list);
            rows.push_back("| " + link(catalog_.category_titles.at(c), c + "/README.md") + " | " + std::to_string(list.size()) + " | "
                           + std::to_string(ct["A"]) + " | " + std::to_string(ct["B"]) + " | " + std::to_string(ct["C"]) + " | "
                           + std::to_string(ct["D"]) + " | " + cell(what_they_beat(catalog_, d, c, list, spec), 90) + " |");
        }
        std::vector<const Entry*> picks;
        for (const Entry* e : es) {
            if (e->tier() == "A" && copyable(*e) && status(*e) == "active") picks.push_back(e);
        }
        std::stable_sort(picks.begin(), picks.end(), [](const Entry* a, const Entry* b) {
            return std::pair(-stars(*a), text::lower(a->name())) < std::pair(-stars(*b), text::lower(b->name()));
        });
        if (picks.size() > 10) picks.resize(10);
        std::vector<std::string> lines = {
            "# " + catalog_.domain_title(d),
            crumbs(page, {{"fastpp", "README.md"}, {"Catalog", "catalog/README.md"}}),
            catalog_.domain_intro(d),
            "**" + std::to_string(es.size()) + " entries in " + std::to_string(by_category.size()) + " categories:** " + tier_summary(t),
            join(rows, "\n")};
        if (!picks.empty()) {
            lines.push_back("## Most-adopted tier A picks");
            lines.push_back("Tier A, copyable and actively maintained, ordered by GitHub stars.");
            lines.push_back(entry_table(page, picks, true));
        }
        lines.push_back(legend);
        return join(lines, "\n\n") + "\n";
    }

    using Tree = std::vector<std::pair<std::string, Domain>>;

    static const Domain* find(const Tree& tree, const std::string& d) {
        for (const auto& [name, domain] : tree) {
            if (name == d) return &domain;
        }
        return nullptr;
    }

    static size_t category_count(const Tree& tree) {
        size_t n = 0;
        for (const auto& [_, domain] : tree) n += domain.size();
        return n;
    }

    std::string render_index(const Tree& tree, const std::vector<const Entry*>& entries, size_t rejected, long long seeds) const {
        std::string page = "catalog/README.md";
        auto t = tier_counts(entries);
        std::vector<std::string> rows = {"| Domain | Entries | A | B | C | D | Categories |", "|---|--:|--:|--:|--:|--:|---|"};
        for (const auto& domain : catalog_.domains) {
            const Domain* by_category = find(tree, domain.slug);
            if (!by_category) continue;
            auto es = flatten(*by_category);
            auto dt = tier_counts(es);
            std::vector<std::string> categories;
            for (const auto* item : by_title(*by_category)) {
                categories.push_back(link(catalog_.category_titles.at(item->first), domain.slug + "/" + item->first + "/README.md"));
            }
            rows.push_back("| " + link("**" + domain.title + "**", domain.slug + "/README.md") + " | " + std::to_string(es.size()) + " | "
                           + std::to_string(dt["A"]) + " | " + std::to_string(dt["B"]) + " | " + std::to_string(dt["C"]) + " | "
                           + std::to_string(dt["D"]) + " | " + join(categories, " · ") + " |");
        }
        std::vector<std::string> grouped;
        for (const char* k : tiers) grouped.push_back(text::group_thousands(t[k]) + " tier " + k);
        std::vector<std::string> lines = {
            "# Catalog",
            crumbs(page, {{"fastpp", "README.md"}}),
            "**" + text::group_thousands(entries.size()) + " verified entries** in " + std::to_string(category_count(tree)) + " categories across "
                + std::to_string(tree.size()) + " domains: " + join(grouped, " · ") + ".",
            "Every entry names the default it beats, quotes the published numbers, and records what is wrong with them. Start from a "
            "domain or jump straight to a category.",
            join(rows, "\n"),
            "## Also here",
            "- [Rejected claims](rejected.md): " + std::to_string(rejected) + " candidates whose evidence did not hold up, with the reason "
            "for each.\n- [Seeds without evidence](seeds-no-evidence.md): " + std::to_string(seeds) + " projects from curated lists that "
            "never published a comparison against a baseline.\n- [catalog.jsonl](catalog.jsonl) and [catalog.csv](catalog.csv): every "
            "entry in machine-readable form ([schema](../docs/schema.md)).",
            legend};
        return join(lines, "\n\n") + "\n";
    }

    std::string render_rejected(std::vector<Value> rejected) const {
        std::string page = "catalog/rejected.md";
        std::stable_sort(rejected.begin(), rejected.end(), [](const Value& a, const Value& b) {
            return std::tuple(text_of(a.get("domain")), text_of(a.get("category")), text::lower(text_of(a.get("name"))))
                < std::tuple(text_of(b.get("domain")), text_of(b.get("category")), text::lower(text_of(b.get("name"))));
        });
        std::vector<std::string> rows = {"| Project | Domain / category | Why it was rejected |", "|---|---|---|"};
        for (const Value& e : rejected) {
            const Value& v = e.get("verification");
            const Value* why = &v.get("reject_reason");
            if (!why->truthy()) why = &v.get("notes");
            if (!why->truthy()) why = &decision(text_of(e.get("id"))).get("reason");
            rows.push_back("| " + link("**" + cell(e.get("name"), 60) + "**", e.get("repo_url")) + " | " + cell(e.get("domain")) + " / "
                           + cell(e.get("category")) + " | " + cell(*why, 600) + " |");
        }
        std::vector<std::string> lines = {
            "# Rejected claims",
            crumbs(page, {{"fastpp", "README.md"}, {"Catalog", "catalog/README.md"}}),
            std::to_string(rejected.size()) + " candidates failed verification because the evidence itself was invalid: a benchmark that "
            "timed a no-op or a `sleep`, a hard-coded baseline column, a fast path that computed a different answer, numbers copied "
            "from design targets. Weak or first-party evidence is not a reason to reject; those entries stay in the catalog at a lower "
            "tier with their shortcomings written down.",
            "Rejected candidates stay on `data/known_list.txt` so later searches skip them.",
            join(rows, "\n")};
        return join(lines, "\n\n") + "\n";
    }

    // ------------------------------------------------------------ exports

    Value export_record(const Entry& e) const {
        static const char* const export_fields[] = {
            "id", "name", "domain", "category", "evidence_tier", "usability", "license", "language", "maintenance_status", "repo_url",
            "benchmark_url", "baseline", "claimed_speedup", "workload", "metric", "hardware", "compiler_and_flags", "caveats",
            "tradeoffs", "stars_or_usage", "last_commit", "has_code", "language_level_claim", "same_algorithm", "same_opt_level",
            "why_faster"};
        static const char* const enrich_fields[] = {
            "one_liner", "what_it_does", "verified_claims_summary", "how_it_is_fast", "when_to_use", "when_not_to_use",
            "pick_this_over_siblings_when", "integration", "gotchas", "status_note", "confidence"};
        Value rec;
        rec.kind = Value::Kind::object;
        for (const char* k : export_fields) {
            if (const Value* value = e.record.find(k)) rec.set(k, *value);
        }
        for (const char* k : enrich_fields) {
            if (const Value* value = e.enrichment.find(k)) rec.set(k, *value);
        }
        const Value* shortcomings = decision(e.id()).find("shortcomings");
        Value empty;
        empty.kind = Value::Kind::array;
        rec.set("shortcomings", shortcomings ? *shortcomings : empty);
        Value verification;
        verification.kind = Value::Kind::object;
        for (const char* k : {"date", "verdict", "tier_before", "tier_reason", "retier", "notes"}) {
            const Value& value = e.get("verification").get(k);
            if (!value.is_null()) verification.set(k, value);
        }
        rec.set("verification", verification);
        rec.set("page", Value::of(e.page));
        rec.set("record", Value::of(e.record_path));
        rec.set("enrichment", Value::of(e.enrichment_path));
        return rec;
    }

    static std::string csv_field(const std::string& field) {
        if (field.find_first_of(",\"\n\r") == std::string::npos) return field;
        return "\"" + text::replace_all(field, "\"", "\"\"") + "\"";
    }

    // csv.writer's text for a value: "" for None, str() for the rest.
    static std::string csv_value(const Value& value) { return value.is_null() ? std::string() : json::str(value); }

    void write_exports(const std::vector<const Entry*>& entries, const fs::path& out) const {
        std::vector<const Entry*> ordered = entries;
        std::stable_sort(ordered.begin(), ordered.end(), [](const Entry* a, const Entry* b) { return a->id() < b->id(); });
        std::string jsonl;
        for (const Entry* e : ordered) jsonl += json::dumps(export_record(*e)) + "\n";
        write_file(out / "catalog.jsonl", jsonl);

        std::string csv = "id,name,domain,category,evidence_tier,usability,license,language,status,stars,last_commit,repo_url,"
                          "benchmark_url,baseline,one_liner,page\n";
        for (const Entry* e : ordered) {
            long long n = stars(*e);
            std::vector<std::string> fields = {
                e->id(), e->name(), e->domain(), e->category(), e->tier(), csv_value(e->get("usability")), text_of(e->get("license")),
                text_of(e->get("language")), status(*e), n ? std::to_string(n) : "", text_of(e->get("last_commit")),
                text_of(e->get("repo_url")), text_of(e->get("benchmark_url")), text::squeeze(text_of(e->get("baseline"))),
                text_of(e->enrichment.get("one_liner")), e->page};
            for (size_t i = 0; i < fields.size(); ++i) {
                if (i) csv += ',';
                csv += csv_field(fields[i]);
            }
            csv += '\n';
        }
        write_file(out / "catalog.csv", csv);
    }

    // ------------------------------------------------------------ README blocks

    static std::string badge(const std::string& label, const std::string& message, const std::string& color) {
        std::string encoded = text::replace_all(text::replace_all(text::replace_all(message, "-", "--"), " ", "_"), ",", "%2C");
        return "<img alt=\"" + label + ": " + message + "\" src=\"https://img.shields.io/badge/" + text::replace_all(label, " ", "_") + "-"
            + encoded + "-" + color + "\">";
    }

    static size_t count_files(const fs::path& data, const std::string& middle, const std::string& prefix) {
        size_t n = 0;
        auto count_in = [&](const fs::path& dir) {
            if (!fs::is_directory(dir)) return;
            for (const auto& item : fs::directory_iterator(dir)) {
                std::string name = item.path().filename().string();
                if (text::starts_with(name, prefix) && name.size() >= 5 && name.ends_with(".json")) ++n;
            }
        };
        for (const fs::path& wave : waves(data)) count_in(wave / middle);
        return n;
    }

    std::vector<std::pair<std::string, std::string>> readme_blocks(const Tree& tree, const std::vector<const Entry*>& entries,
                                                                    size_t rejected) const {
        auto t = tier_counts(entries);
        size_t categories = category_count(tree);
        std::vector<std::pair<std::string, std::string>> blocks;
        blocks.push_back({"badges", "<p align=\"center\">\n  " + join({
            badge("verified entries", text::group_thousands(entries.size()), "2ea44f"),
            badge("tier A", text::group_thousands(t["A"]), "1f6feb"),
            badge("categories", std::to_string(categories), "8250df"),
            badge("claims rejected", std::to_string(rejected), "cf222e"),
            badge("license", "MIT", "blue"),
            "<a href=\"docs/how-it-was-built.md\">" + badge("built with", "Claude Code", "d97757") + "</a>"}, "\n  ") + "\n</p>"});

        blocks.push_back({"stats", "**" + text::group_thousands(entries.size()) + " entries** across **" + std::to_string(categories)
                                       + " categories** in **" + std::to_string(tree.size()) + " domains** · " + text::group_thousands(t["A"])
                                       + " tier A · " + text::group_thousands(t["B"]) + " tier B · " + text::group_thousands(t["C"])
                                       + " tier C · " + text::group_thousands(t["D"]) + " tier D · " + std::to_string(rejected)
                                       + " claims rejected"});

        std::vector<std::string> rows = {"| Domain | Entries | Jump to a category |", "|---|--:|---|"};
        for (const auto& domain : catalog_.domains) {
            const Domain* by_category = find(tree, domain.slug);
            if (!by_category) continue;
            size_t n = flatten(*by_category).size();
            std::vector<const std::pair<std::string, std::vector<const Entry*>>*> biggest;
            for (const auto& item : *by_category) biggest.push_back(&item);
            std::stable_sort(biggest.begin(), biggest.end(), [](auto* a, auto* b) { return a->second.size() > b->second.size(); });
            std::vector<std::string> categories_cell;
            for (size_t i = 0; i < biggest.size() && i < 8; ++i) {
                categories_cell.push_back(link(catalog_.category_titles.at(biggest[i]->first),
                                               "catalog/" + domain.slug + "/" + biggest[i]->first + "/README.md")
                                          + " " + std::to_string(biggest[i]->second.size()));
            }
            std::string cats = join(categories_cell, " · ");
            if (by_category->size() > 8) {
                cats += " · " + link("+" + std::to_string(by_category->size() - 8) + " more", "catalog/" + domain.slug + "/README.md");
            }
            rows.push_back("| " + link("**" + domain.title + "**", "catalog/" + domain.slug + "/README.md") + " | " + std::to_string(n) + " | "
                           + cats + " |");
        }
        blocks.push_back({"index", join(rows, "\n")});

        rows = {"| Need faster… | Pick | What it is | Tier |", "|---|---|---|:-:|"};
        for (const std::string& id : catalog_.featured) {
            auto hit = std::find_if(entries.begin(), entries.end(), [&](const Entry* e) { return e->id() == id; });
            if (hit == entries.end()) continue;
            const Entry& e = **hit;
            rows.push_back("| " + link(catalog_.category_titles.at(e.category()), parent(e.page) + "/README.md") + " | "
                           + link("**" + cell(e.name(), 50) + "**", e.page) + " | " + cell(e.enrichment.get("one_liner"), 160) + " | **"
                           + e.tier() + "** |");
        }
        blocks.push_back({"featured", join(rows, "\n")});

        const fs::path& data = catalog_.data;
        size_t search = count_files(data, "raw", "");
        if (fs::is_directory(data / "seeds" / "raw")) {
            for (const auto& item : fs::directory_iterator(data / "seeds" / "raw")) {
                if (item.path().filename().string().ends_with(".json")) ++search;
            }
        }
        size_t verify = count_files(data, "verify/raw", "batch-");
        size_t retier = count_files(data, "verify/raw", "retier-");
        size_t enrich = count_files(data, "enrich/raw", "");
        blocks.push_back({"pipeline", join({
            "```mermaid",
            "flowchart LR",
            "  S[\"Search agents<br/>" + text::group_thousands(search) + " reports\"] --> M[\"Merge and dedup\"]",
            "  M --> V[\"Verifier agents<br/>" + text::group_thousands(verify) + " batches\"]",
            "  V --> E[\"Enrichment agents<br/>" + text::group_thousands(enrich) + " write-ups\"]",
            "  E --> R[\"Retier checks and decisions<br/>" + std::to_string(retier) + " retier files, "
                + text::group_thousands(decision_count()) + " decisions\"]",
            "  R --> C[\"Catalog<br/>" + text::group_thousands(entries.size()) + " entries\"]",
            "  V -. invalid evidence .-> X[\"Rejected<br/>" + std::to_string(rejected) + " claims\"]",
            "```"}, "\n")});
        return blocks;
    }

    void fill_readme(const std::vector<std::pair<std::string, std::string>>& blocks) const {
        fs::path path = catalog_.root / "README.md";
        std::string readme = read_file(path);
        for (const auto& [name, body] : blocks) {
            std::string open = "<!-- fastpp:" + name + " -->\n";
            std::string close = "<!-- /fastpp:" + name + " -->";
            size_t start = readme.find(open);
            size_t end = start == std::string::npos ? std::string::npos : readme.find(close, start + open.size());
            if (end == std::string::npos) throw std::runtime_error("README.md has no <!-- fastpp:" + name + " --> block");
            readme.replace(start + open.size(), end - start - open.size(), body + "\n");
        }
        write_file(path, readme);
    }

private:
    const Catalog& catalog_;
    std::map<std::string, Value> decisions_;
};

}  // namespace

int render(const Catalog& catalog) {
    Loaded loaded = load_entries(catalog);
    Spec spec = spec_baselines(catalog);

    std::map<std::string, Value> decisions;
    for (Value& d : json::parse(read_file(catalog.data / "decisions.json")).array) decisions[text_of(d.get("id"))] = std::move(d);
    Renderer renderer(catalog, std::move(decisions));

    std::vector<const Entry*> ranked;
    for (const Entry& e : loaded.entries) ranked.push_back(&e);
    std::stable_sort(ranked.begin(), ranked.end(), [](const Entry* a, const Entry* b) { return rank_before(*a, *b); });
    Renderer::Tree tree;
    for (const Entry* e : ranked) {
        auto domain = std::find_if(tree.begin(), tree.end(), [&](const auto& d) { return d.first == e->domain(); });
        if (domain == tree.end()) domain = tree.insert(tree.end(), {e->domain(), {}});
        auto category = std::find_if(domain->second.begin(), domain->second.end(), [&](const auto& c) { return c.first == e->category(); });
        if (category == domain->second.end()) category = domain->second.insert(domain->second.end(), {e->category(), {}});
        category->second.push_back(e);
    }

    fs::path out = catalog.root / "catalog";
    if (fs::exists(out)) {
        // Every subdirectory is generated; stale entry pages go with it.
        for (const auto& item : fs::directory_iterator(out)) {
            if (item.is_directory()) fs::remove_all(item.path());
        }
    }
    fs::create_directories(out);
    for (const auto& [d, by_category] : tree) {
        fs::create_directory(out / d);
        write_file(out / d / "README.md", renderer.render_domain(d, by_category, spec));
        for (const auto& [c, es] : by_category) {
            fs::create_directory(out / d / c);
            write_file(out / d / c / "README.md", renderer.render_category(d, c, es, spec));
            for (const Entry* e : es) write_file(catalog.root / e->page, renderer.render_entry(*e));
        }
    }

    std::vector<fs::path> rejected_files;
    for (const fs::path& wave : waves(catalog.data)) {
        if (fs::exists(wave / "rejected.json")) rejected_files.push_back(wave / "rejected.json");
    }
    std::sort(rejected_files.begin(), rejected_files.end());
    std::vector<Value> rejected;
    for (const fs::path& file : rejected_files) {
        for (Value& e : json::parse(read_file(file)).array) rejected.push_back(std::move(e));
    }
    long long seeds = 0;
    if (fs::path seeds_page = out / "seeds-no-evidence.md"; fs::exists(seeds_page)) {
        std::string page = read_file(seeds_page);
        size_t line = 0;
        while (line < page.size()) {
            size_t end = page.find('\n', line);
            std::string_view text(page.data() + line, (end == std::string::npos ? page.size() : end) - line);
            size_t digits = 0;
            while (digits < text.size() && text::is_ascii_digit(text[digits])) ++digits;
            if (digits && text.substr(digits, 9) == " projects") {
                seeds = std::stoll(std::string(text.substr(0, digits)));
                break;
            }
            if (end == std::string::npos) break;
            line = end + 1;
        }
    }

    std::vector<const Entry*> entries;
    for (const Entry& e : loaded.entries) entries.push_back(&e);
    write_file(out / "README.md", renderer.render_index(tree, entries, rejected.size(), seeds));
    write_file(out / "rejected.md", renderer.render_rejected(rejected));
    renderer.write_exports(entries, out);
    renderer.fill_readme(renderer.readme_blocks(tree, entries, rejected.size()));

    std::cout << "catalog: " << entries.size() << " entries, " << Renderer::category_count(tree) << " categories, " << rejected.size()
              << " rejected; missing enrichment: " << loaded.missing.size() << "; duplicate ids kept once: " << loaded.dropped.size() << "\n";
    return 0;
}
