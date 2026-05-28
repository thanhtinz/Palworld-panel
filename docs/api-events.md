# PALCORE Realtime Event API

PALCORE realtime integrations use a canonical event envelope over WebSocket and internal queues.

## Envelope

```json
{
  "event_id": "uuid",
  "topic": "server.health",
  "server_id": "uuid",
  "occurred_at": "2026-05-28T00:00:00Z",
  "payload": {}
}
```

## Topic Taxonomy

| Domain | Topics |
| --- | --- |
| Player | `player.join`, `player.leave`, `player.death`, `player.level_up` |
| Pal | `pal.spawned`, `pal.updated` |
| World | `world.boss_spawn`, `world.weather_change` |
| Dungeon | `dungeon.open`, `dungeon.clear` |
| Economy | `economy.item_sold`, `economy.auction_win`, `economy.guild_trade` |
| Guild | `guild.war_started` |
| Server | `server.health` |

## Gateway Sources

- UE4SS Lua hooks for live gameplay events and administrative actions.
- Save parser snapshots for authoritative world, Pal, inventory, base, and guild data.
- Dedicated server logs for console, crash, player, and audit streams.
- PALCORE API commands for moderation, economy, dungeon, plugin, and mod actions.

## Consumer Types

- Web dashboard widgets and live map layers.
- Analytics pipelines and retention/economy/dungeon reports.
- Plugin SDK workers that subscribe to scoped topics.
- Mobile alerts for restarts, crashes, player moderation, and dungeon/world events.
