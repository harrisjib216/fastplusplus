# ripgrep

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Filesystems and I/O](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT OR Unlicense` · 🟢 active

> Recursive regex search CLI in Rust; beats GNU grep, git grep, ag and ugrep on code trees and large files.

| | |
|---|---|
| **Beats** | GNU grep, ag, git grep (mmap vs buffered read strategy) |
| **Claimed result** | 0.082 s versus git grep 0.273 s (3.3x) on the Linux kernel tree, i9-12900K; the 2.670 s / 32.70x row is git grep -E under UTF-8, not GNU grep; GNU grep rows: 0.674 s versus 0.063 s (10.69x) and 6.577 s versus 1.042 s (6.31x) on a 13 GB file; hypergrep 0.167 s and ugrep 0.639 s also listed |
| **Workload** | Recursive search of the Linux kernel tree and single-file subtitle search; mmap versus intermediate-buffer reads chosen per workload. |
| **Metric** | throughput |
| **Hardware** | Intel i9-12900K 5.2 GHz (README benchmark) |
| **Adoption** | 68.9k stars |
| **Last commit** | 2026-08-04 |
| **Links** | [repository](https://github.com/BurntSushi/ripgrep) · [benchmark](https://github.com/BurntSushi/ripgrep) |

## Verdict

Author's README timings on an Intel i9-12900K with the Linux kernel tree built with defconfig: rg 0.082s against git grep -P 0.273s, ag 0.443s, ugrep 0.639s and git grep -E under a UTF-8 locale 2.670s; GNU grep itself ran only in the whitelist test (0.674s vs rg 0.063s, 10.69x) and on the 13GB file (6.577s vs 1.042s, 6.31x). One run each, no compiler or build profile stated; the 2.670s figure in the record belongs to git grep, not GNU grep, and the mmap-vs-buffer split (linux_literal, subtitles_literal) is from the blog snippet only and was not checked against the blog.

## Use it when

- Interactive or scripted search over large source trees where skipping ignored, hidden and binary files is what you want (Linux kernel tree: 0.082s vs git grep -P 0.273s, ag 0.443s)
- Searching single huge files cached in memory with Unicode-aware patterns (13GB subtitles: 1.042s vs GNU grep 6.577s under a UTF-8 locale)
- Patterns without usable literals on big inputs, where it still led ugrep 1.40x and LC_ALL=C GNU grep 2.08x in the README
- As a design reference for C++ code that picks mmap vs buffered reads: mmap for a handful of large files, a reused buffer for many small files

## Skip it when

- You need a library callable from C++: rg is a Rust binary, and the grep-\* and ignore crates have Rust APIs only
- You need POSIX grep semantics or a tool guaranteed to exist on every machine; ripgrep does not follow POSIX and default filtering hides files grep would search (use -uuu)
- Very high match counts, where printing dominates and the gap narrows (rg the: 6.948s vs GNU grep 15.217s, ugrep 11.721s)
- Files that may be truncated while being searched: with memory maps on, ripgrep can abort with SIGBUS (use --no-mmap)
- Look-around or backreferences with the default engine; these need -P (PCRE2), which is an optional build feature

## How it is fast

The Rust regex crate uses finite automata with UTF-8 decoding built into its DFA, SIMD literal prefilters and aggressive literal extraction, so Unicode stays on without the large slowdown GNU grep shows under a UTF-8 locale. Directory traversal uses a lock-free parallel recursive iterator (ignore crate), and gitignore globs are matched in one pass with a RegexSet. File I/O is chosen per call: hiargs.rs enables memory maps only when 10 or fewer paths are given and all are files, otherwise it reads incrementally into an intermediate buffer; mmaps get madvise(SEQUENTIAL) on Linux and are never used on macOS.

## Compared with alternatives

Among the filesystem siblings, bfs, al-dente and lsr speed up directory walking and listing, and liburing or SPDK speed up raw block I/O; pick ripgrep when the job is searching file contents, where the regex engine and the mmap-vs-buffer policy matter more than syscall throughput.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | Rust regex, memchr, ignore/globset and grep-\* crates; PCRE2 optional (pcre2 feature) |
| **Minimum toolchain** | Rust 1.96 (workspace rust-version in Cargo.toml for 15.2.0) |
| **Platforms** | Linux, macOS, Windows (memory maps disabled on macOS) |
| **Thread safety** | Multi-threaded CLI (parallel directory walk and search); library crates follow Rust Send/Sync rules |
| **Drop-in for the baseline** | partial — covers most grep options and is a drop-in for interactive use, but defaults to recursive, gitignore-filtered search and is not POSIX grep |

## Gotchas

- Binary-file detection differs between the mmap path (checks only the start of the file) and the buffered path (checks every buffer), so results can differ unless you pass --no-mmap
- The mmap choice is a CLI heuristic (10 or fewer paths, all regular files); the grep-searcher crate defaults to MmapChoice::never(), and MmapChoice::auto() is unsafe
- macOS never uses memory maps: in the PR #3246 discussion the maintainer measured a 3.5GB file at 7.5s without mmap vs 26.7s with mmap plus sequential advice
- -n (line numbers) raises the 13GB single-file time from 1.042s to 1.664s

## Caveats and trade-offs

Search-engine speed dominates, not file I/O alone; it is a CLI tool, not a library (reuse is through the grep-\* / ignore crates). The README benchmark is a single first-party run with no compiler or flags stated. mmap numbers come from a burntsushi.net blog snippet only. MIT OR Unlicense is OSI-approved; the Unlicense option is a public-domain-style dedication with no patent grant.

Rust CLI, not callable from C++ as a library; the I/O insight (mmap slower across many files) is the reusable part.

## Maintenance

Actively maintained (15.2.0, last commit 2026-08-04), MIT OR Unlicense, widely packaged; usable as a tool, not as a C++ library.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** The README quick benchmark compares rg with git grep, ag and GNU grep on the Linux kernel tree on an Intel i9-12900K, but gives no compiler or flags and is first-party, so C. The mmap-versus-buffer numbers are from the blog, which was not opened.
- **Verifier notes:** MIT OR Unlicense is OSI-approved, so usability moves from reference to copyable. 68.9k stars; last commit 2026-08-04 (ignore-0.4.33) confirmed on the commits page.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `usability`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/BurntSushi/ripgrep>
  - <https://github.com/BurntSushi/ripgrep/commits>
  - <https://raw.githubusercontent.com/BurntSushi/ripgrep/HEAD/README.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/BurntSushi/ripgrep/HEAD/README.md>
  - <https://raw.githubusercontent.com/BurntSushi/ripgrep/HEAD/FAQ.md>
  - <https://raw.githubusercontent.com/BurntSushi/ripgrep/HEAD/GUIDE.md>
  - <https://raw.githubusercontent.com/BurntSushi/ripgrep/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/BurntSushi/ripgrep/HEAD/crates/searcher/src/searcher/mmap.rs>
  - <https://raw.githubusercontent.com/BurntSushi/ripgrep/HEAD/crates/searcher/src/searcher/mod.rs>
  - <https://raw.githubusercontent.com/BurntSushi/ripgrep/HEAD/crates/core/flags/defs.rs>
  - <https://raw.githubusercontent.com/BurntSushi/ripgrep/HEAD/crates/core/flags/hiargs.rs>
  - <https://raw.githubusercontent.com/BurntSushi/ripgrep/HEAD/benchsuite/benchsuite>
  - <https://github.com/BurntSushi/ripgrep/pull/3246>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/burntsushi/ripgrep`) · [data/wave11/enrich/raw/github_com_burntsushi_ripgrep.json](../../../data/wave11/enrich/raw/github_com_burntsushi_ripgrep.json) (enrichment confidence 0.75)

</details>
