# marisa-trie (libmarisa)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Succinct data structures](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-2-Clause OR LGPL-2.1-or-later` · 🟢 active

> Static LOUDS-based recursive (nested Patricia) trie dictionary; about 7.4x smaller than darts-clone and 2.5x smaller than tx-trie.

| | |
|---|---|
| **Beats** | darts-clone (compacted double-array trie) and tx-trie (LOUDS-based trie) |
| **Claimed result** | Size: marisa-trie 50,753,560 bytes vs tx-trie 127,727,058 vs darts-clone 376,613,888 (about 2.5x smaller than tx-trie and 7.4x smaller than darts-clone, derived from page data). |
| **Workload** | Dictionary size for 9,805,576 English Wikipedia page titles (Nov 2012, 200,435,403 bytes plain). |
| **Metric** | memory |
| **Adoption** | 633 stars; widely used via Python marisa-trie bindings |
| **Last commit** | 2026-07-28 |
| **Links** | [repository](https://github.com/s-yata/marisa-trie) · [benchmark](https://github.com/s-yata/marisa-trie) |

## Verdict

The only comparison is the README's size table for 9,805,576 English Wikipedia titles (Nov 2012, 200,435,403 bytes): marisa-trie 50,753,560 bytes vs tx-trie 127,727,058 and darts-clone 376,613,888 (about 2.5x and 7.4x smaller, derived from page data). No compiler, hardware or speed numbers are given, and the bundled tools/marisa-benchmark.cc times marisa alone (std::clock), so speed against the baselines is not measured by this repo.

## Use it when

- Large static string sets (millions of words, titles, URLs, n-gram vocabularies) where dictionary size or RSS matters more than per-lookup latency.
- You need key IDs both ways (string to dense ID and ID back to string) without a separate string table.
- Prefix or autocomplete queries (common-prefix search for tokenizers and morphological analysers, predictive search for completion).
- Dictionaries shipped as files and memory-mapped at startup, shared read-only across processes.
- Python projects: the widely used marisa-trie Python package wraps this library.

## Skip it when

- The key set changes at run time: the trie is static and must be rebuilt from a Keyset for any insert or delete.
- Lookup latency is the priority: the catalogued xcdat reports marisa at 1818 ns/key vs 826 (xcdat&lt;8&gt;) and 619 (xcdat&lt;15&gt;) on its Wiki set, and double-array tries such as darts-clone are generally faster at much larger size.
- More than about 4 billion keys or keys longer than 4 GiB: key IDs and lengths are 32-bit (MARISA_INVALID_KEY_ID = UINT32_MAX; set_key asserts length &lt;= UINT32_MAX).
- You need arbitrary values per key: it maps keys to dense IDs only; values must live in a side array indexed by ID.
- Untrusted dictionary files: loading checks only a magic header and vector sizes (see gotchas).

## How it is fast

The win is space, not speed. Each trie level is a LOUDS (level-order unary degree sequence) succinct tree with rank/select bit vectors; edge labels are Patricia-compressed, and the label strings themselves are stored in another MARISA trie recursively (3 levels by default, up to 127), with the final tails merged into a shared TAIL. Lookups are sped up by a small node cache (five size levels) and by weight-ordered child arrangement (the default), and rank/select uses popcount, an SSSE3 or NEON byte-count path, or BMI2 PDEP-based select when built with ENABLE_NATIVE_CODE.

## Compared with alternatives

Pick marisa over darts-clone when the dictionary must be several times smaller and you need reverse lookup or predictive search; pick xcdat or darts-clone when lookup speed matters more than size. lexindex and C2 report smaller and/or faster structures than MARISA in their own benchmarks, but marisa is the long-established, widely packaged option (Debian, Python bindings) with mmap support.

## Integration

| | |
|---|---|
| **Form** | static lib (or shared lib) built with CMake, plus command-line tools |
| **Dependencies** | none (C++ standard library only) |
| **Minimum toolchain** | C++17 minimum since v0.3.0 (CMake sets C++20 with CXX_STANDARD_REQUIRED OFF); CMake 3.22+ |
| **Platforms** | any 32- or 64-bit platform; optional x86-64 SSE2..SSE4.2/POPCNT/BMI/BMI2 paths behind ENABLE_NATIVE_CODE (-march=native), NEON popcount on AArch64; Windows (incl. MinGW64) supported |
| **Thread safety** | not documented; query methods are const on Trie and keep search state in the caller's Agent, so one Agent per thread over a shared built Trie appears intended (inferred from the API, not stated) |
| **Drop-in for the baseline** | partial: darts-clone and tx-trie are also static string tries with lookup and prefix search, but marisa has a different Keyset/Agent API, returns dense key IDs instead of stored values, and uses its own file format |

## Gotchas

- Errors are reported by exceptions (std::logic_error, std::invalid_argument, std::runtime_error, std::system_error since v0.3.1; older releases threw marisa::Exception with MARISA_\*_ERROR codes), so code written against 0.2.x needs its catch clauses updated; the Python binding broke on 0.3.1 (issue #121, closed).
- Trie::map / mmap / load verify only the 'We love Marisa.' header and that each vector size is a multiple of its element size; there is no structural validation (e.g. cache_mask_ = cache_.size() - 1 assumes a power-of-two cache), so a corrupted or crafted dictionary file can lead to out-of-bounds reads. Treat dictionary files as trusted input.
- Open issue #152 (Aug 2026): on 32-bit platforms FlatVector::build_ leaves one unit uninitialized, so saved trie files contain random heap bytes and are not reproducible (lookups still correct; proposed fix resize(num_units, 0) not yet merged). Issue #133 (Nov 2025) reports memory corruption in Trie::build with very large key sets and was closed as not planned without a root cause.
- ENABLE_NATIVE_CODE=ON (shown in the README build line) compiles with -march=native and BMI2/SSE4 defines, so binaries built that way are not portable to older CPUs; the SONAME is still 0 (open issue #126).

## Known shortcomings

- Size-only win (enwiki titles: marisa 50.8 MB vs tx-trie 127.7 MB and darts-clone 376.6 MB); speed against darts-clone is unverified since tools/marisa-benchmark.cc times marisa alone. No compiler, flags or hardware stated.
- Open issue #152 (Aug 2026): on 32-bit, FlatVector::build_ leaves bytes uninitialised so saved files are not reproducible. Issue #133 (Nov 2025): memory corruption in Trie::build with huge keysets, closed not planned. map/load check only the header magic and vector sizes with no structural validation, so crafted files can cause out-of-bounds reads; treat dictionary files as trusted. Keys and IDs are 32-bit. v0.3.1 switched to std exceptions. ENABLE_NATIVE_CODE uses -march=native. C++17+.

## Caveats and trade-offs

The README table reports size only, with no speed numbers, compiler or hardware, and the measurement dates from 2012-era data. The repo's tools/marisa-benchmark.cc times marisa alone (build, lookup, reverse lookup, prefix and predictive search) and does not run darts-clone or tx-trie. darts-clone is already catalogued in this wave, so this is a size-only win over it: The page gives no lookup-speed comparison, so speed against darts-clone is unverified. Recent commits are mostly dependabot CI bumps; the last maintainer commit was 2026-02-11. The readthedocs benchmark page for the Python bindings was not opened (readthedocs blocked).

Static, read-only dictionary (LOUDS-encoded nested Patricia trie); build is slow relative to double-array tries; lookups slower than darts-clone (not measured in README).

## Maintenance

Active (v0.3.1 released July 2024; commits through 2026, recent ones mostly dependabot CI bumps) and dual-licensed BSD-2-Clause OR LGPL-2.1-or-later, so it is safe to vendor or link.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The project's own README table lists dictionary sizes for 9,805,576 English Wikipedia titles (enwiki-20121101, 200,435,403 bytes plain): darts-clone 376,613,888 bytes, tx-trie 127,727,058, marisa-trie 50,753,560. There is no harness, compiler, flags or hardware for that table, and tools/marisa-benchmark.cc includes only marisa.h (no darts-clone or tx-trie comparison), so the tier is C.
- **Verifier notes:** The size numbers and ratios in claimed_speedup match the README (2.5x vs tx-trie, 7.4x vs darts-clone, derived from page data). Metadata confirmed from the github.com page: 633 stars, 103 forks, not archived, not a fork, BSD-2-Clause OR LGPL-2.1-or-later (COPYING.md), last commit 2026-07-28 (dependabot), so active. Treat this as a memory/size entry, not a speed entry.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** first-party README size table
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/s-yata/marisa-trie/HEAD/README.md>
  - <https://raw.githubusercontent.com/s-yata/marisa-trie/HEAD/COPYING.md>
  - <https://github.com/s-yata/marisa-trie>
  - <https://github.com/s-yata/marisa-trie/commits>
  - <https://github.com/s-yata/marisa-trie/tree/master/tools>
  - <https://raw.githubusercontent.com/s-yata/marisa-trie/HEAD/tools/marisa-benchmark.cc>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/s-yata/marisa-trie/HEAD/README.md>
  - <https://raw.githubusercontent.com/s-yata/marisa-trie/HEAD/COPYING.md>
  - <https://raw.githubusercontent.com/s-yata/marisa-trie/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/s-yata/marisa-trie/HEAD/include/marisa.h>
  - <https://raw.githubusercontent.com/s-yata/marisa-trie/HEAD/include/marisa/trie.h>
  - <https://raw.githubusercontent.com/s-yata/marisa-trie/HEAD/include/marisa/keyset.h>
  - <https://raw.githubusercontent.com/s-yata/marisa-trie/HEAD/include/marisa/agent.h>
  - <https://raw.githubusercontent.com/s-yata/marisa-trie/HEAD/include/marisa/base.h>
  - <https://raw.githubusercontent.com/s-yata/marisa-trie/HEAD/lib/marisa/trie.cc>
  - <https://raw.githubusercontent.com/s-yata/marisa-trie/HEAD/lib/marisa/grimoire/io/mapper.cc>
  - <https://raw.githubusercontent.com/s-yata/marisa-trie/HEAD/lib/marisa/grimoire/io/reader.cc>
  - <https://raw.githubusercontent.com/s-yata/marisa-trie/HEAD/lib/marisa/grimoire/trie/louds-trie.cc>
  - <https://raw.githubusercontent.com/s-yata/marisa-trie/HEAD/lib/marisa/grimoire/trie/louds-trie.h>
  - <https://raw.githubusercontent.com/s-yata/marisa-trie/HEAD/lib/marisa/grimoire/trie/header.h>
  - <https://raw.githubusercontent.com/s-yata/marisa-trie/HEAD/lib/marisa/grimoire/vector/bit-vector.cc>
  - <https://raw.githubusercontent.com/s-yata/marisa-trie/HEAD/lib/marisa/grimoire/vector/vector.h>
  - <https://raw.githubusercontent.com/s-yata/marisa-trie/HEAD/lib/marisa/grimoire/vector/pop-count.h>
  - <https://raw.githubusercontent.com/s-yata/marisa-trie/HEAD/tools/marisa-benchmark.cc>
  - <https://github.com/s-yata/marisa-trie/issues?q=is%3Aissue>
  - <https://github.com/s-yata/marisa-trie/issues/133>
  - <https://github.com/s-yata/marisa-trie/issues/152>
  - <https://github.com/s-yata/marisa-trie/releases>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/s-yata/marisa-trie`) · [data/wave9/enrich/raw/github_com_s_yata_marisa_trie.json](../../../data/wave9/enrich/raw/github_com_s_yata_marisa_trie.json) (enrichment confidence 0.8)

</details>
