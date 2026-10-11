"""Pure regressions: shop-wide quantities, equivalence, and fail-closed behavior."""

import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'skills/nutrition-setup/scripts/reconcile_grocery_carts.py'
spec = importlib.util.spec_from_file_location('reconcile_grocery_carts', SCRIPT)
recon = importlib.util.module_from_spec(spec)
import sys
sys.modules[spec.name] = recon
spec.loader.exec_module(recon)


def manifest():
    return {
        'intents': [
            {'id':'eggs', 'label':'Freiland-Eier', 'target':30, 'unit':'Stück'},
            {'id':'ginger', 'label':'Ingwer-Zitrone', 'target':1, 'unit':'Packung','group':'tea'},
            {'id':'turmeric', 'label':'Kurkuma Chai', 'target':1, 'unit':'Packung','group':'tea'},
        ],
        'groups':[{'id':'tea','label':'Tees insgesamt','max_quantity':2,'unit':'Packung'}],
        'products':[
            {'merchant':'wolt','title':'Rewe Beste Wahl Respeggt Eier Freilandhaltung Kl. S-L 10 Stück','intent_id':'eggs','units_per_pack':10},
            {'merchant':'rewe','title':'REWE Beste Wahl Respeggt Eier Freilandhaltung 10 Stück','intent_id':'eggs','units_per_pack':10},
            {'merchant':'wolt','title':'Yogi Tea Bio Ingwer-Zitrone 30,6g (17 Beutel)','intent_id':'ginger','units_per_pack':1},
            {'merchant':'rewe','title':'Yogi Tea Bio Tee Kurkuma Chai 34g 17 Beutel','intent_id':'turmeric','units_per_pack':1},
        ]
    }


def cart(wolt_eggs=0, rewe_eggs=3, ginger=1, turmeric=1):
    lines=[]
    if wolt_eggs:
        lines.append(recon.CartLine('wolt','Rewe Beste Wahl Respeggt Eier Freilandhaltung Kl. S-L 10 Stück',wolt_eggs))
    if rewe_eggs:
        lines.append(recon.CartLine('rewe','REWE Beste Wahl Respeggt Eier Freilandhaltung 10 Stück',rewe_eggs))
    if ginger:
        lines.append(recon.CartLine('wolt','Yogi Tea Bio Ingwer-Zitrone 30,6g (17 Beutel)',ginger))
    if turmeric:
        lines.append(recon.CartLine('rewe','Yogi Tea Bio Tee Kurkuma Chai 34g 17 Beutel',turmeric))
    return lines


class CrossCartRules(unittest.TestCase):
    def test_current_fixed_two_shop_carts_pass(self):
        result=recon.audit(manifest(),cart())
        self.assertTrue(result['ok'],result['errors'])
        egg=next(g for g in result['goals'] if g['id']=='eggs')
        self.assertEqual(egg['actual'],'30')
        self.assertEqual(egg['merchants'],['rewe'])

    def test_original_six_egg_packs_block(self):
        result=recon.audit(manifest(),cart(wolt_eggs=3))
        self.assertFalse(result['ok'])
        self.assertTrue(any('OVERBUY Freiland-Eier: 60 Stück' in x for x in result['errors']))
        self.assertTrue(any('DUPLICATE SHOP ALLOCATION' in x for x in result['errors']))

    def test_splitting_is_explicit_even_without_overbuy(self):
        result=recon.audit(manifest(),cart(wolt_eggs=1,rewe_eggs=2))
        self.assertFalse(result['ok'])
        self.assertTrue(any('DUPLICATE SHOP ALLOCATION' in x for x in result['errors']))

    def test_allowed_split_valid_when_total_within_goal(self):
        model=manifest()
        model['intents'][0]['allow_split']=True
        result=recon.audit(model,cart(wolt_eggs=1,rewe_eggs=2))
        self.assertTrue(result['ok'],result['errors'])

    def test_distinct_tea_flavors_not_duplicates(self):
        result=recon.audit(manifest(),cart())
        self.assertFalse(any('tea' in x.lower() or 'chai' in x.lower() for x in result['errors']))
        self.assertEqual(result['groups'][0]['actual'],'2')

    def test_group_ceiling_blocks_extra_tea(self):
        result=recon.audit(manifest(),cart(ginger=2))
        self.assertFalse(result['ok'])
        self.assertTrue(any('GROUP CAP' in x for x in result['errors']))

    def test_unknown_listing_blocks_instead_of_guessing(self):
        result=recon.audit(manifest(),cart()+[recon.CartLine('rewe','Brandless Eggs 10 Stück',1)])
        self.assertFalse(result['ok'])
        self.assertTrue(any('UNMAPPED' in x for x in result['errors']))

    def test_missing_required_item_is_detected(self):
        result=recon.audit(manifest(),cart(rewe_eggs=0))
        self.assertFalse(result['ok'])
        self.assertTrue(any('UNSOURCED Freiland-Eier' in x for x in result['errors']))

    def test_same_product_mapped_to_two_goals_is_invalid(self):
        model=manifest()
        model['products'].append({'merchant':'rewe','title':'REWE Beste Wahl Respeggt Eier Freilandhaltung 10 Stück','intent_id':'turmeric','units_per_pack':1})
        with self.assertRaisesRegex(ValueError,'Ambiguous retailer SKU mapping'):
            recon.audit(model,cart())

    def test_units_must_be_compatible_for_shared_caps(self):
        model=manifest()
        model['groups'][0]['unit']='Stück'
        with self.assertRaisesRegex(ValueError,'incompatible group units'):
            recon.audit(model,cart())


if __name__ == '__main__':
    unittest.main()
