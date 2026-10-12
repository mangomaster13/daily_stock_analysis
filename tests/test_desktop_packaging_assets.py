# -*- coding: utf-8 -*-
"""Static contracts for third-party data bundled in desktop backends."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class DesktopPackagingAssetsTestCase(unittest.TestCase):
    """Keep Windows and macOS PyInstaller package-data rules aligned."""

    repo_root = Path(__file__).resolve().parent.parent

    def test_stock_caches_follow_desktop_database_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            data_dir = Path(directory) / "Application Support" / "data"
            result = subprocess.run(
                [sys.executable, "-c", "\n".join([
                    "import json",
                    "from src.services.stock_index_remote_service import RemoteStockIndexSettings, get_remote_stock_index_cache_path",
                    "from src.services.name_to_code_resolver import _AKSHARE_DISK_CACHE_PATH",
                    "print(json.dumps([str(get_remote_stock_index_cache_path()), str(RemoteStockIndexSettings().cache_path), str(_AKSHARE_DISK_CACHE_PATH)]))",
                ])],
                cwd=self.repo_root,
                env={**os.environ, "DATABASE_PATH": str(data_dir / "stock_analysis.db")},
                capture_output=True, text=True, check=True,
            )
            self.assertEqual(json.loads(result.stdout), [
                str(data_dir / "cache" / "stocks.index.json"),
                str(data_dir / "cache" / "stocks.index.json"),
                str(data_dir / "cache" / "akshare_name_map.json"),
            ])

    def test_orjson_is_declared_bundled_and_probed(self) -> None:
        requirements = (self.repo_root / "requirements.txt").read_text(encoding="utf-8")
        main = (self.repo_root / "main.py").read_text(encoding="utf-8")
        macos_script = (self.repo_root / "scripts" / "build-backend-macos.sh").read_text(
            encoding="utf-8"
        )
        windows_script = (self.repo_root / "scripts" / "build-backend.ps1").read_text(
            encoding="utf-8"
        )

        self.assertIn("orjson>=3.10,<4", requirements)
        self.assertIn('"orjson"', macos_script)
        self.assertIn("'orjson'", windows_script)
        self.assertIn('DSA_PACKAGED_IMPORT_PROBE="${module}"', macos_script)
        self.assertIn("$env:DSA_PACKAGED_IMPORT_PROBE = $module", windows_script)
        self.assertIn('importlib.import_module(_packaged_import_probe)', main)

    def test_scripts_collect_and_verify_akshare_calendar_data(self) -> None:
        macos_script = (self.repo_root / "scripts" / "build-backend-macos.sh").read_text(
            encoding="utf-8"
        )
        windows_script = (self.repo_root / "scripts" / "build-backend.ps1").read_text(
            encoding="utf-8"
        )

        self.assertIn("--collect-data akshare", macos_script)
        self.assertIn("'--collect-data', 'akshare'", windows_script)
        self.assertIn("_internal/akshare/file_fold/calendar.json", macos_script)
        self.assertIn("_internal\\akshare\\file_fold\\calendar.json", windows_script)


if __name__ == "__main__":
    unittest.main()
