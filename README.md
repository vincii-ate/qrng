# Quantum Random Number Generator (QRNG) Engine & Analysis

A complete Quantum Random Number Generator simulation engine built with **Qiskit** and **NumPy**, featuring hardware noise modeling, NIST-style statistical validation, and Bell-state quantum entanglement analysis.

---

## 🚀 Features

- **Quantum Circuit Simulation**:
  - Hadamard-based superposition for genuine quantum entropy.
  - Statevector simulation for ideal probabilities and shot-based quantum measurements.
- **Hardware Noise Modeling**:
  - Depolarizing noise channels modeling realistic physical quantum decoherence.
- **Entanglement & Bell States**:
  - Entangled pair generation ($|\Phi^+\rangle$) with correlated two-qubit measurement.
- **Statistical Quality Test Suite (6 Acceptance Criteria)**:
  1. Monobit Frequency Test ($p > 0.01$)
  2. Shannon Entropy ($H \ge 0.999$ bits/bit)
  3. Runs Test ($p > 0.01$)
  4. Autocorrelation Analysis ($|r_1| < 0.05$)
  5. Serial/Block Frequency Test ($p > 0.01$)
  6. Cumulative Sums Test ($p > 0.01$)
- **Data Export & Reproducibility**:
  - Export bitstreams to structured JSON in `data/`.
  - Automated testing with `pytest`.

---

## 📁 Repository Structure

```text
qrng/
├── quantum_engine.py            # Core QRNG classes, noise models & statistical tests
├── person1_quantum_engine.ipynb # Interactive tutorial notebook with visualizations
├── build_notebook.py            # Programmatic notebook generator script
├── test_quantum_engine.py       # Automated test suite (6 acceptance criteria)
├── circuit_diagram.png          # Bell state circuit visualization
├── requirements.txt             # Project dependencies
├── .gitignore                   # Ignored files (venv, pycache)
└── data/
    ├── quantum_bits_sim.json    # Sample ideal quantum bitstream
    └── quantum_bits_noisy.json  # Sample noisy quantum bitstream
```

---

## 🛠️ Quickstart

### 1. Installation
Clone this repository and install requirements in a virtual environment:

```bash
git clone https://github.com/vincii-ate/qrng.git
cd qrng
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Run Validation Tests
Run the test suite verifying all 6 statistical validation criteria:

```bash
pytest test_quantum_engine.py -v
```

### 3. Open the Notebook
Launch Jupyter to explore the interactive tutorial and plots:

```bash
jupyter notebook person1_quantum_engine.ipynb
```

---

## 👤 Author
**Vincent Manasseh Siboe** ([@vincii-ate](https://github.com/vincii-ate))
