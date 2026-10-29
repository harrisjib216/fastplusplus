#pragma once

#include <filesystem>

// Reports personal data in the files git tracks under `root` (and, with `commits`, in HEAD's author and committer
// emails). With `fix`, rewrites home-directory paths first. Returns the process exit code.
int check_pii(const std::filesystem::path& root, bool commits, bool fix);
