# fastpp: faster than the default

A catalog of libraries and tools that are measurably faster than the incumbent developers reach for by
default: the C++ standard library, GCC/Clang/ld, zlib, OpenSSL and so on. Every entry names the baseline it
beats, quotes the speedup from its source, and carries an evidence tier. A separate verifier re-checked each
claim against the cited page before it was written up.

## Lists

- [COPYABLE.md](COPYABLE.md): 196 entries under an OSI license or CC0. Code can be vendored or forked.
- [REFERENCE.md](REFERENCE.md): 15 entries with no, unclear, or non-OSI license. Study the idea; don't copy the code.
- [REJECTED.md](REJECTED.md): 5 candidates that failed verification.

Tiers across both lists: A 89, B 22, C 96, D 4.

## Evidence tiers

- **A**: public benchmark code, run against the named baseline, with compiler, flags and CPU model all stated
  (whoever ran it).
- **B**: peer-reviewed paper or well-known independent benchmark suite that falls short of A.
- **C**: numbers from the project itself without full methodology, or numbers without methodology. Listed under
  *Unverified claims*.
- **D**: no numbers; kept only for notable projects.

Ratios marked "(derived from page data)" were computed from numbers on the cited page, not quoted.

## Coverage

| Domain | Category | Entries | A | B | C | D |
|---|---|---|---|---|---|---|
| compression-and-encoding | general-lossless | 2 | 0 | 2 | 0 | 0 |
| crypto-and-hashing | non-crypto-hashes | 2 | 1 | 1 | 0 | 0 |
| numerics-and-science | blas-lapack | 1 | 1 | 0 | 0 | 0 |
| parsing-and-text | regex-engines | 1 | 0 | 1 | 0 | 0 |
| runtime-and-systems | filesystems-and-io | 1 | 0 | 1 | 0 | 0 |
| serialization-and-formats | json | 3 | 2 | 0 | 1 | 0 |
| stdlib-replacements | allocators | 16 | 4 | 4 | 7 | 1 |
| stdlib-replacements | async-tasks-threadpools | 8 | 5 | 1 | 1 | 1 |
| stdlib-replacements | bitsets-and-succinct | 6 | 3 | 0 | 3 | 0 |
| stdlib-replacements | concurrency-queues-locks | 8 | 6 | 0 | 2 | 0 |
| stdlib-replacements | hash-maps-sets | 18 | 13 | 1 | 4 | 0 |
| stdlib-replacements | io-and-filesystem | 3 | 1 | 0 | 2 | 0 |
| stdlib-replacements | math-simd-linear-algebra | 10 | 2 | 2 | 5 | 1 |
| stdlib-replacements | number-parsing-formatting | 15 | 6 | 2 | 7 | 0 |
| stdlib-replacements | ordered-maps-trees | 9 | 4 | 0 | 5 | 0 |
| stdlib-replacements | priority-queues-heaps | 5 | 4 | 0 | 1 | 0 |
| stdlib-replacements | random | 9 | 4 | 2 | 3 | 0 |
| stdlib-replacements | regex | 7 | 3 | 1 | 3 | 0 |
| stdlib-replacements | searching | 5 | 2 | 0 | 3 | 0 |
| stdlib-replacements | sequence-containers | 5 | 2 | 0 | 3 | 0 |
| stdlib-replacements | serialization-json | 10 | 5 | 0 | 5 | 0 |
| stdlib-replacements | small-buffer-and-strings | 7 | 1 | 0 | 5 | 1 |
| stdlib-replacements | smart-pointers-and-refcount | 7 | 3 | 1 | 3 | 0 |
| stdlib-replacements | sorting | 17 | 6 | 0 | 11 | 0 |
| stdlib-replacements | string-search-and-hashing | 9 | 5 | 1 | 3 | 0 |
| toolchain-and-build | build-systems | 5 | 1 | 0 | 4 | 0 |
| toolchain-and-build | compile-caching-and-distribution | 4 | 0 | 0 | 4 | 0 |
| toolchain-and-build | compilers-frontends | 4 | 0 | 1 | 3 | 0 |
| toolchain-and-build | formatters-linters-lsps | 6 | 3 | 0 | 3 | 0 |
| toolchain-and-build | linkers | 3 | 2 | 0 | 1 | 0 |
| toolchain-and-build | preprocessors-and-codegen | 5 | 0 | 1 | 4 | 0 |

## How entries are made

Search agents look for candidates per domain × category × source; a merge step dedups them; an Opus
verifier opens each cited benchmark and re-derives the tier; a Sonnet enrichment agent reads the repo and
writes the entry. Prompts and rules: [faster-than-std-agent-prompt.md](faster-than-std-agent-prompt.md);
scripts: [pipeline/](pipeline/); raw records: [data/](data/).

Speedups are the authors' or third parties' published numbers. None has been re-run on our own hardware yet
(that is the planned code-audit stage).

Regenerate the lists with `python3 pipeline/render_lists.py`.
