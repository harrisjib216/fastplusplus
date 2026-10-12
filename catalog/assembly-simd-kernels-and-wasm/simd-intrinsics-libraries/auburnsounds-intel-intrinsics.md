# intel-intrinsics (inteli, SIMD library for D)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `D` · `BSL-1.0` · 🟢 active

> D library exposing the Intel _mm_\* intrinsics API (MMX to AVX2, SHA, BMI2) on LDC, DMD and GDC, emulated on ARM.

| | |
|---|---|
| **Beats** | Phobos std.digest.sha sha256Of (scalar D standard-library SHA-256) |
| **Claimed result** | README: '18x faster SHA-256 vs Phobos' with intel-intrinsics; separately cites a 3.5x speed-up for some particular loops in a DConf 2019 talk and dg2d renderer 'twice as fast as Cairo' (unmeasured on the page). |
| **Workload** | SHA-256 of a 1,024,000-byte buffer (512 \* 2000 bytes of 'a'), repeated 1000 times, comparing std.digest.sha sha256Of against a SHA-NI implementation written with inteli intrinsics (examples/sha256/source/main.d); both print elapsed microseconds and the digest. |
| **Metric** | throughput |
| **Compiler and flags** | LDC; examples/sha256/dub.json sets dflags-ldc ["-mattr=+sha,+sse4.2,+popcnt"] and no build type (dub builds in debug mode unless --build=release is passed); LDC version and the build command used for the 18x figure are not stated. |
| **Adoption** | 73 stars; used by Auburn Sounds and Cut Through Recordings audio products, dg2d and PixelPerfectEngine |
| **Last commit** | 2026-10-10 |
| **Links** | [repository](https://github.com/AuburnSounds/intel-intrinsics) · [benchmark](https://github.com/AuburnSounds/intel-intrinsics/blob/master/examples/sha256/source/main.d) |

## Verdict

The one measured claim is the README's '18x faster SHA-256 vs Phobos': examples/sha256 hashes a 1,024,000-byte buffer of 'a' 1000 times with Phobos sha256Of (portable scalar transformSHA2) and with an SHA-NI kernel written with inteli's _mm_sha256\* intrinsics, both built by LDC with -mattr=+sha,+sse4.2,+popcnt, and prints elapsed time and both digests. No CPU, LDC version, build type or output is recorded, the default dub build is unoptimized, and the gain mostly reflects dedicated SHA hardware instructions rather than generic SIMD.

## Use it when

- Writing or porting SIMD kernels in D (audio DSP, image processing, parsing) and wanting the same source to build with LDC, DMD and GDC.
- Porting existing C or C++ intrinsics code to D almost line for line, since the function names and type erasure match the Intel guide.
- Shipping x86 intrinsics code to Apple Silicon or other AArch64 targets through LDC without rewriting it in NEON, with rounding-mode semantics preserved through FPCR.
- Hashing large buffers in D on x86 CPUs with SHA extensions: copy the public-domain examples/sha256 kernel and build with LDC -mattr=+sha in an optimized build.

## Skip it when

- C or C++ projects: this is a D library; use the native intrinsics headers, SIMDe, EVE or the Vector Class Library instead.
- AVX-512 code: the supported set stops at AVX2 plus F16C, BMI2 and SHA.
- One binary that must pick the instruction set at run time: feature selection is compile time only (__traits(targetHasFeature) on LDC, __traits(compiles) on GDC), and the README recommends targeting SSE3 for consumer reach.
- Code that needs a guaranteed exact instruction: the README promises semantics, not instruction selection, and accepts slower code to keep semantics.
- SHA-256 on ARM, on DMD, or on LDC without -mattr=+sha: shaintrin.d then runs a scalar D emulation of each SHA instruction, so the 18x figure does not carry over (there is no mapping to the ARMv8 SHA2 instructions).

## How it is fast

Each intrinsic is lowered to the compiler's own vector builtins (LDC's ldc.gccbuiltins_x86 or LLVM IR, GDC's gcc.builtins, DMD's D_SIMD) when the target feature is enabled at compile time, so the compiler emits the corresponding SIMD instruction; otherwise a portable D fallback keeps the same semantics. The SHA-256 example's speed comes from the dedicated x86 SHA extensions (sha256rnds2, sha256msg1, sha256msg2), following the Intel/Sean Gulley SHA-NI kernel as ported in Crypto++, against Phobos' portable scalar transformSHA2.

## Compared with alternatives

Pick intel-intrinsics only for D code: EVE and the Vector Class Library give C++ portable SIMD types with their own APIs, while intel-intrinsics keeps the Intel _mm_\* names across D compilers and emulates them on ARM, which suits porting existing intrinsics code into D.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none (optional nurt runtime for no-druntime builds) |
| **Minimum toolchain** | CI covers DMD 2.098.1+, LDC 1.28.1+ and GDC 12; avoid LDC 1.32.0 (no SIMD builtins, slow path with a compile-time warning) |
| **Platforms** | x86 and x86-64 (DMD, LDC, GDC; GDC vector paths disabled on 32-bit x86), AArch64 and 32-bit ARM (LDC), WebAssembly SIMD partial and still being verified |
| **Thread safety** | not documented; intrinsics are stateless functions, and the ARM MXCSR emulation keeps the rounding mode in FPCR, which is per thread |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw: examples/sha256/dub.json sets dflags-ldc but no buildType, so a plain 'dub run' gives dub's default debug build, and the README records neither the build command nor the CPU, LDC version or timings. Phobos' SHA-256 is a template compiled with the example's flags, and Phobos issue #10423 (open since 2020) reports SHA256 and SHA512 taking up to 26x longer in unoptimized builds than with ldc2 -O3, so the 18x ratio cannot be separated from a debug-build artifact.
- Harness flaw: on Windows the example's getTickUs defaults to precise=true, which reads QueryThreadCycleTime (thread CPU cycles) and returns 1000 \* cycles / QPC frequency labelled as microseconds, although its own comment says this mode 'is not reliable and should never be the default'; both rows share the timer, so only the ratio is usable.
- Masked loads and stores must address fully readable memory even where the mask is zero (pad buffers); AVX float compares do not honour the signalling-NaN option; F16C float-to-half conversions ignore the rounding mode.
- Wrong-result fixes are still landing: on 2026-10-10 _mm256_extract_epi16 and _mm256_extract_epi8 were fixed to zero-extend instead of sign-extend, and _mm_blend_epi32 and _mm_adds_epi32 were fixed under DMD 32-bit after a fuzzing review; open issues include #138 (_mm_pow_ps with small numbers) and DMD/GDC performance gaps (#114, #116).

## Known shortcomings

- README 18x over Phobos SHA-256 with no CPU, LDC version or build type (dub default is debug); the gain comes from SHA-NI hardware against Phobos's portable path. D language.
- Enricher: the example dub.json sets no buildType so the default dub run builds debug, and Phobos SHA-256 is a template compiled with the example's flags (Phobos issue #10423, open since 2020, reports SHA256/512 up to 26x slower unoptimised than ldc2 -O3), so the 18x cannot be told apart from a debug-build artifact; on Windows getTickUs defaults to a precise mode its own comment calls unreliable; ratio only; SHA intrinsics fall back to scalar emulation on ARM, DMD and LDC without +sha; no runtime dispatch, no AVX-512; SHA-256 is example code, not library API. Retiered to D. Leads: cerjones/dg2d (D 2D rasterizer, README claims 2x Cairo), noloader/SHA-Intrinsics.

## Caveats and trade-offs

The 18x figure is a README claim without hardware, compiler version, build type or timing output; the benchmark source prints times but the repo does not record results. dub.json sets no buildType, so a plain 'dub run' builds debug; both sides are templates compiled with the same flags, but the ratio depends on the unstated build mode. Baseline is Phobos' portable SHA-256 (std/digest/sha.d uses transformSHA2 for SHA-256; its SSSE3 assembly path covers SHA-1 only), not an optimised library such as OpenSSL, and the fast path relies on dedicated SHA-NI instructions rather than generic SIMD, so the ratio reflects hardware offload as much as the library. On Windows the example's getTickUs defaults to QueryThreadCycleTime scaled by the QPC frequency, which its own comment calls unreliable; both rows use the same timer, so the ratio is unaffected but the printed microseconds may be wrong. Example code is derived from the Crypto++ SHA-SIMD reference (Walton, Blumenthal, Raad) by Johan Engelen (public domain). Claims for dg2d versus Cairo and the 3.5x DConf 2019 talk figure have no numbers on the page and are not part of this entry's tier. Licence file is named COPYING (BSL-1.0, also declared in dub.json). D language, not C++.

D language only (usable from C++ only by calling D code through a C ABI). Provides the Intel intrinsics API (MMX to AVX2, F16C, BMI2) with one syntax across LDC, DMD and GDC and emulates it on AArch64 and 32-bit ARM. Project states semantics are preserved even at the cost of speed. SHA-NI benchmark needs a CPU with SHA extensions. ARM differences: MXCSR emulated through FPCR, masked loads and stores need padded buffers.

## Maintenance

Actively maintained (fuzzing-driven fixes on 2026-10-10; CI on Linux, Windows and macOS across DMD, LDC and GDC), BSL-1.0 and source-only, so easy to vendor into D projects; irrelevant to C++ codebases except as a model for porting.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now D.
- **Tier reason:** First-party: the README states '18x faster SHA-256 vs Phobos' and links examples/sha256/source/main.d, which times std.digest.sha sha256Of against a SHA-NI path written with inteli intrinsics (1000 x 1,024,000 bytes) and prints both digests; no recorded output, CPU model, LDC version or build type, so it cannot reach A or B.
- **Retiered** C to D: Enricher (2026-10-12): the '18x faster SHA-256 vs Phobos' example's dub.json sets no buildType, so the default dub run builds debug, and Phobos SHA-256 is a template compiled with the example's flags (Phobos issue #10423 reports SHA256/512 up to 26x slower unoptimised than ldc2 -O3); the 18x cannot be distinguished from a debug-build artifact and no optimised measurement exists. Crippled baseline with no valid measurement.
- **Verifier notes:** Record accurate: README claim, workload (512\*2000 bytes of 'a', 1000 iterations), LDC dflags, BSL-1.0, 73 stars and last commit 2026-10-10 all check out. Shortcomings: first-party ratio with no CPU, LDC version or build type; baseline is portable Phobos SHA-256 versus SHA-NI hardware instructions; D library, not C++.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-96 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/AuburnSounds/intel-intrinsics/HEAD/README.md>
  - <https://raw.githubusercontent.com/AuburnSounds/intel-intrinsics/HEAD/examples/sha256/source/main.d>
  - <https://raw.githubusercontent.com/AuburnSounds/intel-intrinsics/HEAD/examples/sha256/dub.json>
  - <https://raw.githubusercontent.com/AuburnSounds/intel-intrinsics/HEAD/dub.json>
  - <https://github.com/AuburnSounds/intel-intrinsics>
  - <https://github.com/AuburnSounds/intel-intrinsics/commits>
  - <https://raw.githubusercontent.com/dlang/phobos/HEAD/std/digest/sha.d>
- **Sources the enricher read:**
  - <https://github.com/AuburnSounds/intel-intrinsics>
  - <https://github.com/AuburnSounds/intel-intrinsics/commits>
  - <https://github.com/AuburnSounds/intel-intrinsics/issues?q=is%3Aissue+is%3Aopen>
  - <https://github.com/AuburnSounds/intel-intrinsics/tree/master/.github/workflows>
  - <https://raw.githubusercontent.com/AuburnSounds/intel-intrinsics/HEAD/README.md>
  - <https://raw.githubusercontent.com/AuburnSounds/intel-intrinsics/HEAD/dub.json>
  - <https://raw.githubusercontent.com/AuburnSounds/intel-intrinsics/HEAD/COPYING>
  - <https://raw.githubusercontent.com/AuburnSounds/intel-intrinsics/HEAD/examples/sha256/source/main.d>
  - <https://raw.githubusercontent.com/AuburnSounds/intel-intrinsics/HEAD/examples/sha256/dub.json>
  - <https://raw.githubusercontent.com/AuburnSounds/intel-intrinsics/HEAD/source/inteli/shaintrin.d>
  - <https://raw.githubusercontent.com/AuburnSounds/intel-intrinsics/HEAD/source/inteli/internals.d>
  - <https://raw.githubusercontent.com/AuburnSounds/intel-intrinsics/HEAD/source/inteli/package.d>
  - <https://raw.githubusercontent.com/AuburnSounds/intel-intrinsics/HEAD/.github/workflows/x86_64.yml>
  - <https://raw.githubusercontent.com/AuburnSounds/intel-intrinsics/HEAD/.github/workflows/gdc.yml>
  - <https://raw.githubusercontent.com/dlang/phobos/HEAD/std/digest/sha.d>
  - <https://github.com/dlang/phobos/issues/10423>
  - WebSearch: intel-intrinsics sha256 SHA-NI Phobos 18x (snippet of issues.dlang.org bug 20939)
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/auburnsounds/intel-intrinsics`) · [data/wave13/enrich/raw/github_com_auburnsounds_intel_intrinsics.json](../../../data/wave13/enrich/raw/github_com_auburnsounds_intel_intrinsics.json) (enrichment confidence 0.65)

</details>
