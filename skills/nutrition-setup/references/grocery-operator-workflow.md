# Grocery shopping operator: weekend-to-receipt workflow

## Purpose and lifecycle

Reduce a grocery weekend to a brief, optionally fully unattended **preparation** followed by Arthur's review of actual online carts. Saturday and Sunday are interchangeable start days; delivery on Saturday, Sunday, or Monday is acceptable. A short gap of roughly one day is tolerable, but leaving an ordinary desired food unpurchased for one or two weeks solely to preserve a 7/14/28-day alignment is not. Calendar cycles are **review opportunities**, not rigid purchase prohibitions.

This is the **operating specification**, not proof that a scheduler, Gmail parser, private receipt ledger, SKU classifier, or automatic stock updater is deployed. If a required tool is unavailable, complete the remaining steps with the data available and report the smallest blocker. Do not promise invisible background processing.

## Sources and data ownership

- [🥗 Nutrition & shopping rhythm](https://app.notion.com/p/575b54c3a7f54fa6bdfdfbc7068a4d03) (`collection://7ae3d926-82cc-4de4-886d-0da8a3b7fd0a`): active/paused foods, preferred form, quantities, rules, expected consumption, 7/14/28-day rhythms, price ceilings, and supplier relations.
- [🛒 Merchants](https://app.notion.com/p/f9f5421c5ede494291553886c8b2b240) (`collection://12e32e66-944a-4c19-8a4d-b98984f4da3f`): the canonical relational **🛒 Händler** property. **Flink über Wolt** is a single merchant route, not two separate shops. REWE and Flaschenpost remain distinct.
- [📦 Current food inventory](https://app.notion.com/p/f635f45269924a2fb1eddbcabd8575ca) (`collection://50a53828-eaec-4874-b954-c29979bb430d`): the fully enumerated observed stock snapshot recorded on 2026-10-11, including quantity and evidence confidence. For **that complete snapshot**, an absent food means zero on hand; do not apply this zero-default to an incomplete future photo set.
- [🗓️ Shopping plan](https://app.notion.com/p/b4dc41e3b2db414395fc8cae433cab42) (`collection://62c019aa-87b7-4a5b-9f1e-d60d75a597f8`): a derived/working proposal, **not** an authoritative ledger or proof that its dates are current.
- Connected **Gmail** receipts/order confirmations: post-snapshot purchases and exact products/quantities. They are evidence for inventory updates, not a separate routine Arthur must fill out.
- Authenticated Wolt → Flink, REWE, and Flaschenpost browser sessions: **live** product availability, cart contents, and prices. A cart is not a purchase record.
- Existing SKU/package details and product image references belong on the corresponding Notion food/product records or a private product-ID mapping, not as invented values or a duplicated historical table in this public skill.

Do not save account data, email addresses, delivery addresses, payment information, order IDs, or raw personal receipts in the public repository. Any automation state/receipt deduplication store must live in an approved private runtime. Notion schema extensions and ingestion software are future implementation work, not existing capabilities.

## Checkpoint 1 — establish current inventory

At the start of the weekend workflow, offer only two paths when useful, with **forecast as the default**:

1. **Estimated stock, no photos (default)**: start with the last timestamped counted inventory; ingest all purchase emails after that snapshot; subtract expected consumption over the intervening days; incorporate explicit corrections/discards from Arthur. Present a concise estimate with an optional correction opportunity.
2. **New observed stock**: accept whole-kitchen photos, selected item photos, or a spoken/written correction. Identify visible packages against the SKU catalogue, use package-size metadata, and estimate partial/open containers separately. The new observation becomes a timestamped baseline for covered foods. If Arthur confirms a **complete** inventory, products absent from it count as zero at that timestamp; if photos cover only a shelf, do **not** zero unseen foods.

**Never ask Arthur to retype a package weight you could establish from its exact repeat-purchased product.** For example, a recognizable manufacturer + package design + product form should resolve to the saved 500 g oats, 750 g frozen broccoli, 250 g prepared chicken or the verified correct variant. Avoid conflating a shop's suggested alternatives with the user's actual SKU.

### Product/SKU recognition and resolution

- Build a reusable mapping when a product first appears: canonical food group, exact manufacturer/product name, retailer product URL or SKU where available, **net content and units**, preparation form, and a reference package image. A package photographed at home and a product listing should resolve to the **same** canonical product ID. A single category can have multiple supported SKUs and pack sizes.
- Resolve photos from readable printed labels/barcodes first where visible, then previously confirmed package appearance, then compare with known merchant product images/URLs. Prefer recognized brand and packaging over visual resemblance alone. Do not use a generic picture of a similar item as proof of the exact product.
- Pull current retailer details when not cached; verify product name, brand, pack net weight/count, multipack, variant and form. Preserve the source URL/evidence. **Do not leave pack weight “unknown” merely because the initial stock photo did not display it** when the exact SKU can be looked up.
- If two pack designs look similar or the exact size genuinely cannot be resolved, mark that item uncertain and ask **one targeted clarification**, not a full stock retelling. For unsealed goods, recognize the item but keep the **remaining** contents separate from the full manufacturer's pack size.
- Only label the first checkpoint **verified/observed** where the actual count is known. Product recognition does not prove the fill level of an opaque or already opened package.

### REWE exact-ID catalogue and idempotent cart operator (implemented 2026-10-11)

**Do not search for known REWE products by description each week.** Extract the product ID and, where present, variantArticleId from the user-authenticated "Deine Produkte" lists. This is a **retailer SKU mapping**, not a replacement for canonical food and quantity rules in Notion: 171 different product IDs do **not** mean 171 active foods. Previously bought/favorited products may be paused or unsuitable.

- Export favorites and purchases, including lazy-loaded listings, into a **private file outside Git**:
  python3 skills/nutrition-setup/scripts/rewe_export_catalog.py --tab tN
  The exporter validates complete page counts (Oct 11: 120 favorites and 133 purchased, 171 distinct IDs), writing ~/.local/share/humanruntime/rewe-products.json with file mode 0600. Refresh when products change or mapping fails, not necessarily every weekend.
- Durable Notion synchronization: first refresh rewe_export_catalog.py, then run rewe_sync_notion.py (preview) and rewe_sync_notion.py --apply (upsert by ID). The script retains all user-edited assignment, active, and notes fields; it does not delete products that disappear from REWE source lists.
- Derive the due **one-delivery** JSON manifest from canonical food rules, stock forecast, and already-confirmed orders. Example: {"items":[{"id":"7144527","quantity":1},{"id":"8245760","quantity":6}]}. Optional variant_id, title, and max_unit_price_eur allow stricter checks. **Quantity is the target final number of outer packs, not an incremental plus-click count.**
- Preview without changing anything:
  python3 skills/nutrition-setup/scripts/rewe_cart_by_id.py --tab tN --manifest /tmp/rewe-week.json
  Once sure that **this shared account basket** belongs to the intended order and the earlier order was actually submitted, add --apply. The script validates exact catalog ID/variant, verifies the live product title and optional unit price ceiling, sets the final quantity, and rereads it. Wrong/unknown IDs, changed titles, unavailable items, and price mismatches become explicit blockers instead of silent guesses.
- A second run is **idempotent for listed SKU targets**. Items missing from the manifest are NOT automatically removed from the basket; audit the **entire** real cart against the whole planned order, including any non-favorite items acquired separately.
- The REWE cart is **account-scoped, not tab-scoped**. Another browser tab or a different Friday picker does NOT create a second independent basket. Never apply a manifest for the next Friday until the previous order was actually submitted by the user. A checkout screen is not a receipt.
- The script **never clicks checkout or purchase** and never reserves a slot. Check the Friday slot, minimum, substitute preferences, bag deposits, and final price; Arthur submits the order.

**Migration warning:** The existing shopping_cycle.py and legacy paragraphs below still assume the OLD biweekly REWE anchor. Arthur subsequently confirmed the **three-shopping-week pattern Wolt → REWE → REWE**, prepared approximately every third Saturday, with the next two REWE Fridays where bookable. The old selector must NOT be used for current live planning until migrated. SKU scripts execute an explicit single-order manifest, not the calendar logic.

### Gmail receipt ingestion and arithmetic

Model an inventory ledger per canonical SKU (or normalized shared-consumption pool):

`estimated_stock_at_t = observed_baseline + purchases_assumed_arrived - modeled_consumption + explicit_adjustments`

- Search Gmail from the last processed point, extracting merchant, item, SKU/description, count, and package quantity. Avoid counting both order confirmation and invoice for the same order. Deduplicate using a **private** message/order identity; do not persist these identifiers in Git.
- Arthur reports that virtually all online goods arrive. Therefore **assume purchased items arrived** around their expected delivery and add them automatically; **do not** impose an item-by-item delivery confirmation, cancellation audit, or human receipt review on the happy path. If he reports a missing, substituted, damaged or discarded item, adjust it then.
- Do not add future undelivered baskets to current stock merely because items were put in a cart. Apply purchase receipts at their sensible delivery date, so a Sunday purchase scheduled for Monday does not falsely appear in Sunday's fridge.
- Translate counts into mass/volume from SKU pack size. Distinguish 1 outer 300 g pack with 2 inner pouches from 2 outer packs; never double-count both levels.
- Consume by known rate (e.g., nuts ~50 g/day; frozen vegetables ~300 g/day as a **single pool**, ideally ≥50% broccoli). **Meat/fish follow packaged meal portions rather than a precise 200 g/day mass debit.** Count how many practical meals remain based on the confirmed SKU/portion rule below and update after a known full-pack or split-pack meal. Use realistic current rates, not an immutable historical number. Enforce no negative reported stock, but track possible shortage for purchasing.
- Corrections overwrite the model **at a timestamp**; replay only later deliveries and subsequent estimated use. Do not add the same product a second time by combining a newly photographed full kitchen with already-booked older receipts.
- Show the estimate and a one-shot correction option. Confidence is provenance: **counted**, **receipt-backed forecast**, or **low-confidence/photo ambiguity**. Don't flood the user with every routine certainty.

## Recurring shopping route — REWE every other weekend (confirmed 2026-10-11)

**Deterministic anchor:** The weekend **10–11 October 2026** is a REWE shopping weekend. **Every second weekend thereafter is also a REWE weekend** (the next is **24–25 October**, then **7–8 November**); the intervening weekends (e.g., 17–18 October) are not obliged to use REWE. Saturday versus Sunday, ordering on Sunday for delivery on Monday, or a small one-/two-day delay **does not reset the REWE phase**. Use the intended weekend/cycle identifier, **not** the exact delivery timestamp, to determine whether this is the biweekly anchor. A skipped shopping session does not silently phase-shift future sessions.

**Reproducible selector:** `python3 scripts/shopping_cycle.py --weekend 2026-10-11` prints the primary merchant and locked REWE phase for the *intended* weekend. Next session: `--weekend 2026-10-18` (Wolt-first), then `--weekend 2026-10-25` (REWE-first). Use this selector before opening any merchant. An order delayed until Monday still uses the Saturday/Sunday of its original shopping session.

### REWE free-delivery windows and advance planning (verified 2026-10-11)

**Account-specific facts outweigh generic web FAQs:** REWE's *actual logged-in delivery-date picker* for Arthur's address explicitly displayed **“Gebührenfreier Liefertag” on Friday 16 October and Friday 23 October 2026** and **“Tipp: Jeden Freitag sind Li…”**. Selected Friday 16 October slots showed **0.00 € delivery charges**. This is **verified for this account and these displayed dates**, not a permanent guarantee that every future Friday stays free. A general REWE public page suggests Tuesday–Thursday by postcode, but this customer's live UI showed Fridays; inspect the actual shop every time. REWE officially states delivery is free at **120 € of eligible product basket value**, excluding deposits and delivery fees; do not target 120 € by buying unwanted extras merely to save a delivery charge of at most a few euros.

**Advance-booking horizon:** REWE's public FAQ says delivery slots may be selected **up to 13 days in advance**. On 11 October 2026 the signed-in REWE UI displayed dates up to **24 October** and showed **Friday 23 October already bookable**, supporting preparing the next biweekly REWE order **on the preceding weekend**. This does NOT establish that four separate weeks can be ordered in one sitting; future availability and how many concurrent purchases the UI allows must be tested without unintended checkout. Slots are not reserved until the retailer confirms an order.

**Reduced-effort plan:**
1. On a free weekend (Saturday or Sunday), prepare any needed **immediate** Wolt/Flink fresh-food delivery for that current weekend **only**, if needed. Independently prepare the **REWE order for the next scheduled free Friday** if the delivery date is already open, *even if that date falls in the following weekly session*. Thus one sitting may prepare both a current Wolt arrival and a later REWE arrival.
2. Prefer **one REWE cart** for the whole week that REWE is going to deliver: approximately 14 days of suitable frozen meat/fish meal packs at the biweekly anchor, plus **7 days of all mandatory fresh produce for the Friday arrival week**, plus legitimately due pantry goods. REWE is the **primary full grocery supplier** in its delivery week. **Do not independently buy the same weekly produce at Wolt for that same delivery period.** If an item will run out *before* Friday, Wolt can bridge that immediate gap, but do not treat the bridging order as a second unconditional seven-day refresh.
3. Because delivery is booked **for a later week**, map each purchase-intent quantity to its **coverage interval** (e.g., this weekend's immediate produce vs next Friday's produce). Different delivery weeks are not accidental duplicates; **the same food with overlapping consumption coverage is**. Record `delivery_date`, `coverage_from`, `coverage_to`, and intended merchant beside each item in the private shopping-run manifest. Reconcile actual overlapping orders, including already placed or pending orders, not merely simultaneous open carts. Treat the receipt as purchased stock only at the likely delivery date.
4. If REWE's Friday is 0 € delivery, **do not force the cart to 120 €**. Meet only the retailer's real minimum eligible merchandise value; if short, advance sensible shelf-stable legumes/nuts/oats as specified under **Minimum-order-value filler**. If Friday is unavailable or not free, compare actual fees versus a natural basket over 120 €; do not add unwanted excess to avoid a small fee.
5. After a future-dated REWE order is **actually submitted by Arthur**, don't open a second order for its same coverage window. The following weekend may legitimately be **shopping-free**, unless something urgent is missing. Next REWE fortnight is anchored by the intended meal coverage and delivery, not shifted by a late Sunday review.

**Practical examples:** On Saturday 17 October prepare a same-day Wolt/Flink fresh top-up only if needed **and** the REWE cart for Friday 23 October (two-week frozen protein + produce for 23–29 October, if those days remain suitable). When Friday 23 October arrives, REWE delivers; the weekend 24–25 October needs **no duplicate weekly fresh-food order** if the Friday arrival already covers it. If Friday delivery is a few days later than the prior order's depletion, a modest tolerated gap or targeted Wolt bridge is preferable to duplicated full weekly fruit purchases.

**Do not checkout automatically.** The agent may prepare carts and review delivery times but Arthur explicitly submits each purchase. A month-ahead ordering optimization remains an experiment until the real shop supports sufficient future dates and multiple independent confirmed orders.

**At each REWE-anchor weekend (a two-week protein purchase):**

1. Open **REWE first**. Target **roughly 14 complete, usable meat/fish meals over two weeks**, shared across compatible chicken and fish, rather than exactly 2.8 kg. Prefer the five-chicken/two-salmon weekly rotation unless Arthur changes it. **The meal is sized by the real product package:** eat one entire **170 g or 250 g pack** as one meal; divide a **400 g pack into two meals**; combine **two 80 g packs** for one meal. Other sizes are resolved sensibly from the actual product and user preferences, not forced to 200 g. Count the planned meals using those portions, subtract already available meals, and buy suitable whole packs. **Do not optimize away a legitimate pack because the nominal 200 g/day × 14 mass would be exceeded.** Small variation in daily grams and total kilos is acceptable; Arthur explicitly accepts the existing REWE chicken/fish basket. Freezer space is roughly two weeks of these packs, not an exact gram ceiling. Use familiar exact REWE SKUs, respect the frozen salmon price ceiling, and use only suitable **pre-cooked chicken**, not raw chicken that cannot be prepared.
2. Without changing shops, put all **weekly mandatory short-life fresh fruit and vegetables** into the same REWE cart for **one week only**. These are automatically due at every weekly shopping session **without asking for a count of leftover bananas, celery, etc.** (unless that week's order has already been booked). Examples currently active in Notion: **bananas, kiwi, pears, fresh broccoli, cherry tomatoes, red bell pepper, mini cucumbers and celery**. Read the live active food rows and weekly quantities; this is an illustrative list, not a second static product database. **Attempt a suitable fresh watermelon** as its weekly active rule specifies; omit with availability explanation when no real melon is sold. **Grapes remain price-/quality-conditional and fresh berries optional;** their `📅 Wöchentlich` label alone does not override their explicit conditional rules. Frozen berries are handled by their own storage policy, not automatically classified as short-life fresh food.
3. Calculate REWE's live **minimum order value** after protein and fresh produce. If short, use the **Minimum-order-value filler** procedure above: first pull forward realistically needed, long-lived **ready-to-eat legumes**, then natural nuts, then oats; stop when the true threshold is reached, not at a fictitious high target. Check the account-specific free-Friday slot and **never inflate the cart to €120 just to save a delivery fee**. If no legitimate pantry top-up fits, report the gap.
4. After the REWE cart is verified, source only **unmet canonical intents for the specific delivery/consumption window** using Wolt/Flink or Flaschenpost. A future-Friday REWE cart is the full primary order for **its arrival week**, not a second weekly basket. Wolt may be used before that Friday for an immediate shortage or after that Friday for a genuine catalog gap.

**Meal-counting examples:** 10 packs × 250 g plus 2 packs × 250 g represent **12 meal-sized packs**, *not* a failure because the mass is 3 kg rather than 2.8 kg. Add the currently available suitable portions to estimate coverage. Conversely, one 400 g pack can count as two meals if split; one 80 g pack counts as half a meal if two are typically consumed together. The agent should compare **meal coverage and freezer capacity**, not create a rigid mass-cap rejection. Avoid buying months of extra frozen food, but accept normal package sizes and small overage.

**At each intervening weekend (the week without mandatory REWE):**

1. Source the **same one-week fresh produce refresh**, normally using **Flink inside Wolt**. No need to start REWE or repeat the frozen meat/fish supply when the previous REWE order still covers the coming days.
2. Check other stock-based needs by forecast/receipts and restock when justified. REWE remains an **optional fallback** for unavailable essentials, not a prohibited merchant.
3. Explicit consumption caps (e.g., eight rice/corn/lentil cakes per four weeks) keep their own replenishment policy and **must not** be bypassed just because a given REWE trip is already planned.

**Weekly freshness versus stock accounting:** a **weekly fresh-refresh rule is a mandatory *shopping attempt***, not a guarantee a product is sold by the shop; it bypasses the cupboard-estimate question only for designated short-lived active foods. Avoid duplicating a weekly purchase if this week's receipt or an in-flight order already records it. Produce available only via an unacceptable premium, spoiled quality or out-of-stock remains an explicit unfilled item, not a silent omission. Do **not** extend this unconditional weekly-buy logic to oats, nuts, eggs, dairy, freezer stock or vacuum-cooked beetroot without their own active rule.

### Minimum-order-value filler — shelf-stable staples first (confirmed 2026-10-11)

**Applies to any retailer with a minimum eligible order value**, including REWE and Wolt/Flink. This is a separate concept from the €120 REWE free-shipping threshold. Earlier REWE observations showed a minimum **around €60**; Arthur suspects Wolt/Flink has a **€30** minimum, which is **NOT verified**. In both cases read the **live checkout minimum and eligible merchandise subtotal**, including whatever the shop actually excludes (e.g., deposits, bag deposits, discounts, service fees). Do not hard-code a guessed Wolt amount.

**Procedure:** First put all planned week-specific fresh produce and actually needed frozen/refrigerated foods into the *assigned* retailer/cart and subtract already booked orders for the same coverage period. Once all required items are in place:

1. If the eligible merchandise value is below the shop's actual minimum, fill **only the shortfall** with preapproved **shelf-stable foods that Arthur already consumes**. Never double the weekly quantity of bananas, lettuce, broccoli, dairy or other perishables simply to pass the minimum.
2. Prefer **ready-to-eat canned/jarred/pouched legumes** (lentils first, beans next, chickpeas after) because consumption is now **about one pack per day / seven packs per week / 28 packs per four weeks**, not the previous five/week estimate. Maintain a flexible forward pantry buffer based on current counted/receipt-projected stock and earlier confirmed or future-dated orders. Filling a cart for minimum value may **pull forward future legume purchases** instead of imposing a fixed four-week replenishment date. A target of up to roughly **8 weeks of consumption (~56 packs total on hand plus confirmed incoming)** is an illustrative **upper planning horizon only when storage, printed best-before date and budget allow**, not a mandate or license to overbuy.
3. If additional legumes would exceed sensible pantry capacity or the accepted price/form, use **natural mixed nuts** or **oats** next **only if future expected consumption justifies them**, counting existing pantry stock and already placed orders. The 2026-10-11 inventory includes substantial nuts and oats; do not replenish them reflexively merely because they are on this filler list.
4. Calculate the number of **whole sale packs** with the item's **live price** and the remaining gap; add the minimum practical count (one pack of overshoot is normal) and recalculate the actual eligible cart value. Re-run the **global cross-shop / cross-delivery** quantity and coverage audit; future pantry demand can be allocated only **once**, not repeated for each advance-booked Friday.
5. If no approved filler fits shelf life, realistic consumption, available space, budget or price ceilings, **stop and report the threshold gap**, or combine with genuinely needed products/change supplier/delivery timing. Do not add paused foods, consumption-capped rice/corn/lentil cakes before their allocation date, dried uncooked legumes, unnecessary gadgets, or arbitrary substitutes. Do not chase €120 purely to save a smaller delivery fee when the Friday slot itself is already free.

**Outcome:** Most ordinary REWE weeks should approach the minimum with normal food; staples merely make up the last few euros when required, while building a deliberately limited emergency pantry buffer. Prefer postponing a longer-cycle pantry buy to a future REWE week that actually needs a minimum filler, without leaving Arthur short of meals before then.

**Multi-shop invariant (not optional):** Start from a **single authoritative list of purchase intents** and their target quantities. Give each exact food/variant a canonical ID, unit and total target for *all shops combined*. Allocate it to **one shop by default**, and move it to a fallback rather than purchasing it in both. Teas with different flavors are **distinct intents**; equivalent Freiland 10-count egg packages at REWE and Wolt are the **same intent**. Before each plus-click and again after all carts are assembled, reconcile normalized quantities across ALL actual carts. A shop's own basket check does not satisfy this invariant. A persisted run-specific JSON/Markdown audit can be stored **privately under /tmp**, not published to the skill repository.

Use `scripts/reconcile_grocery_carts.py` for a **read-only cross-shop audit** before presenting baskets. The canonical manifest must include the entire current purchase plan (including known alternatives and current cart contents), with no unmapped products or quantities above their total planned amounts. Fail closed on unresolved overlaps. Do not claim checkout-ready status until the final audit passes.

## Checkpoint 2 — determine what to buy now

Compute *run-out coverage* from estimated quantity/usage, the next plausible shopping opportunity, storage constraints, existing inventory, planned dietary variety, and each food's policy.

1. **Normally consumed foods:** fruit, fresh vegetables, eggs, Skyr, kefir, prepared proteins, desired tea, etc. If needed before the next practical order, buy **now**, even when a prior 14/28-day calendar phase has shifted. Buying a full planned cycle quantity at a sensible time is generally preferable to subtracting today's stock from a nominal fixed-order quantity (e.g., 6 Skyr now → wait a week → buy 12, not automatically buy 6).
2. **Explicit consumption caps:** rice/corn/lentil cakes are **8 packs total per 28-day allocation**. Running out early must **not** trigger an extra purchase: the cap is the purpose. Record the next legitimate allocation date rather than pretending all empty shelves are emergencies.
3. **Supplier-batched/manual:** protein UHT milk is handled by Arthur with Flaschenpost. Frozen broccoli and vacuum-cooked beetroot may join the next Flaschenpost milk order if that efficiently solves availability; do not build a separate milk cart unasked. Use REWE when the required compatible food is absent at Wolt/Flink.
4. **Shared pools:** frozen broccoli, cauliflower, spinach and equivalents are **one total frozen-vegetable supply**. 3.75 kg at 300 g/day covers ~12.5 days; do not order a separate cauliflower or spinach block solely because its calendar label is due. Interchangeable ready-to-eat beans/lentils/chickpeas form one pool, with the recorded preference order.
5. **Paused/conditional items:** respect explicit inactive foods and product forms. Optional fresh berries are not a must-buy when frozen berries are the reliable economical default. **Desired** watermelon and grapes, by contrast, remain in the actionable shopping attempt; decide whether an acceptable listing exists and meets their price guardrails *during* shop browsing rather than hiding them under “check”.

**Output for the shopping agent:** one actionable list containing *every item to attempt to source this weekend*, with exact quantities/acceptable alternates/price limits; keep intentional exclusions and deferred supplier batches in a small separate exceptions summary. “Requires live price/availability verification” is a task for the agent, **not** an excuse to omit the item from the cart-building pass.

## Checkpoint 3 — shop search and cart building

- **Supplier route is conditional on the anchor weekend:** **REWE first** every other weekend (protein for two weeks + one-week fresh produce); **Flink inside Wolt first** on intervening weekends. REWE is optional as a fallback then. Flaschenpost stays a separate milk-driven batch option. Do not blindly build the entire weekly produce list at both REWE and Wolt. Use the canonical food-row merchant relations, desired products, current inventory and cross-shop reconciliation before and after each cart operation.
- Use the available authenticated browser/computer-control tools; on Arthur's Mac, **Vercel agent-browser CLI** is the established preferred browser interface. Read its installed core skill before use. Do not silently replace it with Playwright MCP when the preferred tool works.
- Search **one product at a time**. Enter the exact product name or a documented alias; submit the query if required. **Wait for the site to return a terminal, query-specific state before drawing a conclusion or typing the next query.**
- Prefer event/DOM-state waits: observe loading indicators/skeleton placeholders, results appearing, the search field matching the submitted query, a completed empty-result message, and the results stabilizing across successive snapshots. Fixed sleeps alone are **not** evidence of completion. Allow time for asynchronous API results (e.g., up to ~20 seconds when the shop is slow); re-snapshot after every meaningful change.
- If genuinely no result **after completion**, retry the exact retailer product name plus ordinary German spelling, singular/plural, synonym and category navigation. Distinguish actual absence from network failure, UI loading, blocked requests, and stale results from the **previous** query. Never call an item unavailable while results are loading.
- Confirm the **exact** item, brand/variant if needed, package unit/net content, raw-versus-ready-to-eat form, per-unit price, and target quantity before adding. Use observed UI evidence, not guessed search paths, stale element handles or inferred button positions.
- **A search is not a cart update.** After waiting for results, call `agent-browser snapshot -i` to inspect every relevant product card in the results, including categories further down the page. Use `agent-browser scroll down 800` followed by another `snapshot -i` if results are truncated or lazily rendered; `agent-browser screenshot --full` and `screenshot --annotate` are available for visual disambiguation. Review product title, image/variant, size, price, and all plausible matches before choosing the card. A first hit such as `Paprika Spitz` is **not** the same as the needed `Paprika Rot`.
- **Click the matched card's plus.** Wolt search cards expose a repeated accessible `button "Weiteren Artikel hinzufügen"`. The correct button is the one **inside the same product card** as the selected title, not the first plus on the page. With `agent-browser snapshot -i`, find the `heading "EXACT ITEM" [level=3]`, then locate the corresponding `button "Weiteren Artikel hinzufügen" [ref=eNNN]` before the next card. Click `agent-browser click @eNNN` as many times as required, or use the helper below. Then ensure the corresponding product card's counter equals the intended quantity.
- **Verify the actual cart, not just the search card.** Open `button "N Bestellung ansehen …"`, find the exact item in `[data-test-id="CartItem"]`, confirm the count in `[data-test-id="CartItemStepper"]`, then close the cart dialog without checking out. A Wolt result card increment alone is incomplete until the cart shows the target. For large results or ambiguous visual layouts use a screenshot in addition to DOM assertions.
- **Reusable tested tool:** `scripts/wolt_flink_cart.py` supports `--inspect` (read-only), then explicit `--exact-title`, `--target`, and optional `--max-unit-price` for a chosen listing; it verifies both the search result quantity **and the actual cart quantity**, refuses ambiguous SKU matches, and never visits checkout. Example from the repo root:

  ```bash
  python3 skills/nutrition-setup/scripts/wolt_flink_cart.py --tab t9 --search 'Paprika' --inspect
  python3 skills/nutrition-setup/scripts/wolt_flink_cart.py --tab t9 --search 'Paprika' --exact-title 'Paprika Rot 1 Stk.' --target 1 --max-unit-price 2.50
  ```

  Confirm the product from the inspected results **before** selecting its exact title. The helper is a Wolt/Flink-specific CLI utility, not a REWE/Flaschenpost operator. Its `--target` denotes the total desired units of that exact listing in the cart, so reruns must not double-add. If the search remains loading or times out, retry/check manually or use a fallback retailer; do **not** silently mark unavailable. A shop closing while searches load may delay results.
- Build **carts only**. Keep already correct items, remove stale disallowed items (e.g., paused apples or early wafer replenishment), and verify the final quantities at each shop. Present cross-cart totals, fees where visible, unexpected substitutes, overpriced/unavailable items, and unsourced essentials.

### Wolt/Flink operator runbook — verified in Chrome on 2026-10-11

**Critical:** Searching and collecting matching product names is *not* basket preparation. A complete pass for **each** planned product is: **search → wait → examine all relevant products → select exact variant → click that variant's plus (+) → verify its quantity → verify in the actual cart**. Do not start the next search before the previous product has either been added and verified or explicitly recorded as an unresolved gap.

The preferred CLI has the required inspection and interaction tools. Use its installed guide (`agent-browser skills get core --full`).

1. **Use existing logged-in tab:** `agent-browser tab list`, then `agent-browser tab t9` (the tab id is illustrative, **discover live**). Do not navigate the user's unrelated tabs or reset the cart.
2. **Search:** `agent-browser fill 'input[placeholder="Suche bei Flink Karolinenstraße"]' 'Süßkartoffel'`. The Wolt search automatically filters; pressing Enter is not universally necessary.
3. **Wait for actual results:** `agent-browser snapshot -i` shows **“Wir suchen nach ...”** and gray skeleton cards while Wolt's asynchronous search API is still loading. **Do not conclude “not available” or type the next product then.** Wait for **“Suchergebnisse für "EXACT QUERY"”**; confirm the input, URL's `search` parameter and that result header all refer to the **same** query. Re-snapshot until results stabilize. `agent-browser wait --fn` can work, but observed false timeouts; the CLI helper polls read-only `agent-browser eval` DOM state instead. `--inspect` gives parsed product cards, exact titles, pack units, prices and current cart quantities. A result list from the *previous query* or a skeleton state is NOT a valid result.
4. **Review *all* plausible results:** `agent-browser snapshot -i` exposes product headings, actual price/size, and **“Weiteren Artikel hinzufügen”** refs. Scroll (`agent-browser scroll down 700`, then take another snapshot) if further product cards/categories are below the fold. Optionally `agent-browser screenshot /tmp/wolt-results.png` for visual inspection. Or run read-only DOM inspection:
   `agent-browser eval 'Array.from(document.querySelectorAll("li[data-test-id=ItemCard]")).map(e=>({name:e.querySelector("h3")?.textContent,price:e.querySelector("[data-test-id=ImageCentricProductCardPrice]")?.textContent}))'`.
5. **Discriminate variants before clicking:** In observed search for `Süßkartoffel`, **“Süßkartoffel 1 Stk.”, 2,19 €** is correct; **“Süsskartoffel Pommes 500g”** is a different product. In `Gurke` results choose **“Gurke Mini 1 Stk.”**, not ordinary Gurke. In `Paprika` choose **“Paprika Rot 1 Stk.”**, not pointed peppers, mixed peppers or cooking peppers. Never assume first result is the best result.
6. **Click the chosen result's PLUS, not the result's product button:** In a fresh snapshot, the **“Weiteren Artikel hinzufügen”** button directly after that product's heading has ref such as `@e2804` (ephemeral example). `agent-browser click @e2804` increments that SKU by **one**. Click as many times as required, observing quantity after the first click. **Refs are regenerated; don't reuse stale refs after a page transition.**
7. **Verify:** `agent-browser snapshot -i` now displays that product's stepper count; its `Weiteren Artikel hinzufügen` control remains available. Read-only DOM via `agent-browser eval` can extract `[data-test-id=ItemCardStepperValue]` on the exact `li[data-test-id=ItemCard]`. Then click `Bestellung ansehen`; inspect `[data-test-id=CartItemName]` and `[data-test-id=CartItemStepper]` in the actual cart, checking **title and quantity**. Close the cart dialog, not checkout.

### Recover Wolt API hangs without losing the saved cart

**Observed failure and tested fix (2026-10-11):** Search sometimes stays indefinitely on **“Wir suchen nach "Yogi Tea"”**, with blank/skeleton cards. Waiting longer or immediately searching the next food either wastes time or misclassifies products. **`agent-browser reload`** on the *same active Wolt store tab* resolved the hang and showed the expected Sweet Chai listing. After that refresh, Wolt displayed the modal **“Bestellung fortsetzen?”** with **“Nein”** and **“Ja”**.

1. If the correct query's results do not finish after roughly 10–15 seconds, first capture a snapshot (or `agent-browser screenshot --annotate`) to confirm the page is truly stuck on loading, not an uninspected loaded result. Optionally inspect `agent-browser errors`, `agent-browser console` when diagnosing repeated failure.
2. **Record the visible cart count**, if available (e.g. **41 × “Bestellung ansehen”**). Save the current live tab identity from `agent-browser tab list`.
3. Run `agent-browser reload` to refresh **that Wolt tab only**. Do **not** open a fresh store/tab, clear site state, or dismiss saved-cart prompts.
4. Immediately call `agent-browser snapshot -i`. When the exact modal heading `Bestellung fortsetzen?` appears, find the **freshly generated** `button "Ja" [ref=eNNN]` and click that reference, e.g. `agent-browser click @eNNN`. **NEVER click “Nein”: it discards the stored cart/start-over session.** Don't use a stale `@e...` ref from a previous snapshot. Generic CSS `button:has-text(...)` did not reliably locate this button in the observed CLI session; a current snapshot's `@ref` did.
5. After clicking **Ja**, verify the dialog disappears **and “N Bestellung ansehen …” is back**, with the **same cart item count** as before refresh. During the modal, the background may display **“Vorbestellung”** instead of the cart button; this does **not** mean the old cart vanished. In the live test, clicking **Ja** restored the existing **41-item / €71.89** cart, without placing an order.
6. Recheck the search results. A reload may preserve the `?search=...` query or clear it. If the page now shows completed results for the right query, **do not type that same query again**: doing so previously caused another hang. Otherwise re-enter it once and wait for a settled, query-matched result list. Continue from the product selection and plus click step.
7. Attempt a bounded recovery (normally one refresh and retry). If still stuck, report **“Wolt-Suche gestört, nicht als ausverkauft bestätigt”** and use REWE or another approved merchant. Do not spin in a browser refresh loop, mislabel the product as unavailable, reset the cart, or keep asking Arthur to intervene.

**Tested automatic recovery command:**

```bash
agent-browser tab list
agent-browser tab t9                    # example: discover the live id
agent-browser reload                    # current Wolt/Flink tab
agent-browser snapshot -i               # read fresh Ja/Nein refs
agent-browser click @eNNN               # ONLY if @eNNN is the fresh "Ja" ref
agent-browser snapshot -i               # verify prior basket appears
```

**Script alternative:** `python3 scripts/wolt_flink_cart.py --tab t9 --recover-only` safely performs reload → identify exact resume-cart dialog → **Ja** → verify the prior cart-unit count; it does **not** modify line items or open checkout. During an ordinary `--inspect` or `--exact-title --target` operation the helper applies the same recovery after an initial bounded wait. Live test: `RELOADED: cart units=41, resumed_saved_cart=True`.

If the result cards or cart count are inconsistent after reload, **stop instead of continuing to write**; inspect a fresh snapshot and compare to the last verified cart. Keep the cart as the user's data, not a disposable search session.


### Cross-shop troubleshooting and safe fallback

- **Shop is currently closed:** Wolt/Flink can display `Geschlossen` and `Öffnet morgen` while still exposing search results, a saved cart and `Vorbestellen`. That does not mean products are unavailable. Check the actual next-delivery/preorder choices and do not submit a purchase.
- **Results look suspicious:** inspect the category heading and **all plausible cards**; broad search terms may produce unrelated prepared food, products containing the search word only as an ingredient, or sponsored cards. Never click the first plus merely because the title shares one word with the desired food.
- **Click fails or “element covered”:** use a **new** `snapshot -i`; close/resolve only the recognized blocking popover or dialog. Then `scrollintoview @ref` and retry on the *current* exact product card. If the DOM and screenshot disagree, take an annotated screenshot and inspect it rather than calling arbitrary JavaScript `.click()` on an unverified element. Never bypass a confirmation or checkout gate.
- **REWE uses different controls:** locate its **own** live search, quantities and cart controls; the Wolt selectors and `scripts/wolt_flink_cart.py` do not apply. A disabled `Zur Kasse` below a displayed minimum basket value is **not** a search failure. It **does** trigger the bounded approved shelf-stable minimum-value filler rule (ready-to-eat legumes → nuts → oats), with projected inventory and all existing/future orders reconciled; never add needless perishables. Carry desired products from a genuine Wolt gap into REWE, verify weight/preparation and **never click “Zur Kasse” as part of an autonomous purchase**.
- **Flaschenpost is separate:** consider the existing milk order/batch and preferred frozen-broccoli/vacuum-beetroot products. Confirm compatible form, quantity and availability in Flaschenpost's *own* UI. Do not order the milk on Arthur's behalf or assume that Wolt/Flink's results imply Flaschenpost stock.
- **Item not found:** distinguish (a) query API still loading/time-out, (b) search completed with unrelated results, (c) exact SKU unavailable but accepted alternative exists, and (d) exact SKU available but too expensive. Only (b)–(d) justify a concrete fallback decision. Keep the intended food in the sourcing list until every approved source has been attempted or an explicit cap/exclusion applies.
- **Interrupted agent session:** resume the **same authenticated tab** and first audit `Bestellung ansehen` and existing counts. Do not blindly replay an old list of `+` clicks; use absolute **target quantities** so recovery doesn't double items. The cart is persistent user state; work must be idempotent.

**Observed proof:** Two clicks on the correct sweet-potato product produced **2 × Süßkartoffel 1 Stk.**; one click on **Zwiebeln rot 500g** added the requested onion pack; two clicks on **Cherrytomaten 250g** produced 500 g; seven clicks on **Gurke Mini 1 Stk.** produced seven mini cucumbers. The top-right `Bestellung ansehen` item count and price increased as expected.

**Reusable helper:** `scripts/wolt_flink_cart.py` (relative to the skill root) implements an inspection-only mode and a strict exact-listing, target-quantity cart addition mode. Example:

```bash
python3 scripts/wolt_flink_cart.py --tab t9 --search Paprika --inspect
python3 scripts/wolt_flink_cart.py --tab t9 --search Paprika --exact-title 'Paprika Rot 1 Stk.' --target 1 --max-unit-price 2.50
```

The helper refuses to add an ambiguous title, exceed a price ceiling, or treat a loading/timeout state as sold out. **Both `--inspect` and the complete add-and-verify path are live-tested:** `Staudensellerie 1 Stk.` was automatically added and confirmed in the Wolt cart on 2026-10-11. `--recover-only` also completed with the **41 existing items** preserved. The script is UI-specific: revalidate against the live Wolt DOM after retailer UI changes and use the manual runbook when selectors/refs fail.

## Checkpoint 4 — Arthur's brief human review

Present the actual Wolt and REWE cart links/pages and a concise report of what is ready, what couldn't be sourced, any different substitutions, and the payable totals/fees if shown. Ask for corrections only on material exceptions. **Never submit an order, choose irreversible payment, or confirm a purchase** on Arthur's behalf; Arthur reviews and buys.

## Checkpoint 5 — close the loop after purchasing

On the next Gmail receipt, ingest the purchased SKUs and quantities **exactly once**, assume routine successful delivery, update the private purchase ledger/derived stock forecast, and carry unsourced gaps to the next session (unless deliberately canceled). New food photos and user corrections refine the snapshot occasionally; repeated complete cupboard inventories are not a prerequisite.

## Reliability checks and acceptance examples

- **Photo → known SKU:** recognize a manufacturer-specific 750 g frozen broccoli bag from verified reference/product listing; report 750 g × observed count. Unknown open-bag remainder stays uncertain, not “750 g”.
- **Receipt idempotency:** order confirmation + invoice for the same REWE purchase increase stock **once**, not twice. A cart left unpurchased increases stock **zero**.
- **Snapshot reset:** new verified complete inventory supersedes older modeled stock; only later purchases/consumption affect it.
- **Calendar drift:** no mandarins, lemons or chai → source now despite a future 14/28-day marker. Six Skyr with one week coverage → no premature 6-unit top-up; review buying 12 at depletion.
- **Consumption cap:** zero rice/corn/lentil cakes halfway through their four-week allocation → **zero extra packs** until reset.
- **Shared vegetable pool:** 5 × 750 g broccoli → 3.75 kg = 12.5 days at 300 g/day; no automatic additional spinach merely because its staggered block is scheduled.
- **Slow Wolt search:** empty placeholders / stale prior query → short bounded wait → refresh **same Wolt tab** → click **Ja** in `Bestellung fortsetzen?` → verify saved cart count → review results and click the correct plus. Do not infer out of stock from loading or treat search alone as a cart write.
- **Resume modal:** `Nein` means discard; an agent must never click it. Fresh refs must be taken from the new snapshot because old refs become invalid on reload. The current cart count is checked before further changes.
- **Search edit:** if completed `Yogi Tea` results are already visible, a redundant re-fill can trigger another API hang; reuse the visible results before considering a new search.
- **Authorization:** full prepared baskets and links may be displayed; **zero purchases** unless Arthur separately completes checkout.

## Implementation status (as of 2026-10-11)

- **Existing now:** Notion food/rhythm, merchants, fully observed inventory snapshot, working purchase plan, online retailer tabs, and a Gmail connector when connected. Merchant relation migration was reconciled on 2026-10-11.
- **Not yet implemented by this documentation change:** durable private receipt/event ledger, automatic recurring trigger, product image recognition/matching pipeline, persistent SKU image index, robust cart operator orchestration, and automated inventory updating across weeks.
- First practical implementation: confirm the private event-store destination and build a receipt→SKU→inventory reconciliation runner with repeat-safe ingest; instrument it with sample receipt/photo cases; only then schedule weekly triggers and deploy. The skill provides the contract for that engineering work.
