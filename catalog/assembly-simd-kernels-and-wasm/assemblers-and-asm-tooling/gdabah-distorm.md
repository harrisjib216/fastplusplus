# diStorm3

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assemblers and assembly tooling](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `BSD-3-Clause` · 🔴 abandoned

> Small table-driven x86/AMD64 decoder in C; decode+format runs 2.6-4.2x faster than Zydis, bddisasm, XED and Capstone in disas-bench.

| | |
|---|---|
| **Beats** | Capstone, Zydis, Intel XED, bddisasm, udis86, BeaEngine (x86/AMD64 disassembler libraries); no GNU as, NASM or MASM comparison |
| **Claimed result** | Decode only: 92.17 MB/s vs Zydis 34.19, XED 55.39, bddisasm 35.48, udis86 80.72 (about 2.7x Zydis, 1.7x XED, derived from page data). Decode+format: 58.85 MB/s vs Capstone 14.02, Zydis 22.24, XED 15.67, bddisasm 16.00 (about 4.2x Capstone, 2.6x Zydis, derived from page data). README: 'ultra fast', and quotes a 2014 thesis that benchmarked five open-source disassembly libraries and chose diStorm3 for best performance. |
| **Workload** | Decoding only, and decoding plus formatting, of the 77 MB .text section of Firefox 86.0.1's 64-bit xul.dll, throughput in MB/s (computed as bytes/1024/1024 per second). The README does not state the loop count: bench.py's built-in default is 20 passes over the 36.4 MiB section of the older 63 MB input/xul.dll checked into the repo, and with a custom file and no loop-count argument it scales the count to keep the same total bytes (about 9 passes over a 77 MB section, derived from bench.py). The Firefox 86 xul.dll itself is not in the repo. |
| **Metric** | throughput |
| **Hardware** | Intel Core i5-6600K, Kubuntu 21.04 (README); test file xul.dll from Firefox 86.0.1.7739, 77 MB code section |
| **Compiler and flags** | Kubuntu 21.04, gcc 10.3.0, Rust 1.52.1 (disas-bench README). make-all.sh builds the C libraries with gcc and LTO: Capstone and bddisasm as CMake Release builds with CFLAGS=-flto, XED via mfile.py --opt=3 --extra-flags=-flto, diStorm via its own make/linux Makefile (current version: -fPIC -O2 -std=c99) with -flto prepended, BeaEngine patched to -O3 -flto, udis86 without LTO (it got slower). The C bench drivers (bench/\*/Makefile) are built with -flto -O3; the Zydis driver is a CMake Release build with CFLAGS=-flto. The Rust drivers (bench/iced-x86/Cargo.toml, bench/yaxpeax/Cargo.toml) use a release profile with opt-level=3, lto=true, codegen-units=1 and no target-cpu setting. C libraries and yaxpeax-x86 are pinned git submodules (last updated March 2021); iced is pulled unpinned from its git master at build time. |
| **Adoption** | 1.3k stars |
| **Last commit** | 2021-12-18 |
| **Links** | [repository](https://github.com/gdabah/distorm) · [benchmark](https://github.com/icedland/disas-bench) |

## Verdict

In icedland/disas-bench (June 2021, i5-6600K, Kubuntu 21.04, gcc 10.3.0 with -flto -O3 drivers, one run per library over the .text of Firefox 86 xul.dll) diStorm decoded at 92.17 MB/s and decoded+formatted at 58.85 MB/s, against Zydis 34.19/22.24, XED 55.39/15.67, bddisasm 35.48/16.00 and Capstone 14.02 (decode+format; it has no decode-only mode), while iced (256.69/149.21) and yaxpeax (182.08 decode) were faster. The October 2025 athre0z/disas-bench charts (Ryzen 9 9950X with GCC 13.3, i9-13900K with GCC 14.2; bar lengths read against axis ticks, approximate) keep the order: diStorm about 99 and 93 MB/s decode+format vs Capstone about 27 and 26, Zydis full about 33 and 35, XED about 21 and 19, bddisasm about 47 and 35; decode-only about 169 and 153 vs Zydis full about 50 and 56, XED about 67 and 73, bddisasm mini about 179 and 179, iced about 362 and 390 MB/s (derived from page data).

## Use it when

- Bulk linear sweeps over legacy or baseline x86-64 code (SSE/AVX1-era compilers, Windows binaries, 32-bit and 16-bit code) where decode or decode+format throughput matters and the C decoders you have are Capstone, Zydis, XED or bddisasm.
- Flow-control scanning: DF_RETURN_FC_ONLY and the DF_STOP_ON_CALL/RET/BRANCH flags filter or stop inside the decoder, which suits call-graph or hook-site discovery (the author's distormx hooking library is built on it).
- Embedding a tiny (\~45 KB), dependency-free, BSD-licensed decoder into a C or C++ tool where a larger multi-architecture framework is unwanted.
- Python scripting that needs a C-speed x86 decoder (distorm3 package), provided the instruction-set gaps below do not matter.

## Skip it when

- Code built for x86-64-v3/v4 or with hand-written SIMD: AVX2 (issue #77, open since 2015; the maintainer wrote in 2022 'It's too hard to implement for outsiders'), AVX-512/ZMM (#186), BMI1/BMI2, ADX, SHA and ENDBR64 (#188) are not decoded; mnemonics.h has no VPERMD, VPBROADCASTD, VPGATHER\*, ANDN, PDEP, PEXT, MULX, KMOV or ENDBR64.
- When you need the fastest decoder regardless of language: iced and yaxpeax-x86 decode 2-3x faster in every disas-bench run, and bddisasm's mini decoder ties diStorm on decode-only in the 2025 runs.
- When you need encoding/assembly (it has no assembler) or other architectures (x86 only; use Capstone).
- Projects that need fixes or new instructions: last commit 2021-12-18 (v3.5.3), PyPI still at 3.5.2 (2021-03-19) with only a win32 cp37 wheel, 10 open issues and 6 open PRs.

## How it is fast

Opcode lookup walks a trie of statically generated tables ('gates', 256-entry for opcode bytes, 8 or 72 for ModR/M reg fields) built by the disOps generator, so most instructions resolve in about three array lookups. The decoder allocates nothing, works on a stack copy of _CodeInfo, writes compact fixed-size structs into a caller-provided batch array, and formatting is a separate pass that callers can skip. Its instruction tables stop at AVX/FMA/AES/CLMUL (no AVX2, AVX-512, BMI1/2 or CET), which also keeps them small.

## Compared with alternatives

Pick diStorm over Capstone, Zydis, Intel XED, bddisasm or udis86 when you want a small C decoder with roughly 2.6-4.9x their decode+format throughput (udis86 is only 1.14x slower on decode-only) on pre-AVX2 code and can live with no AVX2/AVX-512 support; pick iced or yaxpeax-x86 when Rust is acceptable and you want 2-3x more speed with full ISA coverage, and Zydis, XED or bddisasm when correctness on modern instruction sets matters more than speed.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (make/linux, make/mac, make/win32 cdistorm.vcxproj); src/\*.c can also be source-dropped; Python extension via setup.py |
| **Dependencies** | none (C standard library only) |
| **Minimum toolchain** | C99 (Makefile uses -std=c99); MSVC project provided; header has fallbacks for MSVC without stdint.h and for TinyCC |
| **Platforms** | Host: any (big-endian handled by BE_SYSTEM macros; Linux, macOS, Windows build files). Decodes x86 16/32/64-bit only. |
| **Thread safety** | not documented; by inspection decode_internal works on a local copy of _CodeInfo, allocates no heap memory and the only static table seen (Nibble2ChrTable) is read-only, so concurrent calls on separate buffers look safe |
| **Drop-in for the baseline** | no |

## Gotchas

- Unsupported or invalid bytes come back as 1-byte entries with flags == FLAG_NOT_DECODABLE and decoding resumes at the next byte, so AVX2/AVX-512/BMI/ENDBR64 instructions are silently split into junk instructions; check the flag. In benchmarks this also means diStorm walks different instruction boundaries than full-ISA decoders in those regions: the icedland/disas-bench driver formats these entries and never counts them, and the later athre0z driver counts valid vs bad instructions but the README does not publish the counts, so the share of xul.dll diStorm could not decode is unknown.
- SUPPORT_64BIT_OFFSET must be defined the same way in the library build and in your code, or you get an unresolved-symbol link error (distorm.h comment); distorm_decode needs maxInstructions &gt;= 15.
- DECRES_MEMORYERR is the normal 'output array full' return, not a failure: advance code by the last instruction's addr+size and call again, as the benchmark driver does.
- Known decode bugs left open: pushf and pushfw (9c / 66 9c) both decode as pushf in 64-bit mode (#181); the text formatter has no syntax option (one fixed Intel-style format).

## Known shortcomings

- icedland/disas-bench numbers (2021-06-11, i5-6600K, -flto -O3) match, but they are one-shot timings on an off-spec baseline set (other disassemblers, not GNU as/NASM/MASM); abandoned since 2021-12-18. Workload is about 9 passes over 77 MB (FF86 xul.dll not in the repo).
- Enricher: cannot decode AVX2 (#77 open since 2015), AVX-512 (#186), BMI1/2 or ENDBR64 (#188); unsupported bytes come back as 1-byte FLAG_NOT_DECODABLE entries and decoding resyncs at the next byte, so diStorm walks different instruction boundaries than full-ISA decoders on xul.dll and the icedland driver formats these entries without counting them (share unknown); athre0z/disas-bench October 2025 charts (9950X, 13900K) put diStorm at about 99/93 MB/s decode plus format vs Capstone about 27/26, decode-only about 169/153 tying bddisasm mini at about 179, with iced and yaxpeax faster; PyPI stuck at 3.5.2 (2021-03-19).

## Caveats and trade-offs

Numbers are from the iced author's disas-bench fork (June 2021, i5-6600K) with the diStorm submodule of March 2021; diStorm's last commit is 2021-12-18 (v3.5.3), so it is abandoned and instruction-set coverage added since then by other decoders was not checked. The diStorm README itself gives no numbers, only 'ultra fast' and a 2014 thesis quote ('chose diStorm3, which had the best performance'). The benchmark loop count is not stated (see workload). Each driver runs once per configuration (no repetitions or variance); the C drivers time CPU time with clock(), the Rust drivers wall time with millisecond resolution. The decode+format driver discards distorm_format64's output, but its time is well above decode-only (58.85 vs 92.17 MB/s), so formatting work is being timed. Formatters differ in output syntax between libraries. The yaxpeax author's later fork (i7-12700K, GCC 11, rustc 1.67 nightly, bar chart without numbers) shows diStorm at roughly 138 MB/s decode and 86 MB/s decode+format, still ahead of Capstone, XED, Zydis and bddisasm but behind iced and yaxpeax (values read off the bars, approximate). The comparison is decode/disassembly throughput against other disassembler libraries, not assembly speed against GNU as, NASM or MASM (the category's spec baseline); objdump/libopcodes was not tested.

C library with a single decompose API (returns a structured description, optional text formatting), about 45 KB, x86/AMD64 only; Python bindings (distorm3). No commits since 2021 (date read from the GitHub commits page), so recent instruction-set extensions are unlikely to decode.

## Maintenance

Abandoned since 2021-12-18 (v3.5.3; the maintainer declined AVX2 work in 2016 and 2022), but BSD-3-Clause, dependency-free C99 and small enough to vendor for pre-AVX2 x86 code.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** icedland/disas-bench README (results commit 689f3c8, 2021-06-11) lists diStorm at 92.17 MB/s decode and 58.85 MB/s decode+format against Capstone, Zydis, XED, bddisasm, udis86 and BeaEngine; the harness is public (bench.py, make-all.sh, bench/distorm/main.c and Makefile) with gcc 10.3.0, -flto -O3 driver flags in the Makefiles and an i5-6600K stated, so it is reproducible and third-party run (by the iced author).
- **Verifier notes:** Numbers match the disas-bench README rows exactly; tier A holds (public harness, compiler, flags in the per-library Makefiles, CPU). Corrected the workload (the README does not say 20 loops; bench.py would use about 9 passes over the 77 MB section unless a loop count was passed) and filled in the flags the record had not inspected. Shortcomings: abandoned since 2021-12, one-shot timings, off-spec baseline (disassemblers, not GNU as/NASM/MASM).
- **Fields the verifier corrected:** `workload`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-01 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/icedland/disas-bench>
  - <https://github.com/icedland/disas-bench/commits/master>
  - <https://github.com/icedland/disas-bench/tree/master/input>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/make-all.sh>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/bench.py>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/bench/distorm/Makefile>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/bench/distorm/main.c>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/bench/load_bin.inc>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/input/xul.dll>
  - <https://raw.githubusercontent.com/iximeow/disas-bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/iximeow/disas-bench/HEAD/bench-ath.png>
  - <https://github.com/gdabah/distorm>
  - <https://github.com/gdabah/distorm/commits/master>
  - <https://raw.githubusercontent.com/gdabah/distorm/HEAD/COPYING>
  - <https://raw.githubusercontent.com/gdabah/distorm/HEAD/README.md>
  - <https://raw.githubusercontent.com/gdabah/distorm/HEAD/make/linux/Makefile>
- **Sources the enricher read:**
  - <https://github.com/gdabah/distorm>
  - <https://github.com/gdabah/distorm/commits/master>
  - <https://github.com/gdabah/distorm/issues>
  - <https://github.com/gdabah/distorm/issues?q=is%3Aissue+avx>
  - <https://github.com/gdabah/distorm/issues/77>
  - <https://raw.githubusercontent.com/gdabah/distorm/HEAD/README.md>
  - <https://raw.githubusercontent.com/gdabah/distorm/HEAD/COPYING>
  - <https://raw.githubusercontent.com/gdabah/distorm/HEAD/include/distorm.h>
  - <https://raw.githubusercontent.com/gdabah/distorm/HEAD/include/mnemonics.h>
  - <https://raw.githubusercontent.com/gdabah/distorm/HEAD/make/linux/Makefile>
  - <https://raw.githubusercontent.com/gdabah/distorm/HEAD/setup.py>
  - <https://raw.githubusercontent.com/gdabah/distorm/HEAD/src/config.h>
  - <https://raw.githubusercontent.com/gdabah/distorm/HEAD/src/decoder.c>
  - <https://raw.githubusercontent.com/gdabah/distorm/HEAD/src/textdefs.c>
  - <https://raw.githubusercontent.com/gdabah/distorm/HEAD/src/instructions.c>
  - <https://pypi.org/pypi/distorm3/json>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/bench.py>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/make-all.sh>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/bench/distorm/main.c>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/bench/distorm/Makefile>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/bench/load_bin.inc>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/bench/zydis/main.c>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/bench/xed/main.c>
  - <https://raw.githubusercontent.com/iximeow/disas-bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/bench-amd.png>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/bench-intel.png>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/bench.py>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/make-all.sh>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/bench/distorm/main.c>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/bench/distorm/Makefile>
  - <https://github.com/athre0z/disas-bench/commits/master>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/gdabah/distorm`) · [data/wave13/enrich/raw/github_com_gdabah_distorm.json](../../../data/wave13/enrich/raw/github_com_gdabah_distorm.json) (enrichment confidence 0.8)

</details>
