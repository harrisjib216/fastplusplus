# Go goroutines vs Intel TBB on a task-graph dynamic program (Comparison-Go-CppTBB)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Concurrency runtimes](README.md)</sub>

**Tier A** (reproducible public benchmark) · Study only · `Go` · `CC-BY-4.0` · 🔴 abandoned

> 2017 study: Go goroutines vs Intel TBB tasks on tiled optimal-BST dynamic programming; Go won only at N=4096, by 1.003-1.15x.

| | |
|---|---|
| **Beats** | Intel oneTBB (2017 Update 3) C++ task scheduler, MSVC v14 build, on the same static optimal binary search tree task graph |
| **Claimed result** | From docs/N4096.xlsx and docs/N2048.xlsx (d503e57, 5 runs per cell): Go faster than TBB in 14 of 96 N=4096 cells (1.003-1.149x) and in 0 of 96 at N=2048; best configuration against best at N=4096 Go 25,574.2 ms vs TBB 28,655.2 ms (1.12x, derived from page data). Paper: at N=4096 and 4 processors Go ran faster than TBB at VP=256 and VP=512 (TBB/Go 1.12 and 1.15); best speed-up over each language's own sequential code 6.53 (Go) vs 4.41 (TBB) at N=2048 and 6.28 vs 3.95 at N=4096. |
| **Workload** | Static optimal binary search tree (dynamic programming over a DAG of chunk tasks, problem sizes N=2048 and N=4096, chunking factor VP 1 to 2048, 1 to 8 processors) implemented as goroutines plus channels in Go and as TBB tasks with atomic reference counts in C++. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-6700HQ (4 cores, 8 threads, 6 MB cache), Windows 10 Pro build 14393 |
| **Compiler and flags** | Go 1.7.4 (default go build, GOMAXPROCS set to NP); Intel TBB 2017 Update 3 prebuilt (tbb.lib/tbb.dll, vc14); C++ built with MSVC v14 in Visual Studio 2015 Update 3. The public TBB/TBB.vcxproj at release commit d503e57 sets Release\|x64 to Optimization Full (/Ox), IntrinsicFunctions (/Oi), FavorSizeOrSpeed Speed (/Ot), WholeProgramOptimization (/GL), RuntimeLibrary MultiThreaded (/MT) and SDLCheck (/sdl); the Debug\|x64 configuration is /Od with tbb_debug.lib. The paper does not say which configuration was measured; the README's run instructions require tbb.dll, which implies the Release build. |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | not stated |
| **Why it wins** | Paper's speculation: TBB's atomic reference-counter dependencies and depth-first execution give better locality overall, while Go's channel-based synchronization can trigger many more scheduling events; Go wins only at the larger problem size where its chunked tasks fit the cache better. No single mechanism is claimed for the Go win. |
| **Adoption** | 3 stars, 1 fork (archived 2018-08-24) |
| **Last commit** | 2018-08-24 |
| **Links** | [repository](https://github.com/luncliff/Comparison-Go-CppTBB) · [benchmark](https://github.com/luncliff/Comparison-Go-CppTBB/blob/master/%5BFinal%5DComparison%20of%20Go%20and%20C%2B%2B%20TBB%20on%20Parallel%20Processing.pdf) |

## Verdict

On one Intel Core i7-6700HQ laptop (Windows 10, five runs averaged), Go 1.7.4 goroutines beat Intel TBB 2017 Update 3 built with MSVC 2015 (Release /Ox inferred from the vcxproj) only at N=4096: 26,256.6 against 29,365.8 ms (1.12x) at VP=256 and 25,574.2 against 29,381 ms (1.15x) at VP=512, both with NP=4. TBB was faster in every N=2048 cell (1,417.2 against 1,946 ms at NP=4, VP=128, 1.37x) and in 82 of the 96 N=4096 cells.

## Use it when

- As a worked example of mapping a 2-D dynamic-programming wavefront onto goroutines plus channels and onto TBB tasks with atomic reference counts, side by side.
- As raw data for Go-versus-TBB task-graph scaling on a 4-core/8-thread Skylake laptop: docs/N2048.xlsx and docs/N4096.xlsx hold all five runs of every NP x VP cell.
- To choose a tile count for a blocked DP: both runtimes were fastest at VP 128-512 (tiles of 4-32 cells per side) and both lost ground at VP=2048.
- As the 2017 replication of Serfass and Tang (2012), when citing how the Go-versus-TBB gap narrowed with Go 1.7.

## Skip it when

- As evidence that Go beats C++: TBB was faster in all 96 N=2048 cells (best versus best 1.37x) and in 82 of 96 N=4096 cells, and the sequential C++ code was 1.39-2.03x faster.
- Fine-grained graphs with millions of nodes: the Go program starts every tile goroutine up front, and at VP=2048 it took 15.6-80.5 s at N=2048 against TBB's 2.3-7.1 s, with bimodal run-to-run times.
- On a current toolchain without porting: the C++ side uses the low-level tbb::task API (allocate_root, set_ref_count, spawn_and_wait_for_all), which oneTBB removed, and the Go side is a pre-modules GOPATH layout for Go 1.7.4.
- As copyable code: the licence is CC-BY-4.0 (not a software licence), the C++ project is a Windows-only Visual Studio 2015 vcxproj that uses printf_s, and the repository has been archived since 2018.

## How it is fast

There is no Go-specific technique behind the result. Both programs gain from tiling, which acts as cache blocking for the strided column reads cost[k+1][col] (stride N+1 doubles) that the row-by-row sequential sweep does not have, and from running tiles of the dependency wavefront on several cores. The Go program's sequential code is 2.03x (N=2048) and 1.39x (N=4096) slower than the MSVC build, so the narrow Go wins appear only at N=4096, where the table no longer fits in cache and both sides are memory-bound. The paper speculates that TBB's depth-first execution helps locality and that Go's channel waits trigger extra scheduling, but names no mechanism for the Go wins.

## Compared with alternatives

Cite this entry, and not the SCOOP/Qs thread-ring entries for Go and Erlang (whose 'C++/TBB' column is really 503 Boost.Asio-woken pthreads), when you need a compute-bound task graph in which TBB's own task scheduler is the baseline. Its answer is that TBB wins almost everywhere. For data-parallel loops, the Rayon versus OpenMP study is the closer sibling.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | Go: standard library only (GOPATH layout with packages obst, matrix, research, watch). C++: Intel TBB 2017 Update 3 prebuilt binaries (tbb.lib and tbb.dll for vc14) and CmdParser (git submodule under lib/). |
| **Minimum toolchain** | Go 1.7.4 as measured (GOPATH build, no go.mod); MSVC v140 (Visual Studio 2015 Update 3), C++14 (std::make_unique, decltype(auto)); TBB 2017 or another pre-oneTBB release that still has tbb::task |
| **Platforms** | C++ build: Windows x64 (Visual Studio project, printf_s); Go code is portable; measured only on Windows 10 with an Intel Core i7-6700HQ |
| **Thread safety** | Not applicable (benchmark programs). Tiles write disjoint cells of shared matrices; reads of neighbour tiles are ordered by a channel receive (Go) or by the reference count reaching zero (TBB). |
| **Drop-in for the baseline** | no |

## Gotchas

- The raw timings are in the repository after all: docs/N2048.xlsx and docs/N4096.xlsx at release commit d503e57 hold five runs per cell for NP 1-8 x VP 1-2048. From them, Go was faster in 14 of 96 N=4096 cells (VP 128-1024, NP 3-7, 1.003-1.149x) and in none of 96 N=2048 cells. Best against best at N=4096 is Go 25,574.2 ms (NP=4, VP=512) against TBB 28,655.2 ms (NP=5, VP=256), 1.12x (derived from page data); the draft conclusion's 1.15 is the matched NP=4, VP=512 cell. The 6,255.4 and 12,689.6 ms quoted at N=2048 are the sequential runs, and the sheet has 12,698.6 for Go.
- The self speed-ups mix tiling with parallelism. On one processor the tiled code already beats the sequential sweep: at N=2048, TBB at VP=128 took 4,180.6 ms against 6,255.4 ms (1.50x) and Go at VP=32 took 7,260 ms against 12,698.6 ms (1.75x); at N=4096 the one-thread gains are Go 1.47x and TBB 1.12x (derived from page data). So the 'superlinear' Go figures are partly a cache-blocking effect on a slower Go sequential baseline. They also do not contradict each other: 6.53 and 4.41 are the N=2048, NP=4, VP=128 cells, while 6.28 and 3.95 are the N=4096, NP=4 cells.
- No result validation: Go's Tree.Equal and C++'s operator== are never called, and both are inverted (they return false as soon as any compared root or cost pair matches), so the parallel output was never checked against the sequential sweep. My reading of the tile wiring (left and lower predecessors; lower-triangle channels left nil) found no race.
- The timed regions differ by design: Go's includes a blocking runtime.GC() after the parallel run, and C++'s includes constructing and destroying tbb::task_scheduler_init. The inputs differ too: Go uses math/rand with its default seed (Float64), while C++ uses mt19937 seeded from the clock (integers mod 2^20). The amount of work does not depend on the data. Go starts all VP(VP+1)/2 goroutines (about 2.1 million at VP=2048) before any can run, whereas TBB spawns a task only when it becomes ready; the VP=2048 Go averages mix runs of about 11 s and 70 s (N=2048, NP=2).

## Known shortcomings

- Go is faster only at N=4096 with VP 256/512 (1.12x, 1.15x) and TBB is faster elsewhere (1.37x best-vs-best); the paper names no build configuration, so the Release|x64 flags (/Ox /Oi /Ot /GL /MT /sdl in TBB/TBB.vcxproj at commit d503e57) are inferred from the README's tbb.dll requirement; the cache-fit explanation is not in the paper; CC-BY-4.0, archived.
- Raw timings are in the repo after all (docs/N2048.xlsx and docs/N4096.xlsx at d503e57, 5 runs per cell): Go is faster in 14 of 96 N=4096 cells (1.003-1.149x) and 0 of 96 at N=2048; best against best at N=4096 is 1.12x (Go 25,574.2 ms vs TBB 28,655.2 ms). The tiled code on one thread already beats sequential (TBB 1.50x, Go 1.75x at N=2048), so Go's 'superlinear' speed-up is partly cache blocking; Equal/operator== is never called and inverted, so the parallel output is never checked. 6.53/4.41 are N=2048 and 6.28/3.95 are N=4096 (no contradiction); 6255.4/12689.6 are sequential times (the sheet says 12698.6).

## Caveats and trade-offs

Single small first-party experiment: one laptop CPU (i7-6700HQ, 4 cores/8 threads), Windows 10, 5 repetitions averaged, 2017 toolchains (Go 1.7.4, TBB 2017U3); raw timings are not in the repo, only figures. The paper's own wording is that TBB was faster in general and Go won only partially at the larger size (N=4096, VP=256 and VP=512, ratio 1.12 and 1.15; the paper does not label the ratio's direction, TBB time over Go time is implied). At N=2048 TBB was faster in every condition and best-vs-best TBB was 1.37x faster. Go's 'superlinear' self-speed-up (6.28 on N=4096, 6.53 in the conclusion) against TBB's 3.95 (4.41) implies a Go sequential run roughly 1.3-1.4x slower than TBB's (derived from page data, assuming the best cases coincide), so the speed-up figures say little about scheduler quality; the two sets of best speed-ups in section 5 and the conclusion also disagree. At VP=2048 Go collapsed (72-91 s at NP=1, 4.9-66.6 s at NP=4) with the Go runtime taking up to 84% of CPU time, attributed to millions of goroutines. The measured build configuration is not stated in the paper; the public vcxproj Release|x64 flags (/Ox /GL) are inferred to be the ones used. The C++ Matrix holds new T[] in a std::unique_ptr&lt;T&gt; (delete instead of delete[]; undefined behaviour at destruction, outside the timed region). The paper is a KIPS (Korea Information Processing Society) conference paper per the release README ('The paper's copyright is reserved by KIPS'); the PDF itself states no venue and peer review of the proceedings is not established. The repo is archived and the README says it is no longer updated; code is under CC-BY-4.0 (not an OSI software licence), so usability is reference. The 2012 Serfass and Tang paper that this repeats is behind a blocked ACM page. [retier] The tiled code on one thread already beats the sequential baseline (TBB 1.50x, Go 1.75x at N=2048), so Go's 'superlinear' speed-up is partly cache blocking; Equal/operator== is never called and is inverted, so the parallel output is never checked. 6255.4/12689.6 are sequential times (the sheet says 12698.6).

Goroutines come with a garbage-collected runtime and growable stacks; at the highest chunk counts (VP=2048, millions of goroutines) Go lost most of its time in the runtime (up to 84% of CPU time in the worst case, runs from 4.9 s to 66.6 s with 4 processors) while TBB degraded smoothly. Go code is much shorter than the TBB task-graph code.

## Maintenance

Archived 2018-08-24 (56 commits, 3 stars, no issues). The CC-BY-4.0 research code is tied to Go 1.7 GOPATH builds and the removed tbb::task API, so it is a reference only. Its raw spreadsheets support the record but correct three of its caveats: the raw data is public, Go won 14 cells rather than 2, and the two speed-up pairs come from different problem sizes.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded from C: both implementations and their timing harness are public at the release commit d503e57 that the README points to (Go/main.go, Go/src/research/evaluate.go, Go/src/obst/tree.go; TBB/src/main.cpp, TBB/src/research/Tree.cpp, ChunkTask.hpp), the paper names Go 1.7.4, MSVC v14 (VS2015 Update 3), TBB 2017 Update 3 and the Intel Core i7-6700HQ, and the public TBB/TBB.vcxproj fixes the Release|x64 flags (/Ox, /Oi, /Ot, /GL, /MT, /sdl). The paper does not name the build configuration; Release is inferred from the README's run notes, which require tbb.dll (the release DLL; the Debug configuration links tbb_debug).
- **Verifier notes:** Numbers in claimed_speedup all match the PDF (6255.4 vs 12689.6 ms at N=2048; VP=1 6488.6 vs 13266.2 ms; speed-ups 6.28/3.95 and 6.53/4.41; ratios 1.37, 1.12, 1.15). Upgraded to A on the public vcxproj flags, but the build configuration is inferred, not stated: if the orchestrator wants stated flags only, keep C. Record shortcomings: Go faster only in 2 of the measured N=4096 conditions by 1.12-1.15x, TBB faster elsewhere; 2017 toolchains on one laptop; CC-BY-4.0 code, archived. why_faster corrected: the 'cache fit at larger size' explanation is not in the paper. same_opt_level set to true (inferred) in the record keys.
- **Fields the verifier corrected:** `compiler_and_flags`, `stars_or_usage`, `caveats`, `claimed_speedup`
- **Shortcomings recorded by:** verifier batch-84 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/luncliff/Comparison-Go-CppTBB/master/%5BFinal%5DComparison%20of%20Go%20and%20C%2B%2B%20TBB%20on%20Parallel%20Processing.pdf>
  - <https://raw.githubusercontent.com/luncliff/Comparison-Go-CppTBB/master/README.md>
  - <https://github.com/luncliff/Comparison-Go-CppTBB>
  - <https://github.com/luncliff/Comparison-Go-CppTBB/commits/master>
  - <https://github.com/luncliff/Comparison-Go-CppTBB/tree/master/cpp>
  - <https://github.com/luncliff/Comparison-Go-CppTBB/tree/master/cpp/src>
  - <https://raw.githubusercontent.com/luncliff/Comparison-Go-CppTBB/master/appveyor.yml>
  - <https://github.com/luncliff/Comparison-Go-CppTBB/tree/d503e5796589cc8a9fb4dc132146082e89162998>
  - <https://github.com/luncliff/Comparison-Go-CppTBB/commit/d503e5796589cc8a9fb4dc132146082e89162998>
  - <https://raw.githubusercontent.com/luncliff/Comparison-Go-CppTBB/d503e5796589cc8a9fb4dc132146082e89162998/README.md>
  - <https://raw.githubusercontent.com/luncliff/Comparison-Go-CppTBB/d503e5796589cc8a9fb4dc132146082e89162998/TBB/TBB.vcxproj>
  - <https://raw.githubusercontent.com/luncliff/Comparison-Go-CppTBB/d503e5796589cc8a9fb4dc132146082e89162998/TBB/src/research/Tree.cpp>
  - <https://raw.githubusercontent.com/luncliff/Comparison-Go-CppTBB/d503e5796589cc8a9fb4dc132146082e89162998/TBB/src/utils/Matrix.h>
  - <https://raw.githubusercontent.com/luncliff/Comparison-Go-CppTBB/d503e5796589cc8a9fb4dc132146082e89162998/TBB/src/main.cpp>
  - <https://github.com/luncliff/Comparison-Go-CppTBB/tree/d503e5796589cc8a9fb4dc132146082e89162998/Go>
  - <https://raw.githubusercontent.com/luncliff/Comparison-Go-CppTBB/d503e5796589cc8a9fb4dc132146082e89162998/Go/main.go>
  - <https://raw.githubusercontent.com/luncliff/Comparison-Go-CppTBB/d503e5796589cc8a9fb4dc132146082e89162998/Go/src/obst/tree.go>
  - <https://raw.githubusercontent.com/luncliff/Comparison-Go-CppTBB/d503e5796589cc8a9fb4dc132146082e89162998/Go/src/research/evaluate.go>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/luncliff/Comparison-Go-CppTBB/d503e5796589cc8a9fb4dc132146082e89162998/README.md>
  - <https://raw.githubusercontent.com/luncliff/Comparison-Go-CppTBB/master/README.md>
  - <https://raw.githubusercontent.com/luncliff/Comparison-Go-CppTBB/master/%5BFinal%5DComparison%20of%20Go%20and%20C%2B%2B%20TBB%20on%20Parallel%20Processing.pdf>
  - <https://github.com/luncliff/Comparison-Go-CppTBB/tree/d503e5796589cc8a9fb4dc132146082e89162998>
  - <https://github.com/luncliff/Comparison-Go-CppTBB/tree/d503e5796589cc8a9fb4dc132146082e89162998/Go/src/research>
  - <https://github.com/luncliff/Comparison-Go-CppTBB/tree/d503e5796589cc8a9fb4dc132146082e89162998/Go/src/obst>
  - <https://github.com/luncliff/Comparison-Go-CppTBB/tree/d503e5796589cc8a9fb4dc132146082e89162998/TBB/src/research>
  - <https://github.com/luncliff/Comparison-Go-CppTBB/tree/d503e5796589cc8a9fb4dc132146082e89162998/docs>
  - <https://github.com/luncliff/Comparison-Go-CppTBB/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/luncliff/Comparison-Go-CppTBB/d503e5796589cc8a9fb4dc132146082e89162998/Go/main.go>
  - <https://raw.githubusercontent.com/luncliff/Comparison-Go-CppTBB/d503e5796589cc8a9fb4dc132146082e89162998/Go/src/obst/tree.go>
  - <https://raw.githubusercontent.com/luncliff/Comparison-Go-CppTBB/d503e5796589cc8a9fb4dc132146082e89162998/Go/src/research/evaluate.go>
  - <https://raw.githubusercontent.com/luncliff/Comparison-Go-CppTBB/d503e5796589cc8a9fb4dc132146082e89162998/Go/src/research/channels.go>
  - <https://raw.githubusercontent.com/luncliff/Comparison-Go-CppTBB/d503e5796589cc8a9fb4dc132146082e89162998/Go/src/research/config.go>
  - <https://raw.githubusercontent.com/luncliff/Comparison-Go-CppTBB/d503e5796589cc8a9fb4dc132146082e89162998/Go/src/matrix/matrix.go>
  - <https://raw.githubusercontent.com/luncliff/Comparison-Go-CppTBB/d503e5796589cc8a9fb4dc132146082e89162998/Go/src/watch/watch.go>
  - <https://raw.githubusercontent.com/luncliff/Comparison-Go-CppTBB/d503e5796589cc8a9fb4dc132146082e89162998/TBB/src/main.cpp>
  - <https://raw.githubusercontent.com/luncliff/Comparison-Go-CppTBB/d503e5796589cc8a9fb4dc132146082e89162998/TBB/src/research/Tree.cpp>
  - <https://raw.githubusercontent.com/luncliff/Comparison-Go-CppTBB/d503e5796589cc8a9fb4dc132146082e89162998/TBB/src/research/Tree.h>
  - <https://raw.githubusercontent.com/luncliff/Comparison-Go-CppTBB/d503e5796589cc8a9fb4dc132146082e89162998/TBB/src/research/ChunkTask.hpp>
  - <https://raw.githubusercontent.com/luncliff/Comparison-Go-CppTBB/d503e5796589cc8a9fb4dc132146082e89162998/TBB/src/research/Evaluate.cpp>
  - <https://raw.githubusercontent.com/luncliff/Comparison-Go-CppTBB/d503e5796589cc8a9fb4dc132146082e89162998/TBB/src/research/Alias.h>
  - <https://raw.githubusercontent.com/luncliff/Comparison-Go-CppTBB/d503e5796589cc8a9fb4dc132146082e89162998/TBB/src/research/Config.cpp>
  - <https://raw.githubusercontent.com/luncliff/Comparison-Go-CppTBB/d503e5796589cc8a9fb4dc132146082e89162998/TBB/src/utils/Matrix.h>
  - <https://raw.githubusercontent.com/luncliff/Comparison-Go-CppTBB/d503e5796589cc8a9fb4dc132146082e89162998/TBB/src/utils/Watch.hpp>
  - <https://raw.githubusercontent.com/luncliff/Comparison-Go-CppTBB/d503e5796589cc8a9fb4dc132146082e89162998/TBB/TBB.vcxproj>
  - <https://raw.githubusercontent.com/luncliff/Comparison-Go-CppTBB/d503e5796589cc8a9fb4dc132146082e89162998/docs/N2048.xlsx>
  - <https://raw.githubusercontent.com/luncliff/Comparison-Go-CppTBB/d503e5796589cc8a9fb4dc132146082e89162998/docs/N4096.xlsx>
  - <https://raw.githubusercontent.com/luncliff/Comparison-Go-CppTBB/d503e5796589cc8a9fb4dc132146082e89162998/docs/Draft.md>
  - <https://raw.githubusercontent.com/uxlfoundation/oneTBB/master/doc/main/tbb_userguide/Migration_Guide/Task_API.rst>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/luncliff/comparison-go-cpptbb`) · [data/wave14/enrich/raw/github_com_luncliff_comparison_go_cpptbb.json](../../../data/wave14/enrich/raw/github_com_luncliff_comparison_go_cpptbb.json) (enrichment confidence 0.75)

</details>
