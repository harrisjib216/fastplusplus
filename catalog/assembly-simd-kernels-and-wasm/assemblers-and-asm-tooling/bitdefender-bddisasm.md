# bddisasm

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assemblers and assembly tooling](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `Apache-2.0` · 🟢 active

> Bitdefender's x86/x64 instruction decoder in C with rich operand metadata; decode+format 1.4-1.8x Capstone's throughput in disas-bench.

| | |
|---|---|
| **Beats** | Capstone (decode+format throughput); Intel XED, diStorm, iced, yaxpeax-x86, Sleigh and the other listed decoders are measured in the same harness |
| **Claimed result** | disas-bench charts (bar lengths measured against axis ticks, approximate): Ryzen 9 9950X: bddisasm decode+format 46.8 MB/s, bddisasm mini decode+format 48.8 MB/s, Capstone decode+format 27.5 MB/s; decode-only bddisasm 105.7 MB/s, bddisasm mini 179.3 MB/s. i9-13900K: bddisasm decode+format 35.6 MB/s, mini 39.0 MB/s, Capstone 25.9 MB/s; decode-only 102.7 MB/s, mini 179.5 MB/s. Decode+format ratio to Capstone 1.70x (AMD) and 1.37x (Intel), mini 1.77x and 1.51x (derived from page data, chart readings). README alone: legacy decoder around 240 CPU clocks per decoded instruction (\~12M instructions/s) and mini decoder around 150 clocks (\~17M instructions/s) on an Intel Core Ultra 7 165H with BDDISASM v3.0, no baseline. |
| **Workload** | Decoding (and decoding plus formatting) the code section of a 64-bit x86 binary repeatedly in the disas-bench harness, reported as MB/s of machine code. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 9950X (Ubuntu 24.04, Linux 6.8.0) and Intel Core i9-13900K (Debian trixie, Linux 6.12.48) |
| **Compiler and flags** | Harness binaries are built with cc -O3 (bench/cs/Makefile, bench/xed/Makefile, bench/bddisasm/Makefile; bench/zydis via CMake Release), GCC 13.3 on the AMD run and GCC 14.2 on the Intel run. Libraries: Capstone 5.0.6 (submodule accf4df) built with its own Makefile, default CFLAGS -O3, CAPSTONE_ARCHS=x86; bddisasm v3.0.0 via CMake Release with BDD_LTO=ON; Zydis via CMake Release (bench/zydis/CMakeLists.txt, submodule 569320a); XED via mfile.py --opt=3 (make-all.sh). |
| **Adoption** | 1.1k stars |
| **Last commit** | 2026-10-07 |
| **Links** | [repository](https://github.com/bitdefender/bddisasm) · [benchmark](https://github.com/athre0z/disas-bench) |

## Verdict

In athre0z/disas-bench, each harness does a linear sweep that decodes (and, for the format rows, prints) the 0x2460400-byte .text section of a Firefox xul.dll 20 times; harnesses are built with cc -O3. bddisasm v3.0.0 (CMake Release, LTO, NdDecodeEx plus NdToText) is compared with Capstone 5.0.6 (Makefile -O3, x86 only, cs_disasm_iter with detail off). Decode+format: 46.8 vs 27.5 MB/s on a Ryzen 9 9950X with GCC 13.3, and 35.6 vs 25.9 MB/s on an i9-13900K with GCC 14.2 (1.70x and 1.37x); the mini decoder reaches 1.77x and 1.51x (ratios derived from chart readings).

## Use it when

- C or C++ tools that must decode and print large amounts of x86-64 code faster than Capstone: linear-sweep disassembly, binary scanners, malware triage.
- Analysis that needs semantic detail per instruction (operand access modes, implicit operands such as RFLAGS and RSP, memory access, CPUID feature flag, valid modes) without a second pass; the legacy decoder provides it and still beat Capstone in decode+format.
- Restricted environments such as Windows kernel drivers (MSBuild plus WDK targets), hypervisors and introspection agents, where the library must not allocate or depend on libc beyond nd_vsnprintf_s and nd_memset.
- Decode-heavy work where only length, mnemonic and a few operands matter: NdDecodeMini with a 64-byte INSTRUX_MINI ran at about 179 MB/s decode only on both test CPUs.
- Shellcode detection, using the bundled bdshemu emulator over the same decoder.

## Skip it when

- Maximum raw throughput when Rust or .NET is acceptable: in the same disas-bench charts, iced and yaxpeax-x86 decode+format run about 3.4-5.4x faster than bddisasm.
- Non-x86 targets or multi-architecture tools: bddisasm decodes x86/x64 only, where Capstone covers ARM, MIPS, RISC-V and more.
- AT&T syntax output: NdToText supports only Intel/MASM style.
- Drop-in replacement of Capstone code: the API, instruction and register enums, and output text all differ.
- Rust or Python users who want the v3 mini decoder: the published crate bddisasm 0.4.2 (2024-02-21) and PyPI pybddisasm 0.3.0 predate v3.0.0 (2025-07-14).

## How it is fast

Decoding walks lookup tables generated offline by isagenerator from instruction-definition files: opcode map, then opcode byte, then ModRM.mod/reg/rm, mandatory prefix, mode and so on, until it reaches an instruction leaf (NdDecodeInstruction in bdx86_decoder.c). Nothing is allocated and there is no global state, so each call touches only the caller's INSTRUX. v3.0.0 moved validity checks into the tree walk so only instructions that need them pay for them. It also added the mini decoder, which skips operand and metadata expansion; disas-bench measured it at about 1.7x the legacy decoder for decode only (179 vs 104-106 MB/s). Options in ND_CONTEXT remove more work: ND_OPTION_ONLY_EXPLICIT_OPERANDS (the changelog claims 235 to 200 clocks per instruction), ND_OPTION_SKIP_ZERO_INSTRUX and ND_OPTION_SKIP_CACHE_IBYTES.

## Compared with alternatives

Pick bddisasm over Zydis (full decode+format about 33.3 MB/s against 46.8 for bddisasm on the 9950X chart, derived from page data) and Capstone when you need a C library with the richest per-instruction semantics and no allocation, kernel use included. Pick iced or yaxpeax-x86 when raw decode speed matters most and Rust or .NET bindings are fine. Pick diStorm3 or Intel XED when you need their particular C APIs or XED's Intel-authoritative tables.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none. With the CMake build, bddisasm itself supplies nd_vsnprintf_s and nd_memset when libc has vsnprintf and memset. With the Make (Linux) and MSBuild (Windows) builds, the integrator must supply both functions. |
| **Minimum toolchain** | C11 (C_STANDARD 11), CMake 3.16+; tested with GCC and Clang on Linux and MSVC (Visual Studio 2019) on Windows; the Windows kernel build needs MSBuild with WDK 1903. Python 3 is needed only to regenerate the decode tables. |
| **Platforms** | Decodes x86 and x86-64 code (16/32/64-bit modes). The library is portable C that runs in user, kernel and hypervisor mode on Windows and Linux per the README. The only measured host CPUs are x86-64 (Ryzen 9 9950X, i9-13900K, Core Ultra 7 165H). |
| **Thread safety** | Thread-safe by design per the README: no global mutable state and no allocation. Each thread passes its own INSTRUX/INSTRUX_MINI and ND_CONTEXT. |
| **Drop-in for the baseline** | no |

## Gotchas

- The legacy NdDecodeEx zeroes the whole roughly 480-byte INSTRUX and decodes implicit operands on every call. disas-bench uses this default path; it does not pass ND_OPTION_ONLY_EXPLICIT_OPERANDS, and Capstone runs with detail off. The legacy decode+format row therefore compares full-detail bddisasm with no-detail Capstone, which understates bddisasm rather than inflating it. For throughput, use NdDecodeMini or the context options.
- By default, decoding uses ND_VEND_ANY and ND_FEAT_ALL, so MPX, CET and CLDEMOTE encodings in the wide-NOP space decode as those instructions rather than as NOPs. Set FeatMode to ND_FEAT_NONE if you need NOP semantics; otherwise output can differ from other disassemblers.
- Until 3.0.2 (commit 8017978, 2026-10-06), NdFetchModrmSibDisplacement decoded 16-bit displacement-only addressing wrongly: it skipped the displacement of mod=00 rm=110 and expected one for rm=101. The fix leaves the 32/64-bit path unchanged, so the 64-bit disas-bench numbers, measured on v3.0.0, are unaffected. Users decoding 16-bit code should take 3.0.2 or later.
- The README speed figures (about 240 clocks per instruction legacy and 150 mini, on a Core Ultra 7 165H) have no baseline and do not say whether formatting is included. The disas-bench timings come from one clock() run per tool (20 passes over the 0x2460400-byte .text of a checked-in Firefox xul.dll) with no variance reported, and the chart values are bar lengths read off the PNGs.

## Known shortcomings

- disas-bench chart pixels: 1.70x Capstone decode+format on AMD and 1.37x on Intel (derived), slower than iced, yaxpeax-x86 and diStorm; one timed run per tool; off-spec baseline set (disassemblers, not assemblers).
- Enricher: the comparison is tilted against bddisasm (NdDecodeEx zeroes a \~480-byte INSTRUX and decodes implicit operands with ND_OPTION_ONLY_EXPLICIT_OPERANDS unused while Capstone runs with detail off); the 3.0.2 fix (commit 8017978, 2026-10-06) touches 16-bit displacement-only addressing and leaves the 64-bit bench path unchanged; the Rust crate 0.4.2 and pybddisasm 0.3.0 predate the v3 mini API.

## Caveats and trade-offs

Smaller win than iced, yaxpeax-x86 and diStorm in the same charts (iced and yaxpeax decode+format are about 3.4-5.4x faster than bddisasm); the README's own throughput numbers carry no baseline. Each tool is timed in a single run (clock() CPU time over 20 passes of the 0x2460400-byte code section of a checked-in Firefox xul.dll), with no repetitions or variance reported. disas-bench is maintained by Joel Hoener (athre0z), a Zydis copyright holder; the AMD chart was produced by iximeow (yaxpeax-x86 author, 2025-10-24) and the Intel chart by athre0z (2025-10-26). Chart values are bar lengths read off PNGs against the axis ticks (approximate, about +/-1 MB/s), not a text table. Capstone appears only as a decode+format row (cs_disasm_iter, detail off), so decode+format rows are the like-for-like comparison; formatted text differs in detail between libraries. The bddisasm v3.0.0 update and the mini-decoder rows were contributed to disas-bench by ianichitei (2025-10-10), who also authored earlier bddisasm updates there.

C library with Python and Rust bindings, directly usable from C++. Includes a 'mini' decoder with reduced detail and a shellcode-detection emulator (not benchmarked). Decode+format advantage over Capstone is modest.

## Maintenance

Actively maintained by Bitdefender: v3.0.3 released 2026-10-07 after a 16-bit addressing fix on 2026-10-06. Apache-2.0, plain C11 with no dependencies, available through vcpkg and CMake FetchContent, so it is easy to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** disas-bench publishes the harness (bench/bddisasm/main.c, bench/cs/main.c, bench.py, make-all.sh), the flags (-O3 Makefiles, CMake Release, Capstone Makefile default -O3), the compilers (GCC 13.3, GCC 14.2) and the CPUs (Ryzen 9 9950X, i9-13900K), and its charts show bddisasm decode+format ahead of Capstone on both.
- **Verifier notes:** Record accurate; chart readings re-measured from the PNG pixels match the record within rounding (1.70x AMD, 1.37x Intel vs Capstone on decode+format). Metadata confirmed: Apache-2.0, 1.1k stars, 120 forks, not a fork or archived, last commit 2026-10-07 (active). Shortcomings: modest win, slower than iced/yaxpeax/diStorm, single-run timings, suite owner co-authored Zydis.
- **Fields the verifier corrected:** `claimed_speedup`, `baseline`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-07 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/bench-amd.png>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/bench-intel.png>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/bench.py>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/make-all.sh>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/bench/cs/Makefile>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/bench/cs/main.c>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/bench/xed/Makefile>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/bench/load_bin.inc>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/LICENSE>
  - <https://github.com/athre0z/disas-bench/tree/master/libs>
  - <https://github.com/athre0z/disas-bench/commits/master>
  - <https://github.com/athre0z/disas-bench/tree/master/input>
  - <https://raw.githubusercontent.com/capstone-engine/capstone/accf4df/Makefile>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/bench/bddisasm/main.c>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/bench/bddisasm/Makefile>
  - <https://github.com/bitdefender/bddisasm>
  - <https://github.com/bitdefender/bddisasm/commits/master>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/bitdefender/bddisasm/HEAD/README.md>
  - <https://raw.githubusercontent.com/bitdefender/bddisasm/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/bitdefender/bddisasm/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/bitdefender/bddisasm/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/bitdefender/bddisasm/HEAD/inc/bddisasm.h>
  - <https://raw.githubusercontent.com/bitdefender/bddisasm/HEAD/inc/bddisasm_version.h>
  - <https://raw.githubusercontent.com/bitdefender/bddisasm/HEAD/inc/bddisasm_status.h>
  - <https://raw.githubusercontent.com/bitdefender/bddisasm/HEAD/inc/bdx86_core.h>
  - <https://raw.githubusercontent.com/bitdefender/bddisasm/HEAD/inc/bdx86_api_mini.h>
  - <https://raw.githubusercontent.com/bitdefender/bddisasm/HEAD/bddisasm/bdx86_decoder.c>
  - <https://github.com/bitdefender/bddisasm/commits/master>
  - <https://github.com/bitdefender/bddisasm/commit/8017978763d0d34c5ac42c7584f81d06e1c50127>
  - <https://github.com/bitdefender/bddisasm/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/bench.py>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/make-all.sh>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/bench/bddisasm/main.c>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/bench/bddisasm/Makefile>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/bench/cs/main.c>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/bench/load_bin.inc>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/bench/zydis/main.c>
  - <https://crates.io/api/v1/crates/bddisasm>
  - <https://pypi.org/pypi/pybddisasm/json>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/bitdefender/bddisasm`) · [data/wave13/enrich/raw/github_com_bitdefender_bddisasm.json](../../../data/wave13/enrich/raw/github_com_bitdefender_bddisasm.json) (enrichment confidence 0.72)

</details>
