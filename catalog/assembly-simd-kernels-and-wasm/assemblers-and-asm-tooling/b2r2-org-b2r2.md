# B2R2 (binary analysis framework, disassembler front-end)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assemblers and assembly tooling](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `F#` · `MIT` · 🟢 active

> Fully managed F# binary analysis framework whose x86/x86-64 front-end out-ran Capstone.NET about 4.4x in its authors' print-every-instruction harness.

| | |
|---|---|
| **Beats** | Capstone (Capstone.NET and Capstone Python bindings), plus SharpDisasm; compared with iced (C#), which is faster |
| **Claimed result** | B2R2 28.298 s on blob_x86, 24.317 s on blob_x86_64, 0.63 s on libc_x86 (average 17.748 s) vs Capstone.NET 127.847 / 106.414 / 2.245 s (average 78.835 s) and Capstone Python 132.693 / 111.604 / 2.22 s (average 82.172 s): about 4.4x faster than Capstone.NET on average (derived from page data). |
| **Workload** | Seconds (in-process Stopwatch) to linearly disassemble three raw x86/x86-64 blobs from the BAR19-Artifact repo (blob_x86, blob_x86_64, libc_x86) and print every instruction to stdout with Console.WriteLine/print inside the timed loop; each number is the mean of 10 runs, lower is better. |
| **Metric** | throughput |
| **Compiler and flags** | dotnet run -c release for each .NET project, TargetFramework net5.0 (from b2r2_test.fsproj and Capstone.NET_test.csproj; SDK version not stated); B2R2.FrontEnd.BinInterface 0.5.0 from NuGet; Capstone.NET is Gee.External.Capstone 2.0.2 with the CapstoneCoreLin4/CapstoneCoreWin4 1.0.0 native packages (Capstone 4.x era); Capstone Python run as 'python capstone_test_python.py' (capstone package version not stated) |
| **Adoption** | 552 stars |
| **Last commit** | 2026-10-11 |
| **Links** | [repository](https://github.com/B2R2-org/B2R2) · [benchmark](https://github.com/B2R2-org/DisasmComparison) |

## Verdict

In the B2R2 authors' DisasmComparison repo (B2R2 0.5.0 on net5.0; CPU, OS and .NET SDK not stated; mean of 10 runs), linear-sweep disassembly of three BAR'19 blobs, with each instruction printed inside the timer, took 28.3/24.3/0.63 s against 127.8/106.4/2.25 s for Capstone.NET (Gee.External.Capstone 2.0.2 over Capstone 4.x) and 132.7/111.6/2.22 s for the Capstone Python bindings. That is about 4.4x on average against Capstone.NET, while C# iced was faster still (15.7 s average). The times are dominated by console output and the tools do unequal work, so this is not a native Capstone comparison.

## Use it when

- You are already on .NET (F# or C#) and want x86/x86-64 decoding plus lifting to an IR and CFG recovery in one fully managed package, with no native Capstone binaries to ship.
- You need one decoder API across many ISAs (x86, ARM, MIPS, RISC-V, PPC, SPARC, EVM, WASM and others) inside a .NET analysis tool.
- You are replacing Capstone.NET or the Capstone Python bindings in a .NET or scripted pipeline where per-instruction marshalling through a wrapper is the bottleneck.
- You want to parallelise lifting or CFG recovery: the API supports it by creating one LiftingUnit per thread.

## Skip it when

- From C or C++: it is an F#/.NET assembly with no C API, so it needs a hosted CLR or a separate process; native Zydis, bddisasm, XED or iced (Rust) are the direct options.
- When raw x86 decode speed is all you need: in the same harness the C# build of iced was faster (15.737 s vs 17.748 s average), and iced also ships an encoder and a Rust crate.
- Linear sweeps over data-heavy or misaligned bytes: every undecodable position goes through a .NET exception (raised in the parser, re-raised by LiftingUnit, caught by TryParseInstruction), which is far slower than a normal decode.
- When you need a stable API: 0.x releases rename packages and types (B2R2.FrontEnd.BinInterface and BinHandle.TryParseInstr used by the 2021 benchmark are gone; the current package is B2R2.FrontEnd.API on net10.0).
- When you need Capstone's exact output: disassembly syntax and operand formatting differ, and decoding bugs are still being fixed (issues #279 SHA family, #634 ARMv7).

## How it is fast

The x86 parser checks prefixes with a bitmap per high-3-bit group, then dispatches into straight-line per-opcode code that the IntelParserGen generator writes at build time from the instruction table (LegacyOpcodeMap/VEXOpcodeMap), so nothing is looked up at parse time. Since PR #590 (September 2026) operands are value types stored inside the instruction object, cutting per-instruction allocations from three to one; the PR reports this as about 1.4x faster than the previous table-driven parser on the same blobs (relative numbers only). The parser works on ReadOnlySpan&lt;byte&gt; slices of the image, with no native code or P/Invoke.

## Compared with alternatives

Pick B2R2 over iced, Zydis, bddisasm or XED only when you want decoding, lifting to an IR and CFG recovery for many ISAs in one managed .NET package. For pure x86 decode/format speed, iced (C# or Rust) beat it in the authors' own table, and Zydis or bddisasm are the native C choices with independent disas-bench numbers.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | the .NET 10 runtime and FSharp.Core; the core library has no other external dependencies (FParsec, FSharp.Compiler.Service, BenchmarkDotNet and Avalonia.FuncUI are used only by optional tools) |
| **Minimum toolchain** | .NET 10 SDK (net10.0 target, FSharp.Core 10.0.103 pinned) for the current 0.10.1 release; the 2021 benchmark used B2R2 0.5.0 on net5.0 |
| **Platforms** | any OS .NET supports (Linux, macOS, Windows); decodes x86, x86-64, ARMv7, AArch64, MIPS32/64, RISC-V 32/64, PPC32/64, SPARC, S390/S390x, SH4, M68K, Alpha, PA-RISC, AVR, TMS320C6000, EVM, eBPF, WASM, CIL and Python bytecode |
| **Thread safety** | A LiftingUnit is per-thread: the docs say lifting in parallel needs multiple lifting units; a global mutable variable in the Intel front-end was removed in issue #87 (2025). |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw: every tool's timed loop prints each instruction with Console.WriteLine (autoflushed .NET console, or print in Python), so the table measures output more than decoding. B2R2 ran blob_x86 (78,369,750 bytes) at about 2.8 MB/s, iced at 3.1 MB/s and Capstone.NET at 0.61 MB/s (derived from page data). That is roughly 10x below the native decode+format rates in disas-bench (Capstone 27.5 MB/s, different hardware), and iced, B2R2 and SharpDisasm sit within 16% of each other, which fits a shared output floor. The 4.4x figure is not a decoder-speed ratio.
- Unequal work in the harness: Capstone runs with skipdata, so undecodable bytes are formatted and printed as .byte lines, while the B2R2 harness silently advances one byte; the Python harness prints address and operands but no mnemonic. Capstone.NET's timed region also includes creating the disassembler, while B2R2's file load is outside its timer. Capstone.NET's wrapper (current 9ee1/Capstone.NET source; 2.0.2 not checked) pins the whole input array with GCHandle.Alloc on every Iterate step and builds a managed instruction object with marshalled strings, so the baseline is a binding, not native Capstone 4.x.
- Stale numbers: they are for B2R2 0.5.0 (comparison repo last updated 2021-10-23). The Intel parser has since been rewritten twice: first table-driven, then generated per-opcode code (PR #590). The harness no longer builds against current B2R2, because the BinInterface package and the TryParseInstr API are gone.
- Undecodable bytes cost exceptions: Parser.Parse wraps all errors into ParsingFailureException, LiftingUnit.parse re-raises it, and TryParseInstruction catches it, so a Result-returning call still throws internally on every bad byte.

## Known shortcomings

- DisasmComparison harness prints every instruction to the console inside the timed loop, so output dominates; work is unequal (Capstone runs with skipdata, B2R2 skips bad bytes without printing); Capstone 4.x measured through the Gee.External.Capstone 2.0.2 bindings, not native; no CPU, OS or SDK version; slower than Iced; F#, not callable from C++; the comparison repo has no licence; the BAR'19 paper compares lifters, not Capstone.
- asmtool blogs search found the same DisasmComparison claim again (4.4x vs Capstone.NET, first-party, no hardware); folded into the batch-43 record.
- Enricher: every tool prints each instruction with an autoflushed Console.WriteLine inside the timer (blob_x86 at 78,369,750 bytes: B2R2 2.8 MB/s, iced 3.1, Capstone.NET 0.61, derived, about 10x below native disas-bench rates), and iced, B2R2 and SharpDisasm sit within 16% of each other on a shared output floor, so the 4.4x is not decoder speed; Capstone skipdata vs B2R2's silent byte skip; the Capstone.NET timer includes disassembler creation and the wrapper pins the whole buffer per instruction; numbers are from B2R2 0.5.0, the parser was rewritten (PR #590, September 2026) and the harness no longer builds against 0.10.1.

## Caveats and trade-offs

Comparison repo is run by the B2R2 authors; no CPU, OS or .NET SDK version is given, and the repo has no license. Every harness prints each instruction to the console inside the timed region, so the times (25-130 s per blob) are dominated by string formatting and console output, and the output destination is not stated. Work is not equal: the Capstone harnesses enable skipdata (undecodable bytes are emitted as .byte pseudo-instructions and printed), while the B2R2 harness silently advances one byte on a parse error without printing; the Python harness prints only address and operands, not the mnemonic. The baseline is Capstone 4.x through managed (Gee.External.Capstone 2.0.2) or Python bindings, so per-instruction marshalling overhead is included and the ratio overstates the gap to native Capstone; current Capstone 5/6 is not measured. Numbers are for B2R2 v0.5.0 (comparison repo last updated 2021-10-23); the framework has changed a lot since. B2R2 is slower than Iced (15.737 s average) and only slightly faster than SharpDisasm (18.321 s) in the same table. B2R2 is an F#/.NET library, not callable from C++ without hosting the CLR. The README's run command names b2r2_test.csproj but the project file is b2r2_test.fsproj. The peer-reviewed BAR'19 paper (artifact repo B2R2-org/BAR19-Artifact) compares lifting front-ends (BAP, BINSEC, Miasm, PyVEX, radare2 docker images), not Capstone, and its PDF was unreachable here.

Fully managed F# binary analysis framework (also lifts to IR and recovers CFGs, not measured here); needs .NET, no C or C++ API, so use from C++ requires interop or a separate process.

## Maintenance

Very active (0.10.1 released 2026-06-17, commits through 2026-10-11, parser speed work in September 2026) and MIT-licensed, but a 0.x .NET library with frequent API renames, not callable from C++ without hosting the CLR; the only benchmark is a five-year-old first-party run.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party comparison repo B2R2-org/DisasmComparison has public harness code (b2r2_test/b2r2_test/Program.fs, Capstone.NET_test/Capstone.NET_test/Program.cs, capstone_test_python/capstone_test_python/capstone_test_python.py) and run commands, and its README table matches the record exactly, but no CPU, OS or SDK version is stated and it was run by the B2R2 authors, so it stays C.
- **Verifier notes:** Numbers and ratios (4.44x vs Capstone.NET, 4.63x vs Capstone Python, derived from page data) are correct. Harness flaws to record as shortcomings: console printing inside the timed loop dominates, Capstone runs with skipdata while B2R2 skips bad bytes silently, Capstone 4.x through bindings rather than native, no hardware or SDK version, slower than Iced. Last commit 2026-10-11, 552 stars, MIT confirmed.
- **Fields the verifier corrected:** `compiler_and_flags`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-43 (wave 13); asmtool blogs search (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/B2R2-org/DisasmComparison/HEAD/README.md>
  - <https://github.com/B2R2-org/DisasmComparison>
  - <https://github.com/B2R2-org/DisasmComparison/commits>
  - <https://github.com/B2R2-org/DisasmComparison/tree/master/b2r2_test/b2r2_test>
  - <https://raw.githubusercontent.com/B2R2-org/DisasmComparison/HEAD/b2r2_test/b2r2_test/Program.fs>
  - <https://raw.githubusercontent.com/B2R2-org/DisasmComparison/HEAD/b2r2_test/b2r2_test/b2r2_test.fsproj>
  - <https://raw.githubusercontent.com/B2R2-org/DisasmComparison/HEAD/Capstone.NET_test/Capstone.NET_test/Program.cs>
  - <https://raw.githubusercontent.com/B2R2-org/DisasmComparison/HEAD/Capstone.NET_test/Capstone.NET_test/Capstone.NET_test.csproj>
  - <https://github.com/B2R2-org/DisasmComparison/tree/master/capstone_test_python>
  - <https://github.com/B2R2-org/DisasmComparison/tree/master/capstone_test_python/capstone_test_python>
  - <https://raw.githubusercontent.com/B2R2-org/DisasmComparison/HEAD/capstone_test_python/capstone_test_python/capstone_test_python.py>
  - <https://raw.githubusercontent.com/B2R2-org/DisasmComparison/HEAD/iced_test/iced_test/Program.cs>
  - <https://github.com/B2R2-org/B2R2>
  - <https://github.com/B2R2-org/B2R2/commits>
  - <https://github.com/B2R2-org/BAR19-Artifact>
  - <https://github.com/B2R2-org/BAR19-Artifact/tree/master/dockers>
- **Sources the enricher read:**
  - <https://github.com/B2R2-org/B2R2>
  - <https://raw.githubusercontent.com/B2R2-org/B2R2/HEAD/README.md>
  - <https://raw.githubusercontent.com/B2R2-org/B2R2/HEAD/Directory.Build.props>
  - <https://raw.githubusercontent.com/B2R2-org/B2R2/HEAD/CHANGELOG.md>
  - <https://github.com/B2R2-org/B2R2/tree/main/src>
  - <https://github.com/B2R2-org/B2R2/tree/main/src/FrontEnd>
  - <https://github.com/B2R2-org/B2R2/tree/main/src/RearEnd>
  - <https://github.com/B2R2-org/B2R2/tree/main/src/FrontEnd/Intel>
  - <https://raw.githubusercontent.com/B2R2-org/B2R2/HEAD/src/FrontEnd/Intel/README.md>
  - <https://raw.githubusercontent.com/B2R2-org/B2R2/HEAD/src/FrontEnd/Intel/Parser.fs>
  - <https://raw.githubusercontent.com/B2R2-org/B2R2/HEAD/src/FrontEnd/Intel/InstructionTable.fs>
  - <https://raw.githubusercontent.com/B2R2-org/B2R2/HEAD/src/FrontEnd/Intel/B2R2.FrontEnd.Intel.fsproj>
  - <https://raw.githubusercontent.com/B2R2-org/B2R2/HEAD/src/FrontEnd/API/LiftingUnit.fs>
  - <https://raw.githubusercontent.com/B2R2-org/B2R2/HEAD/src/FrontEnd/API/BinHandle.fs>
  - <https://raw.githubusercontent.com/B2R2-org/B2R2/HEAD/src/FrontEnd/API/B2R2.FrontEnd.API.fsproj>
  - <https://github.com/B2R2-org/B2R2/issues?q=is%3Aissue+performance+OR+slow+OR+disassembly>
  - <https://github.com/B2R2-org/B2R2/issues/543>
  - <https://github.com/B2R2-org/B2R2/issues/581>
  - <https://github.com/B2R2-org/B2R2/pull/590>
  - <https://raw.githubusercontent.com/B2R2-org/DisasmComparison/HEAD/README.md>
  - <https://raw.githubusercontent.com/B2R2-org/DisasmComparison/HEAD/b2r2_test/b2r2_test/Program.fs>
  - <https://raw.githubusercontent.com/B2R2-org/DisasmComparison/HEAD/b2r2_test/b2r2_test/b2r2_test.fsproj>
  - <https://raw.githubusercontent.com/B2R2-org/DisasmComparison/HEAD/Capstone.NET_test/Capstone.NET_test/Program.cs>
  - <https://raw.githubusercontent.com/B2R2-org/DisasmComparison/HEAD/Capstone.NET_test/Capstone.NET_test/Capstone.NET_test.csproj>
  - <https://raw.githubusercontent.com/B2R2-org/DisasmComparison/HEAD/capstone_test_python/capstone_test_python/capstone_test_python.py>
  - <https://raw.githubusercontent.com/B2R2-org/DisasmComparison/HEAD/iced_test/iced_test/Program.cs>
  - <https://raw.githubusercontent.com/B2R2-org/BAR19-Artifact/HEAD/README.md>
  - <https://github.com/B2R2-org/BAR19-Artifact/tree/master/blobs>
  - https://raw.githubusercontent.com/B2R2-org/BAR19-Artifact/master/blobs/blob_x86 (HEAD request for size only)
  - https://raw.githubusercontent.com/B2R2-org/BAR19-Artifact/master/blobs/blob_x86_64 (HEAD request for size only)
  - https://raw.githubusercontent.com/B2R2-org/BAR19-Artifact/master/blobs/libc_x86 (HEAD request for size only)
  - <https://raw.githubusercontent.com/9ee1/Capstone.NET/HEAD/Gee.External.Capstone/CapstoneDisassembler.cs>
  - <https://raw.githubusercontent.com/9ee1/Capstone.NET/HEAD/Gee.External.Capstone/NativeCapstone.cs>
  - <https://github.com/icedland/disas-bench>
  - https://softsec.kaist.ac.kr/\~sangkilc/papers/jung-bar19.pdf (unreachable: ENOTFOUND)
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/b2r2-org/b2r2`) · [data/wave13/enrich/raw/github_com_b2r2_org_b2r2.json](../../../data/wave13/enrich/raw/github_com_b2r2_org_b2r2.json) (enrichment confidence 0.65)

</details>
