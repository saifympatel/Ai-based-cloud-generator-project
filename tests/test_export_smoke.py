import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from export import packager


class ExportSmokeTest(unittest.TestCase):
    def test_export_contains_required_deliverables(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            archive_path = workspace / "AI-Generated-Project.zip"

            with patch.object(packager, "BASE_DIR", workspace):
                packager.create_complete_export_package(str(archive_path))

            with zipfile.ZipFile(archive_path) as archive:
                files = set(archive.namelist())

            expected_files = {
                "README.md",
                "security-and-cost-report.md",
                "architecture/architecture.json",
                "requirements/requirements.json",
                "backend/main.py",
                "frontend/App.jsx",
                "database/schema.sql",
                "docker/docker-compose.yml",
                "terraform/main.tf",
            }
            self.assertTrue(expected_files.issubset(files))


if __name__ == "__main__":
    unittest.main()