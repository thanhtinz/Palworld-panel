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
    build_servers,
    load_dashboard_payload,
    to_jsonable,
)


def _external_payload():
    payload = load_dashboard_payload()
    payload.update(
        {
            "servers": [
                {
                    "server_id": "aaaaaaaa-aaaa-4aaa-aaaa-aaaaaaaaaaaa",
                    "name": "External PALCORE Shard",
                    "region": "local",
                    "status": "running",
                    "max_players": 32,
                    "online_players": 7,
                    "cpu_percent": 31.5,
                    "ram_mb": 4096,
                    "disk_gb": 18.2,
                    "tps": 29.5,
                    "fps": 60,
                    "network_in_mbps": 2.4,
                    "network_out_mbps": 5.1,
                    "last_backup_at": "2026-05-28T18:00:00+00:00",
                }
            ],
            "players": [],
            "pals": [
                {
                    "pal_id": "PAL_TEST_001",
                    "species": "Anubis",
                    "level": 50,
                    "owner": "Player123",
                    "guild": "NightRaid",
                    "location": {"x": 1200, "y": 440, "z": 92},
                    "hp": 5000,
                    "stamina": 300,
                    "passives": ["Artisan"],
                    "skills": ["Ground Smash"],
                    "mood": "working",
                    "ai_state": "worker",
                    "current_action": "Working",
                    "current_target": "Ore Site",
                    "element": "ground",
                    "rarity": "epic",
                    "ivs": {"attack": 80, "defense": 76, "work_speed": 99},
                    "genetics": {"mutation_rate": 0.08, "breeding_quality": "A"},
                    "market_value": 76000,
                }
            ],
            "guilds": [],
            "dungeons": [],
            "economy": [],
            "map_markers": [],
            "audit_logs": [],
        }
    )
    return payload


def _write_payload(tmp_path, payload):
    data_file = tmp_path / "dashboard.json"
    data_file.write_text(json.dumps(payload), encoding="utf-8")
    return data_file


def test_core_modules_follow_roadmap_order():
    phases = [module.phase for module in CORE_MODULES]
    assert phases == sorted(phases)
    assert {module.key for module in CORE_MODULES} >= {"server-manager", "realtime-dashboard", "plugin-platform"}


def test_default_data_source_has_no_fake_runtime_records():
    state = build_dashboard_state()

    assert state.servers == ()
    assert state.players == ()
    assert state.pals == ()
    assert state.guilds == ()
    assert state.dungeons == ()
    assert state.economy == ()
    assert state.map_markers == ()
    assert state.audit_logs == ()
    assert state.totals()["online_players"] == 0


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


def test_external_servers_are_dashboard_ready(tmp_path):
    data_file = _write_payload(tmp_path, _external_payload())
    servers = build_servers(data_file)

    assert len(servers) == 1
    assert all(server.online_players <= server.max_players for server in servers)
    assert all(0 <= server.health_score() <= 100 for server in servers)


def test_dashboard_state_is_json_serializable(tmp_path):
    data_file = _write_payload(tmp_path, _external_payload())
    state = build_dashboard_state(data_file)
    payload = to_jsonable({"totals": state.totals(), "state": state})

    assert isinstance(payload["state"]["servers"][0]["server_id"], str)
    assert payload["state"]["event_topics"] == list(EVENT_TOPICS)
    assert payload["state"]["pals"][0]["location"] == {"x": 1200.0, "y": 440.0, "z": 92.0}


def test_dashboard_state_can_be_loaded_from_external_json(tmp_path):
    data_file = _write_payload(tmp_path, _external_payload())

    state = build_dashboard_state(data_file)

    assert state.servers[0].name == "External PALCORE Shard"
    assert state.totals()["online_players"] == 7
    assert state.totals()["player_capacity"] == 32


def test_advanced_pal_system_contract_is_loaded_from_json(tmp_path):
    data_file = _write_payload(tmp_path, _external_payload())
    state = build_dashboard_state(data_file)
    pal = state.pals[0]

    assert state.pal_system.goal.startswith("Turn Pals into")
    assert "breeding simulator" in state.pal_system.pillars
    assert "mutation system" in state.pal_system.breeding_features
    assert "AI override" in state.pal_system.ai_controls
    assert state.pal_system.feature_count() >= 30
    assert pal.pal_id.startswith("PAL_")
    assert pal.guild
    assert pal.location.z >= 0
    assert pal.skills
    assert pal.ai_state in state.pal_system.ai_states
    assert "mutation_rate" in pal.genetics
