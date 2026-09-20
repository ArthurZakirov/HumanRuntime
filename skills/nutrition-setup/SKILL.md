---
name: nutrition-setup
description: Use Arthur's established household food preferences, kitchen equipment, storage capacity, preparation routines, and grocery history for grocery planning, food storage, substitutions, and kitchen preparation. Do not use as the primary skill for medical nutrition, diagnosis, allergies, supplements, or food-diary logging.
---

# Nutrition Setup

Use the maintained context in this skill instead of asking Arthur to re-explain his kitchen and ordinary food routine.

## Load the relevant context

- For appliance capabilities, storage limits, microwave cookware, or safe operating constraints, read [references/equipment.md](references/equipment.md).
- For established microwave and steam-cooking procedures, read [references/preparation-routines.md](references/preparation-routines.md).
- For foods, consumption rhythms, preferences, and disliked friction, read [references/food-profile.md](references/food-profile.md).
- For grocery lists, recurring quantities, supplier choice, substitutions, or cart automation, read [references/shopping-system.md](references/shopping-system.md).
- For determining what is due now from freshness, consumption, last purchase, and remaining stock, read [references/inventory-system.md](references/inventory-system.md).

Read only the references relevant to the request. A grocery-ordering task normally needs `food-profile.md`, `shopping-system.md`, and `inventory-system.md`; a cooking question normally needs `equipment.md` and `preparation-routines.md`.

## Operating principles

- Treat confirmed equipment models and observed purchase history as facts. Treat proposed quantities and inferred preferences as starting points that may need current confirmation.
- Prefer low-friction methods: few preparation steps, microwave-compatible foods, pre-cooked or ready-to-eat ingredients, saved carts, and explicit substitute rules.
- Arthur is price-conscious and does not value organic certification by itself enough to justify a large premium. Compare like quantities and use conventional products when they meet the need.
- This context supports household decisions; it does not replace current medical, allergy, manufacturer, package, or food-safety guidance.
- Do not infer that a historical purchase is still wanted. Use frequency and quantity as evidence, then reconcile against the current request and current inventory.
- For changing prices, availability, delivery windows, food-safety guidance, or product specifications, verify current information before relying on it.
- For any purchase, prepare or update the cart when authorized, but leave the final order and payment confirmation to Arthur unless he explicitly authorizes that exact transaction.
- Never publish or retain delivery addresses, account identifiers, order numbers, payment details, serial numbers, credentials, or email addresses in this skill.

## Maintaining this context

When Arthur explicitly confirms a durable change to equipment, routine, preference, recurring quantity, or substitution rule, update the appropriate reference. Keep observed history separate from active defaults, record uncertainty directly, and remove obsolete assumptions rather than accumulating conflicting rules.
