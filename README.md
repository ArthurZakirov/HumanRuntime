# HumanRuntime

> Maintain the human runtime behind the agents.

HumanRuntime packages reusable agent skills for the personal systems that keep an engineer functioning: nutrition tracking, an ergonomic physical workspace, and cost-aware household laundry.

## Skills

- `cronometer-diary` logs dictated meals in Cronometer and maintains confirmed food mappings and reusable meal bundles.
- `desk-ergonomics-setup` records the physical desk, furniture, charging, lighting, and ergonomic context used for workspace decisions.
- `laundry-planner` maintains a textile-care inventory and builds compatible, sufficiently full AppWash loads.
- `nutrition-setup` supplies Arthur's established food preferences, kitchen equipment, preparation routines, storage context, and grocery-shopping system.

These skills may contain explicitly approved personal routines and equipment details. They must not contain addresses, account credentials, insurance information, career targets, employer-internal material, or other unapproved private records.

## Install

Install all skills for Codex, Claude Code, and OpenCode:

```bash
npx skills add https://github.com/ArthurZakirov/HumanRuntime --skill '*' -a codex claude-code opencode -g -y
```

List the available skills first:

```bash
npx skills add https://github.com/ArthurZakirov/HumanRuntime --list
```

For local development from a cloned repo, link skills into Claude Code, `.agents`, and Codex skill directories:

```bash
./scripts/setup-local-links.sh
```

Existing non-symlink paths are left untouched unless `--force` is used.

## Use

Describe the task or invoke a skill directly:

```text
Use cronometer-diary to log my dictated breakfast in Cronometer.
Use desk-ergonomics-setup to plan a better layout with my existing equipment.
Use laundry-planner to choose the next compatible AppWash load.
```

## Public boundary

See [docs/public-private-boundary.md](docs/public-private-boundary.md) before adding personal context.
