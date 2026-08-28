import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SKILL = ROOT / "skills" / "data-engineering"


class DataEngineeringSpecialistDepthTests(unittest.TestCase):
    def test_core_contract_names_non_negotiable_data_guarantees(self) -> None:
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8").lower()
        for phrase in (
            "data contract",
            "missingness",
            "content identity",
            "reconstruct",
            "point-in-time",
        ):
            self.assertIn(phrase, text)

    def test_references_cover_temporal_missingness_and_exact_reconstruction(self) -> None:
        source = (SKILL / "references" / "source-and-time-semantics.md").read_text(encoding="utf-8").lower()
        repro = (SKILL / "references" / "experiment-data-and-reproducibility.md").read_text(encoding="utf-8").lower()
        self.assertIn("not yet published", source)
        self.assertIn("source unavailable", source)
        self.assertIn("canonical", repro)
        self.assertIn("byte", repro)

    def test_output_evals_require_contract_missingness_and_reconstruction_evidence(self) -> None:
        data = json.loads(
            (ROOT / "tests" / "skills" / "data-engineering" / "output-evals.json").read_text(encoding="utf-8")
        )
        assertion_text = " ".join(
            assertion["text"].lower()
            for case in data["evals"]
            for assertion in case["assertions"]
        )
        self.assertIn("data contract", assertion_text)
        self.assertIn("missingness", assertion_text)
        self.assertIn("reconstruct", assertion_text)


if __name__ == "__main__":
    unittest.main()
