# ugrep (with ugrep-indexer)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Text search and indexing](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> ugrep-indexer builds Bloom-filter file indexes so ugrep's cold recursive search skips non-matching files, beating ripgrep.

| | |
|---|---|
| **Beats** | ripgrep |
| **Claimed result** | README states ugrep's own indexed cold search (0.0487s best-of-4, range 0.0487-0.0983s) is '21 times faster' (10x-21x across runs) than ugrep's own unindexed cold search (1.02s); ripgrep 13.0.0 took 1.18s on the same cold search, i.e. roughly 12x-24x faster than ripgrep for the indexed run (derived from page data). Without indexing, plain ugrep (1.02s) was already marginally faster than ripgrep (1.18s) on this query. |
| **Workload** | Cold-filesystem recursive search for the pattern 'std::chrono' across the ugrep v3.12.6 source tree (1,317 files, 28 directories, 12.2MB), with OS file-system cache cleared by unmounting/remounting the drive; 8 threads |
| **Metric** | latency |
| **Adoption** | 3.3k stars (ugrep); ugrep-indexer companion tool is a separate, smaller repo (84 stars) |
| **Last commit** | 2026-09-15 |
| **Links** | [repository](https://github.com/Genivia/ugrep) · [benchmark](https://github.com/Genivia/ugrep-indexer/blob/main/README.md) |

## Verdict

On ugrep's own v3.12.6 source tree (1,317 files, 12.2MB, 8 threads), cold-filesystem search for 'std::chrono' took 1.02s unindexed vs 0.0487s best-of-4 (range 0.0487-0.0983s) with --index -- a 10x-21x self-comparison; ripgrep 13.0.0 took 1.18s on the same cold search (timed with shell `time`, vs ugrep's internal --stats timer), giving a derived roughly 12x-24x gap between indexed ugrep and ripgrep. No CPU, OS, or compiler flags are stated.

## Use it when

- Recursive greps over directories that are cold in the OS page cache: network drives, rarely-touched archives, first search after mount/boot
- Repeated searches of the same large, slowly-changing tree where the indexing pass amortizes over many searches
- Patterns with a short, selective literal prefix (first 8-16 bytes distinctive) that keep the index false-positive rate low
- Already using ugrep for its grep-compatible CLI, Unicode support, or archive/compressed-file search and want an extra lever for cold storage
- Willing to spend \~0.5KB-14KB of index storage per file depending on chosen accuracy level

## Skip it when

- Files are already warm in the OS page cache -- indexing adds startup/check overhead and can be slower than a plain search
- Highly volatile trees needing frequent re-indexing; re-indexing is incremental but still recurring maintenance work
- Patterns using unlimited `*`/`+` repeats or large Unicode character classes -- these raise both index-hash construction start-up time and the false-positive rate
- Need `-v` (invert), `--filter`, `-P` (Perl regex), or `-Z` (fuzzy) -- `--index` does not support these ugrep modes
- Only one small, first-party benchmark exists (1,317 files/12.2MB on ugrep's own v3.12.6 tree); no independent or larger-scale confirmation

## How it is fast

ugrep-indexer builds a windowed N-gram hash table per file (Bloom-filter-like, tunable accuracy -0 to -9, default -4) using an additive prime-61 rolling hash over up to the first 16 bytes of the eventual search pattern, compiled by ugrep into a hash finite automaton (HFA) layered on top of its regex DFA. At search time ugrep tests each file's stored hash bits against the pattern's HFA before opening the file, so on a cold (uncached) filesystem it avoids the disk read and decompression cost for files that cannot match.

## Compared with alternatives

Sibling entries (frg, ngi, trigrep) speed up ripgrep-class search on warm/in-memory data; ugrep+ugrep-indexer targets the opposite case -- cold, uncached filesystems -- and only pays off after a separate indexing pass, so pick it when your searches hit rarely-cached storage (network or cold disks) and you can tolerate index upkeep, not for ordinary warm-cache greps.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none required for core grep functionality; optional PCRE2 or Boost.Regex for -P (Perl regex), zlib for -z, and optional bzip2/lzma/lz4/zstd/brotli/bzip3 for specific compressed-archive formats |
| **Minimum toolchain** | not documented -- autotools build (AC_PROG_CXX in configure.ac / ./build.sh), no pinned C++ standard flag found in configure.ac or src/Makefile.am |
| **Platforms** | Linux, macOS (Homebrew/MacPorts), Windows (winget), FreeBSD, OpenBSD, Alpine, Arch; x86-64 with SSE2/AVX2/AVX512BW auto-detected (disable via --disable-sse2/--disable-avx2), ARM/AArch64 NEON (--disable-neon to turn off) |
| **Thread safety** | not documented as an explicit API guarantee; project runs ThreadSanitizer, AddressSanitizer, MemorySanitizer and UndefinedBehaviorSanitizer in its dev workflow to catch data races, and search itself runs multi-threaded internally (8 threads in the benchmark) |
| **Drop-in for the baseline** | partial -- explain: plain ugrep is a drop-in replacement for grep/egrep/fgrep (via the `ug` symlink), but indexed mode is not drop-in for ripgrep's zero-setup usage -- it requires running ugrep-indexer ahead of time and passing --index |

## Gotchas

- Index has a false-positive (noise) rate -- some non-matching files are still opened; rate rises with permissive patterns and lower accuracy settings
- Index files are hidden per-directory `._UG#_Store` files; use ugrep-indexer -d to remove them or re-index after large structural changes
- Current --index design is safe (files are always re-scanned if newer than the index timestamp) only because indexes stay per-directory; the README explicitly warns a possible future 'single combined index file' option would drop that safety guarantee
- Higher accuracy levels (-8/-9) push index storage up to tens of KB per very noisy file, versus \~4KB/file at the default -4

## Caveats and trade-offs

Numbers come from the project's own README (ugrep-indexer) with exact commands shown, but no CPU model, OS, or compiler flags are stated, and the dataset is small (1,317 files, 12.2MB, old ugrep v3.12.6 tree; ripgrep 13.0.0). The '21x' figure compares indexed vs ugrep's own unindexed run; the \~12x-24x vs-ripgrep figure is derived from page data. The two tools were timed differently: ugrep through its internal --stats timer, ripgrep through shell `time` wall clock (which includes process startup). The ugrep-indexer repo's last commit is 2025-06-22.

Speed advantage requires running the separate ugrep-indexer tool ahead of time to build per-directory N-gram Bloom-filter index files (\~4KB/file storage overhead at default accuracy, tunable 0-9); index has a false-positive rate so some non-matching files are still opened; benefit is specific to cold/uncached file systems -- on a warm page cache, indexed search adds overhead and may not be faster; index must be kept up to date (incremental re-indexing) as files change.

## Maintenance

Core ugrep is actively maintained (3,302 stars, BSD-3-Clause, last commit 2026-09-15); the ugrep-indexer companion repo is smaller (84 stars) with its own last commit on 2025-06-22, so the indexing feature is iterating more slowly than core ugrep.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** The ugrep-indexer README shows exact commands and timings: cold unindexed ugrep 1.02s, ripgrep 13.0.0 1.18s, indexed ugrep 0.0487s (best of 4, range 0.0487-0.0983s, '21 times faster' vs unindexed). These are first-party numbers with no CPU, OS or compiler stated, so tier C.
- **Verifier notes:** Claim and derived ratios check out (1.18/0.0487 = 24.2x, 1.18/0.0983 = 12.0x). ugrep has 3,302 stars, BSD-3-Clause, not a fork. Its default branch (master) last commit is 2026-09-15; the 2026-09-21 push was a dependabot branch.
- **Fields the verifier corrected:** `last_commit`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/Genivia/ugrep-indexer/blob/main/README.md>
  - <https://github.com/Genivia/ugrep>
  - <https://github.com/Genivia/ugrep-indexer>
- **Sources the enricher read:**
  - <https://github.com/Genivia/ugrep-indexer/blob/main/README.md>
  - <https://github.com/Genivia/ugrep>
  - <https://github.com/Genivia/ugrep/blob/master/README.md>
  - <https://github.com/Genivia/ugrep/blob/master/configure.ac>
  - <https://github.com/Genivia/ugrep/blob/master/src/Makefile.am>
  - https://github.com/Genivia/ugrep (git tree listing)
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/genivia/ugrep`) · [data/wave3/enrich/raw/github_com_genivia_ugrep.json](../../../data/wave3/enrich/raw/github_com_genivia_ugrep.json) (enrichment confidence 0.55)

</details>
