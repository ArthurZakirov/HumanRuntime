# Notion inventory

Use the connected Notion workspace database named **Wäsche-Inventar** as the current structured inventory for laundry planning. Locate it by its exact title through the Notion connector; do not depend on a workspace-specific database identifier stored in this public skill.

## Source roles

- Notion is the current operational view for itemized textiles, care settings, quantities, colors, use/status, and source links.
- `inventory.md` is the public portable snapshot and provenance-friendly fallback.
- `wardrobe.md` is the unresolved discovery backlog. An item that has been migrated into Notion and `inventory.md` must no longer remain as a separately countable backlog item.

If Notion is unavailable, use the Markdown snapshot and say that live inventory changes could not be checked. Do not silently treat the fallback as current.

## Reading the database

Before proposing a load or answering what Arthur owns, query **Wäsche-Inventar** for the relevant rows. Use its structured fields directly rather than extracting settings from long prose:

- `Gegenstand`, `Kategorie`, `Anzahl`, `Größe`, and `Farben`
- `Routine-Temperatur °C`, `Maximaltemperatur °C`, `Programm`, and `Schleudern U/min`
- `Trocknung`, `Waschmittelklasse`, and `Waschmittelhinweis`
- `Material & Details`, `Pflegehinweise`, `Intervall & Auslöser`, and `Kombinationshinweise`
- `Nutzung / Status`, `Datenstatus`, and `Produkt-/Quellen-URL`
- dimensions in `Breite cm`, `Länge cm`, and `Höhe cm` when present

Treat `Datenstatus` as part of the answer. Do not present an assumption or a row needing a label as verified product guidance.

## Updating the database

Use one row for one identifiable product or coherent item group with the same care properties. Preserve the database's structured property types: temperatures, spin speed, quantity, and dimensions are numbers; category, program, drying, detergent class, size, and data status are selections; colors are a multi-selection; the product/source link is a URL.

After a successful Notion mutation, make the equivalent change in the canonical HumanRuntime references during the same authorized maintenance task. If either side cannot be updated, report which source is stale instead of claiming they are synchronized.

Keep workspace identifiers, account details, credentials, addresses, and other private context out of this public skill repository.
