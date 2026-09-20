# Food review ledger

## Purpose

This ledger makes the food-catalogue review auditable. The operational table in [inventory-system.md](inventory-system.md) contains foods that already have a usable shopping decision. This file contains discovered candidates that still need an explicit decision or a finer product-form split.

Lifecycle status such as `active` or `paused` is not the same as review state. A food can be paused and fully reviewed, or historically active but still inadequately classified.

## Review states

- `unreviewed`: discovered from a source but not yet discussed as its own product form;
- `in-review`: currently being discussed;
- `resolved`: explicit decision exists and the candidate maps to an operational row or an explicit duplicate;
- `deferred`: Arthur intentionally postponed the decision; it must remain visible in the unresolved count.

Never claim that the food catalogue is complete while:

- any candidate is `unreviewed` or `in-review`;
- any candidate is `deferred` without a future review trigger; or
- a known source pool has not been imported and reconciled.

## Source coverage

| Source pool | Current coverage | Blocking gap |
| --- | --- | --- |
| Current HumanRuntime nutrition references | audited | Known missing and grouped candidates are queued below |
| Cronometer food mappings and saved meals | audited | Candidate foods not yet represented operationally are queued below |
| Preparation routines | audited | Product forms mentioned only in cooking notes are queued below |
| Current grocery-planning voice conversation | audited incrementally | Every newly mentioned food must enter this ledger before it is discussed |
| Seventeen historical REWE eBons / 98 consolidated foods | incomplete | The repository contains only a summary, not the original workbook or complete 98-food list. Recover or rebuild that source before claiming completeness |
| Flink and Flaschenpost receipts | partially represented | Reconcile every exact line item when the full receipt export is available |

## Systematic review order

Review exactly one unresolved candidate at a time in this order:

1. fresh fruit;
2. frozen or preserved fruit;
3. fresh vegetables and aromatics;
4. frozen or preserved vegetables;
5. dairy and fermented foods;
6. eggs, meat, seafood, and their distinct product forms;
7. legumes;
8. grains, starches, bread, and cakes;
9. nuts, seeds, and oils;
10. condiments, spices, and drinks;
11. supplements and special bulk goods.

After each answer, update the review state and operational mapping before presenting the next unresolved candidate. State progress as `candidate N of M in category` and never switch to a free-association suggestion list.

## Known unresolved candidates

These candidates are already evidenced but not yet individually resolved in the operational inventory. Grouped rows do not count as a resolution when members can differ by supplier, form, preparation, or cadence.

| ID | Candidate and product form | Category | Provenance | Review state | Operational mapping | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| VEG-004 | Cauliflower, frozen | frozen or preserved vegetables | food profile and Flink-basket summary | unreviewed | grouped frozen-vegetable row | Split because availability may differ |
| VEG-005 | Spinach, frozen | frozen or preserved vegetables | food profile and current stock discussion | unreviewed | grouped frozen-vegetable row | Split because availability and package form may differ |
| VEG-006 | Brussels sprouts, frozen | frozen or preserved vegetables | food profile and current availability discussion | unreviewed | grouped frozen-vegetable row | Flink is often unavailable |
| VEG-007 | Kale, frozen | frozen or preserved vegetables | food profile | unreviewed | grouped frozen-vegetable row | Need exact form and supplier |
| VEG-008 | Butter-vegetable mix, frozen | frozen or preserved vegetables | current stock discussion | unreviewed | grouped frozen-vegetable row | Distinct prepared mix |
| VEG-009 | Scandinavian vegetable mix, frozen | frozen or preserved vegetables | Flink-basket summary | unreviewed | grouped frozen-vegetable row | Distinct product listing |
| PRO-001 | Raw chicken, fresh or non-pre-cooked frozen | meat and seafood | preparation-routines safety exclusion | unreviewed | none | Must remain distinct from proven pre-cooked frozen chicken; likely incompatible until a safe method is established |
| LEG-001 | Black beans, ready-to-eat | legumes | food profile and purchase history summary | unreviewed | grouped ready-to-eat-legume row | Split for supplier and quantity review |
| LEG-002 | White beans, ready-to-eat | legumes | food profile and purchase history summary | unreviewed | grouped ready-to-eat-legume row | Split for supplier and quantity review |
| LEG-003 | Brown or green lentils, ready-to-eat | legumes | food profile | unreviewed | grouped ready-to-eat-legume row | Split for supplier and quantity review |
| LEG-004 | Black or Beluga lentils, ready-to-eat | legumes | food profile | unreviewed | grouped ready-to-eat-legume row | Split for supplier and quantity review |
| LEG-005 | Chickpeas, ready-to-eat | legumes | food profile and purchase history summary | unreviewed | grouped ready-to-eat-legume row | Lower preference than beans and lentils but needs explicit row |
| GRN-001 | Dry rice | grains and starches | preparation-routines preference rule | unreviewed | none | Stovetop format is a poor fit; do not conflate with paused microwave rice |
| GRN-002 | Dry quinoa | grains and starches | preparation-routines preference rule | unreviewed | none | Stovetop format is a poor fit |
| NUT-001 | Walnuts | nuts and seeds | exact Flink receipt `ja! Walnüsse ganze Kerne 200g` and food profile | unreviewed | grouped natural-nut-mix row | May differ from mix in price and cadence |
| NUT-002 | Macadamia nuts | nuts and seeds | exact Flink receipt `Kluth Macadamias geröstet & gesalzen` and food profile | unreviewed | grouped natural-nut-mix row | May differ from mix in price and cadence |
| NUT-003 | Hazelnuts | nuts and seeds | confirmed Cronometer breakfast mix | unreviewed | grouped natural-nut-mix row | Need actual purchased form and supplier |
| NUT-004 | Cashews | nuts and seeds | confirmed Cronometer breakfast mix | unreviewed | grouped natural-nut-mix row | Need actual purchased form and supplier |
| VEG-010 | Champignons, cooked and jarred | frozen or preserved vegetables | mushroom routine and user correction | unreviewed | grouped jarred-mushroom row | Exact form needs its own source and package size |
| VEG-011 | Chanterelles, cooked and jarred | frozen or preserved vegetables | food profile | unreviewed | grouped jarred-mushroom row | Exact form needs its own source and package size |
| VEG-012 | Pickled cucumbers, jarred | frozen or preserved vegetables | historical REWE workbook-analysis conversation | unreviewed | none | Exact product, current status, supplier, and cadence need confirmation |
| SPI-001 | Garlic granules, dried | condiments and spices | food profile | unreviewed | grouped manual-spice row | Keep separate from fresh garlic; likely manual |
| SPI-002 | Curry powder or seasoning blend | condiments and spices | food profile and historical purchase analysis | unreviewed | grouped manual-spice row | Likely manual; retain exact form |
| SPI-003 | Gyros seasoning blend | condiments and spices | food profile and historical purchase analysis | unreviewed | grouped manual-spice row | Likely manual; retain exact form |
| SPI-004 | Dill, dried or frozen form unconfirmed | condiments and spices | food profile and historical purchase analysis | unreviewed | grouped manual-spice row | Product form must be confirmed before resolution |
| SPI-005 | Iodized salt | condiments and spices | food profile and historical REWE analysis | unreviewed | none | Salt is not covered by the ground-spice row; likely manual |
| DRK-001 | Turmeric chai tea | drinks | historical REWE workbook-analysis conversation | unreviewed | none | Previously described as seasonal winter product with no large reserve |
| DRK-002 | Ginger-lemon tea | drinks | historical REWE workbook-analysis conversation | unreviewed | none | Previously described as seasonal winter product with no large reserve |
| SUP-001 | AG1 powder | supplements and special bulk goods | confirmed Cronometer mapping | unreviewed | none | Need stock, supplier, cadence, and current active status |
| SUP-002 | Vitamin D3 | supplements and special bulk goods | confirmed Cronometer mapping | unreviewed | none | Need exact current product, stock, cadence, and active status |
| GRN-003 | Basmati rice, dry | grains and starches | historical REWE workbook-analysis conversation | unreviewed | none | Known historical food; likely paused because stovetop cooking is no longer wanted |

## Separate household-supplies candidate

The exact Flink receipt also contained `Melitta Filtertüten 1x4, 80 Stück`. This is not food and must not be forced into the food table. It needs a future kitchen-consumables ledger so recurring grocery-adjacent supplies are not forgotten.

## Resolved corrections from the systematic audit

| ID | Candidate and product form | Review state | Resolution | Operational mapping | Reviewed on |
| --- | --- | --- | --- | --- | --- |
| FRU-001 | Mandarin or clementine, fresh whole fruit | resolved | active citrus check every week; buy a roughly 750 g net for one week, but treat a 1 kg net as two-week stock and do not repurchase it the following week; use oranges as the fallback with the same quantity logic | `Fresh mandarins or clementines` | 2026-09-20 |
| FRU-002 | Pomegranate, fresh whole fruit | resolved | paused; frozen ready-to-use seeds are the active replacement | `Fresh whole pomegranate` | 2026-09-20 |
| VEG-001 | Onion, fresh whole | resolved | active monthly stock check; current seven small red onions cover about two weeks at roughly half to one onion per day; buy one normal pack only when the remaining stock will not cover the next cycle | `Fresh whole onions` | 2026-09-20 |
| VEG-002 | Garlic, fresh whole bulb or cloves | resolved | active manual-only long-life item; do not track or schedule; Arthur adds it himself when visibly low | `Fresh whole garlic` | 2026-09-20 |
| VEG-003 | Sweet potato, fresh whole | resolved | active fourteen-day cycle with target stock of two; current stock is two, so buy none in the current cycle and expect two in the next cycle after subtracting remaining stock | `Fresh whole sweet potatoes` | 2026-09-20 |

## Completion gate

A full review is complete only when:

- the original 98-food REWE source has been recovered or rebuilt;
- every exact candidate from every source has a ledger row;
- every candidate is resolved or explicitly deferred with a review trigger;
- every resolved candidate maps to an operational row or an explicit duplicate;
- umbrella rules such as the fresh-berry cap are not counted as individual foods; and
- foods with different forms, suppliers, preparation compatibility, or cadence are not hidden inside one grouped row.
