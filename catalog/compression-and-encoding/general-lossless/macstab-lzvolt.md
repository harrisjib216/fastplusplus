# lzvolt

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust (hand-written assembly decoders; C header and cdylib/staticlib callable from C++)` · `Apache-2.0` · 🟢 active

> LZ77 codec for small cache/record values whose hand-written per-CPU decoders read 14-83% faster than liblz4.

| | |
|---|---|
| **Beats** | LZ4 (liblz4 decode and pack) |
| **Claimed result** | Decoding own format, GiB/s and margin over liblz4: varied 64 KiB 7.01 (+72%) Xeon 8481C, 8.40 (+64%) EPYC 9B14, 8.15 (+83%) Neoverse V2; records 512 B 9.44 (+29%), 10.78 (+33%), 10.60 (+22%); 18 of 18 cells +14% to +83%. Reading raw LZ4 blocks: ahead on 20 of 27 cells. Packing: ahead on 25 of 27 and smaller output. |
| **Workload** | Decode throughput on small values (records and varied data of 512 B, 4 KiB, 64 KiB, plus incompressible noise), codec vs liblz4 on its own format, same bytes and process, medians of three runs on three machines. |
| **Metric** | throughput |
| **Hardware** | Google Cloud c3-standard-4 (Intel Xeon 8481C), c3d-standard-4 (AMD EPYC 9B14), c4a-standard-4 (Google Axion, Neoverse V2), Debian 12 images; 4-vCPU shared cloud VMs; an Apple M2 Max appears only in a separate four-machine run |
| **Compiler and flags** | rustc 1.85 (pinned in rust-toolchain.toml); Cargo release profile lto="fat", codegen-units=1, default opt-level 3; assembly kernels built through build.rs with the cc crate; Criterion 0.5 harness (benches/codec.rs); baseline liblz4 is the Debian 12 liblz4-dev apt package (scripts/bench-on-gce.sh), its version and build flags not stated in the log |
| **Adoption** | 0 stars |
| **Last commit** | 2026-10-02 |
| **Links** | [repository](https://github.com/macstab/lzvolt) · [benchmark](https://raw.githubusercontent.com/macstab/lzvolt/HEAD/docs/MEASUREMENTS.md) |

## Verdict

In the author's Criterion run (docs/MEASUREMENTS.md, 'The standardised run on ad7d338'), on 4-vCPU GCE VMs with Xeon 8481C, EPYC 9B14 and Neoverse V2, rustc 1.85 with fat LTO, lzvolt decoded its own format 14% to 83% faster than Debian 12's apt liblz4 (LZ4_decompress_safe) on all 18 cells of generated JSON-record data (512 B, 4 KiB, 64 KiB); medians of three. On the same LZ4 blocks it was ahead on 20 of 27 cells (worst noise_512, -15% on Xeon), and its packing was faster on 25 of 27 cells against LZ4_compress_default.

## Use it when

- Read-heavy caches or record stores that compress each value separately, roughly 512 B to 64 KiB, where decode latency per value matters more than ratio.
- JSON-like records with repeated keys: the measured shapes are synthetic JSON records, decoded at 7-13 GiB/s of output on Xeon 8481C, EPYC 9B14 and Neoverse V2.
- Stores that already hold raw LZ4 blocks and want a faster reader without rewriting data (ahead of liblz4 on 20 of 27 measured cells).
- Linux or macOS on x86-64 or aarch64, where the assembly decoders are used.
- Rust services (crate lzvolt 1.0.0) or C/C++ code willing to link a Rust staticlib/cdylib through include/lzvolt.h.

## Skip it when

- You need interoperability: the native format is readable only by lzvolt (a conforming LZ4 decoder rejects some streams), and there is no frame, checksum or streaming mode.
- Large files, archives or values over 2^29-1 bytes (536,870,911): the format caps value size and was tuned only on 512 B to 64 KiB values.
- Windows or other architectures: they get the portable Rust decoder, which is slower and was not benchmarked against liblz4.
- Incompressible small blocks in LZ4 format: noise_512 in LZ4 blocks loses 15% (Xeon) and 12% (EPYC) to liblz4, and the kernel is sensitive to buffer placement there.
- You need ratio comparisons against zstd, LZAV or other fast codecs on standard corpora: only liblz4 and lz4_flex were compared, on generated data.

## How it is fast

Byte-oriented LZ77 (64 KiB window, minimum match 4) with two token bit splits; a value may switch from one split to the other once, which the author measured at about 19% on shapes whose match lengths overflow the narrow field. Decoding uses separate hand-written GAS assembly bodies per CPU part line (Xeon, EPYC, SSSE3-only x86, generic AArch64, Neoverse V2), chosen once per process from CPUID or MIDR, with unchecked wide copies behind an up-front validation pass. The measurement log credits the big wins to removing work: memcpy for long literal runs (+34% on noise_64k), one wide token load replacing three dependent loads (+37%), and an output slack margin (lzvolt_decompress_bound) that lets the last copy run full width.

## Compared with alternatives

Pick lzvolt over LZ4 when you compress small values one at a time and control both the writer and the reader, or when you already store raw LZ4 blocks and want a faster decoder for them. ZXC, misa77 and LZAV publish larger decode margins over LZ4 on file-sized corpora; lzvolt is the one built and measured specifically for 512 B to 64 KiB values.

## Integration

| | |
|---|---|
| **Form** | crate (also staticlib and cdylib with a hand-written C header; prebuilt glibc, musl and macOS libraries with lzvolt.pc and a CMake package config on the v1.0.0 release) |
| **Dependencies** | none at run time; building needs a Rust toolchain and a C compiler/assembler (cc crate in build.rs); system liblz4 only for the comparison benchmarks and interop tests (feature liblz4) |
| **Minimum toolchain** | Rust 1.85 (rust-version and rust-toolchain.toml); C callers need C99 stdint.h |
| **Platforms** | x86-64 and aarch64 on Linux and macOS with assembly decoders; Windows and every other target build the portable Rust decoder |
| **Thread safety** | Header states every function is thread-safe with no shared state; the compressor uses a per-thread scratch buffer. |
| **Drop-in for the baseline** | partial — lzvolt_decompress_lz4 reads raw LZ4 blocks (like LZ4_decompress_safe, with the decoded size passed in), but compression writes a different, non-LZ4 format and the API differs |

## Gotchas

- Compression refuses (returns 0) any input it cannot shrink by at least an eighth; callers must store the raw bytes and track which values are packed. This refusal is also why the packing benchmark shows +820% to +859% over liblz4 on 64 KiB noise: lzvolt declines while liblz4 actually encodes.
- Size the output buffer with lzvolt_decompress_bound(declared), not the exact length, to get the measured speed; the exact length is safe but takes the slower trimmed final copy (34% on incompressible 4 KiB).
- Decoders do unchecked copies; safety rests on the validation pass, which the author fuzzes, runs under Miri and tests the assembly under AddressSanitizer. In the log, a 2026-09-20 x86 kernel port mis-decoded 9 of 5760 liblz4 blocks (caught by the refuse-and-fallback path), and an interop test sat red for a day because the routine check ran without --features liblz4.
- Throughput figures are counted against unpacked bytes, so a better ratio raises the reported GiB/s; lzvolt_backend() names the code path in use and should be logged next to any measurement.

## Known shortcomings

- Tier A (benches/codec.rs public, rustc 1.85 pinned, fat LTO, GCE c3/c3d/c4a CPUs named; liblz4 baseline from Debian 12 apt), but the measured revision ad7d338 is not in the public history (404) and bench-on-gce.sh still builds keva-core. Rust with a C API.
- The packing rows (+820% to +859% on noise_64k) are inflated because the encoder refuses input it cannot shrink by 1/8 while liblz4 actually encodes, so the 25/27 packing count is misleading; all bench data is synthetic JSON records from benches/codec.rs (no Silesia or other standard corpus). 11 crates.io downloads, 0 issues; the log notes the x86 kernel port mis-decoded 9 of 5760 liblz4 blocks on 2026-09-20 (caught by the fallback, fixed the same day).

## Caveats and trade-offs

Brand-new single-author project with 0 stars (263 commits, extracted from the author's KevaVolt project); latest commit 2026-10-02 corrected a misattributed capacity x throughput table in the README (the M2 column had been dropped and labels shifted), which does not affect the decode/pack tables quoted here. The standardised run was on revision ad7d338, which does not exist in this repo's history (commit page 404), and scripts/bench-on-gce.sh still builds the monorepo package keva-core and calls scripts/packer-report.sh, which this repo does not ship, so reproduction needs `make bench` / benches/codec.rs instead. Throughput is counted against unpacked bytes, so smaller output inflates the number. Packing is not ahead on varied_4k Neoverse V2 (-2%) or varied_64k EPYC (+0%). Reading raw LZ4 blocks loses on 7 of 27 cells, worst noise_512 on x86 (-15% Xeon, -12% EPYC); the author attributes this to buffer-placement sensitivity. Rust with hand-written assembly; usable from C++ only through its C ABI (include/lzvolt.h, staticlib/cdylib); assembly kernels only on Linux/macOS x86-64 and aarch64, portable Rust elsewhere. Compared only against liblz4 and lz4_flex, not zstd or other fast LZ codecs.

Own format is not LZ4-compatible (also reads LZ4 blocks). Encoder refuses data it cannot shrink by an eighth. Targets small values for caches and record stores, not large-file streaming. Per-CPU hand-written assembly; C API (include/lzvolt.h) is the only supported path from C++.

## Maintenance

Active single-author project, first released as 1.0.0 on 2026-09-27 (263 commits, 0 stars, 11 crates.io downloads, no issues filed); Apache-2.0 and copyable, but the measured revision ad7d338 is not in the public history and the GCE script references monorepo pieces this repo does not ship.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification A, tier now A.
- **Tier reason:** docs/MEASUREMENTS.md 'The standardised run on ad7d338' has every cell quoted (own-format decode 18/18 cells +14% to +83%, LZ4-block decode 20/27 ahead, packing 25/27 ahead) against liblz4 in the same Criterion process; bench code is public (benches/codec.rs, required-features liblz4), the compiler is pinned (rust-toolchain.toml channel 1.85), flags are in Cargo.toml (release lto="fat", codegen-units=1), and CPUs are named (Xeon 8481C / EPYC 9B14 / Neoverse V2 on GCE c3/c3d/c4a-standard-4, Debian 12 with apt liblz4-dev per scripts/bench-on-gce.sh).
- **Verifier notes:** All numbers in claimed_speedup match the README and the MEASUREMENTS.md standardised run exactly; the 20/27 and 25/27 counts check out against the per-cell tables. The measurement log is unusually candid (records refuted ideas and losing cells), but the measured revision is not in the public history, which is worth an enricher look.
- **Fields the verifier corrected:** `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/macstab/lzvolt/HEAD/docs/MEASUREMENTS.md>
  - <https://raw.githubusercontent.com/macstab/lzvolt/HEAD/README.md>
  - <https://raw.githubusercontent.com/macstab/lzvolt/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/macstab/lzvolt/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/macstab/lzvolt/HEAD/rust-toolchain.toml>
  - <https://raw.githubusercontent.com/macstab/lzvolt/HEAD/scripts/bench-on-gce.sh>
  - <https://github.com/macstab/lzvolt>
  - <https://github.com/macstab/lzvolt/commits>
  - <https://github.com/macstab/lzvolt/tree/main/scripts>
  - <https://github.com/macstab/lzvolt/tree/main/benches>
  - <https://github.com/macstab/lzvolt/commit/ad7d338>
  - <https://github.com/macstab/lzvolt/commit/7437bb1>
- **Sources the enricher read:**
  - <https://github.com/macstab/lzvolt>
  - <https://github.com/macstab/lzvolt/issues?q=is%3Aissue>
  - <https://github.com/macstab/lzvolt/pulls>
  - <https://github.com/macstab/lzvolt/releases>
  - <https://raw.githubusercontent.com/macstab/lzvolt/HEAD/README.md>
  - <https://raw.githubusercontent.com/macstab/lzvolt/HEAD/docs/MEASUREMENTS.md>
  - <https://raw.githubusercontent.com/macstab/lzvolt/HEAD/include/lzvolt.h>
  - <https://raw.githubusercontent.com/macstab/lzvolt/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/macstab/lzvolt/HEAD/rust-toolchain.toml>
  - <https://raw.githubusercontent.com/macstab/lzvolt/HEAD/build.rs>
  - <https://raw.githubusercontent.com/macstab/lzvolt/HEAD/Makefile>
  - <https://raw.githubusercontent.com/macstab/lzvolt/HEAD/benches/codec.rs>
  - <https://raw.githubusercontent.com/macstab/lzvolt/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/macstab/lzvolt/HEAD/src/ffi.rs>
  - <https://raw.githubusercontent.com/macstab/lzvolt/HEAD/docs/FORMAT.md>
  - <https://raw.githubusercontent.com/macstab/lzvolt/HEAD/SECURITY.md>
  - <https://raw.githubusercontent.com/macstab/lzvolt/HEAD/CHANGELOG.md>
  - <https://crates.io/api/v1/crates/lzvolt>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/macstab/lzvolt`) · [data/wave9/enrich/raw/github_com_macstab_lzvolt.json](../../../data/wave9/enrich/raw/github_com_macstab_lzvolt.json) (enrichment confidence 0.75)

</details>
