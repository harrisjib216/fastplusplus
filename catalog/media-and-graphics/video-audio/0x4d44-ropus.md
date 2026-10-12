# ropus (Rust port of libopus)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Media and graphics](../README.md) › [Video and audio](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `BSD-3-Clause (LICENSE is the upstream Xiph libopus BSD text plus a 2026 copyright line for the Rust port additions; ropus/Cargo.toml declares BSD-3-Clause)` · 🟢 active

> Pure-Rust, bit-exact port of fixed-point libopus 1.5.2; runs at about parity with the C reference, not faster.

| | |
|---|---|
| **Beats** | libopus 1.5.2 C reference as built by the repo's own harness (harness/build.rs via the cc crate): fixed-point (FIXED_POINT=1 in harness/config.h), no DNN, x86 runtime dispatch limited to SSE/SSE2/SSE4.1 (no AVX2 sources); the Apple M1 Pro rows use upstream AArch64 NEON intrinsics. Not the stock float build most distributions ship. |
| **Claimed result** | Rust/C time ratio on x86-64 (i7-14700KF, WSL2), medians of 5 sweeps at --iters=30 (below 1.0 means Rust faster): encode SILK NB noise 0.97x, SILK WB noise 0.96x, Hybrid noise 0.97x, CELT sweep 0.96x, CELT sine 1.00x; decode CELT square 0.92x, SILK NB 0.95x, CELT FB mono noise 0.98x, CELT sine 0.99x, CELT sweep 1.00x; worst rows encode 1.20x (CELT square, TTS speech) and decode 1.10x (SILK WB). Means 1.06x encode and 1.01x decode, i.e. parity or slightly slower. The journal's cross-sweep standard deviations (0.02-0.32 on encode, 0.01-0.09 on decode) are as large as the sub-1.0 margins, so the 'faster' rows are within noise. Apple M1 Pro means 1.16x encode and 1.22x decode (decode up to 1.50x on SILK WB), slower on every row except SILK NB/WB encode (0.99x/1.00x). |
| **Workload** | ropus-compare bench (harness/src/cli.rs cmd_bench) on ten WAV vectors (SILK NB/WB noise, Hybrid noise, CELT FB mono/stereo noise, sine, sweep, square, TTS speech, stereo music) at fixed bitrates 16-128 kb/s, complexity 10, CBR, OPUS_APPLICATION_AUDIO, 20 ms frames, codec construction outside the timed loop since commit 54fef85; decode times both decoders on the same C-encoded stream; per-vector ratio is Rust total time over C total time, median across 5 sweeps of tools/bench_sweep.sh --iters=30. The bench does not compare outputs. |
| **Metric** | throughput |
| **Hardware** | Intel i7-14700KF under WSL2 (x86-64 table); Apple M1 Pro (second table, where decode is slower, for example SILK NB 1.30x and SILK WB 1.50x); earlier Ryzen 9 9950X3D baseline kept in a journal |
| **Compiler and flags** | Rust: release profile lto = "thin", codegen-units = 1, target-cpu = x86-64-v3 for x86_64 and apple-a14 for aarch64-apple-darwin (.cargo/config.toml); rustc version not stated (MSRV 1.88). C reference: compiled by harness/build.rs through the cc crate with FIXED_POINT, OPUS_HAVE_RTCD, OPUS_X86_MAY_HAVE_SSE/SSE2/SSE4_1, -msse4.1 and -ffp-contract=off; the optimisation level comes from cc-crate profile defaults and the C compiler and version are not stated (a build.rs comment mentions GCC 13). libopus 1.5.2 ships silk/x86/NSQ_del_dec_avx2.c (SILK_SOURCES_AVX2) but the harness does not compile it, and the C core is not built for x86-64-v3, so code-generation flags favour the Rust side. |
| **Adoption** | 9 stars; 1,289 commits; crates.io ropus 0.12.18, 5,852 downloads (checked 2026-10-04) |
| **Last commit** | 2026-09-13 |
| **Links** | [repository](https://github.com/0x4D44/ropus) · [benchmark](https://raw.githubusercontent.com/0x4D44/ropus/HEAD/README.md) |

## Verdict

The project's own tools/bench_sweep.sh (harness cmd_bench, 10 WAV vectors, CBR, complexity 10, 20 ms frames, C encode and decode timed before Rust in a fixed order, no output comparison) on an i7-14700KF under WSL2 gives Rust/C time ratios with a mean of 1.06x for encode and 1.01x for decode (medians of 5 sweeps; the sub-1.0 rows fall inside the 0.02-0.32 cross-sweep spread). On Apple M1 Pro against upstream NEON C the means are 1.16x and 1.22x. The baseline is the harness's fixed-point, SSE4.1-only libopus 1.5.2, compiler versions are unstated, and both tables predate the 2026-08-01 harness fixes.

## Use it when

- Rust projects (native or WebAssembly) that want Opus without linking C libopus or needing a C compiler; videocall.rs reports using it in production for encode and NetEQ decode, including WASM clients (issue #1).
- When output must match fixed-point libopus 1.5.2 byte for byte (decode, and encode outside the tonality-analysis path), for example to test against a C reference or to replace audiopus or opus-sys bindings without changing bitstreams.
- When you need features most other ports skip: multistream, ambisonics projection, the repacketizer, in-band FEC/DTX and neural PLC.
- Throughput similar to the C reference is enough: about 1.06x encode and 1.01x decode time on x86-64 with the workspace's x86-64-v3 build.

## Skip it when

- If the goal is more speed than libopus: it is at parity on x86-64 and 16-22% slower on Apple M1 Pro, and several sibling ports report real speed-ups.
- Default crates.io builds on x86-64: the x86-64-v3 flag lives in the workspace's .cargo/config.toml, which dependents do not inherit, so a plain cargo add build targets baseline x86-64; the project's own generic-target run was about 1.19x slower than C on encode (Ryzen 9 9950X3D, before the bench fix).
- When you need bit-exactness with the float libopus that distributions ship: ropus tracks the fixed-point build, so decoded PCM will not match a float build bit for bit.
- When you need DRED PCM reconstruction (opus_decoder_dred_decode\*), OSCE, QEXT or custom modes: these are deferred or not ported.
- When maturity and outside review matter: one maintainer with AI agents doing most of the work (CLAUDE.md, AGENTS.md, codex and claude co-authored commits); 9 stars; the latest crates.io release, 0.12.18 (2026-05-11), is four months behind the repository.

## How it is fast

It is a line-by-line port of libopus's fixed-point code, not a new algorithm; speed comes from compiler work. Hot kernels use the wide crate's portable SIMD types plus unchecked indexing in the SILK and CELT inner loops (NSQ, Burg, autocorrelation, FFT butterflies, MDCT rotations), and the workspace builds with ThinLTO, codegen-units = 1 and target-cpu x86-64-v3 (apple-a14 on macOS ARM), so LLVM auto-vectorises at 256-bit width. There are no hand-written intrinsics; the project's April journal credits the x86-64-v3 switch alone with moving mean encode from 1.19x to 1.02x of C.

## Compared with alternatives

Pick ropus over the faster Opus ports (opuspp, opus-pure, ruopus, rusty-opus, gopus) when you need a full libopus API surface (multistream, projection, repacketizer, PLC) and bit-exact agreement with fixed-point libopus 1.5.2, checked by a differential harness and the RFC 6716/8251 vectors, rather than extra speed. For lower CPU cost, those siblings, or libopus-rs's 1-5% gain, are better candidates.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | wide 0.7 (runtime); cc (build script, only used when xiph reference sources are on disk) |
| **Minimum toolchain** | Rust 1.88 (edition 2024) |
| **Platforms** | Any Rust target via portable code; tuned for x86-64-v3 (AVX2, FMA, BMI2) and Apple M1 (apple-a14) in workspace builds; WebAssembly reported by a downstream user; no hand-written intrinsics on any platform |
| **Thread safety** | Encoder and Decoder are Send and Sync (checked by a compile-time test); encode and decode take &mut self, so use one instance per thread or guard it with a Mutex. |
| **Drop-in for the baseline** | partial: the low-level Rust API mirrors libopus, and the repository's capi/ crate (publish = false, built as the mdopus_capi staticlib) exposes the libopus C ABI and passes xiph's test programs, but it is not published, it does not expose the DRED decode calls, and its output matches the fixed-point libopus build, not the usual float build. |

## Gotchas

- The crates.io package ships an empty DNN weights blob (build.rs only embeds weights when the xiph reference tree is on disk), so neural PLC and DRED fall back to classical PLC unless you call set_dnn_blob; workspace builds instead embed an 8.78 MB blob that takes about 3.34 ms to load per decoder.
- Published numbers come from a harness with since-fixed measurement flaws. At commit 54fef85 (x86 table, 2026-05-11) and at the 2026-07-31 Apple run, harness/Cargo.toml always enabled trace-silk-encode, so Rust SILK encode pushed trace records into an unbounded Mutex&lt;Vec&gt;, while C ran a harness-modified traced enc_API.c (project bug ROP-BUG-FLUX-00026, severity High). The C timer also included one codec create and destroy per run (ROP-BUG-FLUX-00027). Both were fixed on 2026-08-01, but the README tables were not re-measured, and the size of either effect is unmeasured.
- The C baseline is the harness's own build: fixed-point, -msse4.1 applied to every C file, SSE4.1-only runtime dispatch (libopus 1.5.2's AVX2 NSQ_del_dec source is not compiled) and -ffp-contract=off. The Rust side gets x86-64-v3, so the 'C dispatches to hand-tuned SSE4.1/AVX2' wording overstates the baseline.
- The crates.io README still shows the stale April table (encode 1.02x, decode 0.95x, Ryzen 9 9950X3D), measured before the bench fix that took decoder construction and its weight load out of the timed loop.

## Known shortcomings

- Not faster: a port of the listed libopus with mean encode 1.06x and decode 1.01x on an i7-14700KF (1.16x/1.22x on an M1 Pro); sub-1.0 rows sit inside the cross-sweep standard deviation. The C side is the harness build (fixed-point, SSE4.1-only dispatch, NSQ_del_dec_avx2.c not compiled) while the Rust side is built x86-64-v3, so the README's 'SSE4.1/AVX2' overstates the baseline; compiler versions unstated. Decode is sample-exact against C; encode is byte-exact except the analysis path (about 5% byte drift on music). The crates.io README still shows the stale pre-fix table.
- Both README tables (x86 at 54fef85 of 2026-05-11; Apple of 2026-07-31) were measured with harness/Cargo.toml forcing trace-silk-encode (a Rust unbounded Mutex&lt;Vec&gt; trace, with C running a traced enc_API.c; tracked as ROP-BUG-FLUX-00026) and with the C timer covering one create/destroy per run (FLUX-00027); both were fixed on 2026-08-01 but the tables were never re-measured, so the size of the effect is unknown. The C build gets -msse4.1 on every file with no AVX2; x86-64-v3 lives only in the workspace .cargo/config.toml, so crates.io users get generic x86-64 (own generic run: encode 1.19x slower); crates.io 0.12.18 ships an empty DNN blob and lags the repo by four months.

## Caveats and trade-offs

Not faster than its baseline: a Rust port of libopus (already a list baseline) at roughly parity, mean encode 1.06x and decode 1.01x slower on x86-64 and 1.16x/1.22x slower on Apple M1 Pro; the few sub-1.0 rows (3-8%) sit inside the cross-sweep spread recorded in wrk_journals/2026.05.11 - JRN - perf-recalibration.md. The C side is the harness's own fixed-point build with SSE4.1-only dispatch (libopus 1.5.2's AVX2 NSQ_del_dec source is not compiled and the C code is not built for x86-64-v3), while the Rust side is compiled for x86-64-v3, so the README's 'C dispatches to hand-tuned SSE4.1/AVX2' overstates the baseline. Compiler versions are unstated, one desktop CPU under WSL2, first-party. Output equivalence: the differential harness, the seven xiph test binaries and the 24 RFC 6716/8251 vectors check decode sample-exact against C (first-party claim); encode is byte-exact except where the float tonality analysis runs (the crate README accepts about 5% byte drift on music under an SNR gate), and the benchmark itself does not compare outputs. The crates.io README (ropus/README.md) still shows the older April table (encode 1.02x, decode 0.95x, Ryzen 9950X3D) from before the 54fef85 bench fix and says both sides dispatch to AVX2. Earlier benches timed decoder construction (8.78 MB DNN weight load) rather than steady-state decode. The repo carries CLAUDE.md and AGENTS.md (AI-assisted).

Rust port of libopus 1.5.2 including DNN features (LPCNet, FARGAN, DRED) with a C ABI shim (capi/) that exposes the libopus API, plus a differential FFI harness that compares byte-for-byte against the C reference; builds the C reference from a pinned xiph/opus checkout. Larger binary because of an embedded 8.78 MB weights blob.

## Maintenance

Very active (1,289 commits, last 2026-09-13; the 99 of 124 internal bug-ledger records fetched are all Closed) and BSD-3-Clause, so it can be copied freely, but it is a young, mostly AI-written port whose crates.io release lags the repository and which is no faster than the C library it replaces.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party numbers from public benchmark code (tools/bench_sweep.sh driving harness/src/cli.rs cmd_bench, C built by harness/build.rs) on a named CPU (i7-14700KF, WSL2), but neither the rustc nor the C compiler version is stated and the C optimisation flags come from cc-crate defaults, so not A; no independent measurement.
- **Verifier notes:** Port of a listed baseline that is at parity, not faster; confirmed at C with the not-faster shortcoming per the batch note. Bench code read: it is like-for-like in codec settings (same bitrate, complexity 10, CBR, same C-encoded stream for decode), but the C reference is built fixed-point with SSE4.1-only dispatch while Rust gets x86-64-v3, which if anything flatters Rust. Decode is claimed sample-exact against libopus; encode is byte-exact except a documented tier-2 drift in the analysis path.
- **Fields the verifier corrected:** `baseline`, `compiler_and_flags`, `claimed_speedup`, `workload`, `stars_or_usage`, `license`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/0x4D44/ropus/HEAD/README.md>
  - <https://raw.githubusercontent.com/0x4D44/ropus/HEAD/tools/bench_sweep.sh>
  - <https://raw.githubusercontent.com/0x4D44/ropus/HEAD/harness/src/main.rs>
  - <https://raw.githubusercontent.com/0x4D44/ropus/HEAD/harness/src/cli.rs>
  - <https://raw.githubusercontent.com/0x4D44/ropus/HEAD/harness/build.rs>
  - <https://raw.githubusercontent.com/0x4D44/ropus/HEAD/harness/config.h>
  - <https://raw.githubusercontent.com/0x4D44/ropus/HEAD/harness/Cargo.toml>
  - <https://raw.githubusercontent.com/0x4D44/ropus/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/0x4D44/ropus/HEAD/.cargo/config.toml>
  - <https://raw.githubusercontent.com/0x4D44/ropus/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/0x4D44/ropus/HEAD/ropus/README.md>
  - <https://raw.githubusercontent.com/0x4D44/ropus/HEAD/ropus/Cargo.toml>
  - <https://raw.githubusercontent.com/0x4D44/ropus/HEAD/wrk_journals/2026.05.11%20-%20JRN%20-%20perf-recalibration.md>
  - <https://raw.githubusercontent.com/xiph/opus/v1.5.2/silk_sources.mk>
  - <https://raw.githubusercontent.com/xiph/opus/v1.5.2/celt_sources.mk>
  - <https://github.com/0x4D44/ropus>
  - <https://github.com/0x4D44/ropus/commits>
  - <https://crates.io/api/v1/crates/ropus>
- **Sources the enricher read:**
  - <https://github.com/0x4D44/ropus>
  - <https://github.com/0x4D44/ropus/tree/main>
  - <https://github.com/0x4D44/ropus/commits>
  - <https://github.com/0x4D44/ropus/commits/main/README.md>
  - <https://github.com/0x4D44/ropus/issues?q=is%3Aissue>
  - <https://github.com/0x4D44/ropus/issues/1>
  - <https://github.com/0x4D44/ropus/pulls?q=is%3Apr>
  - <https://github.com/0x4D44/ropus/tree/main/bugs>
  - <https://raw.githubusercontent.com/0x4D44/ropus/HEAD/README.md>
  - <https://raw.githubusercontent.com/0x4D44/ropus/HEAD/ropus/README.md>
  - <https://raw.githubusercontent.com/0x4D44/ropus/HEAD/ropus/CHANGELOG.md>
  - <https://raw.githubusercontent.com/0x4D44/ropus/HEAD/ropus/Cargo.toml>
  - <https://raw.githubusercontent.com/0x4D44/ropus/HEAD/ropus/build.rs>
  - <https://raw.githubusercontent.com/0x4D44/ropus/HEAD/ropus/src/lib.rs>
  - <https://raw.githubusercontent.com/0x4D44/ropus/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/0x4D44/ropus/HEAD/.cargo/config.toml>
  - <https://raw.githubusercontent.com/0x4D44/ropus/HEAD/capi/Cargo.toml>
  - <https://raw.githubusercontent.com/0x4D44/ropus/HEAD/harness/Cargo.toml>
  - <https://raw.githubusercontent.com/0x4D44/ropus/HEAD/harness/build.rs>
  - <https://raw.githubusercontent.com/0x4D44/ropus/HEAD/harness/config.h>
  - <https://raw.githubusercontent.com/0x4D44/ropus/HEAD/harness/src/cli.rs>
  - <https://raw.githubusercontent.com/0x4D44/ropus/HEAD/tools/bench_sweep.sh>
  - <https://raw.githubusercontent.com/0x4D44/ropus/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/0x4D44/ropus/HEAD/wrk_journals/2026.05.11%20-%20JRN%20-%20perf-recalibration.md>
  - <https://raw.githubusercontent.com/0x4D44/ropus/HEAD/wrk_journals/2026.04.19%20-%20JRN%20-%20avx2-baseline.md>
  - <https://raw.githubusercontent.com/0x4D44/ropus/HEAD/bugs/README.md>
  - <https://raw.githubusercontent.com/0x4D44/ropus/HEAD/bugs/ROP-BUG-FLUX-00026.md>
  - <https://raw.githubusercontent.com/0x4D44/ropus/HEAD/bugs/ROP-BUG-FLUX-00027.md>
  - <https://raw.githubusercontent.com/0x4D44/ropus/HEAD/bugs/ROP-BUG-FLUX-00002.md>
  - <https://raw.githubusercontent.com/0x4D44/ropus/HEAD/bugs/ROP-BUG-CRUCIBLE-00009.md>
  - <https://raw.githubusercontent.com/0x4D44/ropus/HEAD/bugs/ROP-BUG-KIL-00041.md>
  - <https://raw.githubusercontent.com/0x4D44/ropus/54fef85/harness/Cargo.toml>
  - <https://raw.githubusercontent.com/0x4D44/ropus/54fef85/harness/build.rs>
  - <https://raw.githubusercontent.com/0x4D44/ropus/54fef85/ropus/src/lib.rs>
  - <https://raw.githubusercontent.com/0x4D44/ropus/v0.12.18/harness/Cargo.toml>
  - <https://raw.githubusercontent.com/0x4D44/ropus/d0ab87e/harness/Cargo.toml>
  - <https://crates.io/api/v1/crates/ropus>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/0x4d44/ropus`) · [data/wave10/enrich/raw/github_com_0x4d44_ropus.json](../../../data/wave10/enrich/raw/github_com_0x4d44_ropus.json) (enrichment confidence 0.7)

</details>
