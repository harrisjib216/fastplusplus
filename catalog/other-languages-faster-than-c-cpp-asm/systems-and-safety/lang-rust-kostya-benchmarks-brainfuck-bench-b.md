# Rust (kostya/benchmarks brainfuck bench.b)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust tree-walking brainfuck interpreter in kostya/benchmarks: 9-16% faster than the C and C++ ports on bench.b, slower on mandel.b.

| | |
|---|---|
| **Beats** | C and C++ brainfuck interpreters of the same suite, gcc and clang, -O3 -march=native -flto |
| **Claimed result** | bench.b: Rust 1.008 s vs C++/g++ 1.097 s (about 1.09x), C/gcc 1.112 s (about 1.10x), C/clang 1.136 s (about 1.13x), C++/clang++ 1.167 s (about 1.16x), ratios derived from page data. D/ldc2 1.078 s and V/gcc 0.985 s are also ahead of every C and C++ row. On mandel.b the order reverses: Rust 14.460 s vs C++/g++ 10.143 s, C/gcc 12.544 s, C++/clang++ 12.803 s, C/clang 13.120 s. |
| **Workload** | Run the bench.b brainfuck program through a straightforward interpreter in each language; seconds. |
| **Metric** | latency |
| **Hardware** | Intel Xeon E-2324G, Debian forky/sid Docker image |
| **Compiler and flags** | Measured toolchains (2025-08-17 run, rows unchanged since): Rust 1.89.0 with RUSTFLAGS='-C target-cpu=native -C llvm-args=--x86-branches-within-32B-boundaries' cargo build --release; gcc/g++ 14.2.0 and clang/clang++ 19.1.7 with -O3 -march=native -flto=auto -Wa,-mbranches-within-32B-boundaries (common/commands.mk). The README's Rust 1.97.1, gcc 16.1.0 and clang 22.1.8 apply only to the re-measured .NET rows (enricher correction). |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | yes |
| **Adoption** | 2.9k stars (suite repo) |
| **Last commit** | 2026-07-19 |
| **Links** | [repository](https://github.com/kostya/benchmarks) · [benchmark](https://raw.githubusercontent.com/kostya/benchmarks/master/README.md) |

## Verdict

On an Intel Xeon E-2324G in Docker, median of 10 QUIET runs: Rust 1.008 s versus C++/g++ 1.097 s, C/gcc 1.112 s, C/clang 1.136 s and C++/clang++ (libc++) 1.167 s on bench.b, about 1.09-1.16x (derived from page data). All were built at -O3 -march=native -flto=auto (Rust: target-cpu=native, fat LTO, codegen-units 1, panic=abort), and the rows come from the 2025-08-17 run (Rust 1.89.0, gcc 14.2.0, clang 19.1.7). On mandel.b the same binaries reverse: Rust 14.460 s versus C++/g++ 10.143 s and C/gcc 12.544 s.

## Use it when

- As a compact reference for an enum-and-match tree-walking interpreter in Rust that lands within about 15% of equivalent C and C++ ports on current LLVM
- As a baseline when measuring your own interpreter's dispatch and loop-call overhead on bench.b (about 9.5e8 interpreted operations in about 1 s on a Xeon E-2324G)
- Programs dominated by tiny loop bodies such as [-], the shape where it leads

## Skip it when

- As evidence that Rust beats C or C++: with the same bf.c, bf.cpp and logically identical bf.rs, C++/g++ was 1.25x faster in the 2023 run, and on mandel.b C++/g++ is 1.43x faster today
- Running real brainfuck fast: it deliberately skips instruction folding, and the suite's staged rows are far faster (C# Staged 0.373 s on bench.b, 2.917 s on mandel.b)
- Untrusted programs: a '&lt;' at cell 0 wraps pos in a release build and the next get_unchecked reads out of bounds (undefined behaviour), despite the SAFETY comment that pos is checked in next()
- Code that needs standard brainfuck semantics: cells are unbounded i32 and loops run while the cell is greater than 0, not non-zero (the C and C++ ports do the same)

## How it is fast

The suite states no mechanism. The Rust port differs from bf.c and bf.cpp in layout only: an enum with dataless Inc/Dec/Prev/Next variants (no operand load, where C and C++ load a +1/-1 offset), loop bodies stored inline as Box&lt;[Op]&gt; (C goes through an op_list pointer), tape access through get_unchecked (as unchecked as C's raw array and C++'s vector operator[]), and a recursive run() over &mut references. The same interpreter logic lost to C++/g++ by 1.25x in the 2023 run, so the lead tracks compiler versions rather than these choices.

## Compared with alternatives

Against the V/gcc bench.b sibling (0.985 s, a C-emitting backend built with -no-bounds-checking) it is the same-speed choice with bounds discipline left to two unsafe calls, and unlike V it keeps its rank on mandel.b better (14.46 s versus V/gcc 17.87 s). The Rust serde json and Zig base64 siblings in the same suite are library-backed results, while this one is a pure interpreter-codegen comparison with the weakest claim of the three.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none outside the suite (path dependency on common/rust utils for the notify! macro, removable) |
| **Minimum toolchain** | Rust 1.85+ (edition 2024 in Cargo.toml); the published rows were built with Rust 1.89.0 |
| **Platforms** | any Rust target; measured on x86-64 with -C target-cpu=native |
| **Thread safety** | single-threaded program; not documented beyond that |
| **Drop-in for the baseline** | no |

## Gotchas

- The published rows are older than the toolchains the README lists. In the 2026-07-19 README the bench.b and mandel.b tables match the 2025-08-17 README digit for digit, including MAD and energy, except the .NET rows (C#, C# Staged, F#). So the Rust, C and C++ times were measured with Rust 1.89.0, gcc/g++ 14.2.0 and clang 19.1.7 on Debian trixie/sid, not with Rust 1.97.1, gcc 16.1.0 and clang 22.1.8. bf.c, bf.cpp, bf.rs, Cargo.toml and the C/C++/Rust flags in common/commands.mk are unchanged since that run.
- The ranking flips with toolchain on the same code: the 2023-10-16 README (Rust 1.73.0, gcc 13.2.0, clang 16.0.6, same Xeon E-2324G, same bf.c and bf.cpp, a bf.rs differing only in variable names and edition) has C++/g++ 1.323 s, Rust 1.658 s, C/gcc 1.667 s and C/clang 1.674 s on bench.b. V on the same source swings from 0.985 s (gcc backend) to 1.846 s (clang backend).
- bench.b is call-bound, not dispatch-bound. Counted from bench.b in this session: about 5.78e8 Inc/Dec, 5.78e7 moves and 2.89e8 loop-body entries, about 90% of them the one-instruction [-] body, and each entry is a recursive run() call in all three ports. The largest cell value is 10 and the output is 27 bytes, so C's char-truncating tape_get and the per-character flush do not matter here.
- analyze.rb takes the median of 10 runs between the program's start and stop socket messages (parsing included, the self-test excluded) and never compares output checksums across languages. Each binary checks only a Hello World program before timing.

## Known shortcomings

- Lead only 1.09-1.16x and it reverses on mandel.b; V/gcc beats C too, so the gap is op layout rather than the language; capped at C by the no-mechanism rule (cargo release with LTO, codegen-units 1, target-cpu native).
- The JSON3.jl enricher found that kostya/benchmarks' 2026-07-19 update re-measured only the Primes table and the environment table: the Json table rows kept their 2025-08-17 values (gcc 14.2.0, clang 19.1.7), so the compiler versions recorded here (gcc 16.1.0, clang 22.1.8) describe the current environment table and may not be the toolchain behind this table's rows; whether this table was re-run on 2026-07-19 was not checked.
- Stale toolchain behind the published rows: the Rust, C and C++ bench.b and mandel.b rows in the 2026-07-19 README match the 2025-08-17 README digit for digit (only the .NET rows were re-measured), so they were measured with Rust 1.89.0, gcc/g++ 14.2.0 and clang 19.1.7, not the 1.97.1 / 16.1.0 / 22.1.8 the README lists. The ranking flips with the toolchain on the same sources (the 2023-10-16 run had C++/g++ 1.323 s vs Rust 1.658 s). bench.b mostly measures one recursive run() call per [-] iteration. Latent UB: Rust prev() at position 0 wraps and get_unchecked then reads out of bounds.

## Caveats and trade-offs

Margin is 9-16% and flips by benchmark: on mandel.b Rust is slower than every C and C++ row. All three are the same naive tree-walking interpreter (no run-length folding), but the op representations differ: Rust uses an enum with separate Inc/Dec variants and boxed child slices and reads the tape with unsafe get_unchecked, C uses a 16-byte tagged union with an offset field and a tape_get that truncates the int cell to char, and C++ uses a 32-byte Op struct that embeds a std::vector in every op. V/gcc, which emits C and compiles it with gcc, is faster than the C row, which points to data-layout and codegen variance rather than a language advantage. The suite reports median with median absolute deviation from a \~1 s run; no mechanism is given by the source. [retier] Enricher: the bench.b and mandel.b rows in the 2026-07-19 README match the 2025-08-17 README digit for digit except the .NET rows, so the Rust, C and C++ times date from Rust 1.89.0, gcc/g++ 14.2.0 and clang 19.1.7 on Debian trixie/sid; the ranking flips with the toolchain on the same sources (2023-10-16: C++/g++ 1.323 s vs Rust 1.658 s). bench.b mostly measures one recursive run() call per [-] iteration; Rust prev() at position 0 wraps and get_unchecked then reads out of bounds (UB).

Interpreter microbenchmark; one test program.

## Maintenance

The suite (MIT, 2.9k stars) is maintained, with a README update on 2026-07-19, but the brainfuck rows for Rust, C and C++ were not re-run then; the interpreter is copyable as a teaching reference, not a maintained library.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** README bench.b table shows Rust 1.008 s against C++/g++ 1.097 s, C/gcc 1.112 s, C/clang 1.136 s, C++/clang++ 1.167 s; methodology is complete (public code brainfuck/bf.rs, bf.c, bf.cpp; flags in common/commands.mk and bf.rs/Cargo.toml; compiler versions; Intel Xeon E-2324G), which would reach A, but the suite states no mechanism and the margin flips on mandel.b, so the wave-14 no-mechanism cap keeps it at C.
- **Verifier notes:** Numbers match the bench.b table (README updated 2026-07-19). Corrections: Rust build path confirmed (cargo release with LTO, codegen-units 1, panic abort, target-cpu native), speedup ratios restated (1.09x vs g++, 1.10x vs gcc C). Shortcoming: a 9-16% lead on one program that reverses on mandel.b, with V/gcc (C backend) beating C too, so it reflects implementation layout, not a Rust language mechanism; no mechanism in the source.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `baseline_stdlib`, `caveats`
- **Shortcomings recorded by:** verifier batch-28 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/README.md>
  - <https://github.com/kostya/benchmarks>
  - <https://github.com/kostya/benchmarks/commits/master>
  - <https://github.com/kostya/benchmarks/tree/master/brainfuck>
  - <https://github.com/kostya/benchmarks/tree/master/brainfuck/bf.rs>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/brainfuck/Makefile>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/common/commands.mk>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/brainfuck/bf.rs/Cargo.toml>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/brainfuck/bf.rs/src/main.rs>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/brainfuck/bf.c>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/brainfuck/bf.cpp>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/README.md>
  - <https://raw.githubusercontent.com/kostya/benchmarks/63ffa65/README.md>
  - <https://raw.githubusercontent.com/kostya/benchmarks/0fc4e58/README.md>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/brainfuck/Makefile>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/brainfuck/README.md>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/common/commands.mk>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/brainfuck/bf.rs/Cargo.toml>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/brainfuck/bf.rs/src/main.rs>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/brainfuck/bf.c>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/brainfuck/bf.cpp>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/brainfuck/bf.v>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/brainfuck/bench.b>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/brainfuck/mandel.b>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/analyze.rb>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/xtime.rb>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/common/rust/src/lib.rs>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/common/rust/Cargo.toml>
  - <https://raw.githubusercontent.com/kostya/benchmarks/63ffa65/common/commands.mk>
  - <https://raw.githubusercontent.com/kostya/benchmarks/63ffa65/brainfuck/bf.c>
  - <https://raw.githubusercontent.com/kostya/benchmarks/63ffa65/brainfuck/bf.cpp>
  - <https://raw.githubusercontent.com/kostya/benchmarks/63ffa65/brainfuck/bf.rs/src/main.rs>
  - <https://raw.githubusercontent.com/kostya/benchmarks/63ffa65/brainfuck/bf.rs/Cargo.toml>
  - <https://raw.githubusercontent.com/kostya/benchmarks/63ffa65/brainfuck/Makefile>
  - <https://raw.githubusercontent.com/kostya/benchmarks/0fc4e58/brainfuck/bf.rs/src/main.rs>
  - <https://raw.githubusercontent.com/kostya/benchmarks/0fc4e58/brainfuck/bf.rs/Cargo.toml>
  - <https://raw.githubusercontent.com/kostya/benchmarks/0fc4e58/brainfuck/bf.c>
  - <https://raw.githubusercontent.com/kostya/benchmarks/0fc4e58/brainfuck/bf.cpp>
  - <https://raw.githubusercontent.com/kostya/benchmarks/0fc4e58/common/commands.mk>
  - <https://github.com/kostya/benchmarks/commits/master/brainfuck/bf.rs>
  - <https://github.com/kostya/benchmarks/issues?q=is%3Aissue+brainfuck>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:rust/kostya/benchmarks#brainfuck-bench-b`) · [data/wave14/enrich/raw/lang_rust_kostya_benchmarks_brainfuck_bench_b.json](../../../data/wave14/enrich/raw/lang_rust_kostya_benchmarks_brainfuck_bench_b.json) (enrichment confidence 0.75)

</details>
