import importlib.util
import unittest
from pathlib import Path

PATH=Path(__file__).resolve().parents[1]/"skills/nutrition-setup/scripts/rewe_cart_by_id.py"
SPEC=importlib.util.spec_from_file_location("rewe_cart_by_id",PATH)
MODULE=importlib.util.module_from_spec(SPEC)
import sys
sys.modules[SPEC.name]=MODULE
SPEC.loader.exec_module(MODULE)


class ProductIdTests(unittest.TestCase):
    def setUp(self):
        self.one={"id":"7144527","variant_id":"KP4QGSX5","title":"REWE Beste Wahl Kulturheidelbeeren 500g"}
        self.two={"id":"8245760","variant_id":"34AD3HTP","title":"ja! Skyr Natur 500g"}
        self.catalogue={"favorites_expected":1,"purchased_expected":1,"favorites":[self.one],"purchased":[self.two]}

    def test_all_good(self):
        targets=MODULE.prepare_targets({"items":[{"id":"7144527","quantity":2}]},self.catalogue)
        self.assertEqual(targets[0].url, "https://www.rewe.de/shop/products/7144527")
        self.assertEqual(targets[0].quantity,2)

    def test_invalid_quantity(self):
        for bad in (-1,0,1.5,301,True,"3"):
            with self.subTest(bad=bad),self.assertRaises(ValueError):
                MODULE.prepare_targets({"items":[{"id":"7144527","quantity":bad}]},self.catalogue)

    def test_missing_and_ambiguous_products(self):
        for bad in ("999999","../checkout"):
            with self.subTest(bad=bad),self.assertRaises(ValueError):
                MODULE.prepare_targets({"items":[{"id":bad,"quantity":1}]},self.catalogue)

    def test_duplicate_product(self):
        with self.assertRaises(ValueError):
            MODULE.prepare_targets({"items":[{"id":"7144527","quantity":1},{"id":"7144527","quantity":2}]},self.catalogue)

    def test_incomplete_catalogue(self):
        c=dict(self.catalogue,favorites_expected=120)
        with self.assertRaises(ValueError):
            MODULE.prepare_targets({"items":[{"id":"7144527","quantity":1}]},c)

    def test_price_parser(self):
        self.assertEqual(MODULE.german_price("1,29 €"), MODULE.Decimal("1.29"))
        self.assertEqual(MODULE.german_price("1.234,56 €"), MODULE.Decimal("1234.56"))
        self.assertIsNone(MODULE.german_price("not available"))

    def test_price_cap_rejected_if_exceeded(self):
        from unittest.mock import patch
        target=MODULE.prepare_targets(
            {"items":[{"id":"7144527","quantity":2,"max_unit_price_eur":"2.99"}]},
            self.catalogue
        )[0]
        state={"url":target.url,"title":target.title,"quantity":0,
               "price_text":"3,29 €","can_add":True}
        with patch.object(MODULE,"open_product",return_value=state):
            with self.assertRaisesRegex(RuntimeError,"exceeds"):
                MODULE.run(target,apply=True)

    def test_exact_title_and_id_verification(self):
        target=MODULE.prepare_targets({"items":[{"id":"7144527","quantity":1}]},self.catalogue)[0]
        MODULE.assert_same_product(target,{"url":target.url,"title":target.title})
        MODULE.assert_same_product(target,{"url":target.url+"?variantArticleId=OTHER","title":target.title})
        for state in [
            {"url":target.url,"title":"different product"},
            {"url":"https://www.rewe.de/shop/products/4444444","title":target.title},
        ]:
            with self.assertRaises(RuntimeError):
                MODULE.assert_same_product(target,state)


if __name__=="__main__":
    unittest.main()
