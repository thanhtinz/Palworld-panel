# PALCORE Architecture

PALCORE is designed as a control plane for Palworld communities that need server operations, realtime game administration, mod/plugin distribution, economy systems, dungeon/event operations, analytics, and future cloud hosting.

## System Context

```text
                ┌────────────────────┐
                │   Web Dashboard    │
                └─────────┬──────────┘
                          │
                    WebSocket/API
                          │
┌───────────────────────────────────────────┐
│               PALCORE API                 │
├───────────────────────────────────────────┤
│ Auth Service                              │
│ Realtime Gateway                          │
│ Plugin Service                            │
│ Mod Service                               │
│ World Service                             │
│ Analytics Service                         │
│ Economy Service                           │
└───────────────────────────────────────────┘
                          │
                Event Gateway Layer
                          │
        ┌────────────────────────────────┐
        │ UE4SS Hook + Save Parser Core  │
        └────────────────────────────────┘
                          │
                Palworld Dedicated Server
```

## Service Boundaries

| Service | Responsibility | Phase |
| --- | --- | --- |
| Auth Service | Users, organizations, server access, API tokens, plugin permissions, audit identity. | 1 |
| Server Service | Create/delete, start/stop/restart, scheduled restarts, backups, crash recovery, config editing, Docker deployment. | 1 |
| Realtime Gateway | WebSocket sessions, event fan-out, live logs, player join/leave, raid, dungeon, economy, and guild-war streams. | 2 |
| World Service | Player locations, base locations, bosses, resources, map layers, Pal tracking, and save parser ingestion. | 2 |
| Advanced Pal Service | Global Pal registry, live AI state, spawn orchestration, breeding/genetics, evolution, fusion, jobs, equipment, combat replay, marketplace, and cross-server transfer APIs. | 4 |
| Plugin Service | Plugin manifests, SDK runtimes, dependencies, permissions, event subscriptions, marketplace publication. | 3 |
| Mod Service | `.pak` uploads, enable/disable, dependency install, conflict detection, version management, rollback, modpacks. | 3 |
| Dungeon Service | Dungeon resets, scheduling, boss forcing, cooldowns, difficulty scaling, custom raid/event definitions. | 4 |
| Economy Service | Currency, marketplace, auction house, guild bank, taxes, trade logs, dynamic pricing, cross-server trading. | 4 |
| Analytics Service | Retention, popular Pals, economy circulation, dungeon completion, heatmaps, server load, guild growth. | 4 |
| Hosting Service | Billing, plans, cloud backups, autoscaling, multi-tenant provisioning, mobile alerts, enterprise controls. | 5 |

## Data Architecture

PostgreSQL is the system of record for users, servers, players, Pals, guilds, dungeons, plugins, mods, transactions, and events. Redis is the realtime cache for player/world state, WebSocket sessions, event fan-out, rate limits, and short-lived health metrics.

## Event Gateway

The Event Gateway normalizes data from UE4SS Lua hooks, save parser snapshots, logs, and administrative API actions into `EventEnvelope` objects. The envelope carries a topic, server ID, occurrence timestamp, event ID, and JSON payload so dashboard, analytics, plugins, and mobile alerts can consume a consistent contract.

## Plugin Runtime Strategy

Plugins are distributed with a manifest containing name, version, author, dependencies, permissions, and supported runtimes. The first implementation should run plugins in restricted workers with explicit event subscriptions and scoped APIs for economy, world state, guilds, dungeons, moderation, and analytics.

## Delivery Roadmap

1. **Core server manager:** lifecycle commands, backups, monitoring, config editor, crash recovery, logs.
2. **Realtime dashboard:** WebSocket gateway, live logs, dashboard overview, live world map event stream.
3. **Plugin ecosystem:** SDK, plugin manifests, event bus, marketplace metadata, dependency/permission model.
4. **Advanced MMO systems:** economy, guild wars, dungeons, anti-cheat, advanced Pal registry/breeding/genetics/AI systems, analytics.
5. **Cloud hosting:** SaaS plans, billing, autoscaling, cloud backups, enterprise tenancy, mobile app operations.
