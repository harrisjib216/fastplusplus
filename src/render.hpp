#pragma once

#include "catalog.hpp"

// Writes catalog/ and the README's generated blocks. Returns the process exit code.
int render(const Catalog& catalog);

// Compiles data/seeds/no_evidence/*.json into catalog/seeds-no-evidence.md. Returns the process exit code.
int render_seeds(const Catalog& catalog);
