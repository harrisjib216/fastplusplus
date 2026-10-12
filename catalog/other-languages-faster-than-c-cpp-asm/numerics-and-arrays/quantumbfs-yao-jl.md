# Yao.jl (Julia quantum circuit simulator) in Roger-luo/quantum-benchmarks

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Numerics and arrays](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Julia` · `Apache-2.0` · 🟢 active

> Julia quantum-circuit framework with state-vector simulation; its author's 2020 suite shows it beating QuEST through Python, not qulacs.

| | |
|---|---|
| **Beats** | Qulacs 0.1.9 (C++ library driven from Python through pybind11, one Python call per gate or circuit) and QuEST via pyquest-cffi 0.1.1 (C library driven from Python through cffi, one Python call per gate), single-thread full-amplitude state-vector simulation |
| **Claimed result** | Read off the repo's 'relative to Yao' chart images images/gates_relative.png and images/pcircuit_relative.png (log scale, no tables; ratios approximate; bin/plot uses the minimum time for every package). Parameterized circuit (QCBM) at 25 qubits: qulacs about 1.9x and pyquest-cffi (QuEST) about 8x Yao's time; below about 11 qubits qulacs is faster than Yao (about 0.34x of Yao's time at 4 qubits). This circuit does unequal work: Yao makes 19n state-vector passes (each qubit's rotation chain fused into one 2x2 matrix, 8 mid layers, 9 entanglers) while qulacs and QuEST apply 41n separate gates (9 mid layers, 10 entanglers), a 2.16x pass ratio (derived from the benchmark scripts) that covers the whole qulacs gap. Single gates at 25 qubits (same work, one pass each): pyquest-cffi about 2.4x (X), 1.8x (H) and 2.5x (CNOT) Yao's time but about 0.75x on T (QuEST faster); qulacs about 1.0x on X, CNOT and T and about 0.6x on H (qulacs faster), and qulacs is faster than or equal to Yao on all four gates at most sizes between about 11 and 20 qubits (down to about 0.3x on H). |
| **Workload** | Minimum time per gate application for X, H, CNOT and T gates on 4 to 25 qubits, and minimum time for a parameterized QCBM circuit (layers of per-qubit Rx/Rz rotations with ring CNOT entanglers) on 4 to 25 qubits, single thread (OMP/MKL/JULIA threads set to 1), Yao v0.6.1 per RESULTS.md (yao/Manifest.toml at the May 2020 refactor pins Yao 0.6.2 and YaoBlocks 0.10.3) against qulacs, QuEST (pyquest-cffi), qiskit-aer, ProjectQ, Cirq and PennyLane. |
| **Metric** | latency |
| **Hardware** | Intel Xeon Gold 6230 @ 2.10GHz (single thread); Tesla V100 for the CUDA rows |
| **Compiler and flags** | Julia 1.3.0 (LLVM 6.0.1 ORCJIT, skylake target, run without -O flags so Julia's default -O2), BLAS Intel MKL, Python 3.7.3 (from RESULTS.md). Not stated on the results page, derived from package sources: qulacs 0.1.9 exists on PyPI only as an sdist, built by pip through its CMake Release config (CMake default -O3 -DNDEBUG plus -march=native -mtune=native -mfpmath=both, AVX2 SIMD kernels enabled by default, OpenMP limited to 1 thread by OMP_NUM_THREADS=1); pyquest-cffi 0.1.1 is an sdist that builds QuEST through QuEST's own CMake, which sets -O2 (QuEST v3.2.0 CMakeLists; the exact QuEST version bundled by pyquest-cffi 0.1.1 was not checked). GCC version not stated. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | not stated |
| **Same optimization level** | not stated |
| **Adoption** | 1.0k stars and 131 forks (Yao.jl); the benchmark repo, now yardstiq/quantum-benchmarks (old Roger-luo URL redirects), has 129 stars |
| **Last commit** | 2026-09-08 |
| **Links** | [repository](https://github.com/QuantumBFS/Yao.jl) · [benchmark](https://github.com/yardstiq/quantum-benchmarks) |

## Verdict

In its author's single-thread suite on a Xeon Gold 6230 (Julia 1.3.0, MKL, Python 3.7.3; Yao 0.6.1 against qulacs 0.1.9 and QuEST via pyquest-cffi 0.1.1), Yao applied X, H and CNOT to 25-qubit states about 1.8-2.5x faster than QuEST built at -O2 and called through Python, but QuEST was faster on T and qulacs was equal or faster on single gates at most sizes from 11 to 25 qubits. The 1.9x lead over qulacs on the 25-qubit parameterized circuit comes from Yao doing about 2.16x fewer state passes, so it is not a per-gate or language win.

## Use it when

- Variational or parameterized circuit research in Julia where you want fused single-qubit rotation chains, batched registers and built-in gradients in one package
- Single-thread state-vector simulation at 20-25 qubits where the alternative is QuEST driven gate-by-gate through pyquest-cffi (about 1.8-2.5x slower than Yao on X, H and CNOT in the 2020 suite)
- Batched simulation of many small circuits (the suite's QCBM batch rows with 1000 registers) or moving the same circuit to an NVIDIA GPU through CuYao
- Teaching and prototyping, where the 3-line block syntax (e.g. QFT) and symbolic matrices matter more than raw gate throughput

## Skip it when

- C or C++ code that needs a fast simulator library: qulacs (C++, -O3 -march=native with AVX2) matched or beat Yao on single gates at 11-25 qubits in the same suite, down to about 0.3x of Yao's time on H
- Small circuits below about 11 qubits driven from Python bindings, where qulacs was faster than Yao on the parameterized circuit (about 0.34x Yao's time at 4 qubits)
- Latency-sensitive one-shot runs: the first call of each new circuit or function pays Julia JIT compilation (issue #422: a wrapped gradient took 0.037 s with 99.82% compilation time, against 37 us for the built-in expect' gradient)
- Projects needing current, independent speed evidence: the only cross-simulator numbers are its author's 2020 charts (Yao 0.6, Julia 1.3), and the README still calls the project an early-release beta

## How it is fast

Gates go through YaoArrayRegister's instruct! kernels, which dispatch on the gate's matrix type (identity skipped, permutation matrices become row swaps, diagonals become row scaling, Pauli/H/T/SWAP and others have named fast paths) and walk the state vector with bit-mask loops from BitBasis; StaticArrays and LuxurySparse keep small gate matrices on the stack. Composite blocks such as put(i=&gt;chain(Rz, Rx, Rz)) are collapsed into one 2x2 matrix before touching the state, so a rotation chain costs one pass. Julia's JIT specializes each kernel per element type, and the current kernels use Threads.@threads from 10 qubits up when Julia runs with several threads.

## Compared with alternatives

No other quantum-circuit simulator is catalogued in this category; the nearest sibling is ITensors.jl, which wins on tensor-network (DMRG) workloads, while Yao is the pick for state-vector circuits with built-in gradients and can hand a circuit to a tensor-network backend through YaoToEinsum.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | Julia packages BitBasis, LuxurySparse, YaoAPI, YaoArrayRegister, YaoBlocks, YaoSym, YaoPlots, YaoToEinsum, Reexport (StaticArrays, MLStyle, StatsBase and others transitively); CUDA.jl 4 or 5 optional for the CuYao extension |
| **Minimum toolchain** | Julia 1.x (Project.toml compat julia = "1"; Yao 0.9.3) |
| **Platforms** | any platform Julia runs on; NVIDIA GPUs through the CuYao extension |
| **Thread safety** | not documented; kernels multithread internally with Threads.@threads when Julia has more than one thread and the register has 10 or more qubits |
| **Drop-in for the baseline** | no |

## Gotchas

- The headline QCBM result does unequal work: Yao fuses each qubit's rotation chain into one 2x2 pass and builds one fewer layer, so it makes 19n state passes against 41n gate passes for qulacs and QuEST (2.16x), which covers the whole reported 1.9x over qulacs; qulacs' own gate-fusion optimizer was not used. Yao's QCBM also uses zero angles (Rx(0), Rz(0)) where the others use random ones; in YaoArrayRegister 0.6.2 the dense 2x2 path does not test for identity, so this changes the result values, not the speed.
- Single-gate rows are not fully matched: Yao applies gates to qubit 2 (one-based, bit stride 2) from rand_state while qulacs and QuEST use qubit 3 (zero-based, stride 8) from |0&gt;, and qulacs and QuEST are timed through pybind11 and cffi calls from Python, which dominate below about 10 qubits; QuEST was built at its CMake default -O2.
- Results are chart images only (log scale, minimum time), from 2020 package versions; the benchmark repo (now yardstiq/quantum-benchmarks) says the results are only up to date till 2020 and a rewrite is in progress.
- Mixing element types (e.g. a ComplexF32 register with a ComplexF64 gate matrix) prints an 'Element Type Mismatch' warning and converts the operator on every call, which the code itself flags as a possible performance issue.

## Known shortcomings

- Headline 1.9x over qulacs on the parameterized circuit comes from unequal work: Yao fuses each qubit's rotation chain into one 2x2 pass (YaoBlocks 0.10.3 PutBlock apply! calls instruct! on mat(content)) and its script runs one fewer layer (19n vs 41n state passes, 2.16x). Only same-work win is 1.8-2.5x on X/H/CNOT vs QuEST built -O2 via pyquest-cffi (QuEST faster on T); qulacs at -O3 -march=native AVX2 is equal or faster on single gates at 11-25 qubits. Benchmark lives in yardstiq/quantum-benchmarks.
- Identity kept by override: a runtime-jit-beats-aot copy from a later search draft took the bare id at merge; the verified claim is the numerics-and-arrays one (batch-40).
- Verifier's unequal-work finding confirmed (19n vs 41n passes). The Yao QCBM uses zero angles Rx(0)/Rz(0) where other packages use random angles; YaoArrayRegister 0.6.2's dense 2x2 path has no identity check, so values differ but speed does not. JIT latency (issue #422).

## Caveats and trade-offs

First-party: the suite is written by Yao's author (reviewed by maintainers of several competitors per its acknowledgements). Results are marked 'only up to date till 2020'; the chart images were last regenerated on 2020-05-29 and the benchmark repo's last commit is 2022-05-17, with old package versions (qulacs 0.1.9, Julia 1.3.0). RESULTS.md and the README give only chart images, so every ratio is read off a log-scale chart. Unequal work in the parameterized circuit: YaoBlocks 0.10.3 PutBlock apply! calls instruct!(r, mat_matchreg(r, content), locs), so Yao's put(i=&gt;chain(Rz, Rx, Rz)) is one dense 2x2 pass per qubit per layer, and Yao's build_circuit(k, 9, ...) has 8 mid layers and 9 entanglers where qulacs/QuEST build_circuit(n, 9, ...) has 9 and 10, giving 19n Yao passes against 41n qulacs/QuEST gate passes (2.16x); the reported 1.9x over qulacs is therefore not a per-gate or language win (qulacs' QuantumCircuitOptimizer gate fusion was not used). Single gates use different target qubits (Yao qubit 2 one-based, qulacs and QuEST qubit 3 zero-based) and Yao starts from rand_state while qulacs/QuEST start from |0&gt;. qulacs and QuEST are timed through Python (pybind11 and cffi), so below about 10 qubits their numbers are dominated by Python call overhead; pyquest-cffi's QCBM function also calls np.random.rand inside the timed region. QuEST is built at -O2 (QuEST's CMake default) rather than -O3; qulacs is built at -O3 -march=native with AVX2 kernels and matches or beats Yao on single gates at large sizes. RESULTS.md's text calls panel d 'Toffolli' but the chart and bin/plot show the T gate; the relative charts label their y axis 'ns' though they plot ratios. The current quest/ directory holds a newer C++ google-benchmark harness (QFT only) that did not produce these charts. The baseline is not a C or C++ program at a stated -O3. [retier] The Yao QCBM uses zero angles Rx(0)/Rz(0) where other packages use random angles; YaoArrayRegister 0.6.2's dense 2x2 path has no identity check, so values differ but speed does not. JIT latency (issue #422).

Julia JIT start-up and compilation time is not part of the per-gate timings. Qulacs is faster on small circuits and the advantage of Yao appears only at 20 or more qubits.

## Maintenance

Maintained at low volume by QuantumBFS (Yao 0.9.3 released 2026-03-01, last commit 2026-09-08, 21 open issues), Apache-2.0 and installable with Pkg, but the speed evidence is six years old and first-party.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification C, tier now C.
- **Tier reason:** First-party suite by Yao's author (yardstiq/quantum-benchmarks: yao/benchmarks.jl, qulacs/benchmarks.py, pyquest/benchmarks.py, bin/plot) with the CPU (Xeon Gold 6230) and Julia 1.3.0 stated, but the C/C++ compilers and flags are not stated (only derivable from the packages' build configs) and results exist only as log-scale chart images, so not A; the headline parameterized-circuit win comes from unequal work, while the same-work single-gate rows show a 1.8-2.5x win only against QuEST built at -O2 through a Python cffi wrapper.
- **Verifier notes:** Chart readings in the record match images/gates_relative.png and images/pcircuit_relative.png, but the headline 1.9x over qulacs on the parameterized circuit is explained by unequal work (Yao fuses per-qubit rotation chains and runs one fewer layer: 19n vs 41n state passes, verified in yao/benchmarks.jl, qulacs/benchmarks.py, pyquest/benchmarks.py and YaoBlocks 0.10.3 put_block.jl/chain.jl). The only same-work win is 1.8-2.5x on X/H/CNOT against QuEST at -O2 through pyquest-cffi (QuEST faster on T); against qulacs at -O3 -march=native Yao is equal or slower on single gates at 11-25 qubits. Keep at C with these shortcomings; benchmark repo moved to yardstiq/quantum-benchmarks.
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `claimed_speedup`, `compiler_and_flags`, `stars_or_usage`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-40 (wave 14); orchestrator (wave 14 merge); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/Roger-luo/quantum-benchmarks>
  - <https://github.com/Roger-luo/quantum-benchmarks/tree/master/bin>
  - <https://github.com/yardstiq/quantum-benchmarks/commits>
  - <https://github.com/yardstiq/quantum-benchmarks/commits/master/yao/benchmarks.jl>
  - <https://github.com/yardstiq/quantum-benchmarks/commits/master/images/pcircuit_relative.png>
  - <https://github.com/yardstiq/quantum-benchmarks/commits/master/qulacs/benchmarks.py>
  - <https://raw.githubusercontent.com/Roger-luo/quantum-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/Roger-luo/quantum-benchmarks/HEAD/RESULTS.md>
  - <https://raw.githubusercontent.com/Roger-luo/quantum-benchmarks/HEAD/bin/benchmark>
  - <https://raw.githubusercontent.com/Roger-luo/quantum-benchmarks/HEAD/bin/plot>
  - <https://raw.githubusercontent.com/Roger-luo/quantum-benchmarks/HEAD/bin/utils/project.py>
  - <https://raw.githubusercontent.com/Roger-luo/quantum-benchmarks/HEAD/bin/utils/constants.sh>
  - <https://raw.githubusercontent.com/Roger-luo/quantum-benchmarks/HEAD/images/gates_relative.png>
  - <https://raw.githubusercontent.com/Roger-luo/quantum-benchmarks/HEAD/images/pcircuit_relative.png>
  - <https://raw.githubusercontent.com/Roger-luo/quantum-benchmarks/HEAD/yao/benchmarks.jl>
  - <https://raw.githubusercontent.com/Roger-luo/quantum-benchmarks/HEAD/qulacs/benchmarks.py>
  - <https://raw.githubusercontent.com/Roger-luo/quantum-benchmarks/HEAD/qulacs/setup.sh>
  - <https://raw.githubusercontent.com/Roger-luo/quantum-benchmarks/HEAD/pyquest/benchmarks.py>
  - <https://raw.githubusercontent.com/Roger-luo/quantum-benchmarks/HEAD/pyquest/setup.sh>
  - <https://raw.githubusercontent.com/Roger-luo/quantum-benchmarks/HEAD/quest/benchmarks.cc>
  - <https://raw.githubusercontent.com/yardstiq/quantum-benchmarks/f146574/yao/benchmarks.jl>
  - <https://raw.githubusercontent.com/yardstiq/quantum-benchmarks/f146574/qulacs/benchmarks.py>
  - <https://raw.githubusercontent.com/yardstiq/quantum-benchmarks/f146574/yao/Manifest.toml>
  - <https://raw.githubusercontent.com/QuantumBFS/YaoBlocks.jl/v0.10.3/src/composite/put_block.jl>
  - <https://raw.githubusercontent.com/QuantumBFS/YaoBlocks.jl/v0.10.3/src/composite/chain.jl>
  - <https://raw.githubusercontent.com/QuantumBFS/Yao.jl/v0.6.1/Project.toml>
  - <https://raw.githubusercontent.com/qulacs/qulacs/v0.1.9/CMakeLists.txt>
  - <https://raw.githubusercontent.com/qulacs/qulacs/v0.1.9/setup.py>
  - <https://pypi.org/pypi/qulacs/0.1.9/json>
  - <https://pypi.org/pypi/pyquest-cffi/0.1.1/json>
  - <https://raw.githubusercontent.com/HQSquantumsimulations/PyQuEST-cffi/master/setup.py>
  - <https://raw.githubusercontent.com/QuEST-Kit/QuEST/v3.2.0/QuEST/CMakeLists.txt>
  - <https://github.com/QuantumBFS/Yao.jl>
  - <https://github.com/QuantumBFS/Yao.jl/commits>
- **Sources the enricher read:**
  - <https://github.com/QuantumBFS/Yao.jl>
  - <https://github.com/QuantumBFS/Yao.jl/commits>
  - <https://github.com/QuantumBFS/Yao.jl/issues?q=is%3Aissue+performance>
  - <https://github.com/QuantumBFS/Yao.jl/issues/422>
  - <https://raw.githubusercontent.com/QuantumBFS/Yao.jl/HEAD/README.md>
  - <https://raw.githubusercontent.com/QuantumBFS/Yao.jl/HEAD/Project.toml>
  - <https://raw.githubusercontent.com/QuantumBFS/Yao.jl/HEAD/CLAUDE.md>
  - <https://raw.githubusercontent.com/QuantumBFS/Yao.jl/HEAD/NEWS.md>
  - <https://raw.githubusercontent.com/QuantumBFS/Yao.jl/HEAD/lib/YaoArrayRegister/Project.toml>
  - <https://raw.githubusercontent.com/QuantumBFS/Yao.jl/HEAD/lib/YaoArrayRegister/src/instruct.jl>
  - <https://raw.githubusercontent.com/QuantumBFS/Yao.jl/HEAD/lib/YaoArrayRegister/src/utils.jl>
  - <https://raw.githubusercontent.com/QuantumBFS/YaoArrayRegister.jl/v0.6.1/src/instruct.jl>
  - <https://raw.githubusercontent.com/QuantumBFS/YaoArrayRegister.jl/v0.6.2/src/instruct.jl>
  - <https://raw.githubusercontent.com/yardstiq/quantum-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/yardstiq/quantum-benchmarks/HEAD/RESULTS.md>
  - <https://raw.githubusercontent.com/yardstiq/quantum-benchmarks/HEAD/yao/benchmarks.jl>
  - <https://raw.githubusercontent.com/yardstiq/quantum-benchmarks/HEAD/qulacs/benchmarks.py>
  - <https://raw.githubusercontent.com/yardstiq/quantum-benchmarks/HEAD/pyquest/benchmarks.py>
  - <https://raw.githubusercontent.com/yardstiq/quantum-benchmarks/f146574/yao/Manifest.toml>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/quantumbfs/yao.jl`) · [data/wave14/enrich/raw/github_com_quantumbfs_yao_jl.json](../../../data/wave14/enrich/raw/github_com_quantumbfs_yao_jl.json) (enrichment confidence 0.7)

</details>
