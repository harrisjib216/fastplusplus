# Fadec

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assemblers and assembly tooling](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C` · `BSD-3-Clause` · 🟢 active

> Small freestanding C table-driven x86-32/x86-64 decoder plus x86-64 encoder; claims, unmeasured, to beat Capstone, Zydis and libopcodes.

| | |
|---|---|
| **Beats** | libopcodes, Capstone and Zydis (x86 decoding libraries) |
| **Claimed result** | 'Fadec is significantly faster than libopcodes, Capstone, or Zydis due to the absence of high-level abstractions and the small lookup table' (no numbers); encoder API v2 'about 3x faster than v1' (internal comparison). |
| **Workload** | Decoding x86-32 and x86-64 instructions with a lookup-table decoder; a separate x86-64 encoder is included. |
| **Metric** | throughput |
| **Adoption** | 235 stars, 33 forks, 432 commits (github.com page, 2026-10-11). Used as a git submodule (deps/fadec) by the TPDE compiler back-end framework (tpde2/tpde .gitmodules, opened). Search results also show copies at android.googlesource.com platform/external/lfi/fadec (tagged android-17.0.0_r1) and a Chromium mirror chromium.googlesource.com/external/github.com/aengelke/fadec, plus forks oleavr/fadec and GenKyoko/fadec (snippet only; googlesource host did not resolve here). |
| **Last commit** | 2026-06-01 |
| **Links** | [repository](https://github.com/aengelke/fadec) · [benchmark](https://github.com/aengelke/fadec) |

## Verdict

Only qualitative: the README says Fadec is 'significantly faster than libopcodes, Capstone, or Zydis due to the absence of high-level abstractions and the small lookup table', with no numbers, harness, compiler, flags or CPU, and the encoder v2 'about 3x faster than v1' is an internal comparison with no baseline library. Nothing in the repo or in disas-bench measures Fadec against another decoder.

## Use it when

- Embedding a decoder or encoder in freestanding or kernel-like code with no libc and no malloc (the author's stated reason for writing it).
- Compiler back-ends and JITs that emit x86-64 machine code from C or C++ and want a small programmatic encoder without assembly text parsing; the TPDE back-end framework pulls it in as deps/fadec.
- Binary scanners, verifiers and rewriters that only need instruction length, mnemonic and operands quickly, not full semantic information such as flags read and written.
- Size-sensitive builds: decoder plus encoder are about 95 KiB, and Meson options drop 32-bit or 64-bit mode, the encoder or undocumented opcodes.

## Skip it when

- When you need a measured speed advantage: there are no published numbers, no comparison harness and no disas-bench entry; Zydis, Intel XED, iced, yaxpeax-x86 and diStorm have public disas-bench MB/s figures, Fadec does not.
- Code that must follow AMD64-specific behaviour (jump operand sizes, cr8 access with lock, f3 41 90 as xchg rather than pause) or needs XOP, FMA4, MPX, HLE prefixes or Xeon Phi MVEX; 16-bit mode is not supported either.
- Analyses that need exact operand sizes, implicit operands, EFLAGS effects or CPUID feature tags straight from the decoder: Fadec omits that database and its sizes are not always exact (reconstructible, per the README).
- Encoders that must reject invalid register combinations: register-uniqueness rules (VSIB, AMX tiles, AVX-512 FP16 complex multiply) are not enforced, so you can emit encodings the CPU faults on.
- Projects that need Python or other language bindings; the README lists 'No Python API'.

## How it is fast

parseinstrs.py turns the instruction list (instrs.txt) into compact generated uint16 lookup tables (about 37 KiB for 32- and 64-bit mode together) that fd_decode walks as a trie: prefix bytes, then opcode escape (0F, 0F38, 0F3A, VEX/EVEX map), opcode byte, mandatory prefix, ModRM reg/mod fields and VEX.W/L, ending in an 8-byte packed InstrDesc of bit fields. There is no per-instruction allocation, no operand-semantics or flags database and no high-level abstraction layer, and the decoder deliberately reports operand sizes that are not always exact to stay on the fast path. Encoder v2 generates one specialised function per mnemonic, which is where its internal 'about 3x faster than v1' comes from, at a cost of about 3 MiB of code.

## Compared with alternatives

Pick Fadec over Zydis, Intel XED or bddisasm when you need a libc-free decoder and encoder of about 95 KiB that you can embed in a JIT or verifier; pick iced (256.69 MB/s decode in disas-bench), yaxpeax-x86 or diStorm3 when you need published decode throughput, and a heavier decoder such as Zydis, XED or iced when you need richer per-operand information than Fadec's compact FdInstr.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none at run time (no libc needed); Meson 0.49+ and Python 3.9+ at build time to generate the lookup tables from instrs.txt |
| **Minimum toolchain** | C11 compiler (GCC, Clang or MSVC; the Meson file has MSVC warning settings), Meson 0.49+, Python 3.9+ |
| **Platforms** | any host with a C11 compiler; decodes x86-32 and x86-64 (no 16-bit mode), encodes x86-64 only, Intel 64 semantics |
| **Thread safety** | not documented; the decode, format and encode sources hold only static const tables and no mutable global state, so concurrent calls on separate output structs and buffers look safe |
| **Drop-in for the baseline** | no |

## Gotchas

- No benchmark backs the headline claim: the only timing tool, decode-profile.c (added 2026-06-01), times Fadec alone in 64-bit mode over a raw file region, needs -l (the default length 0 decodes nothing and prints 0 MB/s) and does not check -s/-l against the file size, so it cannot reproduce 'significantly faster than libopcodes, Capstone, or Zydis'.
- fd_decode may partially write out_instr even when it returns an error, an implicit fwait is decoded as a separate instruction (finit is FD_FWAIT then FD_FINIT), and the address parameter is deprecated: pass 0 and resolve FD_OT_OFF operands yourself.
- Both encoders need at least 15 bytes of space left in the output buffer, and v2 may overwrite bytes past the returned instruction length; v2 is off by default (-Dwith_encode2=true) and is about 3 MiB of generated code with long compile times.
- Tests are hand-written data (about 3,100 decode cases in decode-test.inc, extended in March 2026 to 'cover all branches') with no fuzzing harness in the repo, and a decoder bug ('Fix collision of 3e bit and broadcast size') was fixed as recently as 2026-06-01; the README still lists low test coverage as a known issue.

## Known shortcomings

- Speed claim over libopcodes, Capstone and Zydis has no numbers; decode-profile.c (2026-06-01) times Fadec only; not in the athre0z or iximeow disas-bench candidate lists; the encoder v2 '3x faster than v1' is an internal comparison. README known issues: low test coverage, Intel-64-only semantics, inexact operand sizes. Used as a submodule by TPDE and in Android external/lfi (snippet only).
- Enricher: no numbers anywhere; decode-profile.c times Fadec alone, its -l defaults to 0 (decodes nothing) and -s/-l are unchecked against the file size; no fuzzing; a decoder bug (3e bit vs broadcast size) was fixed 2026-06-01; encoders need 15 bytes of buffer slack and v2 may overwrite bytes past the returned length.

## Caveats and trade-offs

No benchmark numbers or comparison harness anywhere: the speed claim over libopcodes, Capstone and Zydis is qualitative, and the only timing tool in the repo (decode-profile.c, added 2026-06-01) measures Fadec alone. Fadec is absent from the public disas-bench candidate lists (athre0z and iximeow forks). The encoder v2 '3x faster than v1' figure is an internal comparison with no baseline and comes at \~3 MiB code size (off by default, -Dwith_encode2=true). README lists known issues: low test coverage, register-uniqueness constraints not enforced (VSIB, AMX, AVX-512 FP16 complex multiply), decoded operand sizes not always exact, AMD64-specific behaviour not handled (Intel 64 semantics only), MPX, HLE, XOP, FMA4 and Xeon Phi unsupported. Baselines are disassembler libraries, not GNU as, NASM or MASM. Notability rests on reuse (TPDE, Android LFI, Chromium mirror) rather than stars. Canonical CI pulls from git.sr.ht/\~aengelke/fadec.

C library with no dependencies, about 95 KiB with decoder and encoder, usable in freestanding environments. Targets Intel 64 behaviour; AMD-specific differences are not handled. Decoded operand sizes are not always exact for speed.

## Maintenance

Actively maintained (commits through 2026-06-01, canonical CI on git.sr.ht/\~aengelke/fadec), BSD-3-Clause and reused by the TPDE back-end and Android's external/lfi tree, so it is a credible small dependency, but its speed claim is unmeasured (tier D).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification D, tier now D.
- **Tier reason:** The README names libopcodes, Capstone and Zydis only in an unquantified claim ('significantly faster ... due to the absence of high-level abstractions and the small lookup table'), with no numbers, harness, compiler, flags or CPU. decode-profile.c (added 2026-06-01) times only Fadec's own decode/format MB/s on a user-supplied file, with no baseline, and Fadec is absent from both athre0z/disas-bench and iximeow/disas-bench candidate lists; two WebSearch queries found no independent numbers.
- **Verifier notes:** Record is accurate: BSD-3-Clause (LICENSE opened), not a fork, not archived, last commit 2026-06-01 (active), README claim and v2 '3x' quoted correctly. Keep at tier D with the shortcoming 'no numbers, qualitative speed claim only'; under 1k stars but reused by TPDE and shipped in Android's external/lfi tree, so not rejected.
- **Fields the verifier corrected:** `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-03 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/aengelke/fadec>
  - <https://github.com/aengelke/fadec/commits>
  - <https://raw.githubusercontent.com/aengelke/fadec/HEAD/README.md>
  - <https://raw.githubusercontent.com/aengelke/fadec/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/aengelke/fadec/HEAD/decode-profile.c>
  - <https://raw.githubusercontent.com/aengelke/fadec/HEAD/meson.build>
  - <https://raw.githubusercontent.com/aengelke/fadec/HEAD/.build.yml>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/iximeow/disas-bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/iximeow/yaxpeax-x86/HEAD/README.md>
  - <https://raw.githubusercontent.com/tpde2/tpde/HEAD/.gitmodules>
- **Sources the enricher read:**
  - <https://github.com/aengelke/fadec>
  - <https://github.com/aengelke/fadec/commits/master>
  - <https://github.com/aengelke/fadec/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/aengelke/fadec/HEAD/README.md>
  - <https://raw.githubusercontent.com/aengelke/fadec/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/aengelke/fadec/HEAD/meson.build>
  - <https://raw.githubusercontent.com/aengelke/fadec/HEAD/meson_options.txt>
  - <https://raw.githubusercontent.com/aengelke/fadec/HEAD/.build.yml>
  - <https://raw.githubusercontent.com/aengelke/fadec/HEAD/decode-profile.c>
  - <https://raw.githubusercontent.com/aengelke/fadec/HEAD/fadec.h>
  - <https://raw.githubusercontent.com/aengelke/fadec/HEAD/fadec-enc.h>
  - <https://raw.githubusercontent.com/aengelke/fadec/HEAD/fadec-enc2.h>
  - <https://raw.githubusercontent.com/aengelke/fadec/HEAD/decode.c>
  - <https://raw.githubusercontent.com/aengelke/fadec/HEAD/format.c>
  - <https://raw.githubusercontent.com/aengelke/fadec/HEAD/encode.c>
  - <https://raw.githubusercontent.com/aengelke/fadec/HEAD/parseinstrs.py>
  - <https://raw.githubusercontent.com/aengelke/fadec/HEAD/instrs.txt>
  - <https://raw.githubusercontent.com/aengelke/fadec/HEAD/decode-test.c>
  - <https://raw.githubusercontent.com/aengelke/fadec/HEAD/decode-test.inc>
  - <https://raw.githubusercontent.com/tpde2/tpde/HEAD/README.md>
  - <https://raw.githubusercontent.com/tpde2/tpde/HEAD/.gitmodules>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/aengelke/fadec`) · [data/wave13/enrich/raw/github_com_aengelke_fadec.json](../../../data/wave13/enrich/raw/github_com_aengelke_fadec.json) (enrichment confidence 0.7)

</details>
