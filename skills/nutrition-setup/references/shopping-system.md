# Grocery shopping system

## Objective

Reduce grocery-order preparation from roughly an hour to a short review. The main difficulty is not payment; it is reconstructing the product list, finding exact listings, choosing substitutes, and deciding quantities under time pressure.

## Current preferred workflow

1. Maintain one canonical recurring list with desired quantity, preferred product, acceptable substitutes, price ceiling, and whether the item is required or optional.
2. Keep a prepared cart in the chosen delivery service. Wolt exposed `Deine Bestellungen` with both `Warenkörbe` and `Nochmal bestellen` when verified on 20 September 2026; re-check the current UI before promising persistence or exact quantity restoration. Use a saved Flink cart as the fast operational copy when it remains suitable.
3. Before ordering, reconcile the saved cart against current inventory and the canonical list.
4. Resolve unavailable items using explicit substitutes or the stored backup shop rather than open-ended browsing.
5. On every second Saturday, review all important Flink gaps. If ordinary carrots, suitable frozen chicken, affordable salmon, or other required acceptable forms are unavailable, prepare a compact in-person REWE list and use REWE that Saturday; this may supplement or replace the Flink order.
6. Review changed prices, quantities, fees, and delivery time, then stop. Arthur must explicitly approve that exact cart and transaction before any action that places the order, confirms payment, or otherwise creates a purchase contract.

The saved shop cart is a convenience cache, not the source of truth: listings can disappear, bundle sizes can change, and quantities can become stale.

The active canonical list has not yet been finalized. Historical baskets and planning quantities below are evidence for drafting it, not permission to order those quantities.

Direct Flink preorder availability is conditional rather than categorically present or absent. On Sunday, 20 September 2026, the direct Flink site offered Monday delivery from 08:00–09:00 under “Heute planen, morgen genießen”; on the preceding Saturday evening it showed closed and blocked checkout. Re-check the address-specific live checkout each time instead of assuming that direct preorder is always unavailable or always available.

## Verified reuse and scheduling capabilities

Read-only browser inspection on 20 September 2026 established the following current capabilities:

- Direct Flink exposes one persistent ordinary cart and an order-history page, but no visible named lists, multiple saved carts, or repeat-order control. Treat it as a single working cart, not as three cycle templates.
- Wolt/Flink exposes `Warenkörbe` and `Nochmal bestellen`. The repeat-order area was empty because no prior Wolt order existed, but its interface explicitly states that completed orders appear there for quick reordering. Seeded weekly, biweekly, and four-week orders can therefore become practical historical templates, although they are not freely named lists and must still be reconciled with the canonical inventory rules.
- Wolt/Flink supports preordering through a day and one-hour delivery-window selector. On Sunday, 20 September 2026, the visible day range extended through Saturday, 26 September, with windows from 09:00–10:00 through 22:00–23:00 for that store. This is about six days of lead time, not an indefinite recurring-delivery schedule; verify the live horizon and slot availability each time.
- Wolt's store-level favorite and `Gemeinsam bestellen` controls are not substitutes for named grocery-cycle templates.

Closest practical automation: on the ordering day, generate the due cycle from the canonical list; use `Nochmal bestellen` for the most relevant prior Wolt order when available; reconcile quantities, substitutions, price, and stock; inspect or provisionally select a delivery window; then stop and present the exact cart, total, substitutions, and window to Arthur. Only after his explicit approval may the current transaction be placed. After a successful order, create or update a calendar block for the confirmed delivery window and list any unavailable essentials that still require a REWE/dm trip. Never create the calendar delivery block before the retailer has confirmed the slot.

## Suggested canonical-list fields

The maintained schema and initial cadence classifications live in [inventory-system.md](inventory-system.md). Use that reference as the source of truth instead of duplicating field definitions here.

For the initial implementation, keep the preferred shop and exact product directly on each food row. Add a separate linked `Shops` table only when shop-level information—membership, delivery threshold, fees, account-specific cadence, or several products from the same supplier—would otherwise be duplicated. A food may link to more than one shop in ranked order.

## Ordering rules

- Prefer inexpensive conventional products unless organic quality has a specific requested benefit.
- Normalize prices per kilogram, liter, or item before comparing.
- Prefer familiar REWE/`ja!` products when price and availability are good; brand is often less important than product type.
- Prefer fewer suppliers and fewer fees when the assortment is adequate.
- Do not silently replace a required product with a materially different one. Follow the stored substitution order or ask.
- Category-level exceptions are explicit: for the monthly ready-to-eat legume target, any canned, jarred, or pouched legume may replace another, prioritizing lentils, then beans of any type, then chickpeas. Never fill this target with uncooked dried legumes, which are paused. For scheduled frozen vegetables, preserve the total weight with a comparably nutritious, priced, stored, and prepared frozen vegetable when the preferred variety is unavailable. A paused frozen vegetable used as a one-order emergency substitute remains paused afterward.
- Avoid accumulating excess perishables. For pantry goods, replenish toward a target stock rather than blindly repeating every historical quantity.
- For products with long safe shelf life, minimize order frequency by replenishing toward the largest practical target stock that fits the available refrigerator, freezer, or pantry capacity and will be consumed before the printed date. Do not default every item to the same one- or two-week horizon.
- Keep final checkout human-confirmed because prices, stock, substitutions, service fees, and delivery windows change. Preparing a cart, opening checkout, or inspecting delivery slots is not authorization to order. Never place an order, confirm payment, or create a purchase contract without Arthur's explicit approval for the exact current cart, total price, and delivery window. Fully unattended purchasing is only a future vision and remains disabled until Arthur deliberately authorizes a separate tested workflow.
- Exclude products that cannot be prepared with the currently usable microwave and steamer setup. Availability alone is not enough.
- Treat the requested form and price band as part of availability. Do not count peeled, pre-cut carrots at a large premium as a substitute for ordinary raw unpeeled carrots; do not buy overpriced pears; and keep salmon within its stored price ceiling.
- Never buy an overpriced version merely because it is the only listing in the preferred form. Treat an unreasonably priced preferred form as unavailable, use an approved cheaper form or substitute when one exists, and otherwise leave the item unfilled. In the final cart report, explicitly disclose every omitted desired product, every case where only an overpriced version was available, and every fallback product selected because of price or availability.
- Batch non-Flink gaps into the fourteen-day REWE decision instead of creating repeated one-product trips. Track dm-only goods, such as buckwheat flakes, separately but buy them on the same physical trip whenever a REWE visit is already planned, because dm is next to REWE.

## Known suppliers and long-cycle stock

These are current stock and replenishment signals, not fully specified recurring orders:

- Flaschenpost: a bulk purchase of Schwarzwaldmilch covering roughly one month; likely recurring supplier for that milk.
- Bugs Trait: 1 kg of freeze-dried egg preordered, creating a shelf-stable egg reserve.
- Myprotein: approximately 5 kg of protein powder were recently replenished. At about 50 g/day this is roughly 100 days of coverage. Do not schedule a calendar reminder; Arthur will initiate the next order when the visible cupboard stock becomes low.
- Sunday Natural: magnesium, L-theanine, and omega-3 products in use.
- Amazon / ProFuel: approximately one year of creatine reserve purchased.
- REWE in person: recurring fallback for ordinary raw carrots, suitable frozen chicken breast, affordable salmon when stocked, ready-to-eat cooked potatoes, beef bone broth, apple-cider vinegar, and other important products unavailable or unsuitable at Flink.
- dm: known source for buckwheat flakes; batch dm-only needs rather than searching Flink.
- Complete Organics direct shop is a comparison source, not the default bulk supplier. On 20 September 2026, shipping within Germany was free from EUR 49; `Alle Fermente` cost EUR 47.99 for ten mixed jars and the six-jar `Kimchi Set` cost EUR 29.99. At the same time, Arthur's logged-in Flink shop offered both 240 g Mild and Original Complete Organics Kimchi for EUR 4.79 each. Therefore the manufacturer's advertised set discount did not beat Flink's per-jar price: the direct six-pack was about EUR 5.00 per jar and the ten-jar mixed set about EUR 4.80 per jar, with some mixed-set jars smaller than 240 g. Compare actual normalized end prices rather than discount percentages; when Flink is already used for the grocery order, allocate no extra delivery charge to kimchi unless adding it changes the order fee.

Track supplier, current reserve, expected depletion, and reorder rule separately from ordinary weekly groceries. Do not place these long-cycle products into every Wolt or Flink cart.

## Observed large Flink basket

The September 2026 basket contained 44 product lines and is evidence of preferences, not a weekly template. Representative groups:

- Frozen vegetables: cauliflower, Scandinavian vegetable mix, creamed mixed vegetables, spinach.
- Nuts: buy only the natural mixed-nut product while individual nut varieties remain paused.
- Fruit: blueberries, grapes, bananas, strawberries, pomegranate, red pepper, avocado, melon, lemons.
- Dairy: Fage yogurt and Andechser kefir.
- Protein: seven packs of pre-cooked frozen chicken fillet steaks, salmon portions, tuna.
- Legumes: chickpeas, white beans, black beans, brown lentils.
- Other recurring foods: kimchi, olive oil, oats, coffee, corn cakes, rice cakes, and lentil cakes. Jarred mushrooms and pumpernickel are currently paused and must not surface automatically.
- Seasonal tea: from the next four-week autumn/winter order, one pack turmeric chai and one pack ginger-lemon tea; prefer Yogi Tea but accept a close equivalent when unavailable. Buy none in the current cycle because existing bags cover the month.

## Historical eight-week planning quantities

These were proposed from stated consumption, not permanently approved standing orders:

- Oats: about 4.5 kg, practically nine 500 g packs.
- Nuts: about 2.8 kg.
- Ground coffee: about 1.68 kg, practically four 500 g packs.
- Protein UHT milk: 16 one-liter cartons, subject to shelf life and storage.
- Fish tins: about 16–20, favoring mackerel and sardines.
- Rice cakes: about 12 packs.
- A mixed rotation of ready-to-eat lentils, black beans, white beans, a few chickpeas, cooked potatoes, microwave rice, and buckwheat flakes.

Always check present stock, current consumption, available storage, and minimum shelf life before using these quantities.

## Provenance

The maintained context was consolidated from:

- ChatGPT conversation `REWE Ausgaben analysieren`, including the workbook `REWE_Lebensmittelprofil_und_Einkaufsstrategie.xlsx` derived from 17 eBons.
- ChatGPT conversation `Backofen identifizieren`.
- ChatGPT conversation `Kühlschrankwahl und Stauraumplanung`.
- A confirmed Flink email receipt from September 2026.
- A confirmed OTTO delivery record for the refrigerator model.

Do not store conversation IDs, order identifiers, addresses, account data, or payment data in this public skill.
