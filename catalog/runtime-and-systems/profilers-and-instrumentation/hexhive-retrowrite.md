# RetroWrite

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Profilers and instrumentation](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Python` · `MIT` · 🟡 stale

> Static rewriter adding ASan and AFL coverage to Linux x86-64/aarch64 binaries without source; claims 3x faster than Valgrind memcheck.

| | |
|---|---|
| **Beats** | Valgrind Memcheck |
| **Claimed result** | IEEE S&P 2020 abstract (via search snippets): binary-only ASan 3x faster than Valgrind memcheck on SPEC CPU2006 C benchmarks while detecting 80% more bugs; AFL coverage instrumentation as fast as compiler instrumentation and 4.5x faster than QEMU-mode AFL; fuzzing throughput 4.2x (real-world) and 5.6x (LAVA-M) over QEMU AFL. |
| **Workload** | Binary-only AddressSanitizer (BASan) and AFL coverage instrumentation inserted by static rewriting of x86_64 and aarch64 Linux binaries, versus Valgrind memcheck, source-level ASan and QEMU-mode AFL on SPEC CPU2006 C benchmarks and fuzzing targets. |
| **Metric** | throughput |
| **Adoption** | 751 stars; IEEE S&P 2020 |
| **Last commit** | 2025-04-26 |
| **Links** | [repository](https://github.com/HexHive/retrowrite) |

## Verdict

Only the IEEE S&P 2020 abstract was readable (via search snippets): BASan about 3x faster than Valgrind memcheck and about 0.65x slower than source ASan on the SPEC CPU2006 C benchmarks, detecting 80% more bugs, and AFL coverage 4.5x faster than QEMU mode (a Purdue thesis snippet says 7.5x). CPU, compiler, flags and per-benchmark numbers are in the paper, which was unreachable (nebelwelt.net and cs.purdue.edu DNS-blocked), and the repo has no benchmark data.

## Use it when

- Fuzzing a closed-source Linux x86-64 PIE binary with AFL/AFL++ when QEMU mode is too slow; the paper abstract claims 4.5x over QEMU-mode AFL and parity with compiler instrumentation.
- Memory-error checking of a binary-only C program where Valgrind memcheck's slowdown makes test or fuzz runs impractical (abstract: about 3x faster than memcheck on SPEC CPU2006 C benchmarks).
- Stripped or non-PIE aarch64 Linux binaries, which the aarch64 rewriter supports (the x64 one does not).
- Fuzzing Linux kernel modules without source via KRetrowrite with kcov or BASan.
- Research or tooling that needs editable, reassemblable assembly of a binary to write a custom instrumentation pass in Python.

## Skip it when

- C++ binaries: the README marks C++ support as work in progress on both architectures, and issue #26 (g++ hello world cannot be rebuilt) is open.
- Stripped or non-PIE x86-64 binaries: the x64 rewriter needs symbols and position-independent code (merging stripped-binary function detection is still open as issue #40).
- When you have source: compiler AddressSanitizer is faster (the abstract snippet puts BASan about 0.65x slower than source ASan) and checks wider accesses.
- When you need memcheck's uninitialized-value tracking or leak-checking semantics; BASan is an ASan-style redzone checker, so the 3x comparison is between tools that check different things.
- Production or safety-critical rewriting: reassembly can silently mis-symbolize (open issues #45 RIP-relative addressing, #38 omitted data sections, #35 functions not disassembled, #49 segfaults in BASan-rewritten SPEC2006 gcc and bzip2), and the USENIX Security 2023 'Reassembly Is Hard' study (slides, search snippet only) counts RetroWrite output as compilable for 95.2% of 25,704 binaries and still reports symbolization errors; compiling is not the same as running correctly.

## How it is fast

Instrumentation is inserted statically, so the rewritten program runs as native code with no dynamic binary translation; Valgrind memcheck instead JIT-translates every basic block at run time. On x64, relocation information in position-independent binaries tells pointers apart from constants, which lets it symbolize code and data references (including switch tables) without heuristics. The BASan pass emits the same inline shadow-memory check as compiler ASan (address &gt;&gt; 3, shadow offset 0x7fff8000) before each 1/2/4/8-byte access and uses a register-liveness analysis to borrow free registers and skip saving RFLAGS where possible, so checks avoid most spills. AFL coverage on x64 reuses afl-gcc's assembler instrumentation on the symbolized output, which is why it matches compiler-instrumented speed.

## Compared with alternatives

Pick RetroWrite over Dr. Memory or Valgrind when the target is a supported Linux PIE C binary and you can afford a rewrite step, since the result runs natively with compiler-ASan-style checks; pick E9Patch when the binary is stripped, non-PIE or C++ (it patches in place with trampolines instead of reassembling), and compiler AddressSanitizer whenever you have source.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | Python 3 (README says 3.6) with pyelftools, capstone &gt;= 4.0.2, intervaltree and archinfo pinned to 9.1.11752; a GCC or Clang toolchain to reassemble, libasan for BASan, afl-gcc/afl-clang (AFL++) for x64 coverage |
| **Minimum toolchain** | Python 3.6; capstone 4.0.2+ (README warns distro capstone packages may be too old) |
| **Platforms** | Linux ELF on x86-64 (PIE, non-stripped, non-C++ only) and aarch64 (stripped and non-PIE supported, different algorithm); no Windows or macOS |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial — replaces running the binary under Valgrind memcheck (or AFL QEMU mode) with a rewrite-then-run step on supported binaries, but it reports ASan-style errors, not memcheck's, and works only on binaries the rewriter accepts |

## Gotchas

- The x64 BASan pass skips memory operands that are not 1, 2, 4 or 8 bytes (it prints 'Maybe missed an access'), so 16-byte SSE/AVX accesses go unchecked, and rep stos is marked TODO.
- Stack redzones are added only to functions that load a stack canary in their first 20 instructions, so binaries built without -fstack-protector get no stack-overflow detection.
- Depending on the libasan version the output may fail to link with 'undefined reference to __asan_init_v4'; the README's fix is a sed rename to __asan_init.
- Register analysis is slow on large binaries; the -c flag caches it next to the output, and a stale cache prints 'Missing free reglist in cache. Regenerate!' and falls back to saving registers.

## Known shortcomings

- README table says x64 lacks stripped and non-PIE support and C++ support is WIP on both arches (issue 26: a g++ hello world fails to rebuild). Open issue 49 (2023-08-22, no reply): ASan-rewritten SPEC2006 binaries (bzip2, gcc; GCC 5.5 -O2 PIE) segfault, so the paper's SPEC numbers are hard to reproduce. The 3x over Memcheck and 65% slower than compiler ASan figures are snippet only (nebelwelt.net and hexhive.epfl.ch blocked). Taken from an enricher's report; its enrich file was never written.
- Enricher: the 3x BASan figure is against Valgrind memcheck, which checks different things; x64 BASan skips 16-byte SSE/AVX accesses and adds stack redzones only to canary functions; open issue #49 (BASan-rewritten SPEC2006 gcc and bzip2 segfault); x64 needs non-stripped PIE binaries; C++ support unfinished (#26); stale since 2025-04-26, 29 open issues; paper still unreachable.

## Caveats and trade-offs

Numbers are from abstract snippets only; the paper (nebelwelt.net/files/20Oakland.pdf, hexhive.epfl.ch) is blocked by egress and the README makes only a qualitative zero-overhead claim, so CPU, compiler and per-benchmark numbers were not checked. Retier candidate to B once the paper is reachable. The tool is written in Python, but its output is instrumented x86_64/aarch64 binaries. x64 rewriting needs PIC/PIE binaries; aarch64 uses a different algorithm (thesis). Last commit 2025-04-26. [retier] Enricher: the 3x is against Valgrind memcheck, which checks different things (it also tracks uninitialised values), so it is not a like-for-like sanitizer comparison; the abstract snippet puts BASan about 0.65x slower than source-level ASan on SPEC2006 C, and a Purdue thesis snippet gives 7.5x for AFL over QEMU where the abstract says 4.5x. The x64 BASan pass skips memory operands that are not 1, 2, 4 or 8 bytes, so 16-byte SSE/AVX accesses go unchecked, and it adds stack redzones only to functions that load a stack canary. Open issue #49: BASan-rewritten SPEC2006 gcc and bzip2 segfault on x64, with no maintainer reply. 29 open issues, last commit 2025-04-26.

Works only on position-independent (PIE) x86_64 and aarch64 Linux binaries with symbolization limits; the tool itself is Python but its output is ordinary assembler, so result binaries are usable from C++ workflows.

## Maintenance

Stale research code: last commit 2025-04-26 (jumparound pass), 29 open issues mostly unanswered since 2022, no releases; MIT-licensed, 754 stars.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification B, tier now C.
- **Tier reason:** The 3x-faster-than-Valgrind-memcheck (80% more bugs, SPEC CPU2006 C benchmarks) and 4.5x-over-QEMU claims come from the IEEE S&P 2020 abstract and appear the same way in several WebSearch snippets, but the paper and thesis PDFs (nebelwelt.net, hexhive.epfl.ch) are blocked and no copy exists on GitHub. The repo has no numbers, so this is capped at C on snippet-only evidence until the paper is read.
- **Verifier notes:** The paper is a retier candidate (C to B) once nebelwelt.net or hexhive.epfl.ch is reachable. Metadata matches the record: MIT, 751 stars, last commit 2025-04-26 (stale).
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`, `workload`
- **Shortcomings recorded by:** snippet only; enrichment (wave 11 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://github.com/HexHive/retrowrite>
  - <https://github.com/HexHive/retrowrite/commits>
  - <https://raw.githubusercontent.com/HexHive/retrowrite/HEAD/README.md>
  - <https://raw.githubusercontent.com/HexHive/RetroWrite-Tutorial/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/HexHive/retrowrite>
  - <https://raw.githubusercontent.com/HexHive/retrowrite/HEAD/README.md>
  - <https://raw.githubusercontent.com/HexHive/retrowrite/HEAD/requirements.txt>
  - <https://raw.githubusercontent.com/HexHive/retrowrite/HEAD/setup.py>
  - <https://raw.githubusercontent.com/HexHive/retrowrite/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/HexHive/retrowrite/HEAD/retrowrite>
  - <https://github.com/HexHive/retrowrite/tree/master/rwtools_x64/asan>
  - <https://github.com/HexHive/retrowrite/tree/master/librw_x64>
  - <https://raw.githubusercontent.com/HexHive/retrowrite/HEAD/rwtools_x64/asan/instrument.py>
  - <https://raw.githubusercontent.com/HexHive/retrowrite/HEAD/rwtools_x64/asan/snippets.py>
  - <https://raw.githubusercontent.com/HexHive/retrowrite/HEAD/librw_x64/rw.py>
  - <https://github.com/HexHive/retrowrite/issues?q=is%3Aissue>
  - <https://github.com/HexHive/retrowrite/issues/49>
  - <https://github.com/HexHive/retrowrite/issues/34>
  - <https://github.com/HexHive/retrowrite/commits/master>
  - https://nebelwelt.net/publications/files/20Oakland.pdf (blocked: DNS not resolved)
  - https://www.cs.purdue.edu/homes/dxu/pubs/SP20.pdf (blocked: DNS not resolved)
  - WebSearch snippets: RetroWrite S&P 2020 abstract; USENIX Security 2023 'Reassembly Is Hard' slides
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/hexhive/retrowrite`) · [data/wave11/enrich/raw/github_com_hexhive_retrowrite.json](../../../data/wave11/enrich/raw/github_com_hexhive_retrowrite.json) (enrichment confidence 0.6)

</details>
