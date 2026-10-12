# CryptOpt

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Hand-written assembly kernels](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `TypeScript (emits x86-64 assembly)` · `Apache-2.0` · 🟡 stale

> Randomized-search optimizer emitting formally verified x86-64 assembly for finite-field multiply/square; beats GCC 12 and Clang 15 on Fiat C.

| | |
|---|---|
| **Beats** | GCC 12.1.0 and Clang 15.0.6 compiling Fiat Cryptography's generated C at -O3 -march=native -mtune=native; also hand-optimized assembly (OpenSSL fe-51/fe-64, libsecp256k1 asm, HACL\* fe-64) |
| **Claimed result** | Paper abstract: mean speedup 1.74 over GCC 12.1.0 and 1.40 over Clang 15.0.6 across ten x86-64 platforms; the 1.04x over libsecp256k1's hand-optimized assembly is the verified Fiat path (Table 5: 527k vs 547k cycles; Opt 528k), under 1% over libsecp256k1's C and slower than that C on all four AMD machines (Table 7); Table 6 'Final' multiply vs the better compiler: 1.00x P-521, 1.01x Curve448, 2.26x SIKEp434 |
| **Workload** | Multiply and square in nine prime fields (Curve25519, NIST P-224/P-256/P-384/P-521, secp256k1, Curve448, SIKEp434 field, Poly1305) on ten x86-64 CPUs, plus scalar multiplication through SUPERCOP. |
| **Metric** | latency (CPU cycles per finite-field multiply and square) |
| **Hardware** | Ten x86-64 machines: AMD Ryzen Threadripper 1900X (Zen 1), Ryzen 7 5800X and Ryzen 9 5950X (Zen 3), Ryzen 9 7950X (Zen 4); Intel Core i7-6770HQ, i7-10710U, i9-10900K, i7-11700KF, i9-12900KF, i9-13900KF (performance cores only). |
| **Compiler and flags** | Baseline C built with GCC 12.1.0 and Clang 15.0.6, highest optimization level with -march=native -mtune=native -O3; CPU frequency fixed, boosting disabled, performance governor; Ubuntu Server 22.04.1. |
| **Adoption** | 73 stars, 14 forks; PLDI 2023 Distinguished Paper Award and GECCO 2023 Humies Gold award (university news pages, snippet only); verified assembly published in fiat-crypto's fiat-amd64 directory and Curve25519 code integrated into BoringSSL (per the repo README) |
| **Last commit** | 2023-11-16 |
| **Links** | [repository](https://github.com/0xADE1A1DE/CryptOpt) · [benchmark](https://raw.githubusercontent.com/0xADE1A1DE/CryptOpt/HEAD/papers/KuepperEWGCSTCCGWY23-PLDI23.pdf) |

## Verdict

PLDI 2023 paper (checked-in PDF and full version): on ten x86-64 machines (Zen 1 to Zen 4, Skylake-H to Raptor Lake P-cores, fixed frequency, no boost, Ubuntu 22.04.1), CryptOpt's per-machine-optimized multiply/square ran a mean 1.74x faster than GCC 12.1.0 and 1.40x faster than Clang 15.0.6 compiling Fiat's C at -O3 -march=native -mtune=native; against the better compiler per machine, multiply geometric means are 1.00x (P-521) to 2.26x (SIKEp434), with P-256 1.74x, secp256k1 1.83x and Curve25519 1.17x (Table 6 'Final', full version). In SUPERCOP scalar multiplication it ties OpenSSL's hand-written fe-51/fe-64 Curve25519 asm and is 1.04x faster than libsecp256k1's hand asm (547k vs 527k cycles geometric mean) but under 1% faster than libsecp256k1's C.

## Use it when

- You ship Fiat Cryptography C field arithmetic on x86-64 Linux and want 1.2-2.3x faster multiply/square without giving up machine-checked correctness: drop in the pre-generated fiat-amd64 .asm for P-224, P-256, P-384, secp256k1, SIKEp434 (p434), Curve25519 or Poly1305.
- NIST P-256/P-384 or secp256k1 field ops dominate a verifier or signer on recent Intel cores, where the paper's Table 7 shows CryptOpt-based secp256k1 scalar multiplication 4-5% faster than libsecp256k1's own C and asm on 12th/13th-gen Core.
- You maintain a cryptographic library and want per-microarchitecture tuned straight-line kernels without hand-writing assembly: run the optimizer (20-40 machine hours for 18 primitives) on the target CPU and keep the best of several seeds.
- Research or evaluation of verified compilation and search-based superoptimization for code of hundreds of instructions, where STOKE failed in the paper's comparison.

## Skip it when

- Curve448 and P-521: against the better of GCC and Clang the best CryptOpt multiply is only 1.01x and 1.00x (Table 6 'Final' geometric means in the full paper), and 5-8% slower on several machines.
- Whole-protocol Curve25519 speed: in SUPERCOP scalar multiplication OpenSSL fe-64+CryptOpt (461k cycles geometric mean) is slightly slower than OpenSSL's hand fe-64 (455k) and HACL\* fe-64 (452k), and sandy2x is fastest on Zen 3/4; on AMD the verified secp256k1 variant is 1-5% slower than libsecp256k1's portable C.
- Targets without BMI2 and ADX (pre-Broadwell Intel, some low-end or virtualized CPUs; issue #143 'x86_64 without ADX' is open), Windows x64 ABI, AArch64 or any non-x86-64 platform.
- Kernel or other no-red-zone contexts and code that needs unwind info: default output spills below rsp, treats rbp as a scratch register (framePointer omit) and emits no .cfi directives (issue #166 open); regenerate with --framePointer save or constant and --no-redzone if needed.
- Teams wanting a maintained tool: last commit 2023-11-16, open bugs such as 'tried to spill OF' (#204) and runs that regress after a threshold (#211).

## How it is fast

Genetic-improvement style random program search with a Bet-and-Run schedule (20 bets of 1,000 mutations, then 180,000 mutations on the best): mutations reorder independent operations and change instruction and register choices (including spill decisions over the whole function, not a peephole window), and every candidate is assembled in memory with AssemblyLine and timed against the incumbent with MeasureSuite (randomly interleaved batches calibrated to about 10,000 cycles, median of 31). Generated code leans on BMI2 mulx and the ADX dual carry chains adcx/adox, uses rbp as a general register and spills into the red zone, which compilers rarely schedule this well for multi-limb arithmetic. Gains are largest where register pressure forces spills (P-224/256/384, secp256k1, SIKEp434) and small for spill-free fields (Curve25519, Poly1305).

## Compared with alternatives

Pick CryptOpt over Constantine's inline-asm field arithmetic or CRYPTOGAMS perlasm when you need machine-checked correctness of x86-64 field multiply/square for Fiat-supported primes (P-224/256/384, secp256k1, Curve25519, Poly1305, p434) and can tune per CPU; Constantine covers pairing-friendly curves with portable generated asm, and CRYPTOGAMS covers many architectures and symmetric primitives that CryptOpt does not.

## Integration

| | |
|---|---|
| **Form** | source-drop (generated NASM .asm files); the optimizer itself is a Node.js CLI |
| **Dependencies** | generated asm: none; optimizer: Linux x86-64, Node.js 20.5.1 (downloaded by the Makefile), the AssemblyLine and MeasureSuite C libraries, bundled Fiat Cryptography binaries, perf_event_paranoid=1 for PMC cycle counting (else RDTSCP); Docker image recommended |
| **Minimum toolchain** | NASM-syntax assembler for the .asm files; CPU with BMI2 and ADX (Intel Broadwell/Skylake or later, AMD Zen or later) |
| **Platforms** | x86-64 only, Linux System V ABI (generated files say so); optimizer runs on Linux x86-64 |
| **Thread safety** | not documented; the generated functions are straight-line code that touch only their argument arrays and their own stack red zone, so they keep no shared state |
| **Drop-in for the baseline** | partial: same symbol names and signatures as Fiat Cryptography's C for the listed fields, but x86-64 System V only, needs ADX/BMI2, and libsecp256k1-bridge output is not formally verified |

## Gotchas

- Each speedup in Table 4 is code optimized on and for the machine it was timed on (best of three runs), measured with the same MeasureSuite harness that drove the search; in the independent SUPERCOP scalar-multiplication runs (Table 5) the gains shrink to about +1% to -1% for Curve25519 and +0.6% over libsecp256k1's C. Cross-platform runs (Table 6) show code tuned on one CPU can be beaten by code tuned on another, so pick files by the 10-machine geometric mean listed in generated/fiat-amd64/Readme.md, not by the 'ratio' in the file name, which is the optimizing machine's in-loop ratio against clang-15.
- Record correction: the 1.04x over libsecp256k1's hand assembly comes from the formally verified Fiat path too. Table 5 gives libsecp256k1+CryptOpt (Fiat, verified) 527k and libsecp256k1+CryptOpt (Opt, unverified libsecp256k1-derived) 528k cycles against 547k for the hand asm, although the paper's prose says the Opt variant is faster. Both variants are under 1% faster than libsecp256k1's own C (530k) on average and slower than that C on all four AMD machines (Table 7).
- The paper's text says CryptOpt-based Curve25519 is fastest on i7-11700KF, i9-12900KF and i9-13900KF, but its own Table 7 shows HACL\* fe-64 faster on all three (426k, 367k, 366k against 446k, 387k, 392k cycles); the claim holds only with HACL\* excluded.
- Correctness proof covers functional equivalence to Fiat IR under calling-convention and memory-layout preconditions; constant-time behaviour is argued from straight-line code with no secret-dependent branches or addresses, not proved. Output built with the bitcoin-core or manual bridges runs with --no-proof by default.

## Known shortcomings

- Two big fields slightly slower than GCC (Curve448 and P-521 mul 0.98/0.97); scalar-multiplication gain under 1% over libsecp256k1 C and on par with OpenSSL asm; Zenodo artifact blocked; distinguished-paper and Humies awards known from snippets only.
- Enricher: the 1.04x over libsecp256k1's hand-written assembly comes from the verified Fiat path (527k vs 547k cycles; Opt 528k), not the unverified path as the paper prose says (Table 5); under 1% over libsecp256k1's C and slower than that C on all four AMD machines (Table 7); Table 7 shows HACL\* fe-64 faster than CryptOpt Curve25519 on 11th-13th gen Intel despite the prose; against the better compiler the Table 6 'Final' multiply means 1.00x P-521, 1.01x Curve448 and 2.26x SIKEp434; the generated assembly needs ADX/BMI2, is System V only, uses the red zone, clobbers rbp and has no .cfi directives. Lead: mit-plv/fiat-crypto is not catalogued under its own id.

## Caveats and trade-offs

The assembly is machine-generated by random program search, not hand-written; it sits here because it is compared against both compilers and hand-written assembly. Each platform's numbers come from code optimized on and for that same platform (best of three optimization runs per primitive per machine), against generic compiler output. Gains vary: Curve448 and P-521 multiply are slightly slower than GCC (0.98 and 0.97); gains are modest for Curve25519 and Poly1305. The baseline is Fiat Cryptography's generated C, not each library's own C. In whole scalar multiplication through SUPERCOP (Table 5, geometric-mean cycles) CryptOpt-enhanced code is on par with OpenSSL fe-51 (524k vs 530k) and fe-64 (461k vs 455k) assembly and slower than HACL\* fe-64 (452k); for secp256k1, libsecp256k1's hand asm (547k) is itself slower than its portable C (530k), so CryptOpt's 527k (Fiat, verified) and 528k (Opt) are under 1 percent faster than libsecp256k1's C (derived from page data), and the 1.04 speedup over hand asm comes from the libsecp256k1-derived path that the equivalence checker cannot verify. The Zenodo artifact was not opened (blocked here); the repo README repeats the Table 4 means. Last commit 2023-11-16. [retier] Generated assembly needs ADX/BMI2, System V ABI only, uses the red zone, clobbers rbp, no .cfi directives; HACL\* fe-64 is faster than CryptOpt Curve25519 on 11th-13th gen Intel in Table 7 despite the prose

x86-64 only; the assembly is found by randomized search per microarchitecture (20 to 40 wall-clock hours per machine for the 18 primitives) and must be regenerated for new CPUs; correctness is checked by an equivalence checker only when the input is Fiat IR, the libsecp256k1 variant is unverified; fixed-size field arithmetic, not a general library.

## Maintenance

Stale since 2023-11-16 (73 stars, 6 open issues) but Apache-2.0, and the useful part, the pre-generated verified .asm files, is a static source drop that also ships in Fiat Cryptography and BoringSSL, so maintenance of the optimizer matters only if you regenerate for new CPUs.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** Peer-reviewed PLDI 2023 paper (checked-in PDF) states GCC 12.1.0 and Clang 15.0.6 with -march=native -mtune=native -O3, lists all ten CPU models (Table 1), fixed frequency/no boost/performance governor, and points to a public artifact with reproduction instructions (Zenodo DOI 10.5281/zenodo.7710435, not opened because zenodo is blocked) alongside the optimizer source in the repo; Table 4 and the abstract carry the claimed numbers.
- **Verifier notes:** Abstract (mean 1.74 over GCC 12.1.0, 1.40 over Clang 15.0.6, 1.04 over libsecp256k1 hand asm) and Table 4 multiply means match the record exactly. Metadata on github.com: Apache-2.0, 73 stars, 14 forks, not archived or a fork, default branch main, last commit 2023-11-16 (stale). Main shortcoming: whole-scalar-multiplication gains are within about 1 percent of existing hand asm or C, and two large fields are slightly slower than GCC.
- **Fields the verifier corrected:** `stars_or_usage`, `caveats`, `claimed_speedup`
- **Shortcomings recorded by:** verifier batch-36 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/0xADE1A1DE/CryptOpt>
  - <https://github.com/0xADE1A1DE/CryptOpt/commits/main>
  - <https://raw.githubusercontent.com/0xADE1A1DE/CryptOpt/HEAD/Readme.md>
  - <https://raw.githubusercontent.com/0xADE1A1DE/CryptOpt/HEAD/papers/KuepperEWGCSTCCGWY23-PLDI23.pdf>
  - <https://raw.githubusercontent.com/0xADE1A1DE/CryptOpt/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/0xADE1A1DE/CryptOpt/HEAD/LICENSE>
  - <https://github.com/dderjoel/CryptOpt-Scripts>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/0xADE1A1DE/CryptOpt/HEAD/Readme.md>
  - <https://raw.githubusercontent.com/0xADE1A1DE/CryptOpt/HEAD/papers/KuepperEWGCSTCCGWY23-PLDI23.pdf>
  - <https://raw.githubusercontent.com/0xADE1A1DE/CryptOpt/HEAD/papers/KuepperEWGCSTCCGWY23-PLDI23-full.pdf>
  - <https://raw.githubusercontent.com/0xADE1A1DE/CryptOpt/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/0xADE1A1DE/CryptOpt/HEAD/package.json>
  - <https://raw.githubusercontent.com/0xADE1A1DE/CryptOpt/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/0xADE1A1DE/CryptOpt/HEAD/Makefile>
  - <https://raw.githubusercontent.com/0xADE1A1DE/CryptOpt/HEAD/INSTALL.md>
  - <https://raw.githubusercontent.com/0xADE1A1DE/CryptOpt/HEAD/First_Steps.md>
  - <https://raw.githubusercontent.com/0xADE1A1DE/CryptOpt/HEAD/generated/fiat-amd64/Readme.md>
  - <https://raw.githubusercontent.com/0xADE1A1DE/CryptOpt/HEAD/generated/fiat-amd64/fiat_p256_mul/seed0000000327800118_ratio16285.asm>
  - <https://github.com/0xADE1A1DE/CryptOpt/tree/main/generated/fiat-amd64>
  - <https://github.com/0xADE1A1DE/CryptOpt/issues?q=is%3Aissue>
  - <https://github.com/0xADE1A1DE/CryptOpt/issues/211>
  - <https://github.com/0xADE1A1DE/CryptOpt/issues/144>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/0xade1a1de/cryptopt`) · [data/wave13/enrich/raw/github_com_0xade1a1de_cryptopt.json](../../../data/wave13/enrich/raw/github_com_0xade1a1de_cryptopt.json) (enrichment confidence 0.82)

</details>
