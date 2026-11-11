# Quantum Random Number Generator (QRNG)

> **AstraCode Qiskit Fall Fest 2026 · Project 4: Quantum Random Number Generator**  
> **Team**: Temi (Quantum Engine), Mike (Statistical Analysis), Evans (Presentation & Narrative)  
> **Status**: Full integration complete · Verified on physical quantum processor · 100% test pass rate

---

## 1. Project Overview

True randomness is impossible to achieve using deterministic classical algorithms alone. Classical pseudo-random number generators (PRNGs), such as Python's Mersenne Twister (MT19937), produce predictable streams once their internal state is known.

This project harnesses the fundamental unpredictability of quantum mechanics. By preparing 8 superconducting qubits in an equal Hadamard superposition:

$$H|0\rangle = \frac{|0\rangle + |1\rangle}{\sqrt{2}}$$

and measuring them, the wavefunction collapses into truly non-deterministic classical bits according to the Born rule.

### Three Integrated Components
1. **Quantum Engine (Person 1 · Temi)**: Constructing circuits, non-blocking submission to least-busy IBM Quantum hardware, little-endian bit conversion, offline noise modeling, and unit testing.
2. **Statistical Suite (Person 2 · Mike)**: Zero-dependency rigorous hypothesis testing (frequency/monobit test, runs test, longest run streak, Shannon entropy, lag-1 autocorrelation).
3. **Interactive Narrative (Person 3 · Evans)**: Complete educational presentation notebook featuring real-world applications (dice rolling, one-time pad encryption), dynamic comparison tables, and visual charts.

---

## 2. Verified Hardware Baseline

Our primary shared dataset was collected directly on physical IBM Quantum superconducting hardware:

- **Quantum Processor**: `ibm_marrakesh`
- **Job ID**: `dbplvroqtr0c738elbe0`
- **Dataset File**: [`data/quantum_bits_hardware.json`](data/quantum_bits_hardware.json)
- **Sample Size**: 1,000 bits (125 shots $\times$ 8 qubits)
- **Measured Balance**: **512 ones** / 488 zeros (51.20% ones)

### Statistical Benchmark Results

| Metric | Hardware QRNG (`ibm_marrakesh`) | Python Baseline (`random`, seed=42) | Offline Noisy Sim (`aer_noisy`) | Target / Meaning |
|---|---|---|---|---|
| **Ones Count** | **512 / 1,000** | 514 / 1,000 | 464 / 1,000 | ~500 (balanced) |
| **Monobit $p$-value** | **0.447884** | 0.375921 | 0.022796 | $> 0.01$ (passes test) |
| **Total Runs** | **507** | 494 | 490 | ~500 (alternation) |
| **Longest Run Streak** | **10** | 11 | 11 | Short streaks expected |
| **Shannon Entropy** | **0.9996** bits/bit | 0.9994 bits/bit | 0.9963 bits/bit | Target 1.0 (max uncertainty) |
| **Lag-1 Autocorrelation**| **-0.0136** | 0.0122 | 0.0159 | Target 0.0 (independent bits) |

The shared hardware dataset is immutable (`data/quantum_bits_hardware.json`, SHA256: `FC504841F9B4722829CC90CAEB56E489BB3F9F790E844897A5F2240A24D2C0BB`).

---

## 3. Quick Start & How to Run

### Option A: Explore the Final Presentation Notebook (Zero Qiskit Required)
The final presentation notebook [`qrng_final.ipynb`](qrng_final.ipynb) operates entirely offline on the pre-collected JSON dataset using only `matplotlib` and Python's standard library. No IBM Quantum token or Qiskit install is necessary.

```bash
# 1. Activate your virtual environment and launch the notebook
jupyter notebook qrng_final.ipynb
```

#### Saved vs. Live Switch
At the very top of `qrng_final.ipynb`, you can toggle between datasets:
```python
DATASET = "saved"  # Default: loads verified baseline (ibm_marrakesh, 512 ones)
# or
DATASET = "live"   # Loads fresh live run from data/live_runs/latest.json (with safe fallback)
```

---

### Option B: Run a Live Quantum Hardware Demo
To submit a live job to physical IBM Quantum hardware without blocking:

1. Open [`live_hardware_demo.ipynb`](live_hardware_demo.ipynb).
2. Enter your IBM Quantum API token in Step 1 (uses secure `getpass`; key is never printed or saved in plaintext).
3. Execute **Step 3 ("Submit Live Hardware Job")**: Asynchronously submits 125 shots to the least-busy operational backend and returns immediately.
4. Execute **Step 4 ("Check Job Status")**: Re-runnable polling cell tracking queue position and execution status.
5. Execute **Step 5 ("Save Results")**: Automatically extracts bits (with little-endian reversal), renders frequency charts, and saves to `data/live_runs/latest.json`.
6. Return to `qrng_final.ipynb` with `DATASET = "live"` to analyze your fresh quantum data!

---

### Option C: Run the Statistical Test Suite Directly
Mike's statistical analysis script uses only the Python standard library:

```bash
python statistical_comparison.py
```

To run against a custom or live dataset:
```python
import statistical_comparison as sc
report = sc.build_report(hardware_path="data/live_runs/latest.json")
sc.print_report(report)
```

---

### Option D: Run Offline Unit Tests
Run the automated test suite covering quantum circuit construction, bit conversions, dataset formatting, and noise modeling:

```bash
python -m pytest -q test_quantum_engine.py
# Output: 9 passed
```

---

## 4. Repository Layout

```text
qrng/
├── README.md                         # Comprehensive project documentation (this file)
├── README_person1.md                 # Original quantum engine component documentation
├── qrng_final.ipynb                  # Primary presentation notebook (interactive narrative & stats)
├── live_hardware_demo.ipynb          # Live hardware demo (non-blocking QPU submit, queue check, save)
├── person1_quantum_engine.ipynb      # Person 1 quantum engine demonstration notebook
├── quantum_engine.py                 # Core engine module (circuits, hardware submission, live storage)
├── statistical_comparison.py         # Statistical analysis module (monobit, runs, entropy, autocorrelation)
├── test_quantum_engine.py            # Automated test suite (9 unit tests, 100% passing)
├── circuit_diagram.png               # High-res 8-qubit Hadamard & measurement circuit diagram
├── requirements.txt                  # Pinned dependencies (Qiskit 2.6.2, qiskit-aer, qiskit-ibm-runtime)
└── data/
    ├── quantum_bits_hardware.json    # Real IBM QPU dataset (ibm_marrakesh, 1,000 bits, 512 ones)
    └── quantum_bits_noisy.json       # Offline noisy simulator dataset (aer_noisy, 1,000 bits)
```

---

## 5. Noise Detective & Error Modeling

For the **Noise Detective (+5)** track, we modeled realistic physical noise channels in [`data/quantum_bits_noisy.json`](data/quantum_bits_noisy.json):
- **Depolarizing Gate Error**: 2% depolarizing error on single-qubit gates.
- **Asymmetric Readout Error**: $P(0|1) = 12\%$ versus $P(1|0) = 5\%$.

Because energy relaxation makes state decay $|1\rangle \to |0\rangle$ more probable than excitation $|0\rangle \to |1\rangle$, physical measurement apparatuses frequently exhibit asymmetric readout error. In our noisy simulation, this creates an explainable bias towards zero (**464 ones / 1,000 bits**; monobit $p = 0.022796$).

*(Note: Simulator backends in `quantum_engine.py` exist for offline benchmarking and unit tests; `data/quantum_bits_noisy.json` illustrates noise effects and is not a primary result dataset).*

---

## 6. Public API Reference

### `quantum_engine.py`
| Function | Parameters | Description |
|---|---|---|
| `build_qrng_circuit(n_qubits=8)` | `n_qubits: int` | Builds parallel Hadamard superposition circuit with measurements. |
| `submit_hardware_job(qc, shots=125)`| `qc: QuantumCircuit, shots: int` | Non-blocking submission to least-busy operational IBM Quantum QPU. |
| `save_live_run(bits, backend, job_id, ...)` | `bits, backend, job_id, ...` | Persists live data to `data/live_runs/`; strictly protects `quantum_bits_hardware.json`. |
| `bits_to_numbers(bits, n_qubits=8)` | `bits: list[int], n_qubits: int` | Converts contiguous $n$-bit slices into integers ($0..2^n-1$). |
| `generate_bits(...)` | `n_bits, n_qubits, backend, seed` | Offline bit generator (supports `"hardware"`, `"ideal"`, `"noisy"`). |
| `load_dataset(path)` | `path: str \| Path` | Loads JSON dataset dictionary with metadata and bit list. |

### `statistical_comparison.py`
| Function | Parameters | Description |
|---|---|---|
| `monobit_frequency_test(bits)` | `bits: list[int]` | Calculates proportion of ones, $z$-score, and two-tailed $p$-value. |
| `runs_test(bits)` | `bits: list[int]` | Counts runs, transitions, and run-length frequency distribution. |
| `longest_run(bits)` | `bits: list[int]` | Determines the length of the longest streak of identical bits. |
| `shannon_entropy(bits)` | `bits: list[int]` | Computes empirical binary Shannon entropy ($-\sum p_i \log_2 p_i$). |
| `autocorrelation(bits, lag=1)` | `bits: list[int], lag: int` | Calculates sample Pearson autocorrelation at specified lag. |
| `generate_python_random_bits(n, seed)` | `n: int, seed: int` | Generates reproducible classical PRNG baseline (seed=42). |
| `build_report(hardware_path=...)` | `hardware_path, noisy_path` | Builds structured dictionary comparing hardware, noisy sim, and Python baseline. |

---

## 7. Hackathon Bonus Tracks Addressed

- **Hardware Hero (+5)**: Real physical quantum computer execution demonstrated and recorded on `ibm_marrakesh` (Job `dbplvroqtr0c738elbe0`, 512 ones / 1,000 bits).
- **Noise Detective (+5)**: Explainable noise model implemented, simulated, and benchmarked against physical hardware and classical baselines.
- **Clean Code (+5)**: Type annotations, complete docstrings, comprehensive assertions, zero committed credentials, and a 100% passing test suite.
