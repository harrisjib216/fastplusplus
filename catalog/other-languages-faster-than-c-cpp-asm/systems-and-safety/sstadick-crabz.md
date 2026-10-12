# crabz (Rust pigz-style compressor on gzp, pure-Rust deflate backend)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Unlicense OR MIT` · 🟢 active

> pigz-style parallel gzip/zlib/BGZF/Mgzip/Snappy CLI in Rust on the gzp crate; pure-Rust backend edges pigz 2.4.

| | |
|---|---|
| **Beats** | pigz v2.4 (C, Ubuntu 20 apt package) |
| **Claimed result** | README takeaways: crabz with the rust backend is roughly 5-10% faster than pigz (zlib backend identical, zlib-ng backend 30-50% faster). Rust-backend table (mean seconds): level 3, 1 thread 10.167 vs pigz 11.338 (1.11x, derived from page data); level 3, 32 threads 0.547 vs 0.755 (1.38x); level 9, 1 thread 44.907 vs 53.109 (1.18x); level 9, 32 threads 1.747 vs 2.086 (1.19x); level 6 is a tie (27.064 vs 27.034 at 1 thread, 1.192 vs 1.196 at 32). Decompression 1.599-1.615 s vs pigz 1.696-1.767 s (1.06-1.11x). |
| **Workload** | Parallel gzip compression at levels 3, 6, 9 with 1 to 32 threads, and gzip decompression, of the bench-data text catted together 100 times, timed with hyperfine. |
| **Metric** | throughput |
| **Hardware** | Ubuntu 20, AMD Ryzen 9 3950X 16-core, 64 GB DDR4, 1 TB NVMe |
| **Compiler and flags** | cargo build --release --no-default-features --features deflate_rust,libdeflate,snap_default (benchmark.sh; default release profile, no [profile.release] overrides); rustc version for the original run not stated (repo now pins 1.97.1 in rust-toolchain.toml). The README tables use 'crabz -p N -c L &lt; data.txt' while the current benchmark.sh runs 'crabz -p N -l L -f gzip ./data.txt', so the tables came from an earlier script revision. Every build, the deflate_rust one included, installs mimalloc (C) as #[global_allocator] (src/main.rs; also present in the v0.7.0 and v0.10.0 Cargo.toml). pigz is the Ubuntu 20 apt binary with unstated flags. hyperfine --warmup 3 --runs 3. Decompression inputs are made by system gzip -3/-6/-9. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Adoption** | 375 stars |
| **Last commit** | 2026-08-19 |
| **Links** | [repository](https://github.com/sstadick/crabz) · [benchmark](https://raw.githubusercontent.com/sstadick/crabz/HEAD/README.md) |

## Verdict

First-party hyperfine runs (3 warmups, 3 runs) on a Ryzen 9 3950X under Ubuntu 20 compressed bench-data catted 100 times. crabz built with the miniz_oxide backend ran 1.11x faster than apt pigz 2.4 at level 3 on one thread, 1.38x at 32 threads and 1.18-1.19x at level 9, tied at level 6, and decompressed 1.06-1.11x faster. Compressed sizes were not reported, and at -p &gt;= 2 crabz skipped the per-block dictionary that pigz uses, so equal output quality is not shown.

## Use it when

- You want pigz-class multi-threaded gzip compression from a single static binary that also builds on Windows, installed via cargo, Homebrew, conda-forge or a .deb.
- Bioinformatics pipelines that need BGZF or Mgzip output with multi-threaded block decompression (libdeflate backend), where the README shows crabz ahead of bgzip and pigz on compression at most thread counts.
- Rust programs that need parallel gzip writing: use the gzp crate directly (about 2.56M crates.io downloads) rather than shelling out to pigz.
- Builds that must avoid C zlib: the deflate_rust feature gives miniz_oxide for gzip/deflate, about 1.1x faster than pigz 2.4 at level 3 on one thread and a tie at level 6.

## Skip it when

- When compression ratio matters at a given level: the pure-Rust backend's level 9 searches much less than zlib's and its parallel blocks start with an empty window, and no compressed sizes were published, so compare output sizes before switching.
- Plain gzip decompression speed: crabz -d on a regular .gz is single-threaded flate2 MultiGzDecoder; the README gain over pigz -d is only 1.06-1.11x, and ISA-L or libdeflate-based tools are the faster choice (issue #22 asks for ISA-L).
- If you expect a pure-Rust binary: the default build is zlib-ng plus libdeflate (C), and current releases install the C mimalloc allocator as #[global_allocator] in every feature set.
- Scripts written for gzip/pigz flag semantics: no -k/--keep (issue #30 open), no --no-name (#21 open), -I deletes the input, and the README says -d may change.
- Old toolchains or old distros: current crabz is edition 2024 with let-chains and pins Rust 1.97.1; a CentOS 7 build failure (#10) is still open.

## How it is fast

pigz's design ported to Rust: the caller thread reads 128 KB chunks, N compressor threads each deflate a chunk with a Sync flush and compute its CRC32, and a writer thread emits blocks in order while combining CRCs. With -p 1 it switches to a plain single-stream flate2 GzEncoder. The rust-backend win over pigz comes from miniz_oxide's cheaper match search (greedy at levels &lt;= 3, 768 probes at level 9 versus zlib's max_chain 4096) and, at -p &gt;= 2, from skipping pigz's 32 KB dictionary priming, not from a new algorithm.

## Compared with alternatives

Pick crabz/gzp over zipir when you need multi-threaded gzip or BGZF output and a pigz-like workflow; zipir's catalogued wins are single-threaded whole-command times against zlib-ng, ISA-L and bgzip. Pick it over libbzip2-rs, bzip2z or snap (rust-snappy) only when the format must be gzip-compatible; those siblings target bzip2 and Snappy.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | gzp 2.0.4 (flate2 with zlib-ng, zlib or miniz_oxide; libdeflater; snap; flume; core_affinity), mimalloc, structopt, strum, num_cpus, env_logger |
| **Minimum toolchain** | Rust edition 2024 with let-chains (Rust 1.88+ in practice); repo pins 1.97.1 in rust-toolchain.toml |
| **Platforms** | Linux, macOS and Windows per the README; thread pinning (-P) depends on core_affinity and is skipped with a warning where unsupported |
| **Thread safety** | CLI tool; gzp writers are Send and own their worker threads, concurrent use of one writer is not documented |
| **Drop-in for the baseline** | partial: emits standard multi-member-compatible gzip that gzip/pigz can read, but CLI flags differ from pigz (-l not -N, no -k, stdout default) and level numbers mean different effort on the Rust backend |

## Gotchas

- Harness flaw behind the rust-backend rows at -p &gt;= 2: gzp sets needs_dict() = cfg!(feature = "any_zlib"), so with deflate_rust every 128 KB block is compressed with no 32 KB dictionary from the previous block, while pigz primes each block. This was already so in gzp 0.7.2, the version the README-era crabz (v0.4.0) used. The parallel rows therefore do less work and produce larger output than pigz, and the README gives no sizes. The data fit this: level 6 is a tie at -p 1 (27.064 vs 27.034 s) but crabz wins 1.10x at -p 2 (12.400 vs 13.619 s), and crabz's own -p 1 to -p 2 speedup is 2.18x against pigz's 1.99x (derived from page data).
- -p 1 and -p &gt;= 2 run different code: ZBuilder uses a single-stream flate2 GzEncoder (SyncZ) for 0 or 1 threads and ParCompress (N compressor threads plus a writer thread) otherwise. That explains the superlinear 44.907 s to 19.977 s jump at level 9. The default -p is the logical CPU count.
- miniz_oxide levels are not zlib levels: flate2 level 9 maps to NUM_PROBES[9] = 768 (1500 is level 10, not 9) against zlib's level-9 max_chain of 4096, and levels &lt;= 3 use greedy parsing. The 1.18-1.19x level-9 wins likely trade compression ratio for speed.
- The README tables use the old '-c level' flag of crabz v0.4.0 (gzp 0.7.2, August 2021), whose Cargo.toml had no mimalloc. So the measured 'all Rust' build probably used the system allocator, and the current builds that link mimalloc were never benchmarked. In v0.7.0 the zlib-ng backend wrote corrupt gzip at level 1 on incompressible input (issue #11, output buffer too small); v0.7.1 fixed it.

## Known shortcomings

- deflate_rust is miniz_oxide, whose level 9 searches 1500 probes against zlib's max_chain 4096 with no compressed sizes reported; level 6 is a tie; README tables come from an older benchmark.sh; rustc and pigz flags unstated; the 'pure Rust' build still links C mimalloc; pigz is listed (wave 9).
- Harness flaw: gzp gates its 32 KB dictionary priming on the any_zlib feature (needs_dict() = cfg!(feature = "any_zlib"), same in the README-era gzp 0.7.2), so deflate_rust blocks at -p &gt;= 2 start with an empty window while pigz primes each block: less work and bigger output, with no sizes published; the data fit (level 6 tie at -p 1, 27.064 vs 27.034 s, 1.10x at -p 2; -p 1 runs the separate SyncZ path). Corrections: miniz_oxide level 9 is 768 probes (1500 is level 10); the README tables use v0.4.0's -c flag and the v0.4.0 Cargo.toml has no mimalloc, so the measured build probably used the pure-Rust allocator.

## Caveats and trade-offs

Not a like-for-like deflate comparison: the deflate_rust backend is miniz_oxide, whose level table (NUM_PROBES = [0,1,6,32,16,32,128,256,512,768,1500], greedy parsing at levels &lt;= 3) searches less than zlib at level 9 (1500 probes vs zlib's max_chain 4096); level 6 settings match and the level-6 result is a tie, so the 1.11x-1.38x level-3/9 wins likely buy speed with compression ratio, and the README reports no compressed sizes. crabz -p 2 at level 9 runs more than twice as fast as its own -p 1 (19.977 s vs 44.907 s), which suggests the two tools count threads differently. The 'all Rust' backend still links the C mimalloc allocator. Numbers are from the Ubuntu 20 era with pigz 2.4, three runs each; the README itself says 'none of this is groundbreaking'. Plain-gzip decompression is single-threaded flate2 MultiGzDecoder over miniz_oxide against pigz -d. [retier] gzp gates its 32 KB dictionary priming on the any_zlib feature, so deflate_rust blocks at -p &gt;= 2 start with an empty window while pigz primes each block: less work and bigger output, with no sizes published (level 6 ties at -p 1 and is 1.10x at -p 2). miniz_oxide level 9 is 768 probes (1500 is level 10). The README tables use v0.4.0, whose Cargo.toml has no mimalloc, so the measured build probably used the pure-Rust allocator.

The zlib-ng and libdeflate backends are C libraries; only the deflate_rust backend (miniz_oxide) is pure Rust. Level numbers of miniz_oxide and zlib do not mean the same compression effort.

## Maintenance

Low-activity maintenance: after the March 2024 v0.10.0 the only change is a tooling and dependency refresh released as v0.10.1 on 2026-08-19, and 10 issues remain open. It is Unlicense OR MIT, about 50k crates.io downloads; the reusable engine is gzp (2.0.4, about 2.56M downloads), and the README itself calls the results 'not groundbreaking'.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README hyperfine tables against pigz 2.4 with the CPU named (Ryzen 9 3950X) and a public benchmark.sh, but the rustc version of the run is not stated, pigz is an apt binary with unstated flags, and the README's command lines (-c level, stdin) come from an older revision of benchmark.sh than the one in the repo (-l level, file argument, extra mgzip rows), so it is not reproducible enough for A.
- **Verifier notes:** All claimed numbers match the 'Flate2 rust backend' tables (level 3 1T 10.167 vs 11.338 s, 32T 0.547 vs 0.755; level 9 1T 44.907 vs 53.109, 32T 1.747 vs 2.086; level 6 tie; decompression 1.599-1.615 vs 1.696-1.767 s). Shortcomings to record: no compressed sizes while miniz_oxide's level 9 preset does far less search than zlib's (win likely trades ratio), README tables from an older benchmark.sh revision, rustc and pigz build flags unstated, C mimalloc linked as global allocator in the 'pure Rust' build. Not a duplicate: gzp and miniz_oxide are not in the catalog; pigz is (wave 9).
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-107 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/sstadick/crabz/HEAD/README.md>
  - <https://raw.githubusercontent.com/sstadick/crabz/HEAD/benchmark.sh>
  - <https://raw.githubusercontent.com/sstadick/crabz/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/sstadick/crabz/HEAD/rust-toolchain.toml>
  - <https://raw.githubusercontent.com/sstadick/crabz/HEAD/src/main.rs>
  - <https://raw.githubusercontent.com/sstadick/crabz/v0.10.0/Cargo.toml>
  - <https://raw.githubusercontent.com/sstadick/crabz/v0.7.0/Cargo.toml>
  - <https://github.com/sstadick/crabz>
  - <https://github.com/sstadick/crabz/commits>
  - <https://raw.githubusercontent.com/Frommi/miniz_oxide/master/miniz_oxide/src/deflate/core.rs>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/sstadick/crabz/HEAD/README.md>
  - <https://raw.githubusercontent.com/sstadick/crabz/HEAD/benchmark.sh>
  - <https://raw.githubusercontent.com/sstadick/crabz/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/sstadick/crabz/HEAD/rust-toolchain.toml>
  - <https://raw.githubusercontent.com/sstadick/crabz/HEAD/src/main.rs>
  - <https://raw.githubusercontent.com/sstadick/crabz/v0.4.0/Cargo.toml>
  - <https://raw.githubusercontent.com/sstadick/crabz/v0.4.0/src/main.rs>
  - <https://raw.githubusercontent.com/sstadick/crabz/v0.3.0/Cargo.toml>
  - <https://raw.githubusercontent.com/sstadick/crabz/v0.5.0/Cargo.toml>
  - <https://github.com/sstadick/crabz/issues?q=is%3Aissue>
  - <https://github.com/sstadick/crabz/issues/1>
  - <https://github.com/sstadick/crabz/issues/11>
  - <https://github.com/sstadick/crabz/issues/14>
  - <https://github.com/sstadick/crabz/tags>
  - <https://github.com/sstadick/crabz/tags?after=v0.7.10>
  - <https://github.com/sstadick/crabz/commits>
  - <https://crates.io/api/v1/crates/crabz>
  - <https://raw.githubusercontent.com/sstadick/gzp/HEAD/README.md>
  - <https://raw.githubusercontent.com/sstadick/gzp/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/sstadick/gzp/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/sstadick/gzp/HEAD/src/deflate.rs>
  - <https://raw.githubusercontent.com/sstadick/gzp/HEAD/src/par/compress.rs>
  - <https://raw.githubusercontent.com/sstadick/gzp/v0.7.2/src/deflate.rs>
  - <https://raw.githubusercontent.com/sstadick/gzp/v0.7.2/src/lib.rs>
  - <https://raw.githubusercontent.com/sstadick/gzp/v0.7.2/Cargo.toml>
  - <https://github.com/sstadick/gzp/tags?after=v0.8.0>
  - <https://crates.io/api/v1/crates/gzp>
  - <https://raw.githubusercontent.com/Frommi/miniz_oxide/master/miniz_oxide/src/deflate/core.rs>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/sstadick/crabz`) · [data/wave14/enrich/raw/github_com_sstadick_crabz.json](../../../data/wave14/enrich/raw/github_com_sstadick_crabz.json) (enrichment confidence 0.75)

</details>
