# Intel XED (x86 encoder decoder)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assemblers and assembly tooling](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `Apache-2.0` · 🟢 active

> Intel's own x86/x86-64 decoder and encoder in C; decodes faster than full-mode Zydis, roughly ties or trails Capstone once formatting is included.

| | |
|---|---|
| **Beats** | Capstone (decode+format); Zydis and bddisasm (decode only) |
| **Claimed result** | icedland/disas-bench (2021, i5-6600K, gcc 10.3.0, LTO builds): decode only XED 55.39 MB/s vs Zydis 34.19 and bddisasm 35.48 MB/s (about 1.62x and 1.56x, derived from page data); decode+format XED 15.67 vs Capstone 14.02 MB/s (about 1.12x, derived from page data). The upstream athre0z/disas-bench charts (October 2025, no LTO, newer library versions) reverse the Capstone result: decode+format XED about 21 MB/s vs Capstone about 28 MB/s on a Ryzen 9 9950X (GCC 13.3) and about 20 vs 26 MB/s on an i9-13900K (GCC 14.2), so XED runs at about 0.76-0.77x of Capstone; decode only XED about 67 and 73 MB/s vs Zydis (full) about 50 and 57 MB/s (about 1.3x) but behind bddisasm (about 106 and 103 MB/s) and Zydis (min) (about 90 and 104 MB/s) (2025 values derived from page data: bar lengths read from the pixels of bench-amd.png and bench-intel.png against their axis ticks). XED is slower than iced, yaxpeax and diStorm in every table of both runs. |
| **Workload** | Decode-only and decode+format throughput in MB/s over the 77 MB x86-64 code section of Firefox 86.0.1 xul.dll, one shootout of nine x86 disassembler libraries. |
| **Metric** | throughput |
| **Hardware** | Intel Core i5-6600K |
| **Compiler and flags** | Kubuntu 21.04, gcc 10.3.0, Rust 1.52.1; make-all.sh builds XED with mfile.py --no-encoder --opt=3 --extra-flags=-flto and Capstone as a Release build with -flto |
| **Adoption** | 1.6k stars |
| **Last commit** | 2026-08-24 |
| **Links** | [repository](https://github.com/intelxed/xed) · [benchmark](https://github.com/icedland/disas-bench) |

## Verdict

In icedland/disas-bench (2021, i5-6600K, gcc 10.3.0, LTO builds, Firefox 86 xul.dll code section) XED decoded 55.39 MB/s against Zydis 34.19 and bddisasm 35.48 MB/s and did decode+format at 15.67 MB/s against Capstone's 14.02 MB/s; the upstream athre0z/disas-bench charts of October 2025 (Ryzen 9 9950X with GCC 13.3, i9-13900K with GCC 14.2, XED v2025.06.08 without LTO) show XED at about 0.77x of Capstone in decode+format and behind bddisasm and Zydis (min) in decode only, ahead only of full-mode Zydis.

## Use it when

- You need the most complete and earliest coverage of new Intel ISA extensions: releases in 2025-2026 track APX, AVX10.2, AMX and ACE specification revisions and new chip configurations (Diamond Rapids, Nova Lake).
- You need detailed per-operand semantics (read/write actions, implicit and suppressed operands, flags, ISA set and CPUID-based chip checks) for binary analysis, instrumentation or emulation, not just a text disassembly.
- You need both a decoder and an encoder from one library, including the enc2 fast encoder for JIT-style code generation.
- You only need instruction lengths: the ILD API (examples/xed-dec-ild.c, ILD-only builds) skips full operand decoding.
- Your project is C or C++ and can accept Apache-2.0 and a static libxed.a.

## Skip it when

- Raw decode or disassembly throughput is the goal: iced decodes about 4.6x and diStorm about 1.7x faster in the 2021 run, and in the 2025 runs bddisasm and Zydis (min) also decode faster than XED.
- You want to replace Capstone for decode+format speed: the 2025 runs on Ryzen 9 9950X and i9-13900K put XED at about 0.77x of Capstone.
- You need non-x86 architectures (Capstone covers ARM, RISC-V and others).
- Your build cannot run Python: libxed is produced by the mbuild Python build system (python 3.9 or later per docsrc/xed-build.txt), not CMake or a plain Makefile.
- You need decoding that matches other disassemblers by default on recent XED: since v2025.03.02 LZCNT, TZCNT and PAUSE are off unless enabled, so F3 0F BD decodes as BSR.

## How it is fast

Decoder tables and enumerations are generated at build time by Python generators from text datafiles that describe an internal grammar of nonterminals, so decoding is a table-driven pipeline: an instruction length decode (ILD) pass, a static lookup of the xed_inst_t template, then generated nonterminal functions that capture operands. All decode state lives in the caller's xed_decoded_inst_t, with no allocation per instruction. Its strength is completeness and detail rather than raw speed; in both disas-bench runs the leaner decoders (iced, yaxpeax, diStorm) are several times faster.

## Compared with alternatives

Pick XED over iced, diStorm, yaxpeax-x86 or Zydis when Intel-authoritative ISA coverage, chip/ISA-set checks and an encoder matter more than speed; pick iced (Rust) or diStorm for the fastest decode, bddisasm or Zydis (min) for faster C decode with full operand info, and Zydis for faster decode+format with a permissive C API.

## Integration

| | |
|---|---|
| **Form** | static lib (shared with --shared; installable kit with headers via 'mfile.py install') |
| **Dependencies** | build: Python 3.9+ and the separate intelxed/mbuild repository; runtime: only a few libc functions (memcmp, memset, memcpy, strcmp, strncat, strlen, fprintf, abort) |
| **Minimum toolchain** | C compiler: GCC, Clang (Clang 17-20 named in 2025-2026 release notes) or MSVC; Python 3.9+ for the build |
| **Platforms** | Linux, Windows (with or without cygwin), FreeBSD per the docs; decodes IA-32 and Intel 64 code only; an open issue (#358) carries a macOS build fix |
| **Thread safety** | Reentrant after a single xed_tables_init() call made before threads start; all decode/encode state lives in caller-provided structures. |
| **Drop-in for the baseline** | no |

## Gotchas

- Call xed_tables_init() once before use, and re-initialise the decoded-instruction struct before every decode (xed_decoded_inst_zero_keep_mode() or xed_decoded_inst_zero_set_mode()); the benchmarks use xed_decoded_inst_zero plus set_mode each time.
- Since v2025.03.02, PAUSE, LZCNT and TZCNT are disabled by default unless enabled through the decoder mode/chip-feature APIs (xed_set_decoder_modes, xed_chip_features_t), and unsupported PREFETCH decodes as NOP; default output therefore differs from other disassemblers on modern binaries.
- No benchmark measures current XED: the 2021 icedland run used a decoder-only (--no-encoder) LTO build, the 2025 athre0z run used v2025.06.08 (submodule dc6bdbe) at --opt=3 without LTO, and v2026.02.17 later added systematic API input validation (disable with --no-api-check) whose cost is unmeasured.
- Harness detail: the 2021 icedland bench/xed/main.c ignores xed_decode's error return and still calls xed_format_context and advances by the reported length on invalid bytes; the 2025 upstream version skips one byte per bad instruction and counts them. Each library is timed with clock() in one subprocess run, MB/s computed as MiB, so small gaps (XED 15.67 vs Capstone 14.02 MB/s) are within run-to-run noise.

## Known shortcomings

- Claim against the Capstone incumbent is overstated: the 2021 icedland disas-bench run has XED 1.12x Capstone in decode+format, but the upstream athre0z/disas-bench October 2025 charts (Ryzen 9 9950X, i9-13900K) put XED at about 0.77x Capstone, behind bddisasm and Zydis (min) too; only the decode-only lead over Zydis (full), about 1.3x, still holds.
- No run measures current XED: the 2021 icedland run used a decoder-only LTO build; the 2025 athre0z run used v2025.06.08 (submodule dc6bdbe) at --opt=3 without LTO, which put XED at about 0.77x of Capstone in decode+format; v2026.02.17 later added API input checks (--no-api-check) that no run has measured. Since v2025.03.02 LZCNT, TZCNT and PAUSE are off by default, so F3 0F BD decodes as BSR. The 2021 harness ignores xed_decode errors and times one clock() run per library.

## Caveats and trade-offs

Weak and unstable win: the 2021 icedland run puts XED 1.12x ahead of Capstone in decode+format (derived), but the 2025 upstream athre0z/disas-bench runs on two newer CPUs put it about 0.77x of Capstone (slower), and bddisasm and Zydis (min) now decode faster than XED; only the decode-only lead over Zydis (full) holds in both runs (about 1.3-1.6x). XED sits mid-table or lower and is beaten by iced, yaxpeax and diStorm throughout. The 2021 shootout is run by the iced maintainers (a competitor) in a fork of athre0z/disas-bench; the 2025 runs are in the suite of a Zydis co-author; XED's own README makes no speed claim. The 2021 fork's bench/xed/main.c ignores xed_decode's error return (it formats and advances by the reported length even on invalid bytes); upstream later skips one byte per bad instruction and counts them. One timed run per library (one subprocess, clock() around the loop). Capstone cannot run decode-only, so no decode-only ratio against it. The 2021 build is decoder-only (mfile.py --no-encoder) with -flto; the 2025 build uses neither.

Intel's own IA32/Intel64 encoder and decoder library; built with a Python-based build system (mfile.py/mbuild); the benchmark builds it decoder-only. Other libraries in the same table are several times faster.

## Maintenance

Actively maintained by Intel (v2026.08.23, frequent ISA-alignment releases, 1.6k stars, 41 open issues including a few long-open decoder bugs such as #233 and #275); Apache-2.0 and copyable, but it is a mid-pack performer whose catalogue case rests on coverage rather than speed.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification A, tier now A.
- **Tier reason:** icedland/disas-bench README lists XED at 55.39 MB/s decode and 15.67 MB/s decode+format next to Capstone 14.02, Zydis and bddisasm; the harness is public (bench.py, make-all.sh, bench/xed/main.c and Makefile with -flto -O3, bench/cs) with gcc 10.3.0 and an i5-6600K stated, so the evidence itself is A. Verdict is downgrade because the headline win over Capstone does not hold in the upstream suite's newer runs.
- **Verifier notes:** 2021 numbers match the icedland/disas-bench README rows exactly and the harness is A-grade, but the upstream athre0z/disas-bench October 2025 charts (Ryzen 9 9950X and i9-13900K) show XED slower than Capstone in decode+format (about 0.77x), so the claim against the incumbent is overstated; claimed_speedup and caveats rewritten. Metadata confirmed on github.com: Apache-2.0, 1.6k stars, not a fork or archived, last commit 2026-08-24 (External Release v2026.08.23), active. Shortcomings: win over Capstone does not reproduce on newer runs, mid-table speed, competitor-run suites, single-run timings.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-42 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/icedland/disas-bench>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/make-all.sh>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/bench.py>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/bench/xed/main.c>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/bench/xed/Makefile>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/bench/cs/main.c>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/bench/cs/Makefile>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/bench-amd.png>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/bench-intel.png>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/make-all.sh>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/bench/xed/main.c>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/bench/xed/Makefile>
  - <https://github.com/athre0z/disas-bench/commits>
  - <https://github.com/intelxed/xed>
  - <https://github.com/intelxed/xed/commits>
- **Sources the enricher read:**
  - <https://github.com/intelxed/xed>
  - <https://raw.githubusercontent.com/intelxed/xed/HEAD/README.md>
  - <https://raw.githubusercontent.com/intelxed/xed/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/intelxed/xed/HEAD/mfile.py>
  - <https://raw.githubusercontent.com/intelxed/xed/HEAD/VERSION>
  - <https://raw.githubusercontent.com/intelxed/xed/HEAD/Security.md>
  - <https://raw.githubusercontent.com/intelxed/xed/HEAD/src/dec/xed-decode.c>
  - <https://raw.githubusercontent.com/intelxed/xed/HEAD/include/public/xed/xed-decoded-inst-api.h>
  - <https://raw.githubusercontent.com/intelxed/xed/HEAD/docsrc/xed-doc-top.txt>
  - <https://raw.githubusercontent.com/intelxed/xed/HEAD/docsrc/xed-build.txt>
  - <https://raw.githubusercontent.com/intelxed/xed/HEAD/docsrc/external-requirements.txt>
  - <https://github.com/intelxed/xed/tree/main>
  - <https://github.com/intelxed/xed/tree/main/docsrc>
  - <https://github.com/intelxed/xed/issues>
  - <https://github.com/intelxed/xed/issues?q=is%3Aissue+performance+OR+slow+OR+speed>
  - <https://github.com/intelxed/xed/releases>
  - <https://github.com/intelxed/xed/releases/tag/v2025.03.02>
  - <https://github.com/intelxed/xed/releases/tag/v2026.02.17>
  - <https://github.com/intelxed/xed/commit/dc6bdbe>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/bench/xed/main.c>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/bench/cs/main.c>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/make-all.sh>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/bench.py>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/bench/xed/main.c>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/bench/xed/Makefile>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/make-all.sh>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/bench.py>
  - <https://github.com/athre0z/disas-bench/tree/master/libs>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/intelxed/xed`) · [data/wave13/enrich/raw/github_com_intelxed_xed.json](../../../data/wave13/enrich/raw/github_com_intelxed_xed.json) (enrichment confidence 0.8)

</details>
