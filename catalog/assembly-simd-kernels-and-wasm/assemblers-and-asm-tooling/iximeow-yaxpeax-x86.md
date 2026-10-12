# yaxpeax-x86

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assemblers and assembly tooling](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `0BSD` · 🟢 active

> Rust x86/x86-64 instruction decoder and formatter; in current disas-bench runs it decodes 5-9x faster than XED and Zydis.

| | |
|---|---|
| **Beats** | Capstone, Zydis, Intel XED, bddisasm, diStorm (x86/x64 disassembler libraries); no GNU as, NASM or MASM comparison |
| **Claimed result** | icedland/disas-bench fork (June 2021, i5-6600K): decode only 182.08 MB/s vs Zydis 34.19, XED 55.39, bddisasm 35.48, diStorm 92.17 (about 5.3x Zydis, 3.3x XED, derived from page data); decode+format 40.05 MB/s vs Capstone 14.02, Zydis 22.24, XED 15.67, bddisasm 16.00 (about 2.9x Capstone, derived). Upstream athre0z/disas-bench October 2025 charts (submodule 681262f, after yaxpeax's formatting rework; values read from chart pixels): i9-13900K (GCC 14.2, run by athre0z) decode about 406 vs iced 390 and XED 73 MB/s, decode+format about 192 vs iced 165; Ryzen 9 9950X (GCC 13.3, run by the yaxpeax author) decode about 462 vs iced 363, decode+format about 198 vs iced 160, so yaxpeax-x86 is fastest in both modes on both machines. Repo README: 'roughly 250mb/s decode throughput and on some hardware is the fastest software x86 decoder available', 'an average of 58 cycles on a zen2 core'. |
| **Workload** | Decoding only, and decoding plus formatting, of the 77 MB .text section of Firefox 86.0.1's 64-bit xul.dll, throughput in MB/s (computed as bytes/1024/1024 per second). The README does not state the loop count: bench.py's built-in default is 20 passes over the 36.4 MiB section of the older 63 MB input/xul.dll checked into the repo, and with a custom file and no loop-count argument it scales the count to keep the same total bytes (about 9 passes over a 77 MB section, derived from bench.py). The Firefox 86 xul.dll itself is not in the repo. |
| **Metric** | throughput |
| **Hardware** | Intel Core i5-6600K, Kubuntu 21.04 (README); test file xul.dll from Firefox 86.0.1.7739, 77 MB code section |
| **Compiler and flags** | Kubuntu 21.04, gcc 10.3.0, Rust 1.52.1 (disas-bench README). make-all.sh builds the C libraries with gcc and LTO: Capstone and bddisasm as CMake Release builds with CFLAGS=-flto, XED via mfile.py --opt=3 --extra-flags=-flto, diStorm via its own make/linux Makefile (current version: -fPIC -O2 -std=c99) with -flto prepended, BeaEngine patched to -O3 -flto, udis86 without LTO (it got slower). The C bench drivers (bench/\*/Makefile) are built with -flto -O3; the Zydis driver is a CMake Release build with CFLAGS=-flto. The Rust drivers (bench/iced-x86/Cargo.toml, bench/yaxpeax/Cargo.toml) use a release profile with opt-level=3, lto=true, codegen-units=1 and no target-cpu setting. C libraries and yaxpeax-x86 are pinned git submodules (last updated March 2021); iced is pulled unpinned from its git master at build time. |
| **Adoption** | 162 stars |
| **Last commit** | 2026-08-08 |
| **Links** | [repository](https://github.com/iximeow/yaxpeax-x86) · [benchmark](https://github.com/icedland/disas-bench) |

## Verdict

The catalogued numbers come from icedland/disas-bench (June 2021, i5-6600K, rustc 1.52.1, gcc 10.3.0 LTO builds, one linear sweep per library over Firefox 86 xul.dll .text): yaxpeax decoded at 182.08 MB/s against Zydis 34.19 and XED 55.39, but its decode+format (40.05 MB/s) trailed iced and diStorm. The newer athre0z/disas-bench charts (October 2025, yaxpeax-x86 submodule 681262f, 2.0-era, after the formatting optimization; 20 passes over 0x2460400 bytes) reverse that. On athre0z's own i9-13900K run (GCC 14.2, rustc 1.90.0) yaxpeax decode is about 406 MB/s against iced 390, XED 73 and Zydis full 57, and decode+format about 192 against iced 165, diStorm 94 and Capstone 26. On iximeow's Ryzen 9 9950X run (GCC 13.3, rustc 1.88.0) decode is about 462 against iced 363 and XED 67, and decode+format about 198 against iced 160 and Capstone 28 (bar lengths measured in pixels against the axis ticks, derived from page data).

## Use it when

- Bulk linear-sweep disassembly of large x86-64 code sections (binary analysis, indexing, gadget search, coverage tooling) where decode throughput dominates.
- Rust projects, including no_std or embedded and kernel-adjacent code: the crate builds without std and has no allocation in the decode path.
- Decode plus Intel-syntax text output at volume: in the 2025 disas-bench runs its decode+format beat every other library measured, iced included.
- Tools that need 16-, 32- and 64-bit decoding behind one interface, or per-microarchitecture decoders (Zen 2 to Zen 5 presets since 2.1.0) that reject instructions a given CPU lacks.
- Mixed-architecture tools already using the yaxpeax-arch traits (yaxpeax-arm and the other yaxpeax decoders).

## Skip it when

- C or C++ codebases that want a supported native API. The ffi/ crates have no header files, need nightly cargo (-Z build-std) for the documented build, and the author called them 'kinda useless and awful' in open issue #33 (June 2024). Zydis, XED or bddisasm fit better there.
- Encoding or assembling instructions, or rich semantics such as CPU-flag effects and register read/write lists for every instruction: iced re-encodes and carries more semantic data. yaxpeax has had operand access and exception behavior only since 2.1.0 (May 2026).
- Non-x86 targets from one library: this crate is x86 only (other yaxpeax crates cover other ISAs separately, unlike Capstone).
- Decoders that must reject encodings exactly as hardware does on older crate versions: 2.1.0 to 2.2.0 (2026) fixed many over-permissive VEX/EVEX acceptances, swapped operands, wrong register extensions and wrong memory sizes, so pin 2.2.x or later.
- AT&T syntax output: the formats offered are Intel, pseudo-C and MASM-style.

## How it is fast

Decoding starts from a 256-entry OPCODES table whose records pack the opcode and a 16-bit operand-handling code (bit 15 means 'read ModR/M'). A dedicated hot path handles common unprefixed opcodes before the general prefix/0F/0F38/0F3A loop. The decoder writes into a caller-provided Instruction rather than building a new one, is generic over the reader and annotation sink (the no-op NullSink compiles the annotation code away), and uses inline(always) plus unreachable_unchecked to prune impossible match arms (the CHANGELOG measured about 5% loss without the latter). Formatting writes into a fixed 512-byte InstructionTextBuffer; the author's commit 681262f records display time falling from 91 ns to 47 ns per instruction against 15 ns per decode.

## Compared with alternatives

Pick yaxpeax-x86 over iced when you want the highest decode and decode+format throughput in Rust, a no_std build and small code size, and you need neither re-encoding nor iced's richer semantics. In the 2025 disas-bench charts it edges iced by about 1.04-1.27x on decode and 1.16-1.24x on decode+format. Pick Zydis, XED or bddisasm instead from C or C++, where yaxpeax's FFI is unfinished, and diStorm only for small pre-AVX2 C use.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | yaxpeax-arch 0.3.1, num-traits, cfg-if; serde, serde_derive and serde_json optional (the default features std, colors, use-serde, fmt and behavior pull in serde) |
| **Minimum toolchain** | not documented (Cargo.toml has no rust-version; edition 2018). The benchmark runs used rustc 1.52.1 (2021), 1.88.0 and 1.90.0 (2025). The ffi/ build instructions need nightly cargo -Z build-std. |
| **Platforms** | Any Rust target (no architecture-specific code per the ffi README); decodes x86-16, x86-32 and x86-64 code. The benchmarks ran on x86-64 hosts (i5-6600K, Ryzen 9 9950X, i9-13900K). |
| **Thread safety** | not documented; InstDecoder is plain data (two u64 flag words) used through &self, and each decode writes into a caller-owned Instruction, so one Instruction per thread suffices. |
| **Drop-in for the baseline** | no |

## Gotchas

- Release builds rely on unsafe unreachable_unchecked and get_unchecked on hot paths. Earlier releases had reachable panics and an unsoundness: 1.1.2 fixed a debug-build EVEX panic, 1.1.3 fixed out-of-range RegSpec helpers that could print arbitrary const data, and 1.1.4 fixed a reachable unreachable under DisplayStyle::C. The crate is fuzzed with mishegos and in-tree cargo fuzz targets.
- The README points to an 'examples directory for FFI usage' that does not exist (issue #33, open since February 2024). The FFI formatter neither returns a length nor guarantees NUL termination, per the author.
- Intel-style output prints relative branch targets as \$+0xNN unless you use the AbsoluteAddressFormatter or DisplayRules added in 2.2.0, so text output differs from Zydis or XED and diffing against them needs normalization.
- The default InstDecoder accepts every extension plus both Intel- and AMD-specific quirks of undefined encodings. Use InstDecoder::minimal() or a uarch preset to reject instructions a target CPU lacks. Cargo.toml at HEAD still says 2.2.0 while the CHANGELOG lists 2.2.1 changes (August 2026 commits), so crates.io's latest is 2.2.0.

## Known shortcomings

- disas-bench numbers match but decode+format is 40.05 MB/s, behind iced and diStorm; 'fastest' only on some hardware; off-spec baseline set (disassemblers); ships ffi/ for C/C++.
- The 2021 numbers are stale: upstream athre0z/disas-bench October 2025 charts (submodule 681262f, after the formatting rework) show yaxpeax-x86 fastest in both modes; the i9-13900K run by athre0z (independent) gives decode about 406 vs iced 390 and XED 73 MB/s, decode+format about 192 vs iced 165; the Ryzen 9 9950X run by iximeow (the author) gives decode about 462 vs 363 and decode+format 198 vs 160 (values read from chart pixels). No harness flaw in the drivers. The FFI has no headers, needs nightly, and the author calls it 'kinda useless and awful' (open issue #33); the 2026 releases 2.1-2.2 are not benchmarked.

## Caveats and trade-offs

The table comes from the iced author's disas-bench fork (June 2021, i5-6600K) with the yaxpeax-x86 submodule of March 2021; the yaxpeax author's own fork (linked from the README) is updated to a newer yaxpeax-x86 and shows only a bar chart (i7-12700K, GCC 11, rustc 1.67 nightly) with yaxpeax decode at roughly 351 MB/s, about level with iced (357), and decode+format around 72 MB/s, behind iced and diStorm (values read off the bars, approximate). The README's 'roughly 250mb/s' and 'on some hardware is the fastest software x86 decoder' claims give no hardware or date; the README calls the in-repo benchmark 'so unrealistic as to be unuseful' and defers to disas-bench. The benchmark loop count is not stated (see workload). Each driver runs once per configuration (no repetitions or variance); the C drivers time CPU time with clock(), the Rust drivers wall time with millisecond resolution. Formatters differ in output syntax between libraries; in decode+format yaxpeax (40.05 MB/s) trails iced and diStorm. A C/C++ interface exists in the repo's ffi/ directory (repackaging for non-Rust callers). Decode/disassembly throughput against other disassemblers, not assembly speed against GNU as, NASM or MASM (the category's spec baseline); objdump was not tested. [retier] The 2021 table comes from the iced author's disas-bench fork (i5-6600K, yaxpeax-x86 submodule of March 2021), one run per configuration with the C drivers timing CPU time via clock() and the Rust drivers wall time in milliseconds; the upstream athre0z/disas-bench October 2025 runs (newer yaxpeax with its formatting rework, no LTO) reverse the 2021 decode+format ordering and put yaxpeax ahead of iced and diStorm in both modes, with the Ryzen run contributed by the yaxpeax author (first-party) and the i9-13900K run by the Zydis co-author. The README's 'roughly 250mb/s' and 'fastest on some hardware' claims give no hardware or date, and the README calls the in-repo benchmark 'so unrealistic as to be unuseful'. Release builds rely on unsafe unreachable_unchecked and get_unchecked on hot paths (earlier releases had reachable panics fixed in 1.1.2-1.1.4; fuzzed with mishegos and cargo fuzz). The FFI has no headers, needs nightly and lacks the promised examples directory (issue #33 open since February 2024); the author calls it 'kinda useless and awful'. The 2026 releases 2.1-2.2 are not benchmarked; Cargo.toml at HEAD still says 2.2.0. Intel-style output prints relative branch targets as \$+0xNN unless AbsoluteAddressFormatter or DisplayRules (2.2.0) are used. Disassembly throughput, not assembly speed against GNU as, NASM or MASM.

Rust crate (part of the yaxpeax project), no C API, so C++ use needs FFI; about 143 kB of code and data for the decoder (249 kB with formatting). x86 only in this crate.

## Maintenance

Actively maintained (2.1.0 to 2.2.0 released May-July 2026, last commit 2026-08-08) and 0BSD-licensed, so it is copyable. No harness flaw was found in the drivers. However, the catalogued 2021 numbers are stale: they predate the formatting rework that now puts yaxpeax ahead of iced on decode+format. The Ryzen 9950X chart was produced by yaxpeax's own author (PR #16), so only the i9-13900K run is third-party. Neither run measured the 2026 releases, whose stricter VEX/EVEX rejection and new behavior data are unbenchmarked. The disas-bench drivers count instructions but never read the decoded fields, which is the same for every library.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** icedland/disas-bench README (results commit 689f3c8, 2021-06-11) lists yaxpeax at 182.08 MB/s decode and 40.05 MB/s decode+format against XED, Zydis, bddisasm, Capstone and others; harness code is public (bench.py, bench/yaxpeax/src/main.rs, Cargo.toml release profile with lto) with Rust 1.52.1 and an i5-6600K stated, run by a third party (the iced author).
- **Verifier notes:** Numbers match the disas-bench README rows exactly; tier A holds (public harness, compiler, Cargo/Makefile flags, CPU, third-party run). Corrected the workload's '20 loops' and filled in the inspected flags. Shortcomings: decode+format slower than iced and diStorm, fastest-decoder claim only on some hardware, one-shot timings, off-spec baseline.
- **Fields the verifier corrected:** `workload`, `compiler_and_flags`, `caveats`, `claimed_speedup`
- **Shortcomings recorded by:** verifier batch-01 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/icedland/disas-bench>
  - <https://github.com/icedland/disas-bench/commits/master>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/make-all.sh>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/bench.py>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/bench/yaxpeax/Makefile>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/bench/yaxpeax/Cargo.toml>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/bench/yaxpeax/src/main.rs>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/iximeow/disas-bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/iximeow/disas-bench/HEAD/bench-ath.png>
  - <https://github.com/iximeow/yaxpeax-x86>
  - <https://github.com/iximeow/yaxpeax-x86/commits/no-gods-no-/>
  - <https://raw.githubusercontent.com/iximeow/yaxpeax-x86/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/iximeow/yaxpeax-x86>
  - <https://github.com/iximeow/yaxpeax-x86/issues>
  - <https://github.com/iximeow/yaxpeax-x86/issues/33>
  - <https://github.com/iximeow/yaxpeax-x86/commits/no-gods-no-/>
  - <https://github.com/iximeow/yaxpeax-x86/commit/681262f>
  - <https://raw.githubusercontent.com/iximeow/yaxpeax-x86/HEAD/README.md>
  - <https://raw.githubusercontent.com/iximeow/yaxpeax-x86/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/iximeow/yaxpeax-x86/HEAD/CHANGELOG>
  - <https://raw.githubusercontent.com/iximeow/yaxpeax-x86/HEAD/build.rs>
  - <https://raw.githubusercontent.com/iximeow/yaxpeax-x86/HEAD/Makefile>
  - <https://raw.githubusercontent.com/iximeow/yaxpeax-x86/HEAD/ffi/README.md>
  - <https://raw.githubusercontent.com/iximeow/yaxpeax-x86/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/iximeow/yaxpeax-x86/HEAD/src/long_mode/mod.rs>
  - <https://crates.io/api/v1/crates/yaxpeax-x86>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/bench.py>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/bench/yaxpeax/src/main.rs>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/bench/yaxpeax/Cargo.toml>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/bench/iced-x86/src/main.rs>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/bench/zydis/main.c>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/bench-amd.png>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/bench-intel.png>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/bench.py>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/make-all.sh>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/bench/yaxpeax/src/main.rs>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/bench/yaxpeax/Cargo.toml>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/bench/yaxpeax/Makefile>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/bench/iced-x86/src/main.rs>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/bench/iced-x86/Cargo.toml>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/bench/zydis/main.c>
  - <https://github.com/athre0z/disas-bench/tree/master/libs>
  - <https://github.com/athre0z/disas-bench/commits/master>
  - <https://github.com/athre0z/disas-bench/pull/16>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/iximeow/yaxpeax-x86`) · [data/wave13/enrich/raw/github_com_iximeow_yaxpeax_x86.json](../../../data/wave13/enrich/raw/github_com_iximeow_yaxpeax_x86.json) (enrichment confidence 0.8)

</details>
