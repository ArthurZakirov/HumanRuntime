---
name: laundry-planner
description: Plan and update Arthur's household laundry using his recorded textile inventory and shared AppWash laundry room. Use for washing schedules, load grouping, textile care, or AppWash availability checks.
---

# Laundry planner

Maintain a practical, low-waste laundry routine. Use the live Notion inventory and the laundry-room facts in the references before proposing a wash. Confirm care labels whenever an item is not yet verified; do not turn a likely setting into a certainty.

Read [notion-inventory.md](references/notion-inventory.md) before reading or changing the textile inventory. Read [inventory.md](references/inventory.md) for the public portable snapshot of items with established care guidance, [wardrobe.md](references/wardrobe.md) for the broader wardrobe and care-verification backlog, [laundry-room.md](references/laundry-room.md) for the machines and AppWash workflow, and [shared-machine-hygiene.md](references/shared-machine-hygiene.md) before advising on hygiene in the communal laundry room. Do not add aggregate or historical wardrobe counts to itemized inventory counts unless the overlap has been resolved.

## Planning principles

- Build one compatible load at a time: first separate by maximum safe temperature and fiber type, then by color. Never mix microfiber or encasings with lint-producing cotton towel loads.
- Use a sufficiently filled drum, but do not compact it. For the assumed 7 kg washer, cotton loads may be comfortably full; bulky bedding and a 140 x 200 cm mattress cover need their own deliberately sized load.
- Treat a 2.80 € AppWash start as a fixed charge. Optimize by waiting for compatible laundry, unless hygiene, odor, stains, or lack of essentials requires an earlier wash.
- Give frequency as a normal interval plus earlier triggers. Prefer the product label over general advice.
- Do not start, reserve, cancel, or pay for an AppWash machine unless the user explicitly asks for that action.

## Routine update

When the user adds an item, update the Notion database and the matching canonical Markdown reference in the same maintenance pass. Add its quantity, dimensions when useful, fiber content, exact care label or source, temperature limit, drying limit, color group, suitable load family, normal wash interval, washing-machine program, spin speed, detergent class, status, and product/source URL when available. Put natural-language wardrobe discoveries with missing care data in `references/wardrobe.md` until their labels or exact models are checked. When an item is migrated into the structured inventory, remove or narrow its backlog entry so it is not counted twice. Mark information as `verified`, `partially verified`, `label needed`, `historical`, or `assumption`.

When asked to plan, report: items ready now, the best next compatible load, program and temperature, a fullness check, what must stay out, and what to save for the next load. Check the logged-in AppWash page only if current availability matters.
