# fasthex

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Encoding (base64, hex, CRC)](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0` · 🟢 active

> Rust CLI hex dumper that uses multiple threads, SIMD and mmap to dump large files far faster than xxd, hexyl and hexdump.

| | |
|---|---|
| **Beats** | xxd |
| **Claimed result** | 0.78s vs xxd 43.62s (55.5x slower), hexyl --color=never 53.14s (67.6x slower), hexyl 104.93s (133.5x slower), hexdump 116.03s (147.5x slower) on a 1.5 GiB file; \~1 minute vs hexyl's \~1h30m on a 69 GiB file |
| **Workload** | Hex-dumping large files (1.5 GiB and 69 GiB) to /dev/null, wall-clock time measured with hyperfine (3 warmup runs) |
| **Metric** | throughput |
| **Hardware** | Intel i5-7700T, 16GB DDR4 RAM, Samsung 990 Pro NVMe SSD |
| **Adoption** | 13 stars; crates.io crate fasthex has 451 downloads (latest 0.3.28); README also lists AUR packages fasthex / fasthex-bin |
| **Last commit** | 2026-09-18 |
| **Links** | [repository](https://github.com/CallMeAlphabet/fasthex) · [benchmark](https://github.com/CallMeAlphabet/fasthex#benchmarks) |

## Verdict

These are the author's own hyperfine wall-clock numbers, from the README table last changed 2026-06-12. Dumping a 1.5 GiB file to /dev/null took 0.78 s for fasthex against 43.62 s for xxd, 53.14 s for hexyl --color=never and 116.03 s for hexdump. That is about 1.9 GiB/s input for fasthex vs about 35 MiB/s for xxd (derived). A 69 GiB file took \~1 min vs \~1 h 30 m for hexyl. The rig is an Intel T-series desktop: the gist says 'i5-7700T', which is not a real SKU, and earlier README revisions say i5-7500T. It had 16 GB RAM and a 990 Pro NVMe, and ran with no Rust version, build flags, tool versions or benchmark script published. After the 3 warmups the 1.5 GiB file most likely sits in page cache, so the result compares parallel SIMD formatting against single-threaded formatters, not I/O.

## Use it when

- Dumping very large files (hundreds of MiB to tens of GiB) on a multi-core x86-64 Linux box, where xxd (\~35 MiB/s in the README run) takes minutes
- Producing canonical hex+ASCII dumps into a file or pipe for grep/diff, where the vmsplice/splice path and parallel formatting both apply
- Quick -p plain-hex or -i C-array generation from big binaries when xxd is the bottleneck
- Interactive `fasthex file | less` on huge files, where it keeps up with paging far better than single-threaded dumpers

## Skip it when

- Scripts that parse xxd's exact output: the default layout is hexdump -C style, not xxd's `7f45 4c46` 2-byte grouping, and -p writes the whole file as one unbroken hex line (xxd -p wraps at 60 hex chars), so it is not byte-compatible.
- Input from stdin or several files concatenated: that goes through the single-threaded streaming path (4 MiB buffers, no rayon), so most of the headline speedup does not apply
- Small files or `-w` squeeze / `-m` max-lines runs: squeeze and max-lines force a serial path, and on small inputs thread and mmap setup costs are all overhead
- When correctness matters more than speed: the \~4,650-line main.rs has no unit tests (only a CI smoke check of -p against od on 4 KiB of random data), about 100 `unsafe` uses, and SECURITY.md itself lists 'SIMD paths producing different results than the scalar fallback' as a risk
- Non-Linux or non-x86 hosts: the zero-copy output, MADV_HUGEPAGE and the hand-written intrinsics are Linux- or x86-64-only. aarch64 and macOS builds exist but get the portable or scalar kernels and plain writes. Windows is not in the release matrix.

## How it is fast

When given a single mmap-able file, it maps the file and has rayon format output chunks in parallel (about 16 MiB of output per chunk in the current code). A separate writer thread drains finished buffers while the next chunk is formatted, using a 6-buffer pool. Hot rows are formatted with hand-written x86-64 intrinsics: AVX-512BW, then AVX2 at 32 bytes (2 rows) per call, then SSSE3/SSE4.1 at 16 bytes. Kernels are chosen at runtime with is_x86_feature_detected, and a std::simd nibble-LUT kernel is used on nightly builds. On Linux it also calls madvise(MADV_SEQUENTIAL/WILLNEED/HUGEPAGE) and writes through a private pipe with vmsplice+splice when stdout is a regular file or FIFO.

## Compared with alternatives

The hex siblings (const-hex, zbjornson fast-hex, eddieantonio's hx NEON kernel) are in-process encode/decode libraries that produce bare hex strings. Pick fasthex when you want a ready-made xxd/hexdump-style CLI dump of big files with offsets and an ASCII panel. Pick const-hex or fast-hex when you need hex encoding inside your own Rust or C++ code.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | memmap2 0.9, rayon 1.12, libc 0.2, clihelp 0.1 (binary crate; install via `cargo install fasthex`, AUR fasthex / fasthex-bin, Nix flake, or GitHub release binaries) |
| **Minimum toolchain** | Rust edition 2024 (so 1.85+). crates.io releases are built and smoke-tested on stable; rust-toolchain.toml pins nightly, which enables the std::simd portable_simd kernel detected by build.rs. |
| **Platforms** | Release binaries for x86_64/aarch64 Linux (gnu and musl) and x86_64/aarch64 macOS. SIMD kernels need x86-64 (SSSE3/SSE4.1 minimum, AVX2/AVX-512BW used if present); vmsplice/splice and MADV_HUGEPAGE are Linux-only. Windows is not documented. |
| **Thread safety** | Not applicable (CLI process). Internally it uses rayon's global pool for formatting plus one writer thread; there is no documented flag to set the thread count. |
| **Drop-in for the baseline** | partial — it replaces xxd/hexdump for viewing and has xxd-like -p/-i/-r flags, but the default output format differs from xxd, and flag semantics are its own |

## Gotchas

- The README says the zero-copy path works 'regardless of what stdout is (/dev/null, ...)', but the code only enables vmsplice/splice when stdout is a regular file or FIFO. /dev/null is a character device, so the benchmark runs used plain write(), which is already almost free on /dev/null.
- The input is mmap'd with memmap2 (`unsafe Mmap::map`). Truncating or rewriting the file while it is being dumped can SIGBUS the process or give inconsistent output.
- The octal and minimal fast paths only engage while displayed offsets stay at or below 0xFFFFFFFF, so dumps of files over 4 GiB in those modes fall back to slower kernels. Older versions, including the one that ran the 69 GiB benchmark, wrapped offsets past 4 GiB.
- Default colouring is `auto`: on a TTY it emits ANSI colours and takes the slower coloured path. Use --color=never for apples-to-apples timing. The FASTHEX_DEFAULT_OPTS environment variable is silently prepended to argv.

## Known shortcomings

- A hex-dump CLI (Rust), not a library. The &gt;50x win combines rayon multithreading and AVX2 against single-threaded xxd; stdin and multi-file input take the single-threaded path. The benchmark predates the current code: the stated 'i5-7700T' is a typo for the i5-7500T in the older README, and the 69 GiB run used u32 offsets that wrap (wrong output). vmsplice is used only for regular-file/FIFO stdout, so writes to /dev/null are plain write() calls. No unit tests, \~100 unsafe blocks; versions 0.3.23-0.3.27 yanked; default output is not xxd's layout.

## Caveats and trade-offs

The recorded benchmark_url (a gist) holds only the testing conditions: hardware, iommu settings and 'Hyperfine with 3 warmup runs'. The timing tables are in the README. No benchmark script is published, and no Rust version, build flags or xxd/hexyl/hexdump versions are given. Hardware is stated as 'Intel i5-7700T', which is not a real Intel SKU (i5-7600T and i7-7700T exist), so the CPU model is doubtful. The gains over 50x are not a like-for-like encoder comparison. fasthex formats in parallel with rayon over 64 MiB mmap chunks, uses AVX2/SSE4.1 SIMD, and writes zero-copy through vmsplice/splice, which makes output to /dev/null nearly free. xxd, hexyl and hexdump are single-threaded formatters. The tier is capped at C under the &gt;50x unstated-flags rule.

Relies on Linux-specific I/O tricks (mmap, vmsplice/splice, MADV_SEQUENTIAL) plus rayon parallelism and AVX2/SSE4.1/SSSE3 SIMD formatting; falls back to write_all when splice is unavailable (e.g. a tty); portability to macOS/Windows for the zero-copy path is unclear

## Maintenance

Actively developed by a single author: first commit 2026-04, last commit 2026-09-18, crates.io 0.3.28 with 451 downloads and 13 stars. Several releases were yanked (0.3.23–0.3.27) after stable-build breakage, and the benchmarks predate much of the current code. It is Apache-2.0 and easy to install from crates.io or AUR, but it is young and has little test coverage.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** These are the project's own numbers from the README Benchmarks tables (fasthex 0.78s vs xxd 43.62s, hexyl and hexdump). The gist gives only the hardware, OS settings and 'Hyperfine, 3 warmup runs'. There is no published benchmark script, and no Rust version, build flags or tool versions. With flags unstated and gains over 50x, the tier is capped at C.
- **Verifier notes:** The README numbers match claimed_speedup exactly, including the 69 GiB result (fasthex \~1m vs hexyl \~1h 30m). benchmark_url now points to the README Benchmarks section because the gist has no numbers. Metadata checked via gh: Apache-2.0, 13 stars, last commit 2026-09-18, not a fork, not archived.
- **Fields the verifier corrected:** `benchmark_url`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/CallMeAlphabet/fasthex>
  - <https://github.com/CallMeAlphabet/fasthex/blob/main/README.md>
  - <https://gist.github.com/CallMeAlphabet/4b7022c4b1a8849e6943526de6a23582>
  - <https://crates.io/api/v1/crates/fasthex>
- **Sources the enricher read:**
  - <https://github.com/CallMeAlphabet/fasthex>
  - <https://github.com/CallMeAlphabet/fasthex/blob/main/README.md>
  - <https://github.com/CallMeAlphabet/fasthex/blob/main/Cargo.toml>
  - <https://github.com/CallMeAlphabet/fasthex/blob/main/build.rs>
  - <https://github.com/CallMeAlphabet/fasthex/blob/main/rust-toolchain.toml>
  - <https://github.com/CallMeAlphabet/fasthex/blob/main/src/main.rs>
  - <https://github.com/CallMeAlphabet/fasthex/blob/main/.github/workflows/release.yml>
  - <https://github.com/CallMeAlphabet/fasthex/blob/main/.github/workflows/publish.yml>
  - <https://github.com/CallMeAlphabet/fasthex/blob/main/.github/SECURITY.md>
  - <https://github.com/CallMeAlphabet/fasthex/commits/main>
  - <https://github.com/CallMeAlphabet/fasthex/commits/main/README.md>
  - <https://github.com/CallMeAlphabet/fasthex/commit/4910fae>
  - <https://github.com/CallMeAlphabet/fasthex/commit/1d5c0a1>
  - <https://raw.githubusercontent.com/CallMeAlphabet/fasthex/35e9e8a/README.md>
  - <https://raw.githubusercontent.com/CallMeAlphabet/fasthex/0f39dce/README.md>
  - <https://github.com/CallMeAlphabet/fasthex/issues>
  - <https://gist.github.com/CallMeAlphabet/4b7022c4b1a8849e6943526de6a23582>
  - <https://crates.io/api/v1/crates/fasthex>
  - <https://hn.algolia.com/api/v1/search?query=fasthex&tags=story>
  - <https://aur.archlinux.org/rpc/v5/info?arg[]=fasthex&arg[]=fasthex-bin>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/callmealphabet/fasthex`) · [data/wave7/enrich/raw/github_com_callmealphabet_fasthex.json](../../../data/wave7/enrich/raw/github_com_callmealphabet_fasthex.json) (enrichment confidence 0.6)

</details>
