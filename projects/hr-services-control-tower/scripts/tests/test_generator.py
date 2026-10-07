from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import sys


SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from generate_synthetic_data import generate, sha256_file  # noqa: E402


class SyntheticGeneratorTests(unittest.TestCase):
    def test_small_generation_is_valid_and_reproducible(self) -> None:
        with tempfile.TemporaryDirectory() as first_temp, tempfile.TemporaryDirectory() as second_temp:
            first_root = Path(first_temp)
            second_root = Path(second_temp)
            first = generate(20260824, 500, first_root, False)
            second = generate(20260824, 500, second_root, False)

            self.assertTrue(first["validation"]["passed"])
            self.assertEqual(first["validation"]["metrics"]["case_count"], 500)
            self.assertEqual(
                sha256_file(first_root / "processed" / "fact_cases.csv"),
                sha256_file(second_root / "processed" / "fact_cases.csv"),
            )
            self.assertEqual(
                sha256_file(first_root / "processed" / "fact_case_events.csv"),
                sha256_file(second_root / "processed" / "fact_case_events.csv"),
            )
            self.assertGreater(
                next(row["rows"] for row in first["files"] if row["file"] == "hr_case_export.csv"),
                500,
            )


if __name__ == "__main__":
    unittest.main()

