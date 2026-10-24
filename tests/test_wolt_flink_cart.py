"""Browser automation regressions without opening or mutating a real cart."""

import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "nutrition-setup" / "scripts" / "wolt_flink_cart.py"
spec = importlib.util.spec_from_file_location("wolt_flink_cart", SCRIPT)
shopping = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shopping)


class BrowserOperatorTests(unittest.TestCase):
    def test_inspection_builds_short_item_urls(self):
        import json
        from unittest.mock import patch
        item_id = "05da02c1d063e42d2d0a78ab"
        payload = {"query":"Blumenkohl","heading_query":"Blumenkohl","loading_query":None,
                   "items":[{"title":"❄️ Ja! Blumenkohl, 1 kg","price":"2,39 €","quantity":0,"item_id":item_id}]}
        with patch.object(shopping,"browser",return_value=json.dumps(payload)):
            result = shopping.inspect_items()
        self.assertEqual(result["items"][0]["url"], shopping.WOLT_URL_BASE + item_id)


    def test_increment_ref_is_scoped_to_exact_product_card(self):
        tree = """
- button "Preis 0,99 € Gurke 1 Stk. ..." [ref=e1]
- heading "Gurke 1 Stk." [level=3, ref=e2]
- button "Weiteren Artikel hinzufügen" [ref=e3]
- button "Preis 0,79 € Gurke Mini 1 Stk. ..." [ref=e4]
- heading "Gurke Mini 1 Stk." [level=3, ref=e5]
- button "Produktinfo" [ref=e6]
- button "Weiteren Artikel hinzufügen" [ref=e7]
- button "Preis 1,69 € Bio Gurke 1 Stk. ..." [ref=e8]
- heading "Bio Gurke 1 Stk." [level=3, ref=e9]
- button "Weiteren Artikel hinzufügen" [ref=e10]
"""
        self.assertEqual(shopping.find_increment_ref(tree, "Gurke Mini 1 Stk."), "@e7")
        with self.assertRaisesRegex(RuntimeError, "Expected one product"):
            shopping.find_increment_ref(tree, "Sellerie")

    def test_resume_exact_prompt_uses_ja_not_nein(self):
        before = '- heading "Bestellung fortsetzen?" [level=2, ref=e40]\n- button "Nein" [ref=e41]\n- button "Ja" [ref=e42]'
        after = '- button "41 Bestellung ansehen 71,89 €" [ref=e43]'
        calls = []
        def fake_browser(*args, **_kwargs):
            calls.append(args)
            if args == ("snapshot", "-i"):
                return before if len([c for c in calls if c == args]) == 1 else after
            return "✓ Done"
        with patch.object(shopping, "browser", side_effect=fake_browser):
            self.assertTrue(shopping.resume_saved_cart())
        self.assertIn(("click", "@e42"), calls)
        self.assertNotIn(("click", "@e41"), calls)

    def test_does_not_dismiss_unrecognized_resume_prompt(self):
        tree = '- heading "Bestellung fortsetzen?" [level=2, ref=e40]\n- button "Nein" [ref=e41]'
        with patch.object(shopping, "browser", return_value=tree) as b:
            with self.assertRaisesRegex(RuntimeError, "Ja button missing"):
                shopping.resume_saved_cart()
            b.assert_called_once_with("snapshot", "-i")

    def test_reload_restores_saved_cart_without_changing_count(self):
        with (patch.object(shopping, "cart_counter", side_effect=[41, 41]),
              patch.object(shopping, "resume_saved_cart", return_value=True),
              patch.object(shopping, "browser") as browser):
            shopping.safe_reload()
        browser.assert_called_once_with("reload", timeout=48)

    def test_reload_stops_if_cart_count_changed(self):
        with (patch.object(shopping, "cart_counter", side_effect=[41, 0]),
              patch.object(shopping, "resume_saved_cart", return_value=True),
              patch.object(shopping, "browser") as browser):
            with self.assertRaisesRegex(RuntimeError, "Cart changed"):
                shopping.safe_reload()
        browser.assert_called_once_with("reload", timeout=48)

    def test_completed_same_query_does_not_trigger_refresh(self):
        done = {"query": "Paprika", "heading_query": "Paprika", "loading_query": None,
                "items": [{"title": "Paprika Rot 1 Stk.", "quantity": 0}]}
        with (patch.object(shopping, "inspect_items", return_value=done),
              patch.object(shopping, "resume_saved_cart", return_value=False),
              patch.object(shopping, "safe_reload") as reload,
              patch.object(shopping.time, "sleep")):
            shopping.wait_for_search("Paprika")
        reload.assert_not_called()


if __name__ == "__main__":
    unittest.main()
