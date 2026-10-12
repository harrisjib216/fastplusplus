# parallel-disk-usage (pdu)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Filesystems and I/O](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0` · 🟢 active

> Rust disk-usage analyzer (pdu) that walks directories in parallel with rayon; about 2.2x faster than GNU du warm-cache.

| | |
|---|---|
| **Beats** | GNU du (also dust, dua, ncdu, gdu) |
| **Claimed result** | pdu v0.20.0 vs du on the workflow's tmp.sample tree (hyperfine means): block-size 88.2 ms vs du --count-links 196.8 ms (2.23x), dust 110.9 ms (1.26x), gdu 168.4 ms (1.91x), ncdu 205.7 ms (2.33x), dua 231.0 ms (2.62x); with --deduplicate-hardlinks 88.3 ms vs du 196.9 ms (2.23x). |
| **Workload** | Disk usage scan of a generated sample directory tree (tmp.sample) on a GitHub Actions runner, warm cache, measured with hyperfine; block-size and hardlink-deduplication modes among others. |
| **Metric** | throughput |
| **Hardware** | GitHub Actions runners (CPU model not stated) |
| **Adoption** | 738 stars |
| **Last commit** | 2026-08-09 |
| **Links** | [repository](https://github.com/KSXGitHub/parallel-disk-usage) · [benchmark](https://github.com/KSXGitHub/parallel-disk-usage-0.20.0-benchmarks) |

## Verdict

Project CI (deploy.yaml) runs hyperfine --warmup=1 on a GitHub-hosted ubuntu-latest runner (CPU model not stated) over an unzipped Linux v5.12 source tree plus a small hardlink tree: pdu 0.20.0 block-size 88.2 ms vs du --count-links 196.8 ms (2.23x), dust 110.9 ms, gdu 168.4 ms, ncdu 205.7 ms, dua 231.0 ms; with hardlink dedup 88.3 ms vs du 196.9 ms. This is warm cache only; there is no cold-cache or HDD number.

## Use it when

- Interactive 'where did my disk space go' scans on SSD/NVMe or warm page cache, where parallel stat calls pay off.
- Trees with tens of thousands or more files (the benchmark is a Linux v5.12 source checkout) on multi-core machines.
- When you want a sorted, depth-limited chart or JSON output to pipe into other tools instead of du's flat listing.
- When hardlinks must be counted once: --deduplicate-hardlinks cost nothing measurable in the 0.20.0 benchmark (88.3 ms vs 88.2 ms without it).

## Skip it when

- Spinning disks: issue #257 measured pdu at 1m18s vs du 47s on an HDD with 150,000 files because parallel traversal adds seeks; pdu now detects HDDs and drops to 1 thread, so expect no gain there.
- Very large volumes with tens of millions of files: open issue #277 reports pdu being killed at random points after 28-62 million files (about 6 GB RSS) with no diagnosis yet.
- Scripts that parse du's output format or need du flags (--exclude, --time, -s semantics); pdu is a different CLI.
- Copy-on-write filesystems where reflinks matter (pdu ignores reflinks), or trees reached through symlinks (not followed).
- C++ projects wanting an in-process library: this is a Rust crate with no C API.

## How it is fast

TreeBuilder recurses into each directory and maps its children through rayon's into_par_iter, so lstat (std::fs::symlink_metadata) and read_dir calls for sibling entries run on a work-stealing thread pool instead of du's single-threaded fts walk. Per-entry metadata is dropped immediately and only the size plus child names are kept; hardlink records go into a concurrent dashmap. Below --max-depth (default 10) children are summed rather than stored, which bounds the tree kept in memory.

## Compared with alternatives

Pick pdu over diskus when you need a per-directory breakdown rather than one total, and over gdu when you want a non-interactive chart/JSON and its own benchmark shows it ahead (88 ms vs gdu 168 ms); zdu's own README shows pdu -H ahead of it on a 57k-file tree (14.0 ms vs 19.6 ms), so pdu is a reasonable default among the Rust du-likes.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | rayon, dashmap, sysinfo, derive_more, itertools and other crates; clap and serde_json behind the default cli/json features |
| **Minimum toolchain** | Rust edition 2024; repo pins toolchain 1.97.1 |
| **Platforms** | Linux, macOS, Windows release binaries; block-size/block-count quantities and hardlink handling are POSIX-only |
| **Thread safety** | Uses a global rayon pool; the CLI sets its size from --threads (auto, max or a number). Library thread-safety guarantees beyond Send/Sync bounds are not documented. |
| **Drop-in for the baseline** | partial: computes the same sizes as du (block-size default, du-style hardlink dedup via --deduplicate-hardlinks) but prints a chart or JSON, not du's format |

## Gotchas

- --threads=auto silently becomes 1 thread when any target path is on a detected HDD (prints a warning); pass --threads=max to override.
- Without --deduplicate-hardlinks, every hardlink is counted as real size (like du --count-links), so totals differ from plain du.
- Hardlink dedup with several path arguments removes overlapping paths first; the JSON root is '(total)' when two or more paths are given.
- The published benchmark is for v0.20.0 while the crate is now 0.24.0; the README has not been rerun for newer versions.

## Known shortcomings

- The benchmark tree is unzipped Linux v5.12 source plus a small hardlink tree, hyperfine --warmup=1, warm cache only, on an ubuntu-latest runner; the measured version is 0.20.0 (crate now 0.24.0). pdu is slower than du on HDD (issue 257: 1m18s against 47s), so auto mode now drops to one thread on HDD; open issue 277: pdu is killed at random after 28-62M files (about 6 GB RSS), undiagnosed. Rust, not C++.

## Caveats and trade-offs

First-party benchmark from the project's own CI workflow; GitHub Actions runner CPU model not stated; sample tree is small (\~0.2 s for du). The 299.1 ms / 1255.2 ms and 1.061 s figures in the search record came from snippets of other releases and were not verified; replaced with the 0.20.0 report tables. Gain over du is from parallel traversal. Rust CLI, not a C++ library.

Rust CLI/library crate, not callable from C++ directly; output is a chart tree.

## Maintenance

Actively maintained (v0.24.0, signed release attestations since 0.23.0, packaged in Arch extra), Apache-2.0; usable as a CLI or Rust library but not from C++.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification B, tier now C.
- **Tier reason:** First-party hyperfine benchmark run by the project's own GitHub workflow (.github/workflows/deploy.yaml, results in KSXGitHub/parallel-disk-usage-0.20.0-benchmarks); public code but CPU model not stated and not independent, so C, not B.
- **Verifier notes:** Opened tmp.benchmark-report.competing.block-size.md and .deduplicate-hardlinks.md (raw) in the 0.20.0 benchmarks repo; claimed snippet numbers not on those pages, so replaced. License Apache-2.0, last commit 2026-08-09, 738 stars confirmed.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `baseline`, `workload`, `caveats`
- **Shortcomings recorded by:** first-party CI hyperfine
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/KSXGitHub/parallel-disk-usage/HEAD/README.md>
  - <https://raw.githubusercontent.com/KSXGitHub/parallel-disk-usage/HEAD/LICENSE>
  - <https://github.com/KSXGitHub/parallel-disk-usage/commits>
  - <https://github.com/KSXGitHub/parallel-disk-usage-0.20.0-benchmarks>
  - <https://raw.githubusercontent.com/KSXGitHub/parallel-disk-usage-0.20.0-benchmarks/HEAD/tmp.benchmark-report.competing.block-size.md>
  - <https://raw.githubusercontent.com/KSXGitHub/parallel-disk-usage-0.20.0-benchmarks/HEAD/tmp.benchmark-report.competing.deduplicate-hardlinks.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/KSXGitHub/parallel-disk-usage/HEAD/README.md>
  - <https://raw.githubusercontent.com/KSXGitHub/parallel-disk-usage/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/KSXGitHub/parallel-disk-usage/HEAD/rust-toolchain>
  - <https://raw.githubusercontent.com/KSXGitHub/parallel-disk-usage/HEAD/USAGE.md>
  - <https://raw.githubusercontent.com/KSXGitHub/parallel-disk-usage/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/KSXGitHub/parallel-disk-usage/HEAD/src/fs_tree_builder.rs>
  - <https://raw.githubusercontent.com/KSXGitHub/parallel-disk-usage/HEAD/src/tree_builder.rs>
  - <https://raw.githubusercontent.com/KSXGitHub/parallel-disk-usage/HEAD/src/get_size.rs>
  - <https://raw.githubusercontent.com/KSXGitHub/parallel-disk-usage/HEAD/src/hardlink.rs>
  - <https://raw.githubusercontent.com/KSXGitHub/parallel-disk-usage/HEAD/src/app.rs>
  - <https://raw.githubusercontent.com/KSXGitHub/parallel-disk-usage/HEAD/.github/workflows/deploy.yaml>
  - <https://raw.githubusercontent.com/KSXGitHub/parallel-disk-usage/HEAD/ci/github-actions/competing-benchmark.ts>
  - <https://raw.githubusercontent.com/KSXGitHub/parallel-disk-usage/HEAD/ci/github-actions/benchmark/matrix.ts>
  - <https://raw.githubusercontent.com/KSXGitHub/parallel-disk-usage/HEAD/ci/make-tree-with-hardlinks.sh>
  - <https://github.com/KSXGitHub/parallel-disk-usage/tree/master/ci/github-actions>
  - <https://raw.githubusercontent.com/KSXGitHub/parallel-disk-usage-0.20.0-benchmarks/HEAD/tmp.benchmark-report.competing.block-size.md>
  - <https://raw.githubusercontent.com/KSXGitHub/parallel-disk-usage-0.20.0-benchmarks/HEAD/tmp.benchmark-report.competing.deduplicate-hardlinks.md>
  - <https://raw.githubusercontent.com/KSXGitHub/parallel-disk-usage-0.20.0-benchmarks/HEAD/tmp.benchmark-report.CHARTS.md>
  - <https://github.com/KSXGitHub/parallel-disk-usage/issues?q=is%3Aissue+performance+OR+slow+OR+bug>
  - <https://github.com/KSXGitHub/parallel-disk-usage/issues/277>
  - <https://github.com/KSXGitHub/parallel-disk-usage/issues/257>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/ksxgithub/parallel-disk-usage`) · [data/wave11/enrich/raw/github_com_ksxgithub_parallel_disk_usage.json](../../../data/wave11/enrich/raw/github_com_ksxgithub_parallel_disk_usage.json) (enrichment confidence 0.8)

</details>
