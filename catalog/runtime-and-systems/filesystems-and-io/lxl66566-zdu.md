# zdu

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Filesystems and I/O](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> Parallel Rust disk-usage CLI with a dust-style tree chart; 2.7-10x faster than dust, mixed against pdu.

| | |
|---|---|
| **Beats** | dust and pdu (disk usage tools built on parallel stat/readdir) |
| **Claimed result** | Linux: \~/.cargo (57k files) 19.6 ms vs dust 202.2 ms (10.3x faster) but vs pdu -H 14.0 ms (1.40x slower); \~/programs (509k files) 143.8 ms vs dust 388.2 ms (2.7x) and pdu -H 228.3 ms (1.6x); /nix/store (1.2M files) 402.7 ms vs dust 1.118 s (2.8x) and pdu -H 1.401 s (3.5x). Windows 10/NTFS: 2.7-7.4x faster than dust and 2.0-6.2x faster than pdu (pdu without -H). |
| **Workload** | Disk usage scan of \~/.cargo (57k files), \~/programs (509k files) and /nix/store (1.2M files), hyperfine, warm page cache, 32 logical cores. |
| **Metric** | throughput |
| **Hardware** | 32 logical cores (CPU model not stated) |
| **Adoption** | 0 stars |
| **Last commit** | 2026-09-18 |
| **Links** | [repository](https://github.com/lxl66566/zdu) · [benchmark](https://github.com/lxl66566/zdu#benchmark) |

## Verdict

Author's hyperfine runs with warm page cache on 32 logical cores (CPU not named): on Linux, zdu 19.6/143.8/402.7 ms vs dust 1.2.4 at 202.2 ms/388.2 ms/1.118 s and pdu 0.21.1 -H at 14.0/228.3/1401 ms for 57k, 509k and 1.2M files; on Windows 10/NTFS 2.7-7.4x over dust 1.2.3 and 2.0-6.2x over pdu 0.24.0 without -H. Release build uses LTO and codegen-units=1; no other flags or harness published.

## Use it when

- Interactive disk-usage inspection where you want dust's tree chart but faster on large trees (hundreds of thousands to millions of files).
- Link-heavy trees such as /nix/store, where the README shows 402.7 ms vs pdu -H 1.401 s and dust 1.118 s.
- Windows/NTFS scans: README shows 2.7-7.4x over dust and 2.0-6.2x over pdu on 7.6k-163k file trees.
- Many-core machines with warm page cache, the only setting measured (32 logical cores).

## Skip it when

- Small trees on Linux: pdu -H beat it on \~/.cargo (14.0 ms vs 19.6 ms).
- When you need a library to embed in a C++ program; this is a Rust binary.
- Cold-cache or spinning-disk scans: not benchmarked; diskus and gdu siblings publish cold-cache numbers.
- When you need exact GNU du semantics: allocated size is capped heuristically (blocks\*512 replaced by size rounded to blksize when it exceeds that by more than 65536 blocks), and Windows counts plain-file hard links once per link.
- Production use requiring maturity: 0 stars, first commits and release all in September 2026.

## How it is fast

The walk runs as flat rayon scope tasks (no recursion): each directory is read once into a Vec, entries are processed with into_par_iter clamped to a 64-entry minimum leaf, and each subdirectory spawns its own task that bubbles its node up via an atomic pending counter. Hard-link dedup uses a 256-shard Mutex&lt;HashSet&lt;(inode, device)&gt;&gt; sharded on the inode, which the source says cut /nix/store from 818 ms to 631 ms versus a device-keyed shard; directories are classified from readdir d_type instead of an extra stat. On Windows, DirEntry::metadata() reuses the FindNextFile data so plain entries need no per-file stat.

## Compared with alternatives

Pick zdu over pdu (parallel-disk-usage) when you want dust's tree output, are on Windows, or scan link-heavy trees; pick pdu for small Linux trees and diskus when you only need a single total, since diskus publishes cold-cache numbers and zdu does not.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | rayon, clap, regex, serde/serde_json, chrono, lscolors, nu-ansi-term, terminal_size, config-file, ctrlc, stfu8, thousands, unicode-width; on Windows filesize and winapi-util |
| **Minimum toolchain** | Rust 1.85 (edition 2024) |
| **Platforms** | Linux/Unix and Windows (both benchmarked); macOS not documented |
| **Thread safety** | not applicable (CLI); internally multithreaded via rayon |
| **Drop-in for the baseline** | partial — CLI flags largely follow dust (it is a dust port), but not pdu's flags or output format; installed crate name is zdu-rs, binary zdu |

## Gotchas

- The README links pdu to XAMPPRocky/pdu, but the versions benchmarked (0.21.1, 0.24.0) and the -H/--deduplicate-hardlinks flag match KSXGitHub/parallel-disk-usage.
- No benchmark script is published; the tables give hyperfine means only, with no CPU model or variance.
- Every regular entry's (inode, device) goes into the dedup set in default mode, not only entries with link count above 1, so memory grows with file count; -s (apparent size) skips dedup.
- zdu renders a full tree while pdu prints a flat list, so the comparison is not output-equivalent (README argues this favors pdu).

## Known shortcomings

- No benchmark script and no CPU model. The README links pdu to XAMPPRocky/pdu, but the versions (0.21.1, 0.24.0) and the -H flag match KSXGitHub/parallel-disk-usage. Loses to pdu -H on \~/.cargo (14.0 vs 19.6 ms). Rust, not C++.

## Caveats and trade-offs

Brand-new, first-party, 0 stars. Warm page cache only; no CPU model, no published benchmark script. Loses to pdu on the smallest Linux tree. Its win over pdu on /nix/store comes from pdu's hard-link dedup scaling badly. The 3.5x figure is against pdu; against dust it is 2.8x.

Rust CLI; not a C++ library; baselines are other fast tools, not du.

## Maintenance

Active (88 commits, last 2026-09-18) but brand-new with 0 stars; MIT OR Apache-2.0, installable with cargo install, usable as a CLI tool rather than copyable library code.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party hyperfine tables in the README against dust and pdu, with warm cache and 32 logical cores. No CPU model, no compiler flags and no published benchmark script, so C.
- **Verifier notes:** The record misattributed 3.5x to the dust comparison on /nix/store (it is 2.8x vs dust and 3.5x vs pdu); I added the dust 10.3x row and the Windows table. License MIT OR Apache-2.0 confirmed in Cargo.toml; last commit 2026-09-18.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** first-party README
- **Pages the verifier opened:**
  - <https://github.com/lxl66566/zdu>
  - <https://github.com/lxl66566/zdu/commits>
  - <https://raw.githubusercontent.com/lxl66566/zdu/HEAD/README.md>
  - <https://raw.githubusercontent.com/lxl66566/zdu/HEAD/Cargo.toml>
- **Sources the enricher read:**
  - <https://github.com/lxl66566/zdu>
  - <https://github.com/lxl66566/zdu/commits>
  - <https://github.com/lxl66566/zdu/tree/main/src>
  - <https://raw.githubusercontent.com/lxl66566/zdu/HEAD/README.md>
  - <https://raw.githubusercontent.com/lxl66566/zdu/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/lxl66566/zdu/HEAD/src/dir_walker.rs>
  - <https://raw.githubusercontent.com/lxl66566/zdu/HEAD/src/platform.rs>
  - <https://raw.githubusercontent.com/lxl66566/zdu/HEAD/src/node.rs>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/lxl66566/zdu`) · [data/wave11/enrich/raw/github_com_lxl66566_zdu.json](../../../data/wave11/enrich/raw/github_com_lxl66566_zdu.json) (enrichment confidence 0.6)

</details>
