# Glyd

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Entropy coders](README.md)</sub>

**Tier A** (reproducible public benchmark) · Study only · `Rust` · `BSD-3-Clause OR GPL-2.0 (codec); glyd-store and GPU package under BUSL-1.1` · 🟢 active

> Rust LZ/entropy codec with a C ABI whose blocks decode in parallel; mixed one-core result against zstd -3, wins multicore reads.

| | |
|---|---|
| **Beats** | zstd -3 (also LZ4, zstd -19) |
| **Claimed result** | Suite 2026-09-21 (8.7 GB corpus of logs, JSON events, SQL dumps, Parquet), one thread, MB/s: Glyd --max ratio 3.98 decompresses 1,571 vs zstd -3 (ratio 3.86) 1,425 on Graviton3 (1.10x) but 1,287 vs 1,518 on Sapphire Rapids (0.85x, slower), and compresses at 233 vs 313 and 266 vs 377. Glyd default (ratio 2.82) decompresses 3,309 on Graviton3 and 2,752 on Sapphire Rapids vs LZ4 (ratio 2.72) 1,394 and 1,206, compressing at 332 vs 504 and 327 vs 456. Eight threads: Glyd default decompresses 22,707 MB/s and --max 10,413 vs zstd -3 1,422 and LZ4 1,392, but zstd and LZ4 frames are decoded on one thread. README summary: reads 3-7x faster than zstd on a server, writes at 0.71-0.77x zstd -3's speed. |
| **Workload** | Decompression of an 8.7 GB real-data corpus (logs, JSON events, SQL dumps, Parquet); the --max level uses 8-way interleaved Huffman literals and tANS sequences. |
| **Metric** | throughput |
| **Hardware** | AWS c7g.2xlarge (Graviton3, Neoverse V1, 8 vCPU) and c7i.2xlarge (Sapphire Rapids, Xeon Platinum 8488C, 8 vCPU), Ubuntu 24.04 |
| **Compiler and flags** | rustc 1.98, RUSTFLAGS='-C target-cpu=native', cargo release profile opt-level 3, lto fat, codegen-units 1; baselines libzstd 1.5.7 via the zstd crate (bulk API, in-process) and LZ4 via the lz4 crate's frame encoder/decoder; zstd 1.5.5 and lz4 1.9.4 CLIs from Ubuntu 24.04 for CLI rows. |
| **Adoption** | 240 stars |
| **Last commit** | 2026-10-03 |
| **Links** | [repository](https://github.com/surya-koritala/Glyd) · [benchmark](https://github.com/surya-koritala/Glyd) |

## Verdict

First-party suite of 2026-09-21 on an 8.7 GB corpus (logs, JSON events, SQL dumps, Parquet), rustc 1.98 with target-cpu=native and fat LTO, in-process libzstd 1.5.7 and the lz4 crate, on Graviton3 (c7g.2xlarge) and Xeon Platinum 8488C (c7i.2xlarge): one thread, --max decoded 1,571 vs zstd -3 1,425 MB/s on Graviton3 (1.10x) but 1,287 vs 1,518 on Sapphire Rapids (0.85x), and compressed slower on both (233 vs 313, 266 vs 377). Default decoded 3,309 and 2,752 MB/s vs LZ4 frame 1,394 and 1,206; the 8-thread figures compare parallel Glyd with single-thread zstd/LZ4 decoding.

## Use it when

- Write-once, read-many data (object storage, data lakes, release assets) where reads run on several cores per stream: Glyd's units decode in parallel while a zstd or LZ4 frame decodes on one thread.
- Logs, CSV/TSV, SQL dumps and JSON lines where record mode (-r) stores 12-61% fewer bytes than zstd -3 per the README, if read CPU is not the bill.
- Versioned blobs (nightly dumps, images, source tarballs) where --base stored 1.1-2.1x less than zstd --patch-from at the fast tier in the author's tests.
- aarch64 servers (Graviton3) where the author's one-core --max decode was 1.10x zstd -3 at a slightly better ratio (3.98 vs 3.86).

## Skip it when

- Single-threaded decode on recent Intel x86: on Sapphire Rapids --max decoded at 1,287 MB/s vs zstd -3's 1,518 (0.85x), and the README's own known-gaps list gives 0.79-0.97x there.
- Write-heavy workloads: --max compresses at 0.71-0.77x zstd -3's speed and default at about 0.66-0.72x LZ4's; record mode halves write speed again and reads cost 2-2.7x zstd's CPU.
- Anything needing interoperability: the format is Glyd-only, with no other decoder; zstd and LZ4 frames are read everywhere.
- Small objects with a dictionary: the README says sizes tie with zstd and zstd is 1.4-2x faster per object.
- Risk-averse production use: a one-author project (240 stars, 1 fork, 0 issues filed) at v0.26.0 whose formats have already gone through v6-v9, and whose store and GPU parts are BUSL-1.1 (commercial use needs a license).

## How it is fast

Input is cut into 256 KB blocks and, on the parallel paths, into independent units (one per core, up to 128 MB) so a single stream decodes on every core, which is where the 8-thread read numbers come from. The --max tier uses 8-way interleaved Huffman literals and tANS-coded sequences with repeat offsets over a double-fast parse with an 8 MB window, modeled on zstd's design; the default tier is an LZAV-class finder with a minimum match of 7 and copy-only decode loops. Match finding has an AVX2+BMI2 path chosen at run time and NEON decode/checksum paths on aarch64.

## Compared with alternatives

Over Zstandard (zstd) when reads of large objects can use several cores and you control both ends of the format; stay with zstd for one-core decode on x86, faster writes and universal readers. Over LZ4 or lzvolt only if you want a better ratio with parallel decode; for the fastest single-thread block decode, LZ4's block API, lzvolt or ZXC are the better-measured choices.

## Integration

| | |
|---|---|
| **Form** | crate (also cdylib/staticlib with C header include/glyd.h; prebuilt libraries per release) |
| **Dependencies** | none at run time for the core codec beyond Rust std; the default features pull glyd-preflate (vendored) and lepton_jpeg only to read v0.12-v0.13 container files (--no-default-features drops them); Rayon for the parallel paths |
| **Minimum toolchain** | Rust 1.80+ (README badge); benchmarks built with rustc 1.98 |
| **Platforms** | x86-64 (AVX2+BMI2 fast path, scalar fallback otherwise), aarch64 (NEON); release binaries for Linux x86_64, Linux aarch64, macOS arm64 |
| **Thread safety** | not documented for the C API; the source uses thread-local scratch tables and a process-wide thread count (glyd::set_threads, an atomic), and the \*_parallel C functions run on Rayon's global pool across all cores |
| **Drop-in for the baseline** | partial — it fills the same slot as zstd -3 / LZ4 but has its own API and an incompatible format; existing zstd/LZ4 data and readers cannot use it |

## Gotchas

- The 22.7 GB/s and 10.4 GB/s headline reads are 8-thread Glyd against single-thread zstd and LZ4 frame decoding; like for like on one core the gain over zstd -3 is 1.10x on Graviton3 and a loss on Sapphire Rapids.
- The LZ4 baseline in examples/bench_suite.rs is the lz4 crate's frame encoder at level 1 and its streaming Decoder with read_to_end, not liblz4's block API, so LZ4 decode measured only about 1.2-1.4 GB/s; the default-vs-LZ4 decode gap is likely overstated.
- Glyd verifies a CRC32C per block on decode while the zstd frames in the benchmark carry no checksum, which slightly favors zstd's decode numbers.
- include/glyd.h comments still describe --max as format v7 while the README says v9; libglyd_store (BUSL-1.1) re-exports the whole codec API, so linking the wrong library silently changes your license terms.

## Known shortcomings

- Upgraded C to A (public examples/bench_suite.rs and scripts/bench_aws_suite.sh, rustc 1.98, target-cpu=native, fat LTO, Graviton3 and Xeon 8488C), but the like-for-like gain is small: --max decode vs zstd -3 is 1.10x on Graviton3 and 0.85x on Sapphire Rapids; the 22.7 GB/s headline is 8 threads against 1, and the LZ4 baseline uses the slower streaming frame decoder. Mixed license (BUSL parts). Rust.
- The LZ4 baseline is the lz4 crate's frame encoder at level 1 with a streaming Decoder read_to_end (examples/bench_suite.rs:178-192), not the block API; Glyd checks CRC32C per block while the zstd frames carry no checksum. One-core --max decode is 0.85x zstd -3 on Sapphire Rapids (README known gaps 0.79-0.97x). Single author, 1 fork, 0 issues filed; libglyd_store (BUSL-1.1) re-exports the whole codec API; glyd.h says --max is the v7 format while the README says v9.

## Caveats and trade-offs

First party, very young repo (240 stars, 1 fork) with sweeping claims. Like-for-like (one thread, similar ratio) the decode win over zstd -3 is small and platform-dependent: 1.10x on Graviton3, 0.85x (slower) on Sapphire Rapids, and compression is slower than zstd -3 on both. The 22.7 GB/s headline compares 8-thread Glyd decoding with single-thread zstd/LZ4 frame decoding. The LZ4 baseline in examples/bench_suite.rs uses the lz4 crate's streaming frame Decoder with read_to_end, not the LZ4 block API, which likely explains LZ4 decoding at only about 1.4 GB/s; the README's 'each codec on its fastest API' does not hold for LZ4, so the LZ4 decode comparison is weak. Glyd writes a per-block checksum; zstd frames here carry none. Store and GPU parts are BUSL-1.1 (non-commercial free).

Rust library with a C ABI, callable from C++. Higher ratio than LZ4 but lower than zstd at default level; compress speed 0.77x zstd -3 and 0.33x in record mode. Large parallel-decode gain needs the parallel-friendly Glyd framing, so output is not a drop-in zstd stream.

## Maintenance

Very actively developed (1,039 commits, last commit 2026-10-03, v0.26.0) by a single author; the codec is BSD-3-Clause OR GPL-2.0 and usable commercially, but it is young, has no external users visible in the issue tracker, and the store/GPU parts are BUSL-1.1.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded from C: the benchmark code is public (examples/bench_suite.rs driven by scripts/bench_aws_suite.sh, results in docs/benchmarks/suite-2026-09-21.md and benchmarks/suite/), compiler rustc 1.98 with RUSTFLAGS='-C target-cpu=native' and a release profile of opt-level 3, fat LTO, codegen-units 1, and CPU models Graviton3 (Neoverse V1, c7g.2xlarge) and Xeon Platinum 8488C (c7i.2xlarge), against in-process libzstd 1.5.7 and LZ4. A rests on the one-thread zstd comparison; the LZ4 and 8-thread rows are weaker (see caveats).
- **Verifier notes:** README and suite numbers match the record; methodology is fully documented, so tier rises to A on the one-thread zstd rows, but the honest single-core result is mixed (faster on Graviton3, slower on Sapphire Rapids at --max); the decode lead over LZ4 rests on a frame-reader baseline. Codec license BSD-3-Clause OR GPL-2.0-only (Cargo.toml), usability mixed because of BUSL store/GPU; last commit 2026-10-03 confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/surya-koritala/Glyd>
  - <https://github.com/surya-koritala/Glyd/commits/main>
  - <https://raw.githubusercontent.com/surya-koritala/Glyd/HEAD/README.md>
  - <https://raw.githubusercontent.com/surya-koritala/Glyd/HEAD/docs/benchmarks/suite-2026-09-21.md>
  - <https://raw.githubusercontent.com/surya-koritala/Glyd/HEAD/scripts/bench_aws_suite.sh>
  - <https://raw.githubusercontent.com/surya-koritala/Glyd/HEAD/examples/bench_suite.rs>
  - <https://raw.githubusercontent.com/surya-koritala/Glyd/HEAD/Cargo.toml>
- **Sources the enricher read:**
  - <https://github.com/surya-koritala/Glyd>
  - <https://github.com/surya-koritala/Glyd/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/surya-koritala/Glyd/HEAD/README.md>
  - <https://raw.githubusercontent.com/surya-koritala/Glyd/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/surya-koritala/Glyd/HEAD/include/glyd.h>
  - <https://raw.githubusercontent.com/surya-koritala/Glyd/HEAD/docs/benchmarks/suite-2026-09-21.md>
  - <https://raw.githubusercontent.com/surya-koritala/Glyd/HEAD/examples/bench_suite.rs>
  - <https://raw.githubusercontent.com/surya-koritala/Glyd/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/surya-koritala/Glyd/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/surya-koritala/Glyd/HEAD/SECURITY.md>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/surya-koritala/glyd`) · [data/wave9/enrich/raw/github_com_surya_koritala_glyd.json](../../../data/wave9/enrich/raw/github_com_surya_koritala_glyd.json) (enrichment confidence 0.7)

</details>
