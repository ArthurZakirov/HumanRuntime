import importlib.util
import sys
import unittest
from pathlib import Path

PATH=Path(__file__).resolve().parents[1]/"skills/nutrition-setup/scripts/rewe_export_catalog.py"
SPEC=importlib.util.spec_from_file_location("rewe_export_catalog",PATH)
MODULE=importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name]=MODULE
SPEC.loader.exec_module(MODULE)


class ExportTest(unittest.TestCase):
    def test_parses_product_and_variant_ids(self):
        items=[{"title":"Blaubeeren","href":"/shop/products/7144527?variantArticleId=KP4QGSX5"}]
        rows=MODULE.parse_listings(items,"favorites")
        self.assertEqual(rows[0]["id"],"7144527")
        self.assertEqual(rows[0]["variant_id"],"KP4QGSX5")
        self.assertEqual(rows[0]["url"],"https://www.rewe.de/shop/products/7144527?variantArticleId=KP4QGSX5")

    def test_url_must_be_real_product(self):
        with self.assertRaises(ValueError):
            MODULE.parse_listings([{"title":"X","href":"/shop/checkout/payment"}],"favorites")
