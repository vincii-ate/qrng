"""Builds person1_quantum_engine.ipynb conforming to the strict hardware-only spec."""

import nbformat as nbf

nb = nbf.v4.new_notebook()
nb.metadata = {
    "kernelspec": {
        "display_name": "Python (.venv)",
        "language": "python",
        "name": "qrng-venv"
    },
    "language_info": {
        "name": "python",
        "version": "3.11.9"
    }
}

cells = []

# Step 1: Intro (markdown)
# Must contain exact phrasing from spec:
# "We use qubits in superposition to generate random bits on a real IBM quantum computer, combine them into random numbers, and later compare them with Python's random module."
cells.append(nbf.v4.new_markdown_cell("""# Quantum Random Number Generator (QRNG) on IBM Quantum Hardware
### AstraCode Qiskit Fall Fest 2026 | Person 1 Deliverable

We use qubits in superposition to generate random bits on a real IBM quantum computer, combine them into random numbers, and later compare them with Python's `random` module.
"""))

# Step 2: Setup (markdown + code)
cells.append(nbf.v4.new_markdown_cell("""### Step 2: Environment and Package Setup
Load required modules and verify installed Qiskit versions.
"""))

cells.append(nbf.v4.new_code_cell("""# Colab installation (uncomment if running on Google Colab):
# !pip install qiskit qiskit-ibm-runtime matplotlib

import os
import matplotlib.pyplot as plt
import qiskit
import qiskit_ibm_runtime
from qiskit import QuantumCircuit
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

from quantum_engine import (
    build_qrng_circuit,
    generate_bits,
    bits_to_numbers,
    save_bits,
    load_bits,
    load_dataset,
)

%matplotlib inline

print(f"qiskit version: {qiskit.__version__}")
print(f"qiskit-ibm-runtime version: {qiskit_ibm_runtime.__version__}")

# Closing check: imports succeed and versions are present
assert hasattr(qiskit, "__version__"), "Qiskit import check failed"
assert hasattr(qiskit_ibm_runtime, "__version__"), "Qiskit Runtime import check failed"
"""))

# Step 3: The circuit (markdown + code)
cells.append(nbf.v4.new_markdown_cell("""### Step 3: The Quantum Circuit
We apply a Hadamard ($H$) gate to every qubit to prepare an equal superposition state:
$$H|0\\rangle = \\frac{|0\\rangle + |1\\rangle}{\\sqrt{2}}$$
Each qubit has an equal 50% probability of being measured in state $0$ or state $1$.
Measurement collapses the quantum state into a classical bit.
Below are the 8-qubit production circuit and a 3-qubit visualization.
"""))

cells.append(nbf.v4.new_code_cell("""# 8-qubit production circuit
qc = build_qrng_circuit(n_qubits=8)
fig_8q = qc.draw("mpl", filename="circuit_diagram.png")
plt.show()

# 3-qubit visualization
qc_3q = build_qrng_circuit(n_qubits=3)
fig_3q = qc_3q.draw("mpl")
plt.show()

# Closing check: qc.num_qubits == 8, circuit has 8 h and 8 measure operations
ops = qc.count_ops()
assert qc.num_qubits == 8, f"Expected 8 qubits, got {qc.num_qubits}"
assert ops.get("h", 0) == 8, f"Expected 8 h operations, got {ops.get('h')}"
assert ops.get("measure", 0) == 8, f"Expected 8 measure operations, got {ops.get('measure')}"
print("Circuit verification passed: 8 qubits, 8 Hadamard gates, 8 measurements.")
"""))

# Step 4: Key cell (markdown + code)
cells.append(nbf.v4.new_markdown_cell("""### Step 4: IBM Quantum Authentication
Paste your IBM key when prompted. It is never saved in the notebook.
"""))

cells.append(nbf.v4.new_code_cell("""import os, getpass
if "IBM_QUANTUM_TOKEN" not in os.environ:
    os.environ["IBM_QUANTUM_TOKEN"] = getpass.getpass("IBM API key: ")
if "IBM_QUANTUM_INSTANCE" not in os.environ:
    inst = getpass.getpass("IBM instance CRN or name (Enter to skip): ")
    if inst:
        os.environ["IBM_QUANTUM_INSTANCE"] = inst
"""))

# Step 5: Pre-flight (markdown + code)
cells.append(nbf.v4.new_markdown_cell("""### Step 5: Pre-flight Backend Check
Authenticate with IBM Quantum, query operational physical devices, and inspect status.
"""))

cells.append(nbf.v4.new_code_cell("""token = os.environ.get("IBM_QUANTUM_TOKEN")
if not token:
    print("IBM key not set. Run the key cell first.")
else:
    instance = os.environ.get("IBM_QUANTUM_INSTANCE")
    channel = os.environ.get("IBM_QUANTUM_CHANNEL") or (
        "ibm_cloud" if instance and "bluemix" in instance else "ibm_quantum_platform"
    )
    service = QiskitRuntimeService(channel=channel, token=token, instance=instance)
    backend_obj = service.least_busy(operational=True, simulator=False, min_num_qubits=8)
    status = backend_obj.status()

    print(f"Target backend: {backend_obj.name}")
    print(f"Total qubits: {backend_obj.num_qubits}")
    print(f"Pending jobs: {status.pending_jobs}")
    print(f"Operational status: {status.operational}")

    # Closing check: backend is real (simulator is False) and operational
    assert backend_obj.simulator is False, f"Backend {backend_obj.name} must not be a simulator!"
    assert status.operational is True, f"Backend {backend_obj.name} is not operational!"
    print("Pre-flight check passed: real, operational physical backend selected.")
"""))

# Step 6: Hardware run (markdown + code)
cells.append(nbf.v4.new_markdown_cell("""### Step 6: Hardware Execution and Data Persistence
Execute 1,000 measurements on real physical hardware (125 shots across 8 qubits), retrieve the ordered bitstream, and immediately save to `data/quantum_bits_hardware.json`.
"""))

cells.append(nbf.v4.new_code_cell("""token = os.environ.get("IBM_QUANTUM_TOKEN")
if not token:
    print("IBM key not set. Run the key cell first.")
else:
    # Generate 1,000 bits directly on physical hardware
    bits = generate_bits(n_bits=1000, n_qubits=8, backend="hardware")
    
    from quantum_engine import LAST_HARDWARE_BACKEND, LAST_HARDWARE_JOB_ID
    backend_name = LAST_HARDWARE_BACKEND
    job_id = LAST_HARDWARE_JOB_ID
    print(f"Measured on backend: {backend_name}")
    print(f"Hardware job ID: {job_id}")

    # Save immediately after job returns, before plotting
    out_path = save_bits(bits, "data/quantum_bits_hardware.json", source=backend_name, job_id=job_id, n_qubits=8)
    print(f"Saved dataset to {out_path}")

    # Closing check: len(bits) == 1000, set(bits) <= {0, 1}, saved file reloads to identical list
    assert len(bits) == 1000, f"Expected 1000 bits, got {len(bits)}"
    assert set(bits) <= {0, 1}, "Bits must contain only 0 and 1"
    reloaded_bits = load_bits("data/quantum_bits_hardware.json")
    assert reloaded_bits == bits, "Reloaded bits do not match measured bits!"
    print(f"Hardware execution assertions passed: exact 1,000 bits verified.")
"""))

# Step 7: Results (markdown + code)
cells.append(nbf.v4.new_markdown_cell("""### Step 7: Measured Results and Bit-to-Number Conversion
Group consecutive bits into 8-bit integers ($0..255$), inspect sample values, and plot bit frequency.
"""))

cells.append(nbf.v4.new_code_cell("""# Load measured bits from dataset
dataset = load_dataset("data/quantum_bits_hardware.json")
bits = dataset["bits"]

# Convert to 8-bit numbers
numbers = bits_to_numbers(bits, n_qubits=8)

# Closing check: len(numbers) == 125, all values in 0..255
assert len(numbers) == 125, f"Expected 125 numbers, got {len(numbers)}"
assert all(0 <= n <= 255 for n in numbers), "All numbers must be in 0..255"

print(f"First 32 bits: {bits[:32]}")
print(f"First 10 numbers: {numbers[:10]}")

count_0 = bits.count(0)
count_1 = bits.count(1)
frac_1 = count_1 / len(bits)
print(f"Measured fraction of 1s: {frac_1:.4f} ({count_1}/{len(bits)})")

# Bar chart of 0s vs 1s
plt.figure(figsize=(6, 4))
bars = plt.bar(["0", "1"], [count_0, count_1], color=["#2b5c8f", "#7570b3"], width=0.4)
plt.xlabel("bit value", fontsize=11)
plt.ylabel("count", fontsize=11)
plt.title("Hardware Measured Bit Frequencies", fontsize=12)
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width() / 2, yval + 10, f"{yval}", ha="center", fontweight="bold")
plt.tight_layout()
plt.show()
"""))

# Step 8: Takeaway (markdown + code)
cells.append(nbf.v4.new_markdown_cell("""### Step 8: Measured Summary and Takeaway
Summary generated strictly by code with f-strings from the measured data.
"""))

cells.append(nbf.v4.new_code_cell("""# Summary generated entirely from measured data
dataset = load_dataset("data/quantum_bits_hardware.json")
bits = dataset["bits"]
backend_name = dataset["source"]
job_id = dataset["job_id"]
total_bits = len(bits)
count_1 = bits.count(1)
frac_1 = count_1 / total_bits

if frac_1 > 0.5:
    bias_relation = "above 0.5"
elif frac_1 < 0.5:
    bias_relation = "below 0.5"
else:
    bias_relation = "equal to 0.5"

takeaway_text = (
    f"Measured {total_bits} random bits on quantum processor '{backend_name}' (job ID: {job_id}). "
    f"The observed fraction of 1s was {frac_1:.4f} ({count_1}/{total_bits}), which is {bias_relation}. "
    f"By construction, the circuit placed each qubit in an equal superposition via a Hadamard gate and measured it."
)

print(takeaway_text)
"""))

nb.cells = cells

with open("person1_quantum_engine.ipynb", "w", encoding="utf-8") as f:
    nbf.write(nb, f)

print("Generated person1_quantum_engine.ipynb adhering strictly to Section 8 spec!")
