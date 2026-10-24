import importlib.util
from pathlib import Path
import sys
import unittest
P=Path(__file__).resolve().parents[1]/"skills/nutrition-setup/scripts/rewe_sync_notion.py"
S=importlib.util.spec_from_file_location("rewe_sync_notion",P)
M=importlib.util.module_from_spec(S)
sys.modules[S.name]=M
S.loader.exec_module(M)
class SyncTest(unittest.TestCase):
    def test_preserves_manual_fields(self):
        row={"id":"7144527","title":"REWE Beste Wahl Kulturheidelbeeren 500g",
             "variant_id":"KP4QGSX5","url":"https://www.rewe.de/shop/products/7144527?variantArticleId=KP4QGSX5",
             "price_text":"3,29 €","unavailable":False}
        props=M.properties(row,{"Favoriten","Bereits gekauft"})
        for k in ("Zuordnung Lebensmittel","Aktiv für Einkauf","Anmerkungen"):
            self.assertNotIn(k,props)
        self.assertEqual(props["REWE-ID"]["rich_text"][0]["text"]["content"],"7144527")
    def test_verification_ignores_other_merchants_and_preserves_rewe_checks(self):
        def page(id,title,rewe_id=None,icon=None):
            return {"id":id,"icon":icon,"properties":{
                "Produkt":{"title":[{"plain_text":title}]},
                "REWE-ID":{"rich_text":[{"plain_text":rewe_id}]} if rewe_id else {"rich_text":[]},
            }}
        rewe=page("rewe","REWE Linsen","7814109")
        wolt=page("wolt","❄️ Wolt TK-Blumenkohl")
        result=M.verify_rewe_sync([rewe,wolt],{"7814109"})
        self.assertEqual(result["total_rows"],2)
        self.assertEqual(result["rewe_rows"],1)
        self.assertEqual(result["unique_rewe_ids"],1)
        self.assertFalse(result["missing_ids"] or result["duplicate_ids"] or result["invalid_pages"])

        duplicate=M.verify_rewe_sync([rewe,page("rewe2","REWE Linsen","7814109"),wolt],{"7814109"})
        self.assertEqual(duplicate["duplicate_ids"],{"7814109"})
        missing=M.verify_rewe_sync([wolt],{"7814109"})
        self.assertEqual(missing["missing_ids"],{"7814109"})
        invalid=M.verify_rewe_sync([page("bad","🥝 Kiwi","7814109"),wolt],{"7814109"})
        self.assertEqual(invalid["invalid_pages"],["bad"])

    def test_price_and_emoji(self):
        self.assertEqual(M.price("3,29 €"),3.29)
        self.assertEqual(M.clean("🥝 Kiwi"),"Kiwi")
if __name__=="__main__":
    unittest.main()
