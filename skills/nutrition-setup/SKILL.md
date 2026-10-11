---
name: nutrition-setup
description: Use Arthur's established household food preferences, kitchen equipment, storage capacity, preparation routines, and grocery history for grocery planning, food storage, substitutions, and kitchen preparation. Do not use as the primary skill for medical nutrition, diagnosis, allergies, supplements, or food-diary logging.
---

# Nutrition Setup

Use the maintained context in this skill instead of asking Arthur to re-explain his kitchen and ordinary food routine.

## 🧭 Load the relevant context

| Reference | Contents |
| --- | --- |
| 🧰 [equipment.md](references/equipment.md) | Read for kitchen-equipment capabilities, available cookware, storage capacity, and operating or safety constraints. |
| 🍳 [preparation-routines.md](references/preparation-routines.md) | Read for cooking questions involving established microwave or steam-cooking procedures and preparation routines. |
| 🛒 [shopping-system.md](references/shopping-system.md) | Read for grocery orders, choosing suppliers, substitutions, recurring shopping quantities, and cart preparation. |
| 🤖 [grocery-operator-workflow.md](references/grocery-operator-workflow.md) | Read **first** for a complete weekly shopping run, inventory/photos versus Gmail forecast, product/SKU recognition, robust live retailer search, cart preparation, and post-purchase updates. |
| 📦 [inventory-system.md](references/inventory-system.md) | Read to determine what is due now based on freshness, usage, purchase history, available stock, and shopping cycles; includes unmigrated product rows. |
| 🔎 [food-review-ledger.md](references/food-review-ledger.md) | Catalogue review status, provenance, unresolved candidates, and migration-completeness checks. |


## 🥗 Canonical food data and migration state

- The Notion database [🥗 Ernährungs- & Einkaufsrhythmus](https://app.notion.com/p/575b54c3a7f54fa6bdfdfbc7068a4d03) is the canonical location for structured food-specific data, quantities, product forms, stock snapshots, shopping status, and per-product restrictions. Fetch its schema and query the database rather than copying values from reference Markdown. If Notion querying is unavailable, do not silently treat a historical Markdown snapshot as current inventory.
- Food preferences, food-specific quantities, product status, substitutions and per-food restrictions belong in Notion, not in a separate food-profile Markdown file. The reference Markdown files retain general decision procedures and principles. During incremental migration, remaining product rows in `references/inventory-system.md` have NOT yet been confirmed fully migrated. Migrated product rows are removed immediately after their complete product-specific content has been successfully saved in Notion; see the migration status note there.
- When migrating, preserve both numeric and conditional constraints in Notion, check successful writes, remove precisely the matching migrated rows and duplicated food-specific facts from Markdown, then review the diff. Never remove shared category/process rules or unresolved provenance solely because one food has been migrated.

## 🗃️ Notion data sources

Use the four currently existing, separately scoped Notion databases. Distinguish **canonical product rules**, **supplier relations**, **observed inventory**, and **derived purchase plans**:

| Source | Responsibility | Data Source ID |
| --- | --- | --- |
| 🥗 [Lebensmittel](https://app.notion.com/p/575b54c3a7f54fa6bdfdfbc7068a4d03) | Product preferences, cadence, consumption assumptions and status. | `collection://7ae3d926-82cc-4de4-886d-0da8a3b7fd0a` |
| 🏪 [Händler](https://app.notion.com/p/f9f5421c5ede494291553886c8b2b240) | Canonical `🛒 Händler` relations and supplier routes; **Flink über Wolt** is one shop. | `collection://12e32e66-944a-4c19-8a4d-b98984f4da3f` |
| 📦 [Aktueller Lebensmittelbestand](https://app.notion.com/p/f635f45269924a2fb1eddbcabd8575ca) | Fully observed 2026-10-11 inventory baseline (23 active records); absent foods mean zero **for this snapshot**. | `collection://50a53828-eaec-4874-b954-c29979bb430d` |
| 🗓️ [Einkaufsplan](https://app.notion.com/p/b4dc41e3b2db414395fc8cae433cab42) | Working shopping recommendations subject to recalculation; not a stock or purchase ledger. | `collection://62c019aa-87b7-4a5b-9f1e-d60d75a597f8` |

The former **Produkte** and **Händlerangebote** databases were moved to Notion trash on 2026-10-11 per user instruction. Do not reference them or recreate them. Store useful SKU-specific details with the relevant food record or an approved private product mapping; verify current price and availability in the seller UI. Migration is incremental: remove a product-specific Markdown record only after its relevant facts have been saved and verified in Notion. The catalogue remains incomplete.

## 🚀 REWE exact-ID cart workflow

- Use logged-in REWE "Deine Produkte" favorites/purchases as a private exact-product lookup. Run scripts/rewe_export_catalog.py --tab tN to refresh the complete private SKU cache of IDs, variants, names and observed availability; otherwise reuse an already verified cache.
- For **one delivery only**, derive an explicit JSON manifest of {"id":"...","quantity":N} from the canonical Notion food needs and coverage. Run scripts/rewe_cart_by_id.py --tab tN --manifest /tmp/one-delivery.json in dry-run first; --apply sets the *final* quantity but never checks out. REWE carts are account-wide, not per tab.
- To synchronize the private exported REWE catalog into the separate Notion product table: run scripts/rewe_sync_notion.py to preview and append --apply to write. This is an ID-based upsert and preserves hand-edited assignment/active/notes fields. Products that drop out of favorites are not deleted. Refresh the browser export beforehand.
- The ID cache is a **product-selection index**, not the canonical active-food list, and the SKU script does NOT guarantee the nutritional catalogue's completeness. See grocery-operator-workflow.md for cross-cart safeguards, including the confirmed Wolt → REWE → REWE three-week schedule superseding the still-obsolete fortnightly selector.

## ✅ Operating principles

- Treat confirmed equipment models and observed purchase history as facts. Treat proposed quantities and inferred preferences as starting points that may need current confirmation.
- Prefer low-friction methods: few preparation steps, microwave-compatible foods, pre-cooked or ready-to-eat ingredients, saved carts, and explicit substitute rules.
- Arthur is price-conscious and does not value organic certification by itself enough to justify a large premium. Compare like quantities and use conventional products when they meet the need.
- Prioritize reliably delivered food in usable condition. A small refund is not a substitute for receiving the food needed for the planned meals; inspect quality-sensitive perishables rather than presuming delivery quality.
- Preserve approximate planned amounts within accepted interchangeable food categories when one item is omitted, subject to price, preparation, shelf life and storage. Show the resulting substitutions and uncovered gaps in the final basket; never silently substitute a food marked paused.
- Reconcile any planned order with verified current stock and actual consumption. Historical quantities, purchases and stock snapshots are evidence, not an assertion of what is currently in the kitchen.
- This context supports household decisions; it does not replace current medical, allergy, manufacturer, package, or food-safety guidance.
- Do not infer that a historical purchase is still wanted. Use frequency and quantity as evidence, then reconcile against the current request and current inventory.
- For changing prices, availability, delivery windows, food-safety guidance, or product specifications, verify current information before relying on it.
- For any purchase, prepare or update the cart when authorized, but leave the final order and payment confirmation to Arthur unless he explicitly authorizes that exact transaction.
- Never publish or retain delivery addresses, account identifiers, order numbers, payment details, serial numbers, credentials, or email addresses in this skill.

## 🔧 Maintaining this context

When Arthur explicitly confirms a durable change to equipment, routine, preference, recurring quantity, or substitution rule, update the appropriate reference. Keep observed history separate from active defaults, record uncertainty directly, and remove obsolete assumptions rather than accumulating conflicting rules.
