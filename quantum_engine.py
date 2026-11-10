"""Quantum Random Number Generator (QRNG) - Quantum Engine Module.

Developed for Person 1 (Quantum Engine) in the AstraCode Qiskit Fall Fest 2026.
Provides circuit generation, hardware execution, simulation for tests,
bit-to-number conversion, and dataset persistence.
"""

from __future__ import annotations

from datetime import datetime
import json
import math
import os
from pathlib import Path

from qiskit import QuantumCircuit, transpile
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, ReadoutError, depolarizing_error
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

# System and circuit constants
DEFAULT_QUBITS = 8
DEFAULT_N_BITS = 1000
MIN_QUBITS = 1
MAX_QUBITS = 16
VALID_BACKENDS = ("hardware", "ideal", "noisy")

# Tracking the last executed hardware metadata
LAST_HARDWARE_BACKEND: str | None = None
LAST_HARDWARE_JOB_ID: str | None = None

# Offline noisy simulation parameters (chosen model, not a measurement of any real device)
DEP_GATE_ERROR_RATE = 0.02
READOUT_PROB_1_GIVEN_0 = 0.05
READOUT_PROB_0_GIVEN_1 = 0.12


def build_qrng_circuit(n_qubits: int = DEFAULT_QUBITS) -> QuantumCircuit:
    """Build a QRNG circuit putting all qubits in superposition and measuring them.

    Args:
        n_qubits: Number of qubits and classical bits (1 to 16).

    Returns:
        QuantumCircuit: Constructed circuit with H gates and measurements.
    """
    if not (MIN_QUBITS <= n_qubits <= MAX_QUBITS):
        raise ValueError(
            f"n_qubits must be between {MIN_QUBITS} and {MAX_QUBITS}, got {n_qubits}"
        )
    # Initialize circuit with n_qubits and matching classical register 'c'
    qc = QuantumCircuit(n_qubits, n_qubits)
    # Superposition: H gate maps |0> to (|0> + |1>) / sqrt(2) (equal 50/50 probability)
    qc.h(range(n_qubits))
    # Measurement: Wavefunction collapses into classical bit 0 or 1
    qc.measure(range(n_qubits), range(n_qubits))
    return qc


def make_noisy_simulator() -> AerSimulator:
    """Build an explainable noisy Aer simulator for the Noise Detective track.

    Note: This is a chosen educational noise model, not a physical measurement
    of any specific real hardware device.

    Returns:
        AerSimulator: Simulator configured with gate depolarizing and readout errors.
    """
    noise = NoiseModel()
    # Gate error: 2% depolarizing error on Hadamard gates to model imperfect pulses
    noise.add_all_qubit_quantum_error(
        depolarizing_error(DEP_GATE_ERROR_RATE, 1), ["h"]
    )
    # Readout error: P(1|0)=5%, P(0|1)=12%
    # Real physical devices read 1s less reliably, creating an asymmetric bias towards 0
    readout_matrix = [
        [1.0 - READOUT_PROB_1_GIVEN_0, READOUT_PROB_1_GIVEN_0],
        [READOUT_PROB_0_GIVEN_1, 1.0 - READOUT_PROB_0_GIVEN_1],
    ]
    noise.add_all_qubit_readout_error(ReadoutError(readout_matrix))
    return AerSimulator(noise_model=noise)


def _run_on_simulator(
    qc: QuantumCircuit,
    shots: int,
    simulator: AerSimulator,
    seed: int | None = None,
) -> list[str]:
    """Execute circuit on Aer simulator with individual shot memory."""
    qc_t = transpile(qc, simulator)
    result = simulator.run(
        qc_t, shots=shots, memory=True, seed_simulator=seed
    ).result()
    return result.get_memory()


def _run_on_hardware(qc: QuantumCircuit, shots: int) -> tuple[list[str], str, str]:
    """Execute circuit on real IBM Quantum hardware backend."""
    global LAST_HARDWARE_BACKEND, LAST_HARDWARE_JOB_ID
    token = os.environ.get("IBM_QUANTUM_TOKEN")
    if not token:
        raise RuntimeError(
            "IBM_QUANTUM_TOKEN environment variable is not set. "
            "Please configure it (e.g. export IBM_QUANTUM_TOKEN='...' or "
            "$env:IBM_QUANTUM_TOKEN='...') with your API token from "
            "https://quantum.cloud.ibm.com."
        )
    instance = os.environ.get("IBM_QUANTUM_INSTANCE")
    channel = os.environ.get("IBM_QUANTUM_CHANNEL") or (
        "ibm_cloud" if instance and "bluemix" in instance else "ibm_quantum_platform"
    )
    service = QiskitRuntimeService(
        channel=channel,
        token=token,
        instance=instance,
    )
    backend_obj = service.least_busy(
        operational=True,
        simulator=False,
        min_num_qubits=qc.num_qubits,
    )
    pm = generate_preset_pass_manager(backend=backend_obj, optimization_level=1)
    isa_circuit = pm.run(qc)
    sampler = Sampler(mode=backend_obj)
    job = sampler.run([isa_circuit], shots=shots)
    print(f"Submitted hardware job {job.job_id()} to backend {backend_obj.name}")
    bitstrings = job.result()[0].data.c.get_bitstrings()
    LAST_HARDWARE_BACKEND = backend_obj.name
    LAST_HARDWARE_JOB_ID = job.job_id()
    return bitstrings, backend_obj.name, job.job_id()


def generate_bits(
    n_bits: int = DEFAULT_N_BITS,
    n_qubits: int = DEFAULT_QUBITS,
    backend: str = "hardware",
    seed: int | None = None,
) -> list[int]:
    """Generate a bitstream of random binary digits using quantum circuits.

    Args:
        n_bits: Exact number of bits to generate (must be > 0).
        n_qubits: Qubits per circuit execution (1 to 16).
        backend: Target backend ('hardware' by default, or 'ideal', 'noisy' for offline testing).
        seed: Random seed for simulator repeatability (None for fresh runs).

    Returns:
        list[int]: Generated bits with exact length n_bits.
    """
    if n_bits <= 0:
        raise ValueError(f"n_bits must be positive, got {n_bits}")
    if not (MIN_QUBITS <= n_qubits <= MAX_QUBITS):
        raise ValueError(
            f"n_qubits must be between {MIN_QUBITS} and {MAX_QUBITS}, got {n_qubits}"
        )
    if backend not in VALID_BACKENDS:
        raise ValueError(
            f"Invalid backend '{backend}'. Allowed values are: {VALID_BACKENDS}"
        )

    qc = build_qrng_circuit(n_qubits=n_qubits)
    shots = math.ceil(n_bits / n_qubits)

    if backend == "hardware":
        shot_memory, _, _ = _run_on_hardware(qc, shots)
    elif backend == "ideal":
        sim = AerSimulator()
        shot_memory = _run_on_simulator(qc, shots, sim, seed)
    elif backend == "noisy":
        sim = make_noisy_simulator()
        shot_memory = _run_on_simulator(qc, shots, sim, seed)
    else:
        raise ValueError(f"Unsupported backend '{backend}'")

    # Qiskit outputs bitstrings in little-endian order (qubit 0 at the right).
    # Reversing each shot string with [::-1] aligns character i with qubit i.
    bits: list[int] = []
    for shot in shot_memory:
        for char in shot[::-1]:
            bits.append(int(char))
            if len(bits) == n_bits:
                return bits
    return bits


def bits_to_numbers(bits: list[int], n_qubits: int = DEFAULT_QUBITS) -> list[int]:
    """Convert bitstream into integer numbers of n_qubits bit-depth.

    Args:
        bits: List of binary integers (0 or 1).
        n_qubits: Bits per output number (e.g. 8 produces 0..255).

    Returns:
        list[int]: Converted integers. Trailing incomplete chunks are dropped.
    """
    if not (MIN_QUBITS <= n_qubits <= MAX_QUBITS):
        raise ValueError(
            f"n_qubits must be between {MIN_QUBITS} and {MAX_QUBITS}, got {n_qubits}"
        )
    return [
        int("".join(map(str, bits[i : i + n_qubits])), 2)
        for i in range(0, len(bits) - n_qubits + 1, n_qubits)
    ]


def save_bits(bits: list[int], path: str | Path, **metadata) -> Path:
    """Save bit list and metadata to a JSON file conforming to project contract.

    Args:
        bits: List of binary digits.
        path: Destination file path.
        **metadata: Optional metadata keys (source, n_qubits, seed, job_id, etc.).

    Returns:
        Path: Path to saved file.
    """
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "source": metadata.get("source", "unknown"),
        "n_qubits": metadata.get("n_qubits", DEFAULT_QUBITS),
        "n_bits": len(bits),
        "seed": metadata.get("seed", None),
        "job_id": metadata.get("job_id", None),
        "created": metadata.get("created", datetime.now().isoformat()),
        "bits": bits,
    }
    for key, val in metadata.items():
        if key not in payload:
            payload[key] = val

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    return output_path


def load_bits(path: str | Path) -> list[int]:
    """Load bit list from a JSON file.

    Args:
        path: Path to the JSON file.

    Returns:
        list[int]: Stored bits list.
    """
    input_path = Path(path)
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["bits"]


def load_dataset(path: str | Path) -> dict:
    """Load full dataset dictionary including metadata and bits.

    Args:
        path: Path to the JSON file.

    Returns:
        dict: Full JSON dictionary.
    """
    input_path = Path(path)
    with open(input_path, "r", encoding="utf-8") as f:
        return json.load(f)
