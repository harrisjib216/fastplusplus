# aron

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assemblers and assembly tooling](README.md)</sub>

**Tier D** (directional, no numbers) · Study only · `Rust` · `MPL-2.0` · 🔴 abandoned

> Incomplete Rust x86-64 Intel-syntax assembler emitting Mach-O; a startup-bound hello-world test ran 12.9x faster than macOS as.

| | |
|---|---|
| **Beats** | macOS as (Apple's system assembler, not GNU as) |
| **Claimed result** | README screenshot (imgs/aron-bm.png) of 'hyperfine -N --warmup 10 "target/release/aron test.macos.s" "as test.macos.s"': aron 3.9 ms +/- 0.7 ms (777 runs) versus as 49.8 ms +/- 2.3 ms (60 runs), summary 'aron ... ran 12.94 +/- 2.34 times faster than as'. The README introduces it with 'This is not empirical by any means'. |
| **Workload** | Assembling the repo's test.macos.s, a 31-line clang -S (Intel syntax) output of a hello-world printf program, once per process, with aron versus the macOS assembler; timings are dominated by process startup. |
| **Metric** | compile-time |
| **Hardware** | A macOS machine; CPU model not stated. |
| **Compiler and flags** | aron built with cargo release profile (target/release); the screenshot's shell prompt shows rust v1.60.0 and C v13.1.6-clang (Apple clang 13.1.6 toolchain, which supplies the baseline as), aron v0.1.0; timed with hyperfine -N --warmup 10. No other flags stated. |
| **Adoption** | 2 stars |
| **Last commit** | 2022-10-11 |
| **Links** | [repository](https://github.com/Not-Nik/aron) · [benchmark](https://github.com/Not-Nik/aron) |

## Verdict

One README screenshot of `hyperfine -N --warmup 10` on an unnamed macOS machine (Apple clang 13.1.6 toolchain, Rust 1.60.0, aron 0.1.0) assembling a 31-line, 15-instruction clang -O0 hello-world: aron 3.9 ms against `as` 49.8 ms, 12.94 +/- 2.34x. That is process startup, the author calls it 'not empirical by any means', the objects were never compared, and aron's object omits the unwind, alignment and build-version data that `as` emits.

## Use it when

- Studying a small, readable example of a table-driven x86-64 encoder: a Python script turns a CSV of opcodes into Rust match functions, and the `object` crate handles Mach-O and relocations.
- Assembling tiny clang -O0 Intel-syntax files on macOS that use only rax-rdi, rbp- or rip-relative addressing and general-purpose integer instructions, in a loop where about 45 ms of `as` driver startup per file matters (for example a toy compiler's test suite).
- Forking a teaching assembler under MPL-2.0, as long as you are prepared to fix the encoder bugs listed under gotchas first.

## Skip it when

- Any real build: the table has no SSE/AVX instructions at all (no movaps, pxor, cvtsi2sd), no nop, endbr64 or movabs, and memory operands are only `[reg]` or `[reg +/- disp]` with no index\*scale, so typical -O1 and higher clang output fails or misassembles.
- Code that uses r8-r15 (r9 makes the assembler panic, and other extended registers are encoded as the wrong register), or that addresses through rsp, r12, or [rbp] with no displacement.
- Linux/ELF targets: `-f elf` is parsed, but main.rs hard-codes ObjectFileType::MachO, and AT&T syntax (the GNU as default) is not parsed.
- Functions that need unwinding (C++ exceptions, debuggers, profilers): `.cfi_*` directives are dropped, so the object carries no unwind info.
- Large files: there is no measurement beyond a 15-instruction file, and every line is matched linearly against 918 templates.

## How it is fast

There is no assembly-speed technique: the generated matcher (encodings.rs, which its generator script calls 'a very naive matching algorithm') tries all 918 instruction templates on every line and encodes each successful candidate to keep the shortest. The measured gap is process startup of one small Rust binary against Apple's `as`, which the verifier notes is a driver that hands off to clang's integrated assembler. aron also does less work on the test file: it drops the `.cfi_*`, `.p2align`, `.build_version` and `.subsections_via_symbols` directives that `as` turns into unwind info, alignment and Mach-O load-command data.

## Compared with alternatives

Pick minias for a small assembler whose README says it often beats GNU as and the clang assembler, or Keystone for an embeddable assembler library with LLVM MC's instruction coverage. aron makes sense only as reading material, since it emits Mach-O only, has no SSE/AVX, and misencodes r8-r15.

## Integration

| | |
|---|---|
| **Form** | crate (binary-only CLI, built from source with cargo; not published on crates.io) |
| **Dependencies** | ariadne 0.1, enum_derive 0.1, custom_derive 0.1, object 0.29 (write feature), clap 3.2.17; git submodule GregoryComer/x86-csv plus Python only to regenerate the checked-in encodings.rs |
| **Minimum toolchain** | Rust 2021 edition (1.56+); the README screenshot was built with Rust 1.60.0 |
| **Platforms** | Builds wherever Rust does; emits x86-64 Mach-O objects only (the ELF writer path exists but the CLI never selects it) |
| **Thread safety** | Not applicable (single-shot CLI); not documented |
| **Drop-in for the baseline** | partial: `aron file.s -o out.o` mirrors the `as` command line, but only for Intel-syntax files using a subset of integer instructions, and the object lacks unwind info, build-version data and real section alignment |

## Gotchas

- Register numbering bug: `TryFrom<i32> for Register` (instructions.rs) maps 8 to R8 and then 10 to R9 through 16 to R15, skipping 9. Every generated matcher calls `Register::try_from(reg as i32).unwrap()` on the ModRM reg operand, so any line where r9 could fill that field panics the assembler, and r10-r15 in that field encode as r9-r14.
- Instruction::encode swaps REX.R and REX.B: the r/m register's high bit goes to bit 2 and the reg register's to bit 0. Mixing a legacy register with r8-r15 therefore encodes the wrong registers. No SIB byte is ever written, so `[rsp+...]` and `[r12...]` operands are misencoded, and `[rbp]` without an offset becomes RIP-relative. Narrowing immediates goes through `unwrap_unchecked` (undefined behaviour on overflow).
- Unknown directives are silently ignored (`.p2align`, `.cfi_*`, `.byte/.long/.quad/.zero`, `.text/.data`), so data written through them vanishes without an error, and section alignment is hard-coded to 4. Immediates parse only as decimal: `0x10` becomes a relocation against a symbol named '0x10', and a negative hex value panics.
- Output and symbols: the output file is opened without truncate, so overwriting a larger existing file (both benchmark commands write a.out) leaves stale trailing bytes. Every non-.globl label, L_ temporaries included, is emitted as a linkage-unit (private extern) symbol. The label iterator stops at the first `.globl` name with no definition in that section, which drops the rest of the symbols in random HashMap order.

## Known shortcomings

- Downgraded C to D: the only number is a hyperfine run on a 31-line hello-world (3.9 ms vs 49.8 ms for macOS as, 12.94x) where process startup dominates; the author calls it not empirical; no CPU named, no output check; 2 stars.
- Code bugs: Register::try_from skips 9, so r9 panics and r10-r15 encode one register low; REX.R and REX.B are swapped; no SIB byte, so [rsp] and [r12] are misencoded and a bare [rbp] becomes RIP-relative; no SSE/AVX, nop or endbr64; -f elf is ignored (main.rs always writes Mach-O); the output is opened without truncate; hex immediates turn into symbol relocations. Harness flaw: it drops .cfi_\*, .p2align, .build_version and .subsections_via_symbols, so it does less work than as on top of the startup-dominated timing. Usability moved to reference.

## Caveats and trade-offs

The README says 'This is not empirical by any means'. One 31-line hello-world input (about 15 instructions), so both timings measure process launch rather than assembly: aron finishes in 3.9 ms while macOS as, a driver that hands off to clang's integrated assembler, takes 49.8 ms mostly in startup. No CPU is named, the output objects are not compared, and the assembler is self-described as incomplete, so the speedup also reflects its narrower feature set. The baseline is macOS as, not GNU as. The screenshot was taken on aron v0.1.0 (August 2022); the repo is now at 0.2.0. The language is Rust (Cargo.toml, edition 2021) although the repo page shows no language bar. [retier] The README says 'This is not empirical by any means'. One 31-line hello-world input, so both timings measure process launch (aron 3.9 ms vs macOS as 49.8 ms, a driver that hands off to clang's integrated assembler); no CPU named, output objects not compared, baseline is macOS as rather than GNU as, screenshot from v0.1.0 (August 2022). The assembler is incomplete and buggy, so it does less and wrong work than as: Register::try_from skips 9 (r9 in the ModRM reg field panics; r10-r15 encode one register low), Instruction::encode swaps REX.R and REX.B, no SIB byte is ever written ([rsp+...] and [r12...] misencoded, bare [rbp] becomes RIP-relative), no SSE/AVX, nop or endbr64 support, -f elf is ignored (always Mach-O), the output file is opened without truncate (stale trailing bytes), hex immediates become relocations against a symbol named '0x10', and .cfi_\*, .p2align, .build_version, .subsections_via_symbols and data directives (.byte/.long/.quad/.zero) are silently dropped. Reference only.

Incomplete x86-64 assembler: only ELF64 and Mach-O output, a subset of the instruction set, Rust crate used as a command-line tool, not a library.

## Maintenance

Abandoned since 2022-10-11 (21 commits, 2 stars, no releases, not on crates.io). The MPL-2.0 source is small enough to read, but the encoder bugs (r9 panic, swapped REX.R/REX.B, no SIB) make it unusable beyond toy -O0 files, so treat it as reference material rather than copyable code.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification C, tier now D.
- **Tier reason:** The only number is a README screenshot (imgs/aron-bm.png) of hyperfine -N --warmup 10 assembling test.macos.s, a 31-line clang -S output of a hello-world printf program: aron 3.9 ms vs macOS as 49.8 ms, 12.94 +/- 2.34x. With \~15 instructions of input both timings are process launch (macOS as is a driver that hands off to clang's integrated assembler), so the figure says nothing about assembly speed; the author calls it 'not empirical by any means', no CPU is named, and no output equivalence is checked. Downgraded to D following the wave 11 hop precedent (startup-dominated benchmark); it would be C on the bare rubric.
- **Verifier notes:** Numbers on the README image match the record. Shortcomings: startup-dominated hello-world benchmark (31-line file), author disclaims it as not empirical, CPU unstated, no output check, incomplete assembler, 2 stars, abandoned since 2022-10-11. Downgraded C to D on the hop precedent; keep C instead if the orchestrator prefers the bare rubric.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `caveats`, `usability`
- **Shortcomings recorded by:** verifier batch-02 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/not-nik/aron/HEAD/README.md>
  - <https://raw.githubusercontent.com/not-nik/aron/HEAD/imgs/aron-bm.png>
  - <https://raw.githubusercontent.com/not-nik/aron/HEAD/test.macos.s>
  - <https://raw.githubusercontent.com/not-nik/aron/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/not-nik/aron/HEAD/Cargo.toml>
  - <https://github.com/not-nik/aron>
  - <https://github.com/not-nik/aron/commits>
- **Sources the enricher read:**
  - <https://github.com/Not-Nik/aron>
  - <https://github.com/Not-Nik/aron/commits/master>
  - <https://github.com/Not-Nik/aron/tree/master/src>
  - <https://github.com/Not-Nik/aron/tree/master/src/assembler>
  - <https://github.com/Not-Nik/aron/tree/master/src/parse>
  - <https://raw.githubusercontent.com/not-nik/aron/HEAD/README.md>
  - <https://raw.githubusercontent.com/not-nik/aron/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/not-nik/aron/HEAD/test.macos.s>
  - <https://raw.githubusercontent.com/not-nik/aron/HEAD/test.c>
  - <https://raw.githubusercontent.com/not-nik/aron/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/not-nik/aron/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/not-nik/aron/HEAD/src/main.rs>
  - <https://raw.githubusercontent.com/not-nik/aron/HEAD/src/cli.rs>
  - <https://raw.githubusercontent.com/not-nik/aron/HEAD/src/instructions.rs>
  - <https://raw.githubusercontent.com/not-nik/aron/HEAD/src/number.rs>
  - <https://raw.githubusercontent.com/not-nik/aron/HEAD/src/assembler/mod.rs>
  - <https://raw.githubusercontent.com/not-nik/aron/HEAD/src/assembler/label.rs>
  - <https://raw.githubusercontent.com/not-nik/aron/HEAD/src/assembler/section.rs>
  - <https://raw.githubusercontent.com/not-nik/aron/HEAD/src/parse/mod.rs>
  - <https://raw.githubusercontent.com/not-nik/aron/HEAD/src/parse/parser.rs>
  - <https://raw.githubusercontent.com/not-nik/aron/HEAD/src/parse/lexer.rs>
  - <https://raw.githubusercontent.com/not-nik/aron/HEAD/src/parse/helpers.rs>
  - <https://raw.githubusercontent.com/not-nik/aron/HEAD/src/parse/encodings.rs>
  - <https://raw.githubusercontent.com/not-nik/aron/HEAD/src/parse/tests.rs>
  - <https://raw.githubusercontent.com/not-nik/aron/HEAD/src/parse/generate_instructions.py>
  - <https://crates.io/api/v1/crates/aron>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/not-nik/aron`) · [data/wave13/enrich/raw/github_com_not_nik_aron.json](../../../data/wave13/enrich/raw/github_com_not_nik_aron.json) (enrichment confidence 0.85)

</details>
