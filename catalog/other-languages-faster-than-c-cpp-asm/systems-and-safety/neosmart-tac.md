# tac (neosmart, SIMD-accelerated Rust rewrite of GNU tac)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟡 stale

> Rust tac that reverses a file's lines using mmap and an AVX2 newline scan; claims 2.55x over GNU tac.

| | |
|---|---|
| **Beats** | GNU Coreutils tac (C) |
| **Claimed result** | README: 'significantly (2.55x if mitigations disabled, more otherwise) faster than the version of tac that ships with GNU Coreutils'. The author's blog announces the 2.0 release as up to three times faster than GNU tac (WebSearch snippet only; neosmart.net did not resolve here). |
| **Workload** | Reversing the lines of a file (tac FILE); README gives no input size or command. |
| **Metric** | throughput |
| **Kind** | library or program |
| **Same algorithm as the baseline** | not stated |
| **Same optimization level** | not stated |
| **Why it wins** | README: AVX2/NEON SIMD newline detection plus memory-mapped input, which avoids read-syscall cost when speculative-execution mitigations are enabled. |
| **Adoption** | 113 stars, 6 forks; crates.io 13,404 downloads |
| **Last commit** | 2024-01-22 |
| **Links** | [repository](https://github.com/neosmart/tac) · [benchmark](https://raw.githubusercontent.com/neosmart/tac/HEAD/README.md) |

## Verdict

One first-party ratio: about 2.55x faster than GNU Coreutils tac with mitigations disabled and 'more otherwise', with no CPU, input file, GNU version or command, and no benchmark code in the repo. The author's blog (unreachable here; search snippet only) says up to 3x. The ratio was written for the July 2021 32-bit-mask loop, not the 64-bit loop that ships in 2.0.0 and 2.1.0.

## Use it when

- Only after the AVX2 mask bug below is fixed or ruled out on your build. Then: reversing large, seekable log files on local disk (tac access.log | grep ...) where scan throughput matters
- Workloads that pass FILE arguments (or redirect a file into stdin on Unix), so the mmap path runs
- Systems where speculative-execution mitigations make read() syscalls expensive; the README says the gap over GNU tac widens there
- When you need an MIT-licensed tac or one that runs natively on Windows

## Skip it when

- On x86-64 with AVX2 (the default path) until the movemask sign-extension bug is fixed: per code reading and an emulation of the loop, output gets scrambled whenever a newline is the last byte of the lower 32-byte half of a 64-byte block
- Piped input over 4 MiB: after the spill to the temp file, the loop reads into buf[total_read..], an empty slice, so read returns 0 and everything past the first 4 MiB is dropped without an error
- When you rely on GNU tac options (-s custom separators, -r regex separators, -b) or on GNU behaviour for empty files: tac on a 0-byte file fails with memmap's 'memory map must have a non-zero length' and exits non-zero
- Files that may be truncated while being read (copytruncate log rotation): a shrinking mapped file can raise SIGBUS; GNU's read-based approach does not have this hazard
- aarch64 on stable Rust (scalar fallback only) and 32-bit x86: the x86 cfg imports core::arch::x86_64 and calls _bzhi_u64, which exist only on x86_64, so an i686 build likely fails to compile (not tested)

## How it is fast

The whole input is memory-mapped, so there are no read() syscalls; the README credits this for the larger gain when speculative-execution mitigations make syscalls expensive. On x86 with AVX2 (runtime-detected), the file is scanned backwards from a 32-byte-aligned point, two 32-byte vectors at a time: _mm256_cmpeq_epi8 + _mm256_movemask_epi8 build a 64-bit newline mask, then lzcnt picks the last newline and BZHI clears it. Each line goes out as one write_all of a slice of the mapping into a BufWriter. aarch64 has a NEON version of the same loop, but only with the nightly feature; every other target uses a byte-at-a-time loop.

## Compared with alternatives

No catalogued sibling reverses lines. The closest are the other coreutils rewrites (fd and minifind for find, FUC cpz/rmz for cp/rm, dumac for du), and unlike those tac currently has an unresolved output-correctness problem. Prefer GNU tac until the mask cast is fixed.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | atty 0.2 and memmap 0.7 (both flagged by RustSec: memmap unmaintained RUSTSEC-2020-0077; atty unsound on Windows RUSTSEC-2021-0145 and unmaintained RUSTSEC-2024-0375) |
| **Minimum toolchain** | Rust 2018 edition on stable for x86 AVX2 (no rust-version declared); NEON needs nightly with --features nightly, which enables the old #![feature(stdsimd)] gate |
| **Platforms** | x86-64 with AVX2 runtime-detected (BMI2 and LZCNT are also enabled but not checked); aarch64 NEON on nightly only; scalar fallback elsewhere; Linux, macOS and Windows (stdin mmap is Unix-only) |
| **Thread safety** | not applicable (single-threaded command-line tool) |
| **Drop-in for the baseline** | partial — same default output for newline-separated files, but no -b/-r/-s, errors on empty files, truncates piped input over 4 MiB, and (per code reading) the AVX2 path can scramble output |

## Gotchas

- Correctness bug in the AVX2 hot path (code reading plus an emulation of the loop; not run on the real binary): `matches = (matches << 32) | _mm256_movemask_epi8(..) as u64`. Rust's movemask returns i32, and casting i32 to u64 sign-extends. When bit 31 of the lower 32-byte window is set, the upper 32 mask bits all become 1, and the upper window's 32 bytes come out one byte at a time in reverse order. A Python emulation of search256 differed from GNU tac's output on 162 of 300 random inputs (0 of 300 with zero extension), and on about 1.6% of the bytes of a synthetic 200 KB log. The bug came in with commit ec5f71a (2021-08-31, the 64-byte unroll that changed `as u32` to `as u64`) and ships in crates.io 2.0.0 and 2.1.0. The repo has no tests; CI only runs cargo build and cargo test.
- Stdin spill bug: once buffered stdin reaches 4 MiB, the data is written to std::env::temp_dir()/.tac-&lt;pid&gt;, but later reads target buf[4 MiB..], an empty slice. The loop ends there, so only the first 4 MiB is reversed. The temp-file name is predictable, File::create follows symlinks, and the file is not deleted when output fails, because the `?` on a broken pipe returns before the cleanup.
- The speed numbers predate the current code: the README's 2.55x (no hardware, input or GNU version) was added 2021-07-12 for the 32-bit-mask loop. The later +14% (hyperfine, WSL1, AMD 1950X, 200x concatenated /usr/share/dict/words, commit ec5f71a message) was timed on the unrolled loop that carries the mask bug, and its output was apparently never checked.
- search256 is gated only on is_x86_feature_detected!("avx2") but also enables lzcnt and bmi2 (BZHI); a CPU or emulator that exposes AVX2 without BMI2 would fault with an illegal instruction.

## Known shortcomings

- One ratio (2.55x vs GNU tac) with no bench code, hardware or input; the blog's 'up to 3x' seen in a search snippet only; last commit 2024-01-22.
- Correctness bug in the AVX2 hot path (code reading plus Python emulation, not run on the real binary): _mm256_movemask_epi8(..) as u64 sign-extends the i32, so a newline at bit 31 of the lower window sets all upper mask bits and scrambles 32 bytes; emulation gives 162 of 300 random inputs differing from GNU tac (0 of 300 with zero extension). The bug dates from commit ec5f71a (2021-08-31) and ships in crates 2.0.0 and 2.1.0; the README 2.55x predates it (2021-07-12) but the later +14% was timed on the buggy loop. Piped stdin over 4 MiB is silently truncated (after the spill, reads go into the empty slice buf[total_read..]); the temp file leaks on a broken pipe; an empty file errors; no -s, -r or -b; the repo has no tests.

## Caveats and trade-offs

One number with no hardware, GNU tac version, input size or command; no benchmark code anywhere in the repo (top level holds only src, .cargo, Makefile; the Makefile bench target runs cargo bench but no benches exist). The blog post (neosmart.net) does not resolve from this environment; its 'up to 3x' wording is from a search snippet only. The win comes from SIMD newline search and mmap input rather than the language; piping input through stdin forces full buffering (disk spill above 4 MiB) and loses the mmap advantage. NEON path needs the nightly feature. No GitHub releases; crates.io 2.1.0 published 2024-01-22, last commit the same day. [retier] AVX2 hot-path bug (code reading plus Python emulation): _mm256_movemask_epi8(..) as u64 sign-extends the i32, so a newline at bit 31 of the lower window sets all upper mask bits and scrambles 32 bytes (162 of 300 random inputs differ from GNU tac in emulation); introduced in ec5f71a (2021-08-31), shipped in crates 2.0.0 and 2.1.0; the README 2.55x predates it but the later +14% was timed on the buggy loop. Piped stdin over 4 MiB is silently truncated; the temp file leaks on a broken pipe; an empty file errors; no -s, -r or -b; no tests.

Fast path needs a seekable file; stdin is buffered in memory up to 4 MiB then spilled to disk, so piped input loses the advantage. NEON needs the nightly compiler.

## Maintenance

Stale: last commit and crates.io 2.1.0 on 2024-01-22, two GitHub issues ever, no tests. It is MIT-licensed and one \~380-line source file, so the fixes are small (cast through u32 before widening; read into buf[..] after spilling; handle empty files), but the released crate should not be trusted for correct output on AVX2 machines or piped input over 4 MiB until then.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** README gives one first-party ratio (2.55x with mitigations disabled, 'more otherwise') against GNU Coreutils tac with no hardware, input, command, GNU version or benchmark code; the repo has no benches (Makefile bench target only runs cargo bench), so C as a number without methodology.
- **Verifier notes:** README sentence matches the record exactly; the 'more otherwise' means a larger speedup with speculative-execution mitigations on (mmap avoids read syscalls). Metadata checked: MIT, 113 stars, not a fork or archived, last commit 2024-01-22 (stale). Shortcomings: single unmethodical first-party ratio, no bench code, blog unreachable.
- **Fields the verifier corrected:** `claimed_speedup`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-109 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/neosmart/tac/HEAD/README.md>
  - <https://github.com/neosmart/tac>
  - <https://github.com/neosmart/tac/commits/master>
  - <https://raw.githubusercontent.com/neosmart/tac/HEAD/Makefile>
  - <https://raw.githubusercontent.com/neosmart/tac/HEAD/Cargo.toml>
  - <https://crates.io/api/v1/crates/tac>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/neosmart/tac/HEAD/README.md>
  - <https://raw.githubusercontent.com/neosmart/tac/HEAD/src/tac.rs>
  - <https://raw.githubusercontent.com/neosmart/tac/HEAD/src/main.rs>
  - <https://raw.githubusercontent.com/neosmart/tac/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/neosmart/tac/HEAD/Cargo.lock>
  - <https://raw.githubusercontent.com/neosmart/tac/HEAD/Makefile>
  - <https://raw.githubusercontent.com/neosmart/tac/HEAD/.cargo/config>
  - <https://raw.githubusercontent.com/neosmart/tac/HEAD/.github/workflows/rust.yml>
  - <https://github.com/neosmart/tac>
  - <https://github.com/neosmart/tac/issues?q=is%3Aissue>
  - <https://github.com/neosmart/tac/commits/master>
  - <https://github.com/neosmart/tac/commit/ec5f71a>
  - <https://github.com/neosmart/tac/commit/1c5e429>
  - <https://github.com/neosmart/tac/commit/2db64e3>
  - <https://github.com/neosmart/tac/tree/master/.github/workflows>
  - <https://crates.io/api/v1/crates/tac>
  - <https://crates.io/api/v1/crates/tac/2.1.0/download>
  - <https://crates.io/api/v1/crates/memmap/0.7.0/download>
  - <https://raw.githubusercontent.com/rust-lang/reference/master/src/expressions/operator-expr.md>
  - <https://raw.githubusercontent.com/rust-lang/stdarch/master/crates/core_arch/src/x86/avx2.rs>
  - <https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/memmap/RUSTSEC-2020-0077.md>
  - <https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/atty/RUSTSEC-2021-0145.md>
  - <https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/atty/RUSTSEC-2024-0375.md>
  - WebSearch: neosmart "world's fastest tac" SIMD rust benchmark hyperfine GNU coreutils (snippets of https://neosmart.net/blog/using-simd-acceleration-in-rust-to-create-the-worlds-fastest-tac/)
  - https://neosmart.net/blog/wp-json/wp/v2/posts/4801 (did not resolve)
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/neosmart/tac`) · [data/wave14/enrich/raw/github_com_neosmart_tac.json](../../../data/wave14/enrich/raw/github_com_neosmart_tac.json) (enrichment confidence 0.75)

</details>
