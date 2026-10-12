# Zydis

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assemblers and assembly tooling](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `MIT` · 🟢 active

> C11 x86/x86-64 decoder, formatter and encoder with no allocation; decode+format 1.2-1.35x Capstone's throughput in disas-bench.

| | |
|---|---|
| **Beats** | Capstone (decode+format throughput); Intel XED, diStorm, iced, yaxpeax-x86, Sleigh and the other listed decoders are measured in the same harness |
| **Claimed result** | disas-bench charts (bar lengths measured against axis ticks, approximate): Ryzen 9 9950X: Zydis (full) decode+format 33.3 MB/s vs Capstone decode+format 27.5 MB/s; decode-only Zydis (full) 50.1 MB/s, Zydis (min) 90.1 MB/s. i9-13900K: Zydis (full) decode+format 35.0 MB/s vs Capstone 25.9 MB/s; decode-only (full) 56.6 MB/s, (min) 103.3 MB/s. Decode+format ratio to Capstone 1.21x (AMD) and 1.35x (Intel) (derived from page data, chart readings). README says only 'Optimized for high performance'. |
| **Workload** | Decode+format and decode-only of the 77 MB code section of Firefox's xul.dll (64-bit x86) in the disas-bench harness |
| **Metric** | throughput |
| **Hardware** | Ryzen 9 9950X (GCC 13.3) and Intel i9-13900K (GCC 14.2) for the athre0z/disas-bench charts; the 2021 icedland fork run used an i5-6600K on Kubuntu 21.04. Test file: 0x2460400-byte code section of Firefox xul.dll. |
| **Compiler and flags** | Harness binaries are built with cc -O3 (bench/cs/Makefile, bench/xed/Makefile, bench/bddisasm/Makefile; bench/zydis via CMake Release), GCC 13.3 on the AMD run and GCC 14.2 on the Intel run. Libraries: Capstone 5.0.6 (submodule accf4df) built with its own Makefile, default CFLAGS -O3, CAPSTONE_ARCHS=x86; bddisasm v3.0.0 via CMake Release with BDD_LTO=ON; Zydis via CMake Release (bench/zydis/CMakeLists.txt, submodule 569320a); XED via mfile.py --opt=3 (make-all.sh). |
| **Adoption** | 4.4k stars |
| **Last commit** | 2026-07-27 |
| **Links** | [repository](https://github.com/zyantific/zydis) · [benchmark](https://github.com/athre0z/disas-bench) |

## Verdict

In athre0z/disas-bench, each harness linearly sweeps the 0x2460400-byte .text of a checked-in Firefox xul.dll 20 times. Zydis v4.1.0 (CMake Release, decode plus up to 5 operands plus Intel formatting) is compared with Capstone 5.0.6 (Makefile -O3, x86 only, cs_disasm_iter with detail off, which always formats). Decode+format: 33.3 vs 27.5 MB/s on a Ryzen 9 9950X (Ubuntu 24.04, GCC 13.3) and 35.0 vs 25.9 MB/s on an i9-13900K (Debian trixie, GCC 14.2), 1.21x and 1.35x (derived from page data, chart readings). The record's hardware field (i5-6600K, Kubuntu 21.04) belongs to the 2021 icedland fork, not to these charts.

## Use it when

- C or C++ disassemblers, debuggers and JIT inspectors that print x86-64 code: in disas-bench decode+format, Zydis v4.1.0 ran 33.3 MB/s vs Capstone 27.5 MB/s (Ryzen 9 9950X) and 35.0 vs 25.9 MB/s (i9-13900K), and 1.6-1.8x Intel XED's decode+format rate.
- Tools that both decode and re-encode x86 (binary rewriting, instrumentation, code generation): Zydis ships an encoder in the same library, with zasm as an asmjit-style C++ front-end.
- Kernel drivers, UEFI and other freestanding code: no malloc, a no-libc build (ZYAN_NO_LIBC) and Zycore as the only dependency, tested on Windows, macOS, FreeBSD, Linux and UEFI in user and kernel mode.
- Length decoding and mnemonic scans over large code: minimal mode reached 90-103 MB/s decode-only in disas-bench, about 1.8x the full decode.
- Output that must match a particular assembler syntax or be post-processed: Intel, MASM and AT&T styles plus per-token formatter hooks.

## Skip it when

- Raw throughput when Rust or .NET is acceptable: in the same disas-bench charts, iced (160-165 MB/s) and yaxpeax-x86 (192-197 MB/s) decode+format about 4.7-5.9x faster than Zydis, and diStorm3 2.7-3.0x faster.
- Decode-only work where XED or bddisasm already fit: Zydis full decode (50-57 MB/s) is slower than XED (67-73) and bddisasm (103-106) in the same runs.
- Storing decoded instructions in bulk: a full decode is about 1.1 KB (ZydisDecodedInstruction plus 10 ZydisDecodedOperand, issue #554, open), against roughly 40 bytes for iced; copy out what you need.
- Non-x86 targets or multi-architecture tools: Zydis decodes x86/x86-64 only, while Capstone covers ARM, MIPS, RISC-V and others.
- Tracking master: master is the unreleased 5.0.0 (project(Zydis VERSION 5.0.0.0)); the README says API stability is guaranteed only at tagged commits and ABI stability only between patch versions. The latest release is v4.1.1 (2025-02-16).

## How it is fast

Decoding walks a generated decoder tree of 16-bit nodes (src/Generated/DecoderTables.inc, built from the zydis-db instruction definitions). ZydisDecodeInstruction switches on the node type (opcode, mode, ModRM mod/reg/rm, mandatory prefix, operand size, REX.W, vector length, EVEX/MVEX bits) until it reaches a definition leaf, so there is no pattern matching and no allocation. Work is opt-in: operand decoding is a separate call limited to the operand count you pass, and minimal mode skips semantic analysis (1.8x the full decode-only throughput in disas-bench, derived from page data). Unlike Capstone, which always produces text, Zydis can stop after decoding.

## Compared with alternatives

Pick Zydis over Capstone and Intel XED when you print x86-64 from C or C++ and also want an encoder, AT&T/MASM/Intel styles with formatter hooks, or a no-libc kernel/UEFI build; it formats faster than both in disas-bench. Pick bddisasm for richer per-instruction semantics at similar or better decode+format speed (46.8 vs 33.3 MB/s on the 9950X, about equal on the i9-13900K), diStorm3 for 2.7-3x the decode+format rate in plain C, and iced or yaxpeax-x86 when raw speed matters most and Rust or .NET is acceptable.

## Integration

| | |
|---|---|
| **Form** | static lib (shared optional via ZYDIS_BUILD_SHARED_LIB; amalgamated single header plus single source in each release) |
| **Dependencies** | Zycore (zyantific's own C support library, git submodule or system package); no third-party dependencies, libc optional |
| **Minimum toolchain** | C11 (C_STANDARD 11 via zyan_set_common_flags; MSVC builds without forcing a standard), CMake 3.10+; Visual Studio 2022 project and Meson build also provided |
| **Platforms** | Decodes x86 and x86-64 code (16/32/64-bit modes). Host: any platform with a C11 compiler; tested on Windows, macOS, FreeBSD, Linux and UEFI, user and kernel mode. Packages in Debian, Ubuntu, Arch, Homebrew, NixOS and vcpkg. |
| **Thread safety** | Thread-safe by design per the README: no global mutable state and no allocation; ZydisDecoder and ZydisFormatter are read-only during decode and format, and each thread uses its own instruction, context and operand buffers. |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness note (does not inflate Zydis): disas-bench passes ZYDIS_MAX_OPERAND_COUNT_VISIBLE (5) to ZydisDecoderDecodeOperands, which clamps to instruction.operand_count, a count that includes hidden operands. So the full rows also decode implicit operands such as RSP and stack memory that the formatter never prints; the maintainers recommend operand_count_visible (issue #554). Each tool is timed once (clock() over 20 passes of the 0x2460400-byte .text of a Firefox xul.dll) with no variance, chart values are read off PNGs, and the suite belongs to Joel Hoener (athre0z), a Zydis copyright holder. The 2021 icedland/disas-bench run by the iced author (i5-6600K, gcc 10.3) independently put Zydis at 22.24 vs Capstone 14.02 MB/s decode+format (1.59x, derived from page data).
- The measured build is the v4.1.0 tag (submodule 569320a, 2024-02-04). Master has since added formatter speedups (20d64cb hex digit count, 8a6cdb0 early prefix skip, July 2026) and a decoder-tree reorder (PR #638, 78,397 to 67,585 table elements). PR #638 also fixed REX2 instructions with a mandatory 66 prefix and changed 66 0F 1E/0F 1B NOP decoding. None of these is on the hot path of the measured legacy 64-bit code, so the numbers stand for v4.1.0, but master's speed is unmeasured.
- Default decoder modes reinterpret legacy encodings: MPX, CET, LZCNT, TZCNT, CLDEMOTE, IPREFETCH and APX are on by default. F3 0F BD decodes as lzcnt rather than bsr, wide NOPs decode as MPX or CET instructions, and with APX mode 0xD5 is a REX2 prefix. Enabling KNC mode disables all AVX-512 decoding. Open issue #539: 0f 1a de decodes as 'nop ebx' and drops the esi operand (XED gives 'nop esi, ebx').
- The README example's ZydisDisassembleIntel/ATT re-initialises the decoder and formatter and decodes every operand on each call; its header says to call the separate decode and format functions if performance matters. CVE-2021-41253 (heap corruption from an uninitialised formatter buffer string, reachable only from custom formatter hooks) was fixed in v3.2.1.

## Known shortcomings

- Only 1.21x and 1.35x over Capstone in disas-bench, whose owner (athre0z) is a Zydis co-copyright holder and ran the Intel chart; harness, -O3 flags, Capstone 5.0.6, GCC 13.3/14.2 and CPU models are public; off-spec baseline set.
- disas-bench passes 5 to ZydisDecoderDecodeOperands, which clamps to operand_count including hidden operands, so Zydis decodes operands the formatter never prints (extra work, does not inflate it). The measured build is the v4.1.0 tag (569320a, 2024-02-04); the July 2026 formatter speedups on master are unmeasured; open #539: 0f 1a de drops an operand. The record's 'i5-6600K, Kubuntu 21.04' belongs to the 2021 icedland fork, not the charts, which ran on a Ryzen 9 9950X (GCC 13.3) and an i9-13900K (GCC 14.2); the icedland run gives Zydis 22.24 vs Capstone 14.02 MB/s decode+format (1.59x).

## Caveats and trade-offs

Marginal win over Capstone on decode+format; slower than iced, yaxpeax-x86, diStorm and bddisasm in the same charts, and the README makes no numeric claim. The benchmark suite is not independent of Zydis: its owner and the author of the Intel chart, Joel Hoener (athre0z), is a co-copyright holder of Zydis (LICENSE). Each tool is timed in a single run (clock() CPU time over 20 passes of the 0x2460400-byte code section of a checked-in Firefox xul.dll), with no repetitions or variance reported. disas-bench is maintained by Joel Hoener (athre0z), a Zydis copyright holder; the AMD chart was produced by iximeow (yaxpeax-x86 author, 2025-10-24) and the Intel chart by athre0z (2025-10-26). Chart values are bar lengths read off PNGs against the axis ticks (approximate, about +/-1 MB/s), not a text table. Capstone appears only as a decode+format row (cs_disasm_iter, detail off), so decode+format rows are the like-for-like comparison; formatted text differs in detail between libraries. Zydis version is whatever submodule 569320a pins (not checked). [retier] Marginal win over Capstone on decode+format; slower than iced, yaxpeax-x86, diStorm and bddisasm in the same charts, and the README makes no numeric claim. The suite's owner, Joel Hoener (athre0z), is a co-copyright holder of Zydis. Each tool is timed in a single run (clock() CPU time over 20 passes), no repetition. disas-bench passes 5 to ZydisDecoderDecodeOperands, which clamps to operand_count including hidden operands, so Zydis also decodes implicit operands the formatter never prints (extra work, does not inflate it). The measured build is the v4.1.0 tag (569320a, 2024-02-04); the July 2026 formatter speedups on master are unmeasured; open #539: 0f 1a de drops an operand. The icedland run gives Zydis 22.24 vs Capstone 14.02 MB/s decode+format (1.59x).

C99/C11 library with no dynamic allocation and a C API, directly callable from C++; also has an encoder/code-generation API. The 'min' decode mode drops most operand data, which is why it is faster than the full mode.

## Maintenance

Actively maintained (last commit 2026-07-27 on the unreleased 5.0.0 master; latest release v4.1.1, 2025-02-16), MIT-licensed, fuzzed on OSS-Fuzz, packaged by major distributions and shipped inside x64dbg, Firefox and WebKit, so it is low-risk to adopt; vendor the amalgamated release files or a tagged commit, not master.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** disas-bench publishes the harness (bench/zydis/main.c with CMakeLists.txt, bench/cs/main.c, bench.py, make-all.sh), flags (CMake Release, -O3 Makefiles), compilers (GCC 13.3, GCC 14.2) and CPUs (Ryzen 9 9950X, i9-13900K); its charts show Zydis (full) decode+format ahead of Capstone on both machines.
- **Verifier notes:** Record accurate; chart readings re-measured from the PNG pixels match within rounding (1.21x AMD, 1.35x Intel vs Capstone on decode+format). Metadata confirmed: MIT, 4.4k stars, 515 forks, not a fork or archived, last commit 2026-07-27 (active). Shortcomings: marginal win, slower than four other decoders, suite run by a Zydis co-author, single-run timings.
- **Fields the verifier corrected:** `claimed_speedup`, `baseline`, `compiler_and_flags`, `caveats`, `hardware`, `benchmark_url`
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
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/bench/zydis/main.c>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/bench/zydis/CMakeLists.txt>
  - <https://github.com/zyantific/zydis>
  - <https://github.com/zyantific/zydis/commits/master>
  - <https://raw.githubusercontent.com/zyantific/zydis/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/zyantific/zydis/HEAD/README.md>
  - <https://raw.githubusercontent.com/zyantific/zydis/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/zyantific/zydis/HEAD/CMakeLists.txt>
  - https://raw.githubusercontent.com/zyantific/zydis/HEAD/CHANGELOG.md (404)
  - <https://raw.githubusercontent.com/zyantific/zydis/HEAD/include/Zydis/Zydis.h>
  - <https://raw.githubusercontent.com/zyantific/zydis/HEAD/include/Zydis/Decoder.h>
  - <https://raw.githubusercontent.com/zyantific/zydis/HEAD/include/Zydis/DecoderTypes.h>
  - <https://raw.githubusercontent.com/zyantific/zydis/HEAD/include/Zydis/Formatter.h>
  - <https://raw.githubusercontent.com/zyantific/zydis/HEAD/include/Zydis/SharedTypes.h>
  - <https://raw.githubusercontent.com/zyantific/zydis/HEAD/include/Zydis/Disassembler.h>
  - <https://raw.githubusercontent.com/zyantific/zydis/HEAD/src/Decoder.c>
  - <https://raw.githubusercontent.com/zyantific/zydis/HEAD/src/DecoderData.c>
  - <https://raw.githubusercontent.com/zyantific/zydis/HEAD/src/Formatter.c>
  - <https://raw.githubusercontent.com/zyantific/zydis/HEAD/src/Disassembler.c>
  - <https://raw.githubusercontent.com/zyantific/zydis/HEAD/examples/DisassembleSimple.c>
  - https://raw.githubusercontent.com/zyantific/zydis/HEAD/tools/ZydisPerfTest.c (404)
  - <https://raw.githubusercontent.com/zyantific/zycore-c/HEAD/cmake/zyan-functions.cmake>
  - <https://github.com/zyantific/zydis/releases>
  - <https://github.com/zyantific/zydis/tags>
  - <https://github.com/zyantific/zydis/commits/master>
  - <https://github.com/zyantific/zydis/commit/569320a>
  - <https://github.com/zyantific/zydis/commit/7bc04ec>
  - <https://github.com/zyantific/zydis/pull/638>
  - <https://github.com/zyantific/zydis/issues?q=is%3Aissue+performance>
  - <https://github.com/zyantific/zydis/issues/554>
  - <https://github.com/zyantific/zydis/issues/539>
  - <https://github.com/zyantific/zydis/issues/15>
  - <https://github.com/zyantific/zycore-c/releases/tag/v1.5.0>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/bench.py>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/make-all.sh>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/bench/zydis/main.c>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/bench/zydis/CMakeLists.txt>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/bench/cs/main.c>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/bench/bddisasm/main.c>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/bench/load_bin.inc>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/bench-amd.png>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/bench-intel.png>
  - <https://github.com/athre0z/disas-bench/tree/master/libs>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/README.md>
  - https://nvd.nist.gov/vuln/detail/CVE-2021-41253 (WebSearch snippet only)
  - https://osv.dev/vulnerability/DEBIAN-CVE-2021-41253 (WebSearch snippet only)
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/zyantific/zydis`) · [data/wave13/enrich/raw/github_com_zyantific_zydis.json](../../../data/wave13/enrich/raw/github_com_zyantific_zydis.json) (enrichment confidence 0.75)

</details>
