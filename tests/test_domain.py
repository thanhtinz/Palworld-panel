import json
from uuid import uuid4

from palcore.domain import (
    CORE_MODULES,
    EVENT_TOPICS,
    EventEnvelope,
    PluginManifest,
    ServerInstance,
    ServerStatus,
    build_dashboard_state,
    build_demo_servers,
    load_dashboard_payload,
    to_jsonable,
)


def test_core_modules_follow_roadmap_order():
    phases = [module.phase for module in CORE_MODULES]
    assert phases == sorted(phases)
    assert {module.key for module in CORE_MODULES} >= {"server-manager", "realtime-dashboard", "plugin-platform"}


def test_plugin_manifest_slug_is_directory_safe():
    manifest = PluginManifest(name="Guild War_Manager", version="1.0.0")
    assert manifest.normalized_slug() == "guild-war-manager"
    assert "python" in manifest.runtimes


def test_server_health_score_penalizes_crashes_and_pressure():
    healthy = ServerInstance(name="Healthy", region="us", status=ServerStatus.RUNNING, cpu_percent=20, ram_mb=1024, tps=30)
    unhealthy = ServerInstance(name="Crashed", region="us", status=ServerStatus.CRASHED, cpu_percent=95, ram_mb=32_768, tps=10)

    assert healthy.health_score() == 100
    assert unhealthy.health_score() < healthy.health_score()


def test_event_envelope_serializes_to_wire_contract():
    server_id = uuid4()
    envelope = EventEnvelope(topic="server.health", server_id=server_id, payload={"status": "running"})

    wire = envelope.to_wire()

    assert wire["topic"] in EVENT_TOPICS
    assert wire["server_id"] == str(server_id)
    assert wire["payload"] == {"status": "running"}
    assert "occurred_at" in wire


def test_demo_servers_are_dashboard_ready():
    servers = build_demo_servers()

    assert len(servers) == 3
    assert all(server.online_players <= server.max_players for server in servers)
    assert all(0 <= server.health_score() <= 100 for server in servers)


def test_dashboard_state_contains_full_panel_sections():
    state = build_dashboard_state()
    totals = state.totals()

    assert totals["online_players"] == sum(server.online_players for server in state.servers)
    assert totals["tracked_pals"] == len(state.pals)
    assert state.players
    assert state.guilds
    assert state.dungeons
    assert state.economy
    assert state.map_markers
    assert state.audit_logs


def test_dashboard_state_is_json_serializable():
    state = build_dashboard_state()
    payload = to_jsonable({"totals": state.totals(), "state": state})

    assert isinstance(payload["state"]["servers"][0]["server_id"], str)
    assert isinstance(payload["state"]["audit_logs"][0]["occurred_at"], str)
    assert payload["state"]["event_topics"] == list(EVENT_TOPICS)


def test_dashboard_state_can_be_loaded_from_external_json(tmp_path):
    payload = load_dashboard_payload()
    payload["servers"] = [
        {
            **payload["servers"][0],
            "server_id": "aaaaaaaa-aaaa-4aaa-aaaa-aaaaaaaaaaaa",
            "name": "External PALCORE Shard",
            "online_players": 7,
            "max_players": 32,
        }
    ]
    payload["players"] = []
    payload["pals"] = []
    payload["guilds"] = []
    payload["dungeons"] = []
    payload["economy"] = []
    payload["map_markers"] = []
    payload["audit_logs"] = []
    data_file = tmp_path / "dashboard.json"
    data_file.write_text(json.dumps(payload), encoding="utf-8")

    state = build_dashboard_state(data_file)

    assert state.servers[0].name == "External PALCORE Shard"
    assert state.totals()["online_players"] == 7
    assert state.totals()["player_capacity"] == 32
