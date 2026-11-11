"""QRNG statistical comparison and validation module.

This file loads the QRNG datasets, computes summary statistics, runs the
recommended randomness tests, and compares the results against a Python
`random` baseline.

The analysis focuses on the four tasks requested for Person 2:
1. Monobit frequency test
2. Runs test
3. Shannon entropy
4. Autocorrelation analysis
"""

from __future__ import annotations

import json
import math
import random
from collections import Counter
from pathlib import Path
from statistics import NormalDist
from typing import Iterable

DATA_DIR = Path(__file__).resolve().parent / "data"
HARDWARE_PATH = DATA_DIR / "quantum_bits_hardware.json"
NOISY_PATH = DATA_DIR / "quantum_bits_noisy.json"


def load_dataset(path: str | Path) -> dict:
    """Load a dataset JSON file and return the parsed dictionary."""
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def load_bits(path: str | Path) -> list[int]:
    """Return only the raw bit list from a dataset JSON file."""
    dataset = load_dataset(path)
    return dataset["bits"]


def bits_to_numbers(bits: Iterable[int], n_qubits: int = 8) -> list[int]:
    """Convert a bitstream into integer values from contiguous n_qubit blocks."""
    bit_list = list(bits)
    if n_qubits <= 0:
        raise ValueError("n_qubits must be greater than 0")

    return [
        int("".join(str(bit) for bit in bit_list[i : i + n_qubits]), 2)
        for i in range(0, len(bit_list) - n_qubits + 1, n_qubits)
    ]


def shannon_entropy(bits: list[int]) -> float:
    """Return the Shannon entropy of a binary sequence in bits/bit."""
    if not bits:
        return 0.0

    p1 = sum(bits) / len(bits)
    p0 = 1.0 - p1
    entropy = 0.0
    for p in (p0, p1):
        if p > 0:
            entropy -= p * math.log2(p)
    return entropy


def count_runs(bits: list[int]) -> int:
    """Count the number of runs in a binary sequence."""
    if not bits:
        return 0

    runs = 1
    for previous, current in zip(bits, bits[1:]):
        if previous != current:
            runs += 1
    return runs


def run_length_distribution(bits: list[int]) -> dict[int, int]:
    """Count the frequency of run lengths in the bitstream."""
    if not bits:
        return {}

    lengths: list[int] = []
    current_length = 1
    for previous, current in zip(bits, bits[1:]):
        if previous == current:
            current_length += 1
        else:
            lengths.append(current_length)
            current_length = 1
    lengths.append(current_length)

    return dict(sorted(Counter(lengths).items()))


def monobit_frequency_test(bits: list[int]) -> dict:
    """Perform the monobit frequency test using a standard normal approximation."""
    n = len(bits)
    if n == 0:
        raise ValueError("Cannot run monobit test on an empty bit list.")

    ones = sum(bits)
    zeros = n - ones
    p_hat = ones / n

    # For a fair coin, the test statistic is approximately normal.
    # z = |2*ones - n| / sqrt(n)
    z_score = abs(2 * ones - n) / math.sqrt(n)
    p_value = 2 * (1.0 - NormalDist().cdf(z_score))

    return {
        "n_bits": n,
        "ones": ones,
        "zeros": zeros,
        "proportion_ones": p_hat,
        "expected_proportion": 0.5,
        "z_score": z_score,
        "p_value": p_value,
    }


def runs_test(bits: list[int]) -> dict:
    """Summarize run structure as a basic independence test for binary randomness."""
    n = len(bits)
    if n == 0:
        raise ValueError("Cannot run runs test on an empty bit list.")

    total_runs = count_runs(bits)
    transitions = total_runs - 1
    run_lengths = run_length_distribution(bits)

    return {
        "n_bits": n,
        "total_runs": total_runs,
        "transitions": transitions,
        "transition_rate": transitions / max(n - 1, 1),
        "run_lengths": run_lengths,
    }


def autocorrelation(bits: list[int], lag: int = 1) -> float:
    """Return the lag-k autocorrelation for a binary sequence."""
    if lag < 1:
        raise ValueError("lag must be at least 1")
    if len(bits) <= lag:
        return 0.0

    mean_value = sum(bits) / len(bits)
    numerator = sum(
        (bits[i] - mean_value) * (bits[i + lag] - mean_value)
        for i in range(len(bits) - lag)
    )
    denominator = sum((value - mean_value) ** 2 for value in bits[:-lag])

    if denominator == 0:
        return 0.0
    return numerator / denominator


def generate_python_random_bits(n_bits: int = 1000, seed: int | None = None) -> list[int]:
    """Generate a baseline bitstream using Python's `random` module."""
    rng = random.Random(seed)
    return [rng.randint(0, 1) for _ in range(n_bits)]


def summarize_dataset(label: str, bits: list[int]) -> dict:
    """Create a report dictionary for a single dataset."""
    numbers = bits_to_numbers(bits, n_qubits=8)
    return {
        "label": label,
        "n_bits": len(bits),
        "ones": sum(bits),
        "zeros": len(bits) - sum(bits),
        "proportion_ones": sum(bits) / len(bits),
        "entropy": shannon_entropy(bits),
        "monobit": monobit_frequency_test(bits),
        "runs": runs_test(bits),
        "autocorrelation_lag_1": autocorrelation(bits, lag=1),
        "first_numbers": numbers[:10],
    }


def compare_against_python_random(bits: list[int], python_bits: list[int]) -> dict:
    """Compare the QRNG dataset against a classical Python random baseline."""
    q_summary = summarize_dataset("qrng", bits)
    py_summary = summarize_dataset("python_random", python_bits)

    return {
        "qrng_proportion_ones": q_summary["proportion_ones"],
        "python_proportion_ones": py_summary["proportion_ones"],
        "difference_in_proportion": q_summary["proportion_ones"] - py_summary["proportion_ones"],
        "qrng_entropy": q_summary["entropy"],
        "python_entropy": py_summary["entropy"],
        "qrng_lag_1_autocorrelation": q_summary["autocorrelation_lag_1"],
        "python_lag_1_autocorrelation": py_summary["autocorrelation_lag_1"],
    }


def build_report() -> dict:
    """Load all project datasets and build the comparison report."""
    hardware_dataset = load_dataset(HARDWARE_PATH)
    noisy_dataset = load_dataset(NOISY_PATH)
    hardware_bits = hardware_dataset["bits"]
    noisy_bits = noisy_dataset["bits"]

    baseline_seed = 42
    python_bits = generate_python_random_bits(len(hardware_bits), seed=baseline_seed)

    return {
        "hardware": {
            "source": hardware_dataset.get("source"),
            "job_id": hardware_dataset.get("job_id"),
            **summarize_dataset("hardware", hardware_bits),
        },
        "noisy": {
            "source": noisy_dataset.get("source"),
            "job_id": noisy_dataset.get("job_id"),
            **summarize_dataset("noisy", noisy_bits),
        },
        "python_random_baseline": {
            "seed": baseline_seed,
            "n_bits": len(python_bits),
            "proportion_ones": sum(python_bits) / len(python_bits),
            "entropy": shannon_entropy(python_bits),
            "monobit": monobit_frequency_test(python_bits),
            "runs": runs_test(python_bits),
            "autocorrelation_lag_1": autocorrelation(python_bits, lag=1),
        },
        "comparisons": {
            "hardware_vs_python": compare_against_python_random(hardware_bits, python_bits),
            "noisy_vs_python": compare_against_python_random(noisy_bits, python_bits),
        },
    }


def print_report(report: dict) -> None:
    """Pretty-print the report for the user."""
    print("QRNG Statistical Comparison Report")
    print("=" * 60)

    for label in ("hardware", "noisy"):
        entry = report[label]
        print(f"\n{label.upper()} DATASET")
        print(f"Source: {entry['source']}")
        print(f"Job ID: {entry['job_id']}")
        print(f"n_bits: {entry['n_bits']}")
        print(f"ones: {entry['ones']}")
        print(f"zeros: {entry['zeros']}")
        print(f"fraction_of_ones: {entry['proportion_ones']:.4f}")
        print(f"Shannon entropy: {entry['entropy']:.4f}")
        print(f"Monobit z-score: {entry['monobit']['z_score']:.4f}")
        print(f"Monobit p-value: {entry['monobit']['p_value']:.6f}")
        print(f"Total runs: {entry['runs']['total_runs']}")
        print(f"Transition rate: {entry['runs']['transition_rate']:.4f}")
        print(f"Lag-1 autocorrelation: {entry['autocorrelation_lag_1']:.4f}")
        print(f"First 10 8-bit numbers: {entry['first_numbers'][:10]}")

    print("\nPYTHON RANDOM BASELINE")
    print(f"seed: {report['python_random_baseline']['seed']}")
    print(f"fraction_of_ones: {report['python_random_baseline']['proportion_ones']:.4f}")
    print(f"Shannon entropy: {report['python_random_baseline']['entropy']:.4f}")
    print(f"Monobit z-score: {report['python_random_baseline']['monobit']['z_score']:.4f}")
    print(f"Monobit p-value: {report['python_random_baseline']['monobit']['p_value']:.6f}")
    print(f"Lag-1 autocorrelation: {report['python_random_baseline']['autocorrelation_lag_1']:.4f}")

    print("\nCOMPARISON AGAINST PYTHON RANDOM")
    for label, comparison in report["comparisons"].items():
        print(f"\n{label}")
        for key, value in comparison.items():
            if isinstance(value, float):
                print(f"  {key}: {value:.4f}")
            else:
                print(f"  {key}: {value}")


def main() -> None:
    """Generate the requested statistical comparison report."""
    report = build_report()
    print_report(report)


if __name__ == "__main__":
    main()
