#include "catalog.hpp"

#include <fstream>
#include <iterator>
#include <stdexcept>

#include "json.hpp"

namespace fs = std::filesystem;

std::string read_file(const fs::path& path) {
    std::ifstream in(path, std::ios::binary);
    if (!in) throw std::runtime_error("can't read " + path.string());
    return std::string(std::istreambuf_iterator<char>(in), {});
}

void write_file(const fs::path& path, const std::string& content) {
    std::ofstream out(path, std::ios::binary);
    if (!out) throw std::runtime_error("can't write " + path.string());
    out << content;
}

fs::path find_root(fs::path start) {
    for (fs::path dir = fs::absolute(start); ; dir = dir.parent_path()) {
        if (fs::exists(dir / "data" / "catalog_meta.json")) return dir;
        if (dir == dir.parent_path()) break;
    }
    throw std::runtime_error("no data/catalog_meta.json above " + start.string() + ": run from inside the repository");
}

Catalog Catalog::load(const fs::path& root) {
    Catalog catalog;
    catalog.root = root;
    catalog.data = root / "data";
    json::Value meta = json::parse(read_file(catalog.data / "catalog_meta.json"));
    for (const json::Value& d : meta.get("domains").array) {
        catalog.domains.push_back({d.get("slug").text, d.get("title").text, d.get("intro").text});
    }
    for (const auto& [slug, title] : meta.get("categories").object) catalog.category_titles[slug] = title.text;
    for (const auto& [from, to] : meta.get("category_aliases").object) catalog.category_aliases[from] = to.text;
    catalog.cross_language_domain = meta.get("cross_language").get("domain").text;
    catalog.cross_language_baseline = meta.get("cross_language").get("baseline").text;
    for (const json::Value& id : meta.get("featured").array) catalog.featured.push_back(id.text);
    return catalog;
}

bool Catalog::has_domain(const std::string& slug) const {
    for (const Domain& d : domains) {
        if (d.slug == slug) return true;
    }
    return false;
}

const std::string& Catalog::domain_title(const std::string& slug) const {
    for (const Domain& d : domains) {
        if (d.slug == slug) return d.title;
    }
    throw std::out_of_range("unknown domain " + slug);
}

const std::string& Catalog::domain_intro(const std::string& slug) const {
    for (const Domain& d : domains) {
        if (d.slug == slug) return d.intro;
    }
    throw std::out_of_range("unknown domain " + slug);
}
