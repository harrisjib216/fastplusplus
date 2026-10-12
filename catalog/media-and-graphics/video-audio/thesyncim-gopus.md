# gopus (pure-Go Opus codec)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Video and audio](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Go` · `BSD-3-Clause` · 🟢 active

> Pure-Go (no cgo) Opus encoder/decoder whose SIMD build roughly matches, and in most tested encode cases beats, SIMD libopus 1.6.1.

| | |
|---|---|
| **Beats** | libopus 1.6.1 (C reference encoder and decoder, SIMD build) |
| **Claimed result** | Go SIMD takes 2.5-28.7% less time than matched C SIMD in four of five encoder cases (for example SILK wideband 329.21 vs 462.01 ns/sample, Hybrid fullband mono 225.80 vs 253.40, CELT fullband 20 ms stereo 126.28 vs 129.50) and 14.6% more in the 5 ms CELT case; float32 decode 33.14 vs 35.90 (7.7% less), int16 decode 37.64 vs 38.83 (3.1% less). Scalar rows: Go scalar is slower than C scalar in 6 of 7 rows (derived from page data). |
| **Workload** | Matched C and Go encode and decode workloads in ns per sample per channel. Encode (opus_encode_float vs gopus Encode, float32 PCM from deterministic synthetic signals, complexity 10, CBR, encoder reset per pass): CELT restricted-celt fullband 20 ms stereo 128 kbps, CELT 5 ms mono 64 kbps, SILK restricted-silk wideband 20 ms mono 32 kbps, Hybrid (application audio, voice signal) fullband 20 ms mono 64 kbps and stereo 96 kbps. Decode: RFC test vectors 01-12, 20,075 packets, as float32 and int16. |
| **Metric** | throughput |
| **Hardware** | AMD EPYC 7763 |
| **Compiler and flags** | Go 1.27.1, GOAMD64=v3, GOEXPERIMENT=simd, -pgo=default.pgo (profile generated from the repo's own encode/decode benchmarks); libopus 1.6.1 static archive configured --enable-static --disable-shared --enable-rtcd --enable-intrinsics with CFLAGS -O3 -DNDEBUG -march=x86-64-v3 -mtune=generic (GCC 13.3.0; AVX2/FMA RTCD lane, opus_select_arch=4), C helper compiled -O3 -DNDEBUG with the same target, no PGO or LTO on the C side; scalar lanes use --disable-asm --disable-rtcd --disable-intrinsics plus -fno-tree-vectorize -fno-tree-slp-vectorize against Go -tags nosimd. The C side runs as a separate helper process timed internally with clock_gettime, so process start-up is excluded. Three runs of at least 250 ms per case, median reported. Reproduce with tools/encoderbenchcmp and tools/testvectorbenchcmp. |
| **Adoption** | 27 stars, 2 forks; release v0.1.2; 3,296 commits |
| **Last commit** | 2026-10-02 |
| **Links** | [repository](https://github.com/thesyncim/gopus) · [benchmark](https://raw.githubusercontent.com/thesyncim/gopus/HEAD/README.md) |

## Verdict

On a GitHub Actions AMD EPYC 7763 runner at revision 4b660d668, Go 1.27.1 (GOAMD64=v3, GOEXPERIMENT=simd, PGO) was timed against a libopus 1.6.1 static build (GCC 13.3.0, -O3 -march=x86-64-v3, RTCD + intrinsics, AVX2/FMA lane) on identical PCM and controls (complexity 10, CBR): Go SIMD took 2.5-28.7% less time in four 20 ms encode cases, 14.6% more for 5 ms CELT, and 7.7% / 3.1% less for float32 / int16 decoding of the 12 RFC test vectors. Scalar Go against scalar C was slower in 6 of 7 rows; each row is the median of three runs of at least 250 ms with one codec instance per side, while the repo's own interleaved harness notes buffer placement alone can move a config's speed by up to about 15%.

## Use it when

- Go services (WebRTC SFUs, voice bots, transcoders) that need Opus without cgo, a C toolchain, or shipping libopus binaries.
- Cross-compiled or static Go binaries where cgo is off, e.g. scratch containers or CGO_ENABLED=0 builds for several OS/arch targets.
- amd64 (AVX2/FMA) or arm64 hosts where you can build with GOEXPERIMENT=simd and GOAMD64=v3: 20 ms SILK/Hybrid/CELT encode measured 2.5-28.7% less time than SIMD libopus, decode 3.1-7.7% less.
- Real-time paths that are sensitive to GC pressure: the packet APIs report zero allocations per encode/decode after warmup.

## Skip it when

- Default builds without GOEXPERIMENT=simd: scalar Go takes 18-66% more time than SIMD libopus on every row of the published table (e.g. Hybrid fullband mono encode 420.99 vs 253.40 ns/sample; float decode 42.29 vs 35.90) (derived from page data).
- Low-delay CELT with short frames: 5 ms CELT encode takes 14.6% more time than libopus, and the repo's own 56-config interleaved scoreboard (Intel Xeon, revision 6c0b0640b) has 2.5 ms CELT decodes at 1.22-1.25x libopus time even with SIMD.
- C/C++ codebases: there is no C ABI, so libopus or a C/C++ port is the natural choice; calling Go from C++ adds cgo export and runtime overhead.
- Toolchains older than Go 1.27, or builds where an experimental compiler feature is unacceptable: the SIMD path depends on GOEXPERIMENT=simd, and the validation report lists several open Go compiler SIMD bugs the code has to work around.
- Production use that needs a stable API or long track record: pre-v1 (v0.1.2, v0.1.0 retracted), 27 stars, and a stream of correctness fixes merged on 2026-10-01/02 (FEC, Ogg granules, soft clipping on NaN, codec boundaries).

## How it is fast

It ports the libopus algorithms source-for-source, then replaces all 53 former assembly routines (41 .s files) with Go kernels written against Go 1.27's experimental simd/archsimd package (AVX2/FMA on amd64, NEON on arm64), chosen by runtime CPU checks with scalar fallbacks. Hot paths are allocation-free after warmup (caller-owned buffers), the 256-bit SILK kernels are arranged to avoid legacy-SSE/AVX transition penalties (table-loaded NSQ constants, paired stores), and the published builds use PGO from a profile of the repo's own encode/decode benchmarks.

## Compared with alternatives

Pick gopus when the host language is Go and cgo is off; the other catalogued Opus reimplementations (opus-rs, ropus, ruopus, rusty-opus, opus-pure for Rust; opuspp for C++; libopus-rs's tuned libopus) target Rust or C/C++ callers. Of these, gopus has the most detailed matched-ISA parity and benchmark evidence, but its speed margin over libopus is smaller and less uniform than the larger claims some siblings make.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none (go.mod lists no requirements); optional DRED, OSCE, QEXT, custom-modes and fixed-point features behind build tags; libopus and a C compiler are needed only to run the parity tests and benchmarks |
| **Minimum toolchain** | Go 1.27 for master (go.mod 'go 1.27.0'); GOEXPERIMENT=simd for SIMD kernels; v0.1.2 is the published release |
| **Platforms** | any Go target with scalar kernels; SIMD kernels on amd64 (runtime AVX2/FMA checks, GOAMD64=v3 recommended) and arm64 (NEON); CI parity on Linux, macOS and Windows |
| **Thread safety** | Encoder and Decoder instances keep stream history and are not safe for concurrent calls; use one per stream |
| **Drop-in for the baseline** | partial — bitstream-compatible with libopus and controls map one to one (bitrate, complexity, VBR, DTX, FEC, packet loss, bandwidth, signal), but it is a Go API, not the opus_encode/opus_decode C ABI |

## Gotchas

- The fast numbers need three opt-ins: GOEXPERIMENT=simd, GOAMD64=v3 and PGO. Go applies a default.pgo only from the main package's directory (or an explicit -pgo path), so an application importing gopus does not inherit the repo's profile; the published Go SIMD rows have no no-PGO counterpart, while the C side had no PGO or LTO.
- The PGO profile is generated from benchmarks (EncoderEncode_Restricted CELT, CELT5ms and SILK CBR after reset, CELT/stereo decode) that mirror the timed workloads, so the table may be a best case for those shapes.
- Parity with libopus is scoped, not universal: the CBR contract (19 cases, 2,175 packets/ranges) is packet- and range-exact on the recorded lanes, but floating-point paths allow narrow documented differences and the README states universal packet or float-bit identity is not a release requirement.
- The default bitrate is 64 kbps while libopus defaults to automatic; set bitrate explicitly when comparing outputs, and note DTX makes Encode return zero bytes with a nil error.

## Known shortcomings

- Mixed result: Go SIMD is faster than libopus 1.6.1 (built with intrinsics and RTCD at -O3 -march=x86-64-v3, same flags as the Go side; complexity 10, CBR, matched bitrate, bandwidth, application and frame size) in 4 of 5 encode cases but 14.6% slower on 5 ms CELT frames, and decode is only 3.1-7.7% faster. The Go build uses PGO while the C side has none; the run is on a GitHub Actions EPYC 7763 runner; the decode bench checks sample counts only (bit-exactness is covered by separate final-range and PCM parity suites).
- The PGO profile is trained on benchmarks mirroring the timed workloads (Restricted CELT, CELT 5 ms, SILK CBR) and Go applies default.pgo only from the main package, so importers lose it and no no-PGO numbers are published; one instance per side with 3 runs while the repo's own interleaved harness says buffer placement shifts speed up to about 15%, so the 2.5-7.7% margins sit within noise. The default build (without GOEXPERIMENT=simd) is 18-66% slower than SIMD libopus (derived); the repo's 56-configuration scoreboard (Intel Xeon, 6c0b0640b) shows SIMD decode up to 1.253x libopus. 142 unsafe references were removed after the measured revision (#519, #523) with many correctness fixes on 2026-10-01 and 02.

## Caveats and trade-offs

Mixed result, not a uniform win: Go SIMD is faster than matched libopus SIMD in four of five encoder cases (2.5-28.7% less time) but 14.6% slower in the 5 ms CELT case, and decode wins are small (7.7% float32, 3.1% int16); Go scalar is slower than C scalar in 6 of 7 rows (10.6-23.4% more time, only SILK encode 2.8% faster). The Go side is built with PGO from a profile trained on the repo's own encode/decode benchmarks while the C side has no PGO or LTO. Measured on a GitHub Actions EPYC 7763 runner (shared cloud VM) with three runs per case, so the 2.5-7.7% margins are close to run-to-run noise. The timed decode loop checks only decoded sample counts; parity with libopus is enforced by separate test suites (exact final range and exact PCM on recorded configurations, with narrow documented floating-point allowances), so float decode output is not claimed bit-exact everywhere. The table is for revision 4b660d668 (2026-10-01); later master commits (#519 'Use safer codec kernels', #523 'Use checked kernel views') changed kernels without a fresh AMD64 table (ARM64-only deltas within about 3% are recorded). The file-based bench-encode/bench-decode examples include opus_demo start-up and file I/O and are only rough. First-party harness, though fully public. The fork hujm2023/gopus (0 stars) shows older CI numbers where Go is 1.3-1.7x slower than libopus; those were not used.

Go-only (no cgo) so C++ use needs an FFI shim or a Go service; the win needs GOAMD64=v3 and GOEXPERIMENT=simd, a Go 1.27 toolchain feature, and PGO; the README says the Go build tracks libopus 1.6.1 for bit-exact and quality parity, with optional DRED, QEXT and OSCE builds behind build tags.

## Maintenance

Very actively developed (3,296 commits, last merges 2026-10-02, branch names such as codex/correctness-edges suggest agent-assisted development) and BSD-3-Clause, but pre-v1 with a fast-moving master that requires Go 1.27; pin a commit and rerun tools/encoderbenchcmp on your own hardware before relying on the speed claim.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification A, tier now A.
- **Tier reason:** Public harness tools/encoderbenchcmp/main.go, tools/csrc/libopus_encoder_bench.c, tools/testvectorbenchcmp/main.go and internal/libopustooling/libopustooling.go build libopus 1.6.1 with --enable-rtcd --enable-intrinsics and CFLAGS -O3 -DNDEBUG -march=x86-64-v3 -mtune=generic, and match application, bandwidth, frame size, bitrate, CBR, signal and complexity 10 on both sides; README and reports/validation.md state Go 1.27.1, GCC 13.3.0, GOAMD64=v3, PGO, AMD EPYC 7763 and revision 4b660d668, with a public Actions run (36852328909) holding the raw samples.
- **Verifier notes:** Harness checked line by line: controls match on both arms (complexity 10, CBR, same bitrate/bandwidth/signal/application/frame size) and libopus is a real intrinsics+RTCD build at the same x86-64-v3 target, so tier A holds; the entry is a mixed result with small margins and a PGO asymmetry, stated in caveats. The pure-Go claim is also its usability point: BSD-3-Clause, 27 stars, last commit 2026-10-02.
- **Fields the verifier corrected:** `compiler_and_flags`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/thesyncim/gopus/HEAD/README.md>
  - <https://raw.githubusercontent.com/thesyncim/gopus/HEAD/reports/validation.md>
  - <https://raw.githubusercontent.com/thesyncim/gopus/HEAD/tools/encoderbenchcmp/main.go>
  - <https://raw.githubusercontent.com/thesyncim/gopus/HEAD/tools/testvectorbenchcmp/main.go>
  - <https://raw.githubusercontent.com/thesyncim/gopus/HEAD/tools/csrc/libopus_encoder_bench.c>
  - <https://raw.githubusercontent.com/thesyncim/gopus/HEAD/internal/libopustooling/libopustooling.go>
  - <https://raw.githubusercontent.com/thesyncim/gopus/HEAD/internal/libopustooling/reference_variant_simd.go>
  - <https://raw.githubusercontent.com/thesyncim/gopus/HEAD/internal/libopustooling/amd64_target_v3.go>
  - <https://raw.githubusercontent.com/thesyncim/gopus/HEAD/Makefile>
  - <https://github.com/thesyncim/gopus>
  - <https://github.com/thesyncim/gopus/tree/master/tools/encoderbenchcmp>
  - <https://github.com/thesyncim/gopus/tree/master/internal/libopustooling>
  - <https://github.com/thesyncim/gopus/actions/runs/36852328909>
  - <https://github.com/thesyncim/gopus/commits/master>
- **Sources the enricher read:**
  - <https://github.com/thesyncim/gopus>
  - <https://raw.githubusercontent.com/thesyncim/gopus/HEAD/README.md>
  - <https://raw.githubusercontent.com/thesyncim/gopus/HEAD/go.mod>
  - <https://raw.githubusercontent.com/thesyncim/gopus/HEAD/reports/validation.md>
  - <https://raw.githubusercontent.com/thesyncim/gopus/HEAD/tools/encoderbenchcmp/main.go>
  - <https://raw.githubusercontent.com/thesyncim/gopus/HEAD/tools/csrc/libopus_encoder_bench.c>
  - <https://raw.githubusercontent.com/thesyncim/gopus/HEAD/tools/testvectorbenchcmp/main.go>
  - <https://raw.githubusercontent.com/thesyncim/gopus/HEAD/tools/csrc/libopus_testvector_bench.c>
  - <https://raw.githubusercontent.com/thesyncim/gopus/HEAD/internal/libopustooling/libopustooling.go>
  - <https://raw.githubusercontent.com/thesyncim/gopus/HEAD/Makefile>
  - <https://raw.githubusercontent.com/thesyncim/gopus/HEAD/benchmark_libopus_scoreboard_test.go>
  - <https://raw.githubusercontent.com/thesyncim/gopus/HEAD/benchmark_libopus_scoreboard_interleaved_test.go>
  - <https://raw.githubusercontent.com/thesyncim/gopus/HEAD/SECURITY.md>
  - <https://raw.githubusercontent.com/thesyncim/gopus/HEAD/CONTRIBUTING.md>
  - <https://github.com/thesyncim/gopus/issues>
  - <https://github.com/thesyncim/gopus/issues?q=is%3Aissue+state%3Aclosed>
  - <https://github.com/thesyncim/gopus/pulls?q=is%3Apr>
  - <https://github.com/thesyncim/gopus/pull/519>
  - <https://github.com/thesyncim/gopus/pull/523>
  - <https://github.com/thesyncim/gopus/commits/master>
  - <https://raw.githubusercontent.com/golang/website/master/_content/doc/pgo.md>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/thesyncim/gopus`) · [data/wave10/enrich/raw/github_com_thesyncim_gopus.json](../../../data/wave10/enrich/raw/github_com_thesyncim_gopus.json) (enrichment confidence 0.8)

</details>
