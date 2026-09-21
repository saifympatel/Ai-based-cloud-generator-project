import json
import tempfile
import threading
import unittest
import urllib.request
import zipfile
from http.server import HTTPServer
from pathlib import Path
from unittest.mock import patch

from backend import mock_server
from export import packager


class ReleaseReadinessTest(unittest.TestCase):
    def test_mock_api_health_and_requirement_analysis(self):
        server = HTTPServer(("127.0.0.1", 0), mock_server.MockApiHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base_url = f"http://127.0.0.1:{server.server_port}"

        try:
            with urllib.request.urlopen(f"{base_url}/health") as response:
                health = json.load(response)
            self.assertEqual(health["status"], "healthy")

            payload = json.dumps({
                "domain": "lms",
                "expected_users": 15000,
                "monthly_budget_inr": 20000,
            }).encode("utf-8")
            request = urllib.request.Request(
                f"{base_url}/api/requirements/analyze",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(request) as response:
                requirement = json.load(response)

            self.assertEqual(requirement["domain"], "lms")
            self.assertEqual(requirement["users"], 15000)
            self.assertEqual(requirement["budget_monthly_inr"], 20000)
        finally:
            server.shutdown()
            thread.join(timeout=2)
            server.server_close()

    def test_export_has_deployment_artifacts_and_valid_metadata(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            archive_path = workspace / "AI-Generated-Project.zip"

            with patch.object(packager, "BASE_DIR", workspace):
                packager.create_complete_export_package(str(archive_path))

            with zipfile.ZipFile(archive_path) as archive:
                files = set(archive.namelist())
                architecture = json.loads(archive.read("architecture/architecture.json"))
                requirements = json.loads(archive.read("requirements/requirements.json"))
                summary = json.loads(archive.read("project-summary.json"))

            infrastructure_files = {
                "docker/docker-compose.yml",
                "docker/Dockerfile.backend",
                "docker/Dockerfile.frontend",
                "terraform/main.tf",
                "terraform/network.tf",
                "terraform/database.tf",
                "terraform/compute.tf",
                "terraform/storage.tf",
            }
            self.assertTrue(infrastructure_files.issubset(files))
            self.assertEqual(architecture["provider"], "AWS")
            self.assertEqual(requirements["traceability_coverage"], 100)
            self.assertEqual(summary["status"], "ready_for_delivery")
            self.assertIn("security_score", summary)
            self.assertIn("estimated_monthly_cost_inr", summary)
            self.assertIn("readiness", summary)
            self.assertEqual(summary["readiness"]["deployment_ready"], True)


if __name__ == "__main__":
    unittest.main()