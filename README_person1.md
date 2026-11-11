# Person 1 Handoff Note: Quantum Engine

- **Installation**: Run `python -m venv .venv`, activate it (`.venv\Scripts\activate` or `source .venv/bin/activate`), and run `pip install -r requirements.txt`.
- **Usage**: Import via `from quantum_engine import generate_bits, load_bits`.
- **JSON format**: `{"source": str, "n_qubits": int, "n_bits": int, "seed": int|null, "job_id": str|null, "created": str, "bits": list[int]}`.
- **Datasets**: Exactly 1,000 bits each (`0` and `1`):
  - `data/quantum_bits_hardware.json`: Real physical IBM Quantum processor `ibm_marrakesh` (Job ID: `dbplvroqtr0c738elbe0`), 1,000 bits, 512 ones. **This is the shared hardware dataset.**
  - `data/quantum_bits_noisy.json`: Offline noisy simulator (`source: "aer_noisy"`), 1,000 bits modeled with 2% gate error and asymmetric readout errors. Provided for the Noise Detective track; the simulator backends exist only for offline unit tests and are not primary result datasets.
- **Bit order**: Little-endian Qiskit shot bitstrings were reversed (`[::-1]`) so character index $i$ corresponds directly to qubit $i$.
- **Caveat 1 (Simulator)**: The Aer simulator (tests and optional noise file only) is pseudo-random underneath, so it is not truly quantum.
- **Caveat 2 (Hardware measurement)**: Real hardware run on `ibm_marrakesh` measured 51.20% 1s (512/1,000 bits).
