# PALCORE

**PALCORE** is an advanced Palworld server panel and mod ecosystem: a dedicated server manager, realtime world administration console, plugin/mod marketplace foundation, live map system, dungeon/event operator, economy framework, web dashboard, and future SaaS hosting layer.

The product goal is to become an **“Operating System for Palworld Servers”**—combining the ergonomics of a Linux game panel, the extensibility of a mod marketplace, and MMO-grade live operations tooling for Palworld communities.

## What is included now

This repository now contains a runnable full-source PALCORE panel prototype:

- A dependency-free local web server for development against a configurable data source.
- A responsive web panel with overview, server fleet, player moderation, advanced Pal management, live map, dungeon scheduler, economy, modules, and audit/event sections.
- A framework-light Python domain layer for server, player, Pal, guild, dungeon, economy, map, audit, plugin, and realtime event contracts.
- JSON-backed dashboard contracts in `palcore/data/dashboard.default.json`; runtime game records stay empty until `PALCORE_DASHBOARD_DATA=/path/to/state.json` points at real/exported data.
- An optional FastAPI control-plane entrypoint with API routes and a WebSocket demo stream.
- Architecture and realtime event API documentation.
- Pytest regression coverage for the core domain and dashboard state.

## Quick Start

Run the panel without installing any web framework dependencies:

```bash
python -m palcore.dev_server
```

Open <http://127.0.0.1:8000> and use the bundled API:

- `GET /health`
- `GET /api/v1/dashboard`
- `GET /api/v1/modules`
- `GET /api/v1/servers`
- `GET /api/v1/pals/system`
- `GET /api/v1/events/schema`

Run tests:

```bash
python -m pytest
```

To run the optional FastAPI app after installing API dependencies:

```bash
pip install -e .[api]
uvicorn palcore.app:create_app --factory --reload
```

## Repository Layout

```text
palcore/
  app.py                 # Optional FastAPI application factory and API routes
  dev_server.py          # Dependency-free stdlib panel server
  domain.py              # Core PALCORE domain models and data-source builders
  data/
    dashboard.default.json  # Product catalog defaults; runtime record arrays are empty
  static/
    index.html           # Web dashboard shell
    app.css              # Responsive dark MMO/admin panel styling
    app.js               # Dashboard API client and render logic
  __init__.py            # Public package exports
docs/
  architecture.md        # System architecture, service boundaries, and roadmap
  api-events.md          # Realtime event contract and topic taxonomy
tests/
  test_domain.py         # Domain model regression tests
```

## Data Source

The panel no longer ships fake server/player/Pal records in Python or JSON. By default it reads `palcore/data/dashboard.default.json`, which keeps product catalogs and advanced Pal capability contracts but leaves runtime record arrays empty. To point the dev server or FastAPI app at real/exported state, set:

```bash
PALCORE_DASHBOARD_DATA=/absolute/path/to/dashboard.json python -m palcore.dev_server
```

This keeps UI/API contracts stable while ensuring server, player, Pal, guild, dungeon, economy, map, and audit rows come from an external data source.

## Advanced Pal System

PALCORE now models Pals as live MMO entities instead of simple spawn records:

- Realtime tracking with Pal ID, species, level, owner, guild, 3D location, HP, stamina, passives, skills, mood, AI state, current action, and current target.
- Global registry concepts for rarity tracking, trait indexing, breeding history, ownership history, and filters by element, rarity, passive, IV/stat, alpha/boss, or guild owner.
- Spawn controls for wild, dungeon, raid, admin, event, shiny/custom variant, mass, and timed spawns with level/stat scaling, passive injection, and custom movesets.
- Breeding/genetics systems for calculators, simulators, mutation chance, inherited traits, hidden genes, elemental affinity, evolution trees, and fusion recipes.
- AI/job systems for aggressive, passive, worker, defensive, patrol, escort, combat, and pathfinding states with force attack/gather/patrol and AI override controls.
- Marketplace, equipment, skill tree, personality, loyalty, fatigue, combat replay, dungeon companion, death/recovery, ranking, collection, creator, map-layer, cross-server, dynamic event, and public API foundations.

## Core Capabilities

- Create, start, stop, restart, back up, and monitor multiple Palworld server instances.
- Stream realtime updates for players, guilds, raids, dungeons, economy transactions, and server health.
- Moderate players with kick/ban/mute, teleport, inventory/stat edits, playtime history, guild tools, and audit trails.
- Track and administer Pals with species, level, skills, passives, health, stamina, owner, coordinates, genealogy, breeding, and marketplace hooks.
- Render a live world map with players, bases, bosses, resources, dungeon entrances, guild territories, PvP/safe zones, and active events.
- Manage dungeons, custom raids, timed events, boss spawns, difficulty scaling, loot tracking, and analytics.
- Provide an economy framework with currencies, shops, auction house, guild banks, taxes, trade logs, rare Pal markets, and plugin APIs.
- Support plugin SDKs and mod lifecycle management with manifests, dependency checks, conflict detection, rollbacks, ratings, and verified creators.
- Add anti-cheat, guild systems, analytics, cloud backups, subscriptions, mobile alerts, and developer revenue sharing over time.

## Roadmap

1. **Core server manager:** lifecycle controls, backups, monitoring, config editor, crash recovery.
2. **Realtime dashboard:** WebSocket gateway, live logs, live map, player/guild/world activity feeds.
3. **Plugin ecosystem:** SDK, marketplace, event bus, permissions, dependency resolution.
4. **Advanced MMO systems:** economy, guild wars, dungeon scheduler, anti-cheat, analytics.
5. **Cloud hosting platform:** SaaS billing, multi-tenant control plane, auto scaling, backups, mobile app.
