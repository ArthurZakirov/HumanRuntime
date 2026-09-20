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
| SPI-001 | Garlic granules, dried | condiments and spices | food profile | unreviewed | grouped manual-spice row | Keep separate from fresh garlic; likely manual |
| SPI-002 | Curry powder or seasoning blend | condiments and spices | food profile and historical purchase analysis | unreviewed | grouped manual-spice row | Likely manual; retain exact form |
| SPI-003 | Gyros seasoning blend | condiments and spices | food profile and historical purchase analysis | unreviewed | grouped manual-spice row | Likely manual; retain exact form |
| SPI-004 | Dill, dried or frozen form unconfirmed | condiments and spices | food profile and historical purchase analysis | unreviewed | grouped manual-spice row | Product form must be confirmed before resolution |
| SPI-005 | Iodized salt | condiments and spices | food profile and historical REWE analysis | unreviewed | none | Salt is not covered by the ground-spice row; likely manual |
| DRK-001 | Turmeric chai tea | drinks | historical REWE workbook-analysis conversation | unreviewed | none | Previously described as seasonal winter product with no large reserve |
| DRK-002 | Ginger-lemon tea | drinks | historical REWE workbook-analysis conversation | unreviewed | none | Previously described as seasonal winter product with no large reserve |
| SUP-001 | AG1 powder | supplements and special bulk goods | confirmed Cronometer mapping | unreviewed | none | Need stock, supplier, cadence, and current active status |
| SUP-002 | Vitamin D3 | supplements and special bulk goods | confirmed Cronometer mapping | unreviewed | none | Need exact current product, stock, cadence, and active status |

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
| VEG-004 | Cauliflower, frozen | resolved | active; exactly 1 kg from Flink every four weeks in one block with 600 g leaf spinach, staggered fourteen days from the Flaschenpost broccoli block; none in the current order, first block in fourteen days | `Frozen broccoli, cauliflower, spinach, kale or similar active vegetables` | 2026-09-20 |
| VEG-005 | Spinach, frozen | resolved | active; exactly 600 g REWE Bio leaf spinach from Flink every four weeks in one block with 1 kg cauliflower, staggered fourteen days from the Flaschenpost broccoli block; current stock approximately 400 g | `Frozen broccoli, cauliflower, spinach, kale or similar active vegetables` | 2026-09-20 |
| VEG-006 | Brussels sprouts, frozen | resolved | paused; excluded from ordinary recurring shopping, but eligible as a one-order emergency substitute for an unavailable scheduled frozen vegetable when nutrition, price, storage, and preparation are comparable; emergency use does not reactivate it | `Frozen Brussels sprouts` | 2026-09-20 |
| VEG-007 | Kale, frozen | resolved | paused; excluded from ordinary recurring shopping, but eligible as a one-order emergency substitute for an unavailable scheduled frozen vegetable when nutrition, price, storage, and preparation are comparable; emergency use does not reactivate it | `Frozen kale` | 2026-09-20 |
| VEG-008 | Kaiser vegetable mix, frozen | resolved | accepted existing stock; approximately 400 g currently present, but not part of the fixed recurring blocks | `Frozen broccoli, cauliflower, spinach, kale or similar active vegetables` | 2026-09-20 |
| VEG-009 | Scandinavian vegetable mix, frozen | resolved | paused; historical Flink stopgap and not a preferred recurring product, but eligible as a one-order emergency substitute for an unavailable scheduled frozen vegetable under the category-equivalence rule | `Frozen Scandinavian vegetable mix` | 2026-09-20 |
| PRO-001 | Raw chicken and other raw meat, fresh or non-pre-cooked frozen | resolved | paused; excluded from current purchasing and preparation until Arthur explicitly reactivates a specific format with a safe proven method | `Raw or non-pre-cooked meat` | 2026-09-20 |
| LEG-001–005 | Ready-to-eat black beans, white beans, brown or green lentils, black or Beluga lentils, and chickpeas | resolved | one shared monthly legume category; do not ask about individual varieties. Current stock is seven units; add fourteen units now to reach about 21. Any canned, jarred, or pouched ready-to-eat legume may replace another unavailable one; priority is lentils, then beans of any type, then chickpeas. If none are available, leave the remaining quantity unfilled rather than substituting rice | `Ready-to-eat beans, lentils, and chickpeas in tins, jars, or pouches` | 2026-09-20 |
| GRN-001 and GRN-003 | Dry rice, including Basmati | resolved | paused; stovetop preparation does not fit the current low-friction system. Keep separate from paused microwave rice and never use either form as an automatic legume fallback | `Dry rice, including Basmati` | 2026-09-20 |
| GRN-002 | Dry quinoa | resolved | paused; stovetop preparation does not fit the current low-friction system | `Dry quinoa` | 2026-09-20 |
| LEG-DRY | Dry lentils and all other uncooked dried legumes | resolved | paused as a product-form category; do not buy or use them to fill the active ready-to-eat monthly legume target | `Dry lentils and other dried legumes` | 2026-09-20 |
| NUT-001–004 plus almonds | Individual walnuts, macadamias, hazelnuts, cashews, and almonds | resolved | paused as one category; the natural nut mix is the only active nut format. Do not ask about or buy individual varieties unless Arthur explicitly reactivates them | `Individual nut varieties` | 2026-09-20 |
| VEG-010–011 | Champignons and chanterelles, cooked and jarred | resolved | paused for shopping as one preserved-mushroom category. Approximately 2 kg are already stocked; ignore for now. Consider a four-week cadence only after actual consumption speed and the after-opening freezer-portion routine are validated | `Mushrooms, especially jarred champignons or chanterelles` | 2026-09-20 |
| VEG-012 | Pickled cucumbers, jarred | resolved | paused; retain in the inventory but do not schedule or buy until Arthur explicitly reactivates it | `Pickled cucumbers, jarred` | 2026-09-20 |

## Completion gate

A full review is complete only when:

- the original 98-food REWE source has been recovered or rebuilt;
- every exact candidate from every source has a ledger row;
- every candidate is resolved or explicitly deferred with a review trigger;
- every resolved candidate maps to an operational row or an explicit duplicate;
- umbrella rules such as the fresh-berry cap are not counted as individual foods; and
- foods with different forms, suppliers, preparation compatibility, or cadence are not hidden inside one grouped row.

An explicit user-defined interchangeable category is an exception to individual questioning. When Arthur has already set one shared quantity, supplier logic, and cadence for a group, resolve all named members together and never reopen each variety as a separate question unless its form, status, or sourcing rule actually differs. The ready-to-eat legume mix is the canonical example.

Paused frozen vegetables remain resolved and paused even when the category-level fallback rule permits them as a one-order replacement for an unavailable preferred frozen vegetable. Emergency substitution is not lifecycle reactivation.
