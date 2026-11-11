# Quantum Random Number Generator (QRNG) — Team Handoff & Architecture Guide

> **AstraCode Qiskit Fall Fest 2026 | Project 4: Quantum Random Number Generator**  
> **Component**: Person 1 (Quantum Engine Deliverables & Integration Guide)  
> **Status**: Completed, verified on physical hardware, and test suite passing.

---

## 1. Quick Navigation for Teammates

This project uses quantum mechanical superposition to generate true random bits on real IBM Quantum superconducting hardware, with comparisons against noisy quantum simulations and classical pseudo-random number generators.

### 👤 For Mike (Person 2: Statistical Analysis & Comparison)
You **do not need Qiskit installed** to perform your analysis.
- **Your Primary Input Data**: 
  - [`data/quantum_bits_hardware.json`](data/quantum_bits_hardware.json) — 1,000 bits measured on real physical hardware (`ibm_marrakesh`, job `dbplvroqtr0c738elbe0`, 512 ones). **This is the shared hardware dataset.**
  - [`data/quantum_bits_noisy.json`](data/quantum_bits_noisy.json) — 1,000 bits from the offline noisy simulator (`aer_noisy`). Provided for the **Noise Detective (+5)** track; the simulator backends in `quantum_engine.py` exist only for offline unit tests and are not primary result datasets.
- **How to load the datasets in Python (Zero-dependency)**:
  ```python
  import json

  # Load real hardware data
  with open("data/quantum_bits_hardware.json", "r") as f:
      hw_dataset = json.load(f)

  bits = hw_dataset["bits"]        # list[int] of 1,000 values (0 or 1)
  backend = hw_dataset["source"]   # 'ibm_marrakesh'
  job_id = hw_dataset["job_id"]    # 'dbplvroqtr0c738elbe0'

  # Group bits into 8-bit integers (0 to 255)
  numbers = [
      int("".join(map(str, bits[i:i + 8])), 2)
      for i in range(0, len(bits) - 7, 8)
  ]
  # len(numbers) == 125, all values in 0..255
  ```
- **If you do want to use the module**:
  ```python
  from quantum_engine import load_bits, load_dataset, bits_to_numbers
  bits = load_bits("data/quantum_bits_hardware.json")
  numbers = bits_to_numbers(bits, n_qubits=8)
  ```
- **Recommended Statistical Tests to compare against Python `random`**:
  1. **Monobit Frequency Test**: Proportion of 1s vs 0s ($p$-value from normal distribution).
  2. **Runs Test**: Frequency of alternating run lengths (tests independence between successive bits).
  3. **Shannon Entropy**: Bit entropy $H = -\sum p_i \log_2 p_i$ (target $\approx 1.0$ bit/bit).
  4. **Autocorrelation Analysis**: Correlation between bit $b_i$ and bit $b_{i+k}$.

---

### 👤 For Evans (Person 3: Presentation, Storyline & Explanations)
Here are the core concepts and findings you can present:
- **Physical Superposition**: We place 8 superconducting qubits into an equal superposition state using Hadamard ($H$) gates:
  $$H|0\rangle = \frac{|0\rangle + |1\rangle}{\sqrt{2}}$$
  Measurement collapses the wavefunction with fundamental 50% probability into state $|0\rangle$ or $|1\rangle$.
- **Circuit Visual**: [`circuit_diagram.png`](circuit_diagram.png) shows the 8-qubit register in parallel.
- **Hardware Hero Finding (+5)**:
  - We ran 125 shots $\times$ 8 qubits on the physical quantum processor `ibm_marrakesh`.
  - Observed 1s count: **512 / 1,000** (**51.20%** ones).
- **Noise Detective Finding (+5)**:
  - In [`data/quantum_bits_noisy.json`](data/quantum_bits_noisy.json), we modelled a 2% gate error and asymmetric readout error ($P(0|1) = 12\% > P(1|0) = 5\%$), with the bias coming from readout asymmetry (these noise values are offline simulation assumptions we chose, not measured from a physical device).
  - Observed 1s count: **464 / 1,000** (**46.40%** ones).
  - Teachable point: The readout asymmetry naturally biases measured outcomes towards $|0\rangle$, creating an explainable bias in the simulation if uncorrected.
- **Classical vs. Quantum Randomness**:
  - Python's `random` uses the Mersenne Twister algorithm (MT19937) — fully deterministic given the 624-word internal state.
  - Quantum QRNG measurement outcomes are fundamentally non-deterministic according to the Born rule.

---

## 2. Repository Layout & Deliverables

```text
qrng/
├── README.md                         # Detailed team navigation & integration guide (this file)
├── README_person1.md                 # Original concise 10-line handoff note
├── quantum_engine.py                 # Core reusable module (hardware, offline helpers, contract)
├── person1_quantum_engine.ipynb      # Hardware-only demo notebook (clean, asserted steps)
├── circuit_diagram.png               # High-res 8-qubit Hadamard & measurement diagram
├── test_quantum_engine.py            # Offline test suite (9 test cases, 100% passing)
├── requirements.txt                  # Pinned dependencies (qiskit 2.6.2, qiskit-aer, qiskit-ibm-runtime)
└── data/
    ├── quantum_bits_hardware.json    # Real IBM QPU dataset (ibm_marrakesh, 1,000 bits, 512 ones)
    └── quantum_bits_noisy.json       # Noisy simulator dataset (aer_noisy, 1,000 bits)
```

---

## 3. Data Format Specification

Both dataset files in `data/` conform to this exact JSON schema:

```json
{
  "source": "ibm_marrakesh",
  "n_qubits": 8,
  "n_bits": 1000,
  "seed": null,
  "job_id": "dbplvroqtr0c738elbe0",
  "created": "2026-11-10T20:45:30.123456",
  "bits": [0, 1, 0, 1, 1, 0, 0, 1, ...]
}
```

| Key | Type | Description |
|---|---|---|
| `source` | `str` | Name of the hardware backend (`"ibm_marrakesh"`) or simulator (`"aer_noisy"`). |
| `n_qubits` | `int` | Number of parallel qubits evaluated per shot (8). |
| `n_bits` | `int` | Total count of measured binary digits (1,000). |
| `seed` | `int` \| `null` | Random seed (`null` for genuine physical quantum randomness). |
| `job_id` | `str` \| `null` | IBM Quantum job identifier (`"dbplvroqtr0c738elbe0"` on hardware). |
| `created` | `str` | ISO 8601 timestamp of data generation. |
| `bits` | `list[int]` | Plain Python list containing only binary values `0` and `1`. |

> **Bit Ordering Note**: Qiskit outputs shot strings in little-endian order (qubit 0 at the far right). In `quantum_engine.py`, each shot string was reversed with `[::-1]` so character index $i$ corresponds directly to qubit register $i$.

---

## 4. Environment Setup (If you want to run quantum code)

If you only analyze the JSON data, Python's standard library is all you need.

If you wish to execute the quantum engine or run the test suite locally:

```bash
# 1. Clone repository & enter directory
git clone https://github.com/vincii-ate/qrng.git
cd qrng

# 2. Create and activate virtual environment
python -m venv .venv
# On Windows (PowerShell):
.venv\Scripts\activate
# On Linux / macOS:
source .venv/bin/activate

# 3. Install pinned dependencies
pip install -r requirements.txt

# 4. Run automated test suite
python -m unittest test_quantum_engine.py
```

---

## 5. Public Functions in `quantum_engine.py`

| Function | Signature | Description |
|---|---|---|
| `build_qrng_circuit(n_qubits=8)` | `(n_qubits: int) -> QuantumCircuit` | Constructs circuit applying $H$ on all qubits followed by measurement. |
| `generate_bits(...)` | `(n_bits=1000, n_qubits=8, backend="hardware", seed=None) -> list[int]` | Generates exact bitstream. `backend` accepts `"hardware"`, `"ideal"`, or `"noisy"`. |
| `bits_to_numbers(bits, n_qubits=8)` | `(bits: list[int], n_qubits: int) -> list[int]` | Converts contiguous chunks of `n_qubits` bits into integers ($0..2^{n}-1$). |
| `save_bits(bits, path, **metadata)` | `(bits: list[int], path: str|Path, **metadata) -> Path` | Saves bits and metadata to JSON matching the contract schema. |
| `load_bits(path)` | `(path: str|Path) -> list[int]` | Reads and returns only the integer bit list from a JSON file. |
| `load_dataset(path)` | `(path: str|Path) -> dict` | Reads the entire JSON object including metadata and bits. |

---

## 6. Hackathon Bonus Points Tracked

- **Hardware Hero (+5)**: Real physical quantum computer execution demonstrated and recorded on `ibm_marrakesh` (Job `dbplvroqtr0c738elbe0`).
- **Noise Detective (+5)**: Explainable noise model implemented and benchmarked in [`data/quantum_bits_noisy.json`](data/quantum_bits_noisy.json).
- **Clean Code (+5)**: Type hints, docstrings, strict input validation, zero credentials committed, and 100% test pass rate.

