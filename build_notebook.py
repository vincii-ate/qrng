"""Script to build and execute person1_quantum_engine.ipynb top to bottom."""

import nbformat as nbf
from nbclient import NotebookClient

nb = nbf.v4.new_notebook()
cells = []

# Cell 1: Markdown Introduction
cells.append(nbf.v4.new_markdown_cell("""# Quantum Random Number Generator (QRNG) - Quantum Engine
### AstraCode Qiskit Fall Fest 2026 Hackathon | Person 1 Deliverable

This notebook demonstrates the core quantum engine for **Project 4: Quantum Random Number Generator**.
- **Physical principle**: Putting qubits into an equal superposition of $|0\\rangle$ and $|1\\rangle$ using Hadamard ($H$) gates, then measuring them.
- **Contract**: Generates ordered bitstreams and 8-bit integers, persisted in JSON format for statistical analysis by Person 2 and presentation by Person 3.
"""))

# Cell 2: Code Imports
cells.append(nbf.v4.new_code_cell("""import os
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit
from quantum_engine import (
    build_qrng_circuit,
    generate_bits,
    bits_to_numbers,
    save_bits,
    load_bits,
    load_dataset,
    make_noisy_simulator,
)

print("Quantum Engine module imported successfully!")
"""))

# Cell 3: Markdown 1-qubit coin
cells.append(nbf.v4.new_markdown_cell("""## 1. Single Qubit Quantum Coin
A single qubit initialized in $|0\\rangle$ undergoes a Hadamard transformation:
$$H|0\\rangle = \\frac{|0\\rangle + |1\\rangle}{\\sqrt{2}}$$
Upon measurement, the quantum superposition collapses into either $0$ or $1$ with equal 50% probability.
"""))

# Cell 4: Code 1-qubit execution
cells.append(nbf.v4.new_code_cell("""# Build and draw a 1-qubit circuit (the quantum coin)
qc_1q = build_qrng_circuit(n_qubits=1)
fig_1q = qc_1q.draw("mpl")
plt.show()

# Sample a single coin flip
coin_flip = generate_bits(n_bits=1, n_qubits=1, backend="ideal")
print(f"Single quantum coin flip result: {coin_flip[0]}")
"""))

# Cell 5: Markdown multi-qubit circuits
cells.append(nbf.v4.new_markdown_cell("""## 2. Multi-Qubit Register Diagrams
To generate bytes (integers from $0$ to $255$), we operate registers of independent qubits in parallel.
Below is a beginner-friendly 3-qubit circuit diagram, followed by the full 8-qubit production circuit.
"""))

# Cell 6: Code multi-qubit drawing
cells.append(nbf.v4.new_code_cell("""# 3-qubit circuit (clear visualization for beginners)
qc_3q = build_qrng_circuit(n_qubits=3)
fig_3q = qc_3q.draw("mpl")
plt.show()

# 8-qubit production circuit (used for generating 8-bit bytes)
qc_8q = build_qrng_circuit(n_qubits=8)
fig_8q = qc_8q.draw("mpl")
plt.show()
"""))

# Cell 7: Markdown Bit and Number generation
cells.append(nbf.v4.new_markdown_cell("""## 3. Bitstream and Integer Generation (Ideal Simulator)
We generate 1,000 bits using Qiskit Aer's ideal simulator with shot memory (`memory=True`) to preserve sequential ordering.
Then, we convert contiguous 8-bit chunks into numbers in the range $[0, 255]$.
"""))

# Cell 8: Code Bit and Number generation
cells.append(nbf.v4.new_code_cell("""# Generate 1,000 bits using the ideal simulator
ideal_bits = generate_bits(n_bits=1000, n_qubits=8, backend="ideal")
print(f"Total bits generated: {len(ideal_bits)}")
print(f"First 32 bits: {ideal_bits[:32]}")

# Convert the bits into 8-bit integers (0..255)
numbers = bits_to_numbers(ideal_bits, n_qubits=8)
print(f"Total 8-bit numbers: {len(numbers)}")
print(f"First 10 numbers: {numbers[:10]}")
"""))

# Cell 9: Markdown Noise Detective
cells.append(nbf.v4.new_markdown_cell("""## 4. Noise Detective: Ideal vs. Noisy Simulation
Real quantum hardware is subject to environmental decoherence and asymmetric readout fidelity.
Our noise model includes:
- **Gate error**: 2% depolarizing error on Hadamard gates.
- **Readout error**: $P(1|0) = 5\\%$, $P(0|1) = 12\\%$. Because physical devices misclassify $|1\\rangle$ as $|0\\rangle$ more often than the reverse, real data shows a slight bias towards $0$.
"""))

# Cell 10: Code Noise Detective
cells.append(nbf.v4.new_code_cell("""# Generate 1,000 noisy bits
noisy_bits = generate_bits(n_bits=1000, n_qubits=8, backend="noisy")

# Attempt hardware execution if token is present; skip gracefully if not
hardware_bits = None
if os.environ.get("IBM_QUANTUM_TOKEN"):
    try:
        print("Submitting 1,000-bit job to least-busy IBM Quantum device...")
        hardware_bits = generate_bits(n_bits=1000, n_qubits=8, backend="hardware")
        print("Hardware job finished successfully!")
    except Exception as exc:
        print(f"Hardware execution skipped: {exc}")
else:
    print("IBM_QUANTUM_TOKEN not set. Gracefully skipping real hardware execution.")

# Compute fraction of 1s
ideal_frac = sum(ideal_bits) / len(ideal_bits)
noisy_frac = sum(noisy_bits) / len(noisy_bits)
print(f"Ideal Simulator 1s fraction: {ideal_frac:.4f}")
print(f"Noisy Simulator 1s fraction: {noisy_frac:.4f}")

# Quick comparison bar chart
labels = ["Ideal Simulator", "Noisy Simulator"]
fractions = [ideal_frac, noisy_frac]
colors = ["#2b5c8f", "#d95f02"]

if hardware_bits is not None:
    hw_frac = sum(hardware_bits) / len(hardware_bits)
    labels.append("Real Hardware")
    fractions.append(hw_frac)
    colors.append("#7570b3")
    print(f"Hardware 1s fraction: {hw_frac:.4f}")

plt.figure(figsize=(7, 4))
bars = plt.bar(labels, fractions, color=colors, width=0.45)
plt.axhline(0.5, color="red", linestyle="--", label="Ideal Fair Coin (0.50)")
plt.ylabel("Fraction of 1s")
plt.ylim(0, 1.0)
plt.title("Comparison of 1s Frequency (Teaser for Person 2)")
plt.legend(loc="lower right")

for bar, frac in zip(bars, fractions):
    plt.text(bar.get_x() + bar.get_width() / 2, frac + 0.03, f"{frac:.3f}", ha="center", fontweight="bold")

plt.tight_layout()
plt.show()
"""))

# Cell 11: Markdown Data Persistence
cells.append(nbf.v4.new_markdown_cell("""## 5. Dataset Persistence and Interface Contract
We save the generated datasets into the `data/` folder adhering to the contract format so Persons 2 and 3 can use them without requiring Qiskit.
"""))

# Cell 12: Code Data Persistence
cells.append(nbf.v4.new_code_cell("""# Save datasets
save_bits(ideal_bits, "data/quantum_bits_sim.json", source="aer_simulator", n_qubits=8)
save_bits(noisy_bits, "data/quantum_bits_noisy.json", source="aer_simulator_noisy", n_qubits=8)
if hardware_bits is not None:
    save_bits(hardware_bits, "data/quantum_bits_hardware.json", source="ibm_hardware", n_qubits=8)

print("Saved data/quantum_bits_sim.json and data/quantum_bits_noisy.json")

# Verification round-trip
reloaded_bits = load_bits("data/quantum_bits_sim.json")
assert reloaded_bits == ideal_bits, "Reloaded bits do not match!"
print(f"Successfully verified round-trip loading of {len(reloaded_bits)} bits!")
"""))

nb.cells = cells

with open("person1_quantum_engine.ipynb", "w", encoding="utf-8") as f:
    nbf.write(nb, f)

print("person1_quantum_engine.ipynb written.")

client = NotebookClient(nb, timeout=180, kernel_name="python3")
client.execute()

with open("person1_quantum_engine.ipynb", "w", encoding="utf-8") as f:
    nbf.write(nb, f)

print("Notebook executed top to bottom successfully!")

