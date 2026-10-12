# iced (iced-x86)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assemblers and assembly tooling](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust x86/x64 decoder, formatter, encoder and assembler; decodes 4-7x faster than Zydis, XED and bddisasm in disas-bench.

| | |
|---|---|
| **Beats** | Capstone, Zydis, Intel XED, bddisasm, diStorm, udis86, BeaEngine (x86/x64 disassembler libraries); no GNU as, NASM or MASM assembler comparison |
| **Claimed result** | Decode only: 256.69 MB/s vs Zydis 34.19, Zydis (min) 61.33, XED 55.39, bddisasm 35.48, diStorm 92.17 (about 7.5x Zydis and 4.6x XED, derived from page data). Decode+format: 149.21 MB/s vs Capstone 14.02, Zydis 22.24, XED 15.67, bddisasm 16.00, diStorm 58.85 (about 10.6x Capstone, 6.7x Zydis, derived from page data). iced README claim: 'Decodes &gt;250 MB/s and decode+format &gt;130 MB/s'. |
| **Workload** | Decoding only, and decoding plus formatting, of the 77 MB .text section of Firefox 86.0.1's 64-bit xul.dll, throughput in MB/s (computed as bytes/1024/1024 per second). The README does not state the loop count: bench.py's built-in default is 20 passes over the 36.4 MiB section of the older 63 MB input/xul.dll checked into the repo, and with a custom file and no loop-count argument it scales the count to keep the same total bytes (about 9 passes over a 77 MB section, derived from bench.py). The Firefox 86 xul.dll itself is not in the repo. |
| **Metric** | throughput |
| **Hardware** | Intel Core i5-6600K, Kubuntu 21.04 (README); test file xul.dll from Firefox 86.0.1.7739, 77 MB code section |
| **Compiler and flags** | Kubuntu 21.04, gcc 10.3.0, Rust 1.52.1 (disas-bench README). make-all.sh builds the C libraries with gcc and LTO: Capstone and bddisasm as CMake Release builds with CFLAGS=-flto, XED via mfile.py --opt=3 --extra-flags=-flto, diStorm via its own make/linux Makefile (current version: -fPIC -O2 -std=c99) with -flto prepended, BeaEngine patched to -O3 -flto, udis86 without LTO (it got slower). The C bench drivers (bench/\*/Makefile) are built with -flto -O3; the Zydis driver is a CMake Release build with CFLAGS=-flto. The Rust drivers (bench/iced-x86/Cargo.toml, bench/yaxpeax/Cargo.toml) use a release profile with opt-level=3, lto=true, codegen-units=1 and no target-cpu setting. C libraries and yaxpeax-x86 are pinned git submodules (last updated March 2021); iced is pulled unpinned from its git master at build time. |
| **Adoption** | 3.6k stars |
| **Last commit** | 2026-07-14 |
| **Links** | [repository](https://github.com/icedland/iced) · [benchmark](https://github.com/icedland/disas-bench) |

## Verdict

In iced's own disas-bench fork (2021-06-11; i5-6600K, Kubuntu 21.04, gcc 10.3.0 with LTO for the C libraries, Rust 1.52.1 with LTO, Firefox 86 xul.dll 77 MB .text) iced decoded at 256.69 MB/s vs diStorm 92.17, Zydis (min) 61.33, XED 55.39, bddisasm 35.48 and Zydis 34.19, and decoded+formatted at 149.21 MB/s vs diStorm 58.85, Zydis 22.24, XED 15.67 and Capstone 14.02 (10.6x Capstone, derived). The upstream athre0z/disas-bench charts from October 2025 (Ryzen 9 9950X; i9-13900K) still put iced 2-7x ahead of every C library (decode+format about 160 MB/s vs Capstone 27 and Zydis 33 on the 9950X) but behind yaxpeax-x86.

## Use it when

- Bulk disassembly of large x86-64 binaries (whole .text sections, crash-dump or JIT-code scanning) where the decoder is the bottleneck and the caller is Rust or one of the bindings.
- Tools that need decode, re-encode and assemble in one library: moving or hooking code (BlockEncoder fixes up branches), patching, or emitting instructions with CodeAssembler.
- Analysis passes that need per-instruction register, memory and flag effects or CPUID feature classes without a second library.
- no_std or WebAssembly targets: the crate supports #![no_std] (with alloc) and ships an npm/WASM build; features can be trimmed (decoder only, one formatter).

## Skip it when

- Raw decode speed is the only criterion: the current upstream athre0z/disas-bench charts (October 2025, Ryzen 9 9950X and i9-13900K) show yaxpeax-x86 ahead of iced in both decode only (about 460 vs 360 MB/s and 405 vs 390 MB/s) and decode+format (about 198 vs 160 and 192 vs 166 MB/s); values read off the bars.
- C or C++ projects that want a native API: there is none (open issues #728 'C/C++' and #775 'Support for C?'), so you need your own Rust FFI shim; Zydis, XED, bddisasm or diStorm link directly.
- Non-x86 ISAs, or Intel APX: APX support is an open request (#626, October 2024).
- You need formatted text in nasm, gas or Intel syntax at the benchmarked speed: the fast path is masm-style SpecializedFormatter only; the general formatters are about 3.3x slower per the crate README, which puts decode+format near 45 MB/s on the 2021 machine (derived estimate), below diStorm's 58.85.
- You depend on frequent releases: the last crates.io release is 1.21.0 (2024-01-20); open issues #762 and #783 ask for a new one and master has seen mostly dependency bumps since.

## How it is fast

The decoder dispatches through 256-entry handler tables per opcode map (legacy, VEX, EVEX, XOP, MVEX), each entry a (decode fn pointer, handler data) pair, and reads operand bytes with unaligned pointer loads guarded by one bound check against a pointer capped at 15 bytes past the instruction start. decode_out writes into a caller-owned 40-byte struct, so nothing is allocated or returned by value. The benchmarked formatter is SpecializedFormatter&lt;TraitOptions&gt;, a masm-only formatter whose options are compile-time trait constants (db/dw/dd/dq support and output-capacity checks compiled out); the crate README says it is about 3.3x faster than the general formatters for decode+format.

## Compared with alternatives

Over yaxpeax-x86 when you also need an encoder, assembler, instruction-info API, several output syntaxes or .NET/Python/JS/Java bindings; yaxpeax-x86 now edges it on raw decode in upstream disas-bench. Over diStorm3, Zydis, XED and bddisasm when you can call Rust: iced decodes 2-7x faster than all of them in both the 2021 and 2025 runs, but those four have native C APIs.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | lazy_static (serde optional); also published to NuGet, PyPI, npm and Maven |
| **Minimum toolchain** | Rust 1.57 for crates.io 1.21.0 (rust_version in crates.io metadata); master's Cargo.toml says 1.64.0 |
| **Platforms** | any Rust target, including no_std and wasm32; decodes x86 16/32/64-bit code only |
| **Thread safety** | not documented; Decoder and formatter are per-use objects over borrowed input, so use one per thread |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness note (icedland/disas-bench, the 2021 numbers): the iced driver lets the decoder skip every byte of an invalid instruction and formats Code::INVALID entries, while the current upstream athre0z/disas-bench iced driver counts valid and bad instructions, re-syncs one byte after an invalid decode and skips formatting it; libraries therefore did not walk identical instruction streams in the 2021 run. The effect on a mostly valid xul.dll .text is probably small but was never quantified.
- Also in that harness: the decode-only driver never reads the decoded Instruction, the C drivers time CPU time with clock() while the Rust drivers time wall clock in whole milliseconds, each configuration runs once, MB/s is really MiB/s, and iced is built from unpinned git master. The README's '&gt;250 MB/s, &gt;130 MB/s' claim links to disas-bench commit a865849, not the 2021-06-11 results commit.
- Peak decode+format speed needs SpecializedFormatter with ENABLE_DB_DW_DD_DQ = false and the unsafe verify_output_has_enough_bytes_left() overridden to return false, plus LTO and codegen-units = 1 in your release profile, exactly as the crate README's 'Disassemble as fast as possible' section and the bench driver do. Its masm output is not guaranteed to re-assemble.
- decode_out on bad bytes returns Code::INVALID and advances by the bytes consumed, not by one; resync yourself (as upstream's driver does) if you need byte-granular recovery. Open issue #828 reports a decoder/encoder length mismatch for redundant REX prefixes.

## Known shortcomings

- disas-bench is the iced author's own run: the cheapest SpecializedFormatter is pitted against general C formatters; no C/C++ API (Rust, .NET, Python, JS); recent commits are dependabot only; off-spec baseline set (disassemblers).
- Harness flaw in the 2021 icedland/disas-bench fork: the iced driver skips every consumed byte of an invalid instruction and formats INVALID entries while bddisasm and yaxpeax step one byte and skip formatting, so libraries did not walk identical streams (upstream athre0z driver now resyncs one byte; effect unmeasured). Upstream athre0z/disas-bench October 2025 charts (Ryzen 9 9950X, i9-13900K) put yaxpeax-x86 ahead of iced (about 460 vs 360 MB/s decode, 198 vs 160 decode+format, read off bars); iced remains 2-7x ahead of every C library. Numbers use SpecializedFormatter only (general formatters about 3.3x slower); no C API, no APX, last release 1.21.0 (2024-01-20).

## Caveats and trade-offs

First-party run: disas-bench is a fork of athre0z/disas-bench (MIT, Joel Höner 2017) hosted in iced's own organisation, and the June 2021 results were committed by the iced author; the iced driver's Cargo.toml was written by the yaxpeax author. iced is pulled unpinned from git master at build time, so the measured version is whatever master was in June 2021. The benchmark loop count is not stated (see workload). Each driver runs once per configuration (no repetitions or variance); the C drivers time CPU time with clock(), the Rust drivers wall time with millisecond resolution. The decode-only driver never reads the decoded Instruction (only the decoder position advances), so LTO could drop some operand stores. The decode+format driver uses iced's SpecializedFormatter from the fast_fmt feature with db/dw/dd/dq output disabled and the output-buffer check turned off, the cheapest formatter iced offers, while the C libraries use their general formatters; formatted text differs between libraries. Capstone and BeaEngine have no decode-only mode. The yaxpeax author's later fork (i7-12700K, GCC 11, rustc 1.67 nightly, bar chart only) shows iced at roughly 357 MB/s decode and 217 MB/s decode+format, with yaxpeax-x86 about level on decode (values read off the bars). iced has no C or C++ API (it ships Rust, .NET, Java, Python, JavaScript/WebAssembly and Lua bindings), so C++ users need their own FFI shim. The five newest commits (2026-07-14) are dependabot dependency bumps. Decode/disassembly throughput against other disassemblers, not assembly speed against GNU as, NASM or MASM (the category's spec baseline); objdump was not tested. [retier] First-party run of a fork of athre0z/disas-bench (MIT); iced built from unpinned git master in June 2021. Harness flaw: the fork's iced driver skips every consumed byte of an invalid instruction and formats Code::INVALID entries, while the bddisasm and yaxpeax drivers step one byte and skip formatting, so the libraries did not walk identical instruction streams (upstream's current iced driver resyncs one byte; effect unmeasured). The decode-only driver never reads the decoded Instruction; C drivers time CPU time with clock(), Rust drivers wall clock in whole milliseconds; each configuration runs once; MB/s is MiB/s. Decode+format uses iced's SpecializedFormatter (fast_fmt, db/dw/dd/dq disabled, output-buffer check off), about 3.3x faster than its general formatters, against the C libraries' general formatters. Upstream athre0z/disas-bench October 2025 charts (Ryzen 9 9950X, i9-13900K) show yaxpeax-x86 ahead of iced, about 460 vs 360 MB/s decode and 198 vs 160 MB/s decode+format (read off bars); iced stays 2-7x ahead of every C library. No C or C++ API (#728, #775), no APX (#626); last release 1.21.0 on 2024-01-20, dependabot-only commits since 2026-06. Disassembly throughput, not assembly speed against GNU as/NASM/MASM.

Rust library with an x86/x64 decoder, encoder, formatter and assembler; there is no official C or C++ API (bindings exist for .NET, Java, Python, JavaScript/WebAssembly and Lua), so use from C++ needs FFI or a wrapper. Decoded instruction is a 40-byte struct and the decoder does not allocate. x86/x64 only.

## Maintenance

Maintenance mode: MIT, 3.6k stars and about 3.5M crates.io downloads (1.1M recent), last release 1.21.0 on 2024-01-20, last non-bot merge 2026-06-13 and only dependency bumps since; stable and safe to depend on for x86 decoding, but no APX and no C API.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** icedland/disas-bench README (results commit 689f3c8, 2021-06-11) lists iced at 256.69 MB/s decode and 149.21 MB/s decode+format against Capstone (14.02), XED, Zydis, bddisasm, diStorm and others; harness code is public (bench.py, bench/iced-x86/src/main.rs, Cargo.toml release profile) with Rust 1.52.1/gcc 10.3.0 and an i5-6600K stated. It was run by iced's own author in iced's org, but who ran it does not matter for A.
- **Verifier notes:** All quoted numbers match the README table; tier A holds on the public harness with flags in the Cargo.toml and Makefiles. Shortcomings to record: first-party run in iced's own fork, cheapest specialized formatter versus general C formatters, no C/C++ API, one-shot timings, loop count unstated (record's '20 loops' corrected), off-spec baseline.
- **Fields the verifier corrected:** `workload`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-01 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/icedland/disas-bench>
  - <https://github.com/icedland/disas-bench/commits/master>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/make-all.sh>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/bench.py>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/bench/iced-x86/Makefile>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/bench/iced-x86/Cargo.toml>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/bench/iced-x86/src/main.rs>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/bench/cs/Makefile>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/bench/xed/Makefile>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/iximeow/disas-bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/iximeow/disas-bench/HEAD/bench-ath.png>
  - <https://github.com/icedland/iced>
  - <https://github.com/icedland/iced/commits/master>
  - <https://raw.githubusercontent.com/icedland/iced/HEAD/README.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/icedland/iced/HEAD/README.md>
  - <https://raw.githubusercontent.com/icedland/iced/HEAD/src/rust/iced-x86/README.md>
  - <https://raw.githubusercontent.com/icedland/iced/HEAD/src/rust/iced-x86/Cargo.toml>
  - <https://raw.githubusercontent.com/icedland/iced/HEAD/src/rust/iced-x86/src/lib.rs>
  - <https://raw.githubusercontent.com/icedland/iced/HEAD/src/rust/iced-x86/src/decoder.rs>
  - <https://github.com/icedland/iced/issues?q=is%3Aissue+is%3Aopen>
  - <https://github.com/icedland/iced/commits/master>
  - <https://crates.io/api/v1/crates/iced-x86>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/bench.py>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/make-all.sh>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/bench/load_bin.inc>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/bench/iced-x86/src/main.rs>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/bench/iced-x86/Cargo.toml>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/bench/iced-x86/Makefile>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/bench/zydis/main.c>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/bench/xed/main.c>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/bench/cs/main.c>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/bench/bddisasm/main.c>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/bench/distorm/main.c>
  - <https://raw.githubusercontent.com/icedland/disas-bench/HEAD/bench/yaxpeax/src/main.rs>
  - <https://raw.githubusercontent.com/iximeow/disas-bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/iximeow/disas-bench/HEAD/bench-ath.png>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/bench-amd.png>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/bench-intel.png>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/bench/iced-x86/src/main.rs>
  - <https://raw.githubusercontent.com/athre0z/disas-bench/HEAD/bench/iced-x86/Cargo.toml>
  - <https://github.com/athre0z/disas-bench/commits/master/bench/iced-x86/src/main.rs>
  - <https://github.com/athre0z/disas-bench/commits>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/icedland/iced`) · [data/wave13/enrich/raw/github_com_icedland_iced.json](../../../data/wave13/enrich/raw/github_com_icedland_iced.json) (enrichment confidence 0.8)

</details>
