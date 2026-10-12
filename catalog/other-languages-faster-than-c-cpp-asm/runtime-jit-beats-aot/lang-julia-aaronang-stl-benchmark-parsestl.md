# Julia vs C++ (clang, CMake Release): aaronang/stl-benchmark ParseStl

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Runtime JIT beats ahead-of-time](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Julia` · `MIT` · 🔴 abandoned

> 2018 three-language binary-STL parser where Julia 1.0 reads 7,392 triangles in 212 us against 409 us for clang C++ iostreams.

| | |
|---|---|
| **Beats** | C++ ParseStl benchmark (Google Benchmark) built with clang++ and CMake -DCMAKE_BUILD_TYPE=Release |
| **Claimed result** | C++ 409.210 us, Julia 211.641 us, Python 25150.9 us: Julia about 1.93x faster than C++ (derived from page data). |
| **Workload** | Parse the binary STL file nist.stl (80-byte header, uint32 triangle count, then 50-byte records of 12 float32 plus a 2-byte attribute count; about 7,400 triangles judging from Julia's 347.06 KiB allocation) into a vector of triangle structs, opening the file on every iteration. C++ (cpp/main.cpp): std::ifstream, reserve, then two read() calls per triangle (48 bytes plus a 2-byte dummy) and emplace_back; reported as Google Benchmark mean CPU time over 1729 iterations (real time 429.234 us). Julia (julia/stl.jl): open, skip(80), read UInt32, then map over triangles with read!(stl, Ref{Triangle}) plus skip(2); reported as BenchmarkTools @btime, which prints the minimum time. |
| **Metric** | latency |
| **Hardware** | Only the C++ run lists the machine: '8 X 2300 MHz CPU s', L1 32K, L2 262K, L3 6291K (CPU model not named); the Julia run's hardware is not stated |
| **Compiler and flags** | C++: /usr/bin/clang++ (version not stated, probably Apple clang given the setup) via CMake -DCMAKE_BUILD_TYPE=Release (CMake's Release default for Clang is -O3 -DNDEBUG; not printed in the repo), C++11, no -march; Google Benchmark submodule at 9ffb8df. Julia v1.0 started with julia -O3 (BenchmarkTools 0.4.1 per Manifest.toml); Julia's JIT targets the host CPU. |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | not stated |
| **Same optimization level** | not stated |
| **Adoption** | 7 stars |
| **Last commit** | 2018-10-08 |
| **Links** | [repository](https://github.com/aaronang/stl-benchmark) · [benchmark](https://raw.githubusercontent.com/aaronang/stl-benchmark/master/README.md) |

## Verdict

Parsing nist.stl (7,392 triangles) took 409.210 us mean CPU time in C++ (std::ifstream reads, clang, CMake Release, C++11, on a machine Google Benchmark reports as 8 x 2300 MHz with a 6291K L3, probably 4 cores with SMT) and 211.641 us minimum in Julia 1.0 run with julia -O3 (hardware not stated), about 1.93x by the README's own numbers (derived from page data); Python 3.7 took 25,150.9 us. Julia 1.3+ ran the same code at 689.599 us in PR #3 because of IOStream locking.

## Use it when

- As a cautionary example that small-record reads through a stream library are dominated by per-call overhead (sentry and virtual-buffer calls in iostreams, locks in Julia 1.3+ IOStream or stdio), whatever the language.
- As a starting harness for a fair re-run: same machine, same statistic, current Julia with open(path; lock = false) against C++ reading the whole file once (one read or mmap) and copying 50-byte records.
- When someone cites 'Julia is 2x faster than C++ at parsing files': this repo is the likely source, and its caveats below are the answer.

## Skip it when

- As evidence that Julia beats C++ today: on Julia 1.3 and later the unchanged parser ran 689.599 us because IOStream reads now take a lock (ChrisRackauckas, open PR #3, August 2020), 1.7x slower than the README's C++ time, and only 243.900 us with locking disabled.
- As a parser to vendor: no error handling (C++ ignores stream failures and its end-of-file assert is compiled out by -DNDEBUG in Release), host-endian reads with no byte swapping, binary STL only (no ASCII STL), and no handling of truncated files.
- As a language comparison: neither side uses the fast approach (one bulk read or mmap of the 361 KiB file), so both numbers mostly measure library call overhead plus a file open and close per iteration.
- For any claim about hardware: the Julia run's machine is not stated, and the C++ run only prints '8 X 2300 MHz' with four 32K L1 data caches, four 262K L2 caches and a 6291K L3.

## How it is fast

The measured gap is the per-call cost of the I/O library, not code generation. C++ makes two std::ifstream::read calls per triangle (48 bytes, then a 2-byte dummy), about 14,800 formatted-stream calls per parse; Julia 1.0 makes one read!(io, Ref{Triangle}) plus a skip(io, 2) per triangle on an IOStream that took no lock in 1.0. Derived from page data: about 55 ns per triangle for C++ (409.210 us CPU time / 7,392) against 29 ns for Julia (211.641 us / 7,392), i.e. 0.9 GB/s against 1.75 GB/s for a file that sits in the page cache. SimonDanisch's merged PR #2 (commit 40c7a16) replaced twelve read(stl, Float32) calls per triangle with the single 48-byte read!, which the blog credits with a 4x Julia speedup; the C++ side never received the equivalent tuning.

## Compared with alternatives

Prefer the LangArena, kostya/benchmarks and benchLANG Julia, Java and C# rows, which use current GCC 16 and Clang 22 baselines and many C/C++ configurations, for any current claim; this repo is only worth citing as the I/O-bound case in the category, where the result hinges on stream-library locking and per-call overhead rather than on JIT code generation.

## Integration

| | |
|---|---|
| **Form** | source-drop (three short parsers in one repo; not a package) |
| **Dependencies** | C++: Google Benchmark as a git submodule (commit 9ffb8df) and CMake 3.12+; Julia: BenchmarkTools 0.4.1 (Manifest.toml); Python: standard library only (struct, dataclasses, timeit) |
| **Minimum toolchain** | C++11 (CMake CXX_STANDARD 11) with clang as in the README; Julia 1.0; Python 3.7 for dataclasses. The pddshk fork notes the old benchmark submodule needs '#include &lt;limits&gt;' added to benchmark_register.h to build with newer compilers. |
| **Platforms** | any little-endian host (both parsers reinterpret the file bytes in host byte order); the published C++ run is probably macOS with Apple clang (inferred from /usr/bin/clang and the cache layout), the Julia run's platform is not stated |
| **Thread safety** | not applicable (single-threaded benchmark); the Julia 1.0 IOStream had no locking, which is what the PR #3 regression on 1.3+ is about |
| **Drop-in for the baseline** | no |

## Gotchas

- Different statistics: the C++ figure is Google Benchmark's mean CPU time over 1,729 iterations (409.210 us; wall time 429.234 us), the Julia figure is BenchmarkTools @btime, which prints the minimum wall time, and Python takes the minimum of 500 timeit runs. A minimum-against-mean comparison flatters Julia by an unknown amount, and the two runs may not even share a machine.
- Unequal tuning, then and later: Julia was rewritten by a Julia core contributor (PR #2) while the C++ kept two istream::read calls per record; the unmerged PR #4 (pddshk, 2021) rewrote both sides and still reports C++ 236.744 us CPU against Julia 110.646 us on a '12 X 4500 MHz' machine, but its C++ calls stdio fread twice per triangle, and POSIX stdio locks the stream on every call, while its Julia opens the file with lock = false and unsafe_reads into a preallocated vector, so the locking asymmetry of PR #3 simply moved to the other side.
- The C++ harness discards the returned vector without benchmark::DoNotOptimize, reads the triangle count through an (unsigned int \*) cast of a char array (a strict-aliasing violation that works in practice), relies on transitive includes for &lt;vector&gt; and assert, and compiles its EOF assert out under Release, while Julia's @assert eof(stl) runs on every call; none of these explains the 2x, but they show the C++ side was not reviewed.
- The explanatory blog post (aaronang.github.io) is unreachable here (DNS failure) and the author's site repo has been replaced by a 2025 Vite site, so the post's reasoning could not be read; the README itself says 'I am neither a C++ nor Julia expert'.

## Known shortcomings

- Same algorithm at -O3 on both sides, but the win comes from the I/O library layer (ifstream vs IOStream); the Julia side was tuned by SimonDanisch; on Julia 1.3+ PR #3 shows 689.599 us, slower than the C++ 409.210 us; statistics mixed (mean CPU time vs @btime minimum).
- The gap is I/O per-call overhead, not codegen: nist.stl has 7,392 triangles, C++ 55 ns against Julia 29 ns per triangle. Statistic mismatch: Google Benchmark's mean CPU time against @btime's minimum. The C++ side was never tuned while Julia was rewritten by SimonDanisch in PR #2 (commit 40c7a16); the Julia 1.3+ IOStream lock gives 689.599 us (PR #3). The unmerged PR #4 fork (pddshk/stl-benchmark) has C++ fread at 236.744 us against Julia lock = false at 110.646 us, so the lock asymmetry just moved to the C side (locked fread against unlocked Julia). Minor C++ harness sloppiness: no DoNotOptimize, an aliasing cast, assert compiled out. The blog post is unreachable.

## Caveats and trade-offs

Author says 'I am neither a C++ nor Julia expert'. The Julia side was tuned by a Julia core contributor (PR #2 by SimonDanisch, which the linked blog credits with making the Julia code '4 times faster'), while the C++ side uses straightforward iostream reads. The two timings use different statistics (Google Benchmark mean CPU time vs BenchmarkTools minimum wall time) and the Julia run's hardware is not stated. The win is version dependent: in open PR #3 (2020) Chris Rackauckas reports the unchanged parser at 689.599 us on Julia 1.3+ because IOStream reads now take a lock (243.900 us with the lock disabled), i.e. slower than the README's C++ time (different machine, no C++ rerun). Open PR #4 (2021) rewrites both stl.jl and main.cpp and is unmerged. Explanatory blog post is on github.io (blocked here). Julia 1.0 from 2018. [retier] nist.stl has 7,392 triangles (C++ 55 ns against Julia 29 ns per triangle), so the gap is I/O per-call overhead, not codegen. Statistic mismatch: Google Benchmark's mean CPU time against @btime's minimum. The C++ side was never tuned while Julia was rewritten by SimonDanisch in PR #2; the Julia 1.3+ IOStream lock gives 689.599 us (PR #3). The unmerged PR #4 fork has C++ fread at 236.744 us against Julia lock = false at 110.646 us, so the lock asymmetry moved to the C side. No DoNotOptimize, an aliasing cast, assert compiled out.

Single small parsing kernel written by the repo author in each language.

## Maintenance

Abandoned since 8 October 2018 (two open PRs from 2020 and 2021 never merged), MIT-licensed and trivial to vendor, but the 1.93x figure is tied to Julia 1.0's unlocked IOStream and mismatched statistics, so treat it as a historical anecdote rather than evidence.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** README shows C++ ParseStl 409.210 us (CPU time) and Julia 211.641 us with public code (cpp/main.cpp, cpp/CMakeLists.txt, julia/stl.jl) and build steps (clang, CMake Release, julia -O3), but no clang version, no CPU model (only '8 X 2300 MHz CPU s' for the C++ run) and no hardware for the Julia run, so not A; author's own single measurement, C.
- **Verifier notes:** Confirm C. README numbers match (C++ 409.210 us vs Julia 211.641 us, 1.93x derived; 2.03x using real time 429.234 us). Both sides do the same read pattern at -O3-level optimisation, so not a crippled baseline, but the gain is an I/O-library effect that disappeared on Julia 1.3+ (689.599 us in PR #3) and the Julia side was expert-tuned while the C++ side was not; record these as shortcomings. Metadata (MIT, 7 stars, last commit 2018-10-08, abandoned) checked and correct.
- **Fields the verifier corrected:** `workload`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-74 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/aaronang/stl-benchmark/master/README.md>
  - <https://github.com/aaronang/stl-benchmark>
  - <https://github.com/aaronang/stl-benchmark/commits/master>
  - <https://github.com/aaronang/stl-benchmark/tree/master/cpp>
  - <https://github.com/aaronang/stl-benchmark/tree/master/julia>
  - <https://raw.githubusercontent.com/aaronang/stl-benchmark/master/cpp/CMakeLists.txt>
  - <https://raw.githubusercontent.com/aaronang/stl-benchmark/master/cpp/main.cpp>
  - <https://raw.githubusercontent.com/aaronang/stl-benchmark/master/julia/stl.jl>
  - <https://raw.githubusercontent.com/aaronang/stl-benchmark/master/julia/Manifest.toml>
  - <https://raw.githubusercontent.com/aaronang/stl-benchmark/master/julia/Project.toml>
  - <https://raw.githubusercontent.com/aaronang/stl-benchmark/master/python/benchmark.py>
  - <https://github.com/aaronang/stl-benchmark/pulls?q=is%3Apr>
  - <https://github.com/aaronang/stl-benchmark/pull/2>
  - <https://github.com/aaronang/stl-benchmark/pull/3>
  - <https://github.com/aaronang/stl-benchmark/pull/4>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/aaronang/stl-benchmark/master/README.md>
  - <https://raw.githubusercontent.com/aaronang/stl-benchmark/master/cpp/main.cpp>
  - <https://raw.githubusercontent.com/aaronang/stl-benchmark/master/cpp/CMakeLists.txt>
  - https://raw.githubusercontent.com/aaronang/stl-benchmark/master/cpp/nist.stl (369,684 bytes; header count 7,392 triangles)
  - <https://raw.githubusercontent.com/aaronang/stl-benchmark/master/julia/stl.jl>
  - <https://raw.githubusercontent.com/aaronang/stl-benchmark/master/julia/Project.toml>
  - <https://raw.githubusercontent.com/aaronang/stl-benchmark/master/julia/Manifest.toml>
  - <https://raw.githubusercontent.com/aaronang/stl-benchmark/master/python/benchmark.py>
  - <https://github.com/aaronang/stl-benchmark/tree/master/cpp>
  - <https://github.com/aaronang/stl-benchmark/issues?q=is%3Aissue>
  - <https://github.com/aaronang/stl-benchmark/pull/2>
  - <https://github.com/aaronang/stl-benchmark/commit/40c7a16>
  - <https://github.com/aaronang/stl-benchmark/pull/3>
  - <https://github.com/aaronang/stl-benchmark/pull/4>
  - <https://raw.githubusercontent.com/pddshk/stl-benchmark/master/README.md>
  - <https://raw.githubusercontent.com/pddshk/stl-benchmark/master/cpp/main.cpp>
  - <https://raw.githubusercontent.com/pddshk/stl-benchmark/master/cpp/CMakeLists.txt>
  - <https://raw.githubusercontent.com/pddshk/stl-benchmark/master/julia/stl.jl>
  - <https://github.com/aaronang/aaronang.github.io>
  - <https://github.com/aaronang/aaronang.github.io/branches/all>
  - https://aaronang.github.io/2018/stl-benchmark-comparison-cpp-vs-julia/ (ENOTFOUND)
  - WebSearch: '"STL Benchmark Comparison: C++ vs. Julia" aaronang' (no copy of the post found)
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:julia/aaronang/stl-benchmark#parsestl`) · [data/wave14/enrich/raw/lang_julia_aaronang_stl_benchmark_parsestl.json](../../../data/wave14/enrich/raw/lang_julia_aaronang_stl_benchmark_parsestl.json) (enrichment confidence 0.6)

</details>
