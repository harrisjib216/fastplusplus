# Keystone

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assemblers and assembly tooling](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `GPL-2.0-only` · 🟢 active

> Embeddable multi-architecture assembler library cut down from LLVM 3.9's MC layer; claims over 10x smaller footprint than full LLVM.

| | |
|---|---|
| **Beats** | LLVM as a whole (the full LLVM build whose MC layer Keystone was stripped down from; the page mentions llvm-mc but does not measure it specifically) |
| **Claimed result** | 'Keystone is more than 10 times smaller in size and in memory consumption' than LLVM; 'Initial verson of Keystone takes only 30 seconds to compile on a laptop, while LLVM needs 15 minutes to build.' |
| **Workload** | Footprint and build cost of the assembler engine itself versus the full LLVM it was stripped from; the page gives no assembling-throughput comparison. |
| **Metric** | memory |
| **Adoption** | 2.6k stars; vcpkg port 'keystone', PyPI keystone-engine 0.9.2, crates.io keystone-engine bindings |
| **Last commit** | 2026-07-18 |
| **Links** | [repository](https://github.com/keystone-engine/keystone) · [benchmark](https://raw.githubusercontent.com/keystone-engine/keystone/HEAD/docs/beyond_llvm.md) |

## Verdict

Nothing about assembling speed was measured. The only claim is the project's own statement, written for the initial 2016 version, that Keystone is more than 10 times smaller in binary size and memory use than LLVM and builds in 30 seconds on a laptop versus 15 minutes for LLVM, with no LLVM version, flags, machine or method; the gap comes from removing everything except the MC assembler.

## Use it when

- Assembling text to bytes inside a process (binary patchers, shellcode and exploit tooling, fuzzers, emulator front-ends, debugger plugins) for several ISAs through one C API or a scripting-language binding
- When linking all of LLVM just to reach the MC assembler is too heavy: the PyPI 0.9.2 manylinux x86_64 wheel carrying every backend is 1.77 MB compressed (1.37 MB on win_amd64), and LLVM_TARGETS_TO_BUILD trims architectures further
- Shellcode-style input that mixes code and data in one section, or NASM-flavoured x86 syntax, which the project page says llvm-mc handles poorly
- Batch assembly of whole snippets per call at a known base address, with KS_OPT_SYM_RESOLVER supplying addresses of external symbols

## Skip it when

- Assembly throughput: no timing against llvm-mc, GNU as, NASM or AsmJit exists, and per-call setup makes one-instruction-per-call loops (JIT-style emission) slow by design
- Recent ISA extensions: the x86, Arm and AArch64 tables come from LLVM 3.9 (2016); RISC-V was backported from LLVM 9.0.1 in March 2023 and is in no tagged release (the last is 0.9.2 from June 2020; issue #598 asks for one)
- MASM sources: keystone.h marks KS_OPT_SYNTAX_MASM 'unsupported yet', so the MASM-compatible assemblers (JWasm, UASM, Asmc) are the right tools
- Untrusted or fuzzed input without process isolation: open segfault, crash and assertion reports from short kstool inputs (#171, #181, #198, #220, #288, #307, #316, #394) and a null dereference in the EVM path (#602)
- Closed-source products without a paid licence: GPLv2-only with a FOSS-only client exception, and the commercial-licence and contact links point to keystone-engine.org, which issue #604 reports now redirects to a gambling site after the domain apparently expired

## How it is fast

It is not faster at assembling: the core is LLVM 3.9.0svn's MC layer (lexer, generic asm parser, per-target AsmParser and MCCodeEmitter tables, renamed to namespace llvm_ks) with IR, optimisers, code generators and the other LLVM subsystems removed, so the library and its build shrink while the per-instruction work stays LLVM's. The footprint claim (more than 10x smaller in size and memory, 30 s versus 15 min to build) follows from that scope cut. Each ks_asm call builds a fresh MCContext, code emitter, object streamer and parser (and re-initialises NASM directives every call, a TODO in ks.cpp), so setup cost dominates when assembling one instruction per call.

## Compared with alternatives

The catalogued siblings are mostly disassemblers (Zydis, iced, bddisasm, Intel XED) and standalone assemblers (minias, aron, JWasm, UASM, Asmc); pick Keystone when you need text-to-bytes assembly as a library call across many ISAs from C or a scripting language, and pick JWasm, UASM or Asmc for MASM sources or minias or aron for command-line x86-64 assembly where speed claims exist.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (CMake via make-lib.sh / make-share.sh); also a vcpkg port and PyPI wheels |
| **Dependencies** | none at run time; building needs CMake 3.10+ and a C++ compiler (the stripped LLVM 3.9 MC sources are bundled) |
| **Minimum toolchain** | CMake 3.10+; LLVM 3.9-era C++11 code base; commit #600 (2026-07-18) fixed builds with CMake 4, GCC 15 and MSVC |
| **Platforms** | hosts: Windows, Linux, macOS, \*BSD, Solaris; targets: Arm/Thumb, AArch64, MIPS, PowerPC, SPARC, SystemZ, Hexagon, x86-16/32/64, RISC-V (unreleased), EVM (single opcodes only) |
| **Thread safety** | README says 'thread-safe by design', but in ks.cpp the one-time target registration is guarded by an unsynchronised static bool and ks_asm/ks_option mutate the handle (source buffers, radix, comment string), so use one handle per thread and let one ks_open finish before going concurrent |
| **Drop-in for the baseline** | no |

## Gotchas

- Found this session in llvm/keystone/ks.cpp: ks_option() calls MAI-&gt;setRadix(16) on entry for every option type, before checking the option or the architecture, so selecting AT&T, GAS or Intel syntax without the RADIX16 flag, or only installing a symbol resolver, makes unprefixed numbers hexadecimal ('12(%esp)' becomes 0x12; issues #569 and #571, open since December 2023). The same unconditional line runs on EVM handles, which is consistent with the null-pointer report #602. Write immediates with an explicit 0x prefix or suffix after any ks_option call.
- ks_asm is documented to return 0 or -1, but its out-of-memory paths return KS_ERR_NOMEM (1) without setting ks_errno, so callers testing for -1 miss those failures; test for non-zero.
- The EVM mode is a whole-string, case-insensitive mnemonic lookup that returns one byte (EVMMapping.cpp): PUSH immediates, several statements per call and labels are not supported. keystone.h still labels KS_ARCH_PPC 'currently unsupported' although the README and ChangeLog list PowerPC.
- The 10x size and memory figure and the 30 s versus 15 min build time compare a 2016 build of Keystone with an entire LLVM build (optimisers, code generators, tools), not with llvm-mc's assembler code, and give no version, machine or method; the only concrete size data found are the 1.32-2.95 MB PyPI 0.9.2 wheels, each holding the full multi-architecture library.

## Known shortcomings

- Claims cover binary size, memory and build time only (docs/beyond_llvm.md), no assembly speed; the baseline is all of LLVM, not llvm-mc; no method stated; GPLv2-only plus a commercial licence; last commit 2026-07-18 after a gap since May 2023.
- Bug in llvm/keystone/ks.cpp: ks_option() forces setRadix(16) for every option type, so after selecting a syntax '12(%esp)' assembles as 0x12 (issues #569 and #571 open since December 2023); the same line is the likely cause of the EVM null dereference #602. ks_asm returns 1 (KS_ERR_NOMEM) on out-of-memory although the docs say -1. EVM mode looks up one opcode per call; the 'thread-safe' claim is undercut by unsynchronised static initialisation; tables date from LLVM 3.9; RISC-V is unreleased; the keystone-engine.org domain was lost and now redirects to a gambling site (#604).

## Caveats and trade-offs

Claim is about binary size, memory consumption and build time, not assembly throughput, and gives no measurement method, LLVM version, flags, workload or machine; 'more than 10 times' is an order-of-magnitude statement, not a reported measurement. The comparison is against all of LLVM (which carries optimizers and code generators Keystone removed by design), not against llvm-mc's assembler footprint, so the size gap follows from scope rather than efficiency. First-party doc page that refers to the project's initial version (2016 era). No assemble-time comparison with GNU as, NASM, llvm-mc or AsmJit exists in the repo, and a web search found no independent throughput benchmark. License is GPLv2 only (no 'any later version'), with a FOSS client exception file (EXCEPTIONS-CLIENT) and a paid commercial license as the alternative. The 2026-07-18 commit (build fixes for CMake 4, GCC 15 and MSVC, #600) followed a gap since May 2023, so 'active' reflects one maintenance commit.

Dual licensed: GPL-2.0 only (no 'any later version', with a client exceptions file) or a paid royalty-free commercial licence for production use. Assembler only (no linker or compiler); accepts NASM/MASM-style input in addition to LLVM syntax; many architectures (Arm, Arm64, EVM, Hexagon, Mips, PowerPC, RISC-V, Sparc, SystemZ, X86). Because it is LLVM MC underneath, per-instruction assembling speed is not claimed to differ from llvm-mc.

## Maintenance

Maintenance only: one build-fix commit (2026-07-18, #600) after a three-year gap since May 2023, 217 open issues, last release 0.9.2 in June 2020, and the official website domain lost (#604, #609); GPLv2-only with a FOSS exception, but easy to obtain through vcpkg, PyPI and crates.io bindings.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** docs/beyond_llvm.md is a first-party page that states 'more than 10 times smaller in size and in memory consumption' than LLVM and a 30 s vs 15 min build time, with no measurement method, versions, workload or machine; rough first-party numbers without methodology are C at most.
- **Verifier notes:** Quotes in claimed_speedup match docs/beyond_llvm.md word for word (including the page's 'verson' typo). Weak memory/size claim with no runtime speed evidence; record as a shortcoming that the baseline is the whole of LLVM and nothing measures assembly speed. Metadata confirmed: 2.6k stars, 542 forks, GPL-2.0 (GPLv2-only per README), last commit 2026-07-18, not archived or a fork.
- **Fields the verifier corrected:** `baseline`, `caveats`
- **Shortcomings recorded by:** verifier batch-43 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/keystone-engine/keystone/HEAD/docs/beyond_llvm.md>
  - <https://github.com/keystone-engine/keystone>
  - <https://github.com/keystone-engine/keystone/commits>
  - <https://raw.githubusercontent.com/keystone-engine/keystone/HEAD/README.md>
  - <https://raw.githubusercontent.com/keystone-engine/keystone/HEAD/COPYING>
- **Sources the enricher read:**
  - <https://github.com/keystone-engine/keystone/commits>
  - <https://github.com/keystone-engine/keystone/issues>
  - <https://github.com/keystone-engine/keystone/issues/604>
  - <https://github.com/keystone-engine/keystone/issues/571>
  - <https://github.com/keystone-engine/keystone/issues?q=is%3Aissue+thread>
  - <https://github.com/keystone-engine/keystone/issues?q=is%3Aissue+crash>
  - <https://raw.githubusercontent.com/keystone-engine/keystone/HEAD/README.md>
  - <https://raw.githubusercontent.com/keystone-engine/keystone/HEAD/docs/beyond_llvm.md>
  - <https://raw.githubusercontent.com/keystone-engine/keystone/HEAD/docs/COMPILE.md>
  - <https://raw.githubusercontent.com/keystone-engine/keystone/HEAD/docs/COMPILE-NIX.md>
  - <https://raw.githubusercontent.com/keystone-engine/keystone/HEAD/ChangeLog>
  - <https://raw.githubusercontent.com/keystone-engine/keystone/HEAD/COPYING>
  - <https://raw.githubusercontent.com/keystone-engine/keystone/HEAD/EXCEPTIONS-CLIENT>
  - <https://raw.githubusercontent.com/keystone-engine/keystone/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/keystone-engine/keystone/HEAD/SPONSORS.TXT>
  - <https://raw.githubusercontent.com/keystone-engine/keystone/HEAD/CREDITS.TXT>
  - <https://raw.githubusercontent.com/keystone-engine/keystone/HEAD/include/keystone/keystone.h>
  - <https://raw.githubusercontent.com/keystone-engine/keystone/HEAD/llvm/CMakeLists.txt>
  - <https://raw.githubusercontent.com/keystone-engine/keystone/HEAD/llvm/keystone/ks.cpp>
  - <https://raw.githubusercontent.com/keystone-engine/keystone/HEAD/llvm/keystone/EVMMapping.cpp>
  - <https://pypi.org/pypi/keystone-engine/json>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/keystone-engine/keystone`) · [data/wave13/enrich/raw/github_com_keystone_engine_keystone.json](../../../data/wave13/enrich/raw/github_com_keystone_engine_keystone.json) (enrichment confidence 0.75)

</details>
