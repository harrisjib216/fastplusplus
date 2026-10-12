# mlkem-native (pq-code-package)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Hand-written assembly kernels](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `Apache-2.0 OR ISC OR MIT` · 🟢 active

> Formally verified C90 ML-KEM (FIPS 203) with AArch64 Neon and x86-64 AVX2 assembly, about 2-3x faster than its portable C.

| | |
|---|---|
| **Beats** | mlkem-native's own portable C backend (CI 'no-opt' rows, native backends disabled); that C code is a C90 fork of the pq-crystals/kyber ref implementation and is what liboqs ships as its portable C ML-KEM since 0.13.0 |
| **Claimed result** | (derived from page data) ML-KEM-768 cycles, C backend divided by native backend, repo commit aad9b74 (2026-10-12 CI run): Intel Xeon 4th gen c7i keypair 46550 -&gt; 19302 (2.41x), encaps 55352 -&gt; 20638 (2.68x), decaps 67682 -&gt; 26122 (2.59x); AMD EPYC 4th gen c7a 59740 -&gt; 21586 (2.77x), 67717 -&gt; 22806 (2.97x), 84577 -&gt; 29706 (2.85x); Graviton2 keypair 96838 -&gt; 47604 (2.03x), encaps 109796 -&gt; 53830 (2.04x), decaps 134838 -&gt; 68518 (1.97x); Graviton4 1.97x / 1.98x / 1.90x. Range over the 8 EC2 targets for ML-KEM-768: 1.9x to 3.0x. |
| **Workload** | Cycle counts per ML-KEM-512/768/1024 keypair, encaps and decaps from the project's CI benchmark job (./scripts/tests bench, PMU/PERF cycle counters), native AArch64 (SLOTHY-optimised Neon, HOL-Light-verified) and x86-64 AVX2 assembly backends against the portable C backend of the same tree, on AWS EC2 Graviton2-5, Intel Xeon 3rd/4th gen and AMD EPYC 3rd/4th gen instances. |
| **Metric** | latency |
| **Hardware** | AWS EC2: c7i.metal-24xl (Intel Xeon 4th gen), c6i.large (Intel Xeon 3rd gen), c7a.medium (AMD EPYC 4th gen), c6a.large (AMD EPYC 3rd gen), t4g.small (Graviton2), c7g.medium (Graviton3), c8g.medium (Graviton4), c9g.medium (Graviton5); self-hosted Raspberry Pi 4/5, Snapdragon 888 A55, SpacemiT K1, Apple M1, POWER10 and Cortex-M55 rows also exist in data.js. |
| **Compiler and flags** | GCC from the flake-locked nixpkgs nixos-26.05 (nix dev shell 'bench', toolchains_native = pkgs.gcc wrapped in nix/util.nix; exact version not printed in the opened files), on an Ubuntu 26.04 LTS AMI. Common flags from test/mk/config.mk: -O3 -fomit-frame-pointer -std=c99 -pedantic. Per-target flags from .github/workflows/bench.yml: all EC2 rows add -flto and -DMLK_FORCE_AARCH64 or -DMLK_FORCE_X86_64; c7i: -mavx2 -mbmi2 -mpopcnt -march=sapphirerapids; c7a: -march=znver4; c6i: -march=icelake-server; c6a: -march=znver3; Graviton2: -mcpu=cortex-a76 -march=armv8.2-a; Graviton3: -march=armv8.4-a+sha3; Graviton4: -march=armv9-a+sha3; Graviton5: -march=armv9-a+sha3 -DMLK_SYS_AARCH64_FAST_SHA3. The opt and no-opt rows use identical flags; no-opt passes --opt=no_opt (OPT=0) to disable the native backends. |
| **Adoption** | 247 stars, 69 forks; default ML-KEM in liboqs since 0.13.0 and in AWS-LC since v1.50.0, and so in rustls since 0.23.28 through its AWS-LC provider, per the README |
| **Last commit** | 2026-10-12 |
| **Links** | [repository](https://github.com/pq-code-package/mlkem-native) · [benchmark](https://raw.githubusercontent.com/pq-code-package/mlkem-native/gh-pages/dev/bench/data.js) |

## Verdict

The project's CI benchmark (test/bench/bench_mlkem.c: 500 samples of 300 iterations after 50 warm-up calls, median cycles, shared-secret equality checked) runs the same tree with native backends on and off, built with the same GCC from nixpkgs nixos-26.05 at -O3 -flto and per-CPU -march flags; for ML-KEM-768 at commit aad9b74 the native build takes 1.9x to 3.0x fewer cycles than the C backend across eight AWS EC2 instance types (for example decaps 67,682 to 26,122 cycles on Sapphire Rapids c7i.metal, 134,838 to 68,518 on Graviton2). The harness itself looks sound; the limitation is that the baseline is the project's own optimised C, not the unmodified reference code or another library.

## Use it when

- Adding ML-KEM (or hybrid X25519MLKEM768 key exchange) to a C or C++ TLS, VPN or KEM stack on x86-64 with AVX2 or on AArch64 servers and phones.
- You need assurance beyond tests: HOL-Light proofs of functional correctness, memory safety and constant-time behaviour for the AArch64 and x86-64 assembly, and CBMC memory and type-safety proofs for the C code.
- Handshake-heavy servers where tens of thousands of cycles per encaps/decaps matter: CI shows ML-KEM-768 decaps at about 26k cycles on Sapphire Rapids versus about 68k for the C backend.
- Embedded or freestanding builds that need a C90 code base with stack-only allocation by default, optional custom allocator, zeroize, randombytes, memcpy and memset hooks.
- You already depend on liboqs (0.13.0+) or AWS-LC (v1.50.0+), which ship this code, and want to vendor the same implementation directly.

## Skip it when

- You need ML-DSA or other post-quantum schemes: this repository is ML-KEM only.
- Microcontrollers such as Cortex-M4: the Armv8.1-M Helium backend is experimental and disabled by default, and pqm4 has dedicated Cortex-M4 assembly.
- Threat models with power, EM, fault-injection or speculative-execution attackers: the project states it only targets timing side channels.
- Generic distribution binaries built for baseline x86-64 or Armv8.0 without a capability hook: backends are chosen at compile time by default, so without -mavx2 or MLK_CONFIG_CUSTOM_CAPABILITY_FUNC you get only the C backend.
- Stack-constrained targets: issue #1338 (open) reports stack usage much higher than mlkem-c-embedded.

## How it is fast

A fixed C frontend calls two swappable backends: arithmetic (NTT, inverse NTT, base multiplication with cached Montgomery products, rejection sampling, (de)compression, (de)serialisation) and FIPS-202/Keccak, including a 4-way batched Keccak-f1600 used for matrix generation. The AArch64 Neon assembly is written as clean code and then scheduled by the SLOTHY constraint-solving superoptimiser; the x86-64 backend is AVX2 assembly, including keccak_f1600_x4_avx2_asm.S. The measured speedup over the C backend comes from both backends together, since the no-opt build turns off native arithmetic and native Keccak at once.

## Compared with alternatives

Pick it over neon-ntt or PQRV when you want a complete, maintained, formally verified ML-KEM rather than research kernels for one ISA, and over pqm4 when the target is an application-class CPU rather than a Cortex-M4.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (ships its own FIPS-202; you can plug in your own FIPS-202 or randombytes) |
| **Minimum toolchain** | C90 plus stdint.h and 64-bit unsigned long long; native backends need GNU-style assembler support (GCC or Clang) and the matching -march flags |
| **Platforms** | any for the C backend; native backends for AArch64 (Neon, optional SHA-3 extension Keccak), x86-64 (AVX2), RISC-V 64 (RVV), ppc64le (VSX, POWER8+); Armv8.1-M MVE experimental |
| **Thread safety** | not documented; the API has no global mutable state visible in the header and allocates on the stack by default |
| **Drop-in for the baseline** | partial — same keypair/enc/dec structure and byte formats as FIPS 203, but symbol names are namespaced and return codes must be checked (warn_unused_result); the C-only build is the baseline itself |

## Gotchas

- Native backends are off in the shipped mlkem_native_config.h: you must set MLK_CONFIG_USE_NATIVE_BACKEND_ARITH and MLK_CONFIG_USE_NATIVE_BACKEND_FIPS202 (or pass them in CFLAGS) to get the measured speed, and set MLK_CONFIG_CUSTOM_CAPABILITY_FUNC when the build machine differs from the run machine.
- The x86-64 AVX2 assembly does not issue vzeroupper on return (issue #1772, open); maintainers call this deliberate and unmeasured, but callers that run legacy SSE code afterwards on older Intel cores may pay AVX-SSE transition costs.
- Including mlkem_native.h before the sources in a single-unit build silently dropped build-only config options (issue #1919, fixed September 2026); check your build if you vendored an earlier version.
- Benchmark data are rolling CI points: issue #429 showed up to about 18% run-level variance on virtualised x86 EC2 instances, fixed only for c7i by moving it to bare metal; the other EC2 rows (c6i.large, c7a.medium, c6a.large, t4g.small burstable, c7g/c8g/c9g.medium) are still small VMs, although opt and no-opt run back to back on the same instance in one job.

## Known shortcomings

- The baseline is the project's own portable C backend, not pq-crystals' reference directly, and the rows are rolling CI history on shared EC2 VMs (ML-KEM-768 1.90x-3.01x across eight targets, data.js at aad9b74).
- Enricher: bench harness sound (500 samples x 300 iterations, median, shared-secret check, optimised and no-opt builds run back to back on the same instance), but the baseline is the project's own C backend and no-opt disables native arithmetic and native Keccak x4 together; native backends are off in the shipped config and chosen at compile time unless a custom capability function is set; up to 18% variance on virtualised EC2 (#429, fixed only for c7i by moving to metal; other rows are small VMs, t4g.small burstable); open #1772 (no vzeroupper in AVX2 assembly) and #1338 (high stack use).

## Caveats and trade-offs

The only measured comparison found is native backend against the project's own C backend, not against the unmodified pq-crystals/kyber ref or liboqs portable C directly; the C backend is itself an optimised fork of ref, so the gap to the plain reference code is likely larger. The data.js file holds a rolling history, the numbers above are the latest points (commit aad9b74); they move with every main-branch commit. The rendered page https://pq-code-package.github.io/mlkem-native/dev/bench/ is egress-blocked here, the raw gh-pages data.js file was read instead. EC2 rows are VM timings from CI (c7i is bare metal, others are small shared instance types). Compiler and version for the EC2 jobs are not visible in the opened files. No independent third-party run found. A SLOTHY paper (eprint 2022/1303, blocked) has earlier NTT-level results on Cortex-A55/A72 that were not read. [retier] Enricher: no-opt disables native arithmetic and native Keccak x4 together; native backends are off in the shipped config and chosen at compile time; up to 18% variance on virtualised EC2 (#429); open #1772 (no vzeroupper) and #1338 (stack use).

AArch64 and x86-64 assembly is formally proved functionally correct, memory-safe and constant-time with HOL-Light, C code proved memory- and type-safe with CBMC; assembly exists only for AArch64 (Neon), x86-64 (AVX2), plus RISC-V RVV and POWER VSX backends; build is import-the-sources, the repo's Makefile is for development only; ML-KEM only (no ML-DSA).

## Maintenance

Very actively maintained under the Linux Foundation's PQCA (last commit 2026-10-12 per the verified record, tested against the ACVP and Wycheproof ML-KEM vectors), triple-licensed Apache-2.0, ISC or MIT, and shipped as the default ML-KEM in liboqs and in AWS-LC.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** The gh-pages data.js holds paired opt and no-opt rows from the main-branch CI run at commit aad9b74 (2026-10-12), and every ML-KEM-768 cycle count in claimed_speedup matches exactly. The benchmark code is public (test/bench/bench_mlkem.c driven by ./scripts/tests bench --opt=opt|no_opt), flags are in test/mk/config.mk and .github/workflows/bench.yml, the compiler is the flake-locked nixpkgs nixos-26.05 GCC (nix/util.nix native-gcc), and the CPU is fixed by the EC2 instance type, so tier A stands.
- **Verifier notes:** All 24 ML-KEM-768 values for c7i, c7a, Graviton2 and Graviton4 match data.js; across the 8 EC2 targets the C-backend-to-native ratios run from 1.90x (Graviton4 decaps) to 3.01x (c6a encaps), so '1.9x to 3.0x' holds. Shortcomings to record: the baseline is the project's own portable C backend (a C90 fork of pq-crystals ref), not the unmodified ref or another library; the numbers come from rolling CI history on mostly small shared EC2 VMs (only c7i is bare metal); the compiler version is pinned through flake.lock but not printed in the files read.
- **Fields the verifier corrected:** `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-122 (wave 13 seed pass, 2026-10-13); enricher (seed pass, 2026-10-13)
- **Pages the verifier opened:**
  - <https://github.com/pq-code-package/mlkem-native>
  - <https://github.com/pq-code-package/mlkem-native/commits>
  - <https://raw.githubusercontent.com/pq-code-package/mlkem-native/gh-pages/dev/bench/data.js>
  - <https://raw.githubusercontent.com/pq-code-package/mlkem-native/main/.github/workflows/bench.yml>
  - <https://raw.githubusercontent.com/pq-code-package/mlkem-native/main/.github/workflows/bench_ec2_reusable.yml>
  - <https://raw.githubusercontent.com/pq-code-package/mlkem-native/main/.github/actions/bench/action.yml>
  - <https://raw.githubusercontent.com/pq-code-package/mlkem-native/main/test/mk/config.mk>
  - <https://raw.githubusercontent.com/pq-code-package/mlkem-native/main/flake.nix>
  - <https://raw.githubusercontent.com/pq-code-package/mlkem-native/main/nix/util.nix>
  - <https://raw.githubusercontent.com/pq-code-package/mlkem-native/main/test/bench/bench_mlkem.c>
  - <https://raw.githubusercontent.com/pq-code-package/mlkem-native/main/scripts/tests>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/pq-code-package/mlkem-native/main/README.md>
  - <https://raw.githubusercontent.com/pq-code-package/mlkem-native/main/test/bench/bench_mlkem.c>
  - <https://raw.githubusercontent.com/pq-code-package/mlkem-native/main/mlkem/mlkem_native.h>
  - <https://raw.githubusercontent.com/pq-code-package/mlkem-native/main/mlkem/mlkem_native_config.h>
  - <https://raw.githubusercontent.com/pq-code-package/mlkem-native/main/SECURITY.md>
  - <https://raw.githubusercontent.com/pq-code-package/mlkem-native/main/BIBLIOGRAPHY.md>
  - <https://raw.githubusercontent.com/pq-code-package/mlkem-native/main/API-CONVENTIONS.md>
  - <https://raw.githubusercontent.com/pq-code-package/mlkem-native/main/test/mk/config.mk>
  - <https://raw.githubusercontent.com/pq-code-package/mlkem-native/main/test/mk/components.mk>
  - <https://raw.githubusercontent.com/pq-code-package/mlkem-native/main/mlkem/src/native/x86_64/meta.h>
  - <https://raw.githubusercontent.com/pq-code-package/mlkem-native/main/.github/workflows/bench.yml>
  - <https://raw.githubusercontent.com/pq-code-package/mlkem-native/main/.github/workflows/bench_ec2_reusable.yml>
  - <https://raw.githubusercontent.com/pq-code-package/mlkem-native/main/.github/actions/bench/action.yml>
  - <https://github.com/pq-code-package/mlkem-native/tree/main/mlkem/src/fips202/native/x86_64/src>
  - <https://github.com/pq-code-package/mlkem-native/issues?q=is%3Aissue+label%3Abug>
  - <https://github.com/pq-code-package/mlkem-native/issues?q=is%3Aissue+performance>
  - <https://github.com/pq-code-package/mlkem-native/issues/1772>
  - <https://github.com/pq-code-package/mlkem-native/issues/429>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/pq-code-package/mlkem-native`) · [data/wave13/enrich/raw/github_com_pq_code_package_mlkem_native.json](../../../data/wave13/enrich/raw/github_com_pq_code_package_mlkem_native.json) (enrichment confidence 0.85)

</details>
