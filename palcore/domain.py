"""Core PALCORE domain primitives and configurable data loading.

The models in this module intentionally avoid framework dependencies so they can
be shared by the API, workers, plugin SDKs, tests, and future CLI tooling.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4


class ServerStatus(StrEnum):
    """Lifecycle states for a managed Palworld server instance."""

    CREATING = "creating"
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    RESTARTING = "restarting"
    BACKING_UP = "backing_up"
    CRASHED = "crashed"


class Severity(StrEnum):
    """Operational severity used by audit, moderation, and alert streams."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass(frozen=True, slots=True)
class ModuleCapability:
    """A major PALCORE product module exposed to the dashboard and API."""

    key: str
    name: str
    summary: str
    phase: int
    capabilities: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class PluginManifest:
    """Manifest required for marketplace and server-side plugin loading."""

    name: str
    version: str
    author: str = "PALCORE"
    dependencies: tuple[str, ...] = ()
    permissions: tuple[str, ...] = ()
    runtimes: tuple[str, ...] = ("python", "lua", "javascript")

    def normalized_slug(self) -> str:
        """Return a stable directory-safe plugin slug."""

        return self.name.strip().lower().replace(" ", "-").replace("_", "-")


@dataclass(slots=True)
class ServerInstance:
    """A managed Palworld dedicated server registered in PALCORE."""

    name: str
    region: str
    status: ServerStatus = ServerStatus.STOPPED
    server_id: UUID = field(default_factory=uuid4)
    max_players: int = 32
    online_players: int = 0
    cpu_percent: float = 0.0
    ram_mb: int = 0
    disk_gb: float = 0.0
    tps: float = 0.0
    fps: float = 0.0
    network_in_mbps: float = 0.0
    network_out_mbps: float = 0.0
    last_backup_at: datetime | None = None

    def health_score(self) -> int:
        """Calculate a simple 0-100 health score for dashboard summaries."""

        score = 100
        if self.status in {ServerStatus.CRASHED, ServerStatus.CREATING}:
            score -= 40
        if self.cpu_percent >= 90:
            score -= 20
        elif self.cpu_percent >= 75:
            score -= 10
        if self.ram_mb >= 24_576:
            score -= 15
        if self.tps and self.tps < 20:
            score -= 10
        return max(0, min(100, score))


@dataclass(frozen=True, slots=True)
class PlayerProfile:
    """Realtime player profile used by moderation and live map widgets."""

    player_id: UUID
    name: str
    level: int
    guild: str
    playtime_hours: float
    ping_ms: int
    coordinates: tuple[float, float]
    status: str = "online"
    warnings: int = 0
    last_seen_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True, slots=True)
class Location3D:
    """Game-space location for live Pal/entity tracking."""

    x: float
    y: float
    z: float = 0.0

    def map_coordinates(self) -> tuple[float, float]:
        """Project 3D game coordinates into the current 2D panel map space."""

        return (self.x, self.y)


@dataclass(frozen=True, slots=True)
class PalProfile:
    """Realtime Pal state surfaced in the advanced Pal management system."""

    pal_id: str
    species: str
    level: int
    owner: str
    guild: str
    location: Location3D
    hp: int
    stamina: int
    passives: tuple[str, ...]
    skills: tuple[str, ...]
    mood: str
    ai_state: str
    current_action: str
    current_target: str | None = None
    element: str = "neutral"
    rarity: str = "common"
    is_alpha: bool = False
    is_shiny: bool = False
    ivs: dict[str, int] = field(default_factory=dict)
    genetics: dict[str, Any] = field(default_factory=dict)
    personality: str = "loyal"
    loyalty: int = 0
    fatigue: int = 0
    market_value: int = 0

    @property
    def coordinates(self) -> tuple[float, float]:
        """Backward-compatible 2D map coordinates for the static panel."""

        return self.location.map_coordinates()

    @property
    def hp_percent(self) -> int:
        """Compatibility alias for older dashboard widgets."""

        return self.hp

    @property
    def stamina_percent(self) -> int:
        """Compatibility alias for older dashboard widgets."""

        return self.stamina

    @property
    def passive_traits(self) -> tuple[str, ...]:
        """Compatibility alias for older dashboard widgets."""

        return self.passives


@dataclass(frozen=True, slots=True)
class AdvancedPalSystem:
    """Configuration and capability model for PALCORE's MMO Pal platform."""

    goal: str
    pillars: tuple[str, ...]
    registry_features: tuple[str, ...]
    registry_filters: tuple[str, ...]
    viewer_actions: tuple[str, ...]
    realtime_actions: tuple[str, ...]
    spawn_features: tuple[str, ...]
    spawn_types: tuple[str, ...]
    spawn_controls: tuple[str, ...]
    breeding_features: tuple[str, ...]
    gene_flow: tuple[str, ...]
    genetics: dict[str, Any]
    evolution: dict[str, Any]
    fusion: dict[str, Any]
    ai_states: tuple[str, ...]
    ai_controls: tuple[str, ...]
    job_system: dict[str, Any]
    marketplace: dict[str, Any]
    equipment: dict[str, Any]
    skill_trees: dict[str, Any]
    personalities: dict[str, Any]
    loyalty_bond: dict[str, Any]
    fatigue: dict[str, Any]
    combat_viewer: dict[str, Any]
    dungeon: dict[str, Any]
    death_recovery: dict[str, Any]
    rankings: tuple[str, ...]
    collection: dict[str, Any]
    creator_tools: tuple[str, ...]
    map_layer: tuple[str, ...]
    cross_server: tuple[str, ...]
    dynamic_events: tuple[dict[str, str], ...]
    public_api: tuple[str, ...]
    future_vision: str

    def feature_count(self) -> int:
        """Return a rough count of configured advanced Pal capabilities."""

        return sum(
            len(section)
            for section in (
                self.registry_features,
                self.viewer_actions,
                self.spawn_features,
                self.breeding_features,
                self.ai_controls,
                self.rankings,
                self.creator_tools,
                self.public_api,
            )
        )


@dataclass(frozen=True, slots=True)
class GuildProfile:
    """Guild dashboard aggregate for territory, economy, and war systems."""

    guild_id: UUID
    name: str
    leader: str
    members_online: int
    total_members: int
    territory_count: int
    bank_balance: int
    war_score: int


@dataclass(frozen=True, slots=True)
class DungeonRun:
    """Dungeon/event operations card shown to live operators."""

    dungeon_id: UUID
    name: str
    difficulty: str
    status: str
    boss: str
    next_reset_at: datetime
    completion_rate: float
    fastest_clear_seconds: int
    death_count: int


@dataclass(frozen=True, slots=True)
class EconomyMetric:
    """Economy dashboard metric for marketplace and currency operations."""

    label: str
    value: int
    change_percent: float
    unit: str = "coins"


@dataclass(frozen=True, slots=True)
class MapMarker:
    """Live world map marker normalized from game coordinates."""

    marker_id: UUID
    marker_type: str
    label: str
    x: float
    y: float
    severity: Severity = Severity.INFO


@dataclass(frozen=True, slots=True)
class AuditLogEntry:
    """Operator/audit event displayed in the admin activity feed."""

    log_id: UUID
    actor: str
    action: str
    target: str
    severity: Severity
    occurred_at: datetime


@dataclass(frozen=True, slots=True)
class WorldSnapshot:
    """Realtime world-state aggregate emitted to dashboards and map clients."""

    server_id: UUID
    online_players: int
    active_guilds: int
    active_dungeons: int
    boss_events: int
    economy_transactions_per_minute: int
    captured_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True, slots=True)
class EventEnvelope:
    """Canonical realtime event payload sent through WebSocket/API gateways."""

    topic: str
    server_id: UUID
    payload: dict[str, Any]
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_wire(self) -> dict[str, Any]:
        """Serialize the event into JSON-compatible primitives."""

        return {
            "event_id": str(self.event_id),
            "topic": self.topic,
            "server_id": str(self.server_id),
            "occurred_at": self.occurred_at.isoformat(),
            "payload": self.payload,
        }


@dataclass(frozen=True, slots=True)
class DashboardState:
    """Complete state consumed by the PALCORE web panel."""

    modules: tuple[ModuleCapability, ...]
    servers: tuple[ServerInstance, ...]
    players: tuple[PlayerProfile, ...]
    pals: tuple[PalProfile, ...]
    pal_system: AdvancedPalSystem
    guilds: tuple[GuildProfile, ...]
    dungeons: tuple[DungeonRun, ...]
    economy: tuple[EconomyMetric, ...]
    map_markers: tuple[MapMarker, ...]
    audit_logs: tuple[AuditLogEntry, ...]
    event_topics: tuple[str, ...]

    def totals(self) -> dict[str, int | float]:
        """Return headline metrics for the dashboard hero cards."""

        total_players = sum(server.online_players for server in self.servers)
        capacity = sum(server.max_players for server in self.servers)
        average_health = round(sum(server.health_score() for server in self.servers) / len(self.servers), 1) if self.servers else 0
        return {
            "online_players": total_players,
            "player_capacity": capacity,
            "average_health": average_health,
            "active_guilds": len(self.guilds),
            "tracked_pals": len(self.pals),
            "active_dungeons": sum(1 for dungeon in self.dungeons if dungeon.status != "cooldown"),
            "pal_system_features": self.pal_system.feature_count(),
        }



DEFAULT_DATA_FILE = Path(__file__).with_name("data") / "dashboard.default.json"
DATA_FILE_ENV = "PALCORE_DASHBOARD_DATA"


def _data_file(data_file: str | os.PathLike[str] | None = None) -> Path:
    """Resolve the dashboard data source without hardcoding records in code."""

    configured = data_file or os.environ.get(DATA_FILE_ENV)
    return Path(configured) if configured else DEFAULT_DATA_FILE


def load_dashboard_payload(data_file: str | os.PathLike[str] | None = None) -> dict[str, Any]:
    """Load dashboard/control-plane data from JSON.

    The bundled JSON file contains product catalog defaults only; runtime server,
    player, Pal, guild, dungeon, market, map, and audit rows are expected to
    come from ``PALCORE_DASHBOARD_DATA`` or an explicit ``data_file``.
    """

    path = _data_file(data_file)
    with path.open(encoding="utf-8") as file:
        payload = json.load(file)
    return payload


def _parse_uuid(value: str | UUID | None) -> UUID:
    return value if isinstance(value, UUID) else UUID(str(value)) if value else uuid4()


def _parse_datetime(value: str | datetime | None) -> datetime | None:
    if value is None or isinstance(value, datetime):
        return value
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _coordinates(value: list[float] | tuple[float, float]) -> tuple[float, float]:
    x, y = value
    return (float(x), float(y))


def _location_from_dict(value: dict[str, Any] | list[float] | tuple[float, ...]) -> Location3D:
    if isinstance(value, dict):
        return Location3D(x=float(value.get("x", 0.0)), y=float(value.get("y", 0.0)), z=float(value.get("z", 0.0)))
    x, y, *rest = value
    return Location3D(x=float(x), y=float(y), z=float(rest[0]) if rest else 0.0)


def _string_tuple(value: Any) -> tuple[str, ...]:
    return tuple(str(item) for item in value or ())


def _module_from_dict(item: dict[str, Any]) -> ModuleCapability:
    return ModuleCapability(
        key=item["key"],
        name=item["name"],
        summary=item["summary"],
        phase=int(item["phase"]),
        capabilities=tuple(item.get("capabilities", ())),
    )


def _server_from_dict(item: dict[str, Any]) -> ServerInstance:
    return ServerInstance(
        server_id=_parse_uuid(item.get("server_id")),
        name=item["name"],
        region=item["region"],
        status=ServerStatus(item.get("status", ServerStatus.STOPPED.value)),
        max_players=int(item.get("max_players", 32)),
        online_players=int(item.get("online_players", 0)),
        cpu_percent=float(item.get("cpu_percent", 0.0)),
        ram_mb=int(item.get("ram_mb", 0)),
        disk_gb=float(item.get("disk_gb", 0.0)),
        tps=float(item.get("tps", 0.0)),
        fps=float(item.get("fps", 0.0)),
        network_in_mbps=float(item.get("network_in_mbps", 0.0)),
        network_out_mbps=float(item.get("network_out_mbps", 0.0)),
        last_backup_at=_parse_datetime(item.get("last_backup_at")),
    )


def _player_from_dict(item: dict[str, Any]) -> PlayerProfile:
    return PlayerProfile(
        player_id=_parse_uuid(item.get("player_id")),
        name=item["name"],
        level=int(item["level"]),
        guild=item["guild"],
        playtime_hours=float(item["playtime_hours"]),
        ping_ms=int(item["ping_ms"]),
        coordinates=_coordinates(item["coordinates"]),
        status=item.get("status", "online"),
        warnings=int(item.get("warnings", 0)),
        last_seen_at=_parse_datetime(item.get("last_seen_at")) or datetime.now(UTC),
    )


def _pal_from_dict(item: dict[str, Any]) -> PalProfile:
    return PalProfile(
        pal_id=str(item.get("pal_id") or _parse_uuid(None)),
        species=item["species"],
        level=int(item["level"]),
        owner=item["owner"],
        guild=item.get("guild", "unguilded"),
        location=_location_from_dict(item.get("location") or item.get("coordinates", (0, 0))),
        hp=int(item.get("hp", item.get("hp_percent", 0))),
        stamina=int(item.get("stamina", item.get("stamina_percent", 0))),
        passives=_string_tuple(item.get("passives", item.get("passive_traits", ()))),
        skills=_string_tuple(item.get("skills", ())),
        mood=item.get("mood", "idle"),
        ai_state=item.get("ai_state", "passive"),
        current_action=item.get("current_action", item.get("mood", "idle")),
        current_target=item.get("current_target"),
        element=item.get("element", "neutral"),
        rarity=item.get("rarity", "common"),
        is_alpha=bool(item.get("is_alpha", False)),
        is_shiny=bool(item.get("is_shiny", False)),
        ivs={key: int(value) for key, value in item.get("ivs", {}).items()},
        genetics=dict(item.get("genetics", {})),
        personality=item.get("personality", "loyal"),
        loyalty=int(item.get("loyalty", 0)),
        fatigue=int(item.get("fatigue", 0)),
        market_value=int(item.get("market_value", 0)),
    )


def _advanced_pal_system_from_dict(item: dict[str, Any] | None) -> AdvancedPalSystem:
    item = item or {}
    return AdvancedPalSystem(
        goal=item.get("goal", "Advanced Pal management platform"),
        pillars=_string_tuple(item.get("pillars", ())),
        registry_features=_string_tuple(item.get("registry_features", ())),
        registry_filters=_string_tuple(item.get("registry_filters", ())),
        viewer_actions=_string_tuple(item.get("viewer_actions", ())),
        realtime_actions=_string_tuple(item.get("realtime_actions", ())),
        spawn_features=_string_tuple(item.get("spawn_features", ())),
        spawn_types=_string_tuple(item.get("spawn_types", ())),
        spawn_controls=_string_tuple(item.get("spawn_controls", ())),
        breeding_features=_string_tuple(item.get("breeding_features", ())),
        gene_flow=_string_tuple(item.get("gene_flow", ())),
        genetics=dict(item.get("genetics", {})),
        evolution=dict(item.get("evolution", {})),
        fusion=dict(item.get("fusion", {})),
        ai_states=_string_tuple(item.get("ai_states", ())),
        ai_controls=_string_tuple(item.get("ai_controls", ())),
        job_system=dict(item.get("job_system", {})),
        marketplace=dict(item.get("marketplace", {})),
        equipment=dict(item.get("equipment", {})),
        skill_trees=dict(item.get("skill_trees", {})),
        personalities=dict(item.get("personalities", {})),
        loyalty_bond=dict(item.get("loyalty_bond", {})),
        fatigue=dict(item.get("fatigue", {})),
        combat_viewer=dict(item.get("combat_viewer", {})),
        dungeon=dict(item.get("dungeon", {})),
        death_recovery=dict(item.get("death_recovery", {})),
        rankings=_string_tuple(item.get("rankings", ())),
        collection=dict(item.get("collection", {})),
        creator_tools=_string_tuple(item.get("creator_tools", ())),
        map_layer=_string_tuple(item.get("map_layer", ())),
        cross_server=_string_tuple(item.get("cross_server", ())),
        dynamic_events=tuple(dict(event) for event in item.get("dynamic_events", ())),
        public_api=_string_tuple(item.get("public_api", ())),
        future_vision=item.get("future_vision", "MMO creature ecosystem platform"),
    )


def _guild_from_dict(item: dict[str, Any]) -> GuildProfile:
    return GuildProfile(
        guild_id=_parse_uuid(item.get("guild_id")),
        name=item["name"],
        leader=item["leader"],
        members_online=int(item["members_online"]),
        total_members=int(item["total_members"]),
        territory_count=int(item["territory_count"]),
        bank_balance=int(item["bank_balance"]),
        war_score=int(item["war_score"]),
    )


def _dungeon_from_dict(item: dict[str, Any]) -> DungeonRun:
    reset_at = _parse_datetime(item["next_reset_at"])
    if reset_at is None:
        raise ValueError("Dungeon next_reset_at is required")
    return DungeonRun(
        dungeon_id=_parse_uuid(item.get("dungeon_id")),
        name=item["name"],
        difficulty=item["difficulty"],
        status=item["status"],
        boss=item["boss"],
        next_reset_at=reset_at,
        completion_rate=float(item["completion_rate"]),
        fastest_clear_seconds=int(item["fastest_clear_seconds"]),
        death_count=int(item["death_count"]),
    )


def _economy_from_dict(item: dict[str, Any]) -> EconomyMetric:
    return EconomyMetric(
        label=item["label"],
        value=int(item["value"]),
        change_percent=float(item["change_percent"]),
        unit=item.get("unit", "coins"),
    )


def _marker_from_dict(item: dict[str, Any]) -> MapMarker:
    return MapMarker(
        marker_id=_parse_uuid(item.get("marker_id")),
        marker_type=item["marker_type"],
        label=item["label"],
        x=float(item["x"]),
        y=float(item["y"]),
        severity=Severity(item.get("severity", Severity.INFO.value)),
    )


def _audit_from_dict(item: dict[str, Any]) -> AuditLogEntry:
    occurred_at = _parse_datetime(item["occurred_at"])
    if occurred_at is None:
        raise ValueError("Audit log occurred_at is required")
    return AuditLogEntry(
        log_id=_parse_uuid(item.get("log_id")),
        actor=item["actor"],
        action=item["action"],
        target=item["target"],
        severity=Severity(item["severity"]),
        occurred_at=occurred_at,
    )


def to_jsonable(value: Any) -> Any:
    """Convert PALCORE domain objects into JSON-compatible primitives."""

    if isinstance(value, StrEnum):
        return value.value
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if is_dataclass(value):
        return {key: to_jsonable(item) for key, item in asdict(value).items()}
    if isinstance(value, tuple | list):
        return [to_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {key: to_jsonable(item) for key, item in value.items()}
    return value


def build_modules(data_file: str | os.PathLike[str] | None = None) -> tuple[ModuleCapability, ...]:
    """Build module catalog records from the configured JSON data source."""

    payload = load_dashboard_payload(data_file)
    return tuple(_module_from_dict(item) for item in payload.get("modules", ()))


def build_event_topics(data_file: str | os.PathLike[str] | None = None) -> tuple[str, ...]:
    """Build realtime topic catalog records from the configured JSON data source."""

    payload = load_dashboard_payload(data_file)
    return tuple(str(topic) for topic in payload.get("event_topics", ()))


def build_servers(data_file: str | os.PathLike[str] | None = None) -> tuple[ServerInstance, ...]:
    """Build server records from the configured JSON data source."""

    payload = load_dashboard_payload(data_file)
    return tuple(_server_from_dict(item) for item in payload.get("servers", ()))


def build_dashboard_state(data_file: str | os.PathLike[str] | None = None) -> DashboardState:
    """Build panel state from a JSON data source rather than hardcoded objects."""

    payload = load_dashboard_payload(data_file)
    return DashboardState(
        modules=tuple(_module_from_dict(item) for item in payload.get("modules", ())),
        servers=tuple(_server_from_dict(item) for item in payload.get("servers", ())),
        players=tuple(_player_from_dict(item) for item in payload.get("players", ())),
        pals=tuple(_pal_from_dict(item) for item in payload.get("pals", ())),
        pal_system=_advanced_pal_system_from_dict(payload.get("pal_system")),
        guilds=tuple(_guild_from_dict(item) for item in payload.get("guilds", ())),
        dungeons=tuple(_dungeon_from_dict(item) for item in payload.get("dungeons", ())),
        economy=tuple(_economy_from_dict(item) for item in payload.get("economy", ())),
        map_markers=tuple(_marker_from_dict(item) for item in payload.get("map_markers", ())),
        audit_logs=tuple(_audit_from_dict(item) for item in payload.get("audit_logs", ())),
        event_topics=tuple(str(topic) for topic in payload.get("event_topics", ())),
    )


CORE_MODULES: tuple[ModuleCapability, ...] = build_modules()
EVENT_TOPICS: tuple[str, ...] = build_event_topics()
