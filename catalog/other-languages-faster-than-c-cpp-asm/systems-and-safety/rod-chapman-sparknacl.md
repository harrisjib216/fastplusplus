# SPARKNaCl

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Ada/SPARK` · `BSD-3-Clause` · 🟢 active

> SPARK/Ada re-implementation of TweetNaCl with proven absence of run-time errors; the author reports Ed25519 Sign about 3x faster than TweetNaCl C on a RISC-V board.

| | |
|---|---|
| **Beats** | TweetNaCl (C), compiled into the same binary with the same GNAT compiler at the same -O level |
| **Claimed result** | Snippet only (two WebSearch result summaries; no page opened): in the February 2021 'Performance analysis and tuning of SPARKNaCl' post, one Ed25519 Sign of a 256-byte message on a HiFive1 Rev B took SPARK 198.03 vs C TweetNaCl 241.83 million cycles at -O0, 98.03 vs 97.65 at -O1 and 93.86 vs 84.99 at -O2 (SPARK slower at -O1 and -O2). After tuning, 'Doubling the Performance of SPARKNaCl (again...)' reports SPARK at 181.74 (-O0), 69.96 (-O1) and 57.82 then 34.94 (-O2) million cycles. A slide deck summary gives final SPARK 24.37 million cycles at -O2 against 84.99 for the original TweetNaCl C and 51.00 for a revised C version, i.e. about 3.5x vs original and about 2.1x vs the revised C (derived from snippet data). The FOSDEM 2022 abstract claims SPARKNaCl outperforms TweetNaCl on Sign by a factor of 3 at all optimization levels. README itself gives no numbers. |
| **Workload** | CPU cycles for one Ed25519 Sign operation on a 256-byte message on a SiFive HiFive1 Revision B (32-bit RISC-V); also Curve25519 and SHA512 analysed. |
| **Metric** | other |
| **Hardware** | SiFive HiFive1 Revision B board (FE310 32-bit RISC-V SoC, code built for rv32im), cycles read from the mcycle CSR |
| **Compiler and flags** | GNAT Community 2020/2021 riscv64-elf cross compiler. Since commit e06da81 (2021-02-17) perf/tsign.mk builds the SPARK library with -march=rv32imc plus -falign-functions/-falign-jumps/-falign-loops=4 (and -gnatn at O1 and above) while the TweetNaCl C side gets -march=rv32im with no alignment flags; only the -O level is shared. |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | yes |
| **Why it wins** | Per search snippets only ('formal is fast'): the proof of absence of run-time errors lets the code run without run-time checks; README keeps TweetNaCl's constant-time algorithms. |
| **Adoption** | 139 stars, 14 forks; published in the Alire package index |
| **Last commit** | 2026-03-26 |
| **Links** | [repository](https://github.com/rod-chapman/SPARKNaCl) · [benchmark](https://github.com/rod-chapman/SPARKNaCl) |

## Verdict

Per AdaCore blog and slide snippets only (blog.adacore.com and www.adacore.com unreachable here), one Ed25519 Sign of a 256-byte message on a HiFive1 Rev B (FE310 RISC-V, GNAT Community GCC 8/10 cross compiler, mcycle) went from SPARK roughly level with TweetNaCl at -O1 and behind at -O2 in February 2021 (93.86 vs 84.99 million cycles at -O2) to about 24.37 million cycles at -O2 after tuning, versus 84.99 million for the original TweetNaCl and 51.00 million for a C version patched with some of the same tricks. That is about 3.5x and 2.1x (derived from snippet data). The committed harness compares the two in one image and checks the signatures match, but it builds them with different -march and alignment flags.

## Use it when

- Bare-metal or safety-critical embedded targets (zero-footprint runtime, no heap, no OS) that need Ed25519, X25519 or NaCl box/secretbox with a machine-checked proof of absence of run-time errors.
- Ada or SPARK code bases that want NaCl primitives through Alire, with readable contract-annotated sources for assurance reviews.
- Small 32-bit cores, especially RISC-V, where TweetNaCl is the current choice and its 64-bit-limb multiply is costly; the author's blog posts report roughly 2x to 3.5x fewer cycles for Sign (snippet-only numbers).
- Certification or audit settings where proven type safety and tracked worst-case stack usage (GNATstack reported 5648 bytes for Sign on 32-bit RISC-V in 2020) matter more than peak throughput.

## Skip it when

- Server or desktop throughput on x86-64 or ARM64: there is no SIMD or assembly, and it has only ever been compared against TweetNaCl, a deliberately compact C library, never against speed-oriented C crypto libraries.
- Calling from C or C++: a C API wrapper is still on the README's to-do list.
- When you need reproducible published numbers: the cycle tables live only in AdaCore blog posts and slides, and the README (June 2022) says the latest '\*' results are still to be documented.
- -O0 builds: the README says the 2022 '\*' rewrite is noticeably slower at -O0, and results swing strongly with the optimisation level.
- When constant-time behaviour must be machine-checked: the README claims proof of type safety and some correctness properties; constant-time behaviour is kept by construction, not proven for the whole library.

## How it is fast

The proof bounds every field-element limb (Normal_GF limbs are 0..65535), so the code can be built with -gnatp (all run-time checks off) and the arithmetic can be rewritten safely. GF(2^255-19) multiplication is a fully unrolled product-scanning multiply: each partial product is a 16x16-bit limb product in a 32-bit type (one 32-bit multiply on rv32im), the 38x reduction and the first carry pass are fused into the digit loop, and there is a dedicated Square and a hand-unrolled Inv_25519 (2023 commits). The TweetNaCl C baseline instead multiplies 64-bit limbs and then runs two separate carry passes. The gain therefore comes from different field arithmetic that the proofs made safe to write, not from Ada code generation.

## Compared with alternatives

Pick SPARKNaCl when you need proven-safe public-key crypto (Ed25519, X25519) on bare-metal or Ada targets. Pick tachyon-rs for AES-GCM, ChaCha20-Poly1305 or hashing throughput on desktop or mobile CPUs, and Usuba for bitsliced symmetric ciphers on SIMD hardware; neither offers a type-safety proof or a zero-footprint runtime.

## Integration

| | |
|---|---|
| **Form** | static lib (GPR library project or Alire crate 'sparknacl', 4.0.0 in alire.toml; static, static-pic or relocatable) |
| **Dependencies** | none at run time (works on the GNAT zero-footprint runtime); proving needs GNATprove ^14.1.1 with Z3, CVC5 and Alt-Ergo per sparknacl.gpr |
| **Minimum toolchain** | GNAT &gt;= 14.2.1 per alire.toml (release 3.0.0 supported GNAT Community 2020/2021 and FSF GNAT 11.2.1+); performance tests need a riscv64-elf GNAT cross compiler and Ada_Drivers_Library |
| **Platforms** | any GNAT target; performance tested on SiFive HiFive1 Rev B (FE310, 32-bit RISC-V); tests reproduced on macOS, Linux and Windows |
| **Thread safety** | the packages are declared Pure (no package-level state), so calls should be reentrant; thread safety is not otherwise documented |
| **Drop-in for the baseline** | partial: same NaCl/TweetNaCl functions and identical outputs (the NaCl test suite is re-implemented and passes), but as an Ada API rather than the crypto_\* C API; no C wrapper yet |

## Gotchas

- Harness flag asymmetry: since commit e06da81 (2021-02-17, 'Switch to RV32IMC_A4 by default'), perf/tsign.mk sets SPARKNACL_TARGET_ARCH=rv32imc_a4. That makes sparknacl.gpr compile the SPARK library with -march=rv32imc plus -falign-functions/-jumps/-loops/-labels=4, while perf.gpr compiles perf/tweetnacl.c with -march=rv32im ('No compressed instructions for C') and no alignment flags. At -O1 and above the library also gets -gnatn cross-unit inlining. The record's 'same flags' description therefore holds only for the -O level, not the ISA or code alignment. Per a search snippet, the author had found the E31 core pays a penalty for branches to misaligned compressed code. The effect on the published Sign numbers is unknown.
- Algorithm asymmetry behind the numbers: SPARKNaCl multiplies 16-bit limbs as 32-bit products with fused reduction and carry, and adds a dedicated Square. perf/tweetnacl.c (already patched with the WireGuard carry and an unrolled inner loop 'as per SPARKNaCl') still multiplies i64 limbs, a multi-instruction operation on rv32im, then runs two car25519 passes. The same rewrite is possible in C, so this is library versus library.
- perf/tsign.adb times one Sign per side, single run, from code executing out of SPI flash through the instruction cache. The SPARK Sign runs right after SPARKNaCl.Sign.Keypair, which exercises the same SHA-512 and scalar-multiply code, while TweetNaCl's crypto_sign runs cold. This is probably small next to tens of millions of cycles, but it is not controlled.
- Proof covers the source, not the compiled code: GNAT 14 miscompiled SHA-256 at -O2/-O3 on x86-64 (issue #37, March 2025, fixed with -fno-tree-vrp). sparknacl.gpr adds -fno-tree-vrp only when SPARKNACL_TARGET_ARCH is 'unspecified', so the rv32im, rv32imc and rv32imc_a4 builds do not get the workaround. Run the test suite at your own optimisation level.

## Known shortcomings

- Cycle counts known from search snippets only (AdaCore blog blocked: 24.37 vs 51.00 Mcycles at -O2 against revised C, 84.99 against the original TweetNaCl); the gain comes from the rewritten GF arithmetic (32-bit products, fewer carries), not SPARK codegen; both sides built with checks off (-gnatp); the harness perf/tsign.adb is public.
- Harness flaw: since commit e06da81 (2021-02-17) perf/tsign.mk builds the SPARK library with -march=rv32imc plus -falign-\*=4 (and -gnatn at O1 and above) while the TweetNaCl C side gets -march=rv32im with no alignment flags, so only the -O level is shared. The two sides use different field arithmetic (32-bit limb products versus i64 limbs); one cold run per side, with SPARK running after Keypair has warmed its code. GNAT 14 -O2 miscompiles SHA-256 (issue #37) and the -fno-tree-vrp workaround applies only when TARGET_ARCH is unspecified. The cycle numbers remain snippet-only (www.adacore.com ENOTFOUND).

## Caveats and trade-offs

Numbers are snippet-only: blog.adacore.com, www.adacore.com and www.slideshare.net returned ENOTFOUND here and archive.fosdem.org was EGRESS_BLOCKED for the search agent, so no cycle table was seen; a verifier with access should read 'Performance analysis and tuning of SPARKNaCl', 'Doubling the Performance of SPARKNaCl (again...)', 'SPARKNaCl with GNAT and SPARK Community 2021' and the FOSDEM 2022 talk. The win is not a language-level codegen effect: both sides run with run-time checks off (-gnatp), and the speedup comes from reworked field arithmetic that the SPARK proofs made safe (Normal_GF limbs bounded to 0..65535, '\*' rewritten as a product-scanning multiply on 32-bit limb products U32NL with the carry folded in, fewer carry passes, loop fusion in '+' and '-'), while the C baseline in perf/tweetnacl.c still multiplies i64 limbs (costly on rv32im) followed by two car25519 passes, although it has been given the WireGuard carry and an unrolled inner loop 'as per SPARKNaCl'. The same restructuring could be written in C, so this is a library-versus-library result. Results swing strongly with -O level (SPARK was behind at -O1/-O2 before tuning; README notes the new '\*' is slower at -O0). Not an x86 or -O3 measurement; only one embedded 32-bit RISC-V board. README says the latest results are still to be documented. [retier] The two sides use different field arithmetic (32-bit limb products versus i64 limbs); one cold run per side, with SPARK running after Keypair has warmed its code. GNAT 14 -O2 miscompiles SHA-256 (issue #37) and the -fno-tree-vrp workaround applies only when TARGET_ARCH is unspecified.

Full SPARK proof of absence of run-time exceptions (needs CVC4 and Z3), TweetNaCl-compatible API, readable constant-time code; results are for a small RISC-V core and do not transfer to x86.

## Maintenance

Maintained: proof-maintenance commits in March 2026 for GNATprove updates and an SHA-384 contribution in 2025, with three open issues. It is BSD-3-Clause, small and Alire-packaged, so it is easy to adopt in Ada; performance claims rest on 2021-2022 blog posts about older code.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The repo carries a public harness that times SPARKNaCl.Sign against TweetNaCl's crypto_sign in the same binary with mcycle and checks the signatures match (perf/tsign.adb, perf/tweetnacl.c, perf/perf.gpr, perf/tsign.mk), and the compiler, flags and board are known, but the cycle counts exist only in AdaCore blog posts, a FOSDEM 2022 abstract and a slide deck that are all unreachable here (blog.adacore.com, www.adacore.com and www.slideshare.net return ENOTFOUND; archive.fosdem.org was blocked for the search agent), so the numbers are snippet-only and stay at C per the wave-14 snippet rule.
- **Verifier notes:** Keep at C with the asymmetric-algorithm shortcoming: harness, flags and board are public (perf/tsign.adb compares SPARKNaCl.Sign with TweetNaCl crypto_sign in one image and checks SM1 = SM2), but cycle counts are snippet-only and the win comes from rewritten GF arithmetic rather than from SPARK codegen; language_level_claim and same_algorithm corrected to false. A paper-access retier could reach A for the harness if the blog tables are read, still capped by the different-algorithm caveat.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`, `stars_or_usage`
- **Shortcomings recorded by:** verifier batch-30 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/rod-chapman/SPARKNaCl/HEAD/README.md>
  - <https://github.com/rod-chapman/SPARKNaCl>
  - <https://github.com/rod-chapman/SPARKNaCl/commits>
  - <https://github.com/rod-chapman/SPARKNaCl/tree/master/perf>
  - <https://raw.githubusercontent.com/rod-chapman/SPARKNaCl/HEAD/perf/tsign.adb>
  - <https://raw.githubusercontent.com/rod-chapman/SPARKNaCl/HEAD/perf/tsign.gpr>
  - <https://raw.githubusercontent.com/rod-chapman/SPARKNaCl/HEAD/perf/tsign.mk>
  - <https://raw.githubusercontent.com/rod-chapman/SPARKNaCl/HEAD/perf/perf.gpr>
  - <https://raw.githubusercontent.com/rod-chapman/SPARKNaCl/HEAD/perf/tweetcount.c>
  - <https://raw.githubusercontent.com/rod-chapman/SPARKNaCl/HEAD/perf/tweetnacl.c>
  - <https://raw.githubusercontent.com/rod-chapman/SPARKNaCl/HEAD/src/sparknacl.adb>
  - <https://raw.githubusercontent.com/rod-chapman/SPARKNaCl/HEAD/src/sparknacl.ads>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/rod-chapman/SPARKNaCl/HEAD/README.md>
  - <https://raw.githubusercontent.com/rod-chapman/SPARKNaCl/HEAD/alire.toml>
  - <https://raw.githubusercontent.com/rod-chapman/SPARKNaCl/HEAD/sparknacl.gpr>
  - <https://raw.githubusercontent.com/rod-chapman/SPARKNaCl/HEAD/perf/tsign.adb>
  - <https://raw.githubusercontent.com/rod-chapman/SPARKNaCl/HEAD/perf/perf.gpr>
  - <https://raw.githubusercontent.com/rod-chapman/SPARKNaCl/HEAD/perf/tsign.mk>
  - <https://raw.githubusercontent.com/rod-chapman/SPARKNaCl/HEAD/perf/tsign.gpr>
  - <https://raw.githubusercontent.com/rod-chapman/SPARKNaCl/HEAD/perf/tweetnacl.c>
  - <https://raw.githubusercontent.com/rod-chapman/SPARKNaCl/HEAD/src/sparknacl.ads>
  - <https://raw.githubusercontent.com/rod-chapman/SPARKNaCl/HEAD/src/sparknacl.adb>
  - <https://raw.githubusercontent.com/rod-chapman/SPARKNaCl/HEAD/src/sparknacl-sign.ads>
  - <https://raw.githubusercontent.com/rod-chapman/SPARKNaCl/HEAD/src/sparknacl-sign.adb>
  - <https://raw.githubusercontent.com/rod-chapman/SPARKNaCl/HEAD/src/sparknacl-car.ads>
  - <https://raw.githubusercontent.com/rod-chapman/SPARKNaCl/HEAD/src/sparknacl-car.adb>
  - <https://github.com/rod-chapman/SPARKNaCl/tree/master/perf>
  - <https://github.com/rod-chapman/SPARKNaCl/commits>
  - <https://github.com/rod-chapman/SPARKNaCl/commits/master/perf/tsign.mk>
  - <https://github.com/rod-chapman/SPARKNaCl/issues?q=is%3Aissue>
  - <https://github.com/rod-chapman/SPARKNaCl/issues/37>
  - https://www.adacore.com/blog/doubling-the-performance-of-sparknacl-again (ENOTFOUND)
  - WebSearch snippets: blog.adacore.com 'Doubling the Performance of SPARKNaCl (again...)', 'Performance analysis and tuning of SPARKNaCl', 'SPARKNaCl: two years of optimizing crypto code in SPARK (and counting)', archive.fosdem.org 2022 ada_sparknacl abstract
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/rod-chapman/sparknacl`) · [data/wave14/enrich/raw/github_com_rod_chapman_sparknacl.json](../../../data/wave14/enrich/raw/github_com_rod_chapman_sparknacl.json) (enrichment confidence 0.5)

</details>
