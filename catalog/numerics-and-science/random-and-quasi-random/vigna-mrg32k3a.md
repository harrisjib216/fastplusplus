# MRG32k3a branchless implementation (Vigna)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Random and quasi-random numbers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C (with Java version)` · `CC0-1.0` · 🟢 active

> Branchless 64-bit-integer MRG32k3a in C and Java, about 4x faster per double than L'Ecuyer's reference code, same stream.

| | |
|---|---|
| **Beats** | L'Ecuyer's reference double-based MRG32k3a.c (also the equivalent 64-bit integer implementation) |
| **Claimed result** | Header comment: double-based reference about 17.5 ns per double, equivalent 64-bit integer implementation about 7.9 ns, this implementation about 4.1 ns (about 4.3x and 1.9x faster, derived from page data). README: 'roughly four times faster than the double-based implementation and two times faster than the trivial 64-bit integer implementation'. |
| **Workload** | Time to emit one double in (0,1) from MRG32k3a using the author's standard PRNG timing harness; output stream is identical to the original when seeded through MRG32k3a_init6(). |
| **Metric** | latency |
| **Hardware** | Intel Core i7-7700 @ 3.60GHz |
| **Compiler and flags** | gcc 9.2.1 with the author's standard harness; optimisation flags not stated |
| **Adoption** | 21 stars |
| **Last commit** | 2026-06-09 |
| **Links** | [repository](https://github.com/vigna/MRG32k3a) · [benchmark](https://raw.githubusercontent.com/vigna/MRG32k3a/HEAD/MRG32k3a.h) |

## Verdict

The author's header comment reports, on an Intel Core i7-7700 @3.60GHz with gcc 9.2.1 and his own harness (prng.di.unimi.it/harness.c; flags not stated), about 17.5 ns per double for L'Ecuyer's double-based MRG32k3a.c, 7.9 ns for a straightforward 64-bit integer version and 4.1 ns for this code (about 4.3x and 1.9x, derived from page data). A Python re-implementation of both update rules run in this session produced identical outputs for 201 seeds x 2000 draws (first value 0.12701112204657714 for seed 12345 x6), which supports the identical-stream claim.

## Use it when

- You need MRG32k3a specifically, for example to reproduce results from codes or papers that use L'Ecuyer's generator, and want its scalar draws about 4x cheaper than MRG32k3a.c (17.5 ns to 4.1 ns per double on the author's i7-7700).
- Monte Carlo or discrete-event simulation in C or C++ that draws one double at a time in (0,1) and must use L'Ecuyer's published generator.
- Java simulations that use SSJ's MRG32k3a and want a faster single-stream nextDouble (header Javadoc: 21.6 ns SSJ double-based, 13.6 ns SSJ long-based, 5.4 ns this, JMH on i7-7700).
- Code bases that need a public-domain (CC0) generator they can paste in: two C files or one Java file.

## Skip it when

- Multiple independent streams or substreams (jump-ahead): not implemented; the header points to SSJ's MRG32k3aL for that.
- Batch or vectorized generation: the README itself says Intel MKL's vectorized MRG32k3a is faster for batches.
- When you do not need MRG32k3a in particular: modern 64-bit generators in the same category (xoshiro, PCG, Philox) are cheaper per bit and produce 64 bits instead of one 32-bit-resolution double.
- Multithreaded C code: the C version keeps its state in six global variables with no per-thread instance.
- Integer or 64-bit output: the only output is a double with roughly 32 bits of resolution (multiples of 1/(m1+1)).

## How it is fast

It works on int64_t instead of doubles and removes all three data-dependent branches of the reference code. The two negative-residual fixes go away by adding the constant m\*a13 (m\*a23) before the % so the operand is always nonnegative; modulo by a constant compiles to multiply-and-shift. The combination step's 'if p1 &lt;= p2 add m1' becomes the mask m1 \* ((r - 1) &gt;&gt; 63). The output is computed from the current state rather than the new one, so the CPU can overlap it with the next state update; this is why init6 discards one value to stay aligned with L'Ecuyer's stream.

## Compared with alternatives

Pick it over Randen, OpenRAND/Philox or the xoshiro/PCG siblings only when MRG32k3a itself is required for reproducibility or validation, since those siblings are faster general-purpose generators. Prefer OpenRAND or another counter-based generator when you need many parallel streams or GPU support.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (C: stdint.h, inttypes.h, stdio.h, stdlib.h; Java: none) |
| **Minimum toolchain** | Not documented; needs C with stdint.h/inttypes.h and 64-bit integers. The author timed gcc 9.2.1 (C) and Java 13 (Java). |
| **Platforms** | any with 64-bit integer arithmetic; relies on arithmetic right shift of negative int64_t, which C leaves implementation-defined (gcc, clang and MSVC all shift arithmetically) |
| **Thread safety** | C: not thread-safe (single global state in extern int64_t variables). Java: per-instance state, not synchronized. |
| **Drop-in for the baseline** | partial — same output stream as L'Ecuyer's MRG32k3a.c when seeded with MRG32k3a_init6, but a different function API and no stream/substream (RngStream) support |

## Gotchas

- Seeding by writing the state directly instead of calling MRG32k3a_init6/setSeed(long...) shifts the stream by one value: the generator emits from the current state, so you must discard one output to line up with the reference.
- MRG32k3a_init6 calls abort() on an all-zero or out-of-range seed instead of returning an error.
- The C header has no extern "C" guards, and its state uses reserved double-underscore names; from C++ either compile MRG32k3a.c as C++ or wrap the #include in extern "C".
- In the Java file the constructors have no access modifier (package-private) and the class is in the default package, so you must copy it into your own package or use setSeed on an instance made in that package.

## Known shortcomings

- Flags unstated; harness host (prng.di.unimi.it) blocked here; no LICENSE file (CC0 in headers).
- Code unchanged since 2019-11 (the 2026-06 commit is wording only), so 'active' overstates. Single global state, no streams. Header lacks extern "C"; Java constructors are package-private. Output matches the L'Ecuyer reference (independent re-implementation, 201 seeds x 2000 draws).

## Caveats and trade-offs

First-party header comment with CPU and gcc version but no flags. The timing harness is the author's external prng.di.unimi.it/harness.c (not opened, host blocked), and the 64-bit integer comparison code is not published. Checked: the branchless combination step matches the reference output rule, and MRG32k3a_init6() discards one output to align with L'Ecuyer's stream, as the README says. No multiple-stream support yet (the header says so). The README notes that for batch generation nothing beats Intel MKL's vectorised MRG32k3a. The repo has no LICENSE file; the CC0 dedication is in each source header (no patent grant). Baseline is the reference MRG32k3a, not std::mt19937.

Single stream only (no stream or jump support yet); returns doubles in (0,1); emits the output from the current state, so one value must be discarded to line up with L'Ecuyer's original stream; state is six 64-bit integers.

## Maintenance

The code has not changed since November 2019; the June 2026 commit only renamed 'testless' to 'branchless' in the comments. It is CC0, has no open issues and is small enough to vendor as is.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The MRG32k3a.h header comment states \~17.5 ns (L'Ecuyer's double-based MRG32k3a.c), \~7.9 ns (64-bit integer version) and \~4.1 ns (this code) per double on an i7-7700 @3.60GHz with gcc 9.2.1 and the author's harness (prng.di.unimi.it/harness.c). Optimisation flags are not stated in the repo, and the harness host is egress-blocked here, so it stays first-party C.
- **Verifier notes:** All numbers match the header and README. 21 stars, 7 commits. The last commit ('Testless -&gt; Branchless') is dated 2026-06-09; the previous one was 2019-11-02.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/vigna/MRG32k3a/HEAD/MRG32k3a.h>
  - <https://raw.githubusercontent.com/vigna/MRG32k3a/HEAD/MRG32k3a.c>
  - <https://raw.githubusercontent.com/vigna/MRG32k3a/HEAD/MRG32k3a.java>
  - <https://raw.githubusercontent.com/vigna/MRG32k3a/HEAD/README.md>
  - <https://github.com/vigna/MRG32k3a>
  - <https://github.com/vigna/MRG32k3a/commits/master>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/vigna/MRG32k3a/HEAD/README.md>
  - <https://raw.githubusercontent.com/vigna/MRG32k3a/HEAD/MRG32k3a.h>
  - <https://raw.githubusercontent.com/vigna/MRG32k3a/HEAD/MRG32k3a.c>
  - <https://raw.githubusercontent.com/vigna/MRG32k3a/HEAD/MRG32k3a.java>
  - <https://github.com/vigna/MRG32k3a>
  - <https://github.com/vigna/MRG32k3a/commits/master>
  - <https://github.com/vigna/MRG32k3a/commit/2479161>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/vigna/mrg32k3a`) · [data/wave8/enrich/raw/github_com_vigna_mrg32k3a.json](../../../data/wave8/enrich/raw/github_com_vigna_mrg32k3a.json) (enrichment confidence 0.85)

</details>
