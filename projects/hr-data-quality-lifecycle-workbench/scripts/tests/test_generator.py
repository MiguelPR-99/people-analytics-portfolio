from __future__ import annotations

import csv
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[2]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from config import synthetic_data_config as cfg  # noqa: E402
from scripts.generate_synthetic_data import (  # noqa: E402
    EVENT_FIELDS,
    POSITION_FIELDS,
    WORKER_FIELDS,
    generate_dataset,
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


class SyntheticDataGeneratorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.output_dir = Path(cls.temp_dir.name) / "data"
        cls.manifest = generate_dataset(cls.output_dir)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp_dir.cleanup()

    def test_expected_partitioned_files_and_schemas(self) -> None:
        files = self.manifest["files"]
        self.assertEqual(18, len(files))
        expected_headers = {
            "workers.csv": WORKER_FIELDS,
            "lifecycle_events.csv": EVENT_FIELDS,
            "positions.csv": POSITION_FIELDS,
        }
        for entry in files:
            path = self.output_dir / entry["path"]
            self.assertTrue(path.is_file(), entry["path"])
            with path.open("r", encoding="utf-8", newline="") as handle:
                reader = csv.reader(handle)
                header = next(reader)
                row_count = sum(1 for _ in reader)
            self.assertEqual(expected_headers[path.name], header)
            self.assertEqual(entry["rows"], row_count)
            self.assertEqual(entry["columns"], len(header))
            self.assertEqual(entry["sha256"], sha256(path))

    def test_population_reconciles(self) -> None:
        population = self.manifest["population"]
        self.assertEqual(cfg.DISTINCT_WORKERS, population["distinct_workers"])
        self.assertEqual(cfg.STARTING_EMPLOYED_WORKERS, population["starting_employed_workers"])
        self.assertEqual(cfg.ENDING_EMPLOYED_WORKERS, population["ending_employed_workers"])
        final_status = population["status_by_snapshot"][cfg.CUTOFF_DATE.isoformat()]
        self.assertEqual(cfg.DISTINCT_WORKERS, sum(final_status.values()))
        self.assertEqual(cfg.TERMINATIONS, final_status["Terminated"])

    def test_quality_rules_and_controlled_patterns(self) -> None:
        quality = self.manifest["quality_evaluation"]
        self.assertEqual([snapshot.isoformat() for snapshot in cfg.SNAPSHOT_DATES], list(quality["by_snapshot"]))
        for snapshot in cfg.SNAPSHOT_DATES:
            result = quality["by_snapshot"][snapshot.isoformat()]
            self.assertEqual(set(cfg.RULE_SEVERITY), set(result))
            for counts in result.values():
                self.assertEqual(counts["eligible"], counts["passed"] + counts["failed"])
                self.assertGreater(counts["eligible"], 0)
        self.assertTrue(all(check["passed"] for check in self.manifest["controlled_pattern_checks"].values()))
        final_score = quality["score_by_snapshot"][cfg.CUTOFF_DATE.isoformat()]
        self.assertGreaterEqual(final_score, 98.0)
        self.assertLessEqual(final_score, 99.8)

    def test_every_rule_has_injected_examples(self) -> None:
        totals = {rule: 0 for rule in cfg.RULE_SEVERITY}
        for snapshot_counts in self.manifest["injected_primary_issues"].values():
            for rule, count in snapshot_counts.items():
                totals[rule] += count
        self.assertTrue(all(count > 0 for count in totals.values()), totals)

    def test_prohibited_columns_are_absent(self) -> None:
        prohibited = set(self.manifest["privacy"]["prohibited_fields"])
        self.assertTrue(prohibited.isdisjoint(WORKER_FIELDS))
        self.assertTrue(prohibited.isdisjoint(EVENT_FIELDS))
        self.assertTrue(prohibited.isdisjoint(POSITION_FIELDS))
        self.assertFalse(self.manifest["privacy"]["prohibited_fields_present"])

    def test_generation_is_reproducible(self) -> None:
        generator = PROJECT_DIR / "scripts" / "generate_synthetic_data.py"
        with tempfile.TemporaryDirectory() as first_temp, tempfile.TemporaryDirectory() as second_temp:
            outputs = [Path(first_temp) / "data", Path(second_temp) / "data"]
            for hash_seed, output in zip(("101", "202"), outputs, strict=True):
                environment = dict(os.environ)
                environment["PYTHONHASHSEED"] = hash_seed
                completed = subprocess.run(
                    [sys.executable, str(generator), "--output-dir", str(output)],
                    cwd=PROJECT_DIR,
                    env=environment,
                    check=False,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(0, completed.returncode, completed.stderr)
            manifests = [json.loads((output / "manifest.json").read_text(encoding="utf-8")) for output in outputs]
            hashes = [{entry["path"]: entry["sha256"] for entry in manifest["files"]} for manifest in manifests]
            self.assertEqual(hashes[0], hashes[1])
            self.assertEqual(manifests[0], manifests[1])

    def test_existing_outputs_require_force(self) -> None:
        with self.assertRaises(FileExistsError):
            generate_dataset(self.output_dir)


if __name__ == "__main__":
    unittest.main()

