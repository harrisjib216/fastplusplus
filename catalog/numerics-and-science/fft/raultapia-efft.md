# eFFT (event-based FFT)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [FFT](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `GPL-3.0` · 🟢 active

> Header-only C++17/Eigen incremental 2D FFT for event cameras; updates an exact spectrum per event instead of rerunning FFTW.

| | |
|---|---|
| **Beats** | FFTW (fftw_plan_dft_2d, full N x N 2D FFT recomputed after every event or event packet) |
| **Claimed result** | No comparative numbers published in the repo or on any opened page. The README says FFTW3 'served as the benchmark for testing and evaluation' and benchmarks/efft_benchmark.cpp pairs BenchmarkFeedWithEvents/BenchmarkFeedWithPackets with FFTW versions; CI runs that target (ci.yaml 'Benchmark' step) but results are not committed. A TPAMI abstract snippet (not opened) gives absolute eFFT times only (&lt; 1 microsecond per event for packets of more than 40 events at 128 x 128). |
| **Workload** | Incrementally maintaining the exact 2D FFT of an N x N event-camera frame (N = 16 to 256) as random single events (250 per iteration) or packets of 100 to 5000 events arrive, versus re-running a full FFTW 2D transform after each update. |
| **Metric** | latency |
| **Compiler and flags** | Compiler not stated (CMake default toolchain). benchmarks target in the root CMakeLists.txt: -O3 -march=native -flto -funroll-loops -finline-functions -fomit-frame-pointer -ffast-math, defines NDEBUG, EIGEN_STACK_ALLOCATION_LIMIT=0 and EFFT_USE_FFTW3; C++17, Eigen &gt;= 3.4, FFTW3 &gt;= 3.3.8, Google Benchmark. |
| **Adoption** | 23 stars, 2 forks; PyPI package efft; Docker image; TPAMI 2024 and JORS 2026 papers |
| **Last commit** | 2026-09-22 |
| **Links** | [repository](https://github.com/raultapia/efft) · [benchmark](https://github.com/raultapia/efft/blob/main/benchmarks/efft_benchmark.cpp) |

## Verdict

No comparative numbers are published in the repo or on any reachable page. benchmarks/efft_benchmark.cpp (Google Benchmark, -O3 -march=native -ffast-math for eFFT) pits eFFT against an FFTW 2D transform rerun after every event or packet with FFTW_ESTIMATE | FFTW_NO_SIMD in double precision (a deliberately weak baseline), and CI runs it without committing results. The only figures seen are absolute eFFT times from the TPAMI abstract snippet, with no CPU named.

## Use it when

- Event-camera (DVS) pipelines that need the full 2D spectrum after every event or small packet, e.g. frequency-domain registration or filtering on 64x64 to 256x256 windows.
- Sparse binary frames where a few pixels toggle between consecutive transforms and you would otherwise rerun a full 2D FFT at each step.
- Packets of tens to thousands of events at 128x128; the TPAMI abstract (seen only as a search snippet) reports under 1 microsecond per event for packets over 40 events and under 0.5 microsecond for packets over 200.
- GPL-compatible C++ or Python projects (pip install efft, nanobind bindings) that already use Eigen.

## Skip it when

- General FFTs of dense or fully changing data: every update still rewrites the full N x N root matrix, so a from-scratch FFT (FFTW, PocketFFT, KFR) is the right tool.
- Non-binary pixel values: update() can only set a pixel to 0 or 1; arbitrary intensities enter only through initialize(matrix).
- Non-power-of-two or non-square frames, 1D or 3D transforms, inverse transforms or double precision: none is supported (complex float only; issue #1 asked for IFFT code).
- Memory-tight targets: the tree holds (log2 N + 1) x N^2 complex floats plus an N(N+1) twiddle table, about 5 MB at N=256, spread over roughly (4N^2)/3 separately heap-allocated Eigen matrices (figures derived from the code).
- Proprietary or permissively licensed codebases: GPLv3 copyleft.

## How it is fast

It stores every intermediate matrix of a 2D radix-2x2 decimation-in-time FFT in a quadtree (log2 N + 1 levels). An event changes one leaf, so only the matrices on that leaf's root path are recomputed. A level of size n costs about n^2 butterfly outputs, so one event costs roughly (4/3) N^2 complex operations, against about N^2 log2 N for a full FFT; this ratio is derived from reading the code, not measured. Events that do not change a pixel's state stop the recomputation, and packet updates partition the events by row and column parity so each shared ancestor matrix is recomputed once per packet, not once per event.

## Compared with alternatives

Pick eFFT when the input changes sparsely between transforms and you need the full exact spectrum each time. MPSFT and the SFFT library target sparse spectra, PFT and Auto-MPFT compute only a few output coefficients, and SpFFT handles sparse 3D plane-wave input; for ordinary one-shot 2D FFTs, FFTW, PocketFFT or KFR are the choice.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | Eigen &gt;= 3.4 (Eigen 5 handled); optional FFTW3 &gt;= 3.3.8 with -DEFFT_USE_FFTW3 for ground-truth checks; GTest and Google Benchmark for tests and benchmarks; nanobind for the Python package |
| **Minimum toolchain** | C++17, CMake &gt;= 3.20 |
| **Platforms** | any with C++17 and Eigen; CI builds and tests on Ubuntu, Windows (MinGW-w64 GCC via MSYS2) and macOS |
| **Thread safety** | not documented; each eFFT instance holds mutable tree state (copy deleted, move allowed), so one instance per thread or external locking |
| **Drop-in for the baseline** | partial: it produces the same unnormalized forward 2D DFT as fftw_plan_dft_2d (the tests compare them element-wise), but only for power-of-two square binary frames and through an event-update API, not a plan/execute API |

## Gotchas

- update(Stimuli&) reorders the caller's vector and right-shifts its row/col fields in place, so the packet is unusable afterwards (the tests copy it first); initialize(matrix) likewise overwrites its argument with the transform.
- Within one packet, duplicate events on a pixel resolve to 'on' if any of them is on, regardless of order; it is not last-event-wins.
- No bounds or size checks: row and col are effectively taken modulo N, and no static_assert enforces a power-of-two N.
- Precision is single-precision float. The tests accept a Frobenius-norm difference from FFTW (double) below 0.001 after single events and below 0.1 after packets, for N up to 256.

## Known shortcomings

- Downgraded C to D: paired FFTW benchmark code exists but no numbers are published anywhere reachable (abstract snippet gives absolute times only). The FFTW baseline is deliberately crippled (FFTW_ESTIMATE, FFTW_NO_SIMD, double vs float).
- update(Stimuli&) reorders the caller's vector and shifts its row/col in place; initialize(matrix) overwrites its argument; events set pixels only to 0 or 1; no power-of-two check on N; complex float only, no inverse transform; GPLv3. The TPAMI paper (pubmed blocked, snippet only) gives absolute times and says FFTW SIMD was disabled 'for fair comparison'.

## Caveats and trade-offs

(1) No benchmark numbers or CPU model appear in the repo, README, PyPI description or any page I could open; the TPAMI paper (doi 10.1109/TPAMI.2024.3422209), the JORS paper (doi 10.5334/jors.642, openresearchsoftware.metajnl.com) and Zenodo are egress-blocked. The abstract snippet gives absolute eFFT times only (PSNR &gt; 55 dB, SSIM &gt; 0.999; &lt; 1 microsecond per event for packets &gt; 40 events and &lt; 0.5 microsecond for &gt; 200 events at 128 x 128), not a ratio against FFTW. Retier to B if the TPAMI paper's FFTW comparison is read. (2) The in-repo FFTW baseline is deliberately weak: initializeGroundTruth plans fftw_plan_dft_2d with FFTW_ESTIMATE | FFTW_UNALIGNED | FFTW_NO_SIMD | FFTW_PRESERVE_INPUT, runs in double precision while eFFT uses float, and recomputes the whole N x N transform for every event (or packet); getGroundTruthFFT() also casts and transposes the row-major double result into a float Eigen matrix. Both benchmark sides copy the result into a new matrix (auto result = efft.getFFT() copies too), so the copy cost is roughly symmetric apart from the cast. In CI FFTW comes from the distro package, so the -O3 -march=native -ffast-math flags apply only to eFFT. (3) Different problem from a plain FFT: incremental exact update after sparse input changes versus a from-scratch transform, meaningful only for event-stream use. (4) Events are seeded from std::random_device, so runs are not bit-reproducible. (5) Last commit 2026-09-22 ('Update .gitignore'), read from the github.com commits page; PyPI efft 1.0.5 lists GPL-3.0-later while the header and GitHub say GPL v3.

Header-only C++17 on top of Eigen; frame size is a compile-time template parameter and must be a power of two (radix-2 tree); keeps a tree of intermediate matrices (about log2 N levels of N x N complex floats) so memory is well above one frame; single-precision complex (float) output; GPLv3 copyleft; Python bindings via nanobind. It is not a drop-in FFT: it only wins when the input changes by a few pixels between transforms (event streams) and needs one initial full transform.

## Maintenance

Active: 57 commits, last commit 2026-09-22, a TPAMI 2024 and a JORS 2026 paper, a PyPI package (efft 1.0.5) and a Docker image; it is a single small header that is easy to vendor, but GPLv3 limits that to GPL-compatible projects.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification C, tier now D.
- **Tier reason:** benchmarks/efft_benchmark.cpp does pair eFFT against an FFTW 2D baseline, but no results are published anywhere I could open (README, repo files, PyPI description); the TPAMI and JORS papers are egress-blocked and the only snippet seen gives absolute eFFT times, not a ratio against FFTW, so no comparative number is available: D.
- **Verifier notes:** Downgraded C to D: a paired FFTW benchmark exists but no comparative number is on any reachable page. Not rejected: a TPAMI 2024 paper and a PyPI package make it referenced, and the keep-and-document rule applies; metadata (GPL-3.0, 23 stars, 2 forks, active) confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/raultapia/efft>
  - <https://raw.githubusercontent.com/raultapia/efft/HEAD/README.md>
  - <https://github.com/raultapia/efft/tree/main/benchmarks>
  - <https://github.com/raultapia/efft/blob/main/benchmarks/efft_benchmark.cpp>
  - <https://raw.githubusercontent.com/raultapia/efft/HEAD/benchmarks/efft_benchmark.cpp>
  - <https://github.com/raultapia/efft/tree/main/.github/workflows>
  - <https://raw.githubusercontent.com/raultapia/efft/HEAD/.github/workflows/ci.yaml>
  - <https://raw.githubusercontent.com/raultapia/efft/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/raultapia/efft/HEAD/include/efft.hpp>
  - <https://github.com/raultapia/efft/commits/main>
  - <https://pypi.org/pypi/efft/json>
- **Sources the enricher read:**
  - <https://github.com/raultapia/efft>
  - <https://raw.githubusercontent.com/raultapia/efft/HEAD/README.md>
  - <https://raw.githubusercontent.com/raultapia/efft/HEAD/include/efft.hpp>
  - <https://raw.githubusercontent.com/raultapia/efft/HEAD/benchmarks/efft_benchmark.cpp>
  - <https://raw.githubusercontent.com/raultapia/efft/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/raultapia/efft/HEAD/.github/workflows/ci.yaml>
  - <https://raw.githubusercontent.com/raultapia/efft/HEAD/tests/efft_test.cpp>
  - <https://raw.githubusercontent.com/raultapia/efft/HEAD/python/pyproject.toml>
  - <https://github.com/raultapia/efft/issues?q=is%3Aissue>
  - <https://github.com/raultapia/efft/issues/1>
  - https://pubmed.ncbi.nlm.nih.gov/38954586/ (EGRESS_BLOCKED)
  - WebSearch snippets: TPAMI 10.1109/TPAMI.2024.3422209 abstract and JORS 10.5334/jors.642 summary (pages not opened)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/raultapia/efft`) · [data/wave8/enrich/raw/github_com_raultapia_efft.json](../../../data/wave8/enrich/raw/github_com_raultapia_efft.json) (enrichment confidence 0.75)

</details>
