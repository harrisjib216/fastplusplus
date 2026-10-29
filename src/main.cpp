// fastpp: the tool that turns the research records under data/ into the published catalog, and keeps personal data
// out of the repository. CI runs all three commands on every push and fails when the committed output differs.
#include <filesystem>
#include <iostream>
#include <stdexcept>
#include <string>

#include "catalog.hpp"
#include "check_pii.hpp"
#include "json.hpp"
#include "render.hpp"

namespace {

const char* const usage =
    "usage: fastpp <command>\n"
    "\n"
    "  render                  write catalog/ and the generated blocks of README.md from data/\n"
    "  seeds                   write catalog/seeds-no-evidence.md from data/seeds/no_evidence/\n"
    "  check-pii [--commits] [--fix]\n"
    "                          fail if tracked files carry a home-directory path, a personal email address or a\n"
    "                          credential; --commits also checks HEAD's author and committer emails, --fix rewrites\n"
    "                          home-directory paths to /path/to/fastpp\n"
    "\n"
    "Run it from anywhere inside the repository.\n";

}  // namespace

int main(int argc, char** argv) {
    std::string command = argc > 1 ? argv[1] : "";
    try {
        std::filesystem::path root = find_root(std::filesystem::current_path());
        if (command == "render" && argc == 2) return render(Catalog::load(root));
        if (command == "seeds" && argc == 2) return render_seeds(Catalog::load(root));
        if (command == "check-pii") {
            bool commits = false, fix = false;
            for (int i = 2; i < argc; ++i) {
                std::string flag = argv[i];
                if (flag == "--commits") commits = true;
                else if (flag == "--fix") fix = true;
                else {
                    std::cerr << usage;
                    return 2;
                }
            }
            return check_pii(root, commits, fix);
        }
    } catch (const json::Error& error) {
        std::cerr << "fastpp: malformed JSON: " << error.message << "\n";
        return 1;
    } catch (const std::exception& error) {
        std::cerr << "fastpp: " << error.what() << "\n";
        return 1;
    }
    std::cerr << usage;
    return 2;
}
