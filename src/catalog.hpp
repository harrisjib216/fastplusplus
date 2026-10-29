// Display metadata for the rendered catalog, read from data/catalog_meta.json: domain order, titles and intros,
// category titles and aliases, the cross-language baseline and the README's featured entries. Data files keep
// their slugs; only the rendered pages use these names.
#pragma once

#include <filesystem>
#include <map>
#include <string>
#include <vector>

struct Catalog {
    struct Domain {
        std::string slug;
        std::string title;
        std::string intro;
    };

    std::filesystem::path root;
    std::filesystem::path data;
    // In the order the index pages list them: the standard library first, then the waves in the order they ran.
    std::vector<Domain> domains;
    std::map<std::string, std::string> category_titles;
    std::map<std::string, std::string> category_aliases;
    // The domain whose categories share one baseline (spec Part 4, wave 14), and that baseline's wording.
    std::string cross_language_domain;
    std::string cross_language_baseline;
    // README highlights, chosen by hand; ids that are gone are skipped.
    std::vector<std::string> featured;

    static Catalog load(const std::filesystem::path& root);

    bool has_domain(const std::string& slug) const;
    const std::string& domain_title(const std::string& slug) const;
    const std::string& domain_intro(const std::string& slug) const;
};

// The repository root: the nearest directory above `start` that holds data/catalog_meta.json.
std::filesystem::path find_root(std::filesystem::path start);

std::string read_file(const std::filesystem::path& path);
void write_file(const std::filesystem::path& path, const std::string& content);
