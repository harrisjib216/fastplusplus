# diskus

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Filesystems and I/O](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0 OR MIT` · 🟢 active

> Parallel Rust replacement for du -sh that prints one directory total; author measured 10x faster cold-cache, 2.2x warm.

| | |
|---|---|
| **Beats** | GNU du -sh |
| **Claimed result** | Cold cache 1.746s vs du -sh 17.776s (10.18x); warm cache 500.3ms vs 1098.3ms (2.20x) |
| **Workload** | Total size of a 15GB folder (100k directories, 400k files), hyperfine, cold and warm cache |
| **Metric** | latency |
| **Hardware** | 8-core laptop (CPU model not stated) |
| **Adoption** | 1.3k stars |
| **Last commit** | 2026-02-14 |
| **Links** | [repository](https://github.com/sharkdp/diskus) · [benchmark](https://github.com/sharkdp/diskus) |

## Verdict

First-party hyperfine runs on the author's unnamed 8-core laptop over a private 15 GB folder (100k directories, 400k files): cold cache (drop_caches before each run) diskus 1.746 s vs du -sh 17.776 s (10.18x), warm cache 500.3 ms vs 1098.3 ms (2.20x, despite the prose saying more than 3x); CPU model, disk, filesystem, du version and diskus version are not stated.

## Use it when

- Getting one total size for a large tree (hundreds of thousands of files) on SSD/NVMe with a cold page cache, where serial du stalls on metadata latency
- Scripts and prompts that only need a byte count: output switches to a bare number when piped
- Multi-core machines; the default 3x-cores worker count was tuned for both cold and warm caches
- Embedding a fast parallel du-style total in a Rust program through the library API

## Skip it when

- Small trees: issue #38 reports diskus 115.8 ms vs du -sch 22.8 ms on a \~4.5 GB build directory, because thread-pool startup dominates
- Very deep directory nesting: open issue #27 (since 2019) reports a stack overflow from the recursive walk
- When you need a per-subdirectory breakdown, depth limits, excludes or interactive browsing (use pdu, gdu, dust or ncdu)
- When you need to stay on one filesystem or follow symlinks: no -x / one-file-system option, and following symlinks is an open request (#44)
- Windows totals that must not double count: hard links and junctions are counted multiple times there by design

## How it is fast

It runs symlink_metadata (lstat) and read_dir calls in parallel on a rayon thread pool sized at 3x the CPU count (capped at 64), recursing with into_par_iter over each directory's children, and sends sizes over a crossbeam channel to one summing thread. Oversubscribing threads keeps many metadata requests in flight so the kernel I/O scheduler can reorder them on a cold cache; GNU du issues them one at a time. Hard links are counted once through a (device, inode) HashSet, but only for files with nlink &gt; 1.

## Compared with alternatives

Pick diskus over pdu, gdu or zdu when you want only a single total from the smallest tool; the gdu README itself notes diskus is faster at that, while pdu and gdu give per-directory trees and zdu reports faster runs than dust on its own trees.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | rayon 1.11, crossbeam-channel 0.5; clap, humansize, num-format for the CLI feature |
| **Minimum toolchain** | Rust 1.80 per Cargo.toml rust-version (README still says 1.76) |
| **Platforms** | Linux, macOS, Windows, Haiku and other Unix (packages for Debian, Arch, Void, Homebrew, MacPorts, NixOS) |
| **Thread safety** | Library call spawns its own rayon pool and receiver thread per count(); no shared global state documented |
| **Drop-in for the baseline** | partial — matches du -sh / du -sb totals for a path, but supports none of du's other flags |

## Gotchas

- Default count is disk usage (since v0.6); -b switches to apparent size, and v0.9.0 changed whether directory entries are counted to match du, so totals from older versions differ
- Errors (unreadable directories, missing metadata) are hidden unless --verbose is passed, so a permission problem silently shrinks the total
- Spawns up to 64 threads by default; on shared or throttled hosts pass --threads (-j) explicitly
- Hard-link deduplication keeps a HashSet of every multi-link inode in memory

## Known shortcomings

- Open issue 27 (stack overflow on deep trees) and 38 (5x slower than du on a small tree: 115.8 vs 22.8 ms). README says Rust 1.76 while Cargo.toml says 1.80. Rust, not C++.

## Caveats and trade-offs

First-party hyperfine runs on the author's '8-core laptop'; CPU model, disk type, filesystem and du version not stated; the 15 GB test folder is not published. README prose says 'more than three times faster with a warm disk cache' but its own table shows 2.20x. Rust tool (CLI), not a C++ library; gain comes from parallel directory traversal, so it shrinks on few cores or slow single-queue disks.

Total size only, no per-directory breakdown; Rust.

## Maintenance

Maintained by the author of fd and hyperfine (v0.9.0, last commit 2026-02-14, 1.3k stars), dual MIT/Apache-2.0 and widely packaged; the deep-tree stack overflow (#27) is still open.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** README Benchmark section shows hyperfine tables against du -sh (cold 1.746 s vs 17.776 s, 10.18x; warm 500.3 ms vs 1098.3 ms, 2.20x) with the exact hyperfine commands, but the test folder is private and CPU model, storage and build flags are not stated; first-party, so C.
- **Verifier notes:** Metadata from github.com: Apache-2.0 OR MIT, 1.3k stars, last commit 2026-02-14, not archived. Numbers match the record exactly.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** first-party README
- **Pages the verifier opened:**
  - <https://github.com/sharkdp/diskus>
  - <https://github.com/sharkdp/diskus/commits>
  - <https://raw.githubusercontent.com/sharkdp/diskus/HEAD/README.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/sharkdp/diskus/HEAD/README.md>
  - <https://raw.githubusercontent.com/sharkdp/diskus/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/sharkdp/diskus/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/sharkdp/diskus/HEAD/src/main.rs>
  - <https://raw.githubusercontent.com/sharkdp/diskus/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/sharkdp/diskus/HEAD/src/walk.rs>
  - <https://raw.githubusercontent.com/sharkdp/diskus/HEAD/src/filesize.rs>
  - <https://raw.githubusercontent.com/sharkdp/diskus/HEAD/src/unique_id.rs>
  - <https://github.com/sharkdp/diskus/issues?q=is%3Aissue>
  - <https://github.com/sharkdp/diskus/issues/38>
  - <https://github.com/sharkdp/diskus/issues/27>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/sharkdp/diskus`) · [data/wave11/enrich/raw/github_com_sharkdp_diskus.json](../../../data/wave11/enrich/raw/github_com_sharkdp_diskus.json) (enrichment confidence 0.75)

</details>
