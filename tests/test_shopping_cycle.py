"""REWE biweekly phase and weekly freshness routing regression tests."""
import importlib.util
from pathlib import Path
from datetime import date
import sys
import unittest

p=Path(__file__).resolve().parents[1]/"skills/nutrition-setup/scripts/shopping_cycle.py"
spec=importlib.util.spec_from_file_location("shopping_cycle",p)
mod=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=mod
spec.loader.exec_module(mod)


class CycleTests(unittest.TestCase):
    def test_anchor_saturday_and_sunday_same_rewe_week(self):
        for d in (date(2026,10,10),date(2026,10,11)):
            c=mod.shopping_cycle(d)
            self.assertTrue(c.is_rewe_anchor)
            self.assertEqual(c.primary_shop,"REWE")
            self.assertEqual(c.weekend_start,date(2026,10,10))

    def test_intervening_weekend_wolt_first(self):
        for d in (date(2026,10,17),date(2026,10,18)):
            c=mod.shopping_cycle(d)
            self.assertFalse(c.is_rewe_anchor)
            self.assertEqual(c.primary_shop,"Flink via Wolt")

    def test_second_and_third_rewe_anchor(self):
        self.assertTrue(mod.shopping_cycle(date(2026,10,25)).is_rewe_anchor)
        self.assertTrue(mod.shopping_cycle(date(2026,11,8)).is_rewe_anchor)

    def test_skipping_week_does_not_shift_phase(self):
        # Session on 11 Oct missed? The following dates are still fixed.
        self.assertFalse(mod.shopping_cycle(date(2026,10,18)).is_rewe_anchor)
        self.assertTrue(mod.shopping_cycle(date(2026,10,25)).is_rewe_anchor)

    def test_delivery_monday_not_valid_as_session_id(self):
        with self.assertRaisesRegex(ValueError,"Saturday/Sunday"):
            mod.shopping_cycle(date(2026,10,12))

    def test_nonexistent_prior_anchor(self):
        with self.assertRaisesRegex(ValueError,"earlier weekends"):
            mod.shopping_cycle(date(2026,10,4))


if __name__=="__main__":
    unittest.main()
