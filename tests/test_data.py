"""Regression checks for dashboard data returned from Streamlit's resource cache."""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import data  # noqa: E402


class LoadAssetsTests(unittest.TestCase):
    def test_relabels_stale_cached_segments_without_mutating_cache(self):
        cached = pd.DataFrame({"Cluster": [0, 1, 2, 3], "Segment": [f"Segment 0{i}" for i in range(1, 5)]})
        with patch.object(data, "_load_assets", return_value=(cached, None, None, None)):
            customers, _, _, _ = data.load_assets()

        self.assertEqual(customers["Segment"].tolist(), list(data.SEGMENT_NAMES.values()))
        self.assertEqual(cached["Segment"].tolist(), [f"Segment 0{i}" for i in range(1, 5)])


if __name__ == "__main__":
    unittest.main()
