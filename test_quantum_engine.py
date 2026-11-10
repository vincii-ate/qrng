"""Acceptance checklist test suite for quantum_engine.py using unittest.

Offline checks only (uses 'ideal' and 'noisy' simulators, never hardware).
"""

import os
from pathlib import Path
import tempfile
import unittest

from quantum_engine import (
    build_qrng_circuit,
    generate_bits,
    bits_to_numbers,
    save_bits,
    load_bits,
    load_dataset,
)


class TestQuantumEngine(unittest.TestCase):
    def test_generate_bits_exact_length_and_values(self):
        bits = generate_bits(1000, backend="ideal")
        self.assertIsInstance(bits, list, "Must return a list")
        self.assertEqual(len(bits), 1000, f"Expected 1000 bits, got {len(bits)}")
        self.assertTrue(all(b in (0, 1) for b in bits), "All elements must be 0 or 1")

    def test_generate_bits_custom_qubits_trimming(self):
        # 1000 bits with 5 qubits requires 200 shots, exactly 1000 bits
        bits5 = generate_bits(1000, n_qubits=5, backend="ideal")
        self.assertEqual(len(bits5), 1000, f"Expected 1000 bits with 5 qubits, got {len(bits5)}")
        self.assertTrue(all(b in (0, 1) for b in bits5))

        # 1003 bits with 8 qubits requires 126 shots (1008 bits), trimmed to 1003
        bits_odd = generate_bits(1003, n_qubits=8, backend="ideal")
        self.assertEqual(len(bits_odd), 1003, f"Expected 1003 bits, got {len(bits_odd)}")

    def test_bits_to_numbers(self):
        bits = generate_bits(1000, n_qubits=8, backend="ideal")
        numbers = bits_to_numbers(bits, n_qubits=8)
        self.assertEqual(len(numbers), 125, f"Expected 125 numbers from 1000 bits, got {len(numbers)}")
        self.assertTrue(all(0 <= n <= 255 for n in numbers), "All numbers must be in 0..255")

        # Known bit sequence test: [1, 0, 0, 0, 0, 0, 0, 0] -> 128
        self.assertEqual(bits_to_numbers([1, 0, 0, 0, 0, 0, 0, 0], n_qubits=8), [128])
        # [0, 0, 0, 0, 0, 0, 0, 1] -> 1
        self.assertEqual(bits_to_numbers([0, 0, 0, 0, 0, 0, 0, 1], n_qubits=8), [1])

    def test_ideal_fraction_of_ones(self):
        bits = generate_bits(1000, backend="ideal", seed=42)
        frac = sum(bits) / len(bits)
        self.assertTrue(0.45 <= frac <= 0.55, f"Ideal fraction of ones was {frac}, expected roughly 0.50")

    def test_seed_reproducibility_and_unseeded_variation(self):
        run_a = generate_bits(100, backend="ideal", seed=12345)
        run_b = generate_bits(100, backend="ideal", seed=12345)
        self.assertEqual(run_a, run_b, "Two runs with identical seed must match")

        run1 = generate_bits(100, backend="ideal", seed=None)
        run2 = generate_bits(100, backend="ideal", seed=None)
        self.assertNotEqual(run1, run2, "Two unseeded runs must differ")

    def test_noisy_simulator_bias(self):
        # Over large sample (16,000 bits), noisy simulator fraction of 1s is significantly below ideal
        noisy_bits = generate_bits(16000, backend="noisy", seed=100)
        ideal_bits = generate_bits(16000, backend="ideal", seed=100)
        noisy_frac = sum(noisy_bits) / len(noisy_bits)
        ideal_frac = sum(ideal_bits) / len(ideal_bits)
        self.assertLess(noisy_frac, ideal_frac, f"Noisy fraction {noisy_frac} should be less than ideal {ideal_frac}")
        self.assertLess(noisy_frac, 0.49, f"Noisy fraction should be noticeably below 0.50, got {noisy_frac}")

    def test_bad_inputs_raise_value_error(self):
        with self.assertRaises(ValueError):
            generate_bits(0, backend="ideal")
        with self.assertRaises(ValueError):
            generate_bits(-10, backend="ideal")
        with self.assertRaises(ValueError):
            generate_bits(100, n_qubits=0, backend="ideal")
        with self.assertRaises(ValueError):
            generate_bits(100, n_qubits=17, backend="ideal")
        with self.assertRaises(ValueError):
            generate_bits(100, backend="unknown_backend")

    def test_hardware_without_token_raises_runtime_error(self):
        old_token = os.environ.pop("IBM_QUANTUM_TOKEN", None)
        try:
            with self.assertRaises(RuntimeError):
                generate_bits(100, backend="hardware")
        finally:
            if old_token is not None:
                os.environ["IBM_QUANTUM_TOKEN"] = old_token

    def test_json_roundtrip(self):
        bits = generate_bits(1000, backend="ideal", seed=777)
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test_bits.json"
            saved_path = save_bits(bits, path, source="aer_noisy", n_qubits=8, seed=777, job_id=None)
            self.assertTrue(saved_path.exists())
            loaded_bits = load_bits(path)
            self.assertEqual(loaded_bits, bits, "Loaded bits must strictly equal saved bits")

            dataset = load_dataset(path)
            self.assertEqual(dataset["source"], "aer_noisy")
            self.assertEqual(dataset["n_qubits"], 8)
            self.assertEqual(dataset["n_bits"], 1000)
            self.assertEqual(dataset["seed"], 777)
            self.assertIn("job_id", dataset)
            self.assertIn("created", dataset)
            self.assertEqual(dataset["bits"], bits)


if __name__ == "__main__":
    unittest.main()
