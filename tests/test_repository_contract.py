import hashlib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "docs" / "research" / "2026-05-08"


class RepositoryContractTests(unittest.TestCase):
    def test_required_navigation_and_domain_documents_exist(self) -> None:
        required = [
            ROOT / "AGENTS.md",
            ROOT / "CONTEXT.md",
            ROOT / "PROJECT.md",
            ROOT / "README.md",
            ROOT / ".github" / "workflows" / "ci.yml",
            ROOT / "docs" / "adr" / "0001-preserve-the-paused-plan.md",
            ROOT / "docs" / "agents" / "domain.md",
            ROOT / "docs" / "agents" / "issue-tracker.md",
            ROOT / "docs" / "agents" / "triage-labels.md",
            RESEARCH / "README.md",
        ]

        for path in required:
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertTrue(path.is_file())

    def test_ci_runs_the_contract_with_read_only_permissions(self) -> None:
        workflow = (
            ROOT / ".github" / "workflows" / "ci.yml"
        ).read_text(encoding="utf-8")

        self.assertIn("contents: read", workflow)
        self.assertIn("python3 -m unittest discover -s tests -v", workflow)
        self.assertNotIn("pull-requests: write", workflow)

    def test_project_state_does_not_claim_a_deployment_or_implementation(self) -> None:
        project = (ROOT / "PROJECT.md").read_text(encoding="utf-8")

        self.assertIn("Lifecycle: paused planned project", project)
        self.assertIn("Deployment type: none", project)
        self.assertIn("GitHub implementation: README-only scaffold", project)
        self.assertIn("Public hostname: NXDOMAIN", project)

    def test_context_uses_the_locked_printmaking_language(self) -> None:
        context = (ROOT / "CONTEXT.md").read_text(encoding="utf-8")

        for term in ("**Plate**", "**Block**", "**Patch**", "**Pigment**"):
            with self.subTest(term=term):
                self.assertIn(term, context)
        self.assertIn("water-based pigment", context)
        self.assertIn("Avoid: ink", context)

    def test_original_research_inputs_are_preserved_byte_for_byte(self) -> None:
        expected = {
            "plate-editor-CONTEXT.md": (
                "dc9e9d015270ffc7173a4c7667d8a808"
                "598eff5c7107f3fa84178c138391468f"
            ),
            "plate-editor-proposal.md": (
                "2b6c71e95afdcb1c162b88b7d32d654"
                "27b45331065ee1750f4d5493b552a91f7"
            ),
            "plate-editor-grill-questions.md": (
                "5c106014eb2d0dba0913b5b383608f82"
                "bb80abaa8f9e8b154d0d33da8bb8b10e"
            ),
            "editor-build-plan-v1.md": (
                "6f4c9f9069d379162a1bd1ece4efe73b"
                "fbc5aa43c0aadd104538bd54bf11f3e0"
            ),
        }

        for name, digest in expected.items():
            with self.subTest(name=name):
                payload = (RESEARCH / name).read_bytes()
                self.assertEqual(hashlib.sha256(payload).hexdigest(), digest)

    def test_historical_plan_is_not_presented_as_live_operations(self) -> None:
        provenance = (RESEARCH / "README.md").read_text(encoding="utf-8")
        adr = (
            ROOT / "docs" / "adr" / "0001-preserve-the-paused-plan.md"
        ).read_text(encoding="utf-8")

        self.assertIn("historical research inputs", provenance.lower())
        self.assertIn("not executable instructions", provenance.lower())
        self.assertIn("Status: accepted", adr)
        self.assertIn("no deployment", adr.lower())


if __name__ == "__main__":
    unittest.main()
